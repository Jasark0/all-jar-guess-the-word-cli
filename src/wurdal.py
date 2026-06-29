#!/usr/bin/env python
import asyncio
import login_service
import register_service
import guess_service
import board_service
import logout_service

from session_service import load_player_session 
from utils import load_players, parse_args

async def main():
    # TODO: set up loading in user session and user session management in general
    args = parse_args()

    if args.command == "register":
        await register_service.register(args.player_name)
    elif args.command == "login":
        await login_service.login(args.player_name)
    elif args.command == "guess":
        pass
    elif args.command == "board":
        await board_service.call_board_api(load_player_session())
    elif args.command == "leaderboard":
        pass
    elif args.command == "logout":
        await logout_service.logout()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
