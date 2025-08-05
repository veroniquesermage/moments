from pathlib import Path
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, DateTime, Boolean, delete, or_
)
from sqlalchemy.orm import sessionmaker

# Chargement des variables d'environnement
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env.prod", override=True)
DB_URL = os.getenv("SYNC_DB_URL")
if not DB_URL:
    raise ValueError("SYNC_DB_URL est introuvable. Vérifie ton .env.")

engine = create_engine(DB_URL)
metadata = MetaData()

refresh_tokens = Table(
    "refresh_tokens",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer),
    Column("jti", String),
    Column("expires_at", DateTime(timezone=True)),
    Column("is_active", Boolean),
    Column("created_at", DateTime(timezone=True)),
)

Session = sessionmaker(bind=engine)


def main():
    print("Nettoyage des refresh tokens expirés ou inactifs...")
    session = Session()
    try:
        now = datetime.now(ZoneInfo("Europe/Paris"))
        delete_stmt = delete(refresh_tokens).where(
            or_(
                refresh_tokens.c.expires_at < now,
                refresh_tokens.c.is_active == False,
            )
        )
        result = session.execute(delete_stmt)
        session.commit()
        print(f"{result.rowcount} refresh token(s) supprimé(s).")
    finally:
        session.close()


if __name__ == "__main__":
    main()
