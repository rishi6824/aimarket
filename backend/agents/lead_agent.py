"""
Lead Agent — Scores leads and generates personalized outreach
"""
import json
from services.groq_client import chat_completion, quick_complete
from services import twilio_client
from models import Lead, LeadScore, OutreachRequest


SYSTEM_PROMPT = """You are an elite B2B sales strategist and lead qualification expert.
You analyze leads with precision and craft personalized outreach that converts.
Always respond with valid JSON when asked, and compelling copy when writing outreach."""


async def score_lead(lead: Lead, lead_id: str) -> LeadScore:
    prompt = f"""Analyze this lead and score them 0-100 based on conversion potential.

Lead Data:
- Name: {lead.name}
- Company: {lead.company or 'Unknown'}
- Industry: {lead.industry or 'Unknown'}
- Email: {'✓ Provided' if lead.email else '✗ Missing'}
- Phone: {'✓ Provided' if lead.phone else '✗ Missing'}
- Notes: {lead.notes or 'None'}

Respond ONLY with valid JSON in this exact format:
{{
  "score": <integer 0-100>,
  "grade": "<A|B|C|D>",
  "reasoning": "<2-3 sentence explanation>",
  "recommended_action": "<specific next step>"
}}"""

    response = await chat_completion(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=400,
    )

    try:
        # Extract JSON from response
        start = response.find("{")
        end = response.rfind("}") + 1
        data = json.loads(response[start:end])
        return LeadScore(
            lead_id=lead_id,
            score=int(data.get("score", 50)),
            grade=data.get("grade", "C"),
            reasoning=data.get("reasoning", "Insufficient data for full scoring."),
            recommended_action=data.get("recommended_action", "Schedule discovery call."),
        )
    except Exception:
        return LeadScore(
            lead_id=lead_id,
            score=50,
            grade="C",
            reasoning="Could not parse AI scoring. Manual review recommended.",
            recommended_action="Follow up within 48 hours.",
        )


async def generate_outreach(req: OutreachRequest) -> dict:
    channel_styles = {
        "email": "formal, structured email with subject line and clear CTA",
        "sms": "casual, punchy SMS under 160 characters, no links unless necessary",
        "whatsapp": "conversational WhatsApp message, friendly tone, 2-3 short paragraphs",
    }

    style = channel_styles.get(req.channel, "professional message")

    prompt = f"""Write a highly personalized {style} for the following outreach:

Target: {req.lead_name} at {req.lead_company or 'their company'} ({req.lead_industry or 'their industry'})
Product/Service: {req.product_name}
Value Proposition: {req.value_proposition}
Channel: {req.channel.upper()}

The message should:
- Open with a personalized hook relevant to their industry
- Clearly state the value proposition in their terms
- Include a low-friction CTA (e.g., "15-minute call?")
- Feel human and non-salesy

{'For SMS: Keep under 160 chars strictly.' if req.channel == 'sms' else ''}"""

    message = await chat_completion(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.75,
        max_tokens=500,
    )

    result = {
        "message": message,
        "channel": req.channel,
        "recipient": req.lead_name,
        "sent": False,
        "twilio_result": None,
    }

    # Optionally send via Twilio
    if req.send_via_twilio and req.phone_number:
        if req.channel == "sms":
            twilio_result = twilio_client.send_sms(req.phone_number, message[:160])
        elif req.channel == "whatsapp":
            twilio_result = twilio_client.send_whatsapp(req.phone_number, message)
        else:
            twilio_result = {"error": "Twilio only supports SMS/WhatsApp channels"}

        result["sent"] = "error" not in twilio_result
        result["twilio_result"] = twilio_result

    return result
