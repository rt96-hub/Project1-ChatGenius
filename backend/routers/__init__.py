from fastapi import APIRouter

from .auth import router as auth_router
from .users import router as users_router
from .channels import router as channels_router
from .messages import router as messages_router
from .reactions import router as reactions_router
from .files import router as files_router
from .search import router as search_router
from .websockets import router as websockets_router

# Export all routers for easy access
__all__ = [
    "auth_router",
    "users_router",
    "channels_router",
    "messages_router",
    "reactions_router",
    "files_router",
    "search_router",
    "websockets_router",
] 