from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean

from app.database import Base
from app.utils.date_helper import now_paris


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("utilisateur.id"), nullable=False)
    jti = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=now_paris())
