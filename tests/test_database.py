import pytest
from src.database import Database

def test_database_connection():
    db = Database()
    assert db is not None
