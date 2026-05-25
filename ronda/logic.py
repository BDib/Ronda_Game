from engine.core import GameState, Player, Card, Suit
from engine.spanish_deck import SpanishDeck
from typing import List, Optional

class RondaGameState(GameState):
    def __init__(self, players: List[Player]):
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
        self.target_score = 41
        self.game_over = False
        
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
            winner.score += total_points

    def play_move(self, player: Player, card: Card) -> dict:
        if player != self.current_player:
            return {}
        player.play_card(card)
        events = {"captured": [], "bount": False, "inza": False, "ghader": False, "missa": False, "announcements": {}}
        
        if self.last_card_played and self.last_card_played.rank == card.rank:
            self.match_chain_count += 1
            if self.match_chain_count == 1:
                player.score += 1
                events["bount"] = True
            elif self.match_chain_count == 2:
                player.score += 5
                events["inza"] = True
            elif self.match_chain_count >= 3:
                player.score += 10
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
            
            if not self.table:
                is_last_card = all(len(p.hand) == 0 for p in self.players) and len(self.deck) == 0
                if not is_last_card:
                    player.score += 1
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

    def end_round(self):
        if self.table and self.last_taker:
            self.last_taker.capture(self.table)
            self.table = []
        for player in self.players:
            num_cards = len(player.captured_cards)
            if num_cards > 20: player.score += (num_cards - 20)
            player.captured_cards = [] 
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