import unittest
from ronda.logic import RondaGameState
from engine.core import Player, Card, Suit

class TestRonda(unittest.TestCase):
    def setUp(self):
        self.p1 = Player("P1")
        self.p2 = Player("P2")
        self.game = RondaGameState([self.p1, self.p2])

    def test_initial_setup(self):
        self.assertEqual(len(self.game.table), 4)
        self.assertEqual(len(self.p1.hand), 3)
        self.assertEqual(len(self.p2.hand), 3)
        # Check no pairs on table
        ranks = [c.rank for c in self.game.table]
        self.assertEqual(len(set(ranks)), 4)

    def test_play_move_turn_advancement(self):
        current = self.game.current_player
        card = current.hand[0]
        self.game.play_move(current, card)
        self.assertNotEqual(self.game.current_player, current)

    def test_bount_scoring(self):
        # Reset scores to ensure we only measure this move
        for p in self.game.players:
            p.score = 0

        # Force last card played to match
        self.game.last_card_played = Card(Suit.COINS, 5)
        # current player plays a 5
        self.game.current_player.hand = [Card(Suit.CUPS, 5)]
        player = self.game.current_player
        events = self.game.play_move(player, player.hand[0])
        self.assertTrue(events["bount"])
        self.assertEqual(player.score, 1)

if __name__ == "__main__":
    unittest.main()
