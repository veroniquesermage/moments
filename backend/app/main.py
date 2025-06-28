from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.middleware.cors import CORSMiddleware

from app.core.logger import logger
from app.database import get_db
from app.router import router

app = FastAPI()
app.title = "Liste2Wish API"
app.description = "API pour l'application Liste2Wish"
app.version = "1.0.0"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # ou ["*"] pour tester
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def db_rollback_middleware(request: Request, call_next):
    # On récupère proprement le générateur async (get_db est un async generator)
    gen = get_db()

    # anext() = on récupère le premier yield du générateur
    request.state.db = await anext(gen)

    try:
        # On laisse FastAPI faire son taf avec la requête en cours
        response = await call_next(request)
        return response
    except SQLAlchemyError:
        # Si erreur SQLAlchemy → rollback de la session
        await request.state.db.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": "Erreur interne de la base de données (rollback)."}
        )
    finally:
        # Fermeture propre du générateur (équivaut à session.close())
        await gen.aclose()


# ==== Exception handlers globaux ====
@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.info(f"IntegrityError = {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": "Conflit en base de données : contrainte violée."}
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.info(f"SQLAlchemyError = {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erreur interne de la base de données."}
    )

app.include_router(router)
@app.get("/")
async def read_root():
    return {"message": "🎁 Bienvenue sur Liste2Wish avec FastAPI"}
