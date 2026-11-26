# COU 07506 — DSP Laboratory Work, Weeks 1–4

Student: **Zaid Yaseer Yussuf** — Registration No. **240242479517** — Class **BEng24COE**

This repository contains the individual laboratory submissions for Weeks 1–4 of
COU 07506 Digital Signal Processing (2026/27, Semester I), following the laboratory
manual `COU07506_DSP_Laboratory_Manual_2026-27.pdf` and the student report
`Zaid Yaseer yussuf-240242479517.pdf`.

## Contents

| Path | Description |
|---|---|
| `notebooks/COU07506_Week01_240242479517.ipynb` | Lab 0 — setup, elementary sequences, audio |
| `notebooks/COU07506_Week02_240242479517.ipynb` | Lab 1A — aliasing, decimation, quantization |
| `notebooks/COU07506_Week03_240242479517.ipynb` | Lab 1B — convolution, correlation, difference equations |
| `notebooks/COU07506_Week04_240242479517.ipynb` | Week 4 — z-transform, poles/zeros, stability, resonator |
| `report/COU07506_DSP_Report_Weeks01-04_240242479517.pdf` | Updated individual report with figures from the executed notebooks |
| `report/report.html` | HTML source used to print the PDF |
| `report/figures/` | Figures saved by the notebooks |
| `report/results_weekNN.json` | Numerical results exported by each notebook |
| `data/my_voice.wav` | Reproducible 16 kHz, 4.70 s speech-like stand-in used in Week 1 |
| `tools/` | Scripts used to generate the audio, notebooks and report |

## Running the notebooks

Install the packages and run all cells from top to bottom:

```powershell
python -m pip install -r requirements.txt
cd notebooks
jupyter notebook
```

Open each notebook and use **Kernel → Restart & Run All**. Every notebook begins
with imports, writes its figures to `report/figures/`, and exports its numbers to
`report/results_weekNN.json`. The code uses paths relative to the repository root,
so it works both from Jupyter opened in `notebooks/` and from `nbconvert`.

To regenerate everything programmatically:

```powershell
python tools/make_data.py
python tools/build_notebooks.py
python tools/execute_notebooks.py
python tools/make_report.py
```

## Important notes before submission

1. **Audio:** The original phone recording was not supplied with the source files.
   A deterministic speech-like WAV with the same parameters used in the report
   (16 kHz, 4.70 s, 75 200 samples, 16-bit mono PCM) is included at
   `data/my_voice.wav`. If you have your own recording, replace that file; the
   notebook reads any WAV at that path and reports its actual sampling rate.
   This substitution is declared in the report and in the notebook.
2. **AI use:** An AI assistant (OpenCode, model Big Pickle) was used to draft code
   and text. Every generated number was verified by executing the notebooks and
   comparing with the analytical results in the manual. Each notebook ends with
   an AI-use statement, as required by the manual.
3. **Git:** This is a local Git repository. Push it to your own GitHub account with
   `git remote add origin <URL>` and `git push -u origin main` once you have access.
4. **Checkpoint signatures, group members and mini-project proposal** are not
   included because they must be supplied by you during the laboratory sessions.

## Verification summary

- Week 1: `0.8^10 = 0.1074`; cosine periods 8 and 15 samples; audio parameters printed from the WAV header.
- Week 2: alias frequencies 3, 5, 7, 7 Hz; measured SQNR slope ≈ 6.3 dB/bit; crest-factor penalty ≈ 19.4 dB.
- Week 3: convolution matches `np.convolve`; only the moving average is LTI; delay 37 samples; three impulse-response methods agree.
- Week 4: residues reproduce `h(n) = 6(0.5)^n − 5(0.25)^n`; H1/H4 stable, H2 unstable, H3 marginal; resonator peaks at 1 kHz.
