import io
import json
import os
import sys
import wave
import urllib.request
import urllib.error
import numpy as np
import sounddevice as sd
from pathlib import Path
from PyQt6.QtCore import QSettings

from config import TTS_PROVIDERS, DEFAULT_TTS_PROVIDER

_supertonic_instance = None


def get_supertonic_model():
    """Lazy-loads the Supertonic ONNX model only when needed."""
    global _supertonic_instance
    if _supertonic_instance is None:
        try:
            from supertonic import TTS
        except ImportError as e:
            raise RuntimeError(
                "Supertonic is not installed. Please install 'supertonic' or select a cloud TTS provider."
            ) from e

        model_dir = Path(__file__).resolve().parents[1] / "tts_model"
        _supertonic_instance = TTS(
            model="supertonic-3", model_dir=model_dir, auto_download=True
        )
    return _supertonic_instance


def get_reusable_api_key(provider: str) -> tuple[str, str]:
    """
    Returns (api_key, source_description).
    Looks up explicit TTS keys, reused agent keys, and environment variables.
    """
    settings = QSettings("cognita", "gui")
    p_lower = provider.lower()

    # 1. Check explicit TTS key saved in settings
    tts_key = settings.value(f"tts_{p_lower}_api_key", "").strip()
    if tts_key:
        return tts_key, "Saved TTS key"

    # 2. Check provider-specific agent key
    agent_p_key = settings.value(f"{p_lower}_api_key", "").strip()
    if agent_p_key:
        return agent_p_key, f"Reused from {provider} agent credentials"

    # 3. Check active agent key if current LLM provider matches
    current_agent_provider = settings.value("provider", "").strip().lower()
    if current_agent_provider == p_lower:
        active_key = settings.value("api_key", "").strip()
        if active_key:
            return active_key, f"Reused from active {provider} settings"

    # 4. Check environment variables
    env_map = {
        "openrouter": ["OPENROUTER_API_KEY"],
        "openai": ["OPENAI_API_KEY"],
        "elevenlabs": ["ELEVENLABS_API_KEY", "XI_API_KEY"],
    }
    for env_var in env_map.get(p_lower, []):
        val = os.environ.get(env_var, "").strip()
        if val:
            return val, f"Reused from environment (${env_var})"

    return "", ""


def play_audio_data(audio_bytes: bytes, content_type: str = "", sample_rate: int = 24000):
    """Decodes and plays audio bytes (WAV, PCM, or MP3) through sounddevice."""
    if not audio_bytes:
        return

    # Case A: Standard RIFF WAV format
    if audio_bytes[:4] == b"RIFF":
        with wave.open(io.BytesIO(audio_bytes), "rb") as wf:
            sr = wf.getframerate()
            ch = wf.getnchannels()
            width = wf.getsampwidth()
            frames = wf.readframes(wf.getnframes())
            if width == 2:
                dtype = np.int16
            elif width == 4:
                dtype = np.int32
            elif width == 1:
                dtype = np.int8
            else:
                dtype = np.int16
            data = np.frombuffer(frames, dtype=dtype)
            if ch > 1:
                data = data.reshape(-1, ch)
            sd.play(data, sr)
            sd.wait()
            return

    # Case B: MP3 audio
    is_mp3 = (
        "mpeg" in content_type
        or "mp3" in content_type
        or audio_bytes[:3] == b"ID3"
        or audio_bytes[:2] in (b"\xff\xfb", b"\xff\xf3")
    )

    if is_mp3:
        try:
            import soundfile as sf
            data, sr = sf.read(io.BytesIO(audio_bytes))
            sd.play(data, sr)
            sd.wait()
            return
        except Exception:
            pass

        try:
            from pydub import AudioSegment
            seg = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
            samples = np.array(seg.get_array_of_samples())
            if seg.channels == 2:
                samples = samples.reshape((-1, 2))
            sd.play(samples, seg.frame_rate)
            sd.wait()
            return
        except Exception:
            pass

        # Fallback using temporary file and native system player
        import tempfile
        import subprocess
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
            tf.write(audio_bytes)
            tmp_path = tf.name
        try:
            if sys.platform == "darwin":
                subprocess.run(["afplay", tmp_path], check=True)
            elif sys.platform == "win32":
                ps_cmd = f'(New-Object Media.SoundPlayer "{tmp_path}").PlaySync()'
                subprocess.run(["powershell", "-c", ps_cmd], check=False)
            else:
                subprocess.run(["mpv", "--no-video", tmp_path], check=False)
        finally:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        return

    # Case C: Raw 16-bit PCM
    data = np.frombuffer(audio_bytes, dtype=np.int16)
    sd.play(data, sample_rate)
    sd.wait()


def synthesize_supertonic(text: str, voice: str = "M4") -> tuple[np.ndarray, int]:
    """Generates audio via local Supertonic model."""
    tts = get_supertonic_model()
    voice_name = voice.strip().upper()
    style = tts.get_voice_style(voice_name=voice_name)
    wav, _ = tts.synthesize(text, lang="en", voice_style=style)
    sr = getattr(tts, "sample_rate", 44100)
    return wav.squeeze(), sr


