# v130051: 1,000 games, Defect, Ascension 10

Complete game records from a 1,000-game evaluation of **AlphaDefect v130051**, a later checkpoint of the same training run as [v103049](../v103049), 27,002 policy updates further on. For the model itself see [`docs/model.md`](../../docs/model.md).

The games were played in two batches with the same weights, then merged into one set: the 384 games of the routine evaluation that runs during training, and a follow-up batch with the other 616 seeds. Every decision of every game is here. For each one you can see what the model saw, which option it picked and how much probability it gave each alternative.

| Result | |
|---|---|
| Games | 1,000 (seeds RT0000–RT0999) |
| Wins | **709** |
| Win rate | **70.9%**, 95% confidence interval **68.0%–73.6%** (Wilson) |
| Batch 1: the 384 routine-evaluation seeds | 260 wins, 67.7% (95% CI 62.9%–72.2%) |
| Batch 2: the other 616 seeds | 449 wins, 72.9% (95% CI 69.3%–76.3%) |
| Average floor reached | 46.97 (a full run is 49 floors in most games) |
| Compared with v103049 on the same seeds | 56.1% → 70.9% ([details](#compared-with-other-checkpoints)) |

## Contents

| Path | What it is |
|---|---|
| [`transcripts/`](transcripts) | One plain-text file per game in readable English. **Start here.** |
| [`summary/runs.csv`](summary/runs.csv) | One row per game: result, how far it got, bosses faced, HP entering each boss, what killed it, and whether the seed is in batch 1 (`routine_eval_seed`). |
| [`summary/results.json`](summary/results.json) | The aggregate numbers on this page. |
| [`summary/runs.jsonl`](summary/runs.jsonl) | The evaluator's original per-game record (fights, choice counts, card offers and picks, route stats). |
| [`replays/`](replays) | Raw step-by-step replays (gzip-compressed JSON Lines), one per game. The transcripts are generated from these. |
| [`routine_eval_seeds.txt`](routine_eval_seeds.txt) | The 384 seeds of batch 1. |
| [`meta.json`](meta.json) | Model version, character, Ascension, game version and seed range. |

How to read them: [`docs/reading-records.md`](../../docs/reading-records.md). Field reference for the replays: [`docs/replay-format.md`](../../docs/replay-format.md). Unlike the v103049 replays, these also carry full relic feature rows (`relx`) and card attachment features (`cxa`).

## How the games were played

- Character Defect, Ascension 10, game logic v0.111.0, in the same headless engine used for training.
- Seeds RT0000 to RT0999. These are fixed test seeds. Training games use other seeds.
- Greedy policy: the highest-probability option is always played, with no search. The weights are an exponential moving average of the training weights (decay 0.998), which is what the routine evaluation uses.
- Played on 31 October 2026 on one RTX 3090, in two batches with identical weights and engine build:
  1. The 384 games of the routine evaluation (22:19–22:23 UTC). Its seeds are listed in `routine_eval_seeds.txt`.
  2. The remaining 616 seeds (22:27–22:43 UTC), played right after as a follow-up so that the checkpoint has a full 1,000-seed result.
- No game reached the decision limit.
- v130051 was not picked for its score. It was the newest checkpoint the routine evaluation had scored when the follow-up started, and its 67.7% on the routine seeds is below the neighbouring checkpoints (v129998: 72.1%, v130104: 71.4%).

## Results in detail

**How far runs got**

| Stage | Share of all games |
|---|---|
| Reached Act 2 | 97.2% |
| Reached Act 3 | 92.2% |
| Reached the first Act 3 boss | 90.5% |
| Beat the first Act 3 boss (of those who reached it) | 95.9% |
| Won (of those who reached the second Act 3 boss) | 81.7% |

Act 3 ends with two boss fights in a row, with no rest in between.

**Where runs ended**

| Ending | Games |
|---|---|
| Victory | 709 |
| Died at an Act 3 boss | 196 |
| Died in Act 2 | 50 |
| Died in Act 1 | 28 |
| Died in Act 3 before the bosses | 17 |
| Stalled (decision limit) | 0 |

The most common killers were the three Act 3 bosses, Aeonglass (80), Test Subject (60) and Queen (56), followed by the Act 2 boss Knowledge Demon (20).

### How reliable is 70.9%?

1. **Sampling.** The 95% confidence interval of 68.0%–73.6% covers only the randomness of the 1,000 seeds.
2. **Two batches.** Batch 1 scored 67.7% and batch 2 72.9%. With 384 and 616 games that gap is within chance (two-sided p ≈ 0.08). Because the checkpoint was not selected for its score, the 1,000-game figure needs no correction for selection, unlike [v103049](../v103049#how-reliable-is-561).
3. **Luck within a seed.** One different card play changes how the game's random numbers are used, and the rest of the run can turn out very differently, so the per-seed results here say more about this checkpoint's games than about the seeds.

### Compared with other checkpoints

All three evaluations use seeds RT0000–RT0999 and game version v0.111.0.

| Checkpoint | Wins | Win rate (95% CI) | Both won | Only the later one won | Only the earlier one won | Sign test (two-sided) |
|---|---|---|---|---|---|---|
| v103049 | 561 | 56.1% (53.0%–59.1%) | 462 | 247 | 99 | p < 0.001 |
| v129112 | 680 | 68.0% (65.0%–70.8%) | 544 | 165 | 136 | p = 0.11 |

The two right-hand columns count seeds, with v130051 as the later checkpoint. Only the v103049 records are in this repository; v129112 is listed for context.

Pairing by seed is approximate: one different card play changes everything after it, and the headless engine was rebuilt between the v103049 and v130051 evaluations. The first encounter is the same on all 1,000 seeds, but a rebuilt engine can differ in small details.

## Reproducing the games

A game replays identically with the same seed, weights and engine build. Shortly after these games were played (in the night between 31 October and 1 November 2026) the engine's handling of the start-up seed was changed to match the real game. Before that, the Act 1 content of roughly half of all seeds differed from the real game. Evaluations played with seeds RT0000–RT0999 after the change therefore use different games from this evaluation and from [v103049](../v103049) for about half of the seeds, and seed-by-seed comparisons across the change are less precise.
