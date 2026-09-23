"""
Standalone test: microphone -> record -> Whisper transcription -> print.

Run from the src/ directory:
    python test_voice.py
"""

from whisper import record_and_transcribe


def main():
    print("=== Voice Input Test ===")
    print("Speak clearly into the microphone for 5 seconds...")
    text = record_and_transcribe(duration=5.0, sample_rate=16000)
    print(f"\nTranscription: {text}")


if __name__ == "__main__":
    main()
