# Ronda Moroccan Card Game

A full-featured digital implementation of the traditional Moroccan card game **Ronda**, built with Python and Flet.

## Features
- **2-Player (1v1)** and **4-Player (2v2)** modes.
- **Advanced Scoring Rules**: Bount, Inza, Ghader, and Missa.
- **Customizable Mechanics**:
    - Selectable target scores (41, 82, 164, or Custom).
    - Optional **Oros (Gold) Scoring**: Capture gold cards to add their values to your score.
    - **Ace of Gold Bonus**: Get +10 points for capturing the 1 of Coins.
    - Toggleable Missa rules and last-capture table sweep.
- **Multiplayer (Beta)**:
    - Host and join rooms with a 6-digit code.
    - Lobby system with an adjustable AI timer.
    - Host-driven AI to fill empty slots.
- **AI Opponents**: Easy, Medium, and Hard difficulties.

## How to Run
1. Install dependencies: `pip install flet`
2. Run the game: `python ui/main.py`

## Rules of Ronda
- **Goal**: Reach the target score (default 41) before your opponents.
- **Dealing**: Each player receives 3 cards. 4 cards are placed on the table initially.
- **Capturing**:
    - Match a card rank on the table to capture it.
    - You also capture consecutive cards (e.g., if you match a 5, you also take 6, 7, 10, 11, 12 if they are on the table).
- **Special Scores**:
    - **Ronda/Tringla**: Announcements made when receiving a pair or three-of-a-kind.
    - **Bount/Inza/Ghader**: Awarded when you match a card rank that the previous player just played.
    - **Missa**: Awarded for clearing all cards from the table.
- **Teams**: In 4-player mode, players sitting opposite each other are partners and share a score.

## Development
- `ronda/logic.py`: Core game engine.
- `ui/main.py`: Flet UI and Multiplayer sync.
- `ai/strategies.py`: AI move selection.
