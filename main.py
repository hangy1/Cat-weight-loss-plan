"""FastAPI application initialization"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.api.catfood_routes import router as catfood_router
from app.api.weight_routes import router as weight_router
from app.core.config import settings

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# Include API routes
app.include_router(router)
app.include_router(catfood_router, prefix="/api")
app.include_router(weight_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Actions to perform on application startup"""
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")


@app.on_event("shutdown")
async def shutdown_event():
    """Actions to perform on application shutdown"""
    print(f"Shutting down {settings.PROJECT_NAME}")
