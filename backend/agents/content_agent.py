"""
Content Agent — Generates marketing content using AI
"""
from services.groq_client import chat_completion, quick_complete
from models import ContentRequest, ContentResponse


SYSTEM_PROMPT = """You are an elite marketing copywriter and content strategist with 15+ years of experience.
You craft compelling, conversion-focused content for brands across industries.
Always produce original, engaging, and on-brand content. Never use generic filler text.
Respond ONLY with the requested content — no preamble, no explanations."""


PLATFORM_GUIDES = {
    "twitter": "Max 280 chars, punchy, use 1-2 hashtags",
    "instagram": "Visual storytelling, 3-5 hashtags, emoji-friendly",
    "linkedin": "Professional, insightful, 150-300 words",
    "facebook": "Conversational, community-focused, 40-80 words sweet spot",
    "tiktok": "Gen Z tone, trend-aware, hook in first 3 words",
    "email": "Subject line + body, clear CTA, max 150 words body",
}


async def generate_content(req: ContentRequest) -> ContentResponse:
    platform_guide = ""
    if req.platform:
        guide = PLATFORM_GUIDES.get(req.platform.lower(), "")
        platform_guide = f"\nPlatform: {req.platform} — {guide}" if guide else f"\nPlatform: {req.platform}"

    keywords_str = ""
    if req.keywords:
        keywords_str = f"\nKeywords to include: {', '.join(req.keywords)}"

    length_str = ""
    if req.max_length:
        length_str = f"\nMax length: {req.max_length} characters"

    prompts = {
        "social_post": f"""Write a {req.tone} social media post about: {req.topic}{platform_guide}{keywords_str}{length_str}
Include a strong hook, value statement, and call-to-action.""",

        "blog": f"""Write a compelling blog post about: {req.topic}
Tone: {req.tone}{keywords_str}{length_str}
Structure: Hook headline, intro paragraph, 3 key sections with subheadings, conclusion with CTA.""",

        "email": f"""Write a {req.tone} marketing email about: {req.topic}{keywords_str}{length_str}
Include: Subject line, preview text, personalized greeting, value body, clear CTA, and sign-off.""",

        "ad_copy": f"""Write {req.tone} ad copy for: {req.topic}{platform_guide}{keywords_str}{length_str}
Provide: Headline (max 30 chars), primary text (max 125 chars), description (max 30 chars), and CTA.""",

        "hashtags": f"""Generate the 15 best-performing hashtags for a {req.tone} post about: {req.topic}{platform_guide}
Mix popular (10M+), medium (100K-10M), and niche (<100K) hashtags. Return as space-separated list.""",

        "subject_line": f"""Write 5 high-converting email subject lines for: {req.topic}
Tone: {req.tone}{length_str}
Include: curiosity, urgency, personalization, benefit-driven, and question variants.""",
    }

    prompt = prompts.get(req.content_type, prompts["social_post"])

    content = await chat_completion(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=SYSTEM_PROMPT,
        temperature=0.8,
        max_tokens=1500,
    )

    # Generate quick improvement suggestions
    suggestions_prompt = f"Give 3 quick bullet-point tips to improve this {req.content_type} for better engagement. Keep each tip under 10 words:\n\n{content[:300]}"
    suggestions_raw = await quick_complete(suggestions_prompt)
    suggestions = [s.strip().lstrip("•-*123. ") for s in suggestions_raw.split("\n") if s.strip()][:3]

    return ContentResponse(
        content=content,
        content_type=req.content_type,
        platform=req.platform,
        word_count=len(content.split()),
        suggestions=suggestions,
    )
