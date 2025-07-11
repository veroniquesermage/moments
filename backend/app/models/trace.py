from sqlalchemy import Column, DateTime, String, JSON, Integer

from app.database import Base
from app.utils.date_helper import now_paris


class Trace(Base):
    __tablename__ = "traces"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(DateTime(timezone=True), default=lambda: now_paris())
    utilisateur = Column(String, nullable=False)
    type = Column(String, nullable=False)  # ex: "NETTOYAGE_RESERVATION"
    message = Column(String, nullable=True)  # description lisible
    payload = Column(JSON, nullable=True)  # ce que tu veux logguer