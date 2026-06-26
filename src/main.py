from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from . import db_models
from . import schemas
from .core.database import create_database_session

app = FastAPI()

@app.post("/players", response_model=schemas.Player, status_code=201)
def create_player(player: schemas.PlayersCreate, db: Session = Depends(create_database_session)):
    db_player = db_models.Player(name=player.name)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    
    return db_player