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
        self.ai_players = []
        self.human_player = None
        self.last_events = {}
        self.init_ui()

    def init_ui(self):
        self.page.clean()

        player_count_radio = ft.RadioGroup(content=ft.Row([
            ft.Radio(value="2", label="2 Players (1v1)"),
            ft.Radio(value="4", label="4 Players (2v2 Teams)"),
        ], alignment=ft.MainAxisAlignment.CENTER), value="2")

        difficulty_radio = ft.RadioGroup(content=ft.Row([
            ft.Radio(value="Easy", label="Easy"),
            ft.Radio(value="Medium", label="Medium"),
            ft.Radio(value="Hard", label="Hard"),
        ], alignment=ft.MainAxisAlignment.CENTER), value="Medium")

        self.page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("RONDA", size=80, weight="bold", color="white", italic=True),
                    ft.Text("Moroccan Card Game", size=20, color="white70"),
                    ft.Divider(height=40, color="transparent"),
                    ft.Text("Number of Players", size=18, weight="bold"),
                    player_count_radio,
                    ft.Divider(height=20, color="transparent"),
                    ft.Text("AI Difficulty", size=18, weight="bold"),
                    difficulty_radio,
                    ft.Divider(height=40, color="transparent"),
                    ft.FilledButton("Start Game",
                                    on_click=lambda _: self.start_game(int(player_count_radio.value), difficulty_radio.value),
                                    style=ft.ButtonStyle(padding=20),
                                    width=200),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                expand=True,
                alignment=ft.Alignment(0, 0)
            )
        )

    def start_game(self, num_players, difficulty):
        self.human_player = Player("You")
        if num_players == 2:
            self.ai_players = [RondaAI("CPU", difficulty=difficulty)]
            # CPU (0), Human (1)
            players = [self.ai_players[0], self.human_player]
        else:
            # 4 players: Team 0 (0 & 2), Team 1 (1 & 3)
            # In 4-player, opposite players are partners.
            # Layout positions: 0: Top, 1: Bottom (Human), 2: Left, 3: Right
            # Opposite pairs are (0, 1) and (2, 3).
            # So Team 0: 0 & 1 (Human & Partner Top)
            # Team 1: 2 & 3 (Left & Right Opponents)

            self.ai_players = [
                RondaAI("CPU (Partner)", difficulty=difficulty), # Index 0
                RondaAI("CPU (Left)", difficulty=difficulty),    # Index 2
                RondaAI("CPU (Right)", difficulty=difficulty)    # Index 3
            ]
            players = [
                self.ai_players[0], # Index 0 (Top)
                self.human_player,  # Index 1 (Bottom)
                self.ai_players[1], # Index 2 (Left)
                self.ai_players[2]  # Index 3 (Right)
            ]

        self.game = RondaGameState(players)
        self.last_events = {}
        self.render_game_board()
        if not self.game.current_player.is_human:
            self.page.run_task(self.handle_cpu_move)

    def get_card_image_path(self, card: Card):
        if not card: return "/cards/card_back.jpeg"
        return f"/cards/card_{card.suit.value}_{str(card.rank).zfill(2)}.jpeg"

    def render_game_board(self):
        self.page.clean()
        
        if self.game.game_over:
            winner_p = max(self.game.players, key=lambda p: p.score)
            winner_text = f"Team {winner_p.team_id + 1} Wins!" if len(self.game.players) == 4 else f"{winner_p.name} Wins!"
            self.page.add(
                ft.Container(
                    content=ft.Column([
                        ft.Text("GAME OVER", size=50, weight="bold", color="yellow"),
                        ft.Text(f"{winner_text} with {winner_p.score} points!", size=30, color="white"),
                        ft.FilledButton("Main Menu", on_click=lambda _: self.init_ui()),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True, alignment=ft.Alignment(0, 0)
                )
            )
            return

        def player_panel(player, orientation="horizontal"):
            is_dealer = self.game.players[self.game.dealer_index] == player
            is_turn = self.game.current_player == player

            status_color = "yellow" if is_turn else "white"
            dealer_mark = " (D)" if is_dealer else ""

            content_list = [
                ft.Column([
                    ft.Text(f"{player.name}{dealer_mark}", size=14, weight="bold", color=status_color),
                    ft.Text(f"Score: {player.score}", size=12, color="white70"),
                    ft.Text(f"Captured: {len(player.captured_cards)}", size=11, color="white54"),
                ], spacing=1),
            ]

            hand_images = [ft.Image(src="/cards/card_back.jpeg", width=40 if orientation=="vertical" else 50, border_radius=3) for _ in player.hand]

            if orientation == "horizontal":
                content_list.append(ft.Row(hand_images, spacing=5))
                return ft.Container(
                    content=ft.Row(content_list, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    padding=10, bgcolor="#1b5e20" if not is_turn else "#2e7d32", border_radius=10,
                    border=ft.border.all(2, "yellow") if is_turn else None
                )
            else:
                content_list.append(ft.Column(hand_images, spacing=5))
                return ft.Container(
                    content=ft.Column(content_list, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10, bgcolor="#1b5e20" if not is_turn else "#2e7d32", border_radius=10,
                    border=ft.border.all(2, "yellow") if is_turn else None
                )

        top_player = self.game.players[0]
        bottom_player = self.human_player
        left_player = self.game.players[2] if len(self.game.players) == 4 else None
        right_player = self.game.players[3] if len(self.game.players) == 4 else None

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

        central_area = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text(" ".join(event_text), color="yellow", size=24, weight="bold", italic=True),
                    height=30
                ),
                ft.Row([
                    deck_stack,
                    ft.VerticalDivider(width=20, color="transparent"),
                    ft.Container(content=table_row, expand=True)
                ], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(
                    content=ft.Text(status_text, color=status_color, size=16, weight="bold"),
                    margin=ft.Margin(0, 10, 0, 0)
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            alignment=ft.Alignment(0, 0),
            padding=15,
            bgcolor="#263238",
            border_radius=20,
            margin=ft.Margin(10, 10, 10, 10),
        )

        main_layout = ft.Column([
            player_panel(top_player),
            ft.Row([
                player_panel(left_player, "vertical") if left_player else ft.Container(width=100),
                central_area,
                player_panel(right_player, "vertical") if right_player else ft.Container(width=100),
            ], expand=True),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text(f"Team {self.human_player.team_id + 1 if self.human_player.team_id is not None else ''} | Your Score: {self.human_player.score}", size=18, weight="bold", color="white"),
                            ft.Text("Dealer" if self.game.players[self.game.dealer_index] == self.human_player else "", size=12, color="yellow"),
                        ], spacing=1),
                        ft.Text(f"Captured: {len(self.human_player.captured_cards)}", size=12, color="white70"),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    human_hand
                ]),
                padding=10, bgcolor="#1b5e20" if self.game.current_player != self.human_player else "#2e7d32",
                border_radius=10,
                border=ft.border.all(2, "yellow") if self.game.current_player == self.human_player else None
            )
        ], expand=True, spacing=5)

        self.page.add(main_layout)
        self.page.update()

    def handle_human_move(self, card: Card):
        if self.game.current_player == self.human_player and not self.game.game_over:
            self.last_events = self.game.play_move(self.human_player, card)
            self.render_game_board()
            if not self.game.game_over:
                if not self.game.current_player.is_human:
                    self.page.run_task(self.handle_cpu_move)

    async def handle_cpu_move(self):
        if self.game.game_over: return
        await asyncio.sleep(0.8)
        current_ai = self.game.current_player
        if not current_ai.is_human and not self.game.game_over:
            move = current_ai.select_move(self.game)
            self.last_events = self.game.play_move(current_ai, move)
            self.render_game_board()
            if not self.game.current_player.is_human and not self.game.game_over:
                self.page.run_task(self.handle_cpu_move)

def main(page: ft.Page):
    RondaApp(page)

if __name__ == "__main__":
    # Get the directory of the current script
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_path = os.path.join(base_path, "assets")
    ft.app(target=main, assets_dir=assets_path)
