from flask_smorest import Blueprint
from flask import request
from werkzeug.exceptions import NotFound, Conflict, Unauthorized
from datetime import datetime

from ..db import get_db
from ..models import GameStatus
from ..schemas import (
    GameStartVSPlayerSchema, GameStartVSAISchema, MakeMoveSchema, GameMoveResponseSchema,
    GameHistorySchema, LeaderboardSchema
)
from ..utils import check_winner, ai_make_random_move

blp = Blueprint("Game", "game", url_prefix="/api/game", description="Game management, play, and matchmaking routes")

# Helper: get user from session or header (for demo, use username in json header)
def get_current_username():
    # Accept 'X-Username' header for demo; in prod use session/cookie/JWT
    username = request.headers.get("X-Username")
    if not username:
        raise Unauthorized("Missing username authentication header.")
    return username

# PUBLIC_INTERFACE
@blp.route("/match/vs-player", methods=["POST"])
@blp.arguments(GameStartVSPlayerSchema)
@blp.response(201, GameMoveResponseSchema)
def match_vs_player(args):
    """
    Create/Join a new match against another player (wait matchmaking if no opponent).
    """
    db = get_db()
    username = get_current_username()
    opponent_username = args["opponent_username"]

    # Prevent self-matching
    if username == opponent_username:
        raise Conflict("You cannot match against yourself.")

    # Find or create pending game
    pending_game = db.games.find_one({
        "status": GameStatus.WAITING.value,
        "player_x": opponent_username,  # Other player issued matchmaking request earlier
        "player_o": None,
        "game_type": "vs_player"
    })
    if pending_game:
        # Join as player_o
        db.games.update_one(
            {"_id": pending_game["_id"]},
            {
                "$set": {
                    "player_o": username,
                    "status": GameStatus.IN_PROGRESS.value,
                    "started_at": datetime.utcnow()
                }
            }
        )
        pending_game = db.games.find_one({"_id": pending_game["_id"]})
    else:
        # Create new pending game as X, await O
        pending_game = {
            "player_x": username,
            "player_o": None,
            "status": GameStatus.WAITING.value,
            "game_type": "vs_player",
            "board": [["" for _ in range(3)] for _ in range(3)],
            "moves": [],
            "winner": None,
            "started_at": None,
            "finished_at": None
        }
        pending_game_id = db.games.insert_one(pending_game).inserted_id
        pending_game = db.games.find_one({"_id": pending_game_id})

    resp = {
        "board": pending_game["board"],
        "status": pending_game["status"],
        "winner": pending_game.get("winner"),
        "moves": pending_game.get("moves", []),
        "message": "Match found or awaiting opponent."
    }
    return resp

# PUBLIC_INTERFACE
@blp.route("/match/vs-ai", methods=["POST"])
@blp.arguments(GameStartVSAISchema)
@blp.response(201, GameMoveResponseSchema)
def match_vs_ai(args):
    """
    Start new game against AI (user is X, AI is O, user goes first).
    """
    db = get_db()
    username = get_current_username()
    game = {
        "player_x": username,
        "player_o": "AI",
        "status": GameStatus.IN_PROGRESS.value,
        "game_type": "vs_ai",
        "board": [["" for _ in range(3)] for _ in range(3)],
        "moves": [],
        "winner": None,
        "started_at": datetime.utcnow(),
        "finished_at": None
    }
    game_id = db.games.insert_one(game).inserted_id
    game = db.games.find_one({"_id": game_id})

    resp = {
        "board": game["board"],
        "status": game["status"],
        "winner": game.get("winner"),
        "moves": game.get("moves", []),
        "message": "Game started vs AI."
    }
    return resp

