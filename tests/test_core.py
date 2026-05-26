import unittest
from engine.core import Card, Suit, Player, Deck

class TestCore(unittest.TestCase):
    def test_card_equality(self):
        c1 = Card(Suit.COINS, 1)
        c2 = Card(Suit.COINS, 1)
        c3 = Card(Suit.CUPS, 1)
        self.assertEqual(c1, c2)
        self.assertNotEqual(c1, c3)

    def test_player_capture(self):
        player = Player("Test")
        cards = [Card(Suit.COINS, 1), Card(Suit.CUPS, 2)]
        player.capture(cards)
        self.assertEqual(len(player.captured_cards), 2)
        self.assertEqual(player.captured_cards, cards)

    def test_deck_draw(self):
        ranks = [1, 2, 3]
        suits = [Suit.COINS, Suit.CUPS]
        deck = Deck(ranks, suits)
        self.assertEqual(len(deck), 6)
        drawn = deck.draw(2)
        self.assertEqual(len(drawn), 2)
        self.assertEqual(len(deck), 4)

if __name__ == "__main__":
    unittest.main()
