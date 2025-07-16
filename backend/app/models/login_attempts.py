from sqlalchemy import Column, Integer, String, DateTime

from app.database import Base
from app.utils.date_helper import now_paris


class LoginAttempts(Base):
    __tablename__ = "tentatives_connexions"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, index=True)
    tentatives = Column(Integer, nullable=False, default=0)
    derniere_tentative = Column(DateTime(timezone=True), nullable=False, default=now_paris)

    def increment(self):
        self.tentatives += 1
        self.derniere_tentative = now_paris()
