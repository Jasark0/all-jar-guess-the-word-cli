from sqlalchemy import Column, Integer, String
from .core.database import Base

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)