# Raw replay format

Each file `replays/<seed>.jsonl.gz` is gzip-compressed [JSON Lines](https://jsonlines.org/):

- **Line 1** is the game header.
- **Every following line** is one decision, in the order the model made them. Decision `#N` in the transcripts is line `N + 2`.

Entities are written as integer **vocabulary IDs**. Look them up in `data/vocab.json`, where `vocab[id]` is

```json
{"id": 58, "key": "CARD.BALL_LIGHTNING", "name": "Ball Lightning", "tag": "Attack|Common", "cost": 1}
```

`key` is the game's internal identifier, prefixed with its category (`CARD.`, `RELIC.`, `POTION.`, `POWER.`, `MONSTER.`, `ORB.`, `ENCOUNTER.`, `ENCHANTMENT.`, `AFFLICTION.`, `EVENTOPT:`, `MOVE:`, `MAPNODE:`, `REST:`, `REWARD:`, `ALT:` …). `tag` is "type|rarity" for cards and the type for powers (`Buff` / `Debuff`). `cost` is the base energy cost of a card (`-1` for X-cost cards, `null` for anything else). ID 0 is padding and ID 1 is "unknown".

All numbers are raw game values, rounded to integers unless noted. **Acts are 0-based** (0 = Act 1) and **floors are 1-based** (1–49). Map rows and columns are 0-based.

## Header (line 1)

| Field | Meaning |
|---|---|
| `version` | Checkpoint version (103049) |
| `seed` | Game seed |
| `time` | Unix time the game finished |
| `win` | `true` if the run was won |
| `floor`, `act` | Where the run ended |
| `steps` | Number of decision lines that follow |
| `combats` | One entry per fight, recorded when the fight started: `room` (`Monster`, `Elite`, `Boss`), `encounter` (key without the `ENCOUNTER.` prefix), `act`, `floor`, `hp`, `max_hp`, `deck` (deck size), `relics`, `potions` (counts), `upgrades` (upgraded cards in deck) |

## Decision lines

Always present:

| Field | Meaning |
|---|---|
| `d` | Decision type: 1 combat, 2 card select, 3 card reward, 4 pick a pack, 5 rewards, 6 event, 7 rest site, 8 shop, 9 treasure, 10 Crystal Sphere (minigame), 11 map |
| `a` | Index into `c` of the option the model played |
| `pr` | The model's top options: `[[index into c, probability], ...]`, up to 5, only those with probability ≥ 0.005, highest first |
| `g` | Global state: `[act, floor, hp, max_hp, gold, energy, max_energy, turn, in_combat (0/1), room_type]`. Room type: 0 unassigned, 1 monster, 2 elite, 3 boss, 4 treasure, 5 shop, 6 event, 7 rest site, 8 map. Energy and turn are 0 outside combat |
| `c` | Every legal option (see [Options](#options-c)) |
| `rel` | Relics: `[[relic, counter], ...]`; counter is −1 for relics without one |
| `relx` | Relics with their full feature row: `[[relic, f0, …, f7], ...]` (counter, waxed, disabled, active, triggered this fight, melt order and similar flags) |
| `pot` | Potions: `[[potion, slot], ...]` |

Outside combat:

| Field | Meaning |
|---|---|
| `deck` | `[[card, upgrades], ...]` |

In combat:

| Field | Meaning |
|---|---|
| `pl` | The player: `hp`, `m` (max HP), `b` (block), `p` (powers `[[power, amount], ...]`), `pv` (the value each power shows in the game UI, aligned with `p`), `et` (end-of-turn forecast, below) |
| `en` | Enemies, one object each (below) |
| `orb`, `os` | Orbs `[[orb, passive value, evoke value], ...]`, first channeled first; `os` = number of orb slots |
| `orbx` | `[orb slots full, evoke value of the orb that would be pushed out, block from Loop, other value from Loop]` |
| `hand` | `[[card, upgrades, cost, playable, damage, block], ...]`. Cost is −1 for X-cost or unplayable cards. Damage and block are the values the card currently shows |
| `draw` | Number of cards in the draw pile |
| `drawl` | Draw pile contents `[[card, upgrades], ...]`, **sorted by ID, not in draw order**. The model never sees the real order |
| `disc`, `exh` | Discard and exhaust piles, `[[card, upgrades], ...]` |

`pl.et`, the player's end-of-turn forecast (one decimal):
`[block from Frost orbs, expected HP loss if the turn ended now, self-damage at end of turn, other end-of-turn block, expected HP loss if randomly targeted hits miss the attackers, number of enemies that can only be killed with lucky random targeting]`.

Each enemy in `en`:

| Field | Meaning |
|---|---|
| `n` | Monster ID |
| `s` | Position slot |
| `hp`, `m`, `b` | HP, max HP, block |
| `al` | 1 if alive |
| `p`, `pv` | Powers and their UI values, as for the player |
| `it` | Current intent: `[damage per hit, hits, [attack, buff, debuff, defend, heal/summon, stun/sleep/escape, other]]` (flags are 0/1) |
| `mv` | Move forecast `[[move, step, probability, damage per hit, hits], ...]`. Step 0 is the current move; later steps are derived from the monster's move rules and weights, never from the random number generator, up to three steps ahead |
| `et` | `[damage the orbs will deal it at end of turn, HP + block left after that, most damage you can still deal it this turn with current energy and hand, 1 if it can be killed this turn]` |

Present only when relevant:

| Field | When | Meaning |
|---|---|---|
| `cx` | A card is enchanted or afflicted | `[[zone, card, upgrades, enchantment, enchantment amount, affliction, affliction amount], ...]` |
| `cxa` | Same | Every attachment of each card with its feature row: `[[zone, card, upgrades, [[power, f0, …, f6], ...]], ...]` |
| `rt` | Map decisions, also kept on later lines | Route summary per reachable next node: `[[node type, rows left to the boss, rows to the nearest rest site, rows to the nearest shop (−1 if none), fewest elites before the next rest site, fewest fights], ...]` |
| `map` | Map decisions | The whole act map: `[[row, col, node type, visited, current position, reachable from here, child 1, child 2, child 3], ...]`. Children are the columns of connected nodes in the next row, **plus one** (0 = none) |
| `sel` | Card selection | `[purpose, min, max, already selected, source]`. Purpose: 0 transform, 1 exhaust, 2 remove, 3 enchant, 4 discard, 5 upgrade, 6 a prompt specific to the source card, −1 other. Source is the card, relic, potion or power that asked for the selection (0 if none) |
| `sp` | Crystal Sphere | `[revealed cells, digs left]` |
| `shop` | Shops | The whole shelf, including what the model cannot buy: `g` gold, `full` potion slots full, `it` `[[kind (0 card, 1 relic, 2 potion, 3 card removal), item, price, in stock, affordable, upgrades, removal already used], ...]` |

Zones used in `cx`, `cxa` and object descriptions: 1 player/ally, 2 enemy, 3 hand, 4 draw pile, 5 discard, 6 exhaust, 7 deck, 8 offered (rewards, shop, event), 9 being played, 10 and 11 pack 1 and 2, 12 upgrade preview.

## Options (`c`)

Each option is `[action, A, B, key, f0, f1, f2]`.

`A` and `B` are the objects the action refers to, or `null`. An object is `[record type, ID, zone, extra]`:

| Record type | Extra |
|---|---|
| 2 creature | Position slot |
| 4 card | Number of upgrades |
| 8 map node | `[row, col]` |
| 9 option (event, rest site, reward, shop service) | `[value, attached relic]`. When the option's own ID is 0 or 1 and an attached relic is present, the option is "take this relic", as on Neow's and other Ancients' screens. `value` is, for example, the gold amount of a gold reward |
| 5 relic, 6 potion, others | 0 |

| `action` | Meaning | A | B | Features |
|---|---|---|---|---|
| 1 | End turn | | | |
| 2 | Play a card | card in hand | target creature, if any | |
| 3 | Use a potion | potion | target, if any | |
| 4 | Discard a potion | potion | | |
| 5 | Select a card (one at a time) | card | upgraded preview of it, on upgrade screens | |
| 6 | Confirm the selection | | | |
| 7 | Take a card reward | card | | |
| 8 | Card reward alternative | | | `key` is the vocabulary ID: Skip, Reroll, Sacrifice |
| 9 | Pick a card pack | first card of the pack | | `f0` pack index |
| 10 | Take a reward | gold option, potion or relic | | |
| 11 | Leave / skip / proceed | | | |
| 12 | Event option | option | first card, relic or potion in the option's tooltip | |
| 13 | Rest site option | option | | |
| 14 | Buy | card, relic, potion or removal option | | `f0` price |
| 15 | Move on the map | map node | its route summary | |
| 16 | Take a treasure relic | relic | | |
| 17 | Skip the treasure relic | | | |
| 18 | Dig a Crystal Sphere cell | | | `f0` x, `f1` y, `f2` tool (0 small, 1 big) |

Multi-card selections are split into one decision per card followed by "confirm". Screens with only one possible outcome are resolved by the engine and do not appear as decisions.

## Replay lines versus the model's input

A replay line is a readable summary of the observation, not the exact network input. The network also received numeric features that are not all reproduced here, such as static card properties and extra route statistics. The `shop` shelf was recorded from additional engine information for review only. The policy never saw the true order of the draw pile or any upcoming random outcome.
