# Ronda Moroccan Card Game

A digital implementation of the traditional Moroccan card game **Ronda**, built with Python and the Flet UI framework.

## Overview

Ronda is a popular card game from Morocco, played with a 40-card Spanish deck. This project features both 1v1 and 2v2 team-based modes with an adaptable AI.

## Features

- **Multi-Player Support**: Play 1v1 or 2v2 with AI teammates and opponents.
- **Dynamic AI Difficulty**: Choose between Easy, Medium, and Hard strategies.
- **Team-Based Scoring**: In 4-player mode, scores and captured cards are pooled for teams.
- **Modular Game Engine**: Designed to be extensible for other Spanish-deck games like Brisca, Mus, or Escoba.
- **Community Inspired**: Refined with UX insights from popular Ronda community projects.

---

## 📖 How to Play Ronda

### The Deck
Ronda uses the 40-card **Spanish deck** (Baraja Española). It has 4 suits (Coins, Cups, Swords, Clubs) with ranks 1–7 and 10–12. Ranks 8 and 9 are not used.

### The Objective
The goal is to score **41 points** first. Points are earned during the round through announcements and special matches, and at the end of the round by counting captured cards.

### Dealing & Start
1.  **Initial Table**: 4 cards are placed face-up on the table (no pairs allowed initially).
2.  **Hand**: Each player is dealt **3 cards**. Once everyone plays their 3 cards, another 3 are dealt until the deck is empty.
3.  **Teams**: In 4-player mode, you and the player opposite you form a team.

### Gameplay Tutorial
1.  **Matching**: On your turn, play one card. If its rank matches any card on the table, you **capture** both.
2.  **Sequences**: If you make a match, you also capture any cards on the table that follow the matched rank in numerical order (e.g., matching a 5 also takes the 6 and 7 if they are on the table).
3.  **Discarding**: If your card doesn't match anything, it stays on the table for others to capture.
4.  **Missa**: If you capture all cards from the table, you score 1 point.

### Special Scoring Events
*   **Bount (+1 pt)**: Match the card that the player *immediately before you* just played.
*   **Inza (+5 pts)**: If you match a card that was just used for a Bount (i.e., three of the same rank played in a row).
*   **Ghader (+10 pts)**: If all four cards of the same rank are played consecutively.

### Announcements (At Deal)
When you receive your 3 cards, the game checks for:
*   **Ronda (+1 pt)**: A pair in your hand.
*   **Tringla (+5 pts)**: Three-of-a-kind in your hand.
*   *Note: Only the player/team with the highest-ranking announcement scores the total points of all announcements made in that deal.*

### End of Round
Once the deck is empty and all cards are played:
1.  The last person to make a capture takes any remaining cards on the table.
2.  Count your captured cards. Every card **beyond 20** scores 1 point (e.g., 25 cards = 5 points).
3.  In teams, combine your cards (Team total > 20).

---

## 🏗️ Technical Architecture

This project is built on a modular engine (`engine/core.py`) that can be adapted for other Mediterranean card games:
*   **Brisca / Briscola**: Update `logic.py` for trick-taking and trump suit logic.
*   **Mus**: Add betting phases and specific hand-ranking logic.
*   **Escoba**: Modify capture logic to sum to 15.
*   **Tute / Chinchón**: Implement melding and specific scoring declarations.

The UI is built with **Flet (Flutter for Python)**, providing a responsive and hardware-accelerated experience.

---

## 🚀 Getting Started

See [BUILD.md](BUILD.md) for installation and running instructions.

## 🤝 Acknowledgments
Inspired by the work of the Moroccan developer community, specifically:
*   [ozennou/Ronda-dev](https://github.com/ozennou/Ronda-dev)
*   [Dahercode/ronda](https://github.com/Dahercode/ronda)
*   [Callmevbdu/Ronda-moroccan_game](https://github.com/Callmevbdu/Ronda-moroccan_game)

## License
MIT License - see [LICENSE](LICENSE) for details.
