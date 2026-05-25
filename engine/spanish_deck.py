from engine.core import Deck, Suit

class SpanishDeck(Deck):
    def __init__(self, include_8_9: bool = False):
        ranks = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]
        if include_8_9:
            ranks.extend([8, 9])
            ranks.sort()
        suits = [Suit.COINS, Suit.CUPS, Suit.SWORDS, Suit.CLUBS]
        super().__init__(ranks, suits)