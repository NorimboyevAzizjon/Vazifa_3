from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import auth_router, settings_router, debts_router, monitoring_router

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Qarzlarni hisoblash va monitoring qilish tizimi API (Debt Manager API)",
    description=(
        "Biror kishidan qarz olayotgan yoki qarz berayotgan holatlarni yozib boradigan, "
        "valyutalar va har bir odam bo'yicha alohida qarzlarni monitoring qiladigan tizimning Bekend API qismi."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(settings_router, prefix=settings.API_V1_STR)
app.include_router(debts_router, prefix=settings.API_V1_STR)
app.include_router(monitoring_router, prefix=settings.API_V1_STR)


import os
from fastapi.responses import FileResponse

# Static folder path
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

@app.get("/", tags=["UI App"], summary="Debt Manager vizual ilovasi")
def serve_ui():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "status": "healthy",
        "service": "Debt Manager API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health Check"])
def health_check():
    return {
        "status": "healthy",
        "service": "Debt Manager API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "auth": f"{settings.API_V1_STR}/auth",
            "settings": f"{settings.API_V1_STR}/settings/",
            "debts": f"{settings.API_V1_STR}/debts/",
            "monitoring": f"{settings.API_V1_STR}/monitoring/",
        },
    }
