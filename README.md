# AlphaDefect evaluation runs

Complete game records from evaluations of **AlphaDefect**, a set of self-trained reinforcement learning models that play *Slay the Spire 2* at Ascension 10. The repository covers four characters: the Defect, the Regent, the Silent and the Fool.

Every decision of every game is here. For each one you can see what the model saw, which option it picked and how much probability it gave each alternative. Each character's model learned from scratch with reinforcement learning only: no human games, no imitation learning and no hand-written strategy. In these records the models do not search or look ahead; each decision is one forward pass of a neural network.

Each evaluation is one checkpoint playing 1,000 fixed test seeds with a greedy policy. Evaluations of the same character on the same seeds can be compared game by game. New evaluations are added as new folders under [`evaluations/`](evaluations).

## Evaluations

| Evaluation | Character | Game version | Seeds | Games | Wins | Win rate (95% CI) | Mean floor |
|---|---|---|---|---|---|---|---|
| [v103049](evaluations/v103049) | Defect | v0.111.0 | RT0000–RT0999 | 1,000 | 561 | 56.1% (53.0%–59.1%) | 45.96 |
| [v130051](evaluations/v130051) | Defect | v0.111.0 | RT0000–RT0999 | 1,000 | 709 | 70.9% (68.0%–73.6%) | 46.97 |
| [regent-v53840](evaluations/regent-v53840) | Regent | v0.111.0 | W1 | 1,000 | 722 | 72.2% (69.3%–74.9%) | 47.07 |
| [silent-v26428](evaluations/silent-v26428) | Silent | v0.111.0 | W1 | 1,000 | 712 | 71.2% (68.3%–73.9%) | 45.38 |
| [fool-v23981](evaluations/fool-v23981) | Fool | v0.113.0 | F25 | 1,000 | 592 | 59.2% (56.1%–62.2%) | 44.93 |

All games are at Ascension 10 in a headless engine that runs the game's own logic. The same table, as data, is in [`evaluations/index.csv`](evaluations/index.csv).

- **[v103049](evaluations/v103049)** (Defect): the checkpoint the AlphaDefect live stream used from 30 October 2026.
- **[v130051](evaluations/v130051)** (Defect): a later checkpoint of the same training run, 27,002 policy updates on.
- **[regent-v53840](evaluations/regent-v53840)** (Regent): a late checkpoint of the Regent's training run, three days after it started from scratch.
- **[silent-v26428](evaluations/silent-v26428)** (Silent): the checkpoint the live stream has used for the Silent since 12 November 2026.
- **[fool-v23981](evaluations/fool-v23981)** (Fool): a checkpoint from the fourth day of Fool training, on the game version that introduced the character. Its seeds were drawn fresh for this test.

Win rates are not directly comparable across characters. The characters differ in difficulty, the evaluations use different seed pools and game versions, and each model trained for a different length of time.

Read the "How reliable" section of each evaluation before quoting its win rate. Several of these checkpoints were chosen, at least in part, because they scored well, and each evaluation says how that affects its number.

## Repository layout

| Path | What it is |
|---|---|
| [`evaluations/<id>/`](evaluations) | One folder per evaluation. Defect folders are named after the checkpoint (`v130051` is the 130,051st policy update); the others start with the character's name. |
| `evaluations/<id>/README.md` | Results, how the games were played and how far to trust the numbers. |
| `evaluations/<id>/transcripts/` | One plain-text file per game in readable English. **Start here.** |
| `evaluations/<id>/summary/` | `runs.csv` (one row per game), `results.json` (aggregate numbers) and `runs.jsonl` (the evaluator's original per-game record). |
| `evaluations/<id>/replays/` | Raw step-by-step replays (gzip-compressed JSON Lines), one per game. The transcripts are generated from these. |
| `evaluations/<id>/meta.json` | Checkpoint version, character, Ascension, game version and seed pool. |
| `evaluations/<id>/seeds.txt`, `routine_eval_seeds.txt` | The seeds played, for evaluations with named seed pools; for the Defect, the 384 seeds shared with the routine evaluation that runs during training. |
| [`evaluations/index.csv`](evaluations/index.csv) | One row per evaluation. |
| [`docs/model.md`](docs/model.md) | An overview of the models and how they were trained, and which checkpoint each evaluation used. |
| [`docs/reading-records.md`](docs/reading-records.md) | How to pick games from the summary, read a transcript and use the raw replays. |
| [`docs/replay-format.md`](docs/replay-format.md) | Field-by-field reference for the raw replays. |
| [`data/vocab.json`](data/vocab.json) | Vocabulary shared by all evaluations: maps the numeric IDs in the replays to cards, relics, potions, monsters and so on, with English names. IDs are only appended, so older replays stay valid. |
| [`tools/`](tools) | Dependency-free Python 3 scripts that regenerate the transcripts, the summaries and the index. |

## Getting started

1. Open the `summary/runs.csv` of an evaluation, for example [`evaluations/regent-v53840/summary/runs.csv`](evaluations/regent-v53840/summary/runs.csv), filter for a loss to a boss you are curious about, and open the transcript named in its last column.
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

- The games come from a headless engine that runs the game's own logic. The live stream plays the real Steam game through a mod. On the stream, some boss and elite fights also use a short search before the model commits to a move; none of the games here do.
- Games replay identically only with the same seed, weights and engine build. For the Defect, the engine's handling of the start-up seed was changed to match the real game in the night between 31 October and 1 November 2026, so Defect evaluations played after that point use different games for about half of the RT seeds. The Defect evaluation READMEs say which side of the change they are on; the Regent, Silent and Fool evaluations were all played after it.
- Names come from the game's English localization, as of the game version in which each vocabulary entry was added. A few entries that a later game version renamed keep their earlier name. Internal keys that have no English name are shown as a tidied key (for example `Mock Combat Cleanup`).
- *Slay the Spire 2* and its cards, relics, monsters and names belong to Mega Crit. This repository contains only records of games played by the models, and no game files or art.
- The model weights are not included.
