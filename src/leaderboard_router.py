from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .core.database import create_database_session
from .leaderboard_core import build_leaderboard_data
from .players.router import Player

router = APIRouter()


@router.get("/leaderboard")
def get_leaderboard(db: Session = Depends(create_database_session)):
    players = db.query(Player).all()
    return build_leaderboard_data(players)
