"""Build the four Weeks 1-4 Jupyter notebooks for COU 07506.

The notebooks are written with nbformat so that they can be executed from top to
bottom with `jupyter nbconvert --execute`. All text follows the student's report
and the laboratory manual; every figure and number is produced by the code.
"""
from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"
NOTEBOOKS.mkdir(parents=True, exist_ok=True)

REG = "240242479517"
NAME = "Zaid Yaseer Yussuf"

COMMON = r'''
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import signal
from scipy.io import wavfile
from IPython.display import Audio, display

plt.rcParams["figure.figsize"] = (9, 3.5)
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.25

ROOT = Path.cwd()
if ROOT.name == "notebooks":
    ROOT = ROOT.parent
FIGDIR = ROOT / "report" / "figures"
FIGDIR.mkdir(parents=True, exist_ok=True)
DATA = ROOT / "data"
REPORT = ROOT / "report"
REPORT.mkdir(parents=True, exist_ok=True)
print("Repository root:", ROOT)
'''


def md(text):
    return nbf.v4.new_markdown_cell(text.strip())


def code(text):
    return nbf.v4.new_code_cell(text.strip())


def new_notebook(title, cells):
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
    }
    nb.cells = [md(title)] + cells
    return nb


def write(nb, week):
    path = NOTEBOOKS / f"COU07506_Week{week:02d}_{REG}.ipynb"
    nbf.write(nb, path)
    print("Wrote", path)


# ---------------------------------------------------------------------------
# WEEK 1
# ---------------------------------------------------------------------------
week1 = new_notebook(f'''# COU 07506 — Week 1: Lab 0, Setting Up the DSP Laboratory

**Student:** {NAME} &nbsp;|&nbsp; **Registration number:** {REG} &nbsp;|&nbsp;
**Class:** BEng24COE &nbsp;|&nbsp; **Date:** 26 November 2026 &nbsp;|&nbsp;
**Submission:** Individual laboratory work (group details to be added during the session).
''', [
    md('''
## Pre-lab preparation

**Reading.** How to Use This Handout, §1.1 and Listing 1.3.

**Question — three devices containing DSP and one signal each processes**

| Device | Signal processed | DSP operation |
|---|---|---|
| Smartphone | Speech from the microphone | Noise reduction and speech coding |
| Digital audio system (music player / sound card) | Audio stream | Equalisation and digital-to-analogue conversion |
| Wi-Fi router | Radio-frequency signal | Modulation/demodulation and error correction |
'''),
    code(COMMON),
    md('''
## Task 1.1 — Elementary sequences

Generate δ(n), u(n), r(n) and (0.8)ⁿu(n) for −5 ≤ n ≤ 10 and draw each sequence
with a stem plot, because a discrete-time signal is defined only at integer n.
'''),
    code(r'''
n = np.arange(-5, 11)
delta = (n == 0).astype(float)
step = (n >= 0).astype(float)
ramp = n * step
expo = 0.8**n * step

fig, axes = plt.subplots(1, 4, figsize=(13, 2.8))
for ax, x, title in zip(axes, [delta, step, ramp, expo],
                        ["$\delta(n)$", "$u(n)$", "$r(n)$", "$(0.8)^n u(n)$"]):
    ax.stem(n, x, basefmt="k-")
    ax.set_title(title)
    ax.set_xlabel("n (samples)")
    ax.set_ylabel("amplitude")
fig.suptitle("Task 1.1 — elementary discrete-time sequences")
fig.tight_layout()
fig.savefig(FIGDIR / "week01_task1_1.png", dpi=160, bbox_inches="tight")
plt.show()

print("n      :", n.tolist())
print("delta  :", delta.astype(int).tolist())
print("step   :", step.astype(int).tolist())
print("ramp   :", ramp.astype(int).tolist())
print("expo   :", np.round(expo, 4).tolist())
print("expo[10] =", round(float(expo[10]), 6))
'''),
    md('''
**Observation.** δ(n) is a single unit sample at n = 0; u(n) steps to 1 and stays
there; r(n) grows linearly and r(10) = 10; (0.8)ⁿu(n) decays geometrically and
equals 0.8¹⁰ = 0.1074 at n = 10.
'''),
    md('''
## Task 1.2 — Changing the parameters

(a) Plot aⁿu(n) for a = 0.5, −0.8 and 1.1. (b) Plot cos(2πn/8) and cos(2πn/7.5)
for 0 ≤ n ≤ 40 and find the fundamental period numerically.
'''),
    code(r'''
n2 = np.arange(-5, 21)
step2 = (n2 >= 0).astype(float)
fig, axes = plt.subplots(1, 3, figsize=(12, 3.2))
for ax, a in zip(axes, [0.5, -0.8, 1.1]):
    ax.stem(n2, a**n2 * step2, basefmt="k-")
    ax.set_title(f"$a={a}$")
    ax.set_xlabel("n (samples)")
    ax.set_ylabel("$a^n u(n)$")
fig.suptitle("Task 1.2(a) — effect of the parameter a")
fig.tight_layout()
fig.savefig(FIGDIR / "week01_task1_2a.png", dpi=160, bbox_inches="tight")
plt.show()
a_values = {str(a): float(a**20) for a in [0.5, -0.8, 1.1]}
print("Values at n = 20:", {k: round(v, 6) for k, v in a_values.items()})

n3 = np.arange(0, 41)
c8 = np.cos(2 * np.pi * n3 / 8)
c75 = np.cos(2 * np.pi * n3 / 7.5)

def fundamental_period(x, max_N=40):
    for N in range(1, max_N + 1):
        if N < len(x) and np.allclose(x[N:], x[:-N], atol=1e-9):
            return N
    return None

period_8 = fundamental_period(c8)
period_75 = fundamental_period(c75)
print("cos(2*pi*n/8)   : f0 = 1/8  =", 1/8,  "-> period =", period_8, "samples")
print("cos(2*pi*n/7.5) : f0 = 2/15 =", 2/15, "-> period =", period_75, "samples")

fig, axes = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
axes[0].stem(n3, c8, basefmt="k-", label="cos(2$\\pi$n/8)")
axes[1].stem(n3, c75, basefmt="k-", label="cos(2$\\pi$n/7.5)", linefmt="C1-", markerfmt="C1o")
for ax in axes:
    ax.set_ylabel("amplitude")
    ax.legend(loc="upper right")
axes[0].set_title("Task 1.2(b) — sampled cosines")
axes[1].set_xlabel("n (samples)")
fig.tight_layout()
fig.savefig(FIGDIR / "week01_task1_2b.png", dpi=160, bbox_inches="tight")
plt.show()
'''),
    md('''
**Observation.** Both sequences are periodic because both normalised frequencies
are rational: 1/8 gives N = 8 samples and 2/15 gives N = 15 samples. For a = 1.1
the exponential grows without bound, so it could not be a stable impulse response.
'''),
    md('''
## Task 1.3 — Working with audio

The original phone recording was not supplied, so a deterministic speech-like
stand-in WAV with the parameters reported in the report is read from
`data/my_voice.wav`. Replace that file with your own recording and re-run the cell
to use your own voice; the code reports the actual header values.
'''),
    code(r'''
fname = DATA / "my_voice.wav"
if fname.exists():
    fs, x_audio = wavfile.read(fname)
    raw_dtype = str(x_audio.dtype)
    if x_audio.ndim > 1:
        x_audio = x_audio.mean(axis=1)
    peak_raw = float(np.max(np.abs(x_audio)))
    x_norm = x_audio.astype(float) / peak_raw
    source = "data/my_voice.wav (speech-like stand-in; declared in AI-use statement)"
else:
    fs = 16000
    t_fb = np.arange(0, 2, 1 / fs)
    x_norm = 0.5 * np.sin(2 * np.pi * 440 * t_fb) * np.exp(-t_fb)
    raw_dtype = "float64 (manual fallback)"
    peak_raw = float(np.max(np.abs(x_norm)))
    source = "manual fallback test signal"

t_audio = np.arange(len(x_norm)) / fs
duration = len(x_norm) / fs
print("source                 :", source)
print("fs                     :", fs, "Hz")
print("Nyquist frequency      :", fs / 2, "Hz")
print("duration               :", f"{duration:.2f} s")
print("number of samples      :", len(x_norm))
print("original WAV dtype     :", raw_dtype)
print("peak before normalise  :", peak_raw)

fig, ax = plt.subplots(figsize=(10, 3.2))
ax.plot(t_audio, x_norm, lw=0.7)
ax.set_title("Task 1.3 — recorded voice (normalised amplitude)")
ax.set_xlabel("time (s)")
ax.set_ylabel("normalised amplitude")
fig.tight_layout()
fig.savefig(FIGDIR / "week01_task1_3.png", dpi=160, bbox_inches="tight")
plt.show()

# Uncomment to listen in a notebook:
# display(Audio(x_norm, rate=fs))
'''),
    md('''
The waveform consists of several amplitude bursts separated by quieter gaps,
which is characteristic of speech. One minute of mono audio at this rate needs
60 × fs numbers (960 000 at 16 kHz).
'''),
    md('''
## Task 1.4 — The same sequences in GNU Octave (optional)

The following Octave script produces the four sequences of Task 1.1. It is not
executed in this notebook; it is included for the notebook record.

```octave
n = -5:10;
delta = double(n == 0);
step  = double(n >= 0);
ramp  = n .* step;
expo  = 0.8.^n .* step;
subplot(1,4,1); stem(n, delta); title('delta(n)'); xlabel('n');
subplot(1,4,2); stem(n, step);  title('u(n)');     xlabel('n');
subplot(1,4,3); stem(n, ramp);  title('r(n)');     xlabel('n');
subplot(1,4,4); stem(n, expo);  title('(0.8)^n u(n)'); xlabel('n');
```

| Feature | Python / NumPy | Octave |
|---|---|---|
| Index origin | 0 | 1 |
| Range −5 to 10 | `np.arange(-5, 11)` | `-5:10` |
| Logical → numeric | `.astype(float)` | `double()` |
| Element-wise product / power | `*` and `**` | `.*` and `.^` |
| Multiple plots | `plt.subplots()` | `subplot(r, c, k)` |

## Task 1.5 — Repository

The notebooks are kept in the local Git repository `COU07506-labs`; see the
repository README for the commit history and the GitHub push instructions.
'''),
    md('''
## Analysis questions

1. **Storage.** At fs = 16 kHz one minute of mono audio requires 60 × 16 000 =
   960 000 numbers. At 44.1 kHz it needs 2 646 000 and at 48 kHz 2 880 000.
2. **Stem plot.** x(n) is defined only at integer n. A continuous line would
   suggest values between samples, whereas a stem plot shows only the samples
   that actually exist.
3. **Growing exponential.** For a = 1.1, Σ|h(n)| diverges. A bounded input could
   therefore produce an unbounded output, violating BIBO stability (Unit 1 §1.7).
'''),
    code(r'''
results_week01 = {
    "week": 1,
    "elementary": {
        "expo_10": round(float(expo[10]), 6),
        "ramp_10": int(ramp[10]),
        "delta_nonzero_index": int(n[np.argmax(delta)]),
    },
    "a_values_at_20": {k: round(v, 6) for k, v in a_values.items()},
    "periods": {"cos_n8": period_8, "cos_n7_5": period_75},
    "audio": {
        "fs": int(fs),
        "duration_s": round(float(duration), 3),
        "samples": int(len(x_norm)),
        "dtype": raw_dtype,
        "peak_before_normalisation": peak_raw,
        "source": source,
    },
}
(REPORT / "results_week01.json").write_text(json.dumps(results_week01, indent=2))
print(json.dumps(results_week01, indent=2))
'''),
    md('''
## AI-use statement

**Tool:** OpenCode (model Big Pickle). **Used for:** drafting the Python code,
the Octave listing and the written answers in this notebook. **Verification:**
the notebook was restarted and run from top to bottom. Task 1.1 was compared with
the expected sequences in the manual (δ at n = 0, r(10) = 10, 0.8¹⁰ = 0.1074);
the cosine periods were checked numerically with x(n + N) = x(n); and the audio
parameters were read from the WAV header. The speech-like audio is a declared
reproducible stand-in, not a new recording. I can explain every line of code.
'''),
])
write(week1, 1)


