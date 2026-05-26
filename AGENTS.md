# Ronda Agent Instructions

## Codebase Structure
- `engine/`: Core card game logic (Card, Deck, Player).
- `ronda/`: Specific Ronda game rules and scoring.
- `ui/`: Flet-based user interface and multiplayer networking.
- `ai/`: AI strategies for Ronda.

## Modular Game Mechanics
The Ronda implementation supports several modular mechanics that can be toggled:
- **Target Score**: Default is 41, but can be 82, 164, or custom.
- **Oros Scoring**: If enabled, the face value of captured Gold cards is added to the team score at the end of the round.
- **Ace of Gold Bonus**: If enabled, capturing the Ace of Gold (1 of Coins) gives a +10 point bonus.
- **Missa Last Card**: By default, Missa (clearing the table) is not awarded on the very last card. This can be toggled.
- **Last Capture Wins Table**: If enabled, the last player to make a capture takes all remaining cards on the table at the end of the hand.

## Network Multiplayer
- Uses Flet's `pubsub` for room-based communication.
- Global `active_rooms` dictionary stores game state.
- The **Host** (Player index 1 in the lobby) is responsible for:
    - Initializing the `RondaGameState`.
    - Controlling AI moves in multiplayer rooms.
    - Broadcasting state updates.

## Coding Conventions
- Use `ft.Border.all` instead of `ft.border.all` (Flet v0.85+ compatibility).
- Assets must be referenced with leading slashes (e.g., `/cards/card_back.jpeg`) for web compatibility.
- Ensure `RondaGameState` remains serializable for future persistence improvements.
