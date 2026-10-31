# AlphaDefect evaluation runs

Complete game records from evaluations of **AlphaDefect**, a self-trained reinforcement learning model that plays *Slay the Spire 2* as the Defect on Ascension 10.

Every decision of every game is here. For each one you can see what the model saw, which option it picked and how much probability it gave each alternative. The model learned from scratch with reinforcement learning only: no human games, no imitation learning and no hand-written strategy. It does not search or look ahead; each decision is one forward pass of a neural network.

Each evaluation is one checkpoint played on the same fixed 1,000 seeds with a greedy policy, so checkpoints can be compared game by game. New evaluations are added as new folders under [`evaluations/`](evaluations).

## Evaluations

| Evaluation | Games | Wins | Win rate (95% CI) | Mean floor |
|---|---|---|---|---|
| [v103049](evaluations/v103049) | 1,000 | 561 | 56.1% (53.0%–59.1%) | 45.96 |
| [v130051](evaluations/v130051) | 1,000 | 709 | 70.9% (68.0%–73.6%) | 46.97 |

All evaluations so far use the Defect at Ascension 10, seeds RT0000–RT0999 and *Slay the Spire 2* game logic v0.111.0, in a headless engine. The same table, as data, is in [`evaluations/index.csv`](evaluations/index.csv).

- **[v103049](evaluations/v103049)**: the checkpoint the AlphaDefect live stream has used since 30 October 2026. 1,000 games in one batch.
- **[v130051](evaluations/v130051)**: a later checkpoint of the same training run, 27,002 policy updates on. 1,000 games played in two batches (the 384 games of the routine evaluation, plus the other 616 seeds), merged into one set. On the same seeds it won on 247 seeds that v103049 lost and lost on 99 that v103049 won.

Read the "How reliable" section of each evaluation before quoting its win rate. A checkpoint that was picked because it scored well on a subset of the seeds carries some of that luck into its full result, and each evaluation says how to correct for it.

## Repository layout

| Path | What it is |
|---|---|
| [`evaluations/<id>/`](evaluations) | One folder per evaluation, named after the checkpoint (`v130051` is the 130,051st policy update). |
| `evaluations/<id>/README.md` | Results, how the games were played and how far to trust the numbers. |
| `evaluations/<id>/transcripts/` | One plain-text file per game in readable English. **Start here.** |
| `evaluations/<id>/summary/` | `runs.csv` (one row per game), `results.json` (aggregate numbers) and `runs.jsonl` (the evaluator's original per-game record). |
| `evaluations/<id>/replays/` | Raw step-by-step replays (gzip-compressed JSON Lines), one per game. The transcripts are generated from these. |
| `evaluations/<id>/routine_eval_seeds.txt`, `meta.json` | The 384 seeds shared with the routine evaluation that runs during training; model version, character, Ascension and game version. |
| [`evaluations/index.csv`](evaluations/index.csv) | One row per evaluation. |
| [`docs/model.md`](docs/model.md) | The model's architecture and training, and how the checkpoints differ. |
| [`docs/reading-records.md`](docs/reading-records.md) | How to pick games from the summary, read a transcript and use the raw replays. |
| [`docs/replay-format.md`](docs/replay-format.md) | Field-by-field reference for the raw replays. |
| [`data/vocab.json`](data/vocab.json) | Vocabulary shared by all evaluations: maps the numeric IDs in the replays to cards, relics, potions, monsters and so on, with English names. IDs are only appended, so older replays stay valid. |
| [`tools/`](tools) | Dependency-free Python 3 scripts that regenerate the transcripts, the summaries and the index. |

## Getting started

1. Open [`evaluations/v130051/summary/runs.csv`](evaluations/v130051/summary/runs.csv), filter for a loss to a boss you are curious about, and open the transcript named in its last column.
2. Read the transcript floor by floor. Every decision shows the probability the model gave its choice and the runners-up. [`docs/reading-records.md`](docs/reading-records.md) explains the notation.
3. For the exact game state before any decision, load the raw replay. A few lines of Python do it:

```python
import gzip, json
vocab = json.load(open("data/vocab.json"))
name = lambda i: vocab[i]["name"]

with gzip.open("evaluations/v130051/replays/RT0000.jsonl.gz", "rt") as f:
    head = json.loads(f.readline())
    steps = [json.loads(line) for line in f]

print(head["version"], head["win"], head["floor"], len(steps))
print([name(card) for card, *_ in steps[2]["hand"]])   # the hand at decision #2
```

## Notes

- The games come from a headless engine that runs the game's own logic. The live stream plays the real Steam game through a mod, with the same model and the same greedy policy.
- Games replay identically only with the same seed, weights and engine build. The engine's handling of the start-up seed was changed to match the real game in the night between 31 October and 1 November 2026, so evaluations played after that point use different games for about half of the seeds, even under the same seed names. Each evaluation README states which side of the change it is on.
- Names come from the game's English localization. Internal keys that have no English name are shown as a tidied key (for example `Mock Combat Cleanup`).
- *Slay the Spire 2* and its cards, relics, monsters and names belong to Mega Crit. This repository contains only records of games played by the model, and no game files or art.
- The model weights are not included.
