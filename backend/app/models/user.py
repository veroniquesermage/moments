from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base

class User(Base):
    __tablename__ = "utilisateur"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    google_id = Column(String(255), nullable=False)

    groupes = relationship("UserGroup", back_populates="utilisateur")
    cadeaux_crees = relationship("Gift", foreign_keys="Gift.utilisateur_id", back_populates="utilisateur")
    cadeaux_reserves = relationship("Gift", foreign_keys="Gift.reserve_par_id", back_populates="reservePar")

    cadeaux_partages = relationship(
        "GiftShared",
        foreign_keys="[GiftShared.preneur_id]",
        back_populates="preneur"
    )

    cadeaux_participes = relationship(
        "GiftShared",
        foreign_keys="[GiftShared.participant_id]",
        back_populates="participant"
    )
