# Ronda Networking Guide

Ronda supports both Single Player (vs AI) and Multiplayer modes. This guide explains how to set up the game for LAN and Online play.

## Local Area Network (LAN) Play

To play with friends on the same Wi-Fi or local network:

### 1. Host the Server
The host should run the game in web mode. You can use the included automation script:

```bash
python3 scripts/serve_lan.py
```

This script will:
1. Detect your computer's local IP address (e.g., `192.168.1.15`).
2. Launch the Flet web server on port 8550.
3. Display a URL that your friends can enter in their browsers.

### 2. Join the Game
Friends can navigate to the URL displayed by the host (e.g., `http://192.168.1.15:8550`).
1. One player creates a "Multiplayer Room" (2-player or 4-player).
2. The host shares the 6-digit Room Code (e.g., `AB12CD`).
3. Other players enter the code and click "Join Room".

## Online Play (Advanced)

To play over the internet, you have two main options:

### Option A: Reverse Proxy (Recommended)
Use a tool like **ngrok** or **Cloudflare Tunnel** to expose your local port to the internet.

1. Start the game: `flet run --web --port 8550 ui/main.py`
2. Run ngrok: `ngrok http 8550`
3. Share the generated public URL (e.g., `https://random-id.ngrok-free.app`) with your friends.

### Option B: Port Forwarding
1. Configure your router to forward TCP traffic on port 8550 to your local machine's IP.
2. Share your public IP address with your friends: `http://[YOUR_PUBLIC_IP]:8550`.

## How Multiplayer Works

Ronda uses Flet's built-in **PubSub** (Publish-Subscribe) mechanism.
- **Room Isolation**: Each game session is isolated by a unique `room_id`.
- **State Synchronization**: When a move is made, the Host's browser calculates the new state and broadcasts it to all subscribers in that room.
- **Persistence**: Game rooms are stored in memory in the `active_rooms` dictionary. Note that restarting the server will clear all active sessions.

## Troubleshooting

- **Connection Refused**: Ensure the host's firewall allows traffic on the chosen port (default 8550).
- **Latency**: Since the "Host" client handles AI logic and state broadcasting, a stable connection for the host is critical.
- **Assets Not Loading**: Ensure the server is started from the root directory so it can find the `ui/assets/` folder.
