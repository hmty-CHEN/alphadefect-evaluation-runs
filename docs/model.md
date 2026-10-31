# The model

AlphaDefect is a reinforcement learning model that plays *Slay the Spire 2* as the Defect. It was trained from scratch with reinforcement learning only: no human games, no imitation learning and no hand-written strategy. It plays every part of a run: map routing, card rewards, shops, events, rest sites and every combat turn.

This page describes what is common to all evaluations in this repository. What differs between checkpoints is listed [at the end](#checkpoints-compared); each evaluation's own README links back here.

## Architecture

- **About 18.1 million parameters**, in a transformer that reads the game state as a set of entity records.
- **Input:** every visible object is one record: each card in hand, draw pile, discard pile and deck, each enemy and its intents, each power, relic, potion, orb, map node and event option. A record has a vocabulary ID embedding (about 2,300 game entities), type and zone embeddings, and a vector of numeric features such as HP, block, cost, damage or upgrades. A fixed "content prior" adds static properties of each card, relic, power and enchantment taken from the game data, so the model can relate entities it rarely sees. Draw, discard and exhaust piles, the deck and the relics are also pooled into five summary slots.
- **Encoder:** 6 pre-norm transformer layers, width 256, 4 attention heads, feed-forward width 1,024 (4.74M parameters).
- **Action scoring:** the game engine lists every legal action. Each action is scored by combining the encoded records it refers to (for example the card and its target) with the global state, using separate heads for combat and out-of-combat decisions. A softmax over the scores gives the probabilities shown in the transcripts.
- **Value heads:** separate combat and out-of-combat value heads are used only in training. They also receive privileged information such as the true order of the draw pile. The policy never sees it, so the choices in these records use only information a human player would have.
- **Where the parameters are:** about 10.5M are ID embedding tables (entity identity, upcoming and recent encounters, the act's bosses), 4.7M are the encoder, about 1.6M are the action and value heads, and the remaining 1.3M are feature projections and small helper networks.

## Training

- PPO with generalized advantage estimation, on parallel copies of a headless game engine. The engine runs *Slay the Spire 2*'s own game logic (public beta v0.111.0) without graphics.
- Some of the training engines play full runs. The others play single fights from a combat curriculum, including fights started from saved snapshots of boss fights, so the hardest combats get extra practice.
- Rewards are mainly the outcome of the run, with bonuses for each boss defeated and a small reward per floor. Practice fights also count HP lost.
- A checkpoint's version number is the number of policy updates made so far. Training started on 25 October 2026, on rented RTX 4090 and RTX 3090 machines.

## How it plays

No search, no lookahead, no solver. At each decision the network runs one forward pass and the highest-probability option is played (greedy). It does not reload saves. On the live stream it plays the real Steam game through a mod that reads the game state and carries out the chosen actions, and it receives no random-number information.

## Checkpoints compared

| | v103049 | v130051 |
|---|---|---|
| Parameters | 18,094,341 | 18,099,461 |
| Architecture | as above | as above, plus small input layers for observation formats 16–18 (5,120 parameters) |
| Observation format | 15 | 18 |
| Weights used for play | the training weights | an exponential moving average of the training weights (decay 0.998) |
| Share of training engines playing full runs | 50% | 75% |
| Game steps per policy update | 32,768 | 65,536 |
| Learning rate | 1.5e-4 | 1.1e-4 |
| Share of practice fights that are boss fights | 37% | 77% |

Observation formats 16–18 add a handful of inputs, mainly about shops and rewards (for example the price of the next card removal, the actual odds of a question-mark room, and card rewards that have not been claimed yet). The vocabulary grew from 2,284 to 2,286 entries; IDs are only ever appended, so [`data/vocab.json`](../data/vocab.json) serves every checkpoint.
