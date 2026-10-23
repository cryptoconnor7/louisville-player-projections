"""
Player stat projection model with backtesting.

Input CSV columns (one row per player per game):
    player, date, opponent, home (1/0), minutes, points, rebounds, assists

For each player and game, the model projects points, rebounds, and assists
using ONLY games played before that game (no lookahead). It then compares
projections to actual results and reports MAE and bias.

Usage:
    python projection_model.py games.csv --window 5
"""
import argparse
import pandas as pd

STATS = ["points", "rebounds", "assists"]


def add_projections(df: pd.DataFrame, window: int) -> pd.DataFrame:
    df = df.sort_values(["player", "date"]).copy()
    for stat in STATS:
        # Rolling mean of the player's previous `window` games (shift avoids lookahead)
        base = (
            df.groupby("player")[stat]
            .transform(lambda s: s.shift(1).rolling(window, min_periods=3).mean())
        )
        df[f"proj_{stat}"] = base
    # Simple adjustment: scale by minutes relative to the player's prior average minutes
    prior_min = df.groupby("player")["minutes"].transform(
        lambda s: s.shift(1).rolling(window, min_periods=3).mean()
    )
    ratio = (df["minutes"].fillna(prior_min) / prior_min).clip(0.5, 1.5)
    for stat in STATS:
        df[f"proj_{stat}"] = df[f"proj_{stat}"] * ratio.where(ratio.notna(), 1.0)
    return df


def evaluate(df: pd.DataFrame) -> pd.DataFrame:
    scored = df.dropna(subset=[f"proj_{s}" for s in STATS])
    rows = []
    for stat in STATS:
        err = scored[f"proj_{stat}"] - scored[stat]
        rows.append({
            "stat": stat,
            "games_scored": len(scored),
            "MAE": round(err.abs().mean(), 2),
            "bias (proj - actual)": round(err.mean(), 2),
        })
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv")
    parser.add_argument("--window", type=int, default=5)
    parser.add_argument("--out", default="projections_vs_actual.csv")
    args = parser.parse_args()

    games = pd.read_csv(args.csv, parse_dates=["date"])
    projected = add_projections(games, args.window)
    projected.to_csv(args.out, index=False)
    print(evaluate(projected).to_string(index=False))
    print(f"\nSaved: {args.out}")


if __name__ == "__main__":
    main()
