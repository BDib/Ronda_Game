# Testing Ronda

This document outlines the testing strategy and instructions for the Ronda card game.

## Overview

The Ronda codebase is tested using Python's built-in `unittest` framework. Tests are divided into several categories:
- **Core Logic**: Testing the deck, cards, and player management.
- **Game Rules**: Verifying the specific rules of Ronda (Bwahad, Missa, 9a3a, etc.).
- **Team Mode**: Ensuring partnership scoring and turn alternation work correctly.
- **Multiplayer Logic**: Validating room management and state serialization.

## Running Tests

To run all tests, execute the following command from the root directory:

```bash
python3 -m unittest discover tests
```

To run a specific test file:

```bash
python3 -m unittest tests/test_ronda_rules.py
```

## Test Suites

### 1. `tests/test_ronda_rules.py`
Focuses on the 1v1 game mechanics:
- **Bwahad (Bount)**: Points for matching the previous card.
- **Bkhamsa/Bashara**: Response points (+5, +10).
- **Maysa (Missa)**: Table clearing bonus.
- **Consecutive Captures**: Validating that playing a card captures all sequential ranks on the table.
- **End Round Scoring**: Card counting and Oros (Gold) bonuses.

### 2. `tests/test_ronda_team_rules.py`
Focuses on the 2v2 partnership mechanics:
- **Turn Alternation**: Ensuring the sequence is Team A -> Team B -> Team A -> Team B.
- **Shared Scoring**: Verifying that points earned by one player are correctly attributed to the team total.
- **9a3a (Endgame Knocks)**: Testing the King/Ace bonuses in a team context.

### 3. `tests/test_multiplayer.py`
*(Coming Soon)* Focuses on networking and room management:
- Room creation and ID generation.
- Player joining and slot occupancy.
- Serialization of game state for PubSub broadcasting.

## Continuous Integration

It is recommended to run the full test suite before submitting any pull requests to ensure no regressions are introduced in the core scoring logic.
