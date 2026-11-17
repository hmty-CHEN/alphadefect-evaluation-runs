# regent-v53840: 1,000 games, Regent, Ascension 10

Complete game records from a 1,000-game evaluation of the **AlphaDefect Regent model at checkpoint 53,840**, three days after its training started from scratch. For the models themselves see [`docs/model.md`](../../docs/model.md).

Every decision of every game is here. For each one you can see what the model saw, which option it picked and how much probability it gave each alternative.

| Result | |
|---|---|
| Games | 1,000 (seed pool W1, listed in [`seeds.txt`](seeds.txt)) |
| Wins | **722** |
| Win rate | **72.2%**, 95% confidence interval **69.3%–74.9%** (Wilson) |
| Average floor reached | 47.07 (a full run is 49 floors in most games) |
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

How to read them: [`docs/reading-records.md`](../../docs/reading-records.md). Field reference for the replays: [`docs/replay-format.md`](../../docs/replay-format.md). Regent replays also record the Regent's stars and the star cost of each card in hand, and the transcripts show them.

## How the games were played

- Character Regent, Ascension 10, game logic v0.111.0, in the same headless engine used for training.
- 1,000 seeds from a fixed test pool (W1) that the Regent model never played in training. The [Silent evaluation](../silent-v26428) uses the same seeds.
- Greedy policy: the highest-probability option is always played, with no search. The weights are an exponential moving average of the training weights.
- Two rules from the routine evaluation that runs during training were in force. A fight in which the enemies' combined HP has not reached a new low for 20 player turns is scored as a loss, and a turn that keeps returning to the same position is ended. The 20-turn rule did not decide any game here.
- Played on 9 November 2026 (07:56–08:16 UTC) on one RTX 3090.
- One game (K5BM8YY7G2) reached the 6,000-decision limit in the Act 1 boss fight against Soul Fysh, where the model replayed Particle Wall+, which returns to the hand when played, thousands of times in one turn. It is counted as a loss.

## Results in detail

**How far runs got**

| Stage | Share of all games |
|---|---|
| Reached Act 2 | 97.8% |
| Reached Act 3 | 92.0% |
| Reached the first Act 3 boss | 90.8% |
| Beat the first Act 3 boss (of those who reached it) | 94.3% |
| Won (of those who reached the second Act 3 boss) | 84.3% |

Act 3 ends with two boss fights in a row, with no rest in between.

**Where runs ended**

| Ending | Games |
|---|---|
| Victory | 722 |
| Died at an Act 3 boss | 186 |
| Died in Act 2 | 58 |
| Died in Act 1 | 21 |
| Died in Act 3 before the bosses | 12 |
| Stalled (decision limit) | 1 |

The most common killers were the three Act 3 bosses, Aeonglass (73), Queen (65) and Test Subject (48), followed by the Act 2 bosses Kaiser Crab (14) and Knowledge Demon (12).

### How reliable is 72.2%?

1. **Sampling.** The 95% confidence interval of 69.3%–74.9% covers only the randomness of the 1,000 seeds.
2. **Selection.** This checkpoint was chosen for the repository partly because it did well in a comparison on these same seeds. A result picked that way is more likely to be a little high than a little low.
3. **Luck within a seed.** One different card play changes how the game's random numbers are used, and the rest of the run can turn out very differently, so the per-seed results say more about this checkpoint's games than about the seeds.

## Relation to the live stream

The Regent on the live stream, since 9 November 2026, uses a later model from the same training run, not this checkpoint. Its games are not in this repository.

## Reproducing the games

A game replays identically with the same seed, weights and engine build. These games use game logic v0.111.0; later game versions change some cards, monsters and events, so the same seeds do not give the same games there.
