from sqlalchemy import Column, Integer, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship

from app.database import Base


class GiftIdeas(Base):
    __tablename__ = "idees_cadeaux"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    proposee_par_id = Column(Integer, ForeignKey("utilisateur.id"), nullable=False)
    proposee_par = relationship("User", foreign_keys=[proposee_par_id], back_populates="gift_ideas_created")
    visibilite = Column(Boolean, default=False)

    gift = relationship("Gift", back_populates="gift_idea", uselist=False)

    __table_args__ = (
        Index("ix_gift_ideas_propose", "proposee_par_id"),
    )
