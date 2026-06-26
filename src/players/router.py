import json
from pathlib import Path

from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/players", tags=["players"])

MOCK_DATA_PATH = Path(__file__).with_name("mock.json")


def access_denied_response() -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={"error": {"description": "Access denied"}},
    )


def player_not_found_response(player_id: int) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": {"description": f"Player {player_id} not found"}},
    )


def load_mock_players() -> list[dict[str, object]]:
    with MOCK_DATA_PATH.open() as mock_file:
        return json.load(mock_file)


def find_player_board(player_id: int) -> dict[str, object] | None:
    mock_players = load_mock_players()

    for player in mock_players:
        user = player.get("user", {})
        if user.get("id") == player_id:
            return player

    return None


def normalize_current_game(player_board: dict[str, object]) -> dict[str, object]:
    current = player_board.get("current")
    if not isinstance(current, dict):
        return player_board

    result = current.get("result")
    if not isinstance(result, dict):
        return player_board

    status = result.get("status")
    if status in {"won", "lost"}:
        current["guesses"] = []
        current["result"] = {"status": "in-progress", "word": None}

    return player_board


@router.get("/{id}/board")
async def get_player_board(
    id: int,
    authorization: str | None = Header(default=None),
    authentication: str | None = Header(default=None),
) -> dict[str, object]:
    token = authorization or authentication
    if token != f"Bearer {id}":
        return access_denied_response()

    player_board = find_player_board(id)
    if player_board is None:
        return player_not_found_response(id)

    return normalize_current_game(player_board)
