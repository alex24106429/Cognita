"""
Cognita backend smoke test.

Boots the FastAPI app on an isolated port, exercises the real HTTP surface
(health, validation, error contract, CORS preflight) and then shuts the server
down again. Only ever manages the uvicorn process it spawned itself.

Usage:
    python backend/scripts/smoke_test.py            # autodetect interpreter
    python backend/scripts/smoke_test.py --port 8099
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

PASS = "PASS"
FAIL = "FAIL"

results: list[tuple[str, str, str]] = []


def free_port(preferred: int) -> int:
    """Return `preferred` if it is bindable, otherwise an OS-assigned port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            probe.bind(("127.0.0.1", 0))
            return int(probe.getsockname()[1])


def wait_for_health(base_url: str, timeout: float = 25.0) -> dict:
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{base_url}/api/health", timeout=2) as response:
                return json.loads(response.read().decode())
        except Exception as exc:  # noqa: BLE001 - polling loop
            last_error = exc
            time.sleep(0.5)
    raise RuntimeError(f"Backend did not become healthy in {timeout}s: {last_error}")


def post_json(url: str, payload: dict) -> tuple[int, dict]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        # A live provider round trip can legitimately take tens of seconds
        # (chunking + retries), so this must be generous to avoid false failures.
        with urllib.request.urlopen(request, timeout=120) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        try:
            return exc.code, json.loads(body)
        except json.JSONDecodeError:
            return exc.code, {"raw": body}


def record(name: str, ok: bool, detail: str) -> None:
    results.append((name, PASS if ok else FAIL, detail))
    print(f"[{PASS if ok else FAIL}] {name} :: {detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Cognita backend smoke test")
    parser.add_argument("--port", type=int, default=8010)
    args = parser.parse_args()

    port = free_port(args.port)
    base_url = f"http://127.0.0.1:{port}"

    env = dict(os.environ)
    env.setdefault("PYTHONPATH", str(BACKEND_DIR))

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        cwd=str(BACKEND_DIR),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        health = wait_for_health(base_url)
        record("health endpoint responds", health.get("status") == "healthy", json.dumps(health))
        record(
            "health exposes model metadata",
            "model" in health and "base_url" in health and "api_key_configured" in health,
            f"model={health.get('model')} key_configured={health.get('api_key_configured')}",
        )

        status, payload = post_json(f"{base_url}/api/transform", {"raw_text": "too short"})
        record(
            "short input rejected with 422",
            status == 422,
            f"status={status} detail={payload.get('detail')}",
        )

        status, payload = post_json(f"{base_url}/api/transform", {"raw_text": "x" * 50001})
        record(
            "oversized input rejected with 422",
            status == 422,
            f"status={status} detail={payload.get('detail')}",
        )

        status, payload = post_json(
            f"{base_url}/api/transform",
            {
                "raw_text": (
                    "Deliberate practice requires immediate feedback on performance. "
                    "Ericsson argues that elite performers do not simply accumulate hours; "
                    "they refine specific sub-skills under expert supervision and coaching."
                )
            },
        )
        # The expectation depends on how the server was configured, so branch on
        # what /api/health reported instead of assuming no key is present.
        if health.get("api_key_configured"):
            record(
                "configured key reaches the provider without a config error",
                status in (200, 502, 503),
                f"status={status} detail={str(payload.get('detail'))[:90]}",
            )
        else:
            # Without a real API key the backend must degrade gracefully with an
            # actionable message rather than a stack trace.
            record(
                "placeholder key produces actionable error",
                status in (500, 503)
                and "OPENAI_API_KEY" in str(payload.get("detail", "")),
                f"status={status} detail={payload.get('detail')}",
            )

        request = urllib.request.Request(
            f"{base_url}/api/transform",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
            method="OPTIONS",
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                cors_ok = response.status == 200
        except urllib.error.HTTPError as exc:
            cors_ok = False
            exc.read()
        record("CORS preflight for the Vite origin succeeds", cors_ok, f"port={port}")
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()

    failures = [name for name, status, _ in results if status == FAIL]
    print()
    if failures:
        print(f"{len(failures)} check(s) failed: {', '.join(failures)}")
        return 1
    print(f"All {len(results)} smoke checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
