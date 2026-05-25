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
python ui/main.py
```

## Assets

The game requires card images located in `assets/cards/`. Ensure these files are present before running the application.

## Troubleshooting

- **ModuleNotFoundError**: Ensure you are running the script from the project root and that your `PYTHONPATH` includes the current directory.
- **Flet Warnings**: You may see deprecation warnings from Flet; these are normal and do not affect gameplay.
