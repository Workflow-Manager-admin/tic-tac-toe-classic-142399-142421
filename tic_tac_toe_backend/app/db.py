"""
MongoDB connection singleton for Tic Tac Toe backend.

Uses environment variables:
- MONGODB_URL
- MONGODB_DB
"""

import os
from pymongo import MongoClient

# PUBLIC_INTERFACE
def get_db():
    """Returns the MongoDB database client instance."""
    mongodb_url = os.environ.get('MONGODB_URL')
    mongodb_db = os.environ.get('MONGODB_DB')
    if not mongodb_url or not mongodb_db:
        raise RuntimeError("Environment variables MONGODB_URL and MONGODB_DB must be set.")
    client = MongoClient(mongodb_url)
    return client[mongodb_db]
