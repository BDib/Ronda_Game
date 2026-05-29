# Contributing to Ronda

Thank you for your interest in contributing to the Ronda card game! This project aims to provide the most authentic Moroccan card game experience.

## Code of Conduct

Please be respectful and inclusive in all interactions. We aim to celebrate Moroccan culture through this project.

## How to Contribute

### 1. Reporting Bugs
- Use the GitHub Issue tracker.
- Provide a clear description of the bug and steps to reproduce it.
- Include information about your environment (OS, Python version, Flet version).

### 2. Suggesting Features
- We welcome suggestions for new game modes (e.g., 3-player Ronda) or other Spanish-deck games (Brisca, Tute).
- Open an issue to discuss the feature before starting implementation.

### 3. Submitting Changes
- Create a new branch for your feature or fix.
- Ensure all tests pass by running `python3 -m unittest discover tests`.
- Add new tests for any new logic or rules.
- Follow the existing code style (see below).
- Update documentation if necessary.

## Development Setup

1. Clone the repository.
2. Install dependencies: `pip install flet`.
3. Run the game locally: `python3 ui/main.py`.

## Coding Standards

- **Terminology**: Use Darija terms in the UI (Bwahad, Bkhamsa, Bashara, Maysa).
- **Modularity**: Keep game logic in `ronda/` and UI logic in `ui/`.
- **Serialization**: Ensure any changes to `Player` or `Card` objects are reflected in `serialize_state()` for multiplayer compatibility.
- **Formatting**: Use standard PEP 8 guidelines.

## Regional Variations

Ronda has many regional rules. If you add a new rule:
- Make it toggleable in the `RondaGameState` constructor.
- Add a corresponding switch in the `ui/main.py` lobby.
- Document the rule in `README.md`.
