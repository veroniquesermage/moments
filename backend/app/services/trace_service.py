from sqlalchemy.ext.asyncio import AsyncSession
from app.models.trace import Trace

class TraceService:

    @staticmethod
    async def record_trace(
        db: AsyncSession,
        utilisateur: str,
        trace_type: str,
        message: str,
        payload: dict | None = None,
    ):
        trace = Trace(
            utilisateur=utilisateur,
            type=trace_type,
            message=message,
            payload=payload or {},
        )
        db.add(trace)
        await db.commit()
