from enum import Enum

from fastapi import APIRouter, Header, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, relationship
from sqlalchemy import Column, Enum as SAEnum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from ..core.database import create_database_session, Base

app = APIRouter()


class MatchValue(str, Enum):
    full = "full"
    partial = "partial"
    none = "none"


class GameStatus(str, Enum):
    in_progress = "in-progress"
    won = "won"
    lost = "lost"


class CurrentGame(Base):
    __tablename__ = "current_games"

    id = Column(Integer, primary_key=True)
    secret_word = Column(String, nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, unique=True)

    guesses = relationship(
        "GameGuess", back_populates="current_game", cascade="all, delete-orphan"
    )
    result = relationship(
        "GameResult", back_populates="current_game", uselist=False, cascade="all, delete-orphan"
    )
    player = relationship("Player", back_populates="current_game", uselist=False)


class GameGuess(Base):
    __tablename__ = "game_guesses"

    id = Column(Integer, primary_key=True)
    current_game_id = Column(Integer, ForeignKey("current_games.id"), nullable=False)

    current_game = relationship("CurrentGame", back_populates="guesses")
    letters = relationship(
        "GuessLetter", back_populates="guess", cascade="all, delete-orphan"
    )


class GuessLetter(Base):
    __tablename__ = "guess_letters"

    id = Column(Integer, primary_key=True)
    guess_id = Column(Integer, ForeignKey("game_guesses.id"), nullable=False)
    letter = Column(String(1), nullable=False)
    match = Column(SAEnum(MatchValue), nullable=False)

    guess = relationship("GameGuess", back_populates="letters")


class GameResult(Base):
    __tablename__ = "game_results"

    id = Column(Integer, primary_key=True)
    current_game_id = Column(Integer, ForeignKey("current_games.id"), nullable=False, unique=True)
    status = Column(SAEnum(GameStatus), nullable=False)
    word = Column(String, nullable=True)

    current_game = relationship("CurrentGame", back_populates="result")

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    seen_words = Column(ARRAY(String), nullable=False, default=list)

    current_game = relationship("CurrentGame", back_populates="player", uselist=False)
    

class PlayerRegister(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    name: str

class PlayerRead(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: int
    name: str
    current_game: "CurrentGameRead | None" = None


class PlayerIdentityRead(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: int
    name: str
    seen_words: list[str]


class LetterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    letter: str
    match: MatchValue


class GuessRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    letters: list[LetterRead]


class GameResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: GameStatus
    word: str | None


class CurrentGameRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)

    secret_word: str
    guesses: list[GuessRead]
    result: GameResultRead | None = None


PlayerRead.model_rebuild()

@app.post("", response_model=PlayerIdentityRead, status_code=201)
def create_player(
    player: PlayerRegister,
    db: Session = Depends(create_database_session)
):
    if not player.name.strip():
        raise HTTPException(status_code=422, detail={"error": {"description": "Name is required"}})
    
    player_name = player.name.replace(" ", "").lower()
    
    existing_player = db.query(Player).filter(Player.name == player_name).first()
    if existing_player:
        raise HTTPException(status_code=422, detail={"error": {"description": "Name must be unique"}})

    db_player = Player(name=player_name, seen_words=[])
    db.add(db_player)
    db.commit()
    db.refresh(db_player)

    return db_player

@app.post("/sessions", response_model=PlayerIdentityRead, status_code=200)
def get_player_by_id(
    player: PlayerRegister,
    db: Session = Depends(create_database_session)
):
    if not player.name.strip():
        raise HTTPException(status_code=422, detail={"error": {"description": "Name is required"}})
    
    player_name = player.name.replace(" ", "").lower()
    
    existing_player = db.query(Player).filter(Player.name == player_name).first()
    if not existing_player:
        raise HTTPException(status_code=422, detail={"error": {"description": "Player not found"}})
    
    return existing_player


def access_denied_response() -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content={"error": {"description": "Access denied"}},
    )


@app.get("/{id}/board")
async def get_player_board(
    id: int,
    authorization: str | None = Header(default=None),
    db: Session = Depends(create_database_session)
) -> dict[str, object]:
    token = authorization
    if token != f"Bearer {id}":
        return access_denied_response()

    existing_player = db.query(Player).filter(Player.id == id).first()

    if not existing_player:
        raise HTTPException(status_code=422, detail={"error": {"description": "Player not found"}})

    current_game = existing_player.current_game
    if current_game is None:
        


        return {
            "user": {"id": existing_player.id, "name": existing_player.name},
            "current": None,
        }

    return {
        "user": {"id": existing_player.id, "name": existing_player.name},
        "current": CurrentGameRead.model_validate(current_game).model_dump(by_alias=True),
    }
