from sqlalchemy import Column, String, Integer, Boolean, Numeric, Date, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship

from app.core.enum import GiftStatusEnum
from app.database import Base


class Gift(Base):
    __tablename__ = "cadeau"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nom = Column(String, nullable=False)
    description = Column(String, nullable=True)
    url = Column(String, nullable=True)
    quantite = Column(Integer, default=1)
    prix = Column(Numeric(10, 2), nullable=True)
    commentaire = Column(String, nullable=True)
    priorite = Column(Integer, nullable=False)
    utilisateur_id = Column(Integer, ForeignKey("utilisateur.id"), nullable=False)
    utilisateur = relationship("User", foreign_keys=[utilisateur_id], back_populates="cadeaux_crees")

    statut = Column(Enum(GiftStatusEnum), nullable=False)

    reserve_par_id = Column(Integer, ForeignKey("utilisateur.id"), nullable=True)
    reservePar = relationship("User", foreign_keys=[reserve_par_id], back_populates="cadeaux_reserves")

    dateReservation = Column(DateTime, nullable=True)
    lieuLivraison = Column(String, nullable=True)
    dateLivraison = Column(DateTime, nullable=True)
    recu = Column(Boolean, default=False)

    marque = Column(String, nullable=True)
    magasin = Column(String, nullable=True)
    prixReel = Column(Numeric(10, 2), nullable=True)
    fraisPort = Column(Numeric(10, 2), nullable=True)

    partages = relationship("GiftShared", back_populates="cadeau")



