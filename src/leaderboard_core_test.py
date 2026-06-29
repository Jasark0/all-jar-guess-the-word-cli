from leaderboard_core import build_leaderboard_data


class FakePlayer:
    def __init__(self, name, wins=0, losses=0, guess_count=0):
        self.name = name
        self.wins = wins
        self.losses = losses
        self.guess_count = guess_count


class BarePlayer:
    def __init__(self, name):
        self.name = name


def test_build_leaderboard_empty():
    assert build_leaderboard_data([]) == {"players": []}


def test_build_leaderboard_defaults_when_no_record_fields():
    result = build_leaderboard_data([BarePlayer("amy"), BarePlayer("bob")])

    assert result == {
        "players": [
            {"name": "amy", "wins": 0, "losses": 0, "averageGuesses": 0.0},
            {"name": "bob", "wins": 0, "losses": 0, "averageGuesses": 0.0},
        ]
    }


def test_build_leaderboard_sorted_by_wins_then_name():
    players = [
        FakePlayer("amy", wins=2),
        FakePlayer("zed", wins=5),
        FakePlayer("bob", wins=2),
    ]

    result = build_leaderboard_data(players)

    assert [p["name"] for p in result["players"]] == ["zed", "amy", "bob"]


def test_build_leaderboard_average_guesses_uses_wins_only():
    result = build_leaderboard_data([FakePlayer("amy", wins=2, guess_count=7)])

    assert result["players"][0]["averageGuesses"] == 3.5
