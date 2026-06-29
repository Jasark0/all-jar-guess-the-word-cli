import os

os.environ.setdefault("DATABASE_URL", "sqlite://")

from fastapi.testclient import TestClient  # noqa: E402

from src.main import app  # noqa: E402
from src.core.database import create_database_session  # noqa: E402


class FakePlayer:
    def __init__(self, name):
        self.name = name


class FakeQuery:
    def __init__(self, players):
        self._players = players

    def all(self):
        return self._players


class FakeSession:
    def __init__(self, players):
        self._players = players

    def query(self, _model):
        return FakeQuery(self._players)


def _override_with(players):
    def _dependency():
        yield FakeSession(players)

    return _dependency


def test_leaderboard_endpoint_empty():
    app.dependency_overrides[create_database_session] = _override_with([])
    try:
        client = TestClient(app)
        response = client.get("/leaderboard")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"players": []}


def test_leaderboard_endpoint_returns_players_sorted_by_name():
    players = [FakePlayer("bob"), FakePlayer("amy")]
    app.dependency_overrides[create_database_session] = _override_with(players)
    try:
        client = TestClient(app)
        response = client.get("/leaderboard")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "players": [
            {"name": "amy", "wins": 0, "losses": 0, "averageGuesses": 0.0},
            {"name": "bob", "wins": 0, "losses": 0, "averageGuesses": 0.0},
        ]
    }
