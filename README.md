# Player Stat Projection Model: Louisville Players, 2025–26 Season

## Summary
A Python backtesting project that projects each player's points, rebounds, and assists game by game using only prior games, then measures how far those projections were from the actual results.

## Methods
Each method projects a player's stat for a game using only games played before it:
- **Rolling average (3, 5, 10 games):** the average of the player's last N games.
- **Season-to-date average:** the average of all the player's prior games.
- **League average:** the average of every player's prior games combined.

All methods are scored on the same games (each player needs at least 3 prior games), so the comparison is fair.

**Train/test split:** Games before January 17, 2026 (75 games) were used to choose the rolling window. Games from January 17 onward (81 games) were used for the final results, so the window was not chosen on the games it was judged on.

**Metrics:** Mean absolute error (MAE), bias (projected minus actual), and the percentage of games where the projection landed within one MAE of the actual result.

## Data
**Data verification:** All 156 scored games (2025–26 regular season, six players) were checked against official box scores. No discrepancies were found.

- Source: CBS Sports player game log pages, 2025–26 regular-season games only. Postseason games are excluded.
- Players: Mikel Brown Jr., Ryan Conwell, Isaac McKneely, Adrian Wooley, Sananda Fru, and J'Vonne Hadley, all Louisville players in 2025–26. Each player's first 3 games are used as warm-up, so 156 games are scored in total.
- Home/away: "vs" treated as home (1), "@" as away (0). Neutral-site games were not separately identified.
- Data was entered by hand from the source tables and then verified against official box scores, as described above.

## Results

**Final held-out test (81 games, using the 10-game window chosen on training data):**

| Stat | 10-game rolling MAE | Season-average MAE | League-average MAE |
|---|---|---|---|
| Points | **5.13** | 5.27 | 5.97 |
| Rebounds | 1.67 | **1.60** | 1.78 |
| Assists | 1.19 | **1.17** | 1.30 |

**Full comparison (all 156 scored games):**

| Stat | Rolling 3 | Rolling 5 | Rolling 10 | Season avg | League avg |
|---|---|---|---|---|---|
| Points | 5.36 | 5.09 | 4.99 | 5.06 | 5.64 |
| Rebounds | 1.81 | 1.76 | 1.69 | **1.65** | 1.77 |
| Assists | 1.28 | 1.26 | 1.19 | 1.18 | 1.32 |

**What the results show**
- Both simple methods beat the league average on every stat, so the player's own history carries real information.
- The 10-game window was the best rolling option on all three stats across the full data. Longer windows smooth out the noise in single-game performance.
- A season-average projection was competitive with the best rolling model. It was better on rebounds and assists, and essentially tied on points.
- The projections landed within one MAE of the actual result about 55 to 65 percent of the time, which means the error is typical rather than rare.

**Takeaway:** Simple averages are a strong baseline for these stats. Improving on them will likely need information the model doesn't use yet, such as opponent, rest, or injury news.

Per-player details are in `results/evaluation/per_player_comparison.csv`.

## Line Calibration (Prop-Style Check)
PrizePicks-style props are set as lines. As a check, each player's 10-game rolling average was treated as the line, and the number of games where the player finished over or under it was counted across all 156 scored games.

| Stat | Over | Under | Push (exact) |
|---|---|---|---|
| Points | 50.0% | 49.4% | 0.6% |
| Rebounds | 45.5% | 51.3% | 3.2% |
| Assists | 42.9% | 50.6% | 6.4% |

**What it shows:** A fair line should finish over about half the time. Points are well calibrated. Assists finished over only 43% of the time, which suggests a rolling average sits slightly high for assists in this sample.

