"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from auth.routes import router as auth_router
from photo.routes import router as photo_router

app = FastAPI(
    title="PupMatch API",
    description="Backend API for PupMatch - A puppy dating application",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(photo_router)

# Mount static files for photo uploads (local storage)
# In production with S3/GCS, this won't be needed
import os
uploads_dir = "uploads"
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "0.1.0"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to PupMatch API"}
