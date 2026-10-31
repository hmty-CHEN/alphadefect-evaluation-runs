# AlphaDefect v103049: 1,000 evaluation runs

Complete game records from a 1,000-game evaluation of **AlphaDefect v103049**, a self-trained reinforcement learning model that plays *Slay the Spire 2* as the Defect on Ascension 10. This is the checkpoint the AlphaDefect live stream has used since 30 October 2026.

Every decision of every game is here. For each one you can see what the model saw, which option it picked and how much probability it gave each alternative.

| Result | |
|---|---|
| Games | 1,000 (seeds RT0000–RT0999) |
| Wins | **561** |
| Win rate | **56.1%**, 95% confidence interval **53.0%–59.1%** (Wilson) |
| Win rate on the 616 seeds not used to select this checkpoint | 54.2%, 95% CI 50.3%–58.1% ([why this matters](#how-reliable-is-561)) |
| Average floor reached | 45.96 (a full run is 49 floors) |

## Contents

| Path | What it is |
|---|---|
| [`transcripts/`](transcripts) | One plain-text file per game in readable English. **Start here.** |
| [`summary/runs.csv`](summary/runs.csv) | One row per game: result, how far it got, bosses faced, HP entering each boss, what killed it. |
| [`summary/results.json`](summary/results.json) | The aggregate numbers on this page. |
| [`summary/runs.jsonl`](summary/runs.jsonl) | The evaluator's original per-game record (fights, choice counts, card offers and picks, route stats). |
| [`replays/`](replays) | Raw step-by-step replays (gzip-compressed JSON Lines), one per game. The transcripts are generated from these. |
| [`data/vocab.json`](data/vocab.json) | Vocabulary: maps the numeric IDs in the replays to cards, relics, potions, monsters and so on, with English names. |
| [`data/eval_subset_seeds.txt`](data/eval_subset_seeds.txt) | The 384 seeds shared with the routine evaluation that selected this checkpoint. |
| [`docs/replay-format.md`](docs/replay-format.md) | Field-by-field reference for the raw replays. |
| [`tools/`](tools) | Two dependency-free Python 3 scripts that regenerate the transcripts and the summary. |

## The model

AlphaDefect was trained from scratch with reinforcement learning only: no human games, no imitation learning and no hand-written strategy. It plays every part of a run: map routing, card rewards, shops, events, rest sites and every combat turn.

**Size and architecture**

- **18,094,341 parameters**, in a transformer that reads the game state as a set of entity records.
- **Input:** every visible object is one record: each card in hand, draw pile, discard pile and deck, each enemy and its intents, each power, relic, potion, orb, map node and event option. A record has a vocabulary ID embedding (2,284 game entities), type and zone embeddings, and a vector of numeric features such as HP, block, cost, damage or upgrades. A fixed "content prior" adds static properties of each card, relic, power and enchantment taken from the game data, so the model can relate entities it rarely sees. Draw, discard and exhaust piles, the deck and the relics are also pooled into five summary slots.
- **Encoder:** 6 pre-norm transformer layers, width 256, 4 attention heads, feed-forward width 1,024 (4.74M parameters).
- **Action scoring:** the game engine lists every legal action. Each action is scored by combining the encoded records it refers to (for example the card and its target) with the global state, using separate heads for combat and out-of-combat decisions. A softmax over the scores gives the probabilities shown in the transcripts.
- **Value heads:** separate combat and out-of-combat value heads are used only in training. They also receive privileged information such as the true order of the draw pile. The policy never sees it, so the choices in these records use only information a human player would have.
- **Where the parameters are:** about 10.5M are ID embedding tables (entity identity, upcoming and recent encounters, the act's bosses), 4.7M are the encoder, about 1.6M are the action and value heads, and the remaining 1.3M are feature projections and small helper networks.

**Training**

- PPO with generalized advantage estimation, on parallel copies of a headless game engine. The engine runs *Slay the Spire 2*'s own game logic (public beta v0.111.0) without graphics.
- Half of the training engines play full runs. The other half play single fights from a combat curriculum, including fights started from saved snapshots of boss fights, so the hardest combats get extra practice.
- Rewards are mainly the outcome of the run, with bonuses for each boss defeated and a small reward per floor. Practice fights also count HP lost.
- v103049 means the 103,049th policy update. Training started on 25 October 2026 and reached this checkpoint on 30 October, on rented RTX 4090 and RTX 3090 machines.

**How it plays**

No search, no lookahead, no solver. At each decision the network runs one forward pass and the highest-probability option is played (greedy). It does not reload saves. On the live stream it plays the real Steam game through a mod that reads the game state and carries out the chosen actions, and it receives no random-number information.

## How the games were played

- Character Defect, Ascension 10, game logic v0.111.0, in the same headless engine used for training.
- Seeds RT0000 to RT0999. These are fixed test seeds. Training games use other seeds.
- Greedy policy, exactly as on stream. With the same seed and weights a game always plays out identically, so every game here can be reproduced.
- Played on 30 October 2026 on one RTX 3090.
- One game (RT0876) reached the 6,000-decision limit in an endless Act 3 fight, where the model kept ending its turn with no cards left and neither side could win. It is counted as a loss.

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

1. **Selection.** During training a routine evaluation plays 384 seeds that are a subset of RT0000–RT0999 (listed in `data/eval_subset_seeds.txt`). v103049 was chosen for this 1,000-game test because it scored 59.1% on those 384 seeds, one of the highest results of any checkpoint. The games on those seeds are identical in both tests, so part of that luck is carried into the 56.1% here. On the other **616 seeds** the model won **54.2% (95% CI 50.3%–58.1%)**, the least biased estimate of its strength.
2. **Luck within a seed.** One different card play changes how the game's random numbers are used, and the rest of the run can turn out very differently. The same seed is not equally hard for every checkpoint, so the per-seed results here say more about this checkpoint's games than about the seeds.

For comparison, on the same 1,000 seeds the previous live-stream checkpoint, v89500, won 49.9% (95% CI 46.8%–53.0%). Comparing seed by seed, only v103049 won on 222 seeds and only v89500 won on 160 (two-sided sign test p = 0.002).

## How to read the records

### 1. Pick games from the summary

Open [`summary/runs.csv`](summary/runs.csv) (GitHub shows it as a searchable table) and filter by what interests you, such as losses to a given boss or wins that went into the last fight at low HP. The `transcript` column links to the game.

| Column | Meaning |
|---|---|
| `seed` | Game seed; also the file name in `transcripts/` and `replays/` |
| `result`, `ending` | `win`/`loss`; `victory`, `died_act1`, `died_act2`, `died_act3_other`, `died_act3_boss` or `stalled` |
| `act`, `floor` | Act (1–3) and floor (1–49) where the game ended |
| `decisions` | Number of decisions the model made |
| `combats`, `elites` | Fights played, and how many of them were elites |
| `act1_boss` … `act3_boss2` | The boss fought at each point, if reached |
| `…_hp_in` | HP / max HP when that boss fight started |
| `lost_to` | The fight the model died in |
| `final_deck_size`, `final_relics` | Deck size and relic count at the last decision outside combat |

### 2. Read a transcript

Each transcript tells the game floor by floor. Here is the start of the first fight in `transcripts/RT0000.txt`:

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

### 3. Use the raw replays

Each file in `replays/` is gzip-compressed JSON Lines: one header line summarizing the game, then one line per decision with the full observation in compact form, using vocabulary IDs instead of names. It contains more than the transcript: the state before every decision, enemy move forecasts, the full map, route summaries for every reachable map node, enchantments, pile contents and the full list of candidate actions. See [`docs/replay-format.md`](docs/replay-format.md).

```python
import gzip, json
vocab = json.load(open("data/vocab.json"))
name = lambda i: vocab[i]["name"]

with gzip.open("replays/RT0000.jsonl.gz", "rt") as f:
    head = json.loads(f.readline())
    steps = [json.loads(line) for line in f]

print(head["win"], head["floor"], len(steps))
s = steps[2]
print([name(card) for card, *_ in s["hand"]])     # the hand at decision #2
print(s["pr"])                                   # [[option index, probability], ...]
```

To regenerate the transcripts or the summary (Python 3.9+, standard library only):

```bash
python3 tools/transcript.py replays/RT0000.jsonl.gz          # print one game
python3 tools/transcript.py --all replays transcripts        # rewrite all transcripts
python3 tools/build_summary.py                               # rewrite summary/runs.csv and results.json
```

## Notes

- Names come from the game's English localization. Internal keys that have no English name are shown as a tidied key (for example `Mock Combat Cleanup`).
- *Slay the Spire 2* and its cards, relics, monsters and names belong to Mega Crit. This repository contains only records of games played by the model, and no game files or art.
- The model weights are not included.
