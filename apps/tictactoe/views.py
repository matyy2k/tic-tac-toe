import uuid
from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Blueprint, jsonify, request, session
from sqlalchemy import desc, func

from db import session as db

from .models import UserStats
from .utils import find_best_move, login_required

app = Blueprint("app", __name__)


def init_board():
    return [["", "", ""], ["", "", ""], ["", "", ""]]


def has_sufficient_credits():
    return session["player"]["credits"] >= 3


def is_board_full(board):
    for row in board:
        if "" in row:
            return False
    return True


def check_rows(board, player):
    for row in board:
        if all(cell == player for cell in row):
            return True
    return False


def check_columns(board, player):
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    return False


def check_diagonals(board, player):
    if all(board[i][i] == player for i in range(3)):
        return True
    if all(board[i][2 - i] == player for i in range(3)):
        return True
    return False


def is_winner(board, player):
    return (
        check_rows(board, player)
        or check_columns(board, player)
        or check_diagonals(board, player)
    )


def update_game_state(result):
    player = (
        db.query(UserStats)
        .filter(UserStats.user_id == session["player"]["user_id"])
        .first()
    )

    if result == "win":
        session["player"]["credits"] += 4
        player.wins = 1 if not player.wins else player.wins + 1
        db.add(player)

    elif result == "loss":
        session["player"]["credits"] -= 3
        player.losses = 1 if not player.losses else player.losses + 1
        db.add(player)

    elif result == "draw":
        player.draws = 1 if not player.draws else player.draws + 1
        db.add(player)

    db.commit()


@app.route("/player/login", methods=["POST"])
def login_player():
    name = request.json.get("name")

    if not name:
        return jsonify({"message": "Name is required."}), 400

    user_id = str(uuid.uuid4())

    session["player"] = {
        "name": name,
        "credits": 10,
        "user_id": user_id,
    }

    obj = {"user_name": name, "user_id": user_id}

    user_stats = UserStats(**obj)
    db.add(user_stats)
    db.commit()

    return jsonify({"message": "Player logged in successfully."})


@app.route("/game/start", methods=["POST"])
@login_required
def start_game():
    if not has_sufficient_credits():
        end_time = datetime.now(tz=ZoneInfo(key="Europe/Warsaw"))
        player = (
            db.query(UserStats)
            .filter(UserStats.user_id == session["player"]["user_id"])
            .first()
        )
        player.start_game = end_time
        db.add(player)
        db.commit()
        return jsonify({"message": "Insufficient credits."}), 400

    player = (
        db.query(UserStats)
        .filter(UserStats.user_id == session["player"]["user_id"])
        .first()
    )

    start_time = datetime.now(tz=ZoneInfo(key="Europe/Warsaw"))
    if not player.start_game:
        player.start_game = start_time
        db.add(player)
        db.commit()

    session["board"] = init_board()

    return jsonify({"message": session["board"]})


@app.route("/game/move", methods=["POST"])
@login_required
def make_move():
    data = request.get_json()
    row = data.get("row")
    col = data.get("col")

    if row is None or col is None:
        return jsonify({"message": "Row and col parameters are required."}), 400

    board = session["board"]
    player = "X"

    if board[row][col] != "":
        return jsonify({"message": "Invalid move."}), 400

    board[row][col] = player

    if is_winner(board, player):
        update_game_state("win")
        return jsonify({"message": "You win!"})

    if is_board_full(board):
        update_game_state("draw")
        return jsonify({"message": "It's a draw!"})

    ai_row, ai_col = make_ai_move(board)
    board[ai_row][ai_col] = "O"

    if is_winner(board, "O"):
        update_game_state("loss")
        return jsonify({"message": "You lose!"})

    return jsonify({"message": "Move executed."}, {"board": session["board"]})


def make_ai_move(board):
    move = find_best_move(board)
    return move


@app.route("/game/status", methods=["GET"])
@login_required
def get_game_status():
    if "board" not in session:
        return jsonify({"message": "Game not started."}), 400

    return jsonify({"player": session["player"], "board": session["board"]})


@app.route("/player/credits", methods=["GET", "POST"])
@login_required
def get_player_credits():
    if request.method == "GET":
        return jsonify(session["player"])

    if request.method == "POST":
        if session["player"]["credits"] == 0:
            session["player"]["credits"] += 10
            return jsonify({"message": "Credits added successfully."})
        else:
            return jsonify({"message": "Player already has credits."})


@app.route("/stats/<date>", methods=["GET"])
def get_stats(date):
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD."}), 400

    stats = (
        db.query(
            func.sum(UserStats.wins),
            func.sum(UserStats.losses),
            func.sum(UserStats.draws),
            func.avg(UserStats.duration),
        )
        .filter(func.DATE(UserStats.created_at) == date)
        .first()
    )
    total_wins, total_losses, total_draws, average_duration = stats

    best_player = db.query(UserStats).order_by(desc(UserStats.wins)).first()

    return jsonify(
        {
            "date": date,
            "total_wins": total_wins or 0,
            "total_losses": total_losses or 0,
            "total_draws": total_draws or 0,
            "average_duration": average_duration or 0,
        },
        {
            "best_player": best_player.user_name,
        },
    )
