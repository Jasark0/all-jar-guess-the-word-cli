def build_leaderboard_data(players) -> dict:
    """
    Build the leaderboard payload from stored player records.

    Win, loss and guess-count values are read defensively so this keeps
    working once those columns are added to the database. Until then they
    default to 0 and the average is 0.0.

    :param players: an iterable of player records exposing a ``name`` attribute
    :returns: a dict shaped as ``{"players": [...]}`` sorted by wins descending
    """
    rows = []
    for player in players:
        wins = getattr(player, "wins", 0) or 0
        losses = getattr(player, "losses", 0) or 0
        guess_count = getattr(player, "guess_count", 0) or 0
        average_guesses = round(guess_count / wins, 1) if wins > 0 else 0.0
        rows.append(
            {
                "name": player.name,
                "wins": wins,
                "losses": losses,
                "averageGuesses": average_guesses,
            }
        )
    rows.sort(key=lambda row: (-row["wins"], row["name"]))
    return {"players": rows}
