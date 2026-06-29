import httpx
import pytest

from leaderboard_service import (
    call_leaderboard_api,
    display_leaderboard,
    player_sort,
)


def test_player_sort_orders_by_wins_then_name(player_factory):
    players = [
        player_factory(name="bob", wins=2, in_progress=False),
        player_factory(name="amy", wins=2, in_progress=False),
        player_factory(name="zed", wins=1, in_progress=False),
    ]

    sorted_players = player_sort(players)

    assert [p.name for p in sorted_players] == ["amy", "bob", "zed"]


def test_display_leaderboard_empty_message(capsys):
    display_leaderboard([])
    out = capsys.readouterr().out

    assert "Leaderboard" in out
    assert "No players on the leaderboard yet. Be the first to register!" in out


def test_display_leaderboard_shows_player_stats(capsys):
    players = [
        {"name": "Alice", "wins": 4, "losses": 5, "averageGuesses": 2.4},
        {"name": "Tom", "wins": 3, "losses": 12, "averageGuesses": 4.2},
    ]

    display_leaderboard(players)
    out = capsys.readouterr().out

    assert "1. Alice - wins: 4, losses: 5, average guesses: 2.4" in out
    assert "2. Tom - wins: 3, losses: 12, average guesses: 4.2" in out
    assert out.index("Alice") < out.index("Tom")


def test_call_leaderboard_api_displays_players(monkeypatch, capsys):
    def fake_get(url):
        return httpx.Response(
            200,
            json={
                "players": [
                    {"name": "Alice", "wins": 4, "losses": 5, "averageGuesses": 2.4},
                    {"name": "Tom", "wins": 3, "losses": 12, "averageGuesses": 4.2},
                ]
            },
            request=httpx.Request("GET", url),
        )

    monkeypatch.setattr("leaderboard_service.httpx.get", fake_get)

    call_leaderboard_api()
    out = capsys.readouterr().out

    assert "1. Alice - wins: 4, losses: 5, average guesses: 2.4" in out
    assert "2. Tom - wins: 3, losses: 12, average guesses: 4.2" in out


def test_call_leaderboard_api_empty(monkeypatch, capsys):
    monkeypatch.setattr(
        "leaderboard_service.httpx.get",
        lambda url: httpx.Response(
            200, json={"players": []}, request=httpx.Request("GET", url)
        ),
    )

    call_leaderboard_api()
    out = capsys.readouterr().out

    assert "No players on the leaderboard yet. Be the first to register!" in out


def test_call_leaderboard_api_server_error(monkeypatch, capsys):
    monkeypatch.setattr(
        "leaderboard_service.httpx.get",
        lambda url: httpx.Response(
            500, text="Internal Server Error", request=httpx.Request("GET", url)
        ),
    )

    with pytest.raises(SystemExit):
        call_leaderboard_api()

    out = capsys.readouterr().out
    assert "Looks like the wurdal servers are taking a loss... try again later!" in out


def test_call_leaderboard_api_server_down(monkeypatch, capsys):
    def fake_get(url):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr("leaderboard_service.httpx.get", fake_get)

    with pytest.raises(SystemExit):
        call_leaderboard_api()

    out = capsys.readouterr().out
    assert "Looks like the wurdal servers are taking a loss... try again later!" in out

