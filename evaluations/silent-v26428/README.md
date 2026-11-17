# silent-v26428: 1,000 games, Silent, Ascension 10

Complete game records from a 1,000-game evaluation of the **AlphaDefect Silent model at checkpoint 26,428**, the checkpoint the live stream has used for the Silent since 12 November 2026. For the models themselves see [`docs/model.md`](../../docs/model.md).

Every decision of every game is here. For each one you can see what the model saw, which option it picked and how much probability it gave each alternative.

| Result | |
|---|---|
| Games | 1,000 (seed pool W1, listed in [`seeds.txt`](seeds.txt)) |
| Wins | **712** |
| Win rate | **71.2%**, 95% confidence interval **68.3%–73.9%** (Wilson) |
| Average floor reached | 45.38 (a full run is 49 floors in most games) |
| Game version | v0.111.0 |

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

- Character Silent, Ascension 10, game logic v0.111.0, in the same headless engine used for training.
- 1,000 seeds from a fixed test pool (W1) that the Silent model never played in training. The [Regent evaluation](../regent-v53840) uses the same seeds.
- Greedy policy: the highest-probability option is always played, with no search. The weights are an exponential moving average of the training weights, the same weights the live stream uses.
- Two rules from the routine evaluation that runs during training were in force. A fight in which the enemies' combined HP has not reached a new low for 20 player turns is scored as a loss, and a turn that keeps returning to the same position is ended. The 20-turn rule decided one game: QAYRGK2UHM, an Act 3 fight on floor 45 in which an Axebot on 4 HP took no further damage for 20 turns.
- Played on 12 November 2026 (05:19–05:22 UTC) on one RTX 4090.
- No game reached the decision limit.

## Results in detail

**How far runs got**

| Stage | Share of all games |
|---|---|
| Reached Act 2 | 92.9% |
| Reached Act 3 | 87.7% |
| Reached the first Act 3 boss | 86.1% |
| Beat the first Act 3 boss (of those who reached it) | 96.1% |
| Won (of those who reached the second Act 3 boss) | 86.1% |

Act 3 ends with two boss fights in a row, with no rest in between.

**Where runs ended**

| Ending | Games |
|---|---|
| Victory | 712 |
| Died at an Act 3 boss | 149 |
| Died in Act 1 | 71 |
| Died in Act 2 | 52 |
| Died in Act 3 before the bosses | 16 |
| Stalled (decision limit) | 0 |

The most common killers were the three Act 3 bosses, Test Subject (68), Aeonglass (44) and Queen (37), followed by the Act 2 bosses The Insatiable (12) and Kaiser Crab (11) and the Act 1 boss Lagavulin Matriarch (11).

### How reliable is 71.2%?

1. **Sampling.** The 95% confidence interval of 68.3%–73.9% covers only the randomness of the 1,000 seeds.
2. **Selection.** This checkpoint went onto the live stream partly because of this result, so 71.2% is more likely to be a little high than a little low. A later checkpoint of the same run scored 69.6% on the same seeds.
3. **Luck within a seed.** One different card play changes how the game's random numbers are used, and the rest of the run can turn out very differently, so the per-seed results say more about this checkpoint's games than about the seeds.

## Relation to the live stream

These are the weights the live stream has used for the Silent since 12 November 2026. The stream has since moved to game version v0.113, while these games use v0.111.0, so stream results and these records are not directly comparable.

## Reproducing the games

A game replays identically with the same seed, weights and engine build. These games use game logic v0.111.0; later game versions change some cards, monsters and events, so the same seeds do not give the same games there.
