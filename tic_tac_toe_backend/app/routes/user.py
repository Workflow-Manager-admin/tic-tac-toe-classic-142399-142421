from flask_smorest import Blueprint
from werkzeug.exceptions import Conflict, Unauthorized

from ..db import get_db
from ..schemas import UserRegisterSchema, UserLoginSchema
from ..utils import hash_password, verify_password

blp = Blueprint("User", "user", url_prefix="/api/user", description="User authentication and management routes")

# PUBLIC_INTERFACE
@blp.route("/register", methods=["POST"])
@blp.arguments(UserRegisterSchema)
def register(args):
    """
    Register a new user. Username must be unique.
    """
    db = get_db()
    username = args["username"]
    password = args["password"]
    password_hash = hash_password(password)

    if db.users.find_one({"username": username}):
        raise Conflict("Username already exists.")
    db.users.insert_one({
        "username": username,
        "password_hash": password_hash,
        "wins": 0,
        "losses": 0,
        "draws": 0,
        "games_played": 0
    })
    return {"message": "User registered successfully."}

# PUBLIC_INTERFACE
@blp.route("/login", methods=["POST"])
@blp.arguments(UserLoginSchema)
def login(args):
    """
    User login. Expects username and password.
    """
    db = get_db()
    username = args["username"]
    password = args["password"]

    user = db.users.find_one({"username": username})
    if not user or not verify_password(password, user["password_hash"]):
        raise Unauthorized("Invalid username or password.")
    # For this example, login is stateless; in prod return JWT or session
    return {"message": "Login succeeded."}
