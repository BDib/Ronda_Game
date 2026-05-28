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
        p1 = Player("P1") # Team 0 (Index 0)
        p2 = Player("P2") # Team 1 (Index 1)
        p3 = Player("P3") # Team 0 (Index 2)
        p4 = Player("P4") # Team 1 (Index 3)

        # Ensure hands don't have announcements
        p1.hand = [Card(Suit.COINS, 1), Card(Suit.CUPS, 2), Card(Suit.SWORDS, 3)]
        p2.hand = [Card(Suit.COINS, 4), Card(Suit.CUPS, 5), Card(Suit.SWORDS, 6)]
        p3.hand = [Card(Suit.COINS, 7), Card(Suit.CUPS, 10), Card(Suit.SWORDS, 11)]
        p4.hand = [Card(Suit.COINS, 12), Card(Suit.CUPS, 1), Card(Suit.SWORDS, 2)]

        # Override resolve_announcements to do nothing
        original_resolve = RondaGameState.resolve_announcements
        RondaGameState.resolve_announcements = lambda self: None

        game = RondaGameState([p1, p2, p3, p4])
        # Empty deck to prevent redeals during play_move if all cards played
        game.deck.cards = []

        for p in game.players: p.score = 0

        # Teams: Team 0: [P1, P3], Team 1: [P2, P4]
        self.assertEqual(p1.team_id, 0)
        self.assertEqual(p2.team_id, 1)
        self.assertEqual(p3.team_id, 0)
        self.assertEqual(p4.team_id, 1)

        # Force a Bount for P1 (Team 0)
        game.last_card_played = Card(Suit.COINS, 7)
        game.current_player_index = 0 # P1's turn
        p1.hand = [Card(Suit.CUPS, 7)]
        game.play_move(p1, p1.hand[0])

        self.assertEqual(p1.score, 1)
        self.assertEqual(p3.score, 1)
        self.assertEqual(p2.score, 0)

        RondaGameState.resolve_announcements = original_resolve

    def test_end_round_card_counting_teams(self):
        p1 = Player("P1") # T0
        p2 = Player("P2") # T1
        p3 = Player("P3") # T0
        p4 = Player("P4") # T1

        # Override resolve_announcements to do nothing
        original_resolve = RondaGameState.resolve_announcements
        RondaGameState.resolve_announcements = lambda self: None

        game = RondaGameState([p1, p2, p3, p4])
        game.deck.cards = []
        game.target_score = 1 # Force game over to avoid redeal and random points
        for p in game.players: p.score = 0

        # Ensure no table cards are captured at the end
        game.last_taker = None
        game.table = []

        # Team 0 (P1 + P3): 25 cards -> Expected 5 points each
        p1.captured_cards = [Card(Suit.COINS, 1)] * 15
        p3.captured_cards = [Card(Suit.COINS, 1)] * 10
        # Team 1 (P2 + P4): 15 cards -> Expected 0 points each
        p2.captured_cards = [Card(Suit.COINS, 1)] * 5
        p4.captured_cards = [Card(Suit.COINS, 1)] * 10

        game.end_round()

        self.assertEqual(p1.score, 5)
        self.assertEqual(p3.score, 5)
        self.assertEqual(p2.score, 0)
        self.assertEqual(p4.score, 0)

        RondaGameState.resolve_announcements = original_resolve

if __name__ == "__main__":
    unittest.main()