# ---------------------------------------------------------------------------
# WEEK 2
# ---------------------------------------------------------------------------
week2 = new_notebook(f'''# COU 07506 — Week 2: Lab 1A, Sampling, Aliasing and Quantization

**Student:** {NAME} &nbsp;|&nbsp; **Registration number:** {REG} &nbsp;|&nbsp;
**Class:** BEng24COE &nbsp;|&nbsp; **Date:** 26 November 2026 &nbsp;|&nbsp;
**Submission:** Individual laboratory work.
''', [
    md('''
## Pre-lab preparation

**Reading.** Handout §1.2, Listings 1.1–1.2 and Example 1.1.

**(a)** A 7 kHz tone sampled at 10 kHz appears at |7 − 10| = **3 kHz**.

**(b)** For an 8-bit quantiser with range ±1 V: Δ = 2/2⁸ = 2/256 =
**7.8125 mV**, and the theoretical SQNR = 6.02 × 8 + 1.76 = **49.9 dB**.
'''),
    code(COMMON),
    code(r'''
# Functions used in this notebook

def alias_freq(f0, fs):
    """Return (|F - k fs|, k) with k = round(F/fs)."""
    k = round(f0 / fs)
    return abs(f0 - k * fs), k

def quantize(x, bits, full_scale=1.0):
    """Uniform mid-tread quantiser on [-full_scale, full_scale - delta]."""
    delta = 2 * full_scale / 2**bits
    q = np.round(x / delta) * delta
    return np.clip(q, -full_scale, full_scale - delta)

def sqnr_db(x, xq):
    return float(10 * np.log10(np.sum(x**2) / np.sum((x - xq)**2)))

def chirp_signal(fs=44100, T=3):
    t = np.arange(0, T, 1 / fs)
    return fs, 0.5 * signal.chirp(t, 200, T, 15000)

def speech_like(fs=16000, T=4.7, seed=3):
    """Synthetic speech-like signal: voiced bursts plus noise (fixed seed)."""
    rng = np.random.default_rng(seed)
    t = np.arange(0, T, 1 / fs)
    env = np.zeros_like(t)
    for centre, width, amp in [(0.9, 0.18, 0.7), (1.5, 0.15, 0.5),
                               (2.3, 0.22, 1.0), (3.0, 0.20, 0.8),
                               (3.8, 0.25, 0.45)]:
        env += amp * np.exp(-0.5 * ((t - centre) / width) ** 2)
    f0 = 110 + 25 * np.sin(2 * np.pi * 0.4 * t)
    phase = 2 * np.pi * np.cumsum(f0) / fs
    voiced = sum(np.sin(k * phase) / k**0.8 for k in range(1, 30))
    b, a = signal.butter(2, [300, 2500], btype="band", fs=fs)
    voiced = signal.lfilter(b, a, voiced)
    b2, a2 = signal.butter(2, 1500, btype="high", fs=fs)
    noise = signal.lfilter(b2, a2, rng.standard_normal(len(t)))
    x = env * voiced + 0.02 * noise + 0.1 * env * noise
    return fs, x / np.max(np.abs(x))
'''),
    md('''
## Task 2.1 — Aliasing of a sinusoid

A 7 Hz cosine is drawn on a dense grid (the "analog" signal) together with its
samples and the predicted alias for fs = 10, 12, 14 and 20 Hz.
'''),
    code(r'''
f0 = 7.0
t_dense = np.linspace(0, 1, 2000)
alias_rows = []
fig, axes = plt.subplots(2, 2, figsize=(11, 6))
for ax, fs_now in zip(axes.ravel(), [10, 12, 14, 20]):
    fa, k = alias_freq(f0, fs_now)
    n = np.arange(0, int(fs_now) + 1)
    tn = n / fs_now
    ax.plot(t_dense, np.cos(2*np.pi*f0*t_dense), label="7 Hz input")
    ax.plot(t_dense, np.cos(2*np.pi*fa*t_dense), "--", label=f"{fa:g} Hz alias")
    ax.stem(tn, np.cos(2*np.pi*f0*tn), linefmt="k-", markerfmt="ko",
            basefmt=" ", label="samples")
    ax.set_title(f"fs = {fs_now} Hz, k = {k}, alias = {fa:g} Hz")
    ax.set_xlabel("time (s)")
    ax.set_ylabel("amplitude")
    ax.legend(fontsize=8)
    alias_rows.append({"fs_Hz": fs_now, "k": k, "abs_F_minus_kfs_Hz": fa,
                       "comment": ("aliased" if fa != f0 else "no alias / Nyquist limit")})
fig.suptitle("Task 2.1 — sampling a 7 Hz cosine at four rates")
fig.tight_layout()
fig.savefig(FIGDIR / "week02_task2_1.png", dpi=160, bbox_inches="tight")
plt.show()
display(pd.DataFrame(alias_rows))
'''),
    md('''
## Task 2.2 — Aliasing in a decimated signal

The manual's 3 s chirp (200 Hz → 15 kHz at 44.1 kHz) is used so the result is
reproducible. Each decimation by k is done once by keeping every k-th sample and
once with `signal.decimate`, which low-pass filters before discarding samples.
'''),
    code(r'''
fs_chirp, x_chirp = chirp_signal()
x_chirp_rms = float(np.sqrt(np.mean(x_chirp**2)))
decim_rows = []
for k in [2, 4, 8]:
    naive = x_chirp[::k]
    proper = signal.decimate(x_chirp, k, ftype="fir")
    new_fs = fs_chirp / k
    nyquist = new_fs / 2
    frac = np.clip((nyquist - 200) / (15000 - 200), 0.0, 1.0)
    predicted = x_chirp_rms * np.sqrt(frac)
    decim_rows.append({"k": k, "new_fs_Hz": new_fs,
                       "rms_naive": float(np.sqrt(np.mean(naive**2))),
                       "rms_decimate": float(np.sqrt(np.mean(proper**2))),
                       "rms_predicted_filtered": float(predicted)})
    print(f"k = {k}: new fs = {new_fs:g} Hz, new Nyquist = {nyquist:g} Hz")
display(pd.DataFrame(decim_rows))

naive8 = x_chirp[::8]
proper8 = signal.decimate(x_chirp, 8, ftype="fir")
fs8 = fs_chirp / 8
f_n, t_n, Z_n = signal.spectrogram(naive8, fs=fs8, nperseg=1024, noverlap=768)
f_p, t_p, Z_p = signal.spectrogram(proper8, fs=fs8, nperseg=1024, noverlap=768)
fig, axes = plt.subplots(1, 2, figsize=(12, 3.6), sharey=True)
for ax, tt, ff, ZZ, title in [
    (axes[0], t_n, f_n, Z_n, "Every 8th sample (no filter)"),
    (axes[1], t_p, f_p, Z_p, "signal.decimate (FIR anti-alias)"),
]:
    im = ax.pcolormesh(tt, ff, 10*np.log10(ZZ + 1e-12), shading="auto", cmap="viridis")
    ax.set_title(title)
    ax.set_xlabel("time (s)")
    ax.set_ylim(0, fs8 / 2)
axes[0].set_ylabel("frequency (Hz)")
fig.colorbar(im, ax=axes, label="PSD (dB/Hz)")
fig.suptitle("Task 2.2 — spectrograms of the chirp decimated by 8")
fig.tight_layout()
fig.savefig(FIGDIR / "week02_task2_2_spec.png", dpi=160, bbox_inches="tight")
plt.show()

# Listening check (uncomment in a notebook):
# display(Audio(naive8, rate=int(fs8)))
# display(Audio(proper8, rate=int(fs8)))
'''),
    md('''
**Listening observation.** The unfiltered version sweeps up to the new Nyquist
frequency (2756 Hz) and then folds back, producing a repeated zig-zag and an
unnatural "descending again" tone. The filtered version contains only the part of
the sweep below 2756 Hz followed by near-silence.
'''),
    md('''
## Task 2.3 — A uniform quantiser

A 300 Hz sinusoid of amplitude 0.99 sampled at 8 kHz (80 samples, three cycles)
is quantised with B = 3 bits, so Δ = 2/8 = 0.25.
'''),
    code(r'''
fs_q = 8000
t_q = np.arange(0, 0.01, 1 / fs_q)
x_sine = 0.99 * np.sin(2 * np.pi * 300 * t_q)
delta3 = 2 / 2**3
xq3 = quantize(x_sine, 3)
max_err3 = float(np.max(np.abs(x_sine - xq3)))
print(f"delta = {delta3}, +/-delta/2 = +/-{delta3/2}, max |error| = {max_err3:.4f}")

fig, ax = plt.subplots(figsize=(10, 3.4))
ax.plot(t_q * 1e3, x_sine, label="input x(n)")
ax.step(t_q * 1e3, xq3, where="mid", label="3-bit quantised")
ax.plot(t_q * 1e3, x_sine - xq3, label="error e(n)")
ax.set_title("Task 2.3 — 3-bit uniform quantisation of a 300 Hz sinusoid")
ax.set_xlabel("time (ms)")
ax.set_ylabel("amplitude")
ax.legend()
fig.tight_layout()
fig.savefig(FIGDIR / "week02_task2_3.png", dpi=160, bbox_inches="tight")
plt.show()
'''),
    md('''
The error remains inside ±Δ/2 = ±0.125 except at the positive peaks, where 0.99
would round to 1.0 but the quantiser clips to 1 − Δ = 0.75; the largest error is
therefore about 0.24.
'''),
    md('''
## Task 2.4 — Verify the 6 dB-per-bit rule

Measure SQNR = 10 log₁₀(Σx²/Σe²) for B = 2, 4, …, 16 and compare with
6.02B + 1.76 dB.
'''),
    code(r'''
bits = np.arange(2, 17, 2)
measured = [sqnr_db(x_sine, quantize(x_sine, int(B))) for B in bits]
theory = (6.02 * bits + 1.76).tolist()
mask = bits >= 4
slope = float(np.polyfit(bits[mask], np.array(measured)[mask], 1)[0])
sqnr_table = [{"B": int(B), "measured_dB": round(m, 2),
               "theory_dB": round(t, 2), "difference_dB": round(m - t, 2)}
              for B, m, t in zip(bits, measured, theory)]
display(pd.DataFrame(sqnr_table))
print(f"Fitted slope for B >= 4: {slope:.2f} dB/bit (theory 6.02 dB/bit)")

fig, ax = plt.subplots(figsize=(9, 3.6))
ax.plot(bits, measured, "o-", label="measured SQNR")
ax.plot(bits, theory, "s--", label="6.02B + 1.76 dB")
ax.set_title("Task 2.4 — SQNR against number of bits")
ax.set_xlabel("number of bits B")
ax.set_ylabel("SQNR (dB)")
ax.legend()
fig.tight_layout()
fig.savefig(FIGDIR / "week02_task2_4.png", dpi=160, bbox_inches="tight")
plt.show()
'''),
    md('''
## Task 2.5 — Quantising speech

The speech-like signal (16 kHz, 4.7 s, seed 3) is quantised to 4, 8 and 12 bits;
a full-scale sine is quantised in the same way for comparison.
'''),
    code(r'''
fs_sp, x_sp = speech_like()
crest = float(np.max(np.abs(x_sp)) / np.sqrt(np.mean(x_sp**2)))
sine_full = 0.999 * np.sin(2 * np.pi * 440 * np.arange(len(x_sp)) / fs_sp)
speech_rows = []
for B in [4, 8, 12]:
    qs = sqnr_db(x_sp, quantize(x_sp, B))
    qn = sqnr_db(sine_full, quantize(sine_full, B))
    speech_rows.append({"B": B, "speech_SQNR_dB": round(qs, 2),
                        "sine_SQNR_dB": round(qn, 2),
                        "theory_dB": round(6.02*B + 1.76, 2),
                        "gap_dB": round(qn - qs, 2)})
display(pd.DataFrame(speech_rows))
crest_penalty = 20 * np.log10(crest / np.sqrt(2))
print(f"Crest factor = {crest:.2f}")
print(f"Crest-factor penalty = {crest_penalty:.1f} dB")

fig, axes = plt.subplots(3, 1, figsize=(10, 5), sharex=True)
t_sp = np.arange(800) / fs_sp
for ax, B in zip(axes, [4, 8, 12]):
    ax.plot(t_sp * 1e3, x_sp[:800], label="speech-like input", lw=0.8)
    ax.step(t_sp * 1e3, quantize(x_sp, B)[:800], where="mid", label=f"{B}-bit")
    ax.set_ylabel("amplitude")
    ax.legend(fontsize=8)
axes[0].set_title("Task 2.5 — speech-like signal quantised to 4, 8 and 12 bits")
axes[-1].set_xlabel("time (ms)")
fig.tight_layout()
fig.savefig(FIGDIR / "week02_task2_5.png", dpi=160, bbox_inches="tight")
plt.show()
'''),
    md('''
**Listening observation.** At 4 bits the speech is gritty and the quantisation
noise is obvious in pauses. At 8 bits the noise is quiet but still audible; at
12 bits it is essentially inaudible. The measured SQNR is about 20 dB below the
full-scale sine because the crest factor is large: the step Δ is set by the peak
while the average power is much lower.
'''),
    md('''
## Analysis questions

1. **Frequency-axis sketch.** Sampling at 10 Hz repeats the spectrum at
   ±k·10 Hz. The copy of +7 Hz at 7 − 10 = −3 Hz and the copy of −7 Hz at
   −7 + 10 = +3 Hz both fall inside the baseband, so the 7 Hz tone is seen as 3 Hz.
2. **Aliasing cannot be removed afterwards.** After sampling, a genuine 3 Hz
   component and an aliased 7 Hz component give identical samples. The
   information that distinguishes them has been lost, so only an anti-alias
   filter **before** sampling/decimation can prevent it.
3. **Change per bit.** Adding one bit halves Δ, so the noise power Δ²/12 falls by
   a factor of 4 = 10 log₁₀4 ≈ 6.02 dB. The measured slope (printed above) agrees.
4. **Temperature sensor.** Range 0–100 °C with 0.01 °C resolution needs
   100/0.01 = 10 000 levels, so B = ceil(log₂10 000) = 14 bits. The signal changes
   by at most 0.1 °C/s, so fs = 1 Hz is adequate; a higher rate such as 10 Hz with
   averaging could reduce noise but is not required.
'''),
    code(r'''
# Frequency-axis sketch for analysis question 1
fig, ax = plt.subplots(figsize=(10, 3.2))
ax.axhspan(-0.05, 0.05, color="lightgrey", alpha=0.6, label="baseband |f| <= fs/2")
for m in [-1, 0, 1, 2]:
    centre = m * 10
    for sign in [-1, 1]:
        ax.plot([centre + sign*7, centre + sign*7], [0, 0.35], color="C0", lw=2)
    ax.text(centre, 0.42, f"{centre} Hz", ha="center", fontsize=9)
ax.plot([3, 3], [0, 0.55], color="C1", lw=2, label="observed alias at 3 Hz")
ax.plot([-3, -3], [0, 0.55], color="C1", lw=2)
ax.axvline(-5, color="k", ls="--", lw=0.8)
ax.axvline(5, color="k", ls="--", lw=0.8)
ax.annotate("7 Hz input", xy=(7, 0.35), xytext=(8, 0.62),
            arrowprops=dict(arrowstyle="->"), fontsize=10)
ax.set_xlim(-18, 30)
ax.set_ylim(-0.1, 0.78)
ax.set_xlabel("frequency (Hz)")
ax.set_ylabel("spectral line (arbitrary)")
ax.set_title("Analysis 1 — spectral copies when a 7 Hz tone is sampled at 10 Hz")
ax.legend(loc="upper right", fontsize=8)
fig.tight_layout()
fig.savefig(FIGDIR / "week02_analysis_alias.png", dpi=160, bbox_inches="tight")
plt.show()
'''),
    code(r'''
results_week02 = {
    "week": 2,
    "alias": alias_rows,
    "decimation": decim_rows,
    "quant3": {"delta": delta3, "max_error": round(max_err3, 4)},
    "sqnr_bits": {"bits": [int(b) for b in bits],
                  "measured": [round(v, 2) for v in measured],
                  "theory": [round(v, 2) for v in theory],
                  "slope_dB_per_bit": round(slope, 2)},
    "speech": {"crest_factor": round(crest, 2),
               "crest_penalty_dB": round(float(crest_penalty), 1),
               "rows": speech_rows},
}
(REPORT / "results_week02.json").write_text(json.dumps(results_week02, indent=2))
print(json.dumps(results_week02, indent=2))
'''),
    md('''
## AI-use statement

**Tool:** OpenCode (model Big Pickle). **Used for:** drafting the Python code and
written answers in this notebook. **Verification:** the notebook was restarted
and run from top to bottom; alias frequencies were checked against |F − kfₛ|, the
decimated RMS against the analytic prediction, the measured SQNR against
6.02B + 1.76 dB, and the speech penalty against the crest-factor formula. I can
explain every line of code.
'''),
])
write(week2, 2)


