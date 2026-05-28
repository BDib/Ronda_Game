import unittest
from engine.core import Player, Card, Suit
from ronda.logic import RondaGameState

class TestMultiplayerLogic(unittest.TestCase):
    def setUp(self):
        self.p1 = Player("P1")
        self.p1.team_id = 0
        self.p2 = Player("P2")
        self.p2.team_id = 1
        self.players = [self.p1, self.p2]
        self.game = RondaGameState(self.players, target_score=41, skip_setup=True)

    def test_serialization_basic(self):
        # Add some cards to table and hands
        c1 = Card(Suit.COINS, 1)
        c2 = Card(Suit.CUPS, 7)
        self.game.table = [c1]
        self.p1.hand = [c2]

        state = self.game.serialize_state()

        self.assertEqual(len(state["table"]), 1)
        self.assertEqual(state["table"][0]["rank"], 1)
        self.assertEqual(state["table"][0]["suit"], "coins")

        self.assertEqual(len(state["players"]), 2)
        # Player 1 is human by default in Player constructor if not specified
        # But serialize_state checks p.is_human
        self.p1.is_human = True
        state = self.game.serialize_state()
        self.assertEqual(len(state["players"][0]["hand"]), 1)

    def test_team_stats_serialization(self):
        # P1 captures Ace of Gold
        ace_gold = Card(Suit.COINS, 1)
        seven_gold = Card(Suit.COINS, 7)
        self.p1.capture([ace_gold, seven_gold])

        state = self.game.serialize_state()
        team0_stats = state["team_stats"]["0"]

        self.assertEqual(team0_stats["oros_count"], 2)
        self.assertEqual(team0_stats["oros_sum"], 8)
        self.assertTrue(team0_stats["ace_of_gold"])
        self.assertEqual(team0_stats["captured_count"], 2)

    def test_room_logic_mock(self):
        # Testing the concept of room management
        active_rooms = {}
        room_id = "TEST01"
        game_opts = {"target_score": 41, "oros_scoring": False, "ace_of_gold_bonus": True,
                     "missa_last_card_allowed": False, "last_capture_wins_table": True}

        # Room creation
        active_rooms[room_id] = {
            "num_players": 2,
            "players": [None, None],
            "state": None,
            "game_opts": game_opts
        }

        # Player 1 joins
        active_rooms[room_id]["players"][0] = Player("Alice")
        # Player 2 joins
        active_rooms[room_id]["players"][1] = Player("Bob")

        # Game starts
        room = active_rooms[room_id]
        room["state"] = RondaGameState(room["players"], **room["game_opts"])

        self.assertIsNotNone(room["state"])
        self.assertEqual(len(room["state"].players), 2)
        self.assertEqual(room["state"].target_score, 41)

if __name__ == "__main__":
    unittest.main()
