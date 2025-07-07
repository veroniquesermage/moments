from operator import and_
from pathlib import Path

from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, DateTime,
    JSON, update, null, delete
)
from sqlalchemy.orm import sessionmaker

# --- Chargement des variables d'environnement ---
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env.prod", override=True)
db_url = os.getenv("SYNC_DB_URL")
if not db_url:
    raise ValueError("SYNC_DB_URL est introuvable. Vérifie ton .env.")

# --- Connexion à la base ---
def get_engine():
    return create_engine(db_url)

# --- Définition des tables ---
def get_cadeaux_table(metadata):
    return Table(
        "cadeaux",
        metadata,
        Column("id", Integer),
        Column("statut", String),
        Column("reserve_par_id", Integer),
        Column("date_reservation", DateTime),
        Column("expiration_reservation", DateTime),
    )

def get_traces_table(metadata):
    return Table(
        "traces",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("utilisateur", String),
        Column("type", String),
        Column("message", String),
        Column("payload", JSON),
        Column("date", DateTime)
    )

def write_trace(session, traces, utilisateur, trace_type, message, payload=None):
    insert_stmt = traces.insert().values(
        date=datetime.now(ZoneInfo("Europe/Paris")),
        utilisateur=utilisateur,
        type=trace_type,
        message=message,
        payload=payload
    )
    session.execute(insert_stmt)
    session.commit()

# --- Logique principale ---
def main():
    print("Nettoyage des réservations expirées...")

    engine = get_engine()
    metadata = MetaData()
    cadeaux = get_cadeaux_table(metadata)
    traces = get_traces_table(metadata)

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        now = datetime.now(ZoneInfo("Europe/Paris"))

        # 1. Récupération des cadeaux expirés
        cadeaux_expired = session.execute(
            cadeaux.select().where(
                and_(
                    cadeaux.c.statut == 'RESERVE',
                    cadeaux.c.expiration_reservation < now
                )
            )
        ).fetchall()

        if cadeaux_expired:
            # Mise à jour des cadeaux expirés
            stmt = (
                update(cadeaux)
                .where(and_(
                    cadeaux.c.statut == 'RESERVE',
                    cadeaux.c.expiration_reservation < now
                ))
                .values(
                    statut='DISPONIBLE',
                    reserve_par_id=null(),
                    date_reservation=null(),
                    expiration_reservation=null()
                )
            )
            result = session.execute(stmt)
            session.commit()

            payload_data = [
                {
                    "id": row.id,
                    "statut": row.statut,
                    "reserve_par_id": row.reserve_par_id,
                    "date_reservation": row.date_reservation.isoformat() if row.date_reservation else None,
                    "expiration_reservation": row.expiration_reservation.isoformat() if row.expiration_reservation else None
                }
                for row in cadeaux_expired
            ]

            write_trace(
                session=session,
                traces=traces,
                utilisateur="SCRIPT_CLEANUP",
                trace_type="NETTOYAGE_RESERVATION",
                message=f"{len(payload_data)} réservation(s) expirée(s) nettoyée(s)",
                payload=payload_data
            )

            print(f"{result.rowcount} réservation(s) nettoyée(s).")
        else:
            print("Aucune réservation expirée à nettoyer.")

        # 2. Suppression des traces anciennes (>14 jours)
        cutoff_date = now - timedelta(days=14)
        delete_stmt = delete(traces).where(traces.c.date < cutoff_date)
        deleted = session.execute(delete_stmt)
        session.commit()

        print(f"{deleted.rowcount} trace(s) supprimée(s) de plus de 14 jours.")

        # Trace pour suppression des anciennes traces
        write_trace(
            session=session,
            traces=traces,
            utilisateur="SCRIPT_CLEANUP",
            trace_type="NETTOYAGE_TRACE",
            message=f"{deleted.rowcount} trace(s) ancienne(s) supprimée(s)"
        )

    except Exception as e:
        print(f"Erreur lors du nettoyage : {e}")
    finally:
        session.close()

# --- Exécution directe ---
if __name__ == "__main__":
    main()
