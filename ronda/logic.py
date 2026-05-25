from engine.core import GameState, Player, Card, Suit
from engine.spanish_deck import SpanishDeck
from typing import List, Optional

class RondaGameState(GameState):
    def __init__(self, players: List[Player],
                 target_score: int = 41,
                 oros_scoring: bool = False,
                 ace_of_gold_bonus: bool = False,
                 allow_missa: bool = True,
                 missa_last_card_allowed: bool = False,
                 last_capture_wins_table: bool = True):
        super().__init__()
        self.deck = SpanishDeck(include_8_9=False)
        self.players = players
        self.current_player_index = 1 # Dealer is 0, so player 1 starts
        self.last_taker: Optional[Player] = None
        self.last_card_played: Optional[Card] = None
        self.match_chain_count: int = 0
        
        self.announcements = {}
        self.announcement_ranks = {}
        self.dealer_index = 0
        self.target_score = target_score
        self.oros_scoring = oros_scoring
        self.ace_of_gold_bonus = ace_of_gold_bonus
        self.allow_missa = allow_missa
        self.missa_last_card_allowed = missa_last_card_allowed
        self.last_capture_wins_table = last_capture_wins_table

        self.game_over = False
        self._assign_teams()
        
        self.initial_table_setup()
        self.deal_cards()

    def initial_table_setup(self):
        self.table = []
        self.deck.shuffle()
        while len(self.table) < 4:
            if not self.deck.cards: break
            card = self.deck.draw(1)[0]
            ranks = [c.rank for c in self.table]
            if card.rank in ranks:
                # In Ronda, only pairs are forbidden on the initial table
                self.deck.cards.append(card)
                self.deck.shuffle()
            else:
                self.table.append(card)

    def deal_cards(self):
        if len(self.deck) >= len(self.players) * 3:
            for player in self.players:
                player.add_to_hand(self.deck.draw(3))
            self.resolve_announcements()
        else:
            self.end_round()

    def _assign_teams(self):
        if len(self.players) == 4:
            # Team 0: Players 0 and 1 (Opposite), Team 1: Players 2 and 3 (Opposite)
            # Players: 0 (Top), 1 (Bottom/Human), 2 (Left), 3 (Right)
            self.players[0].team_id = 0
            self.players[1].team_id = 0
            self.players[2].team_id = 1
            self.players[3].team_id = 1
        else:
            # Each player is their own team
            for i, p in enumerate(self.players):
                p.team_id = i

    def add_score(self, player: Player, points: int):
        target_team = player.team_id
        for p in self.players:
            if p.team_id == target_team:
                p.score += points

    def resolve_announcements(self):
        self.announcements = {}
        self.announcement_ranks = {}
        total_points = 0
        announcers = []
        
        for player in self.players:
            ranks = [c.rank for c in player.hand]
            rank_counts = {r: ranks.count(r) for r in set(ranks)}
            if 3 in rank_counts.values():
                rank = [r for r, c in rank_counts.items() if c == 3][0]
                self.announcements[player] = "Tringla"
                self.announcement_ranks[player] = rank
                total_points += 5
                announcers.append(player)
            elif 2 in rank_counts.values():
                rank = [r for r, c in rank_counts.items() if c == 2][0]
                self.announcements[player] = "Ronda"
                self.announcement_ranks[player] = rank
                total_points += 1
                announcers.append(player)

        if announcers:
            def sort_key(p):
                base = 100 if self.announcements[p] == "Tringla" else 0
                return base + self.announcement_ranks[p]
            winner = max(announcers, key=sort_key)
            self.add_score(winner, total_points)

    def play_move(self, player: Player, card: Card) -> dict:
        if player != self.current_player:
            return {}
        player.play_card(card)
        events = {"captured": [], "bount": False, "inza": False, "ghader": False, "missa": False, "announcements": {}}
        
        if self.last_card_played and self.last_card_played.rank == card.rank:
            self.match_chain_count += 1
            if self.match_chain_count == 1:
                self.add_score(player, 1)
                events["bount"] = True
            elif self.match_chain_count == 2:
                self.add_score(player, 5)
                events["inza"] = True
            elif self.match_chain_count >= 3:
                self.add_score(player, 10)
                events["ghader"] = True
        else:
            self.match_chain_count = 0
            
        captured = []
        match_idx = -1
        for i, table_card in enumerate(self.table):
            if table_card.rank == card.rank:
                match_idx = i
                break
        
        if match_idx != -1:
            matched_card = self.table.pop(match_idx)
            captured.append(card)
            captured.append(matched_card)
            full_ranks = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]
            current_rank = card.rank
            while True:
                try:
                    next_rank_idx = full_ranks.index(current_rank) + 1
                    if next_rank_idx >= len(full_ranks): break
                    next_rank = full_ranks[next_rank_idx]
                    found_next = False
                    for i, table_card in enumerate(self.table):
                        if table_card.rank == next_rank:
                            captured.append(self.table.pop(i))
                            current_rank = next_rank
                            found_next = True
                            break
                    if not found_next: break
                except ValueError: break
            
            player.capture(captured)
            self.last_taker = player
            events["captured"] = captured
            
            if not self.table and self.allow_missa:
                is_last_card = all(len(p.hand) == 0 for p in self.players) and len(self.deck) == 0
                if not is_last_card or self.missa_last_card_allowed:
                    self.add_score(player, 1)
                    events["missa"] = True
        else:
            self.table.append(card)
            
        self.last_card_played = card
        self.next_turn()

        if all(len(p.hand) == 0 for p in self.players):
            if len(self.deck) > 0:
                self.deal_cards()
                events["announcements"] = self.announcements
            else:
                self.end_round()
        return events

    def _add_team_score(self, team_id, points):
        for p in self.players:
            if p.team_id == team_id:
                p.score += points

    def serialize_state(self):
        team_stats = {}
        for p in self.players:
            tid = str(p.team_id)
            if tid not in team_stats:
                team_stats[tid] = {"oros_count": 0, "oros_sum": 0, "ace_of_gold": False, "captured_count": 0}
            team_stats[tid]["captured_count"] += len(p.captured_cards)
            for c in p.captured_cards:
                if c.suit == Suit.COINS:
                    team_stats[tid]["oros_count"] += 1
                    team_stats[tid]["oros_sum"] += c.rank
                    if c.rank == 1:
                        team_stats[tid]["ace_of_gold"] = True

        return {
            "table": [{"suit": c.suit.value, "rank": c.rank} for c in self.table],
            "players": [
                {
                    "name": p.name,
                    "hand_size": len(p.hand),
                    "score": p.score,
                    "captured_count": len(p.captured_cards),
                    "team_id": p.team_id,
                    "hand": [{"suit": c.suit.value, "rank": c.rank} for c in p.hand] if p.is_human else []
                } for p in self.players
            ],
            "current_player_index": self.current_player_index,
            "dealer_index": self.dealer_index,
            "game_over": self.game_over,
            "deck_count": len(self.deck),
            "team_stats": team_stats
        }

    def end_round(self):
        if self.table and self.last_taker and self.last_capture_wins_table:
            self.last_taker.capture(self.table)
            self.table = []

        team_captures = {}
        team_oros_points = {}
        team_ace_of_gold = {}

        for player in self.players:
            tid = player.team_id
            team_captures[tid] = team_captures.get(tid, 0) + len(player.captured_cards)

            if self.oros_scoring or self.ace_of_gold_bonus:
                for card in player.captured_cards:
                    if card.suit == Suit.COINS:
                        if self.oros_scoring:
                            team_oros_points[tid] = team_oros_points.get(tid, 0) + card.rank
                        if self.ace_of_gold_bonus and card.rank == 1:
                            team_ace_of_gold[tid] = True

            player.captured_cards = []

        unique_tids = set(p.team_id for p in self.players)
        for tid in unique_tids:
            count = team_captures.get(tid, 0)
            # Standard scoring for captured cards > 20
            if count > 20:
                points = count - 20
                self._add_team_score(tid, points)

            # Oros scoring
            if self.oros_scoring and tid in team_oros_points:
                self._add_team_score(tid, team_oros_points[tid])

            # Ace of Gold bonus
            if self.ace_of_gold_bonus and team_ace_of_gold.get(tid):
                self._add_team_score(tid, 10)

        winner = [p for p in self.players if p.score >= self.target_score]
        if winner:
            self.game_over = True
            self.is_over = True
        else:
            self.dealer_index = (self.dealer_index + 1) % len(self.players)
            self.current_player_index = (self.dealer_index + 1) % len(self.players)
            self.deck = SpanishDeck(include_8_9=False)
            self.last_taker = None
            self.last_card_played = None
            self.match_chain_count = 0
            self.table = []
            for player in self.players:
                player.hand = []
                player.captured_cards = []
            self.initial_table_setup()
            self.deal_cards()
