from fastapi import APIRouter
from app.api.v1 import auth, users, channels, posts, ai, stats, media, telegram

api_router = APIRouter(prefix="/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(channels.router)
api_router.include_router(posts.router)
api_router.include_router(ai.router)
api_router.include_router(stats.router)
api_router.include_router(media.router)
api_router.include_router(telegram.router)
