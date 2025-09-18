from sqlalchemy import Column, String, Text, Integer, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.date_helper import now_paris


class Group(Base):
    __tablename__ = "groupe"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom_groupe = Column("name", String(255), nullable=False)
    description = Column(Text, nullable=True)

    utilisateurs = relationship("UserGroup", back_populates="groupe")
