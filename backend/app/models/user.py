from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "utilisateur"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    google_id = Column(String(255), nullable=False)
