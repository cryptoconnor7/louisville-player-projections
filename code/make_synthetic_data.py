"""
Generates FAKE random test data (not real players or games).
Used only to check that projection_model.py runs correctly. Do not use for results.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
rows = []
for p in range(8):
    base = {"points": rng.uniform(6, 18), "rebounds": rng.uniform(2, 8), "assists": rng.uniform(1, 6)}
    minutes_base = rng.uniform(15, 34)
    for g in range(30):
        row = {
            "player": f"Test Player {p+1}",
            "date": pd.Timestamp("2025-11-01") + pd.Timedelta(days=2 * g),
            "opponent": f"Opponent {rng.integers(1, 15)}",
            "home": int(rng.integers(0, 2)),
            "minutes": max(5, rng.normal(minutes_base, 4)),
        }
        for stat in base:
            row[stat] = max(0, round(rng.normal(base[stat], base[stat] * 0.35)))
        rows.append(row)

pd.DataFrame(rows).to_csv("synthetic_test_games.csv", index=False)
print("Wrote synthetic_test_games.csv (FAKE DATA FOR TESTING ONLY)")
