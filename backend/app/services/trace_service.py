from sqlalchemy.orm import Session
from app.models.trace import Trace

class TraceService:

    @staticmethod
    def record_trace(db: Session, utilisateur: str, trace_type: str, message: str, payload: dict = None):
        trace = Trace(
            utilisateur= utilisateur,
            type=trace_type,
            message=message,
            payload=payload or {},
        )
        db.add(trace)
        db.commit()