# Building and Running Ronda

## Prerequisites

- Python 3.9 or higher
- [pip](https://pip.pypa.io/en/stable/installation/)

## Installation

1. Clone the repository (if applicable) or navigate to the project directory.
2. Install the required dependencies:
   ```bash
   pip install flet
   ```

## Running the Game

To start the game, run the following command from the root directory:
```bash
python3 ui/main.py
```

## Features for Testers

- **2-Player Mode**: Standard 1v1 against a single AI.
- **4-Player Mode**: 2v2 team-based play. Your partner is the AI at the top of the screen.
- **Difficulty Selection**: Easy (Random), Medium (Basic Captures), Hard (Strategic Bount/Missa hunting).

## Assets

The game requires card images located in `assets/cards/`. Ensure these files are present before running the application.

## Manual Testing Instructions

1.  Launch the game.
2.  Choose **4 Players** on the setup screen.
3.  Choose **Hard** difficulty.
4.  Verify that:
    - Players are positioned at Top, Bottom, Left, and Right.
    - Capturing a card played by the opponent to your left triggers a "BOUNT!".
    - Score increases for both you and your partner simultaneously.
    - At the end of the round, the combined cards from you and your partner contribute to the team score.

## Troubleshooting

- **ModuleNotFoundError**: Ensure you are running the script from the project root.
- **Flet Warnings**: You may see deprecation warnings from Flet; these are normal and do not affect gameplay.
