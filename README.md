# tic-tac-toe

The game is based on the REST API. Uses sessions to temporarily identify a player.

# TECHNOLOGIES

- Python 3.10
- Flask
- SQLAlchemy
- Docker + Docker Compose
- PostgreSQL

# HOW TO RUN

`docker-compose up --build`

# DOCS

Available methods:

| URL                                  | GET            | POST             |
| ------------------------------------ | -------------- | ---------------- |
| http://127.0.0.1:5000/player/login   | NOT ALLOWED    | Login new player |
| http://127.0.0.1:5000/game/start     | NOT ALLOWED    | Start a game     |
| http://127.0.0.1:5000/game/move      | NOT ALLOWED    | Move             |
| http://127.0.0.1:5000/game/status    | Status game    | NOT ALLOWED      |
| http://127.0.0.1:5000/player/credits | Player credits | Add 10 credits   |
| http://127.0.0.1:5000/stats/date     | Stats for day  | NOT ALLOWED      |
