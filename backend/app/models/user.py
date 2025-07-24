from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.date_helper import now_paris


class User(Base):
    __tablename__ = "utilisateur"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    prenom = Column(String(255), nullable=False)
    nom = Column(String(255), nullable=True)
    google_id = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    date_creation = Column(DateTime(timezone=True), default=lambda:now_paris())
    is_compte_tiers = Column(Boolean, default=False, nullable=False)
    gere_par = Column(Integer, ForeignKey("utilisateur.id"), nullable=True)

    manager = relationship("User", remote_side=lambda: [User.id], backref="compte_tiers")
    groupes = relationship("UserGroup", back_populates="utilisateur")
    cadeaux_crees = relationship("Gift", foreign_keys="Gift.destinataire_id", back_populates="destinataire")
    cadeaux_reserves = relationship("Gift", foreign_keys="Gift.reserve_par_id", back_populates="reserve_par")
    gift_ideas_created = relationship("GiftIdeas", foreign_keys="GiftIdeas.proposee_par_id", back_populates="proposee_par")
    cadeaux_partages = relationship("GiftShared", foreign_keys="[GiftShared.preneur_id]",  back_populates="preneur")
    cadeaux_participes = relationship("GiftShared", foreign_keys="[GiftShared.participant_id]", back_populates="participant")
