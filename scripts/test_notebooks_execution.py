"""Automated test runner for standalone Jupyter Notebook execution.
Tests each notebook by executing all its code cells in an isolated namespace.
"""
import sys
import json
from pathlib import Path
import os

# Ensure non-blocking matplotlib across entire process
os.environ["MPLBACKEND"] = "Agg"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def noop_show(*args, **kwargs):
    pass

plt.show = noop_show
if "matplotlib.pyplot" in sys.modules:
    sys.modules["matplotlib.pyplot"].show = noop_show

REPO_ROOT = Path(__file__).resolve().parent.parent

def test_notebook(nb_path: Path) -> bool:
    print(f"Testing {nb_path.name}...")
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = json.load(f)
    
    # Guarantee plt.show does not block even if re-imported
    import matplotlib.pyplot as p
    p.show = noop_show
    sys.modules["matplotlib.pyplot"].show = noop_show
    
    ns = {
        "__name__": "__main__",
        "__file__": str(nb_path),
        "sys": sys,
        "plt": p
    }
    
    code_cells = [c for c in nb.get("cells", []) if c.get("cell_type") == "code"]
    for i, cell in enumerate(code_cells):
        src = "".join(cell.get("source", []))
        try:
            exec(src, ns)
        except Exception as e:
            print(f"  [FAIL] Cell #{i} raised {type(e).__name__}: {e}")
            return False
    print(f"  [PASS] {nb_path.name} executed completely standalone with 0 errors!")
    return True

if __name__ == "__main__":
    days_to_test = range(1, 41)
    if len(sys.argv) > 1:
        days_to_test = [int(x) for x in sys.argv[1:]]
    
    failed = []
    passed = []
    for d in days_to_test:
        day_dir = REPO_ROOT / f"day{d:02d}"
        nb_files = list(day_dir.glob("*.ipynb"))
        if not nb_files:
            continue
        nb_path = nb_files[0]
        ok = test_notebook(nb_path)
        if ok:
            passed.append(d)
        else:
            failed.append(d)
    
    print("\n" + "="*50)
    print(f"PASSED ({len(passed)}): Day {passed}")
    if failed:
        print(f"FAILED ({len(failed)}): Day {failed}")
        sys.exit(1)
    else:
        print("ALL TESTED NOTEBOOKS PASSED WITH 100% SUCCESS!")
