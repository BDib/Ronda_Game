import unittest
from engine.core import Player, Card, Suit
from ronda.logic import RondaGameState

class TestRondaRules(unittest.TestCase):
    def setUp(self):
        self.p1 = Player("P1")
        self.p2 = Player("P2")
        # skip_setup=True prevents initial dealing and announcements
        self.game = RondaGameState([self.p1, self.p2], target_score=1000, skip_setup=True, allow_missa=False)

        self.game.table = []
        self.p1.hand = []
        self.p2.hand = []
        self.p1.captured_cards = []
        self.p2.captured_cards = []
        self.p1.score = 0
        self.p2.score = 0
        self.game.last_card_played = None
        self.game.match_chain_count = 0
        self.game.deck.cards = [Card(Suit.COINS, 7)] * 100
        self.game.resolve_announcements = lambda: None

    def test_bwahad_scoring(self):
        self.game.current_player_index = 0
        c1 = Card(Suit.COINS, 1)
        c2 = Card(Suit.CUPS, 1)
        self.p1.hand = [c1]
        self.p2.hand = [c2]

        self.game.play_move(self.p1, c1)
        events = self.game.play_move(self.p2, c2)
        self.assertTrue(events.get("bount"))
        self.assertEqual(self.p2.score, 1)

    def test_bkhamsa_scoring(self):
        self.game.current_player_index = 0
        c1 = Card(Suit.COINS, 1)
        c2 = Card(Suit.CUPS, 1)
        c3 = Card(Suit.SWORDS, 1)
        self.p1.hand = [c1, c3]
        self.p2.hand = [c2]

        self.game.play_move(self.p1, c1)
        self.game.play_move(self.p2, c2)
        events = self.game.play_move(self.p1, c3)
        self.assertTrue(events.get("inza"))
        self.assertEqual(self.p1.score, 5)

    def test_bashara_scoring(self):
        self.game.current_player_index = 0
        c1 = Card(Suit.COINS, 1)
        c2 = Card(Suit.CUPS, 1)
        c3 = Card(Suit.SWORDS, 1)
        c4 = Card(Suit.CLUBS, 1)
        self.p1.hand = [c1, c3]
        self.p2.hand = [c2, c4]

        self.game.play_move(self.p1, c1)
        self.game.play_move(self.p2, c2)
        self.game.play_move(self.p1, c3)
        events = self.game.play_move(self.p2, c4)
        self.assertTrue(events.get("ghader"))
        self.assertEqual(self.p2.score, 11)

    def test_maysa_scoring(self):
        self.game.allow_missa = True
        self.game.table = [Card(Suit.COINS, 5)]
        c1 = Card(Suit.CUPS, 5)
        self.p1.hand = [c1]
        self.game.current_player_index = 0

        events = self.game.play_move(self.p1, c1)
        self.assertTrue(events.get("missa"))
        self.assertEqual(self.p1.score, 1)

    def test_consecutive_capture(self):
        self.game.table = [Card(Suit.COINS, 5), Card(Suit.CUPS, 6), Card(Suit.SWORDS, 7)]
        c1 = Card(Suit.CLUBS, 5)
        self.p1.hand = [c1]
        self.game.current_player_index = 0

        self.game.play_move(self.p1, c1)
        self.assertEqual(len(self.p1.captured_cards), 4)

    def test_oros_scoring_end_round(self):
        self.game.oros_scoring = True
        self.p1.captured_cards = [Card(Suit.COINS, 7), Card(Suit.COINS, 10)]
        self.game.deck.cards = []
        self.game.end_round()
        self.assertEqual(self.p1.score, 17)

    def test_ace_of_gold_bonus(self):
        self.game.ace_of_gold_bonus = True
        self.p1.captured_cards = [Card(Suit.COINS, 1)]
        self.game.end_round()
        self.assertEqual(self.p1.score, 10)

    def test_9a3a_rey(self):
        self.game.enable_9a3a = True
        self.game.dealer_index = 0
        self.game.last_card_played = Card(Suit.COINS, 12)
        self.game.end_round()
        self.assertEqual(self.p1.score, 5)

    def test_9a3a_as(self):
        self.game.enable_9a3a = True
        self.game.dealer_index = 0
        self.game.last_card_played = Card(Suit.COINS, 1)
        self.game.end_round()
        self.assertEqual(self.p2.score, 5)

if __name__ == "__main__":
    unittest.main()
