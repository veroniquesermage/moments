from fastapi import FastAPI, Depends, Request
from sqlalchemy import inspect
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.logger import logger
from app.database import get_db, engine
from app.middleware import DBSessionMiddleware
from app.router import router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # ou ["*"] pour tester
    allow_credentials=True,
    allow_methods=["*"],  # ou ["POST"]
    allow_headers=["*"],  # important pour Authorization, Content-Type, etc.
)

@app.middleware("http")
async def db_rollback_middleware(request: Request, call_next):
    # on attache la session
    async for session in get_db():
        request.state.db = session
        break
    try:
        response = await call_next(request)
    except SQLAlchemyError:
        # rollback si une erreur SQLAlchemy remonte
        await request.state.db.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": "Erreur interne de la base de données (rollback)."}
        )
    return response

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
