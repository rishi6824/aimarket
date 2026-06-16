"""
Campaigns Router — /api/campaigns
"""
from fastapi import APIRouter, HTTPException
from models import Campaign, CampaignUpdate
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services import supabase_client
import uuid

router = APIRouter(prefix="/api/campaigns", tags=["Campaigns"])


@router.get("/")
async def list_campaigns(limit: int = 50):
    try:
        campaigns = await supabase_client.select("campaigns", limit=limit)
        return {"campaigns": campaigns, "total": len(campaigns)}
    except Exception as e:
        return {"campaigns": [], "total": 0, "error": str(e)}


@router.post("/")
async def create_campaign(campaign: Campaign):
    try:
        data = campaign.model_dump()
        data["id"] = str(uuid.uuid4())
        data["status"] = "draft"
        data["impressions"] = 0
        data["clicks"] = 0
        data["conversions"] = 0
        data["spend"] = 0.0
        saved = await supabase_client.insert("campaigns", data)
        return {"campaign": saved, "message": "Campaign created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{campaign_id}")
async def update_campaign(campaign_id: str, update: CampaignUpdate):
    try:
        data = {k: v for k, v in update.model_dump().items() if v is not None}
        await supabase_client.update("campaigns", campaign_id, data)
        return {"campaign_id": campaign_id, "updated": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: str):
    try:
        await supabase_client.delete("campaigns", campaign_id)
        return {"campaign_id": campaign_id, "deleted": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