# PUBLIC_INTERFACE
@blp.route("/<game_id>/move", methods=["POST"])
@blp.arguments(MakeMoveSchema)
@blp.response(200, GameMoveResponseSchema)
def make_move(args, game_id):
    """
    Make a move in an ongoing game.
    """
    db = get_db()
    username = get_current_username()
    row, col = args["row"], args["col"]
    game = db.games.find_one({"_id": game_id})

    if not game or game["status"] not in [GameStatus.IN_PROGRESS.value, GameStatus.WAITING.value]:
        raise NotFound("Game not found or is finished.")

    # Determine player marker
    if username == game["player_x"]:
        marker = "X"
    elif username == game["player_o"]:
        marker = "O"
    else:
        raise Unauthorized("You are not a player in this game.")

    # Only allow move if status matches
    if game["status"] == GameStatus.WAITING.value:
        raise Conflict("Waiting for other player to join.")

    board = game["board"]
    if board[row][col]:
        raise Conflict("Cell already occupied.")

    board[row][col] = marker
    move = {"player": username, "marker": marker, "row": row, "col": col, "ts": datetime.utcnow().isoformat()}
    game["moves"].append(move)

    winner = check_winner(board)
    if winner:
        game["winner"] = username if winner == marker else game["player_o"] if marker == "X" else game["player_x"]
        game["status"] = GameStatus.FINISHED.value
        game["finished_at"] = datetime.utcnow()
        # Leaderboard: Update stats
        for player in (game["player_x"], game["player_o"]):
            if player and player != "AI":
                inc = {"wins": 1} if player == username and winner != "draw" else {}
                inc["games_played"] = 1
                db.users.update_one({"username": player}, {"$inc": inc}, upsert=True)
    else:
        # If vs AI, AI makes a move if game ongoing
        if game["game_type"] == "vs_ai" and marker == "X":
            ai_move = ai_make_random_move(board)
            if ai_move:
                ai_row, ai_col = ai_move
                board[ai_row][ai_col] = "O"
                move_ai = {"player": "AI", "marker": "O", "row": ai_row, "col": ai_col, "ts": datetime.utcnow().isoformat()}
                game["moves"].append(move_ai)
                winner = check_winner(board)
                if winner:
                    game["winner"] = game["player_x"] if winner == "X" else "AI" if winner == "O" else None
                    game["status"] = GameStatus.FINISHED.value
                    game["finished_at"] = datetime.utcnow()
    db.games.update_one({"_id": game["_id"]}, {"$set": {
        "board": board,
        "moves": game["moves"],
        "winner": game.get("winner"),
        "status": game.get("status"),
        "finished_at": game.get("finished_at")
    }})
    game = db.games.find_one({"_id": game["_id"]})

    resp = {
        "board": game["board"],
        "status": game["status"],
        "winner": game.get("winner"),
        "moves": game.get("moves", []),
        "message": (
            "Game finished." if game["status"] == GameStatus.FINISHED.value
            else "Move registered."
        )
    }
    return resp

# PUBLIC_INTERFACE
@blp.route("/history", methods=["GET"])
@blp.response(200, GameHistorySchema(many=True))
def get_game_history():
    """
    Fetch game history for the current user.
    """
    db = get_db()
    username = get_current_username()
    games = db.games.find({
        "$or": [
            {"player_x": username},
            {"player_o": username}
        ]
    }).sort("started_at", -1)
    result = []
    for g in games:
        res_item = {**g}
        res_item["game_id"] = str(g["_id"])
        del res_item["_id"]
        result.append(res_item)
    return result

# PUBLIC_INTERFACE
@blp.route("/leaderboard", methods=["GET"])
@blp.response(200, LeaderboardSchema(many=True))
def get_leaderboard():
    """
    Fetch top users by win count.
    """
    db = get_db()
    # MongoDB aggregation for leaderboard
    pipeline = [
        {"$project": {"username": 1, "wins": 1, "games_played": 1}},
        {"$sort": {"wins": -1, "games_played": 1}},
        {"$limit": 10}
    ]
    leaderboard = list(db.users.aggregate(pipeline))
    return leaderboard
