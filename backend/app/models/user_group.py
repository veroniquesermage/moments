from sqlalchemy import Column, ForeignKey, String, DateTime, CheckConstraint, Integer, Index
from sqlalchemy.orm import relationship

from app.database import Base
from app.utils.date_helper import now_paris


class UserGroup(Base):
    __tablename__ = "utilisateur_groupe"

    utilisateur_id = Column(Integer, ForeignKey("utilisateur.id"), primary_key=True)
    groupe_id = Column(Integer, ForeignKey("groupe.id"), primary_key=True)
    role = Column(String(50), nullable=False)
    surnom = Column(String(255), nullable=True)
    date_ajout = Column(DateTime(timezone=True), default=lambda: now_paris())

    __table_args__ = (
        Index("ix_user_group_user_groupe", "utilisateur_id", "groupe_id"),
        Index("ix_user_group_groupe", "groupe_id"),
        Index("ix_user_group_user", "utilisateur_id"),
        CheckConstraint("role IN ('ADMIN', 'MEMBRE', 'INVITE')", name="check_role"),
    )


    utilisateur = relationship("User", back_populates="groupes")
    groupe = relationship("Group", back_populates="utilisateurs")
