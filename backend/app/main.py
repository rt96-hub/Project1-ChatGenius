from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models
import os
from dotenv import load_dotenv
import logging
from .middleware import SearchRateLimitMiddleware, CacheControlMiddleware
from .embedding_service import embedding_service

# Import all routers
from .routers import (
    auth,
    users,
    channels,
    files,
    search,
    messages,
    reactions,
    websockets,
    ai
)

# Configure logging for errors only
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

load_dotenv()

# Load environment variables
MAX_CONNECTIONS_PER_USER = int(os.getenv('MAX_WEBSOCKET_CONNECTIONS_PER_USER', '5'))
MAX_TOTAL_CONNECTIONS = int(os.getenv('MAX_TOTAL_WEBSOCKET_CONNECTIONS', '1000'))
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
MAX_SEARCH_REQUESTS = int(os.getenv('MAX_SEARCH_REQUESTS_PER_MINUTE', '60'))
SEARCH_WINDOW_SIZE = int(os.getenv('SEARCH_RATE_LIMIT_WINDOW', '60'))

# Create the main app
app = FastAPI()

@app.get("/")
async def root():
    """
    Root endpoint that returns API status and information
    """
    return {
        "status": "online",
        "api_version": "1.0",
        "message": "ChatGenius API is running. Please use the appropriate endpoints for specific functionality."
    }

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        f"http://{os.getenv('EC2_PUBLIC_DNS')}:3000",
        f"https://{os.getenv('EC2_PUBLIC_DNS')}:3000",
        f"http://{os.getenv('EC2_PUBLIC_DNS')}",
        f"https://{os.getenv('EC2_PUBLIC_DNS')}"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting and caching middleware
app.add_middleware(
    SearchRateLimitMiddleware,
    window_size=SEARCH_WINDOW_SIZE,
    max_requests=MAX_SEARCH_REQUESTS
)
app.add_middleware(CacheControlMiddleware)

# Create database tables
# models.Base.metadata.create_all(bind=engine)

# Include all routers with appropriate prefixes
root_path = os.getenv('ROOT_PATH', '')
app.include_router(auth.router, prefix=f"{root_path}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{root_path}/users", tags=["users"])
app.include_router(channels.router, prefix=f"{root_path}/channels", tags=["channels"])
app.include_router(files.router, prefix=f"{root_path}/files", tags=["files"])
app.include_router(search.router, prefix=f"{root_path}/search", tags=["search"])
app.include_router(messages.router, prefix=f"{root_path}/messages", tags=["messages"])
app.include_router(reactions.router, prefix=f"{root_path}/reactions", tags=["reactions"])
app.include_router(websockets.router, prefix=root_path, tags=["websockets"])
app.include_router(ai.router, prefix=f"{root_path}/ai", tags=["ai"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