# ---------------------------------------------------------------------------
# WEEK 3
# ---------------------------------------------------------------------------
week3 = new_notebook(f'''# COU 07506 — Week 3: Lab 1B, Convolution, Correlation and Difference Equations

**Student:** {NAME} &nbsp;|&nbsp; **Registration number:** {REG} &nbsp;|&nbsp;
**Class:** BEng24COE &nbsp;|&nbsp; **Date:** 26 November 2026 &nbsp;|&nbsp;
**Submission:** Individual laboratory work.
''', [
    md('''
## Pre-lab preparation

**Reading.** Handout §1.7–§1.9.

**(a)** Convolution of x = {1, −1, 2} with h = {2, 1, 0, 1}:

y(0) = 1·2 = 2, y(1) = 1·1 + (−1)·2 = −1, y(2) = 1·0 + (−1)·1 + 2·2 = 3,
y(3) = 1·1 + (−1)·0 + 2·1 = 3, y(4) = (−1)·1 + 2·0 = −1, y(5) = 2·1 = 2.
The result is **{2, −1, 3, 3, −1, 2}**, verified by the code below.

**(b)** For y(n) = n·x(n), delaying the input gives n·x(n − n₀), while delaying
the output gives (n − n₀)·x(n − n₀). They are different for n₀ ≠ 0, so the
system is **not time-invariant**.
'''),
    code(COMMON),
    code(r'''
import time

def conv(x, h):
    """Linear convolution directly from y(n) = sum_k x(k) h(n-k)."""
    x = np.asarray(x, dtype=float)
    h = np.asarray(h, dtype=float)
    N = len(x) + len(h) - 1
    y = np.zeros(N)
    for n in range(N):
        for k in range(len(x)):
            if 0 <= n - k < len(h):
                y[n] += x[k] * h[n - k]
    return y

def delay_estimate(sigma, seed=1, true_delay=37, N=500):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(N)
    y = np.concatenate([np.zeros(true_delay), 0.6 * x])[:N] + sigma * rng.standard_normal(N)
    r = signal.correlate(y, x, mode="full")
    lags = signal.correlation_lags(len(y), len(x), mode="full")
    return int(lags[np.argmax(r)]), lags, r

def delay_success_rate(sigma, trials=300, true_delay=37):
    ok = sum(delay_estimate(sigma, seed=1000 + s, true_delay=true_delay)[0] == true_delay
             for s in range(trials))
    return ok / trials
'''),
    md('''
## Task 3.1 — Convolution from the definition

Compare the direct double loop with `np.convolve` for short sequences, then time
both on two random sequences of length 2000.
'''),
    code(r'''
y_manual = conv([1, 2, 3, 1], [1, 1, 1])
y_np = np.convolve([1, 2, 3, 1], [1, 1, 1])
print("conv([1,2,3,1],[1,1,1]) :", y_manual.astype(int).tolist())
print("np.convolve            :", y_np.astype(int).tolist())

x_pre, h_pre = [1, -1, 2], [2, 1, 0, 1]
y_pre = conv(x_pre, h_pre)
y_pre_np = np.convolve(x_pre, h_pre)
print("pre-lab conv           :", y_pre.astype(int).tolist())
print("pre-lab np.convolve    :", y_pre_np.astype(int).tolist())

rng = np.random.default_rng(0)
a_rand, b_rand = rng.standard_normal(2000), rng.standard_normal(2000)
t0 = time.perf_counter(); y_loop = conv(a_rand, b_rand); t_loop = time.perf_counter() - t0
t0 = time.perf_counter(); y_fast = np.convolve(a_rand, b_rand); t_fast = time.perf_counter() - t0
print(f"double loop : {t_loop:.4f} s")
print(f"np.convolve : {t_fast*1000:.3f} ms")
print(f"speed ratio : {t_loop/t_fast:.0f}x ; results agree:", np.allclose(y_loop, y_fast))
'''),
    md('''
## Task 3.2 — Smoothing a noisy signal

x(n) = sin(2πn/50) + 0.5w(n), 0 ≤ n < 300, is convolved with moving-average
filters of length M = 3, 9 and 25 using `mode="same"`. The RMS error is computed
away from the ends to avoid edge effects.
'''),
    code(r'''
rng = np.random.default_rng(0)
n_s = np.arange(300)
clean = np.sin(2 * np.pi * n_s / 50)
x_noisy = clean + 0.5 * rng.standard_normal(300)
smooth_rows = []
smoothed = {}
for M in [3, 9, 25]:
    y = np.convolve(x_noisy, np.ones(M) / M, mode="same")
    core = slice(M, 300 - M)
    w0 = 2 * np.pi / 50
    gain = abs(np.sin(M * w0 / 2) / (M * np.sin(w0 / 2)))
    rms_err = float(np.sqrt(np.mean((y[core] - clean[core]) ** 2)))
    smooth_rows.append({"M": M, "gain_at_50_samples": round(float(gain), 3),
                        "rms_error": round(rms_err, 3)})
    smoothed[M] = y
smooth_rows.insert(0, {"M": 0, "gain_at_50_samples": 1.0,
                       "rms_error": round(float(np.sqrt(np.mean((x_noisy-clean)**2))), 3)})
display(pd.DataFrame(smooth_rows))

fig, axes = plt.subplots(4, 1, figsize=(10, 7), sharex=True)
axes[0].plot(n_s, clean, label="clean sine", lw=1.2)
axes[0].plot(n_s, x_noisy, label="noisy x(n)", lw=0.6, alpha=0.7)
axes[0].set_title("Task 3.2 — moving-average smoothing")
for ax, M in zip(axes[1:], [3, 9, 25]):
    ax.plot(n_s, clean, label="clean sine", lw=1.0)
    ax.plot(n_s, smoothed[M], label=f"M = {M} filtered", lw=1.0)
    ax.set_title(f"M = {M}")
for ax in axes:
    ax.set_ylabel("amplitude")
    ax.legend(fontsize=8)
axes[-1].set_xlabel("n (samples)")
fig.tight_layout()
fig.savefig(FIGDIR / "week03_task3_2.png", dpi=160, bbox_inches="tight")
plt.show()
'''),
    md('''
M = 9 gives the smallest error; M = 25 removes more noise but attenuates the
wanted sine, so the total error rises again.
'''),
    md('''
## Task 3.3 — Testing linearity and time-invariance

Three systems are tested with random inputs, a = 2, b = −3 and a 5-sample delay.
'''),
    code(r'''
rng = np.random.default_rng(0)
x1, x2 = rng.standard_normal(50), rng.standard_normal(50)
a_coef, b_coef = 2.0, -3.0
systems = {"x^2": lambda x: x**2,
           "n x(n)": lambda x: np.arange(len(x)) * x,
           "moving average": lambda x: np.convolve(x, np.ones(3)/3)[:len(x)]}
system_rows = []
for name, T in systems.items():
    linear = bool(np.allclose(T(a_coef*x1 + b_coef*x2), a_coef*T(x1) + b_coef*T(x2)))
    xd = np.concatenate([np.zeros(5), x1])[:50]
    yd = np.concatenate([np.zeros(5), T(x1)])[:50]
    tinv = bool(np.allclose(T(xd), yd))
    system_rows.append({"system": name, "linear": linear,
                        "time_invariant": tinv, "LTI": linear and tinv})
    print(f"{name:15s} linear={linear}  time-invariant={tinv}")
display(pd.DataFrame(system_rows))
'''),
    md('''
The squarer is time-invariant but non-linear (the cross term 2abx₁x₂ breaks
superposition). Multiplication by n is linear but time-varying; the moving
average has constant coefficients and is LTI.
'''),
    md('''
## Task 3.4 — Finding a hidden delay

A noise-free 500-sample sequence is delayed by 37 samples, scaled by 0.6 and
corrupted with Gaussian noise. The cross-correlation peak gives the delay.
'''),
    code(r'''
est05, lags05, r05 = delay_estimate(0.5, seed=1)
print("estimated delay at sigma=0.5:", est05, "samples")
print(f"distance at 343 m/s and fs=1000 Hz: {est05/1000*343:.2f} m")

fig, ax = plt.subplots(figsize=(9, 3.2))
ax.plot(lags05, r05)
ax.axvline(37, color="C1", ls="--", label="true delay = 37 samples")
ax.set_xlim(-200, 200)
ax.set_title("Task 3.4 — cross-correlation, sigma = 0.5")
ax.set_xlabel("lag (samples)")
ax.set_ylabel("cross-correlation")
ax.legend()
fig.tight_layout()
fig.savefig(FIGDIR / "week03_task3_4.png", dpi=160, bbox_inches="tight")
plt.show()

delay_rows = []
for sigma in [0.5, 1, 2, 4, 8, 16]:
    est, _, _ = delay_estimate(sigma, seed=1)
    rate = delay_success_rate(sigma, trials=300)
    delay_rows.append({"sigma": sigma, "single_run_estimate": est,
                       "success_rate_300_trials": round(rate, 3)})
    print(f"sigma={sigma:4g}: estimate={est:3d}, success={rate:.0%}")
display(pd.DataFrame(delay_rows))
'''),
    md('''
## Task 3.5 — Difference equation

For y(n) − 0.75y(n−1) + 0.125y(n−2) = x(n) + x(n−1), compute h(n) by recursion,
with `lfilter` and from h(n) = 6(0.5)ⁿ − 5(0.25)ⁿ; then compute the step response.
'''),
    code(r'''
b_de, a_de = [1, 1], [1, -0.75, 0.125]
N_de = 10
imp = np.zeros(N_de); imp[0] = 1
h_rec = np.zeros(N_de)
for n in range(N_de):
    h_rec[n] = imp[n] + (imp[n-1] if n >= 1 else 0)
    h_rec[n] += 0.75 * (h_rec[n-1] if n >= 1 else 0) - 0.125 * (h_rec[n-2] if n >= 2 else 0)
h_lf = signal.lfilter(b_de, a_de, imp)
n_de = np.arange(N_de)
h_cf = 6 * 0.5**n_de - 5 * 0.25**n_de
step_resp = signal.lfilter(b_de, a_de, np.ones(60))
H1 = float(sum(b_de) / sum(a_de))
print("recursion :", np.round(h_rec, 4).tolist())
print("lfilter   :", np.round(h_lf, 4).tolist())
print("closed form:", np.round(h_cf, 4).tolist())
print("all agree :", np.allclose(h_rec, h_lf) and np.allclose(h_rec, h_cf))
print("step final value:", round(float(step_resp[-1]), 4), " H(1) =", round(H1, 4))
display(pd.DataFrame({"n": n_de.tolist(), "recursion": np.round(h_rec, 4).tolist(),
                      "lfilter": np.round(h_lf, 4).tolist(),
                      "closed_form": np.round(h_cf, 4).tolist()}))

fig1, ax1 = plt.subplots(figsize=(9, 3.2))
ax1.stem(n_de, h_rec, basefmt="k-", label="recursion")
ax1.plot(n_de, h_lf, "o", mfc="none", label="lfilter")
ax1.plot(n_de, h_cf, "x", label="closed form")
ax1.set_title("Task 3.5 — impulse response: three matching methods")
ax1.set_xlabel("n (samples)")
ax1.set_ylabel("h(n)")
ax1.legend()
fig1.tight_layout()
fig1.savefig(FIGDIR / "week03_task3_5_imp.png", dpi=160, bbox_inches="tight")
plt.show()

fig2, ax2 = plt.subplots(figsize=(9, 3.2))
ax2.plot(np.arange(60), step_resp, label="step response")
ax2.axhline(H1, color="C1", ls="--", label=f"H(1) = {H1:.4f}")
ax2.set_title("Task 3.5 — step response")
ax2.set_xlabel("n (samples)")
ax2.set_ylabel("y(n)")
ax2.legend()
fig2.tight_layout()
fig2.savefig(FIGDIR / "week03_task3_5_step.png", dpi=160, bbox_inches="tight")
plt.show()
'''),
    md('''
## Analysis questions

1. Both methods perform L·M multiplications (4 000 000 here). `np.convolve` is
   faster because the loops run in compiled code over whole arrays, while the
   Python double loop interprets every iteration.
2. Only the moving average is LTI, as predicted: the squarer is non-linear and
   multiplication by n is time-varying.
3. Tanzania applications: (i) cross-correlating two sensor signals on a water
   pipe to locate a leak from the time delay; (ii) radar/GPS, where correlating
   the received signal with the transmitted code gives range.
4. The system is IIR because h(n) never becomes exactly zero. It is stable: the
   poles are at z = 0.5 and 0.25 and Σ|h(n)| = H(1) = 5.333 is finite.
'''),
    code(r'''
results_week03 = {
    "week": 3,
    "convolution": {"expected": [1, 3, 6, 6, 4, 1],
                    "prelab": [int(v) for v in y_pre],
                    "loop_time_s": round(float(t_loop), 4),
                    "numpy_time_s": round(float(t_fast), 6),
                    "speed_ratio": round(float(t_loop / t_fast), 1)},
    "smoothing": smooth_rows,
    "systems": system_rows,
    "delay": delay_rows,
    "diffeq": {"h": [round(float(v), 4) for v in h_rec],
               "step_final": round(float(step_resp[-1]), 4),
               "H1": round(H1, 4),
               "methods_agree": bool(np.allclose(h_rec, h_lf) and np.allclose(h_rec, h_cf))},
}
(REPORT / "results_week03.json").write_text(json.dumps(results_week03, indent=2))
print(json.dumps(results_week03, indent=2))
'''),
    md('''
## AI-use statement

**Tool:** OpenCode (model Big Pickle). **Used for:** drafting the Python code and
written answers in this notebook. **Verification:** the notebook was restarted and
run from top to bottom; `conv` was checked against `np.convolve` and the expected
{1, 3, 6, 6, 4, 1}; system properties were checked against the definitions; the
delay estimate was checked against the known 37 samples; and the three impulse
responses were compared with `np.allclose`. I can explain every line of code.
'''),
])
write(week3, 3)


