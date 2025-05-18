from fastapi import APIRouter

from app.routes import auth_route

router = APIRouter()
router.include_router(auth_route.router)