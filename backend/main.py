"""
Marketing AI Agent Platform — FastAPI Main App
"""
import os
import sys
from pathlib import Path

# Ensure backend directory is in path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()

from routers import content, leads, campaigns, analytics, chat, stocks
from models import HealthResponse

app = FastAPI(
    title="Marketing AI Agent Platform",
    description="AI-powered marketing automation with Groq + OpenRouter + Supabase",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000", "http://0.0.0.0:8000", "https://marketing-agent.aria.vercel.app", "https://frontend-mu-sand-24.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Exception Handling ───────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    # Log exception internally here if needed
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(content.router)
app.include_router(leads.router)
app.include_router(campaigns.router)
app.include_router(analytics.router)
app.include_router(chat.router)
app.include_router(stocks.router)

# ─── Static Frontend ──────────────────────────────────────────────────────────
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_dashboard():
        return FileResponse(str(frontend_path / "index.html"))

# ─── Health ───────────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    from services import supabase_client, twilio_client

    groq_ok = bool(os.getenv("GROQ_API_KEY"))
    openrouter_ok = bool(os.getenv("OPENROUTER_API_KEY"))
    twilio_ok = twilio_client.health_check()

    try:
        supabase_ok = await supabase_client.health_check()
    except Exception:
        supabase_ok = False

    return HealthResponse(
        status="healthy" if (groq_ok or openrouter_ok) else "degraded",
        version="1.0.0",
        services={
            "groq": "✅ connected" if groq_ok else "❌ missing key",
            "openrouter": "✅ connected" if openrouter_ok else "❌ missing key",
            "supabase": "✅ connected" if supabase_ok else "⚠️ check connection",
            "twilio": "✅ configured" if twilio_ok else "⚠️ SID/Token mismatch",
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=os.getenv("DEBUG", "true").lower() == "true",
    )
