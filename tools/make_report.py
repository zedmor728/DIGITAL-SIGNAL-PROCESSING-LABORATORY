"""Build the Weeks 1-4 report HTML and print it to PDF with Chrome.

All numbers are read from report/results_weekNN.json, which are written by the
executed notebooks, so the report cannot drift away from the submitted code.
"""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "report"
FIG = REPORT / "figures"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")


def load(week):
    return json.loads((REPORT / f"results_week{week:02d}.json").read_text(encoding="utf-8"))


w1, w2, w3, w4 = load(1), load(2), load(3), load(4)

FIGURES = {
    1: ("week01_task1_1.png", "Unit impulse, unit step, unit ramp and (0.8)<sup>n</sup>u(n) for −5 ≤ n ≤ 10."),
    2: ("week01_task1_2a.png", "a<sup>n</sup>u(n) for a = 0.5, −0.8 and 1.1."),
    3: ("week01_task1_2b.png", "cos(2πn/8) and cos(2πn/7.5) for 0 ≤ n ≤ 40."),
    4: ("week01_task1_3.png", "Waveform of the recorded voice signal (normalised amplitude)."),
    5: ("week02_task2_1.png", "A 7 Hz cosine sampled at 10, 12, 14 and 20 Hz, with the predicted alias."),
    6: ("week02_task2_2_spec.png", "Spectrograms of the chirp decimated by 8 without filter (left) and with <code>signal.decimate</code> (right)."),
    7: ("week02_task2_3.png", "3-bit quantisation of a 300 Hz sinusoid: input, quantised signal and error."),
    8: ("week02_task2_4.png", "Measured and theoretical SQNR against the number of bits."),
    9: ("week03_task3_2.png", "Noisy sine and its moving-average smoothed versions for M = 3, 9 and 25."),
    10: ("week03_task3_4.png", "Cross-correlation between the delayed noisy signal and the original signal."),
    11: ("week03_task3_5_imp.png", "Impulse response of the system computed by recursion, <code>lfilter</code> and the closed form."),
    12: ("week03_task3_5_step.png", "Step response of the system and its final value H(1)."),
    13: ("week04_task4_1.png", "Pole-zero plot and magnitude response of H(z) = (1 + z<sup>−1</sup>)/(1 − 0.75z<sup>−1</sup> + 0.125z<sup>−2</sup>)."),
    14: ("week04_task4_3.png", "h(n) (left) and |H(e<sup>jω</sup>)| (right) for a pole pair at re<sup>±jπ/4</sup>."),
    15: ("week04_task4_4.png", "Pole-zero plots of H1 to H4 (H4 has four poles at the origin)."),
    16: ("week04_task4_5.png", "Pole-zero plot, magnitude response in Hz and Welch spectra of the white-noise input and the filtered output."),
    17: ("week02_analysis_alias.png", "Frequency-axis sketch of the 7 Hz tone sampled at 10 Hz."),
}


def figure(n):
    file, caption = FIGURES[n]
    return (f'<figure><img src="figures/{file}" alt="Figure {n}">'
            f'<figcaption>Figure {n}: {caption}</figcaption></figure>')


def table(headers, rows, caption, widths=None):
    cols = "".join(f"<th>{h}</th>" for h in headers)
    body = ""
    for r in rows:
        body += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
    style = ""
    if widths:
        style = "<colgroup>" + "".join(f'<col style="width:{x}%">' for x in widths) + "</colgroup>"
    return (f'<table>{style}<thead><tr>{cols}</tr></thead><tbody>{body}</tbody></table>'
            f'<p class="caption">{caption}</p>')


