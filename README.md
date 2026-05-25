# Ronda Moroccan Card Game

A digital implementation of the traditional Moroccan card game **Ronda**, built with Python and the Flet UI framework.

## Overview

Ronda is a popular trick-taking card game from Morocco, played with a 40-card Spanish deck. This project brings the game to your desktop with a single-player mode against a challenging AI.

## Features

- **Classic Rules**: Accurate implementation of Ronda rules, including matches and announcements.
- **AI Opponent**: Play against a CPU with strategic move selection.
- **Visual Feedback**: Real-time updates for game events like Bount, Inza, and Missa.
- **Cross-Platform UI**: Modern interface powered by Flet.

## How to Play

### Setup
- The game uses a 40-card Spanish deck (ranks 1-7 and 10-12).
- Each player is dealt 3 cards per hand.
- 4 cards are placed on the table at the start of each round.

### Objective
Capture as many cards as possible by matching ranks on the table. Capturing sequences of cards is also possible (e.g., matching a 3 on the table allows you to also capture a 4, 5, etc., if they are present in sequence).

### Scoring
- **Bount (Match)**: Matching a card played by the previous player (1 point).
- **Inza (Triple Match)**: Matching a card that was already matched once (5 points).
- **Ghader (Quad Match)**: Matching a card for the fourth time (10 points).
- **Missa**: Clearing the entire table (1 point).
- **Announcements**:
  - **Ronda**: Two cards of the same rank (1 point).
  - **Tringla**: Three cards of the same rank (5 points).
- **End of Round**: Players receive 1 point for every card captured beyond 20.

## Installation and Usage

See [BUILD.md](BUILD.md) for detailed instructions on setting up the environment and running the game.

## Testing

Run tests located in the `tests/` directory to verify game logic:
```bash
python3 -m unittest discover tests
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
