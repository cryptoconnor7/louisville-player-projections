"""
Runs the same comparison as evaluate.py on Lamar Jackson's regular-season
games (2022 to 2025 seasons), using passing yards, passing TDs, and rushing yards.

Run from the project folder:
    python code/nfl_evaluate.py
Writes tables to results/nfl/.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import evaluate as ev  # reuses the same methods, metrics, and train/test split

ev.STATS = ["passing_yds", "passing_tds", "rushing_yds"]
ev.DATA = ROOT / "data" / "nfl" / "lamar_jackson_2022_25.csv"
ev.OUT = ROOT / "results" / "nfl"

if __name__ == "__main__":
    ev.main()
