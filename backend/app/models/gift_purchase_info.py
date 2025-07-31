
from sqlalchemy import Integer, Column, ForeignKey, String, Numeric
from sqlalchemy.orm import relationship

from app.database import Base


class GiftPurchaseInfo(Base):
    __tablename__ = 'detail_achat_cadeau'

    gift_id = Column(Integer, ForeignKey("cadeaux.id"), primary_key=True, index=True)
    gift = relationship("Gift", back_populates="gift_purchase_info", uselist=False)
    prix_reel = Column(Numeric(10, 2), nullable=True)
    commentaire = Column(String, nullable=True)
    compte_tiers_id = Column(Integer, ForeignKey("utilisateur.id"), nullable=True)
    compte_tiers = relationship("User", back_populates="cadeaux_pris_en_nom")