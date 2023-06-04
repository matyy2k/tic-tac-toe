# tic-tac-toe

Gra oparta jest na REST API. Wykorzystuje sesje do tymczasowej identyfikacji gracza.

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
