# Ronda Moroccan Card Game (روندا)

A high-performance, cross-platform digital implementation of the traditional Moroccan card game **Ronda**, built with Python and the Flet UI framework. This version supports single-player vs AI and local/network multiplayer with advanced team-based scoring, regional variations, and authentic Darija terminology.

---

## 🎴 Overview

**Ronda (روندا)** is one of Morocco’s most popular traditional card games, played with the 40‑card Spanish deck (Baraja Española). It is a game of memory, strategy, and timing, centered on capturing cards from the table with unique scoring rules and expressive Darija terms like “بواحد”, “بخمسة”, “بعشرة”, and “ميسا”.

### The Suits (الأنواع)
| Darija (Arabic script) | Transliteration | Spanish | English |
| :--- | :--- | :--- | :--- |
| **زراوط** | *Zrawoṭ* | Bastos | Clubs |
| **سيوفة** | *Syoufa* | Espadas | Swords |
| **زلافات** | *Zlafat* | Copas | Cups |
| **ذَهَب** | *Dhab* | Oros | Coins |

---

## 🕹️ Game Rules & Scoring

### Basic Setup
- **Deck**: 40 cards (1–7 and 10–12). Ranks 8 and 9 are excluded.
- **Objective**: Be the first to reach the target score (default 41).
- **Deal**: Each player receives 3 cards. 4 cards are placed face‑up on the table initially.

### How to Play
- Players alternate turns. Play one card to capture matching ranks on the table.
- **Consecutive Captures**: Matching a card rank also captures any consecutive sequence (e.g., matching a 5 also takes the 6, 7, 10, 11, 12 if they are on the table).

### ⭐ Special Cases (Darija Terms)
| Term (Darija) | Meaning | Effect |
| :--- | :--- | :--- |
| **بواحد (Bwahad)** | “By one” | Playing the same card as the opponent’s last move → +1 point. |
| **بخمسة (Bkhamsa)** | “By five” | Opponent responds with the same card again → +5 points. |
| **بعشرة (Bashara)** | “By ten” | If the first player has the fourth identical card → +10 points. |
| **ميسا (Maysa)** | “Clear” | Capturing all cards on the table in one move → +1 point. |
| **قعقة الري (9a3a Rey)** | “King’s knock” | Dealer wins +5 pts if the **last card played** is a 12. |
| **قعقة الآس (9a3a As)** | “Ace’s knock” | Opponent wins +5 pts if the **dealer’s last card** is a 1. |

---

## 🌟 Features

- **Game Modes**: 1v1 (2 Players) and 2v2 (4 Players Teams).
- **Dynamic AI**: Three levels: Easy, Medium, and Strategic Hard.
- **Regional Variation Support**:
  - Optional **Oros (Gold) Scoring**.
  - **9a3a As & 9a3a Rey** endgame bonuses.
  - Custom target scores.
- **Multiplayer**: Room-based syncing with real-time perspective shifts.
- **Visuals**: Real-time capture tallies and gold coin tracking.

---

## 🚀 Getting Started

### Installation
```bash
pip install flet
```

### Running the Game
**Desktop Mode**:
```bash
python ui/main.py
```
**Web/Browser Mode**:
```bash
flet run --web ui/main.py
```

---

## 🛠️ Technical Architecture
- `engine/`: Core Spanish deck primitives.
- `ronda/`: Authentic Moroccan game logic.
- `ui/`: Responsive Flet interface with PubSub networking.
- `ai/`: Heuristic strategies for realistic gameplay.

## 📜 License
Distributed under the MIT License.
