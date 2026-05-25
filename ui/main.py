import flet as ft
import os
import sys
import asyncio

# Add current directory to path so it can find engine/ronda/ai folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ronda.logic import RondaGameState
    from ai.strategies import RondaAI
    from engine.core import Player, Card
except ImportError:
    # If running from inside ui/ folder
    sys.path.append(os.getcwd())
    from ronda.logic import RondaGameState
    from ai.strategies import RondaAI
    from engine.core import Player, Card

class RondaApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Ronda Moroccan Card Game"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#2e7d32" 
        self.game = None
        self.ai_player = None
        self.human_player = None
        self.last_events = {}
        self.init_ui()

    def init_ui(self):
        self.page.clean()
        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("RONDA", size=60, weight="bold", color="white"),
                    ft.FilledButton("Start New Game", on_click=self.start_single_player),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                expand=True,
                alignment=ft.Alignment(0, 0)
            )
        )

    def start_single_player(self, e):
        self.human_player = Player("You")
        self.ai_player = RondaAI("CPU", difficulty="Hard")
        self.game = RondaGameState(["You", "CPU"])
        self.game.players = [self.human_player, self.ai_player]
        self.game.deal_cards()
        self.render_game_board()

    def get_card_image_path(self, card: Card):
        if not card: return "cards/card_back.jpeg"
        return f"cards/card_{card.suit.value}_{str(card.rank).zfill(2)}.jpeg"

    def render_game_board(self):
        self.page.clean()
        
        cpu_row = ft.Row([
            ft.Text(f"CPU: {self.ai_player.score} pts", size=18, weight="bold"),
            ft.Row([ft.Image(src="cards/card_back.jpeg", width=60) for _ in self.ai_player.hand])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        table_row = ft.Row(
            controls=[ft.Image(src=self.get_card_image_path(c), width=90) for c in self.game.table],
            alignment=ft.MainAxisAlignment.CENTER, spacing=15, wrap=True
        )

        event_text = ""
        if self.last_events.get("bount"): event_text += "BOUNT! "
        if self.last_events.get("missa"): event_text += "MISSA! "
        
        human_hand = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Image(src=self.get_card_image_path(c), width=100),
                    on_click=lambda _, card=c: self.handle_human_move(card),
                ) for c in self.human_player.hand
            ], alignment=ft.MainAxisAlignment.CENTER
        )

        self.page.add(
            ft.Column([
                cpu_row,
                ft.Container(content=ft.Column([
                    ft.Text(event_text, color="yellow", size=24, weight="bold"),
                    table_row
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER), expand=True, alignment=ft.Alignment(0, 0)),
                ft.Column([
                    ft.Text(f"Your Score: {self.human_player.score}", size=20, weight="bold"),
                    human_hand
                ])
            ], expand=True)
        )

    def handle_human_move(self, card: Card):
        if self.game.current_player == self.human_player and not self.game.game_over:
            self.last_events = self.game.play_move(self.human_player, card)
            self.render_game_board()
            if not self.game.game_over:
                self.page.run_task(self.handle_cpu_move)

    async def handle_cpu_move(self):
        await asyncio.sleep(1)
        if self.game.current_player == self.ai_player and not self.game.game_over:
            move = self.ai_player.select_move(self.game)
            self.last_events = self.game.play_move(self.ai_player, move)
            self.render_game_board()

def main(page: ft.Page):
    page.assets_dir = "assets"
    RondaApp(page)

if __name__ == "__main__":
    ft.app(target=main)