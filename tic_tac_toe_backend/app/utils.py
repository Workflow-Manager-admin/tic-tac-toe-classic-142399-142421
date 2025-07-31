"""
Utility functions for password hashing, game logic, and AI moves (simple random AI).
"""

import hashlib
import random

# PUBLIC_INTERFACE
def hash_password(password: str) -> str:
    """Hash a password using SHA-256 (for demo only, not production level)."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# PUBLIC_INTERFACE
def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a hash."""
    return hash_password(password) == password_hash

# PUBLIC_INTERFACE
def get_opponent_marker(marker: str) -> str:
    """Return the marker for the opponent."""
    return "O" if marker == "X" else "X"

# PUBLIC_INTERFACE
def check_winner(board):
    """Return 'X'/'O' if that player won, 'draw' if draw, or None if game ongoing."""
    # Rows/cols
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != "":
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != "":
            return board[0][i]
    # Diagonals
    if board[0][0] == board[1][1] == board[2][2] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != "":
        return board[0][2]
    # Draw
    if all(cell for row in board for cell in row):
        return "draw"
    return None

# PUBLIC_INTERFACE
def ai_make_random_move(board):
    """Return (row, col) index for AI's move by picking a free cell."""
    empty_cells = [(i, j) for i in range(3) for j in range(3) if not board[i][j]]
    return random.choice(empty_cells) if empty_cells else None
