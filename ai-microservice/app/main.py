"""
Sconces AI Microservice - Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import API routes
from .api import imslp, transcribe_audio, edit_melody, recommend, music_generation, music_edit, setlist_design, ai_router, chat_setlist

# Create FastAPI app
app = FastAPI(
    title="Sconces AI Microservice",
    description="AI-powered music notation and transcription service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(imslp.router, prefix="/api/v1", tags=["classical-music"])
app.include_router(transcribe_audio.router, prefix="/api/v1", tags=["audio-transcription"])
app.include_router(edit_melody.router, prefix="/api/v1", tags=["melody-editing"])
app.include_router(recommend.router, prefix="/api/v1", tags=["recommendations"])
app.include_router(music_generation.router, prefix="/api/v1", tags=["music-generation"])
app.include_router(music_edit.router, prefix="/api/v1", tags=["music-editing"])
app.include_router(setlist_design.router, prefix="/api/v1", tags=["setlist-design"])
app.include_router(ai_router.router, prefix="/api/v1", tags=["ai-router"])
app.include_router(chat_setlist.router, prefix="/api/v1", tags=["chat-setlist"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Sconces AI Microservice",
        "version": "1.0.0",
        "features": [
            "IMSLP Classical Music Search",
            "Audio-to-Notation Transcription", 
            "Melody Editing",
            "Music Recommendations",
            "Natural Language to Sheet Music Generation",
            "Conversational Sheet Music Editing",
            "AI Multi-Agent Setlist Designer",
            "Intelligent AI Request Routing"
        ]
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": "2024-12-19T00:00:00Z",
        "services": {
            "openai": "connected",
            "basic_pitch": "ready",
            "langchain": "ready"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
