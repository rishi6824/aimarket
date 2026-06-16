"""
Ads Agent — Generates ad creatives, A/B variants, and campaign insights
"""
import json
from services.groq_client import chat_completion
from models import AdCreativeRequest, AIInsightRequest


SYSTEM_PROMPT = """You are a performance marketing expert specializing in digital advertising.
You create high-converting ad creatives and provide data-driven campaign optimization insights.
Always produce multiple variants for A/B testing. Respond with valid JSON when requested."""


PLATFORM_SPECS = {
    "google": {
        "headline_limit": 30,
        "description_limit": 90,
        "note": "Google Search Ads — focus on keywords and search intent"
    },
    "meta": {
        "headline_limit": 40,
        "primary_text_limit": 125,
        "note": "Facebook/Instagram Ads — visual storytelling, emotion-driven"
    },
    "tiktok": {
        "headline_limit": 100,
        "note": "TikTok Ads — native, trend-aware, Gen Z friendly"
    },
    "linkedin": {
        "headline_limit": 70,
        "description_limit": 300,
        "note": "LinkedIn Ads — B2B focused, professional value proposition"
    },
}


async def generate_ad_creatives(req: AdCreativeRequest) -> dict:
    specs = PLATFORM_SPECS.get(req.platform, {})
    spec_note = specs.get("note", "")

    prompt = f"""Create {req.variants} unique ad creative variants for:

Product: {req.product}
Target Audience: {req.target_audience}
Platform: {req.platform.upper()} — {spec_note}
Campaign Objective: {req.objective}
{f'Budget: ${req.budget}' if req.budget else ''}

Platform specs: {json.dumps({k:v for k,v in specs.items() if k != 'note'}, indent=2)}

For each variant, provide:
- "variant": variant number (1, 2, 3...)
- "angle": the creative angle/hook used
- "headline": attention-grabbing headline
- "body": main ad copy/primary text
- "cta": call-to-action button text
- "emoji": 1-2 relevant emojis (for applicable platforms)
- "why_it_works": 1 sentence explaining the strategy

Respond ONLY with a JSON array of {req.variants} variant objects."""

    response = await chat_completion(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.85,
        max_tokens=1500,
    )

    try:
        start = response.find("[")
        end = response.rfind("]") + 1
        variants = json.loads(response[start:end])
    except Exception:
        variants = [{"variant": 1, "headline": response[:100], "body": response, "cta": "Learn More"}]

    return {
        "product": req.product,
        "platform": req.platform,
        "objective": req.objective,
        "variants": variants,
        "total_variants": len(variants),
    }


async def get_campaign_insights(req: AIInsightRequest) -> dict:
    ctr = (req.clicks / req.impressions * 100) if req.impressions > 0 else 0
    cvr = (req.conversions / req.clicks * 100) if req.clicks > 0 else 0
    cpa = (req.spend / req.conversions) if req.conversions > 0 else 0
    cpc = (req.spend / req.clicks) if req.clicks > 0 else 0

    prompt = f"""Analyze this marketing campaign performance and provide actionable insights:

Campaign: {req.campaign_name}
Impressions: {req.impressions:,}
Clicks: {req.clicks:,}
CTR: {ctr:.2f}%
Conversions: {req.conversions:,}
Conversion Rate: {cvr:.2f}%
Total Spend: ${req.spend:,.2f}
CPA: ${cpa:.2f}
CPC: ${cpc:.2f}

Provide:
1. Overall performance assessment (1 sentence)
2. Top 3 optimization recommendations (specific, actionable)
3. Budget reallocation suggestion
4. A/B test idea to improve CTR by 20%+
5. Risk flag (if any metric is critically off)

Be direct, specific, and data-driven. No fluff."""

    insights = await chat_completion(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.4,
        max_tokens=600,
    )

    return {
        "campaign": req.campaign_name,
        "metrics": {
            "impressions": req.impressions,
            "clicks": req.clicks,
            "ctr": round(ctr, 2),
            "conversions": req.conversions,
            "cvr": round(cvr, 2),
            "spend": req.spend,
            "cpa": round(cpa, 2),
            "cpc": round(cpc, 2),
        },
        "ai_insights": insights,
    }
