from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.orm import relationship
from app.database import Base


class Group(Base):
    __tablename__ = "groupe"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom_groupe = Column("name", String(255), nullable=False)
    description = Column(Text, nullable=False)
    code = Column(String(10), unique=True, nullable=False)

    utilisateurs = relationship("UserGroup", back_populates="groupe")
