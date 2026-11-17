# fool-v23981: 1,000 games, Fool, Ascension 10

Complete game records from a 1,000-game evaluation of the **AlphaDefect Fool model at checkpoint 23,981**, three and a half days after its training started from scratch. The Fool was added to the game in v0.113.0, and these games use that version. For the models themselves see [`docs/model.md`](../../docs/model.md).

Every decision of every game is here. For each one you can see what the model saw, which option it picked and how much probability it gave each alternative.

| Result | |
|---|---|
| Games | 1,000 (seed pool F25, listed in [`seeds.txt`](seeds.txt)) |
| Wins | **592** |
| Win rate | **59.2%**, 95% confidence interval **56.1%–62.2%** (Wilson) |
| Average floor reached | 44.93 (a full run is 49 floors) |
| Game version | v0.113.0 |

## Contents

| Path | What it is |
|---|---|
| [`transcripts/`](transcripts) | One plain-text file per game in readable English. **Start here.** |
| [`summary/runs.csv`](summary/runs.csv) | One row per game: result, how far it got, bosses faced, HP entering each boss, what killed it. |
| [`summary/results.json`](summary/results.json) | The aggregate numbers on this page. |
| [`summary/runs.jsonl`](summary/runs.jsonl) | The evaluator's original per-game record (fights, choice counts, card offers and picks, route stats). |
| [`replays/`](replays) | Raw step-by-step replays (gzip-compressed JSON Lines), one per game. The transcripts are generated from these. |
| [`seeds.txt`](seeds.txt) | The 1,000 seeds, in the order the summary lists them. |
| [`meta.json`](meta.json) | Checkpoint version, character, Ascension, game version and seed pool. |

How to read them: [`docs/reading-records.md`](../../docs/reading-records.md). Field reference for the replays: [`docs/replay-format.md`](../../docs/replay-format.md).

## How the games were played

- Character Fool, Ascension 10, game logic v0.113.0, in the same headless engine used for training.
- 1,000 seeds (pool F25) drawn fresh for this test. They were not used in training or in any earlier test.
- Greedy policy: the highest-probability option is always played, with no search. The weights are an exponential moving average of the training weights.
- Two rules from the routine evaluation that runs during training were in force. A fight in which the enemies' combined HP has not reached a new low for 20 player turns is scored as a loss, and a turn that keeps returning to the same position is ended. The 20-turn rule did not decide any game here.
- Played on 16 November 2026 (14:16–14:19 UTC) on one RTX 4090.
- No game reached the decision limit.

## Results in detail

**How far runs got**

| Stage | Share of all games |
|---|---|
| Reached Act 2 | 93.0% |
| Reached Act 3 | 84.8% |
| Reached the first Act 3 boss | 82.4% |
| Beat the first Act 3 boss (of those who reached it) | 91.6% |
| Won (of those who reached the second Act 3 boss) | 78.4% |

Act 3 ends with two boss fights in a row, with no rest in between.

**Where runs ended**

| Ending | Games |
|---|---|
| Victory | 592 |
| Died at an Act 3 boss | 232 |
| Died in Act 2 | 82 |
| Died in Act 1 | 70 |
| Died in Act 3 before the bosses | 24 |
| Stalled (decision limit) | 0 |

The most common killers were the three Act 3 bosses, Aeonglass (104), Queen (73) and Test Subject (55), followed by the Act 2 boss Knowledge Demon (24).

### How reliable is 59.2%?

1. **Sampling.** The 95% confidence interval of 56.1%–62.2% covers only the randomness of the 1,000 seeds.
2. **Selection.** The seeds are new, but this was the best of three candidates from the same training run tested on them (the other two scored 56.3% and 57.3%). The gaps are within chance, and 59.2% is more likely to be a little high than a little low.
3. **Luck within a seed.** One different card play changes how the game's random numbers are used, and the rest of the run can turn out very differently, so the per-seed results say more about this checkpoint's games than about the seeds.

## Relation to the live stream

Since 17 November 2026 the live stream has used checkpoint 24,181 of the same training run, 200 policy updates after this one. On the stream it also searches in boss and elite fights. Its games are not in this repository.

## Names in the transcripts

Game version v0.113.0 renamed a few existing monster moves and powers without changing what they do. The vocabulary keeps one entry for each, so the transcripts show the earlier v0.111.0 name for those (for example, the Rocket's moves).

## Reproducing the games

A game replays identically with the same seed, weights and engine build. These games use game logic v0.113.0.
