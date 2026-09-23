"""
Local speech-to-text using pywhispercpp and the Whisper large-v3-turbo-q5_0 model.

This module is import-safe: the Whisper model is NOT loaded at import time.
It is only loaded when transcribe_audio() or record_and_transcribe() is called.
"""

import os
import wave
import tempfile
import psutil
import numpy as np
import sounddevice as sd
from pywhispercpp.model import Model


def _get_n_threads() -> int:
    """Return the number of physical CPU cores for Whisper threading."""
    return psutil.cpu_count(logical=False) or 4


def record_audio(duration: float = 5.0, sample_rate: int = 16000) -> np.ndarray:
    """
    Record audio from the default microphone.

    Args:
        duration: Recording length in seconds.
        sample_rate: Target sample rate in Hz (Whisper expects 16 kHz).

    Returns:
        1-D numpy array of int16 samples (mono).
    """
    print(f"Recording {duration}s at {sample_rate} Hz (mono)...")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
    )
    sd.wait()  # block until recording is done
    print("Recording complete.")
    return audio.squeeze()


def save_wav(audio: np.ndarray, sample_rate: int, path: str) -> str:
    """Write a mono int16 numpy array to a WAV file."""
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit = 2 bytes
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
    return path


def transcribe_audio(
    wav_path: str,
    model_name: str = "large-v3-turbo-q5_0",
    language: str = "en",
) -> str:
    """
    Transcribe a WAV file using a local pywhispercpp model.

    The model is loaded lazily (only when this function is called),
    so importing this module does not trigger a download.

    Args:
        wav_path: Path to the input WAV file.
        model_name: Whisper model identifier.
        language: Language code for transcription.

    Returns:
        Concatenated transcription text.
    """
    n_threads = _get_n_threads()
    print(f"Loading Whisper model '{model_name}' (n_threads={n_threads})...")
    model = Model(model_name, n_threads=n_threads)

    print(f"Transcribing '{wav_path}'...")
    segments = model.transcribe(
        wav_path,
        language=language,
    )

    text = "".join(seg.text for seg in segments)
    return text.strip()


def record_and_transcribe(
    duration: float = 5.0,
    sample_rate: int = 16000,
    model_name: str = "large-v3-turbo-q5_0",
    language: str = "en",
) -> str:
    """
    Full pipeline: record from microphone -> save WAV -> transcribe -> return text.
    """
    audio = record_audio(duration, sample_rate)

    # Use a temporary file for the WAV
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name
    save_wav(audio, sample_rate, wav_path)

    try:
        text = transcribe_audio(wav_path, model_name, language)
    finally:
        os.unlink(wav_path)

    return text
