from fastapi import APIRouter

from app.routes import auth_route, group_route, gift_route

router = APIRouter()
router.include_router(auth_route.router)
router.include_router(group_route.router)
router.include_router(gift_route.router)