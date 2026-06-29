from fastapi import FastAPI
from .players.router import app as players_router
from .core.database import Base, engine


app = FastAPI()


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(players_router, prefix="/players", tags=["players"])
