"""
Marshmallow schemas for API validation/serialization.
"""

from marshmallow import Schema, fields

# User registration/login
class UserRegisterSchema(Schema):
    username = fields.Str(required=True, description="Unique user name")
    password = fields.Str(required=True, description="Password (plaintext, will be hashed)")

class UserLoginSchema(Schema):
    username = fields.Str(required=True, description="Registered user name")
    password = fields.Str(required=True, description="User password")

# Game creation
class GameStartVSPlayerSchema(Schema):
    opponent_username = fields.Str(required=True, description="Username of opponent player")

class GameStartVSAISchema(Schema):
    ai_level = fields.Str(required=False, description="AI level (for future extension)")

class MakeMoveSchema(Schema):
    row = fields.Int(required=True, description="Board row index (0-2)")
    col = fields.Int(required=True, description="Board column index (0-2)")

class GameMoveResponseSchema(Schema):
    board = fields.List(fields.List(fields.Str()), description="Current game board")
    status = fields.Str(description="Game status: in_progress/finished")
    winner = fields.Str(allow_none=True, description="Winner username or 'draw' if applicable")
    moves = fields.List(fields.Dict(), description="All moves played in the game so far")
    message = fields.Str(description="Summary message")

# Game history
class GameHistorySchema(Schema):
    game_id = fields.Str()
    player_x = fields.Str()
    player_o = fields.Str()
    status = fields.Str()
    winner = fields.Str(allow_none=True)
    moves = fields.List(fields.Dict())
    started_at = fields.DateTime()
    finished_at = fields.DateTime(allow_none=True)

# Leaderboard stats
class LeaderboardSchema(Schema):
    username = fields.Str()
    wins = fields.Int()
    games_played = fields.Int()
