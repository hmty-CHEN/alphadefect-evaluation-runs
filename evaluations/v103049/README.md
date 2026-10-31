# v103049: 1,000 games, Defect, Ascension 10

Complete game records from a 1,000-game evaluation of **AlphaDefect v103049**, the checkpoint the AlphaDefect live stream has used since 30 October 2026. For the model itself see [`docs/model.md`](../../docs/model.md).

Every decision of every game is here. For each one you can see what the model saw, which option it picked and how much probability it gave each alternative.

| Result | |
|---|---|
| Games | 1,000 (seeds RT0000–RT0999) |
| Wins | **561** |
| Win rate | **56.1%**, 95% confidence interval **53.0%–59.1%** (Wilson) |
| Win rate on the 616 seeds not used to select this checkpoint | 54.2%, 95% CI 50.3%–58.1% ([why this matters](#how-reliable-is-561)) |
| Average floor reached | 45.96 (a full run is 49 floors in most games) |

## Contents

| Path | What it is |
|---|---|
| [`transcripts/`](transcripts) | One plain-text file per game in readable English. **Start here.** |
| [`summary/runs.csv`](summary/runs.csv) | One row per game: result, how far it got, bosses faced, HP entering each boss, what killed it. |
| [`summary/results.json`](summary/results.json) | The aggregate numbers on this page. |
| [`summary/runs.jsonl`](summary/runs.jsonl) | The evaluator's original per-game record (fights, choice counts, card offers and picks, route stats). |
| [`replays/`](replays) | Raw step-by-step replays (gzip-compressed JSON Lines), one per game. The transcripts are generated from these. |
| [`routine_eval_seeds.txt`](routine_eval_seeds.txt) | The 384 seeds shared with the routine evaluation that selected this checkpoint. |
| [`meta.json`](meta.json) | Model version, character, Ascension, game version and seed range. |

How to read them: [`docs/reading-records.md`](../../docs/reading-records.md). Field reference for the replays: [`docs/replay-format.md`](../../docs/replay-format.md).

## How the games were played

- Character Defect, Ascension 10, game logic v0.111.0, in the same headless engine used for training.
- Seeds RT0000 to RT0999. These are fixed test seeds. Training games use other seeds.
- Greedy policy, exactly as on stream. With the same seed, weights and engine build a game always plays out identically.
- Played on 30 October 2026 on one RTX 3090, before the engine's start-up seed handling was changed to match the real game (see the [repository notes](../../README.md#notes)).
- One game (RT0876) reached the 6,000-decision limit in an endless Act 3 fight, where the model kept ending its turn with no cards left and neither side could win. It is counted as a loss.
- Training started on 25 October 2026 and reached this checkpoint on 30 October, on rented RTX 4090 and RTX 3090 machines.

## Results in detail

**How far runs got**

| Stage | Share of all games |
|---|---|
| Reached Act 2 | 96.2% |
| Reached Act 3 | 88.5% |
| Reached the first Act 3 boss | 84.4% |
| Beat the first Act 3 boss (of those who reached it) | 91.1% |
| Won (of those who reached the second Act 3 boss) | 73.0% |

Act 3 ends with two boss fights in a row, with no rest in between.

**Where runs ended**

| Ending | Games |
|---|---|
| Victory | 561 |
| Died at an Act 3 boss | 283 |
| Died in Act 2 | 77 |
| Died in Act 3 before the bosses | 40 |
| Died in Act 1 | 38 |
| Stalled (decision limit) | 1 |

The most common killers were the three Act 3 bosses, Aeonglass (118), Queen (86) and Test Subject (79), followed by the Act 2 boss Knowledge Demon (33).

### How reliable is 56.1%?

The 95% confidence interval of 53.0%–59.1% covers only the randomness of the 1,000 seeds. Two further points matter:

1. **Selection.** During training a routine evaluation plays 384 seeds that are a subset of RT0000–RT0999 (listed in `routine_eval_seeds.txt`). v103049 was chosen for this 1,000-game test because it scored 59.1% on those 384 seeds, one of the highest results of any checkpoint. The games on those seeds are identical in both tests, so part of that luck is carried into the 56.1% here. On the other **616 seeds** the model won **54.2% (95% CI 50.3%–58.1%)**, the least biased estimate of its strength.
2. **Luck within a seed.** One different card play changes how the game's random numbers are used, and the rest of the run can turn out very differently. The same seed is not equally hard for every checkpoint, so the per-seed results here say more about this checkpoint's games than about the seeds.

For comparison, on the same 1,000 seeds the previous live-stream checkpoint, v89500, won 49.9% (95% CI 46.8%–53.0%). Comparing seed by seed, only v103049 won on 222 seeds and only v89500 won on 160 (two-sided sign test p = 0.002). The later checkpoint [v130051](../v130051) won 70.9% on the same seeds.
