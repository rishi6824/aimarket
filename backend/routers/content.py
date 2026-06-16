"""
Content Router — /api/content
"""
from fastapi import APIRouter, HTTPException
from models import ContentRequest, ContentResponse
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.content_agent import generate_content
from services import supabase_client

router = APIRouter(prefix="/api/content", tags=["Content"])


@router.post("/generate", response_model=ContentResponse)
async def generate(req: ContentRequest):
    """Generate AI marketing content."""
    try:
        result = await generate_content(req)
        # Save to Supabase
        try:
            await supabase_client.insert("content_items", {
                "type": req.content_type,
                "body": result.content,
                "platform": req.platform,
                "topic": req.topic,
                "word_count": result.word_count,
            })
        except Exception:
            pass  # Don't fail if DB save fails
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history(limit: int = 20):
    """Fetch recently generated content."""
    try:
        items = await supabase_client.select("content_items", limit=limit)
        return {"items": items, "total": len(items)}
    except Exception as e:
        return {"items": [], "total": 0, "error": str(e)}


@router.get("/types")
async def get_content_types():
    """List available content types."""
    return {
        "types": [
            {"id": "social_post", "label": "Social Post", "icon": "📱"},
            {"id": "blog", "label": "Blog Article", "icon": "📝"},
            {"id": "email", "label": "Email Campaign", "icon": "📧"},
            {"id": "ad_copy", "label": "Ad Copy", "icon": "🎯"},
            {"id": "hashtags", "label": "Hashtags", "icon": "#️⃣"},
            {"id": "subject_line", "label": "Email Subject Lines", "icon": "✉️"},
        ]
    }
