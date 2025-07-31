"""
Domain models for Tic Tac Toe application.
"""

from enum import Enum
from datetime import datetime

class PlayerType(Enum):
    HUMAN = "human"
    AI = "ai"

class GameStatus(Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"

class MoveMarker(Enum):
    X = "X"
    O = "O"

# PUBLIC_INTERFACE
class User:
    """Represents a user in the system."""
    def __init__(self, username, password_hash, stats=None):
        self.username = username
        self.password_hash = password_hash
        self.stats = stats if stats else {"wins": 0, "losses": 0, "draws": 0}

# PUBLIC_INTERFACE
class GameSession:
    """Represents a game session."""
    def __init__(self, player_x, player_o=None, board=None, status=GameStatus.WAITING,
                 game_type="vs_player", moves=None, winner=None, started_at=None, finished_at=None):
        self.player_x = player_x  # username
        self.player_o = player_o  # username or "AI"
        self.status = status
        self.board = board if board else [["" for _ in range(3)] for _ in range(3)]
        self.moves = moves if moves else []
        self.game_type = game_type
        self.winner = winner
        self.started_at = started_at or datetime.utcnow()
        self.finished_at = finished_at

# PUBLIC_INTERFACE
class LeaderboardStats:
    """Represents stats for leaderboard."""
    def __init__(self, username, wins, games_played):
        self.username = username
        self.wins = wins
        self.games_played = games_played
