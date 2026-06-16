"""
Marketing AI Chat Agent — Conversational assistant for marketing tasks
"""
import uuid
from services.groq_client import chat_completion
from models import ChatRequest, ChatResponse


MARKETING_SYSTEM_PROMPT = """You are ARIA — Advanced Revenue Intelligence Agent — an elite AI marketing strategist.

You help businesses with:
- Content strategy and copywriting
- Campaign planning and optimization
- Lead generation and nurturing
- Ad creative and targeting
- Social media strategy
- Email marketing
- SEO and growth hacking
- Analytics interpretation
- Competitor analysis

Your personality:
- Confident and direct — you give real answers, not vague platitudes
- Data-driven — back recommendations with metrics when possible
- Proactive — always suggest next steps
- Concise — be thorough but never rambling

When asked about specific tools, always suggest 2-3 concrete options.
Always end responses with a quick follow-up question or suggested next action."""


async def chat_with_agent(req: ChatRequest) -> ChatResponse:
    session_id = req.session_id or str(uuid.uuid4())

    # Build message history
    messages = []
    if req.history:
        for msg in req.history[-10:]:  # Keep last 10 messages for context
            messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": req.message})

    reply = await chat_completion(
        messages=messages,
        system_prompt=MARKETING_SYSTEM_PROMPT,
        temperature=0.75,
        max_tokens=800,
    )

    # Generate contextual quick-reply suggestions
    suggestions_prompt = f"""Based on this marketing conversation, suggest 3 short follow-up questions the user might want to ask next.
User asked: "{req.message}"
AI replied about: {reply[:200]}

Return exactly 3 suggestions, one per line, as short questions (max 8 words each). No numbering or bullets."""

    try:
        suggestions_raw = await chat_completion(
            messages=[{"role": "user", "content": suggestions_prompt}],
            system_prompt="You generate concise follow-up question suggestions.",
            temperature=0.6,
            max_tokens=100,
        )
        suggestions = [s.strip() for s in suggestions_raw.split("\n") if s.strip()][:3]
    except Exception:
        suggestions = ["Tell me more about this", "How do I measure results?", "What's the next step?"]

    return ChatResponse(
        reply=reply,
        session_id=session_id,
        suggestions=suggestions,
    )
