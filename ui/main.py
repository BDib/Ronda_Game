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
        # Game expects a list of players. Dealer is index 0 (CPU in this case), human is index 1.
        players = [self.ai_player, self.human_player]
        self.game = RondaGameState(players)
        self.last_events = {}
        self.render_game_board()
        if self.game.current_player == self.ai_player:
            self.page.run_task(self.handle_cpu_move)

    def get_card_image_path(self, card: Card):
        if not card: return "cards/card_back.jpeg"
        # Ensure the path is relative to assets directory which flet expects
        return f"cards/card_{card.suit.value}_{str(card.rank).zfill(2)}.jpeg"

    def render_game_board(self):
        self.page.clean()
        
        if self.game.game_over:
            winner = max(self.game.players, key=lambda p: p.score)
            self.page.add(
                ft.Container(
                    content=ft.Column([
                        ft.Text("GAME OVER", size=50, weight="bold", color="yellow"),
                        ft.Text(f"{winner.name} Wins with {winner.score} points!", size=30, color="white"),
                        ft.FilledButton("Play Again", on_click=self.start_single_player),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True, alignment=ft.Alignment(0, 0)
                )
            )
            return

        cpu_row = ft.Row([
            ft.Column([
                ft.Text(f"CPU: {self.ai_player.score} pts", size=18, weight="bold", color="white"),
                ft.Text("Dealer" if self.game.players[self.game.dealer_index] == self.ai_player else "", size=12, color="yellow"),
            ]),
            ft.Row([
                ft.Text(f"Captured: {len(self.ai_player.captured_cards)}", size=12, color="white70"),
                ft.Row([ft.Image(src="cards/card_back.jpeg", width=60) for _ in self.ai_player.hand])
            ])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        deck_stack = ft.Stack([
            ft.Image(src="cards/card_back.jpeg", width=70, opacity=0.8),
            ft.Container(
                content=ft.Text(str(len(self.game.deck)), size=14, weight="bold", color="white"),
                alignment=ft.Alignment(0, 0),
                width=70, height=100
            )
        ]) if len(self.game.deck) > 0 else ft.Container()

        table_row = ft.Row(
            controls=[ft.Image(src=self.get_card_image_path(c), width=90) for c in self.game.table],
            alignment=ft.MainAxisAlignment.CENTER, spacing=15, wrap=True
        )

        event_text = []
        if self.last_events.get("bount"): event_text.append("BOUNT! (+1)")
        if self.last_events.get("inza"): event_text.append("INZA! (+5)")
        if self.last_events.get("ghader"): event_text.append("GHADER! (+10)")
        if self.last_events.get("missa"): event_text.append("MISSA! (+1)")
        
        ann_events = self.last_events.get("announcements", {})
        for p, ann in ann_events.items():
            pts = 5 if ann == "Tringla" else 1
            event_text.append(f"{p.name}: {ann} (+{pts})")

        status_text = "Your Turn" if self.game.current_player == self.human_player else "CPU is thinking..."
        if self.game.game_over: status_text = "Game Over"

        def on_card_hover(e):
            e.control.border = ft.border.all(2, "yellow") if e.data == "true" else None
            e.control.update()

        human_hand = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Image(src=self.get_card_image_path(c), width=100),
                    on_click=lambda _, card=c: self.handle_human_move(card),
                    border_radius=5,
                    on_hover=on_card_hover
                ) for c in self.human_player.hand
            ], alignment=ft.MainAxisAlignment.CENTER
        )

        self.page.add(
            ft.Column([
                cpu_row,
                ft.Container(
                    content=ft.Column([
                        ft.Text(" ".join(event_text), color="yellow", size=24, weight="bold"),
                        ft.Row([deck_stack, table_row], alignment=ft.MainAxisAlignment.CENTER, spacing=30),
                        ft.Text(status_text, color="white", size=16, italic=True)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True, alignment=ft.Alignment(0, 0)
                ),
                ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text(f"Your Score: {self.human_player.score}", size=20, weight="bold", color="white"),
                            ft.Text(f"Captured: {len(self.human_player.captured_cards)} cards", size=12, color="white70"),
                        ]),
                        ft.Text("Dealer" if self.game.players[self.game.dealer_index] == self.human_player else "", size=12, color="yellow"),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    human_hand
                ])
            ], expand=True, spacing=20)
        )
        self.page.update()

    def handle_human_move(self, card: Card):
        if self.game.current_player == self.human_player and not self.game.game_over:
            self.last_events = self.game.play_move(self.human_player, card)
            self.render_game_board()
            if not self.game.game_over:
                if self.game.current_player == self.ai_player:
                    self.page.run_task(self.handle_cpu_move)

    async def handle_cpu_move(self):
        if self.game.game_over: return
        await asyncio.sleep(1)
        if self.game.current_player == self.ai_player and not self.game.game_over:
            move = self.ai_player.select_move(self.game)
            self.last_events = self.game.play_move(self.ai_player, move)
            self.render_game_board()
            # If it's still CPU's turn (e.g. in multi-player games or if logic changes)
            if self.game.current_player == self.ai_player and not self.game.game_over:
                self.page.run_task(self.handle_cpu_move)

def main(page: ft.Page):
    # Set assets directory relative to current working directory if possible
    # or use absolute path
    page.assets_dir = os.path.join(os.getcwd(), "assets")
    RondaApp(page)

if __name__ == "__main__":
    ft.app(main, assets_dir="assets")