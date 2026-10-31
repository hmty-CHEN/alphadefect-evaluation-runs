# How to read the records

Every evaluation folder under [`evaluations/`](../evaluations) has the same three layers, from the most readable to the most complete:

1. `summary/`: one row per game, for choosing which games to look at.
2. `transcripts/`: one plain-text file per game, written for people.
3. `replays/`: the raw, step-by-step data the other two are generated from.

The examples below use `evaluations/v130051`; every other evaluation works the same way.

## 1. Pick games from the summary

Open `summary/runs.csv` (GitHub shows it as a searchable table) and filter by what interests you, such as losses to a given boss or wins that went into the last fight at low HP. The `transcript` column gives the path of the game's transcript.

| Column | Meaning |
|---|---|
| `seed` | Game seed; also the file name in `transcripts/` and `replays/` |
| `result`, `ending` | `win`/`loss`; `victory`, `died_act1`, `died_act2`, `died_act3_other`, `died_act3_boss` or `stalled` |
| `act`, `floor` | Act (1–3) and floor where the game ended (a full run is 49 floors in most games; a few end on floor 50 or 51) |
| `decisions` | Number of decisions the model made |
| `routine_eval_seed` | `yes` if the seed belongs to the 384 seeds of the routine evaluation that runs during training (see the evaluation's README for why that matters) |
| `combats`, `elites` | Fights played, and how many of them were elites |
| `act1_boss` … `act3_boss2` | The boss fought at each point, if reached |
| `…_hp_in` | HP / max HP when that boss fight started |
| `lost_to` | The fight the model died in |
| `final_deck_size`, `final_relics` | Deck size and relic count at the last decision outside combat |
| `transcript` | Path of the transcript, from the repository root |

`summary/results.json` holds the aggregate numbers, and `summary/runs.jsonl` the evaluator's original per-game record (fights, choice counts, card offers and picks, route statistics).

## 2. Read a transcript

Each transcript tells the game floor by floor. Here is the start of the first fight in `evaluations/v103049/transcripts/RT0000.txt`:

```
=== Act 1 - Floor 2 - Monster: Seapunk ===   HP 60/75  Gold 99
  -- Turn 1 --
     HP 60/75  Block 0  Energy 3/3  Orbs (3 slots): Lightning
     Enemy Seapunk: HP 49/49  Intent Sea Kick: Attack 13
     Hand: Strike [1], Defend [1], Strike [1], Defend [1], Ascender's Bane [-]  | Draw 6  Discard 0  Exhaust 0
     #2    Play Defend   [49.8%, 5 options]
            also: Play Defend 49.8% (identical option)
     #3    Play Defend   [100.0%, 4 options]
     #4    Play Strike -> Seapunk   [49.8%, 3 options]
            also: Play Strike -> Seapunk 49.8% (identical option)
     #5    End turn   [100.0%, 1 option]
  #16   [Rewards] Take reward: Card reward   [99.8%, 2 options]
  #17   [Card reward] Take Go for the Eyes   [91.4%, 4 options]
         also: Skip 3.3%; Take Feral 2.8%; Take Smokestack 2.5%
  Deck change: +Go for the Eyes  (12 cards)
```

- `=== … ===` starts a floor: act, floor, room (with the encounter name for fights), and HP and gold on arrival.
- `-- Turn N --` starts a combat turn and shows the state the model saw: your HP, block, energy, orbs and powers, each enemy's HP, block, intent and powers, the hand with card costs in brackets (`-` means unplayable, `X` an X-cost card), the pile sizes, and the potions.
- `#N` is a decision. `N` counts from 0 and matches line `N + 2` of the decompressed raw replay, since line 1 is the game header. Then come the chosen action, its probability, and how many legal options there were. Outside combat the decision type is shown in brackets, such as `[Map]`, `[Shop]` or `[Event]`.
- `also:` lists the other options with at least 0.5% probability. When two cards in hand are identical, each copy is a separate option and the probability is split between them. Those are marked `(identical option)` or `xN`, so a 49.8% / 49.8% split means the model was certain, not torn.
- Between decisions, `Deck change`, `Relic gained` and `Relic lost` report what changed. Shops print their whole shelf, card-selection screens their purpose (upgrade, remove, transform…), and the file ends with the final deck and relics.

Turn states are printed once, at the start of each turn. To see the exact state before any single decision, use the raw replay.

The probability tells you how sure the model was. Near 100% means a settled choice. A low value on a screen with few options, say 40% among 3, means the model was close to undecided and a small change in the position could have flipped it. Crystal Sphere screens offer close to 200 options, so probabilities of about 1% are normal there.

## 3. Use the raw replays

Each file in `replays/` is gzip-compressed JSON Lines: one header line summarizing the game, then one line per decision with the full observation in compact form, using vocabulary IDs instead of names. It contains more than the transcript: the state before every decision, enemy move forecasts, the full map, route summaries for every reachable map node, enchantments, pile contents and the full list of candidate actions. See [`replay-format.md`](replay-format.md) for every field.

```python
import gzip, json
vocab = json.load(open("data/vocab.json"))
name = lambda i: vocab[i]["name"]

with gzip.open("evaluations/v130051/replays/RT0000.jsonl.gz", "rt") as f:
    head = json.loads(f.readline())
    steps = [json.loads(line) for line in f]

print(head["version"], head["win"], head["floor"], len(steps))
s = steps[2]
print([name(card) for card, *_ in s["hand"]])     # the hand at decision #2
print(s["pr"])                                   # [[option index, probability], ...]
```

`data/vocab.json` is shared by all evaluations: vocabulary IDs are only ever appended, so an older replay reads correctly with the newest file.

## Regenerating the derived files

Python 3.9+, standard library only. Run from the repository root:

```bash
python3 tools/transcript.py evaluations/v130051/replays/RT0000.jsonl.gz     # print one game
python3 tools/transcript.py --all evaluations/v130051/replays evaluations/v130051/transcripts
python3 tools/build_summary.py evaluations/v130051                          # summary/runs.csv and results.json
python3 tools/build_index.py                                                # evaluations/index.csv
```
