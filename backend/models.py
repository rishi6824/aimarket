"""
Marketing AI Agent Platform — Pydantic Models
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal
from datetime import datetime


# ─── Content ────────────────────────────────────────────────────────────────

class ContentRequest(BaseModel):
    content_type: Literal["social_post", "blog", "email", "ad_copy", "hashtags", "subject_line"]
    topic: str = Field(..., max_length=1000)
    tone: Literal["professional", "casual", "humorous", "urgent", "inspirational"] = "professional"
    platform: Optional[str] = None
    keywords: Optional[List[str]] = []
    max_length: Optional[int] = None

class ContentResponse(BaseModel):
    content: str
    content_type: str
    platform: Optional[str]
    word_count: int
    suggestions: List[str] = []


# ─── Leads ──────────────────────────────────────────────────────────────────

class Lead(BaseModel):
    name: str = Field(..., max_length=200)
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    notes: Optional[str] = None

class LeadScore(BaseModel):
    lead_id: str
    score: int
    grade: Literal["A", "B", "C", "D"]
    reasoning: str
    recommended_action: str

class OutreachRequest(BaseModel):
    lead_name: str
    lead_company: Optional[str] = None
    lead_industry: Optional[str] = None
    channel: Literal["email", "sms", "whatsapp"] = "email"
    product_name: str
    value_proposition: str
    send_via_twilio: bool = False
    phone_number: Optional[str] = None


# ─── Campaigns ──────────────────────────────────────────────────────────────

class Campaign(BaseModel):
    name: str
    channel: Literal["social", "email", "ads", "sms", "whatsapp"]
    budget: Optional[float] = None
    goal: Optional[str] = None
    target_audience: Optional[str] = None

class CampaignUpdate(BaseModel):
    status: Optional[Literal["active", "paused", "completed", "draft"]] = None
    budget: Optional[float] = None
    goal: Optional[str] = None


# ─── Analytics ──────────────────────────────────────────────────────────────

class AnalyticsEvent(BaseModel):
    campaign_id: str
    event: Literal["impression", "click", "conversion", "spend"]
    value: float = 1.0

class AIInsightRequest(BaseModel):
    campaign_name: str
    impressions: int
    clicks: int
    conversions: int
    spend: float


# ─── Chat ───────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., max_length=2000)
    session_id: Optional[str] = None
    history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    reply: str
    session_id: str
    suggestions: List[str] = []


# ─── Ads ────────────────────────────────────────────────────────────────────

class AdCreativeRequest(BaseModel):
    product: str = Field(..., max_length=500)
    target_audience: str = Field(..., max_length=500)
    platform: Literal["google", "meta", "tiktok", "linkedin"]
    budget: Optional[float] = None
    objective: Literal["awareness", "traffic", "conversions", "leads"] = "conversions"
    variants: int = 3


# ─── General ────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict

# ─── Stocks ─────────────────────────────────────────────────────────────────

class StockPredictionRequest(BaseModel):
    symbol: str = Field(..., max_length=10)

class StockPredictionResponse(BaseModel):
    symbol: str
    prediction: str
    current_price: float
    time_series_data: dict

class TradeRequest(BaseModel):
    symbol: str = Field(..., max_length=10)
    action: Literal["BUY", "SELL"]
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0)

class Holding(BaseModel):
    symbol: str
    quantity: float
    avg_price: float

class PortfolioResponse(BaseModel):
    balance: float
    holdings: List[Holding]
    total_value: float

class TradeResponse(BaseModel):
    status: str
    message: str
    trade: dict
