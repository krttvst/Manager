from fastapi import APIRouter
from app.api.v1 import auth, users, channels, posts, ai, stats

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(channels.router)
api_router.include_router(posts.router)
api_router.include_router(ai.router)
api_router.include_router(stats.router)
