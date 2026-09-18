import json
import os
import platform
import stat
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

MODEL_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin"
MODEL_FILE = "ggml-large-v3-turbo-q5_0.bin"
SAMPLE_URL = "https://github.com/ggml-org/whisper.cpp/raw/master/samples/jfk.wav"
SAMPLE_FILE = "jfk.wav"
BIN_DIR = Path("./whisper_bin")

def download_file(url: str, output_path: Path):
    """Downloads a file with a live progress indicator."""
    if output_path.exists() and output_path.stat().st_size > 0:
        print(f"[-] {output_path.name} already exists, skipping download.")
        return

    print(f"[*] Downloading {output_path.name} from {url}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    with urllib.request.urlopen(req) as response, open(output_path, "wb") as out_file:
        total_size = int(response.headers.get("content-length", 0))
        block_size = 1024 * 1024  # 1 MB chunks
        downloaded = 0

        while True:
            buffer = response.read(block_size)
            if not buffer:
                break
            downloaded += len(buffer)
            out_file.write(buffer)
            if total_size > 0:
                percent = downloaded / total_size * 100
                mb_down = downloaded / (1024 * 1024)
                mb_tot = total_size / (1024 * 1024)
                sys.stdout.write(f"\r    {mb_down:.1f}MB / {mb_tot:.1f}MB ({percent:.1f}%)")
                sys.stdout.flush()
        print()


def get_platform_asset_pattern() -> str:
    """Determines the appropriate asset filename based on current OS and Arch."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    is_arm = any(a in machine for a in ["arm", "aarch64"])
    is_x86_64 = any(a in machine for a in ["x86_64", "amd64"])

    if system == "linux":
        if is_arm:
            return "whisper-bin-ubuntu-arm64.tar.gz"
        elif is_x86_64:
            return "whisper-bin-ubuntu-x64.tar.gz"
        else:
            raise RuntimeError(f"Unsupported Linux architecture: {machine}")

    elif system == "windows":
        if is_arm:
            return "whisper-bin-win-cpu-arm64.zip"
        elif is_x86_64:
            return "whisper-bin-x64.zip"
        else:
            return "whisper-bin-Win32.zip"

    elif system == "darwin":
        raise RuntimeError(
            "whisper.cpp releases do not provide pre-compiled CLI binaries for macOS (only xcframework). "
            "Please install it using 'brew install whisper-cpp' instead."
        )
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")


def get_latest_prerelease_asset(asset_filename: str) -> tuple[str, str]:
    """Fetches the latest pre-release download URL from the GitHub API."""
    api_url = "https://api.github.com/repos/ggml-org/whisper.cpp/releases"
    req = urllib.request.Request(api_url, headers={"User-Agent": "Python-Whisper-Script"})

    print("[*] Fetching releases from GitHub...")
    with urllib.request.urlopen(req) as resp:
        releases = json.loads(resp.read().decode())

    # Find the newest release flagged as pre-release
    target_release = next((r for r in releases if r.get("prerelease")), None)
    if not target_release and releases:
        target_release = releases[0]  # Fallback to the latest release

    tag = target_release["tag_name"]
    print(f"[*] Selected pre-release version: {tag}")

    for asset in target_release.get("assets", []):
        if asset["name"] == asset_filename:
            return asset["name"], asset["browser_download_url"]

    raise FileNotFoundError(f"Could not find asset '{asset_filename}' in release {tag}")


def extract_archive(archive_path: Path, extract_to: Path):
    """Extracts tar.gz or zip archives."""
    print(f"[*] Extracting {archive_path.name}...")
    extract_to.mkdir(exist_ok=True)

    if archive_path.name.endswith(".tar.gz") or archive_path.name.endswith(".tgz"):
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(extract_to)
    elif archive_path.name.endswith(".zip"):
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)


def find_executable(search_dir: Path) -> Path:
    """Finds the whisper CLI binary ('whisper-cli' or fallback 'main')."""
    candidates = ["whisper-cli.exe", "whisper-cli", "main.exe", "main"]
    for root, _, files in os.walk(search_dir):
        for candidate in candidates:
            if candidate in files:
                exe_path = Path(root) / candidate
                # Ensure execution bit is set on Unix
                if os.name != "nt":
                    exe_path.chmod(exe_path.stat().st_mode | stat.S_IEXEC)
                return exe_path

    raise FileNotFoundError("Could not locate whisper executable inside the downloaded package.")


def main():
    # 1. Determine platform and asset
    asset_name = get_platform_asset_pattern()
    print(f"[*] Target platform asset: {asset_name}")

    # 2. Get asset download URL
    filename, download_url = get_latest_prerelease_asset(asset_name)

    # 3. Download & extract whisper.cpp binary
    archive_path = Path(filename)
    download_file(download_url, archive_path)
    extract_archive(archive_path, BIN_DIR)
    binary_path = find_executable(BIN_DIR)
    print(f"[*] Found executable: {binary_path}")

    # 4. Download Model
    model_path = Path(MODEL_FILE)
    download_file(MODEL_URL, model_path)

    # 5. Download Sample Audio
    sample_path = Path(SAMPLE_FILE)
    download_file(SAMPLE_URL, sample_path)

    # 6. Run transcription
    print("\n" + "=" * 50)
    print("[*] Running Whisper transcription...")
    print("=" * 50 + "\n")

    cmd = [
        str(binary_path.resolve()),
        "-m", str(model_path.resolve()),
        "-f", str(sample_path.resolve())
    ]
    
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[!] Error: {e}", file=sys.stderr)
        sys.exit(1)