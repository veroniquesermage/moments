from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware

from app.database import get_db
from app.router import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # ou ["*"] pour tester
    allow_credentials=True,
    allow_methods=["*"],  # ou ["POST"]
    allow_headers=["*"],  # important pour Authorization, Content-Type, etc.
)
app.include_router(router)
@app.get("/")
async def read_root():
    return {"message": "🎁 Bienvenue sur Liste2Wish avec FastAPI"}
