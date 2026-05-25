from enum import Enum
import random
from typing import List, Optional

class Suit(Enum):
    COINS = "coins"
    CUPS = "cups"
    SWORDS = "swords"
    CLUBS = "clubs"

class Card:
    def __init__(self, suit: Suit, rank: int):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank} of {self.suit.value}"

    def __eq__(self, other):
        if not isinstance(other, Card): return False
        return self.rank == other.rank and self.suit == other.suit

class Deck:
    def __init__(self, ranks: List[int], suits: List[Suit]):
        self.cards = [Card(suit, rank) for suit in suits for rank in ranks]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, count: int = 1) -> List[Card]:
        drawn = self.cards[:count]
        self.cards = self.cards[count:]
        return drawn

    def __len__(self):
        return len(self.cards)

class Player:
    def __init__(self, name: str, is_human: bool = True):
        self.name = name
        self.is_human = is_human
        self.hand: List[Card] = []
        self.captured_cards: List[Card] = []
        self.score = 0
        self.team_id: Optional[int] = None

    def add_to_hand(self, cards: List[Card]):
        self.hand.extend(cards)

    def play_card(self, card: Card) -> Card:
        self.hand.remove(card)
        return card

    def capture(self, cards: List[Card]):
        self.captured_cards.extend(cards)

class GameState:
    def __init__(self):
        self.table: List[Card] = []
        self.players: List[Player] = []
        self.current_player_index = 0
        self.is_over = False

    @property
    def current_player(self) -> Player:
        return self.players[self.current_player_index]

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