def synthesize_openrouter(text: str, voice: str = "flux-alexis-en", api_key: str = "") -> tuple[bytes, str]:
    """Generates speech using deepgram/flux-tts:free on OpenRouter."""
    if not api_key:
        raise ValueError(
            "OpenRouter API key is required. Please configure your key.")

    url = "https://openrouter.ai/api/v1/audio/speech"
    payload = {
        "model": "deepgram/flux-tts:free",
        "input": text,
        "voice": voice or "flux-alexis-en",
        "response_format": "pcm",
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Cognita-Agent",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content_type = resp.headers.get("Content-Type", "audio/pcm")
            return resp.read(), content_type
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        try:
            msg = json.loads(body).get("error", {}).get("message", str(e))
        except Exception:
            msg = str(e)
        raise RuntimeError(f"OpenRouter TTS error ({e.code}): {msg}") from e
    except Exception as e:
        raise RuntimeError(f"OpenRouter TTS request failed: {e}") from e


def synthesize_openai(text: str, voice: str = "alloy", model: str = "tts-1", api_key: str = "") -> tuple[bytes, str]:
    """Generates speech via OpenAI /audio/speech endpoint."""
    if not api_key:
        raise ValueError(
            "OpenAI API key is required. Please configure your key.")

    url = "https://api.openai.com/v1/audio/speech"
    payload = {
        "model": model or "tts-1",
        "input": text,
        "voice": voice or "alloy",
        "response_format": "wav",
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Cognita-Agent",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content_type = resp.headers.get("Content-Type", "audio/wav")
            return resp.read(), content_type
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        try:
            msg = json.loads(body).get("error", {}).get("message", str(e))
        except Exception:
            msg = str(e)
        raise RuntimeError(f"OpenAI TTS error ({e.code}): {msg}") from e
    except Exception as e:
        raise RuntimeError(f"OpenAI TTS request failed: {e}") from e


def synthesize_elevenlabs(text: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM",
                          model: str = "eleven_multilingual_v2", api_key: str = "") -> tuple[bytes, str]:
    """Generates speech via ElevenLabs /text-to-speech API."""
    if not api_key:
        raise ValueError(
            "ElevenLabs API key is required. Please configure your key.")

    # Extract ID if formatted as "Name (voice_id)"
    if "(" in voice_id and ")" in voice_id:
        voice_id = voice_id.split("(")[-1].split(")")[0].strip()

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128"
    payload = {
        "text": text,
        "model_id": model or "eleven_multilingual_v2",
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "User-Agent": "Cognita-Agent",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content_type = resp.headers.get("Content-Type", "audio/mpeg")
            return resp.read(), content_type
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        try:
            err_data = json.loads(body)
            detail = err_data.get("detail")
            msg = detail.get("message") if isinstance(
                detail, dict) else str(detail) or str(e)
        except Exception:
            msg = str(e)
        raise RuntimeError(f"ElevenLabs TTS error ({e.code}): {msg}") from e
    except Exception as e:
        raise RuntimeError(f"ElevenLabs TTS request failed: {e}") from e


def speak_text(text: str, provider: str = None, voice: str = None,
               api_key: str = None, model: str = None):
    """Synthesizes and speaks text using specified or configured TTS engine."""
    text = (text or "").strip()
    if not text:
        return

    settings = QSettings("cognita", "gui")
    provider = (provider or settings.value(
        "tts_provider", DEFAULT_TTS_PROVIDER)).lower()

    if provider == "supertonic":
        voice = voice or settings.value("tts_voice", "M4")
        wav, sr = synthesize_supertonic(text, voice=voice)
        sd.play(wav, sr)
        sd.wait()
    elif provider == "openrouter":
        voice = voice or settings.value("tts_voice", "flux-alexis-en")
        if not api_key:
            api_key, _ = get_reusable_api_key("openrouter")
        audio_bytes, ctype = synthesize_openrouter(
            text, voice=voice, api_key=api_key)
        play_audio_data(audio_bytes, content_type=ctype, sample_rate=24000)
    elif provider == "openai":
        voice = voice or settings.value("tts_voice", "alloy")
        model = model or settings.value("tts_model", "tts-1")
        if not api_key:
            api_key, _ = get_reusable_api_key("openai")
        audio_bytes, ctype = synthesize_openai(
            text, voice=voice, model=model, api_key=api_key)
        play_audio_data(audio_bytes, content_type=ctype)
    elif provider == "elevenlabs":
        voice = voice or settings.value("tts_voice", "21m00Tcm4TlvDq8ikWAM")
        model = model or settings.value("tts_model", "eleven_multilingual_v2")
        if not api_key:
            api_key, _ = get_reusable_api_key("elevenlabs")
        audio_bytes, ctype = synthesize_elevenlabs(
            text, voice_id=voice, model=model, api_key=api_key)
        play_audio_data(audio_bytes, content_type=ctype)
    else:
        raise ValueError(f"Unknown TTS provider: {provider}")


def speak(text: str):
    """Main entrypoint called by worker on task finish."""
    settings = QSettings("cognita", "gui")
    if not settings.value("tts_enabled", True, type=bool):
        return
    try:
        speak_text(text)
    except Exception as e:
        print(f"[TTS Error] Failed to speak: {e}", file=sys.stderr)
