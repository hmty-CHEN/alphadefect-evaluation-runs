# The models

AlphaDefect is a project that trains reinforcement learning models to play *Slay the Spire 2*. It began with the Defect and now has one model per character: Defect, Regent, Silent and Fool. Each character's model was trained from scratch with reinforcement learning only: no human games, no imitation learning, no hand-written strategy, and no weights carried over from another character. A model plays every part of a run: map routing, card rewards, shops, events, rest sites and every combat turn.

This page covers what all evaluations in this repository have in common. Each evaluation's README says which checkpoint it used and how it relates to the model on the live stream.

## Architecture

All four characters use the same network design, with about 18 to 20 million parameters.

- **Input:** the game state as a set of records, one per visible object: cards in hand, in the draw, discard and exhaust piles and in the deck, enemies and their intents, powers, relics, potions, orbs, map nodes and the options on each screen.
- **Encoder:** a transformer reads all records together.
- **Action scoring:** the game engine lists every legal action. The network scores each one from the records it refers to (for example the card and its target) and the overall state. A softmax over the scores gives the probabilities shown in the transcripts.
- **Value estimates** are used only during training and may draw on information that is hidden during play, such as the true order of the draw pile. The policy never sees it, so every choice in these records uses only information a human player would have.

## Training

- PPO on many parallel copies of a headless game engine that runs *Slay the Spire 2*'s own game logic without graphics.
- Some engines play full runs; the others play single practice fights, with extra practice on the hardest ones.
- A checkpoint's version number counts the policy updates in that character's own training run. Version numbers are not comparable between characters.
- The checkpoints in this repository play with an exponential moving average of the training weights, except v103049, which uses the training weights directly.
- Training started on 25 October 2026 (Defect), 6 November (Regent), 9 November (Silent) and 13 November (Fool), on rented RTX 4090 and RTX 3090 machines.

## How it plays in these records

No search, no lookahead and no solver. At each decision the network runs one forward pass and the highest-probability option is played. It never reloads a save.

The live stream plays the real Steam game through a mod with the same kind of model. On the stream, some boss and elite fights also use a short search before the model commits to a move. None of the games in this repository use it.

## Checkpoints in this repository

| Evaluation | Character | Checkpoint | Weights | Game version |
|---|---|---|---|---|
| [v103049](../evaluations/v103049) | Defect | 103,049 | training weights | v0.111.0 |
| [v130051](../evaluations/v130051) | Defect | 130,051 | moving average | v0.111.0 |
| [regent-v53840](../evaluations/regent-v53840) | Regent | 53,840 | moving average | v0.111.0 |
| [silent-v26428](../evaluations/silent-v26428) | Silent | 26,428 | moving average | v0.111.0 |
| [fool-v23981](../evaluations/fool-v23981) | Fool | 23,981 | moving average | v0.113.0 |

The Fool was added to the game in v0.113.0, so its model trained and played on that version. The vocabulary in [`data/vocab.json`](../data/vocab.json) grew from 2,286 to 2,557 entries with that version; IDs are only ever appended, so the one file serves every evaluation.
