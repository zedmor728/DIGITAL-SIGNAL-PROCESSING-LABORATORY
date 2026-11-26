"""Restart and execute all four notebooks from top to bottom."""
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = ROOT / "notebooks"

for week in range(1, 5):
    path = NOTEBOOKS / f"COU07506_Week{week:02d}_240242479517.ipynb"
    print(f"Executing {path.name} ...", flush=True)
    nb = nbformat.read(path, as_version=4)
    ep = ExecutePreprocessor(timeout=900, kernel_name="python3", allow_errors=False)
    ep.preprocess(nb, {"metadata": {"path": str(NOTEBOOKS)}})
    nbformat.write(nb, path)
    print(f"  finished {path.name}", flush=True)

print("All notebooks executed without errors.")
