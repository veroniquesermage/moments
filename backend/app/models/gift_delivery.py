
from sqlalchemy import Integer, Column, ForeignKey, String, DateTime, Boolean, Numeric, Date
from sqlalchemy.orm import relationship

from app.database import Base


class GiftDelivery(Base):
    __tablename__ = 'gift_delivery'

    gift_id = Column(Integer, ForeignKey("cadeaux.id"), primary_key=True, index=True)
    gift = relationship("Gift", back_populates="gift_delivery", uselist=False)
    prix_reel = Column(Numeric(10, 2), nullable=True)
    lieu_livraison = Column(String, nullable=True)
    date_livraison = Column(Date, nullable=True)
    recu = Column(Boolean, default=False)  # 0: not received, 1: received