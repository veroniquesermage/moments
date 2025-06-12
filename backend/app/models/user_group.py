from sqlalchemy import Column, ForeignKey, String, DateTime, CheckConstraint, Integer
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from app.database import Base


class UserGroup(Base):
    __tablename__ = "utilisateur_groupe"

    utilisateur_id = Column(Integer, ForeignKey("utilisateur.id"), primary_key=True)
    groupe_id = Column(Integer, ForeignKey("groupe.id"), primary_key=True)
    role = Column(String(50), nullable=False)
    surnom = Column(String(255), nullable=True)
    date_ajout = Column(DateTime, default=lambda: datetime.now(UTC))

    __table_args__ = (
        CheckConstraint("role IN ('ADMIN', 'MEMBRE', 'INVITE')", name="check_role"),
    )

    utilisateur = relationship("User", back_populates="groupes")
    groupe = relationship("Group", back_populates="utilisateurs")