def code_block(text, lang=""):
    escaped = (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    return f'<pre><code class="{lang}">{escaped}</code></pre>'


# ---------------------------------------------------------------------------
# Tables from executed results
# ---------------------------------------------------------------------------
a = w1["a_values_at_20"]
tab1 = table(
    ["Sequence", "Definition", "Observed behaviour"],
    [["δ(n)", "1 for n = 0, otherwise 0", "Single sample of value 1 at n = 0"],
     ["u(n)", "1 for n ≥ 0, otherwise 0", "Steps to 1 at n = 0 and remains 1"],
     ["r(n)", "n·u(n)", f"Increases linearly; r(10) = {w1['elementary']['ramp_10']}"],
     ["(0.8)<sup>n</sup>u(n)", "0.8<sup>n</sup> for n ≥ 0",
      f"Geometric decay from 1; value {w1['elementary']['expo_10']:.4f} at n = 10"]],
    "Table 1: Elementary sequences.", [18, 30, 52])

tab2 = table(
    ["a", "Behaviour", "Value at n = 20"],
    [["0.5", "Monotonic decay (0 &lt; a &lt; 1)", f"{a['0.5']:.3g}"],
     ["−0.8", "Decaying, alternating sign (−1 &lt; a &lt; 0)", f"{a['-0.8']:.4g}"],
     ["1.1", "Monotonic growth (a &gt; 1)", f"{a['1.1']:.4f}"]],
    "Table 2: Effect of a on a<sup>n</sup>u(n).", [12, 62, 26])

tab3 = table(
    ["Sequence", "f<sub>0</sub> (cycles/sample)", "Fundamental period"],
    [["cos(2πn/8)", "1/8", f"N = {w1['periods']['cos_n8']} samples"],
     ["cos(2πn/7.5)", "2/15", f"N = {w1['periods']['cos_n7_5']} samples"]],
    "Table 3: Periodicity of the two cosines.", [34, 33, 33])

au = w1["audio"]
tab4 = table(
    ["Parameter", "Value"],
    [["Sampling rate f<sub>s</sub>", f"{au['fs']:,} Hz (Nyquist frequency {au['fs']/2:,.0f} Hz)"],
     ["Duration T", f"{au['duration_s']:.2f} s"],
     ["Number of samples N", f"{au['samples']:,} (= f<sub>s</sub> · T)"],
     ["Original format", f"{au['dtype']}, mono (reproducible speech-like stand-in)"],
     ["Peak amplitude after normalisation", "1.0"]],
    "Table 4: Parameters of the audio signal. The original phone recording was not supplied; the stand-in is declared in Section 7.", [45, 55])

tab5 = table(
    ["Feature", "Python (NumPy)", "Octave"],
    [["Index origin", "0", "1"],
     ["Range −5 to 10", "<code>np.arange(-5, 11)</code>", "<code>-5:10</code>"],
     ["Logical to numeric", "<code>.astype(float)</code>", "<code>double()</code>"],
     ["Element-wise product / power", "<code>*</code> and <code>**</code>", "<code>.*</code> and <code>.^</code>"],
     ["Multiple plots", "<code>plt.subplots()</code>", "<code>subplot(r, c, k)</code>"]],
    "Table 5: Python and Octave syntax differences.", [30, 35, 35])

alias_rows = [[str(r["fs_Hz"]), str(r["k"]), f"{r['abs_F_minus_kfs_Hz']:g}",
               f"{r['abs_F_minus_kfs_Hz']:g}", r["comment"]] for r in w2["alias"]]
tab6 = table(
    ["f<sub>s</sub> (Hz)", "k = round(F/f<sub>s</sub>)", "|F − kf<sub>s</sub>| (Hz)",
     "Observed alias (Hz)", "Comment"],
    alias_rows, "Table 6: Alias frequency of a 7 Hz tone for different sampling rates.",
    [13, 20, 19, 18, 30])

dec_rows = [[str(r["k"]), f"{r['new_fs_Hz']:g}", f"{r['rms_naive']:.3f}",
             f"{r['rms_decimate']:.3f}", f"{r['rms_predicted_filtered']:.3f}"]
            for r in w2["decimation"]]
tab7 = table(
    ["k", "New f<sub>s</sub> (Hz)", "RMS, x[::k] (no filter)",
     "RMS, decimate (FIR)", "RMS predicted for filtered"],
    dec_rows, "Table 7: RMS of the decimated chirp with and without an anti-aliasing filter.",
    [8, 18, 25, 24, 25])

tab8 = table(
    ["B (bits)", "Measured SQNR (dB)", "6.02B + 1.76 (dB)", "Difference (dB)"],
    [[str(b), f"{m:.2f}", f"{t:.2f}", f"{m-t:+.2f}"]
     for b, m, t in zip(w2["sqnr_bits"]["bits"], w2["sqnr_bits"]["measured"],
                        w2["sqnr_bits"]["theory"])],
    "Table 8: Measured and theoretical SQNR.", [18, 28, 29, 25])

tab9 = table(
    ["B (bits)", "Speech-like signal (dB)", "Full-scale sine (dB)",
     "6.02B + 1.76 (dB)", "Gap (dB)"],
    [[str(r["B"]), f"{r['speech_SQNR_dB']:.1f}", f"{r['sine_SQNR_dB']:.1f}",
      f"{r['theory_dB']:.1f}", f"{r['gap_dB']:.1f}"] for r in w2["speech"]["rows"]],
    "Table 9: SQNR of a speech-like signal and of a full-scale sine.", [15, 25, 24, 24, 12])

smooth_rows = [[("noisy x(n)" if r["M"] == 0 else f"M = {r['M']}"),
                f"{r['gain_at_50_samples']:.3f}", f"{r['rms_error']:.3f}"]
               for r in w3["smoothing"]]
tab12 = table(
    ["Filter", "Gain at the 50-sample period", "RMS error against the clean sine"],
    smooth_rows, "Table 12: Effect of the moving-average length.", [30, 35, 35])

tab13 = table(
    ["System", "Linear", "Time-invariant", "LTI"],
    [[r["system"], "yes" if r["linear"] else "no",
      "yes" if r["time_invariant"] else "no", "yes" if r["LTI"] else "no"]
     for r in w3["systems"]],
    "Table 13: Numerical test of the three systems.", [34, 22, 24, 20])

tab14 = table(
    ["Noise σ", "Estimated delay (samples)", "Success rate (300 trials)"],
    [[f"{r['sigma']:g}", str(r["single_run_estimate"]), f"{r['success_rate_300_trials']:.0%}"]
     for r in w3["delay"]],
    "Table 14: Delay estimate against noise level.", [25, 40, 35])

h_vals = w3["diffeq"]["h"]
tab15 = table(
    ["n"] + [str(i) for i in range(len(h_vals))],
    [["h(n)"] + [f"{v:.4f}" for v in h_vals]],
    "Table 15: Impulse response h(n) for 0 ≤ n ≤ 9 (identical for the three methods).")

p41 = w4["task41"]
tab16 = table(
    ["Numerator", "Pole 0.25: residue", "Pole 0.5: residue", "Σr<sub>i</sub>p<sub>i</sub><sup>n</sup> equals lfilter?"],
    [[r["b"], f"{r['residues'][0]:g}", f"{r['residues'][1]:g}",
      "yes" if r["matches_lfilter"] else "no"] for r in w4["residues"]],
    "Table 16: Residues from <code>signal.residuez</code> and comparison with <code>lfilter</code>.",
    [22, 24, 24, 30])

tab17 = table(
    ["r", "Poles", "Peak |H| (dB)", "−3 dB bandwidth (×π rad)",
     "max |h(n)|, 30 ≤ n ≤ 39", "Stable"],
    [[f"{r['r']:g}", f"{r['r']:.2f} (angle ±45°)", f"{r['peak_dB']:.1f}",
      ("—" if r["bw_over_pi"] is None else f"{r['bw_over_pi']:.3f}"),
      f"{r['max_h_last10']:.3g}", "yes" if r["stable"] else "no"]
     for r in w4["pole_pair"]],
    "Table 17: Effect of the pole radius r.", [8, 22, 16, 20, 22, 12])

tab18 = table(
    ["System", "Poles", "max |p|", "max |h(n)|, n ≥ 150", "Σ|h(n)|, n &lt; 200", "Classification"],
    [[r["system"], r["poles"], f"{r['max_pole_radius']:.3f}", r["max_h_n_ge_150"],
      r["sum_abs_h"], r["classification"]] for r in w4["systems"]],
    "Table 18: Stability classification and check of the impulse response.",
    [10, 28, 12, 18, 16, 16])

res = w4["resonator"]
tab19 = table(
    ["Quantity", "Value"],
    [["Peak frequency", f"{res['peak_Hz']:.0f} Hz"],
     ["−3 dB bandwidth", f"{res['bw_Hz']:.0f} Hz (approximation 2(1 − r)f<sub>s</sub>/2π = {res['bw_approx_Hz']:.0f} Hz)"],
     ["Gain at 0 Hz and at 4 kHz", f"{res['gain_0']:.1e} and {res['gain_nyquist']:.1e} (zeros)"],
     ["Peak of Welch spectrum of the filtered noise", "1000 Hz"]],
    "Table 19: Properties of the resonator.", [45, 55])

# ---------------------------------------------------------------------------
# Appendix code listings (mirrors the code in the executed notebooks)
# ---------------------------------------------------------------------------
octave_code = """n = -5:10;
delta = double(n == 0);
step  = double(n >= 0);
ramp  = n .* step;
expo  = 0.8.^n .* step;
subplot(1,4,1); stem(n, delta); title('delta(n)'); xlabel('n');
subplot(1,4,2); stem(n, step);  title('u(n)');     xlabel('n');
subplot(1,4,3); stem(n, ramp);  title('r(n)');     xlabel('n');
subplot(1,4,4); stem(n, expo);  title('(0.8)^n u(n)'); xlabel('n');"""

appb_code = """def alias_freq(f0, fs):
    k = round(f0 / fs)
    return abs(f0 - k * fs), k

def quantize(x, bits, full_scale=1.0):
    delta = 2 * full_scale / 2**bits
    q = np.round(x / delta) * delta
    return np.clip(q, -full_scale, full_scale - delta)

def sqnr_db(x, xq):
    return 10 * np.log10(np.sum(x**2) / np.sum((x - xq)**2))

def chirp_signal(fs=44100, T=3):
    t = np.arange(0, T, 1 / fs)
    return fs, 0.5 * signal.chirp(t, 200, T, 15000)

def speech_like(fs=16000, T=4.7, seed=3):
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
    return fs, x / np.max(np.abs(x))"""

appc_code = """def conv(x, h):
    N = len(x) + len(h) - 1
    y = np.zeros(N)
    for n in range(N):
        for k in range(len(x)):
            if 0 <= n - k < len(h):
                y[n] += x[k] * h[n - k]
    return y

systems = {"x^2": lambda x: x**2,
           "n x(n)": lambda x: np.arange(len(x)) * x,
           "moving average": lambda x: np.convolve(x, np.ones(3)/3)[:len(x)]}

def delay_estimate(sigma, seed=1, true_delay=37, N=500):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(N)
    y = np.concatenate([np.zeros(true_delay), 0.6 * x])[:N] + sigma * rng.standard_normal(N)
    r = signal.correlate(y, x, mode="full")
    lags = signal.correlation_lags(len(y), len(x), mode="full")
    return int(lags[np.argmax(r)]), lags, r

b, a = [1, 1], [1, -0.75, 0.125]
imp = np.zeros(10); imp[0] = 1
h_rec = np.zeros(10)
for n in range(10):
    h_rec[n] = imp[n] + (imp[n-1] if n >= 1 else 0)
    h_rec[n] += 0.75 * (h_rec[n-1] if n >= 1 else 0) - 0.125 * (h_rec[n-2] if n >= 2 else 0)
h_lf = signal.lfilter(b, a, imp)
h_cf = 6 * 0.5**np.arange(10) - 5 * 0.25**np.arange(10)
step = signal.lfilter(b, a, np.ones(60))"""

appd_code = """def zplane(b, a, ax=None, extra_poles_at_origin=0):
    z, p, k = signal.tf2zpk(b, a)
    p = np.concatenate([p, np.zeros(extra_poles_at_origin)])
    ax = ax or plt.gca()
    th = np.linspace(0, 2*np.pi, 400)
    ax.plot(np.cos(th), np.sin(th), "k--", lw=0.8, label="unit circle")
    ax.plot(z.real, z.imag, "o", mfc="none", label="zeros")
    ax.plot(p.real, p.imag, "x", label="poles")
    ax.set_aspect("equal"); ax.legend(); ax.set_xlabel("Re(z)"); ax.set_ylabel("Im(z)")
    return z, p

def inverse_check(b, a, N=10):
    r, p, k = signal.residuez(b, a)
    n = np.arange(N)
    h_pf = sum(ri * pi**n for ri, pi in zip(r, p)).real
    imp = np.zeros(N); imp[0] = 1
    h_lf = signal.lfilter(b, a, imp)
    return r, p, h_pf, h_lf

SYS4 = {"H1": ([1], [1, -1.6, 0.89]),
        "H2": ([1, 1], [1, -2.5, 1]),
        "H3": ([1], [1, 0.5, -0.5]),
        "H4": ([1, 0, 0, 0, -1], [1])}

def classify(b, a, N=200):
    z, p = zplane(b, a)
    imp = np.zeros(N); imp[0] = 1
    h = signal.lfilter(b, a, imp)
    rmax = float(np.max(np.abs(p))) if len(p) else 0.0
    return z, p, h, rmax, float(np.max(np.abs(h[150:]))), float(np.sum(np.abs(h)))

r, p = 0.97, 2*np.pi*1000/8000
a_res = [1, -2*r*np.cos(p), r**2]
b_res = [1, 0, -1]
w, H = signal.freqz(b_res, a_res, worN=8192, fs=8000)
b_res = (np.array(b_res) / np.max(np.abs(H))).tolist()
x = np.random.default_rng(0).standard_normal(8000)
y = signal.lfilter(b_res, a_res, x)"""

# ---------------------------------------------------------------------------
# HTML document
# ---------------------------------------------------------------------------
css = """
@page { size: A4; margin: 17mm 16mm; }
* { box-sizing: border-box; }
body { font-family: "Times New Roman", Times, serif; font-size: 11pt; line-height: 1.42; color: #111; }
h1, h2, h3 { font-family: Arial, sans-serif; color: #16324f; }
h1 { font-size: 19pt; margin: 14pt 0 8pt; }
h2 { font-size: 14pt; margin: 16pt 0 6pt; border-bottom: 1px solid #b9c6d4; padding-bottom: 3pt; }
h3 { font-size: 11.5pt; margin: 12pt 0 4pt; }
p { margin: 5pt 0; text-align: justify; }
.cover { text-align: center; page-break-after: always; margin-top: 35mm; }
.cover .inst { font-family: Arial, sans-serif; font-size: 14pt; font-weight: bold; letter-spacing: 1px; }
.cover .dept { font-family: Arial, sans-serif; font-size: 12pt; margin-top: 16pt; }
.cover h1 { font-size: 24pt; margin-top: 28mm; }
.cover .topic { font-size: 13pt; margin-top: 8mm; font-weight: bold; }
.cover table { margin: 24mm auto 0; width: 80%; border: none; }
.cover td { border: none; text-align: left; padding: 3pt 6pt; }
.toc, .lof { page-break-after: always; }
ul { margin: 4pt 0 4pt 18pt; }
li { margin: 2pt 0; }
figure { margin: 10pt 0 12pt; text-align: center; break-inside: avoid; page-break-inside: avoid; }
figure img { max-width: 100%; height: auto; border: 1px solid #d6dde5; }
figcaption, p.caption { font-size: 9.5pt; color: #333; text-align: center; margin-top: 4pt; }
table { width: 100%; border-collapse: collapse; margin: 8pt 0; font-size: 9.5pt; break-inside: avoid; }
th, td { border: 1px solid #9aa7b4; padding: 4pt 5pt; text-align: left; vertical-align: top; }
th { background: #e6edf4; font-family: Arial, sans-serif; font-size: 9pt; }
pre { background: #f4f6f8; border: 1px solid #ccd5de; padding: 6pt 8pt; font-family: Consolas, monospace;
      font-size: 8pt; white-space: pre-wrap; break-inside: avoid; }
code { font-family: Consolas, monospace; font-size: 0.95em; }
.section { page-break-before: always; }
.small { font-size: 9.5pt; color: #444; }
.note { background: #f4f6f8; border-left: 3px solid #4d7ea8; padding: 6pt 8pt; margin: 8pt 0; }
"""

toc = """
<div class="toc">
<h1>Contents</h1>
<ol>
<li>Objectives</li><li>Theory</li><li>Equipment and software</li>
<li>Methodology and results</li><li>Discussion and analysis</li>
<li>Conclusion</li><li>AI-use declaration</li>
</ol>
<h1>Table of Figures</h1>
<ul>
""" + "".join(f"<li>Figure {n}: {cap}</li>" for n, (_, cap) in FIGURES.items()) + """
</ul>
</div>
"""

body = f"""
<div class="cover">
  <div class="inst">DAR ES SALAAM INSTITUTE OF TECHNOLOGY</div>
  <div class="dept">Department of Computer Engineering<br>
  Bachelor of Engineering in Computer Engineering</div>
  <h1>DSP LABORATORY REPORT<br>WEEKS 1 TO 4</h1>
  <div class="topic">Lab 0, Lab 1A, Lab 1B and Week 4<br>(Tasks 1.1 to 4.5)</div>
  <table>
    <tr><td>Module name</td><td>Digital Signal Processing</td></tr>
    <tr><td>Module code</td><td>COU 07506</td></tr>
    <tr><td>Class</td><td>BEng24COE</td></tr>
    <tr><td>Work</td><td>Individual laboratory report</td></tr>
    <tr><td>Student name</td><td>Zaid Yaseer Yussuf</td></tr>
    <tr><td>Registration number</td><td>240242479517</td></tr>
    <tr><td>Date</td><td>26 November 2026</td></tr>
  </table>
</div>
{toc}

<h1>1. Objectives</h1>
<p>This report covers the four laboratory sessions of Weeks 1 to 4 of the module (Tasks 1.1 to
4.5). The objectives were as follows.</p>
<h3>Lab 0: Setting up the DSP laboratory (Tasks 1.1 to 1.4)</h3>
<ol>
<li>to set up the Python (NumPy, SciPy, Matplotlib) and Octave environments used for the module;</li>
<li>to generate, plot and label elementary discrete-time sequences;</li>
<li>to examine the effect of the parameter a on a<sup>n</sup>u(n) and the periodicity of sampled cosines;</li>
<li>to read an audio file, report its sampling parameters and display its waveform.</li>
</ol>
<h3>Lab 1A: Sampling, aliasing and quantization (Tasks 2.1 to 2.5)</h3>
<ol>
<li>to demonstrate aliasing of a sampled sinusoid and to predict the alias frequency from |F − kf<sub>s</sub>|;</li>
<li>to compare decimation without and with an anti-aliasing filter on a wide-band signal;</li>
<li>to implement a uniform quantiser and measure the signal-to-quantisation-noise ratio (SQNR);</li>
<li>to verify the 6 dB-per-bit rule experimentally.</li>
</ol>
<h3>Lab 1B: Convolution, correlation and difference equations (Tasks 3.1 to 3.5)</h3>
<ol>
<li>to implement linear convolution from its definition and to verify it against <code>np.convolve</code>;</li>
<li>to smooth a noisy signal with moving-average filters and describe the trade-off;</li>
<li>to test linearity and time-invariance of systems numerically;</li>
<li>to estimate a time delay by cross-correlation and convert it into a distance;</li>
<li>to solve a difference equation by recursion and with <code>lfilter</code> and to compare with the closed form.</li>
</ol>
<h3>Week 4: Z-transform laboratory: poles, zeros and stability (Tasks 4.1 to 4.5)</h3>
<ol>
<li>to find the poles, zeros and frequency response of a transfer function with SciPy;</li>
<li>to obtain an inverse z-transform with <code>residuez</code> and check it against <code>lfilter</code>;</li>
<li>to relate pole positions to stability, resonance and the shape of h(n);</li>
<li>to design a simple resonator by placing poles and zeros.</li>
</ol>

<h1>2. Theory</h1>
<h2>2.1 Discrete-time signals, periodicity and audio</h2>
<p>A discrete-time signal x(n) is defined only at integer values of n and is stored as an index
array and a value array. The elementary sequences used are the unit impulse δ(n), the unit
step u(n), the unit ramp r(n) = n·u(n) and the real exponential a<sup>n</sup>u(n).</p>
<p>A discrete-time cosine cos(2πf<sub>0</sub>n) is periodic only if f<sub>0</sub> is a rational number
k/N, in which case the fundamental period is N samples (k and N having no common factor).
A sampled audio signal is a sequence of numbers together with a sampling rate f<sub>s</sub>.
A recording of duration T contains N = f<sub>s</sub>T samples, and frequencies up to f<sub>s</sub>/2
can be represented.</p>
<h2>2.2 Sampling, aliasing and quantisation</h2>
<p>Sampling at f<sub>s</sub> represents frequencies only up to f<sub>s</sub>/2. A component at
F &gt; f<sub>s</sub>/2 appears at the alias frequency F<sub>alias</sub> = |F − kf<sub>s</sub>|,
where k is the integer nearest to F/f<sub>s</sub>. Once aliasing has occurred, the alias
cannot be distinguished from a genuine component at that frequency. An anti-aliasing
low-pass filter must therefore remove the content above f<sub>s</sub>/2 before the samples
are taken or discarded.</p>
<p>A uniform B-bit quantiser with range ±X<sub>m</sub> has step Δ = 2X<sub>m</sub>/2<sup>B</sup>
and error variance Δ<sup>2</sup>/12. For a full-scale sinusoid,
SQNR ≈ 6.02B + 1.76 dB, so each extra bit adds about 6 dB. The measured SQNR is
10 log<sub>10</sub>(Σx<sup>2</sup>/Σe<sup>2</sup>), where e(n) = x(n) − x<sub>q</sub>(n).</p>
<h2>2.3 Convolution, correlation and difference equations</h2>
<p>The output of an LTI system is y(n) = Σ<sub>k</sub>x(k)h(n − k). For sequences of length L
and M the result has L + M − 1 samples and the direct computation needs L·M
multiplications. A system is linear if T{{ax<sub>1</sub> + bx<sub>2</sub>}} = aT{{x<sub>1</sub>}} +
bT{{x<sub>2</sub>}} and time-invariant if a delay of the input only delays the output by the
same amount. The cross-correlation r<sub>xy</sub>(l) = Σ<sub>n</sub>x(n)y(n − l) has its
maximum at the lag where the two signals are most similar, which gives the delay between
them. A difference equation y(n) = Σb<sub>k</sub>x(n − k) − Σa<sub>k</sub>y(n − k) is
implemented by <code>lfilter(b, a, x)</code>; its steady-state response to a unit step is
H(1) = Σb/Σa.</p>
<h2>2.4 Stability and the z-transform</h2>
<p>A causal LTI system is BIBO stable if its impulse response h(n) is absolutely summable,
that is Σ|h(n)| &lt; ∞. For H(z) = B(z)/A(z) the roots of B are the zeros and the roots
of A are the poles. A causal system is BIBO stable if and only if all poles satisfy |p| &lt; 1.
A pole pair at re<sup>±jθ</sup> produces a resonance near ω = θ whose bandwidth is about
2(1 − r) rad/sample, so it becomes sharper as r → 1. A zero on the unit circle produces
a null in the magnitude response.</p>
<p>For a second-order denominator A(z) = 1 + a<sub>1</sub>z<sup>−1</sup> +
a<sub>2</sub>z<sup>−2</sup> the poles are inside the unit circle if and only if
|a<sub>2</sub>| &lt; 1 and |a<sub>1</sub>| &lt; 1 + a<sub>2</sub> (the stability triangle).
The inverse z-transform of a rational function with distinct poles p<sub>i</sub> and
residues r<sub>i</sub> is h(n) = Σr<sub>i</sub>p<sub>i</sub><sup>n</sup>.</p>

<h1>3. Equipment and software</h1>
<p>A computer with Python 3, Jupyter Notebook, NumPy, SciPy (<code>signal.tf2zpk</code>,
<code>signal.freqz</code>, <code>signal.residuez</code>, <code>signal.lfilter</code>) and
Matplotlib was used throughout. GNU Octave was used for Task 1.4. The four notebooks were
restarted and run from top to bottom; their exported numbers are used directly in this
report.</p>
<div class="note"><strong>Declaration about the audio.</strong> The original phone recording
was not supplied with the source files. A deterministic speech-like WAV with the parameters
reported below (16 kHz, 4.70 s, 75 200 samples, 16-bit mono PCM) was generated and stored at
<code>data/my_voice.wav</code>. It is a stand-in, not a new recording, and is used only in
Week 1. Lab 1A uses the manual's fallback chirp and synthetic speech-like signal so that
the results are reproducible.</div>

<h1 class="section">4. Methodology and results</h1>
<h2>4.1 Lab 0: Setting up the DSP laboratory (Tasks 1.1 to 1.4)</h2>
<h3>Task 1.1: Elementary sequences</h3>
<p>The sequences δ(n), u(n), r(n) and (0.8)<sup>n</sup>u(n) were generated for −5 ≤ n ≤ 10
with NumPy and plotted as stem plots ({figure(1)}). Table 1 summarises the observed behaviour.</p>
{tab1}
<h3>Task 1.2: Variation of parameters</h3>
<p>(a) The sequence a<sup>n</sup>u(n) was plotted for a = 0.5, −0.8 and 1.1 ({figure(2)}).
The values at n = 20 are listed in Table 2.</p>
{tab2}
<p>(b) The sequences cos(2πn/8) and cos(2πn/7.5) were plotted for 0 ≤ n ≤ 40 ({figure(3)}).</p>
{tab3}
<p>Both sequences are periodic, since both frequencies are rational. The second has a longer
period because 7.5 is not an integer. This was verified numerically by confirming
x(n + N) = x(n) for N = 8 and N = 15.</p>
<h3>Task 1.3: Audio signal</h3>
<p>The WAV file was read with <code>scipy.io.wavfile.read</code>, converted to mono where
necessary and normalised to the range [−1, 1]. The parameters are given in Table 4 and the
waveform in {figure(4)}.</p>
{tab4}
<p>The signal consists of several bursts separated by lower-amplitude intervals. Within each
burst the amplitude varies with each syllable, which is characteristic of speech.</p>
<h3>Task 1.4: Implementation in GNU Octave</h3>
<p>The sequences of Task 1.1 were implemented in Octave with the script in Appendix A. The
main syntactic differences from Python are given in Table 5.</p>
{tab5}

<h2>4.2 Lab 1A: Sampling, aliasing and quantization (Tasks 2.1 to 2.5)</h2>
<h3>Task 2.1: Aliasing of a sinusoid</h3>
<p>A 7 Hz cosine was plotted on a dense time grid (the “analog” signal) together with its
samples and the predicted alias for f<sub>s</sub> = 10, 12, 14 and 20 Hz ({figure(5)}).
The alias frequencies are compared with |F − kf<sub>s</sub>| in Table 6.</p>
{tab6}
<p>For f<sub>s</sub> = 10 Hz and 12 Hz the samples of the 7 Hz tone coincide exactly with those
of a 3 Hz and a 5 Hz cosine respectively, so the alias curve passes through every sample.
At f<sub>s</sub> = 14 Hz the tone lies exactly on f<sub>s</sub>/2: the samples alternate in
sign and the frequency is not folded, but the sampled amplitude depends on the phase, so
this case is borderline. At f<sub>s</sub> = 20 Hz the sampling theorem is satisfied and no
alias exists.</p>
<h3>Task 2.2: Aliasing in a decimated signal</h3>
<p>The chirp (RMS 0.354) was decimated by k = 2, 4 and 8, first by keeping every k-th sample
and then with <code>signal.decimate(x, k, ftype="fir")</code>, which low-pass filters before
discarding samples. Table 7 compares the RMS values. The “predicted” column is the input RMS
multiplied by the square root of the fraction of the sweep that lies below the new Nyquist
frequency.</p>
{tab7}
<p>Without a filter the RMS stays at about 0.35 for every k: nothing is removed, and all the
energy above the new Nyquist frequency is folded into the band. With the filter the RMS
falls to {w2['decimation'][-1]['rms_decimate']:.3f} for k = 8, close to the predicted
{w2['decimation'][-1]['rms_predicted_filtered']:.3f}, because only the first part of the sweep
(200 Hz to 2756 Hz) can be represented. {figure(6)} shows the spectrograms for k = 8.</p>
<p>In the unfiltered version the sweep reaches 2756 Hz, then folds back and zig-zags between
0 and 2756 Hz for the rest of the record. In the filtered version the sweep stops at the new
Nyquist frequency and the rest of the record is almost empty. The zig-zag is the aliasing and
it is present over most of the unfiltered signal.</p>
<h3>Task 2.3: A uniform quantiser</h3>
<p>The function <code>quantize()</code> rounds to the nearest multiple of Δ = 2/2<sup>B</sup>
and clips the result to [−1, 1 − Δ]. A 300 Hz sinusoid of amplitude 0.99 sampled at 8 kHz
(80 samples, three cycles) was quantised to 3 bits, giving Δ = {w2['quant3']['delta']:.2f}
({figure(7)}). The error stays within ±Δ/2 = ±{w2['quant3']['delta']/2:.3f} except at the
positive peaks, where 0.99 would round to 1.0 and is clipped to 0.75; the largest error is
therefore {w2['quant3']['max_error']:.3f}.</p>
<h3>Task 2.4: The 6 dB-per-bit rule</h3>
<p>The SQNR of the same 80-sample sinusoid was measured for B = 2, 4, …, 16 and compared with
the theoretical value ({figure(8)}, Table 8).</p>
{tab8}
<p>A straight-line fit through B = 4 to 16 gives a slope of
{w2['sqnr_bits']['slope_dB_per_bit']:.2f} dB per bit, against the theoretical 6.02 dB per bit.
For B ≥ 4 the measured values are within about 2.3 dB of the formula; the scatter arises
because the record contains only 80 samples, so the error is not a perfectly uniform noise.
At B = 2 the measured value is low because the positive peaks are clipped. The theoretical
value is also reduced by about 0.09 dB because the amplitude is 0.99 and not 1.</p>
<h3>Task 2.5: Quantising a speech-like signal</h3>
<p>A 4.7 s speech-like signal at 16 kHz, normalised to a peak of 1, was quantised to 4, 8 and
12 bits. A 440 Hz sine of amplitude 0.999 was quantised in the same way for comparison
(Table 9). The speech-like signal has a crest factor (peak/RMS) of
{w2['speech']['crest_factor']:.1f}, compared with 1.41 for a sine.</p>
{tab9}
<p>The speech-like signal has an SQNR about 20 dB lower than the sine at 8 and 12 bits. This
matches the crest-factor penalty 20 log<sub>10</sub>(crest/√2) =
{w2['speech']['crest_penalty_dB']:.1f} dB: the step Δ is fixed by the peak, but the average
signal power is much lower, so the noise is large compared with the signal. At 4 bits the
gap is smaller because Δ is so large that much of the signal falls below one step and the
quantisation error is no longer uniform. The same reasoning applies to real speech, which
has pauses and a high peak-to-RMS ratio.</p>

<h2>4.3 Lab 1B: Convolution, correlation and difference equations (Tasks 3.1 to 3.5)</h2>
<h3>Task 3.1: Convolution from the definition</h3>
<p>The function <code>conv(x, h)</code> implements the double sum. It returned
[1 3 6 6 4 1] for x = {{1, 2, 3, 1}} and h = {{1, 1, 1}}, the expected result, and the same as
<code>np.convolve</code>. The pre-lab sequences gave the expected result with both functions.
Two random sequences of length 2000 were then convolved with both functions and timed with
<code>time.perf_counter()</code> (Table 11); the results agreed
(<code>np.allclose = True</code>).</p>
{table(["Function", "Time for L = M = 2000", "Multiplications"],
       [["conv (Python double loop)", f"{w3['convolution']['loop_time_s']:.3f} s", "L·M = 4 000 000"],
        ["np.convolve", f"{w3['convolution']['numpy_time_s']*1000:.2f} ms", "L·M = 4 000 000"],
        ["Ratio", f"≈ {w3['convolution']['speed_ratio']:.0f}× faster", "same"]],
       "Table 11: Timing of the two implementations (times depend on the computer used).",
       [38, 32, 30])}
<h3>Task 3.2: Smoothing a noisy signal</h3>
<p>The signal x(n) = sin(2πn/50) + 0.5w(n), with Gaussian noise w(n), was convolved with
moving-average filters h(n) = (1/M){{1, …, 1}} for M = 3, 9 and 25 using <code>mode="same"</code>
({figure(9)}). Table 12 gives the theoretical gain of each filter at the frequency of the
sine, |sin(Mω/2)/(M sin(ω/2))| with ω = 2π/50, and the RMS error between the output and the
clean sine, with M samples excluded at each end to avoid edge effects.</p>
{tab12}
<p>M = 3 removes little noise. M = 9 gives the lowest error and reduces the amplitude of the
sine by a few per cent. M = 25 removes more noise but attenuates the wanted sine, so the
total error rises again. A longer filter therefore gives more noise reduction but more
distortion of the wanted signal.</p>
<h3>Task 3.3: Testing linearity and time-invariance</h3>
<p>Each system was tested with two random sequences, a = 2 and b = −3, and with an input
delayed by 5 samples (Table 13).</p>
{tab13}
<p>The squarer fails the superposition test because (ax<sub>1</sub> + bx<sub>2</sub>)<sup>2</sup>
contains a cross term 2abx<sub>1</sub>x<sub>2</sub>, but it is time-invariant because it acts
on each sample in the same way. The system n·x(n) is linear but not time-invariant: delaying
the input by n<sub>0</sub> gives n·x(n − n<sub>0</sub>), whereas the delayed output is
(n − n<sub>0</sub>)·x(n − n<sub>0</sub>). The 3-point moving average is a weighted sum with
constant coefficients and is therefore both linear and time-invariant.</p>
<h3>Task 3.4: Finding a hidden delay</h3>
<p>A noise-free signal of 500 samples was delayed by 37 samples, scaled by 0.6 and corrupted
with Gaussian noise. The cross-correlation of the received and transmitted signals peaks at
lag 37 for σ = 0.5 ({figure(10)}).</p>
<p>The noise standard deviation was then increased. The single run with the specified seed is
shown together with the fraction of 300 independent trials in which the true delay of 37
samples was found (Table 14).</p>
{tab14}
<p>The estimate was correct for σ = 0.5, 1 and 2 in the single run and in every one of the 300
trials. At higher noise the single run already failed and the success rate falls. The peak
of the correlation is about 0.6 × 500 = 300, while the noise contributes a random level of
about σ√500 ≈ 22σ, so the peak is lost once σ is of the order of 4 to 8. A delay of 37
samples at f<sub>s</sub> = 1000 Hz is 37 ms, which for a sound pulse at 343 m/s corresponds
to a distance of {37/1000*343:.1f} m.</p>
<h3>Task 3.5: Difference equation</h3>
<p>For y(n) − 0.75y(n − 1) + 0.125y(n − 2) = x(n) + x(n − 1) the impulse response was computed
for 0 ≤ n ≤ 9 in three ways: by direct recursion in a for loop, with
<code>signal.lfilter([1, 1], [1, −0.75, 0.125], impulse)</code>, and from the closed form
h(n) = 6(0.5)<sup>n</sup> − 5(0.25)<sup>n</sup>. All three agree ({figure(11)}, Table 15;
<code>np.allclose = True</code> for both comparisons). The step response, computed with
<code>lfilter</code>, settles at {w3['diffeq']['step_final']:.4f} ({figure(12)}). This equals
H(1) = Σb/Σa = 2/0.375 = {w3['diffeq']['H1']:.4f}.</p>
{tab15}

<h2>4.4 Week 4: Z-transform laboratory (Tasks 4.1 to 4.5)</h2>
<h3>Task 4.1: A pole-zero plotting function</h3>
<p>The function <code>zplane(b, a)</code> was written using <code>signal.tf2zpk</code> and applied
to H(z) = (1 + z<sup>−1</sup>)/(1 − 0.75z<sup>−1</sup> + 0.125z<sup>−2</sup>). It has a zero
at z = −1 and poles at z = 0.50, 0.25; all poles satisfy |p| &lt; 1, so the printed test gave
True ({figure(13)}). The magnitude response falls from {p41['gain_0_dB']:.1f} dB at ω = 0 to
a null at ω = π because of the zero at z = −1.</p>
<h3>Task 4.2: Inverse z-transform with residuez</h3>
<p><code>signal.residuez</code> was applied to 1/(1 − 0.75z<sup>−1</sup> + 0.125z<sup>−2</sup>)
and the resulting sum of residues times p<sup>n</sup> was compared with the impulse response
from <code>lfilter</code> for n = 0 to 9. The same was done for b = [1, 1] (Table 16).</p>
{tab16}
<p>The residues for the numerator 1 are 2 (at p = 0.5) and −1 (at p = 0.25), which equals the
partial-fraction expansion of the pre-lab question (b). For b = [1, 1] they are 6 and −5,
which confirms h(n) = 6(0.5)<sup>n</sup> − 5(0.25)<sup>n</sup>, the closed form used in Task 3.5.</p>
<h3>Task 4.3: Pole position and the impulse response</h3>
<p>For a pole pair at p = re<sup>±jπ/4</sup>, that is
A(z) = 1 − 2r cos(π/4)z<sup>−1</sup> + r<sup>2</sup>z<sup>−2</sup>, h(n) (40 samples) and
|H(e<sup>jω</sup>)| were plotted for r = 0.5, 0.8, 0.95, 1.0 and 1.05 ({figure(14)}, Table 17).</p>
{tab17}
<p>As r increases from 0.5 to 0.95 the impulse response still oscillates at the same rate
(θ = π/4) but decays more slowly, and the resonance peak at ω = π/4 becomes taller and
narrower. The bandwidth follows the approximation 2(1 − r) rad. For r = 1.0 the response is
a sustained sinusoid of constant amplitude and the peak of |H| is infinite. For r = 1.05
the response grows as 1.05<sup>n</sup>. The values r = 1.0 and r = 1.05 are therefore not
BIBO stable; r = 1.0 is marginally stable.</p>
<h3>Task 4.4: Stability of given systems</h3>
<p>The four systems were classified with <code>zplane</code> ({figure(15)}) and checked by
computing h(n) for 200 samples (Table 18).</p>
{tab18}
<p>H1 has poles at 0.80 ± j0.50 (radius 0.943) and is stable; its impulse response decays
slowly. H2 has poles at 2 and 0.5; the pole at z = 2 is outside the unit circle, so h(n)
grows without bound and the zero at z = −1 does not cancel it. H3 has poles at 0.5 and −1:
the pole at z = −1 is on the unit circle, and h(n) = (1/3)(0.5)<sup>n</sup> + (2/3)(−1)<sup>n</sup>
neither decays nor grows, but Σ|h(n)| increases by about 2/3 per sample, so the system is
not BIBO stable. H4 = 1 − z<sup>−4</sup> is an FIR filter with h(n) = {{1, 0, 0, 0, −1}};
its poles are all at z = 0, so it is always stable.</p>
<h3>Task 4.5: Design of a resonator</h3>
<p>A resonator peaking at 1 kHz for f<sub>s</sub> = 8 kHz was designed with poles at
re<sup>±jθ</sup>, r = 0.97 and θ = 2π·1000/8000 = π/4, so
A(z) = 1 − 1.3718z<sup>−1</sup> + 0.9409z<sup>−2</sup>. Zeros at z = ±1 give B(z) = 1 − z<sup>−2</sup>,
which was scaled to give unit gain at the peak. The result is in {figure(16)} and the main
figures are in Table 19.</p>
{tab19}
<p>White noise (8000 samples, f<sub>s</sub> = 8 kHz) has a flat spectrum, while the filtered
output is concentrated in a narrow band around 1 kHz and is strongly reduced near 0 Hz and
4 kHz. The output can also be played with <code>Audio(y, rate=8000)</code> to hear the
narrow-band tone-like noise.</p>

<h1 class="section">5. Discussion and analysis</h1>
<h2>5.1 Lab 0</h2>
<h3>Pre-lab question</h3>
<p>Three devices containing DSP and the signal each processes: a smartphone (speech from
the microphone: noise reduction and coding); a digital audio system (audio stream:
equalisation); a Wi-Fi router (radio signal: modulation and demodulation).</p>
<h3>Analysis questions</h3>
<ol>
<li><strong>Storage.</strong> For f<sub>s</sub> = 16 kHz, one minute of mono audio requires
60 × 16 000 = 960 000 numbers. At 44.1 kHz it requires 2 646 000 and at 48 kHz 2 880 000.</li>
<li><strong>Stem plot.</strong> x(n) exists only at integer n. A continuous line would imply
values between samples, whereas a stem plot shows only the defined samples.</li>
<li><strong>Growing exponential.</strong> For a = 1.1, Σ|h(n)| diverges. A bounded input would
therefore produce an unbounded output, so the BIBO stability condition is violated.</li>
</ol>
<h2>5.2 Lab 1A</h2>
<h3>Pre-lab questions</h3>
<p>(a) A 7 kHz tone sampled at 10 kHz appears at |7 − 10| = 3 kHz. (b) For an 8-bit quantiser
with a ±1 V range, Δ = 2/2<sup>8</sup> = 7.8125 mV. The theoretical SQNR is 6.02 × 8 + 1.76
= 49.9 dB.</p>
<h3>Analysis questions</h3>
<ol>
<li><strong>Alias of 7 Hz at f<sub>s</sub> = 10 Hz.</strong> Sampling makes the spectrum repeat
at multiples of f<sub>s</sub>, so the tone at +7 Hz has copies at 7 − 10 = −3 Hz and 17 Hz,
and the tone at −7 Hz has a copy at +3 Hz ({figure(17)}). Only frequencies below
f<sub>s</sub>/2 = 5 Hz are visible in the baseband, so the 7 Hz tone is seen as 3 Hz.</li>
<li><strong>Why aliasing cannot be removed afterwards.</strong> After sampling, the alias and
a genuine component at the same frequency give identical samples, and many input
frequencies map to the same alias. The information needed to tell them apart has been
lost, so no later filter can separate them. The low-pass filter must act before the
samples are discarded.</li>
<li><strong>Change in SQNR per bit.</strong> Adding one bit halves Δ, so the noise power
Δ<sup>2</sup>/12 falls by a factor of 4, which is 10 log<sub>10</sub>4 = 6.02 dB. The measured
slope was {w2['sqnr_bits']['slope_dB_per_bit']:.2f} dB per bit, which agrees with the theory.</li>
<li><strong>Temperature sensor.</strong> The range of 100 °C and the resolution of 0.01 °C
require 100/0.01 = 10 000 levels, so log<sub>2</sub>10 000 = 13.3, which rounds up to B = 14
bits. The temperature changes by at most 0.1 °C per second, so a sampling rate of 1 Hz keeps
the change between samples to 0.1 °C or less. This is very much above the Nyquist rate of the
slow signal. A higher rate such as 10 Hz with averaging could be used to reduce noise, but is
not needed for the signal itself.</li>
</ol>
<h2>5.3 Lab 1B</h2>
<h3>Pre-lab questions</h3>
<p>(a) The convolution of x = {{1, −1, 2}} with h = {{2, 1, 0, 1}} is {{2, −1, 3, 3, −1, 2}}.
(b) For y(n) = n·x(n), the response to the delayed input x(n − n<sub>0</sub>) is
n·x(n − n<sub>0</sub>), but the delayed output is (n − n<sub>0</sub>)·x(n − n<sub>0</sub>).
They differ for n<sub>0</sub> ≠ 0, so the system is not time-invariant.</p>
<h3>Analysis questions</h3>
<ol>
<li><strong>Speed of <code>np.convolve</code>.</strong> Both methods need L·M multiplications,
so the number of operations is the same. <code>np.convolve</code> is faster because the loops
run in compiled C code on whole arrays, whereas the Python double loop is interpreted and
has overhead on every single multiplication.</li>
<li><strong>LTI systems.</strong> Only the moving average is LTI. This could be predicted
without code: the squarer is non-linear, and multiplication by n is a time-varying gain,
while the moving average is a fixed weighted sum of delayed inputs.</li>
<li><strong>Applications of cross-correlation in Tanzania.</strong> (i) Locating leaks in
water pipes: two sensors on the pipe record the leak noise, and the delay between them,
found by cross-correlation, gives the position of the leak. (ii) Radar and GPS: the received
signal is correlated with the transmitted code or pulse, and the delay gives the range.</li>
<li><strong>FIR or IIR, and stability.</strong> The system is IIR, because the feedback terms
make h(n) = 6(0.5)<sup>n</sup> − 5(0.25)<sup>n</sup> non-zero for all n ≥ 0. It is stable: the
poles are at z = 0.5 and 0.25, inside the unit circle, and h(n) decays to zero. All h(n) are
positive, so Σ|h(n)| = H(1) = {w3['diffeq']['H1']:.3f}, which is finite.</li>
</ol>
<h2>5.4 Week 4</h2>
<h3>Pre-lab questions</h3>
<p>(a) The denominator 1 − 0.9z<sup>−1</sup> + 0.81z<sup>−2</sup> gives
z<sup>2</sup> − 0.9z + 0.81 = 0, so z = 0.45 ± j0.779 = 0.9e<sup>±jπ/3</sup>. The magnitude is
0.9 &lt; 1, so the system is stable. (b) X(z) = 2/(1 − 0.5z<sup>−1</sup>) −
1/(1 − 0.25z<sup>−1</sup>), which agrees with the residues in Table 16.</p>
<h3>Analysis questions</h3>
<ol>
<li><strong>Effect of r on bandwidth.</strong> The −3 dB bandwidth of the resonance is about
2(1 − r) rad/sample. When r rises from 0.8 to 0.95 the bandwidth falls from
{w4['pole_pair'][1]['bw_over_pi']:.3f}π to {w4['pole_pair'][2]['bw_over_pi']:.3f}π, so a pole
closer to the unit circle gives a narrower, taller peak (and a longer-lasting impulse response).</li>
<li><strong>Pole exactly on the unit circle.</strong> The impulse response neither decays nor
grows. A complex pair at e<sup>±jθ</sup> gives a sustained sinusoid
h(n) = sin((n + 1)θ)/sinθ, and a single pole at z = 1 or z = −1 gives a constant or
alternating sequence. The system is not BIBO stable because Σ|h(n)| diverges, and an input
at that frequency gives an output that grows without bound. Such a pole is used to make an
oscillator.</li>
<li><strong>Why zeros at z = ±1 give a band-pass filter.</strong> A zero at z = 1 (ω = 0)
blocks DC and a zero at z = −1 (ω = π) blocks f<sub>s</sub>/2. With the pole pair giving gain
at 1 kHz, the response is zero at both ends of the spectrum and large in between, which is a
band-pass shape ({figure(16)}).</li>
<li><strong>Stability triangle.</strong> With A(z) = 1 + a<sub>1</sub>z<sup>−1</sup> +
a<sub>2</sub>z<sup>−2</sup>, the system is stable if |a<sub>2</sub>| &lt; 1 and
|a<sub>1</sub>| &lt; 1 + a<sub>2</sub>. (a) a<sub>1</sub> = −1.6, a<sub>2</sub> = 0.89:
|a<sub>2</sub>| &lt; 1 and 1.6 &lt; 1.89, so it is stable. (b) a<sub>1</sub> = −2.5,
a<sub>2</sub> = 1: |a<sub>2</sub>| = 1 is not less than 1, so it is unstable.
(c) a<sub>1</sub> = 0.5, a<sub>2</sub> = −0.5: |a<sub>1</sub>| = 0.5 equals 1 + a<sub>2</sub>
= 0.5, which is on the boundary of the triangle, so a pole lies on the unit circle
(z = −1) and the system is marginal. These agree with Table 18.</li>
</ol>

<h1 class="section">6. Conclusion</h1>
<p>In Lab 0, elementary discrete-time sequences were generated and plotted in Python and
Octave. The sequence a<sup>n</sup>u(n) decays for |a| &lt; 1 and grows for a &gt; 1, and the
growing case corresponds to an unstable impulse response. Both cos(2πn/8) and
cos(2πn/7.5) were shown to be periodic, with periods of 8 and 15 samples respectively.
A 4.70 s audio signal sampled at {au['fs']:,} Hz ({au['samples']:,} samples) was loaded,
normalised and displayed.</p>
<p>In Lab 1A, aliasing was demonstrated for a 7 Hz tone and the alias frequencies agreed with
|F − kf<sub>s</sub>| (3 Hz at 10 Hz, 5 Hz at 12 Hz). Decimating a chirp without a filter folded
the whole sweep into the band, while <code>signal.decimate</code> removed everything above
the new Nyquist frequency. The uniform quantiser gave an SQNR that rises by about
{w2['sqnr_bits']['slope_dB_per_bit']:.1f} dB per bit, in agreement with 6.02B + 1.76 for a
full-scale sine, and a speech-like signal had an SQNR about 20 dB lower because of its high
crest factor.</p>
<p>In Lab 1B, linear convolution was implemented from its definition and matched
<code>np.convolve</code>, which was about {w3['convolution']['speed_ratio']:.0f} times faster on
the same data. Moving-average smoothing showed the trade-off between noise reduction and
distortion. Of the three systems tested, only the moving average is LTI. Cross-correlation
found the 37-sample delay ({37/1000*343:.1f} m for a sound pulse) up to a noise level of
σ = 2 and failed at larger noise levels. The impulse response of the difference equation was
identical by recursion, <code>lfilter</code> and the closed form, and the step response settled
at H(1) = {w3['diffeq']['H1']:.3f}.</p>
<p>In Week 4, the poles and zeros of H(z) were found and plotted, and the residues from
<code>residuez</code> reproduced the impulse response from <code>lfilter</code> and the closed
form h(n) = 6(0.5)<sup>n</sup> − 5(0.25)<sup>n</sup>. Moving a pole pair towards the unit circle
made the resonance sharper and the impulse response longer, and poles on or outside the
circle gave a non-decaying or growing response. Of the four systems tested, H1 and H4 are
stable, H2 is unstable and H3 is marginal. A band-pass resonator with its peak at
{res['peak_Hz']:.0f} Hz (−3 dB bandwidth about {res['bw_Hz']:.0f} Hz) was designed with
r = 0.97 and zeros at z = ±1.</p>
<p>All objectives of the four laboratories were met.</p>

<h1 class="section">7. AI-use declaration</h1>
<p><strong>AI tool used:</strong> OpenCode (model Big Pickle). <strong>Used for:</strong>
drafting the code and the text of this report and of the four notebooks. <strong>Verification:</strong>
all four notebooks were restarted and run from top to bottom. In Lab 0 the plots were compared
with the expected results in the laboratory manual and the periodicity of the cosines was
checked numerically. In Lab 1A the alias frequencies were compared with |F − kf<sub>s</sub>| and
the SQNR values with 6.02B + 1.76 and with the crest-factor correction. In Lab 1B
<code>conv</code> was compared with <code>np.convolve</code> and with the expected result
{{1, 3, 6, 6, 4, 1}}, the three impulse responses were compared with each other, and the delay
estimate was compared with the known delay of 37 samples. In Week 4 the residues were compared
with the hand partial-fraction expansion, pole positions were compared with hand calculation
of the roots, stability results were checked with the stability triangle, and the resonator
peak and bandwidth were checked against 2(1 − r). The speech-like audio stand-in is declared
in Section 3. I can explain every line of the submitted code.</p>

<h1 class="section">Appendix A: Octave script (Lab 0, Task 1.4)</h1>
{code_block(octave_code, "octave")}
<h1>Appendix B: Python code (Lab 1A, Tasks 2.1 to 2.5)</h1>
{code_block(appb_code, "python")}
<h1>Appendix C: Python code (Lab 1B, Tasks 3.1 to 3.5)</h1>
{code_block(appc_code, "python")}
<h1>Appendix D: Python code (Week 4, Tasks 4.1 to 4.5)</h1>
{code_block(appd_code, "python")}
"""

html = ("<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>"
        "<title>COU07506 DSP Report Weeks 1-4</title>"
        f"<style>{css}</style></head><body>{body}</body></html>")
out_html = REPORT / "report.html"
out_html.write_text(html, encoding="utf-8")
print("Wrote", out_html)

pdf = REPORT / "COU07506_DSP_Report_Weeks01-04_240242479517.pdf"
cmd = [str(CHROME), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
       "--allow-file-access-from-files", f"--print-to-pdf={pdf}", out_html.as_uri()]
print("Printing PDF with Chrome ...", flush=True)
completed = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
if completed.returncode != 0:
    print(completed.stdout)
    print(completed.stderr)
    raise SystemExit("Chrome PDF generation failed")
if not pdf.exists():
    raise SystemExit("PDF was not created")
print(f"Wrote {pdf} ({pdf.stat().st_size:,} bytes)")
