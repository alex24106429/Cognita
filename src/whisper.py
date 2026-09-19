import psutil
from pywhispercpp.model import Model

threads = psutil.cpu_count(logical=False) or 4

model = Model("large-v3-turbo-q5_0", n_threads=threads)

# Transcribe with greedy search (beam_size=1 is default in whisper.cpp)
segments = model.transcribe(
    "audio.wav",
    language="en",
    speed_up=False  # speed_up=True does 2x audio subsampling if ultra-low quality is acceptable
)

for seg in segments:
    print(f"[{seg.t0} -> {seg.t1}] {seg.text}")