**Caution:** These are small samples. The assists gap is about 1.8 standard errors from 50%, which is suggestive but not conclusive. Per-player rates (for example, 63% over on points for J'Vonne Hadley) rest on 27 to 28 games and should not be read as reliable.

Run with `python code/line_calibration.py`. Output is in `results/evaluation/line_calibration_*.csv`.

## Limitations
- **Small sample:** 156 scored games across six players, and only 81 in the held-out test. Differences of 0.05 MAE or less are within the noise. Results describe this method on this data, not a general accuracy claim.
- **Page header:** The CBS pages show each player's current team, which can differ from the 2025–26 season (for example, Brooklyn Nets and Miami Heat for NBA-linked pages, and Marquette for Sananda Fru). The game tables are the 2025–26 Louisville games, against ACC and Big 12 opponents.
- **Simple model:** These averages ignore opponent strength, rest, injuries, role changes, and lineup context.
- **Volatile stats:** Points varied widely (for example, 5 to 45 for Mikel Brown Jr.), so any average-based projection will miss often.
- **Manual data entry:** Errors in transcription would affect the results.

## Planned Next Steps
1. Verify each game row against an official box score (a 15 to 20 game spot-check is recommended).
2. Add opponent strength and rest-day features and test whether they beat the season average.
3. Add injury and lineup news as an input and measure how much it changes the error.
4. Add more Louisville players for a larger test sample.

## Folder Contents
- `code/evaluate.py`: runs every comparison and the train/test split
- `code/line_calibration.py`: checks how often players finish over a rolling-average line
- `code/projection_model.py`: the original projection script (5-game rolling average with a minutes adjustment)
- `data/`: per-player and combined game logs
- `results/evaluation/`: all comparison tables, including per-player results and every projection
- `results/`: earlier per-player runs from the original script

## How to Reproduce
1. Install Python 3 and pandas (`pip install pandas`).
2. From the project folder, run `python code/evaluate.py`.
3. The tables are written to `results/evaluation/`. Results will match the tables above.

## NFL Extension: Lamar Jackson, 2022 to 2025 Regular Seasons

The same method was applied to Lamar Jackson's regular-season games, using passing yards, passing touchdowns, and rushing yards. Data: CBS Sports game logs. Files: `data/nfl/lamar_jackson_2022.csv`, `lamar_jackson_2023.csv`, `lamar_jackson_2024_25.csv`, the combined `data/nfl/lamar_jackson_2022_25.csv`, and `code/nfl_evaluate.py`. Output: `results/nfl/`.

**Data notes**
- 2022: 12 games played. Five games with no stats are excluded (Dec 11, Dec 17, Dec 24, Jan 1, Jan 8). The Dec 4, 2022 game against Denver is included even though it's partial (he left early).
- 2023: 16 games played. The Jan 6, 2024 game is excluded because he did not play.
- 2024: 17 games. 2025: 13 games played. Four 2025 games (Oct 5, Oct 12, Oct 26, Dec 27) are excluded because he did not play.
- Postseason games are excluded.
- Warm-up: the first 3 games of each season are not scored, so 55 games are scored in total.
- Split: games before September 22, 2024 (27 games) were used to choose the window. Games from that date on (28 games) were used for the final test.
- Home/away: "vs" = home, "@" = away.
- With one player, the "league average" equals the season average, so it adds no separate information.

**Held-out test (28 games, window chosen on the first 27 games)**

| Stat | Rolling average MAE | Season-average MAE | Notes |
|---|---|---|---|
| Passing yards | 48.7 (10-game) | 49.2 | Essentially tied |
| Passing TDs | **1.16** (5-game) | 1.23 | Recent form better |
| Rushing yards | **21.8** (10-game) | 24.3 | Recent form better |

**All 55 scored games:** The 10-game average was slightly better than the season average on passing yards (51.9 vs 52.8). The 5-game average was best on passing TDs (1.12 vs 1.18) and rushing yards (21.5 vs 23.6).

**What it shows:** With four seasons, recent form has a small, consistent edge on touchdowns and rushing yards, and passing yards are a tie. The season average is no longer clearly better on touchdowns, which changed from the three-season result. The gaps are small, and the best window differs from stat to stat, so these findings are suggestive. Both methods projected his 2025 rushing too high, which reflects a drop in rushing production.

**Caution:** 28 test games is still a small sample, the window was chosen on a single split, and quarterback stats depend heavily on opponent and game script, which the model doesn't account for.

Run with `python code/nfl_evaluate.py`.
