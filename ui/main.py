import flet as ft
import os
import sys
import asyncio
import json
import random
import string

# Add current directory to path so it can find engine/ronda/ai folders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ronda.logic import RondaGameState
    from ai.strategies import RondaAI
    from engine.core import Player, Card, Suit
except ImportError:
    # If running from inside ui/ folder
    sys.path.append(os.getcwd())
    from ronda.logic import RondaGameState
    from ai.strategies import RondaAI
    from engine.core import Player, Card, Suit

# Global store for active rooms
active_rooms = {}

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
        self.room_id = None
        self.my_player_index = 0
        self.is_multiplayer = False
        self.init_ui()

    def init_ui(self):
        self.page.clean()

        # Game Options
        target_score_dropdown = ft.Dropdown(
            label="Target Score",
            options=[
                ft.dropdown.Option("41"),
                ft.dropdown.Option("82"),
                ft.dropdown.Option("164"),
                ft.dropdown.Option("Custom"),
            ],
            value="41",
            width=150,
        )
        custom_score_input = ft.TextField(label="Custom Score", width=100, visible=False, value="41")

        def on_score_change(e):
            custom_score_input.visible = (target_score_dropdown.value == "Custom")
            self.page.update()

        target_score_dropdown.on_change = on_score_change

        oros_toggle = ft.Switch(label="Oros Scoring (Sum of Gold Cards)", value=False)
        ace_bonus_toggle = ft.Switch(label="Ace of Gold Bonus (+10 pts)", value=False)
        missa_last_toggle = ft.Switch(label="Allow Missa on Last Card", value=False)
        last_cap_toggle = ft.Switch(label="Last Capture Wins Table", value=True)

        player_count_radio = ft.RadioGroup(content=ft.Row([
            ft.Radio(value="2", label="2 Players (1v1)"),
            ft.Radio(value="4", label="4 Players (2v2 Teams)"),
        ], alignment=ft.MainAxisAlignment.CENTER), value="2")

        difficulty_radio = ft.RadioGroup(content=ft.Row([
            ft.Radio(value="Easy", label="Easy"),
            ft.Radio(value="Medium", label="Medium"),
            ft.Radio(value="Hard", label="Hard"),
        ], alignment=ft.MainAxisAlignment.CENTER), value="Medium")

        lobby_timer_slider = ft.Slider(min=0.5, max=10, divisions=19, label="{value} min", value=1)

        join_code_input = ft.TextField(label="Enter Room Code", width=200, text_align=ft.TextAlign.CENTER)

        def get_game_opts():
            score = int(custom_score_input.value) if target_score_dropdown.value == "Custom" else int(target_score_dropdown.value)
            return {
                "target_score": score,
                "oros_scoring": oros_toggle.value,
                "ace_of_gold_bonus": ace_bonus_toggle.value,
                "missa_last_card_allowed": missa_last_toggle.value,
                "last_capture_wins_table": last_cap_toggle.value,
                "difficulty": difficulty_radio.value
            }

        single_player_view = ft.Column([
            ft.Text("Single Player", size=24, weight="bold"),
            ft.Text("Number of Players", size=18),
            player_count_radio,
            ft.Text("AI Difficulty", size=18),
            difficulty_radio,
            ft.FilledButton("Start Single Player Game",
                            on_click=lambda _: self.start_game(int(player_count_radio.value), **get_game_opts()),
                            width=250),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        multiplayer_view = ft.Column([
            ft.Text("Multiplayer (Experimental)", size=24, weight="bold"),
            ft.Text("Opposite players are partners"),
            ft.Text("Lobby AI Timer (minutes)"),
            lobby_timer_slider,
            ft.Row([
                ft.FilledButton("Host 2-Player Room", on_click=lambda _: self.create_multiplayer_room(2, lobby_timer_slider.value, get_game_opts())),
                ft.FilledButton("Host 4-Player Room", on_click=lambda _: self.create_multiplayer_room(4, lobby_timer_slider.value, get_game_opts())),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=20, color="transparent"),
            ft.Text("Join Existing Game", size=18),
            join_code_input,
            ft.FilledButton("Join Room", on_click=lambda _: self.join_multiplayer_room(join_code_input.value)),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        # Basic layout without Tabs to avoid keyword errors
        self.page.add(
            ft.Container(
                content=ft.ListView([
                    ft.Column([
                        ft.Text("RONDA", size=80, weight="bold", color="white", italic=True),
                        ft.Text("Moroccan Card Game", size=20, color="white70"),
                        ft.Divider(height=20, color="transparent"),

                        ft.Container(
                            content=ft.Column([
                                ft.Text("Game Rules & Options", size=24, weight="bold"),
                                ft.Row([target_score_dropdown, custom_score_input], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([oros_toggle, ace_bonus_toggle], alignment=ft.MainAxisAlignment.CENTER),
                                ft.Row([missa_last_toggle, last_cap_toggle], alignment=ft.MainAxisAlignment.CENTER),
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=20, bgcolor="#1b5e20", border_radius=15
                        ),

                        ft.Divider(height=30),
                        single_player_view,
                        ft.Divider(height=40),
                        multiplayer_view,
                        ft.Divider(height=40),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                ]),
                expand=True, alignment=ft.Alignment(0, 0)
            )
        )

    def create_multiplayer_room(self, num_players, timer_mins, game_opts):
        self.room_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.is_multiplayer = True
        self.my_player_index = 1
        active_rooms[self.room_id] = {
            "num_players": num_players,
            "players": [None] * num_players,
            "state": None,
            "last_events": {},
            "game_opts": game_opts,
            "timer_seconds": int(timer_mins * 60),
            "start_time": asyncio.get_event_loop().time()
        }
        self.page.pubsub.subscribe_topic(f"room_{self.room_id}", self.on_multiplayer_message)
        self.join_multiplayer_room(self.room_id, is_host=True)
        self.page.run_task(self.lobby_timer_task)

    async def lobby_timer_task(self):
        while self.room_id in active_rooms and self.game is None:
            room = active_rooms[self.room_id]
            elapsed = asyncio.get_event_loop().time() - room["start_time"]
            remaining = max(0, room["timer_seconds"] - elapsed)

            if remaining <= 0:
                self.start_multiplayer_with_ai()
                break

            # Update lobby UI with timer (we'll need a reference to the label)
            # For now, just sleep
            await asyncio.sleep(1)

    def start_multiplayer_with_ai(self):
        if not self.room_id or self.game: return
        room = active_rooms.get(self.room_id)
        if not room: return

        # Fill remaining slots with AI
        for i in range(room["num_players"]):
            if room["players"][i] is None:
                difficulty = room["game_opts"].get("difficulty", "Medium")
                name = f"AI {i+1}"
                room["players"][i] = RondaAI(name, difficulty=difficulty)

        self.game = RondaGameState(room["players"],
                                   target_score=room["game_opts"]["target_score"],
                                   oros_scoring=room["game_opts"]["oros_scoring"],
                                   ace_of_gold_bonus=room["game_opts"]["ace_of_gold_bonus"],
                                   missa_last_card_allowed=room["game_opts"]["missa_last_card_allowed"],
                                   last_capture_wins_table=room["game_opts"]["last_capture_wins_table"])
        room["state"] = self.game
        self.broadcast_state()

    def join_multiplayer_room(self, room_id, is_host=False):
        if not room_id: return
        room_id = room_id.upper()
        if room_id not in active_rooms:
            self.page.snack_bar = ft.SnackBar(ft.Text("Room not found!"))
            self.page.snack_bar.open = True
            self.page.update()
            return
        self.room_id = room_id
        self.is_multiplayer = True
        room = active_rooms[room_id]
        if not is_host:
            for i in range(room["num_players"]):
                if room["players"][i] is None:
                    self.my_player_index = i
                    break
            if self.my_player_index is None:
                self.page.snack_bar = ft.SnackBar(ft.Text("Room is full!"))
                self.page.snack_bar.open = True
                self.page.update()
                return
            self.page.pubsub.subscribe_topic(f"room_{self.room_id}", self.on_multiplayer_message)
        self.page.clean()
        controls = [
            ft.Text(f"ROOM: {self.room_id}", size=40, weight="bold"),
            ft.Text("Waiting for players to join...", size=20),
            ft.ProgressRing(),
            ft.Text(f"Your Position: {self.get_pos_name(self.my_player_index)}"),
            ft.Text(f"Invite code: {self.room_id}", size=24, color="yellow", weight="bold"),
        ]
        if is_host:
            controls.append(ft.FilledButton("Start with AI Now", on_click=lambda _: self.start_multiplayer_with_ai()))

        self.page.add(
            ft.Container(
                content=ft.Column(controls, horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER),
                expand=True
            )
        )
        self.page.update()
        self.page.pubsub.send_all_on_topic(f"room_{self.room_id}", json.dumps({
            "type": "JOIN", "index": self.my_player_index, "name": f"Player {self.my_player_index + 1}"
        }))

    def get_pos_name(self, index):
        if index == self.my_player_index: return "Bottom (You)"
        # Assuming team mode (4 players)
        # 0 & 1 are partners, 2 & 3 are partners
        my_team = 0 if self.my_player_index in [0, 1] else 1
        partner_index = 1 if self.my_player_index == 0 else 0 if self.my_player_index == 1 else 3 if self.my_player_index == 2 else 2
        if index == partner_index: return "Top (Partner)"
        # Opponents
        return f"Side (Opponent {index+1})"

    def on_multiplayer_message(self, message):
        msg = json.loads(message)
        room = active_rooms.get(self.room_id)
        if not room: return
        if msg["type"] == "JOIN":
            room["players"][msg["index"]] = Player(msg["name"])
            if all(p is not None for p in room["players"]):
                if self.my_player_index == 1: # Host
                    self.game = RondaGameState(room["players"],
                                               target_score=room["game_opts"]["target_score"],
                                               oros_scoring=room["game_opts"]["oros_scoring"],
                                               ace_of_gold_bonus=room["game_opts"]["ace_of_gold_bonus"],
                                               missa_last_card_allowed=room["game_opts"]["missa_last_card_allowed"],
                                               last_capture_wins_table=room["game_opts"]["last_capture_wins_table"])
                    room["state"] = self.game
                    self.broadcast_state()
        elif msg["type"] == "UPDATE":
            self.game = room["state"]
            self.last_events = room["last_events"]
            self.render_game_board()
            if self.my_player_index == 1 and not self.game.current_player.is_human: # Host handles AI
                self.page.run_task(self.handle_cpu_move)
        elif msg["type"] == "STATE":
            self.game = room["state"]
            self.human_player = self.game.players[self.my_player_index]
            self.render_game_board()
            if self.my_player_index == 1 and not self.game.current_player.is_human: # Host handles AI
                self.page.run_task(self.handle_cpu_move)

    def broadcast_state(self):
        self.page.pubsub.send_all_on_topic(f"room_{self.room_id}", json.dumps({"type": "STATE"}))

    def start_game(self, num_players, **opts):
        self.is_multiplayer = False
        difficulty = opts.pop("difficulty", "Medium")
        self.human_player = Player("You")
        if num_players == 2:
            self.ai_players = [RondaAI("CPU", difficulty=difficulty)]
            players = [self.ai_players[0], self.human_player]
            self.my_player_index = 1
        else:
            self.ai_players = [
                RondaAI("CPU (Partner)", difficulty=difficulty),
                RondaAI("CPU (Left)", difficulty=difficulty),
                RondaAI("CPU (Right)", difficulty=difficulty)
            ]
            players = [self.ai_players[0], self.human_player, self.ai_players[1], self.ai_players[2]]
            self.my_player_index = 1
        self.game = RondaGameState(players, **opts)
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
                    border=ft.Border.all(2, "yellow") if is_turn else None
                )
            else:
                content_list.append(ft.Column(hand_images, spacing=5))
                return ft.Container(
                    content=ft.Column(content_list, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=10, bgcolor="#1b5e20" if not is_turn else "#2e7d32", border_radius=10,
                    border=ft.Border.all(2, "yellow") if is_turn else None
                )

        player_me = self.game.players[self.my_player_index]
        if len(self.game.players) == 4:
            # Partners sit opposite each other (0&1, 2&3)
            if self.my_player_index == 0:
                partner_idx, left_idx, right_idx = 1, 2, 3
            elif self.my_player_index == 1:
                partner_idx, left_idx, right_idx = 0, 2, 3
            elif self.my_player_index == 2:
                partner_idx, left_idx, right_idx = 3, 0, 1
            else: # 3
                partner_idx, left_idx, right_idx = 2, 0, 1
        else:
            partner_idx = 0 if self.my_player_index == 1 else 1
            left_idx, right_idx = None, None

        top_player = self.game.players[partner_idx]
        left_player = self.game.players[left_idx] if left_idx is not None else None
        right_player = self.game.players[right_idx] if right_idx is not None else None
        deck_stack = ft.Stack([
            ft.Image(src="/cards/card_back.jpeg", width=80, border_radius=5, opacity=0.9),
            ft.Container(content=ft.Text(str(len(self.game.deck)), size=18, weight="bold", color="white"), alignment=ft.Alignment(0, 0), width=80, height=114)
        ]) if len(self.game.deck) > 0 else ft.Container(width=80, height=114)
        table_row = ft.Row(
            controls=[ft.Container(content=ft.Image(src=self.get_card_image_path(c), width=100, border_radius=5), animate_scale=ft.Animation(300, ft.AnimationCurve.DECELERATE), scale=1.0) for c in self.game.table],
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
        is_my_turn = self.game.current_player == player_me
        status_color = "yellow" if is_my_turn else "white70"
        status_text = "YOUR TURN" if is_my_turn else f"{self.game.current_player.name}'S TURN"
        if self.game.game_over: status_text = "GAME OVER"
        def on_card_hover(e):
            e.control.scale = 1.1 if e.data == "true" else 1.0
            e.control.border = ft.Border.all(3, "yellow") if e.data == "true" else None
            e.control.update()
        human_hand = ft.Row(
            controls=[ft.Container(content=ft.Image(src=self.get_card_image_path(c), width=120, border_radius=8), on_click=lambda _, card=c: self.handle_human_move(card), border_radius=8, on_hover=on_card_hover, animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT), disabled=not is_my_turn) for c in player_me.hand],
            alignment=ft.MainAxisAlignment.CENTER, spacing=15
        )
        active_rules = []
        if self.game.oros_scoring: active_rules.append("Oros Scoring")
        if self.game.ace_of_gold_bonus: active_rules.append("Ace of Gold Bonus")
        if self.game.missa_last_card_allowed: active_rules.append("Missa Last Card")
        if not self.game.last_capture_wins_table: active_rules.append("No Last Capture Rule")
        rules_text = ft.Text(f"Rules: {', '.join(active_rules) if active_rules else 'Standard'} | Target: {self.game.target_score}", size=10, color="white54")

        central_area = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text(f"Room: {self.room_id}" if self.is_multiplayer else "Local", size=10, color="white54"), ft.VerticalDivider(), rules_text], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(content=ft.Text(" ".join(event_text), color="yellow", size=24, weight="bold", italic=True), height=30),
                ft.Row([deck_stack, ft.VerticalDivider(width=20, color="transparent"), ft.Container(content=table_row, expand=True)], alignment=ft.MainAxisAlignment.CENTER, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(content=ft.Text(status_text, color=status_color, size=16, weight="bold"), margin=ft.Margin(10, 10, 10, 10))
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True, alignment=ft.Alignment(0, 0), padding=15, bgcolor="#263238", border_radius=20, margin=ft.Margin(10, 10, 10, 10),
        )
        main_layout = ft.Column([
            player_panel(top_player),
            ft.Row([player_panel(left_player, "vertical") if left_player else ft.Container(width=100), central_area, player_panel(right_player, "vertical") if right_player else ft.Container(width=100)], expand=True),
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Column([ft.Text(f"Team {player_me.team_id + 1 if player_me.team_id is not None else ''} | Your Score: {player_me.score}", size=18, weight="bold", color="white"), ft.Text("Dealer" if self.game.players[self.game.dealer_index] == player_me else "", size=12, color="yellow")], spacing=1),
                        ft.Text(f"Captured: {len(player_me.captured_cards)}", size=12, color="white70")
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    human_hand
                ]),
                padding=10, bgcolor="#1b5e20" if not is_my_turn else "#2e7d32", border_radius=10, border=ft.Border.all(2, "yellow") if is_my_turn else None
            )
        ], expand=True, spacing=5)
        self.page.add(main_layout)
        self.page.update()

    def handle_human_move(self, card: Card):
        player_me = self.game.players[self.my_player_index]
        if self.game.current_player == player_me and not self.game.game_over:
            events = self.game.play_move(player_me, card)
            self.last_events = events
            if self.is_multiplayer:
                room = active_rooms[self.room_id]
                room["last_events"] = events
                self.page.pubsub.send_all_on_topic(f"room_{self.room_id}", json.dumps({"type": "UPDATE"}))
            else:
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
            if self.is_multiplayer:
                room = active_rooms[self.room_id]
                room["last_events"] = self.last_events
                self.page.pubsub.send_all_on_topic(f"room_{self.room_id}", json.dumps({"type": "UPDATE"}))
            else:
                self.render_game_board()
                if not self.game.current_player.is_human and not self.game.game_over:
                    self.page.run_task(self.handle_cpu_move)

def main(page: ft.Page):
    RondaApp(page)

if __name__ == "__main__":
    # Use absolute path for assets to ensure compatibility across execution modes
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_path = os.path.join(base_path, "assets")
    ft.app(target=main, assets_dir=assets_path)
