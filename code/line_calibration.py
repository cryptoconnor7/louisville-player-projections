"""
Line calibration check.

Treats each player's 10-game rolling average (known before the game) as the
line, then measures how often the player actually finished OVER it.
If the average is a fair line, the over rate should be near 50%.
Pushes (actual exactly equal to the line) are counted separately.

Run from the project folder:
    python code/line_calibration.py
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "results" / "evaluation" / "all_projections.csv"
OUT = ROOT / "results" / "evaluation"
STATS = ["points", "rebounds", "assists"]


def over_under_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for stat in STATS:
        line = df[f"rolling_10_{stat}"]
        actual = df[stat]
        n = len(df)
        over = (actual > line).sum()
        under = (actual < line).sum()
        push = (actual == line).sum()
        rows.append({
            "stat": stat,
            "games": n,
            "over_pct": round(over / n * 100, 1),
            "under_pct": round(under / n * 100, 1),
            "push_pct": round(push / n * 100, 1),
        })
    return pd.DataFrame(rows)


def main():
    df = pd.read_csv(SRC, parse_dates=["date"])
    overall = over_under_table(df)
    overall.to_csv(OUT / "line_calibration_overall.csv", index=False)

    per_player = []
    for player, g in df.groupby("player"):
        t = over_under_table(g)
        t.insert(0, "player", player)
        per_player.append(t)
    per_player = pd.concat(per_player, ignore_index=True)
    per_player.to_csv(OUT / "line_calibration_per_player.csv", index=False)

    print("Overall:\n", overall.to_string(index=False))
    print("\nPer player:\n", per_player.to_string(index=False))


if __name__ == "__main__":
    main()
