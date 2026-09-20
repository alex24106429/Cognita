import sounddevice as sd
from pathlib import Path
from supertonic import TTS

model_dir = Path(__file__).resolve().parents[1] / "tts_model"
tts = TTS(model="supertonic-3", model_dir=model_dir, auto_download=True)
style = tts.get_voice_style(voice_name="M4")


def speak(text: str):
    wav, _ = tts.synthesize(text, lang="en", voice_style=style)
    sd.play(wav.squeeze(), getattr(tts, "sample_rate", 44100))
