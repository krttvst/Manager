from fastapi import APIRouter
from app.api.v1 import auth, users, channels, posts, stats, media, telegram, agent_settings

api_router = APIRouter(prefix="/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(channels.router)
api_router.include_router(posts.router)
api_router.include_router(stats.router)
api_router.include_router(media.router)
api_router.include_router(telegram.router)
api_router.include_router(agent_settings.router)
