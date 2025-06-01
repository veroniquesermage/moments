from sqlalchemy import Column, Integer, ForeignKey, Boolean, Numeric, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.orm import relationship

from app.database import Base


class GiftShared(Base):
    __tablename__ = "cadeaux_partages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    preneur_id = Column(Integer, ForeignKey("utilisateur.id"), nullable=False)
    preneur = relationship(
        "User",
        foreign_keys=[preneur_id],
        back_populates="cadeaux_partages"
    )

    cadeau_id = Column(Integer, ForeignKey("cadeaux.id"), nullable=False)
    cadeau = relationship("Gift", back_populates="partages")

    participant_id = Column(Integer, ForeignKey("utilisateur.id"), nullable=False)
    participant = relationship(
        "User",
        foreign_keys=[participant_id],
        back_populates="cadeaux_participes"
    )

    montant = Column(Numeric(10, 2), nullable=False)
    rembourse = Column(Boolean, default=False)


    __table_args__ = (
        CheckConstraint('participant_id != preneur_id', name='check_pas_soi_meme'),
        UniqueConstraint('cadeau_id', 'participant_id', name='uix_cadeau_participant'),
        Index("ix_cadeaux_partages_cadeau_id", "cadeau_id"),
        Index("ix_cadeaux_partages_participant_id", "participant_id"),
    )
