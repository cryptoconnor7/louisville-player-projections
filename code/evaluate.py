"""
Compares projection methods on Louisville 2025-26 game logs.

Methods (each uses ONLY games played before the game being projected):
  - rolling_3, rolling_5, rolling_10: average of the player's last N games
  - season_to_date: average of all the player's prior games
  - league_average: average of all players' prior games (all players combined)

Every method is scored on the SAME set of games (games where every method has
at least MIN_PRIOR prior games), so the comparison is fair.

Train/test split: games before SPLIT_DATE are used to choose the rolling
window; games on/after SPLIT_DATE are used to report final results.

Usage (from the project folder):
    python code/evaluate.py
Writes all tables to results/evaluation/.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "combined_games_2025_26.csv"
OUT = ROOT / "results" / "evaluation"
STATS = ["points", "rebounds", "assists"]
MIN_PRIOR = 3
WINDOWS = [3, 5, 10]


def build_projections(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["date", "player"]).reset_index(drop=True)
    grp = df.groupby("player")
    for stat in STATS:
        for w in WINDOWS:
            df[f"rolling_{w}_{stat}"] = grp[stat].transform(
                lambda s: s.shift(1).rolling(w, min_periods=MIN_PRIOR).mean())
        df[f"season_{stat}"] = grp[stat].transform(
            lambda s: s.shift(1).expanding(min_periods=MIN_PRIOR).mean())
        # League average: mean of ALL players' prior games, by date
        daily = df.groupby("date")[stat].agg(["sum", "count"]).sort_index()
        prior_sum = daily["sum"].shift(1).fillna(0).cumsum()
        prior_cnt = daily["count"].shift(1).fillna(0).cumsum()
        league = (prior_sum / prior_cnt).where(prior_cnt >= MIN_PRIOR)
        df[f"league_{stat}"] = df["date"].map(league)
    return df


def scored_subset(df: pd.DataFrame) -> pd.DataFrame:
    cols = [f"{m}_{s}" for s in STATS for m in
            [f"rolling_{w}" for w in WINDOWS] + ["season", "league"]]
    return df.dropna(subset=cols).copy()


def mae_table(df: pd.DataFrame, methods: list[str]) -> pd.DataFrame:
    rows = []
    for stat in STATS:
        for m in methods:
            err = df[f"{m}_{stat}"] - df[stat]
            rows.append({"stat": stat, "method": m,
                         "games": len(df),
                         "MAE": round(err.abs().mean(), 3),
                         "bias": round(err.mean(), 3)})
    return pd.DataFrame(rows)


def within_one_mae(df: pd.DataFrame, method: str, stat: str, mae: float) -> float:
    err = (df[f"{method}_{stat}"] - df[stat]).abs()
    return round((err <= mae).mean() * 100, 1)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(DATA, parse_dates=["date"])
    full = build_projections(raw)
    games = scored_subset(full)

    dates = games["date"].sort_values().reset_index(drop=True)
    split_date = dates.iloc[int(len(dates) * 0.5)]
    train = games[games["date"] < split_date]
    test = games[games["date"] >= split_date]

    methods = [f"rolling_{w}" for w in WINDOWS] + ["season", "league"]

    # 1) All methods on all scored games (full comparison)
    all_tbl = mae_table(games, methods)
    all_tbl.to_csv(OUT / "method_comparison_all_games.csv", index=False)

    # 2) Window choice uses TRAIN only
    train_tbl = mae_table(train, [f"rolling_{w}" for w in WINDOWS])
    train_tbl.to_csv(OUT / "window_selection_train.csv", index=False)
    best = {}
    for stat in STATS:
        sub = train_tbl[train_tbl.stat == stat]
        best[stat] = sub.sort_values("MAE").iloc[0]["method"]

    # 3) Final report on TEST only, using the train-chosen window
    test_rows = []
    for stat in STATS:
        chosen = best[stat]
        for m in [chosen, "season", "league"]:
            err = test[f"{m}_{stat}"] - test[stat]
            mae = err.abs().mean()
            test_rows.append({
                "stat": stat,
                "method": m,
                "test_games": len(test),
                "MAE": round(mae, 3),
                "bias": round(err.mean(), 3),
                "pct_within_1_MAE": within_one_mae(test, m, stat, mae),
            })
    test_tbl = pd.DataFrame(test_rows)
    test_tbl.to_csv(OUT / "final_test_results.csv", index=False)

    # 4) Per-player results on all scored games (chosen rolling window vs season)
    per_player = []
    for p, g in games.groupby("player"):
        for stat in STATS:
            per_player.append({
                "player": p, "stat": stat, "games": len(g),
                "rolling_5_MAE": round((g[f"rolling_5_{stat}"] - g[stat]).abs().mean(), 3),
                "season_MAE": round((g[f"season_{stat}"] - g[stat]).abs().mean(), 3),
                "league_MAE": round((g[f"league_{stat}"] - g[stat]).abs().mean(), 3),
            })
    pd.DataFrame(per_player).to_csv(OUT / "per_player_comparison.csv", index=False)

    # Save scored games with all projections for auditing
    games.to_csv(OUT / "all_projections.csv", index=False)

    print(f"Scored games: {len(games)} | Train: {len(train)} | Test: {len(test)} | Split date: {split_date.date()}")
    print("\nAll scored games:\n", all_tbl.to_string(index=False))
    print("\nWindow selection (train only):\n", train_tbl.to_string(index=False))
    print("\nChosen window per stat (from train):", best)
    print("\nFinal TEST results:\n", test_tbl.to_string(index=False))


if __name__ == "__main__":
    main()
