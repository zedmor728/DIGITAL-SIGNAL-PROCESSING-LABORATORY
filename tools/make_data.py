"""Create the reproducible speech-like WAV used by Week 1 (and available to Week 2).

The original phone recording was not supplied with the student's source files.
This script generates a deterministic, speech-like stand-in with the parameters
reported in the report: 16 kHz, 4.70 s, 75 200 samples, 16-bit mono PCM.
Replace data/my_voice.wav with your own recording if you have one.
"""
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)


def speech_like(fs=16000, T=4.7, seed=3):
    """Voiced bursts (harmonics + formants) plus noise, normalised to peak 1."""
    rng = np.random.default_rng(seed)
    t = np.arange(0, T, 1 / fs)
    env = np.zeros_like(t)
    for centre, width, amp in [(0.9, 0.18, 0.7), (1.5, 0.15, 0.5),
                               (2.3, 0.22, 1.0), (3.0, 0.20, 0.8),
                               (3.8, 0.25, 0.45)]:
        env += amp * np.exp(-0.5 * ((t - centre) / width) ** 2)
    f0 = 110 + 25 * np.sin(2 * np.pi * 0.4 * t)
    phase = 2 * np.pi * np.cumsum(f0) / fs
    voiced = sum(np.sin(k * phase) / k ** 0.8 for k in range(1, 30))
    b, a = signal.butter(2, [300, 2500], btype="band", fs=fs)
    voiced = signal.lfilter(b, a, voiced)
    b2, a2 = signal.butter(2, 1500, btype="high", fs=fs)
    noise = signal.lfilter(b2, a2, rng.standard_normal(len(t)))
    x = env * voiced + 0.02 * noise + 0.1 * env * noise
    return fs, x / np.max(np.abs(x))


if __name__ == "__main__":
    fs, x = speech_like()
    pcm = np.round(x * 32767).astype(np.int16)
    out = DATA / "my_voice.wav"
    wavfile.write(out, fs, pcm)
    print(f"Wrote {out}")
    print(f"fs = {fs} Hz, samples = {len(pcm)}, duration = {len(pcm)/fs:.2f} s")
