from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import logging setup function (not the logger directly)
from app.core.logging import setup_logging
from app.core.rate_limiting import rate_limit_middleware
from app.database.database import init_db, close_db
from app.api.endpoints import health, auth, profiles, posts, comments, journals, mood, crisis, uploads, files, websocket, live_audio_rooms
# Add with other router includes
from app.api.endpoints import users
from app.api.endpoints import mood
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
app.include_router(websocket.router, prefix="/api/v1", tags=["websocket"])
app.include_router(live_audio_rooms.router, prefix="/api/v1/audio", tags=["live-audio-rooms"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(mood.router, prefix="/api/v1/mood", tags=["mood"])

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

# Enhanced Moderation Endpoints - Phase 3, Item 6
from app.api.endpoints.enhanced_moderation import router as enhanced_moderation_router
app.include_router(enhanced_moderation_router, prefix="/api/v1/moderation", tags=["enhanced-moderation"])

# Professional Directory Endpoints - Phase 3, Item 7
from app.api.endpoints.professional_directory import router as professional_directory_router
app.include_router(professional_directory_router, prefix="/api/v1/professional", tags=["professional-directory"])

# AI Personalization Endpoints - Phase 4, Item 1
from app.api.endpoints.ai_personalization import router as ai_personalization_router
from app.api.endpoints.advanced_safety_systems import router as advanced_safety_systems_router
app.include_router(advanced_safety_systems_router, prefix="/api/v1/safety", tags=["advanced-safety-systems"])
app.include_router(ai_personalization_router, prefix="/api/v1/ai", tags=["ai-personalization"])
from app.api.endpoints.enhanced_ux_community import router as enhanced_ux_community_router
app.include_router(enhanced_ux_community_router, prefix="/api/v1/ux-community", tags=["enhanced-ux-community"])
from app.api.endpoints.final_phase_features import router as final_phase_features_router
app.include_router(final_phase_features_router, prefix="/api/v1/final-phase", tags=["final-phase-features"])

# Import Phase 6 Missing Features
from app.api.endpoints.phase6_missing_features import router as phase6_missing_features_router

# Include Phase 6 Missing Features router
app.include_router(
    phase6_missing_features_router,
    prefix="/api/v1/phase6",
    tags=["Phase 6 - Missing Features"]
)

# Import Missing Phase 1 Features
from app.api.endpoints.missing_phase1_features import router as missing_phase1_features_router

# Include Missing Phase 1 Features router
app.include_router(
    missing_phase1_features_router,
    prefix="/api/v1",
    tags=["Phase 1 & 2 - Missing Features"]
)
