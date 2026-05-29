import unittest
from engine.core import Player, Card, Suit
from ronda.logic import RondaGameState

class TestRondaRules(unittest.TestCase):
    def setUp(self):
        # 4 Players
        self.p1 = Player("P1") # Team 0 (Index 0)
        self.p2 = Player("P2") # Team 1 (Index 1)
        self.p3 = Player("P3") # Team 0 (Index 2)
        self.p4 = Player("P4") # Team 1 (Index 3)
        self.players = [self.p1, self.p2, self.p3, self.p4]
        # skip_setup=True prevents initial dealing and announcements
        self.game = RondaGameState(self.players, target_score=1000, skip_setup=True, allow_missa=False)

        for p in self.players:
            p.hand = []
            p.captured_cards = []
            p.score = 0
        self.game.table = []
        self.game.last_card_played = None
        self.game.match_chain_count = 0
        self.game.deck.cards = [Card(Suit.COINS, 7)] * 100
        self.game.resolve_announcements = lambda: None

    def test_turn_alternation(self):
        # Index 0 (T0) -> Index 1 (T1) -> Index 2 (T0) -> Index 3 (T1)
        self.assertEqual(self.players[0].team_id, 0)
        self.assertEqual(self.players[1].team_id, 1)
        self.assertEqual(self.players[2].team_id, 0)
        self.assertEqual(self.players[3].team_id, 1)

    def test_bwahad_scoring_team_alternation(self):
        # P1 (T0) plays, P2 (T1) matches
        self.game.current_player_index = 0
        c1 = Card(Suit.COINS, 1)
        c2 = Card(Suit.CUPS, 1)
        self.p1.hand = [c1]
        self.p2.hand = [c2]

        self.game.play_move(self.p1, c1)
        events = self.game.play_move(self.p2, c2)

        # P2 matches P1 immediately -> Bwahad for Team 1
        self.assertTrue(events.get("bount"))
        self.assertEqual(self.p2.score, 1)
        self.assertEqual(self.p4.score, 1) # Partner gets score
        self.assertEqual(self.p1.score, 0)

    def test_oros_scoring_team(self):
        self.game.oros_scoring = True
        self.p1.captured_cards = [Card(Suit.COINS, 7)]
        self.p3.captured_cards = [Card(Suit.COINS, 10)]
        self.game.deck.cards = []
        self.game.end_round()
        # Team 0 score = 7 + 10 = 17
        self.assertEqual(self.p1.score, 17)
        self.assertEqual(self.p3.score, 17)

    def test_9a3a_as_team(self):
        self.game.enable_9a3a = True
        self.game.dealer_index = 0 # P1 is dealer (Team 0)
        self.game.last_card_played = Card(Suit.COINS, 1) # Ace's knock
        self.game.end_round()
        # Opponent Team (Team 1: P2 & P4) gets 5 points
        self.assertEqual(self.p2.score, 5)
        self.assertEqual(self.p4.score, 5)
        self.assertEqual(self.p1.score, 0)

if __name__ == "__main__":
    unittest.main()