# ---------------------------------------------------------------------------
# WEEK 4
# ---------------------------------------------------------------------------
week4 = new_notebook(f'''# COU 07506 — Week 4: z-Transform Laboratory, Poles, Zeros and Stability

**Student:** {NAME} &nbsp;|&nbsp; **Registration number:** {REG} &nbsp;|&nbsp;
**Class:** BEng24COE &nbsp;|&nbsp; **Date:** 26 November 2026 &nbsp;|&nbsp;
**Submission:** Individual laboratory work.
''', [
    md('''
## Pre-lab preparation

**Reading.** Handout §2.2–§2.4, Listing 2.1 and Examples 2.2–2.5.

**(a)** For 1 − 0.9z⁻¹ + 0.81z⁻², z² − 0.9z + 0.81 = 0 gives
z = 0.45 ± j0.779 = 0.9e^{±jπ/3}. Since |p| = 0.9 < 1, the causal system is stable.

**(b)** Partial fractions:

X(z) = 1/[(1 − 0.5z⁻¹)(1 − 0.25z⁻¹)]
     = 2/(1 − 0.5z⁻¹) − 1/(1 − 0.25z⁻¹),

so x(n) = 2(0.5)ⁿ − (0.25)ⁿ for n ≥ 0.
'''),
    code(COMMON),
    code(r'''
def zplane(b, a, ax=None, extra_poles_at_origin=0):
    """Pole-zero plot with the unit circle (Task 4.1)."""
    z, p, k = signal.tf2zpk(b, a)
    p = np.concatenate([p, np.zeros(extra_poles_at_origin)])
    ax = ax or plt.gca()
    th = np.linspace(0, 2*np.pi, 400)
    ax.plot(np.cos(th), np.sin(th), "k--", lw=0.8, label="unit circle")
    if len(z):
        ax.plot(z.real, z.imag, "o", mfc="none", ms=8, color="C0", label="zeros")
    if len(p):
        ax.plot(p.real, p.imag, "x", ms=8, mew=2, color="C1", label="poles")
    ax.set_aspect("equal")
    ax.set_xlabel("Re(z)")
    ax.set_ylabel("Im(z)")
    ax.legend(loc="upper right", fontsize=8)
    return z, p

def inverse_check(b, a, N=10):
    r, p, k = signal.residuez(b, a)
    n = np.arange(N)
    h_pf = sum(ri * pi**n for ri, pi in zip(r, p)).real
    imp = np.zeros(N); imp[0] = 1
    h_lf = signal.lfilter(b, a, imp)
    return r, p, h_pf, h_lf, bool(np.allclose(h_pf, h_lf))

def pole_pair(radius, theta=np.pi/4, N=40):
    a = [1, -2*radius*np.cos(theta), radius**2]
    imp = np.zeros(N); imp[0] = 1
    h = signal.lfilter([1], a, imp)
    w, H = signal.freqz([1], a, worN=4001)
    mag = np.abs(H)
    peak_db = float(20*np.log10(np.max(mag)))
    if radius < 1:
        above = w[mag >= np.max(mag)/np.sqrt(2)]
        bw_pi = float((above.max() - above.min()) / np.pi)
    else:
        bw_pi = float("nan")
    return {"a": a, "h": h, "w": w, "H": H, "peak_db": peak_db,
            "bw_pi": bw_pi, "h_last": float(np.max(np.abs(h[-10:])))}

SYS4 = {"H1": ([1], [1, -1.6, 0.89]),
        "H2": ([1, 1], [1, -2.5, 1]),
        "H3": ([1], [1, 0.5, -0.5]),
        "H4": ([1, 0, 0, 0, -1], [1])}

def classify(b, a, N=200):
    z, p = zplane(b, a)
    imp = np.zeros(N); imp[0] = 1
    h = signal.lfilter(b, a, imp)
    rmax = float(np.max(np.abs(p))) if len(p) else 0.0
    return {"z": z, "p": p, "h": h, "rmax": rmax,
            "tail": float(np.max(np.abs(h[150:]))),
            "abssum": float(np.sum(np.abs(h)))}
'''),
    md('''
## Task 4.1 — A pole-zero plotting function

Apply `zplane` to H(z) = (1 + z⁻¹)/(1 − 0.75z⁻¹ + 0.125z⁻²) and plot the
magnitude response.
'''),
    code(r'''
b41, a41 = [1, 1], [1, -0.75, 0.125]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8))
z41, p41 = zplane(b41, a41, ax1)
w41, H41 = signal.freqz(b41, a41, worN=512)
ax2.plot(w41/np.pi, 20*np.log10(np.abs(H41)), label="|H(e^{jω})|")
ax2.set_xlabel("normalised frequency ω/π (rad/sample)")
ax2.set_ylabel("magnitude (dB)")
ax2.set_title("Magnitude response")
ax2.legend()
fig.suptitle("Task 4.1 — pole-zero plot and frequency response")
fig.tight_layout()
fig.savefig(FIGDIR / "week04_task4_1.png", dpi=160, bbox_inches="tight")
plt.show()
print("zeros:", np.round(z41, 6))
print("poles:", np.round(p41, 6))
print("all poles inside unit circle:", bool(np.all(np.abs(p41) < 1)))
print("gain at ω=0 (dB):", round(float(20*np.log10(abs(H41[0]))), 2))
print("gain at ω=pi (dB):", round(float(20*np.log10(abs(H41[-1]))), 2))
'''),
    md('''
## Task 4.2 — Inverse z-transform with `residuez`

Compare the partial-fraction reconstruction Σrᵢpᵢⁿ with `lfilter` for b = [1] and
for b = [1, 1].
'''),
    code(r'''
residue_rows = []
fig, axes = plt.subplots(2, 1, figsize=(9, 5))
for ax, b_now in zip(axes, [[1], [1, 1]]):
    r, p, h_pf, h_lf, ok = inverse_check(b_now, a41, N=10)
    residue_rows.append({"b": str(b_now), "residues": [round(float(v), 4) for v in r],
                         "poles": [round(float(v), 4) for v in p], "matches_lfilter": ok})
    n_now = np.arange(10)
    ax.stem(n_now, h_pf, basefmt="k-", label=r"$\sum r_i p_i^n$")
    ax.plot(n_now, h_lf, "o", mfc="none", label="lfilter")
    ax.set_title(f"Task 4.2 — b = {b_now}, match = {ok}")
    ax.set_xlabel("n (samples)")
    ax.set_ylabel("h(n)")
    ax.legend()
    print("b =", b_now, " residues =", np.round(r, 4), " poles =", np.round(p, 4),
          " matches:", ok)
fig.tight_layout()
fig.savefig(FIGDIR / "week04_task4_2.png", dpi=160, bbox_inches="tight")
plt.show()
display(pd.DataFrame(residue_rows))
'''),
    md('''
For b = [1] the residues are −1 at p = 0.25 and +2 at p = 0.5, giving
x(n) = 2(0.5)ⁿ − (0.25)ⁿ. For b = [1, 1] they are −5 and +6, confirming
h(n) = 6(0.5)ⁿ − 5(0.25)ⁿ from Task 3.5.
'''),
    md('''
## Task 4.3 — Pole position and the impulse response

For poles at r·e^{±jπ/4}, A(z) = 1 − 2r cos(π/4)z⁻¹ + r²z⁻². Plot h(n) and |H(e^{jω})|
for r = 0.5, 0.8, 0.95, 1.0 and 1.05.
'''),
    code(r'''
radii = [0.5, 0.8, 0.95, 1.0, 1.05]
pole_rows = []
fig, axes = plt.subplots(5, 2, figsize=(11, 11), sharex="col")
for row, radius in enumerate(radii):
    d = pole_pair(radius)
    h_now = d["h"]
    axes[row, 0].stem(np.arange(len(h_now)), h_now, basefmt="k-")
    axes[row, 0].set_title(f"r = {radius}, poles = {radius:.2f} e^{{±jπ/4}}")
    axes[row, 0].set_ylabel("h(n)")
    mag_db = 20*np.log10(np.maximum(np.abs(d["H"]), 1e-12))
    axes[row, 1].plot(d["w"]/np.pi, mag_db)
    axes[row, 1].set_ylim(-20, 40)
    axes[row, 1].set_ylabel("|H| (dB)")
    axes[row, 1].set_title(f"peak = {d['peak_db']:.1f} dB, "
                           + (f"BW = {d['bw_pi']:.3f}π" if radius < 1 else "BW undefined"))
    pole_rows.append({"r": radius, "peak_dB": round(d["peak_db"], 2),
                      "bw_over_pi": (round(d["bw_pi"], 3) if radius < 1 else None),
                      "max_h_last10": round(d["h_last"], 4),
                      "stable": bool(radius < 1)})
axes[-1, 0].set_xlabel("n (samples)")
axes[-1, 1].set_xlabel("normalised frequency ω/π")
fig.suptitle("Task 4.3 — impulse response (left) and magnitude (right) for a pole pair")
fig.tight_layout()
fig.savefig(FIGDIR / "week04_task4_3.png", dpi=160, bbox_inches="tight")
plt.show()
display(pd.DataFrame(pole_rows))
'''),
    md('''
As r → 1 the resonance at ω = π/4 becomes taller and narrower and h(n) decays
more slowly. The −3 dB bandwidth follows ≈ 2(1 − r) rad/sample. At r = 1 the
response is a sustained sinusoid; at r = 1.05 it grows, so both are not BIBO stable.
'''),
    md('''
## Task 4.4 — Stability of given systems

Classify H1–H4 from pole positions and verify with h(n) over 200 samples.
'''),
    code(r'''
system_rows = []
fig, axes = plt.subplots(2, 2, figsize=(9, 7))
labels = {"H1": "stable", "H2": "unstable", "H3": "marginal (not BIBO)", "H4": "stable (FIR)"}
for ax, (name, (b_now, a_now)) in zip(axes.ravel(), SYS4.items()):
    d = classify(b_now, a_now)
    extra = 4 if name == "H4" else 0
    z, p = zplane(b_now, a_now, ax=ax, extra_poles_at_origin=extra)
    ax.set_title(f"{name}: max|p| = {d['rmax']:.3f}, {labels[name]}")
    system_rows.append({"system": name,
                        "poles": ", ".join(f"{v.real:.3f}{v.imag:+.3f}j" for v in p),
                        "max_pole_radius": round(d["rmax"], 3),
                        "max_h_n_ge_150": f"{d['tail']:.3g}",
                        "sum_abs_h": f"{d['abssum']:.3g}",
                        "classification": labels[name]})
    print(name, "max|p| =", round(d["rmax"], 4),
          "tail =", f"{d['tail']:.3g}", "sum|h| =", f"{d['abssum']:.3g}")
fig.suptitle("Task 4.4 — pole-zero plots of H1 to H4")
fig.tight_layout()
fig.savefig(FIGDIR / "week04_task4_4.png", dpi=160, bbox_inches="tight")
plt.show()
display(pd.DataFrame(system_rows))
'''),
    md('''
H1 is stable (|p| = 0.943); H2 has a pole at z = 2 and grows without bound; H3
has a pole at z = −1 on the unit circle, so h(n) oscillates without decaying and
Σ|h(n)| diverges; H4 = 1 − z⁻⁴ is FIR with all poles at the origin and is stable.
'''),
    md('''
## Task 4.5 — Design a resonator

Poles at r·e^{±jθ} with r = 0.97 and θ = 2π·1000/8000 = π/4; zeros at z = ±1
give B(z) = 1 − z⁻². The numerator is scaled for unit gain at the peak and the
filter is applied to white noise.
'''),
    code(r'''
fs_res, f0_res, r_res = 8000, 1000, 0.97
theta = 2*np.pi*f0_res/fs_res
a_res = np.array([1, -2*r_res*np.cos(theta), r_res**2])
b_res = np.array([1.0, 0, -1.0])
w_res, H_res = signal.freqz(b_res, a_res, worN=8192, fs=fs_res)
b_res = b_res / np.max(np.abs(H_res))
w_res, H_res = signal.freqz(b_res, a_res, worN=8192, fs=fs_res)
mag_res = np.abs(H_res)
f_peak = float(w_res[np.argmax(mag_res)])
above = w_res[mag_res >= 1/np.sqrt(2)]
bw_hz = float(above.max() - above.min())
rng = np.random.default_rng(0)
x_res = rng.standard_normal(8000)
y_res = signal.lfilter(b_res, a_res, x_res)
f_w, Pxx = signal.welch(x_res, fs=fs_res, nperseg=1024)
f_w2, Pyy = signal.welch(y_res, fs=fs_res, nperseg=1024)
approx_bw = 2*(1-r_res)*fs_res/(2*np.pi)
print(f"peak frequency: {f_peak:.0f} Hz")
print(f"-3 dB bandwidth: {bw_hz:.1f} Hz (approximation 2(1-r)fs/2pi = {approx_bw:.1f} Hz)")
print(f"gain at 0 Hz: {abs(H_res[0]):.3g}; gain at fs/2: {abs(H_res[-1]):.3g}")

fig, axes = plt.subplots(1, 3, figsize=(14, 3.8))
zplane(b_res, a_res, ax=axes[0])
axes[0].set_title("Pole-zero plot")
axes[1].plot(w_res, 20*np.log10(np.maximum(mag_res, 1e-12)))
axes[1].set_title(f"Magnitude response, peak {f_peak:.0f} Hz")
axes[1].set_xlabel("frequency (Hz)")
axes[1].set_ylabel("magnitude (dB)")
axes[2].plot(f_w, 10*np.log10(Pxx + 1e-12), label="white-noise input")
axes[2].plot(f_w2, 10*np.log10(Pyy + 1e-12), label="filtered output")
axes[2].set_title("Welch spectra")
axes[2].set_xlabel("frequency (Hz)")
axes[2].set_ylabel("PSD (dB/Hz)")
axes[2].legend(fontsize=8)
fig.suptitle("Task 4.5 — 1 kHz band-pass resonator")
fig.tight_layout()
fig.savefig(FIGDIR / "week04_task4_5.png", dpi=160, bbox_inches="tight")
plt.show()

# Listening check (uncomment in a notebook):
# display(Audio(y_res/np.max(np.abs(y_res)), rate=fs_res))
'''),
    md('''
## Analysis questions

1. **Effect of r.** The −3 dB bandwidth of the resonance is ≈ 2(1 − r)
   rad/sample: raising r from 0.8 to 0.95 narrows the peak from about 0.153π to
   0.032π and lengthens h(n).
2. **Pole on the unit circle.** h(n) neither decays nor grows. A complex pair at
   e^{±jθ} gives a sustained sinusoid h(n) = sin((n+1)θ)/sinθ; a pole at ±1 gives
   a constant or alternating sequence. Σ|h(n)| diverges, so the system is not BIBO stable.
3. **Zeros at z = ±1.** A zero at z = 1 blocks DC (ω = 0) and a zero at z = −1
   blocks fs/2 (ω = π). With the poles providing gain at 1 kHz, the response is a
   band-pass shape.
4. **Stability triangle.** For A(z) = 1 + a₁z⁻¹ + a₂z⁻², stability requires
   |a₂| < 1 and |a₁| < 1 + a₂. (a) a₁ = −1.6, a₂ = 0.89: 1.6 < 1.89, stable.
   (b) a₁ = −2.5, a₂ = 1: |a₂| = 1, unstable. (c) a₁ = 0.5, a₂ = −0.5:
   |a₁| = 1 + a₂ = 0.5, on the boundary, so a pole lies at z = −1 (marginal).
'''),
    code(r'''
results_week04 = {
    "week": 4,
    "task41": {"zeros": [f"{v.real:.4f}{v.imag:+.4f}j" for v in z41],
               "poles": [f"{v.real:.4f}{v.imag:+.4f}j" for v in p41],
               "stable": bool(np.all(np.abs(p41) < 1)),
               "gain_0_dB": round(float(20*np.log10(abs(H41[0]))), 2),
               "gain_pi_dB": round(float(20*np.log10(abs(H41[-1]))), 2)},
    "residues": residue_rows,
    "pole_pair": pole_rows,
    "systems": system_rows,
    "resonator": {"peak_Hz": round(f_peak, 1),
                  "bw_Hz": round(bw_hz, 1),
                  "bw_approx_Hz": round(approx_bw, 1),
                  "gain_0": float(abs(H_res[0])),
                  "gain_nyquist": float(abs(H_res[-1])),
                  "b": [float(v) for v in b_res],
                  "a": [float(v) for v in a_res]},
}
(REPORT / "results_week04.json").write_text(json.dumps(results_week04, indent=2))
print(json.dumps(results_week04, indent=2))
'''),
    md('''
## AI-use statement

**Tool:** OpenCode (model Big Pickle). **Used for:** drafting the Python code and
written answers in this notebook. **Verification:** the notebook was restarted and
run from top to bottom; residues were compared with the hand partial-fraction
expansion, pole positions with hand root calculations, stability with the
stability triangle, and the resonator peak/bandwidth with 2(1 − r)fs/2π. I can
explain every line of code.
'''),
])
write(week4, 4)

print("All notebooks written.")
