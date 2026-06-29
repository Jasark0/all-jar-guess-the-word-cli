import sys

import httpx

from models import Player

LEADERBOARD_URL = "http://localhost:8000/leaderboard"


def get_leaderboard_data(registered_players: list[Player]) -> dict:
    sorted_players = player_sort(registered_players)
    players = []
    for player in sorted_players:
        wins = player.record.wins
        average_guesses = (
            round(player.record.guess_count / wins, 1) if wins > 0 else 0.0
        )
        players.append(
            {
                "name": player.name,
                "wins": wins,
                "losses": player.record.losses,
                "averageGuesses": average_guesses,
            }
        )
    return {"players": players}


def call_leaderboard_api():
    """
    Calls GET /leaderboard and prints the leaderboard for the CLI user.
    """
    try:
        response = httpx.get(LEADERBOARD_URL)
        response.raise_for_status()
        players = response.json().get("players", [])
    except (httpx.HTTPError, ValueError):
        print("Looks like the wurdal servers are taking a loss... try again later!")
        sys.exit(1)

    display_leaderboard(players)


def display_leaderboard(players: list[dict]):
    """
    Prints the leaderboard from API player data already sorted by wins.

    :param players: a list of player dicts with name, wins, losses and
        averageGuesses keys *
    """
    print("Leaderboard\n")
    if len(players) == 0:
        print("No players on the leaderboard yet. Be the first to register!")
        return

    for i, player in enumerate(players):
        print(
            f"{i + 1}. {player['name']} - "
            f"wins: {player['wins']}, "
            f"losses: {player['losses']}, "
            f"average guesses: {player['averageGuesses']}"
        )


def player_sort(registered_players: list[Player]):
    """
    Sorts the list of Player objects by wins in descending order.

    :param registered_players: a list of Player objects *
    :returns: sorted list of Player objects
    """
    return sorted(registered_players, key=lambda x: (-x.record.wins, x.name))
