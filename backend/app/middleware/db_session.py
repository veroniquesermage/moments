from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class DBSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # on récupère la session injectée par get_db
        # obligatoire de l’avoir stockée dans request.state
        db: AsyncSession = request.state.db
        try:
            response = await call_next(request)
        except SQLAlchemyError as exc:
            # rollback automatique
            await db.rollback()
            return JSONResponse(
                status_code=500,
                content={"detail": "Erreur interne de la base de données (rollback effectué)."}
            )
        return response