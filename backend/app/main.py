from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import logging setup function (not the logger directly)
from app.core.logging import setup_logging
from app.core.rate_limiting import rate_limit_middleware
from app.database.database import init_db, close_db
from app.api.endpoints import health, auth, profiles, posts, comments, journals, mood, crisis, uploads, files

# Setup logging at module level
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Safe Zone API Server")
    await init_db()
    logger.info("Database connection established")
    yield
    # Shutdown
    await close_db()
    logger.info("Database connection closed")
    logger.info("Safe Zone API Server stopped")

# Create FastAPI application
app = FastAPI(
    title="Safe Zone API",
    description="Secure Mental Health Platform Backend",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if True else None,  # Always show docs for now
    redoc_url="/redoc" if True else None,
)

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# CORS middleware
from app.core.config import settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(profiles.router, prefix="/api/v1/profiles", tags=["profiles"])
app.include_router(posts.router, prefix="/api/v1/posts", tags=["posts"])

app.include_router(comments.router, prefix="/api/v1/comments", tags=["comments"])

app.include_router(journals.router, prefix="/api/v1/journals", tags=["journals"])

app.include_router(mood.router, prefix="/api/v1/mood", tags=["mood"])

app.include_router(crisis.router, prefix="/api/v1/crisis", tags=["crisis"])

app.include_router(uploads.router, prefix="/api/v1/uploads", tags=["uploads"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Safe Zone API",
        "version": "1.0.0",
        "environment": "development",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
    )
