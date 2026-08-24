"""
Calls the Groq API (Llama 3) to generate plain-language resume improvement
suggestions, based on the gaps found between the resume and the JD.
"""
from typing import List

from app.core.config import settings

FALLBACK_MESSAGE = (
    "AI suggestions are unavailable because no GROQ_API_KEY is configured. "
    "Get a free key at https://console.groq.com/keys and add it to your .env file "
    "to enable this feature. In the meantime, review the missing skills list above "
    "and consider adding relevant experience or projects that demonstrate them."
)


def build_prompt(resume_text: str, jd_text: str, missing_skills: List[str]) -> str:
    missing_str = ", ".join(missing_skills) if missing_skills else "None identified"

    # Truncate long inputs to keep the prompt (and API cost) reasonable.
    resume_excerpt = resume_text[:3000]
    jd_excerpt = jd_text[:2000]

    return f"""You are a career coach helping a candidate improve their resume for a specific job.

JOB DESCRIPTION:
{jd_excerpt}

CANDIDATE'S RESUME:
{resume_excerpt}

SKILLS MENTIONED IN THE JOB DESCRIPTION BUT NOT FOUND IN THE RESUME:
{missing_str}

Give the candidate 4-6 short, specific, actionable suggestions to improve their resume
for this job. Focus on: how to address the missing skills (add them if the candidate
likely has related experience, or suggest how to gain/demonstrate them), how to better
highlight relevant experience already in the resume, and any clear gaps between the
resume and the job requirements. Write each suggestion as a single concise sentence.
Return ONLY a numbered list of suggestions, nothing else - no preamble, no summary."""


def generate_suggestions(resume_text: str, jd_text: str, missing_skills: List[str]) -> str:
    """
    Returns a string of AI-generated suggestions (numbered list as plain text),
    or a helpful fallback message if no Groq API key is configured or the
    call fails for any reason.
    """
    if not settings.GROQ_API_KEY:
        return FALLBACK_MESSAGE

    try:
        from groq import Groq

        client = Groq(api_key=settings.GROQ_API_KEY)
        prompt = build_prompt(resume_text, jd_text, missing_skills)

        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=600,
        )
        return response.choices[0].message.content.strip()

    except Exception as exc:
        # Don't let an LLM/network hiccup break the whole analysis - the
        # embeddings + keyword results are still valid and useful on their own.
        return (
            f"Could not generate AI suggestions right now ({exc}). "
            f"The scores and skill comparison above are still valid."
        )
