import uuid
from functools import wraps

from flask import Blueprint, jsonify, request, session

app = Blueprint("app", __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not "player" in session:
            return jsonify({"message": "Player is not logged in."}), 401
        return f(*args, **kwargs)

    return decorated_function


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
    if result == "win":
        session["player"]["credits"] += 4
    elif result == "loss":
        session["player"]["credits"] -= 3


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


# Rozpoczyna nową grę
@app.route("/game/start", methods=["POST"])
@login_required
def start_game():
    if not has_sufficient_credits():
        return jsonify({"message": "Insufficient credits."}), 400

    session["board"] = init_board()

    return jsonify({"message": session["board"]})


@app.route("/game/status", methods=["GET"])
@login_required
def get_game_status():
    if "board" not in session:
        return jsonify({"message": "Game not started."}), 400

    return jsonify({"player": session["player"], "board": session["board"]})


@app.route("/player/credits", methods=["GET"])
@login_required
def get_player_credits():
    return jsonify(session["player"])


# Logowanie gracza - inicjalizacja sesji
@app.route("/player/login", methods=["POST"])
def login_player():
    name = request.json.get("name")

    if not name:
        return jsonify({"message": "Name is required."}), 400

    session["player"] = {
        "name": name,
        "credits": 10,
        "id": str(uuid.uuid4()),
    }

    return jsonify({"message": "Player logged in successfully."})


player, opponent = "X", "O"


# This function returns true if there are moves
# remaining on the board. It returns false if
# there are no moves left to play.
def is_moves_left(board):
    for i in range(3):
        for j in range(3):
            if board[i][j] == "_":
                return True
    return False


# This is the evaluation function as discussed
# in the previous article ( http://goo.gl/sJgv68 )
def evaluate(b):
    # Checking for Rows for X or O victory.
    for row in range(3):
        if b[row][0] == b[row][1] and b[row][1] == b[row][2]:
            if b[row][0] == player:
                return 10
            elif b[row][0] == opponent:
                return -10

    # Checking for Columns for X or O victory.
    for col in range(3):
        if b[0][col] == b[1][col] and b[1][col] == b[2][col]:
            if b[0][col] == player:
                return 10
            elif b[0][col] == opponent:
                return -10

    # Checking for Diagonals for X or O victory.
    if b[0][0] == b[1][1] and b[1][1] == b[2][2]:
        if b[0][0] == player:
            return 10
        elif b[0][0] == opponent:
            return -10

    if b[0][2] == b[1][1] and b[1][1] == b[2][0]:
        if b[0][2] == player:
            return 10
        elif b[0][2] == opponent:
            return -10

    # Else if none of them have won then return 0
    return 0


# This is the minimax function. It considers all
# the possible ways the game can go and returns
# the value of the board
def minimax(board, depth, isMax):
    score = evaluate(board)

    # If Maximizer has won the game return his/her
    # evaluated score
    if score == 10:
        return score

    # If Minimizer has won the game return his/her
    # evaluated score
    if score == -10:
        return score

    # If there are no more moves and no winner then
    # it is a tie
    if is_moves_left(board) == False:
        return 0

    # If this maximizer's move
    if isMax:
        best = -1000

        # Traverse all cells
        for i in range(3):
            for j in range(3):
                # Check if cell is empty
                if board[i][j] == "_":
                    # Make the move
                    board[i][j] = player

                    # Call minimax recursively and choose
                    # the maximum value
                    best = max(best, minimax(board, depth + 1, not isMax))

                    # Undo the move
                    board[i][j] = "_"
        return best

    # If this minimizer's move
    else:
        best = 1000

        # Traverse all cells
        for i in range(3):
            for j in range(3):
                # Check if cell is empty
                if board[i][j] == "_":
                    # Make the move
                    board[i][j] = opponent

                    # Call minimax recursively and choose
                    # the minimum value
                    best = min(best, minimax(board, depth + 1, not isMax))

                    # Undo the move
                    board[i][j] = "_"
        return best


# This will return the best possible move for the player
def find_best_move(board):
    print(board)
    bestVal = -1000
    bestMove = (-1, -1)

    for i in range(3):
        for j in range(3):
            if board[i][j] == "":
                board[i][j] = player

                moveVal = minimax(board, 0, False)

                board[i][j] = ""

                if moveVal > bestVal:
                    bestMove = (i, j)
                    bestVal = moveVal

    return bestMove
