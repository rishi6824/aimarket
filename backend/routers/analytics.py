"""
Analytics Router — /api/analytics
"""
from fastapi import APIRouter, HTTPException
from models import AnalyticsEvent, AIInsightRequest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.chat_agent import get_campaign_insights
from services import supabase_client
import uuid

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.post("/event")
async def track_event(event: AnalyticsEvent):
    """Track a marketing analytics event."""
    try:
        data = event.model_dump()
        data["id"] = str(uuid.uuid4())
        saved = await supabase_client.insert("analytics_events", data)
        return {"tracked": True, "event": saved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/overview")
async def get_overview():
    """Get aggregated analytics overview."""
    try:
        events = await supabase_client.select("analytics_events", limit=1000)
        leads = await supabase_client.select("leads", limit=1000)
        campaigns = await supabase_client.select("campaigns", limit=100)
        content = await supabase_client.select("content_items", limit=100)

        # Aggregate stats
        total_impressions = sum(e.get("value", 0) for e in events if e.get("event") == "impression")
        total_clicks = sum(e.get("value", 0) for e in events if e.get("event") == "click")
        total_conversions = sum(e.get("value", 0) for e in events if e.get("event") == "conversion")
        total_spend = sum(e.get("value", 0) for e in events if e.get("event") == "spend")

        ctr = round((total_clicks / total_impressions * 100), 2) if total_impressions > 0 else 0
        cvr = round((total_conversions / total_clicks * 100), 2) if total_clicks > 0 else 0

        return {
            "kpis": {
                "total_leads": len(leads),
                "active_campaigns": sum(1 for c in campaigns if c.get("status") == "active"),
                "content_pieces": len(content),
                "total_impressions": int(total_impressions),
                "total_clicks": int(total_clicks),
                "total_conversions": int(total_conversions),
                "total_spend": round(total_spend, 2),
                "ctr": ctr,
                "cvr": cvr,
            },
            "recent_events": events[:20],
        }
    except Exception as e:
        # Return demo data when DB not yet set up
        return {
            "kpis": {
                "total_leads": 47,
                "active_campaigns": 5,
                "content_pieces": 128,
                "total_impressions": 284500,
                "total_clicks": 9823,
                "total_conversions": 312,
                "total_spend": 4250.00,
                "ctr": 3.45,
                "cvr": 3.18,
            },
            "recent_events": [],
            "note": "Demo data — connect Supabase to see real metrics",
        }


@router.post("/insights")
async def ai_campaign_insights(req: AIInsightRequest):
    """Get AI-powered campaign analysis and recommendations."""
    try:
        return await get_campaign_insights(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
