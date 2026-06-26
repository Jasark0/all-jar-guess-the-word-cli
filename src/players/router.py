from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from ..core.database import create_database_session, Base

app = APIRouter()

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class PlayersRegister(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    name: str

class PlayerCreate(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: int
    name: str

@app.post("", response_model=PlayerCreate, status_code=201)
def create_player(
    player: PlayersRegister,
    db: Session = Depends(create_database_session)
):
    if not player.name.strip():
        raise HTTPException(status_code=422, detail={"error": {"description": "Name is required"}})
    
    player_name = player.name.strip().lower()
    
    existing_player = db.query(Player).filter(Player.name == player_name).first()
    if existing_player:
        raise HTTPException(status_code=422, detail={"error": {"description": "Name must be unique"}})

    db_player = Player(name=player_name)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)

    return db_player
