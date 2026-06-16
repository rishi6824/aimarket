"""
Leads Router — /api/leads
"""
from fastapi import APIRouter, HTTPException
from models import Lead, OutreachRequest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.lead_agent import score_lead, generate_outreach
from services import supabase_client
import uuid

router = APIRouter(prefix="/api/leads", tags=["Leads"])


@router.get("/")
async def list_leads(limit: int = 50):
    """List all leads."""
    try:
        leads = await supabase_client.select("leads", limit=limit)
        return {"leads": leads, "total": len(leads)}
    except Exception as e:
        return {"leads": [], "total": 0, "error": str(e)}


@router.post("/")
async def create_lead(lead: Lead):
    """Create a new lead."""
    try:
        lead_id = str(uuid.uuid4())
        data = lead.model_dump()
        data["id"] = lead_id
        data["status"] = "new"
        data["score"] = 0

        # Score the lead with AI
        try:
            scoring = await score_lead(lead, lead_id)
            data["score"] = scoring.score
            data["grade"] = scoring.grade
            data["ai_notes"] = scoring.reasoning
            data["recommended_action"] = scoring.recommended_action
        except Exception:
            data["grade"] = "C"

        saved = await supabase_client.insert("leads", data)
        return {"lead": saved, "message": "Lead created and scored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{lead_id}/score")
async def rescore_lead(lead_id: str):
    """Re-score an existing lead with AI."""
    try:
        leads = await supabase_client.select("leads", {"id": lead_id}, limit=1)
        if not leads:
            raise HTTPException(status_code=404, detail="Lead not found")
        lead_data = leads[0]
        lead = Lead(**{k: lead_data.get(k) for k in Lead.model_fields.keys() if k in lead_data})
        scoring = await score_lead(lead, lead_id)
        await supabase_client.update("leads", lead_id, {
            "score": scoring.score,
            "grade": scoring.grade,
            "ai_notes": scoring.reasoning,
            "recommended_action": scoring.recommended_action,
        })
        return scoring
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/outreach")
async def create_outreach(req: OutreachRequest):
    """Generate personalized outreach message for a lead."""
    try:
        result = await generate_outreach(req)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{lead_id}/status")
async def update_status(lead_id: str, status: str):
    """Update lead status."""
    valid = ["new", "contacted", "qualified", "proposal", "closed_won", "closed_lost"]
    if status not in valid:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {valid}")
    try:
        await supabase_client.update("leads", lead_id, {"status": status})
        return {"lead_id": lead_id, "status": status, "updated": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
