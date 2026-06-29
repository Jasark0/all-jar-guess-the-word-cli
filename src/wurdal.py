#!/usr/bin/env python
import asyncio
import login_service
import register_service
import board_service
from session_service import load_player_session
from utils import parse_args


async def main():
    # TODO: set up loading in user session and user session management in general
    args = parse_args()

    if args.command == "register":
        await register_service.register(args.player_name)
    elif args.command == "login":
        # TODO: hook up login function so that it calls created api
        await login_service.login(args.player_name)
    elif args.command == "guess":
        pass
    elif args.command == "board":
        await board_service.call_board_api(load_player_session())
    elif args.command == "leaderboard":
        pass


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
