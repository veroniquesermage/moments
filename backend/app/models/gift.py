from sqlalchemy import Column, Integer, String, Numeric, Enum, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship

from app.core.enum import GiftStatusEnum
from app.database import Base


class Gift(Base):
    __tablename__ = "cadeaux"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    destinataire_id = Column(Integer, ForeignKey("utilisateur.id"), nullable=False)
    destinataire = relationship("User", foreign_keys=[destinataire_id], back_populates="cadeaux_crees")
    nom = Column(String, nullable=False)
    description = Column(String, nullable=True)
    marque = Column(String, nullable=True)
    magasin = Column(String, nullable=True)
    url = Column(String, nullable=True)
    quantite = Column(Integer, default=1)
    prix = Column(Numeric(10, 2), nullable=True)
    frais_port = Column(Numeric(10, 2), nullable=True)
    commentaire = Column(String, nullable=True)
    priorite = Column(Integer, nullable=False)
    statut = Column(Enum(GiftStatusEnum), nullable=False)
    reserve_par_id = Column(Integer, ForeignKey("utilisateur.id"), nullable=True)
    reserve_par = relationship("User", foreign_keys=[reserve_par_id], back_populates="cadeaux_reserves")
    date_reservation = Column(DateTime(timezone=True), nullable=True)
    gift_idea_id = Column(Integer, ForeignKey("idees_cadeaux.id"), nullable=True)
    gift_idea = relationship("GiftIdeas", back_populates="gift", uselist=False)

    gift_delivery = relationship("GiftDelivery", back_populates="gift", uselist=False, cascade="all, delete-orphan")
    partages = relationship("GiftShared", back_populates="cadeau")

    __table_args__ = (
        Index("ix_gift_utilisateur", "destinataire_id"),
        Index("ix_gift_reserve_par", "reserve_par_id"),
        Index("ix_gift_statut", "statut"),
    )


