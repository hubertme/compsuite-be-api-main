from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.app_config import settings

def setup_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,  # Allows all origins
        allow_credentials=True,
        allow_methods=["POST", "OPTIONS", "GET", "PUT", "DELETE", "PATCH"],
        allow_headers=["Content-Type", "Content-Length", "Accept-Encoding", "X-CSRF-Token", "Authorization", "accept", "origin", "Cache-Control", "X-Requested-With"],
    )