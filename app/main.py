from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.database import engine, Base
from app.utils.helper import ensure_directories_exist

# Import all models so SQLAlchemy registers them before create_all()
import app.models  # noqa: F401 — triggers __init__.py which imports all models

from app.routers import auth, complaint, officer, department, dashboard

# ─── Create all DB tables ────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ─── Ensure upload directories exist ─────────────────────────────────────────
ensure_directories_exist([
    "uploads/images",
    "uploads/pdf",
    "uploads/extracted_text",
])

# ─── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Grievance Management System API",
    description=(
        "A full-featured REST API for managing citizen grievances. "
        "Supports complaint submission with file upload, AI-based department routing, "
        "OCR text extraction, PDF report generation, and role-based access control."
    ),
    version="1.0.0",
    contact={
        "name": "Grievance Management Team",
    },
    license_info={
        "name": "MIT",
    },
)

# ─── CORS Middleware ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Mount Upload Files as Static ────────────────────────────────────────────
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ─── Register Routers ─────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(complaint.router)
app.include_router(officer.router)
app.include_router(department.router)
app.include_router(dashboard.router)


# ─── Root Health Check ────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "message": "✅ Grievance Management API is running",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}