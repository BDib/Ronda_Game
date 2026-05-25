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

    def test_team_scoring_4_players(self):
        p1 = Player("P1") # Top
        p2 = Player("P2") # Bottom (Human)
        p3 = Player("P3") # Left
        p4 = Player("P4") # Right
        # Ensure hands don't have announcements by making them unique and distinct
        p1.hand = [Card(Suit.COINS, 1), Card(Suit.CUPS, 2), Card(Suit.SWORDS, 3)]
        p2.hand = [Card(Suit.COINS, 4), Card(Suit.CUPS, 5), Card(Suit.SWORDS, 6)]
        p3.hand = [Card(Suit.COINS, 7), Card(Suit.CUPS, 10), Card(Suit.SWORDS, 11)]
        p4.hand = [Card(Suit.COINS, 12), Card(Suit.CUPS, 1), Card(Suit.SWORDS, 2)]

        # Override RondaGameState.deal_cards to do nothing so it doesn't mess with our hands
        original_deal = RondaGameState.deal_cards
        RondaGameState.deal_cards = lambda self: None

        game = RondaGameState([p1, p2, p3, p4])
        RondaGameState.deal_cards = original_deal

        game.target_score = 100
        for p in game.players: p.score = 0

        # Teams: Team 0: [P1, P2] (Top/Bottom), Team 1: [P3, P4] (Left/Right)
        self.assertEqual(p1.team_id, 0)
        self.assertEqual(p2.team_id, 0)
        self.assertEqual(p3.team_id, 1)
        self.assertEqual(p4.team_id, 1)

        # Force a Bount for P2 (Team 0)
        game.last_card_played = Card(Suit.COINS, 7)
        game.current_player_index = 1 # P2's turn
        p2.hand = [Card(Suit.CUPS, 7)]
        game.play_move(p2, p2.hand[0])

        self.assertEqual(p1.score, 1)
        self.assertEqual(p2.score, 1)
        self.assertEqual(p3.score, 0)

    def test_end_round_card_counting_teams(self):
        p1 = Player("P1")
        p2 = Player("P2")
        p3 = Player("P3")
        p4 = Player("P4")

        # Prevent initial dealing
        original_deal = RondaGameState.deal_cards
        RondaGameState.deal_cards = lambda self: None
        game = RondaGameState([p1, p2, p3, p4])
        RondaGameState.deal_cards = original_deal

        game.target_score = 100
        for p in game.players: p.score = 0

        # Ensure no table cards are captured at the end
        game.last_taker = None
        game.table = []

        # Team 0: P1 + P2 = 25 cards
        p1.captured_cards = [Card(Suit.COINS, 1)] * 15
        p2.captured_cards = [Card(Suit.COINS, 1)] * 10
        # Team 1: P3 + P4 = 15 cards
        p3.captured_cards = [Card(Suit.COINS, 1)] * 5
        p4.captured_cards = [Card(Suit.COINS, 1)] * 10

        game.end_round()

        self.assertEqual(p1.score, 5)
        self.assertEqual(p2.score, 5)
        self.assertEqual(p3.score, 0)
        self.assertEqual(p4.score, 0)

if __name__ == "__main__":
    unittest.main()
