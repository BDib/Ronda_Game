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
        if not card: return "/cards/card_back.jpeg"
        # Ensure the path is relative to assets directory which flet expects
        return f"/cards/card_{card.suit.value}_{str(card.rank).zfill(2)}.jpeg"

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

        cpu_row = ft.Container(
            content=ft.Row([
                ft.Column([
                    ft.Text(f"CPU: {self.ai_player.score} pts", size=22, weight="bold", color="white"),
                    ft.Text("Dealer" if self.game.players[self.game.dealer_index] == self.ai_player else "", size=14, color="yellow", weight="w500"),
                ], spacing=2),
                ft.Row([
                    ft.Container(
                        content=ft.Text(f"Captured: {len(self.ai_player.captured_cards)}", size=14, color="white"),
                        bgcolor="bluegrey700",
                        padding=ft.Padding(10, 5, 10, 5),
                        border_radius=15,
                    ),
                    ft.Row([ft.Image(src="/cards/card_back.jpeg", width=70, border_radius=5) for _ in self.ai_player.hand], spacing=5)
                ], spacing=20)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=10,
            bgcolor="#1b5e20",
            border_radius=10,
        )

        deck_stack = ft.Stack([
            ft.Image(src="/cards/card_back.jpeg", width=80, border_radius=5, opacity=0.9),
            ft.Container(
                content=ft.Text(str(len(self.game.deck)), size=18, weight="bold", color="white"),
                alignment=ft.Alignment(0, 0),
                width=80, height=114
            )
        ]) if len(self.game.deck) > 0 else ft.Container(width=80, height=114)

        table_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Image(src=self.get_card_image_path(c), width=100, border_radius=5),
                    animate_scale=ft.Animation(300, ft.AnimationCurve.DECELERATE),
                    scale=1.0,
                ) for c in self.game.table
            ],
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

        status_color = "yellow" if self.game.current_player == self.human_player else "white70"
        status_text = "YOUR TURN" if self.game.current_player == self.human_player else "CPU IS THINKING..."
        if self.game.game_over: status_text = "GAME OVER"

        def on_card_hover(e):
            e.control.scale = 1.1 if e.data == "true" else 1.0
            e.control.border = ft.border.all(3, "yellow") if e.data == "true" else None
            e.control.update()

        human_hand = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Image(src=self.get_card_image_path(c), width=120, border_radius=8),
                    on_click=lambda _, card=c: self.handle_human_move(card),
                    border_radius=8,
                    on_hover=on_card_hover,
                    animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
                    disabled=self.game.current_player != self.human_player
                ) for c in self.human_player.hand
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=15
        )

        self.page.add(
            ft.Column([
                cpu_row,
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Text(" ".join(event_text), color="yellow", size=32, weight="bold", italic=True),
                            height=40
                        ),
                        ft.Row([
                            deck_stack,
                            ft.VerticalDivider(width=20, color="transparent"),
                            ft.Container(content=table_row, expand=True)
                        ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Container(
                            content=ft.Text(status_text, color=status_color, size=20, weight="bold"),
                            margin=ft.Margin(0, 20, 0, 0)
                        )
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                    padding=20,
                    bgcolor="#263238",
                    border_radius=20,
                    margin=ft.Margin(0, 10, 0, 10),
                    shadow=ft.BoxShadow(blur_radius=15, color="black26")
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Column([
                                ft.Text(f"Your Score: {self.human_player.score}", size=24, weight="bold", color="white"),
                                ft.Text("Dealer" if self.game.players[self.game.dealer_index] == self.human_player else "", size=14, color="yellow", weight="w500"),
                            ], spacing=2),
                            ft.Container(
                                content=ft.Text(f"Captured: {len(self.human_player.captured_cards)} cards", size=14, color="white"),
                                bgcolor="bluegrey700",
                                padding=ft.Padding(10, 5, 10, 5),
                                border_radius=15,
                            ),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        human_hand
                    ]),
                    padding=10,
                    bgcolor="#1b5e20",
                    border_radius=10,
                )
            ], expand=True, spacing=10)
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
    RondaApp(page)

if __name__ == "__main__":
    # Get the directory of the current script
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_path = os.path.join(base_path, "assets")
    ft.app(target=main, assets_dir=assets_path)