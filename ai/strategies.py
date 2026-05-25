import random
from engine.core import Player, Card
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ronda.logic import RondaGameState

class RondaAI(Player):
    def __init__(self, name: str, difficulty: str = "Medium"):
        super().__init__(name, is_human=False)
        self.difficulty = difficulty

    def select_move(self, state: 'RondaGameState') -> Card:
        if self.difficulty == "Easy": return self._move_easy(state)
        elif self.difficulty == "Hard": return self._move_hard(state)
        else: return self._move_medium(state)

    def _get_capture_info(self, card: Card, table: List[Card]) -> dict:
        info = {"count": 0, "is_missa": False, "ranks": []}
        ranks_on_table = [c.rank for c in table]
        if card.rank in ranks_on_table:
            captured_ranks = [card.rank, card.rank]
            temp_ranks = list(ranks_on_table)
            temp_ranks.remove(card.rank)
            full_ranks = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]
            current_rank = card.rank
            while True:
                try:
                    idx = full_ranks.index(current_rank) + 1
                    if idx >= len(full_ranks): break
                    next_rank = full_ranks[idx]
                    if next_rank in temp_ranks:
                        captured_ranks.append(next_rank)
                        temp_ranks.remove(next_rank)
                        current_rank = next_rank
                    else: break
                except ValueError: break
            info["count"] = len(captured_ranks)
            info["ranks"] = captured_ranks
            info["is_missa"] = (len(temp_ranks) == 0)
        return info

    def _move_easy(self, state: 'RondaGameState') -> Card:
        return random.choice(self.hand)

    def _move_medium(self, state: 'RondaGameState') -> Card:
        captures = []
        for card in self.hand:
            info = self._get_capture_info(card, state.table)
            if info["count"] > 0: captures.append((card, info))
        if captures:
            best_move = max(captures, key=lambda x: x[1]["count"])
            return best_move[0]
        ranks_on_table = [c.rank for c in state.table]
        safe_cards = [c for c in self.hand if c.rank not in ranks_on_table]
        return random.choice(safe_cards) if safe_cards else random.choice(self.hand)

    def _move_hard(self, state: 'RondaGameState') -> Card:
        captures = []
        for card in self.hand:
            info = self._get_capture_info(card, state.table)
            score = info["count"]
            if info["is_missa"]: score += 10
            if state.last_card_played and card.rank == state.last_card_played.rank:
                score += 5
            if score > 0: captures.append((card, score))
        if captures:
            best_move = max(captures, key=lambda x: x[1])
            return best_move[0]
        return random.choice(self.hand)