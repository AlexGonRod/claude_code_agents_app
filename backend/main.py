# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from ocr import router as ocr_router
from drive import router as drive_router

app = FastAPI(title="Invoice Processing API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Astro dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth")
app.include_router(ocr_router, prefix="/ocr")
app.include_router(drive_router, prefix="/drive")

@app.get("/")
async def root():
    return {"message": "Invoice Processing API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}