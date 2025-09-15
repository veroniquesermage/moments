from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from app.utils.date_helper import now_paris


class Invitation(Base):
    __tablename__ = "invitation"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    groupe_id = Column(Integer, ForeignKey("groupe.id"), nullable=False)
    envoye_par_id = Column(Integer, ForeignKey("utilisateur.id"), nullable=False)
    date_envoi = Column(DateTime, nullable=False)

    # Relations
    groupe = relationship("Group", backref="invitations")
    envoye_par = relationship("User", backref="invitations_envoyees")