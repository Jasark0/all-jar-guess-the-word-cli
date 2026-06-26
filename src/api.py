from fastapi import FastAPI

from players.router import router as players_router

app = FastAPI()
app.include_router(players_router)
