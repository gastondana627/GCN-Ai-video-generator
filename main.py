import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from mangum import Mangum

load_dotenv()  # Load environment variables from your .env file

from media_rotation_client import (
    execute_image_generation_with_fallback,
    execute_video_generation_with_fallback
)

app = FastAPI(title="GCN AI Media Generator Hub")

# Enable CORS for local and codespace development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerationRequest(BaseModel):
    prompt: str

@app.post("/generate-image")
def generate_image(payload: GenerationRequest):
    """Routes image requests through the multi-provider failover client."""
    return execute_image_generation_with_fallback(payload.prompt)

@app.post("/generate-video")
def generate_video(payload: GenerationRequest):
    """Routes video requests through the multi-provider failover client."""
    return execute_video_generation_with_fallback(payload.prompt)

# Mount local static files (like your Kickflip.mp4, nugget.png, and index.html)
app.mount("/", StaticFiles(directory=".", html=True), name="static")

# Expose handler for Vercel Serverless Functions
handler = Mangum(app)