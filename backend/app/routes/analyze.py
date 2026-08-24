"""
The single endpoint this app needs: POST /analyze.

Accepts the resume and JD as either pasted text or an uploaded file
(pdf/docx/txt), for each independently. Runs the full pipeline and combines
5 weighted parameters into one overall compatibility score:

    Skills Match            30%
    Semantic Similarity     25%
    Experience Relevance    20%
    Keyword Match           15%
    Education Match         10%
"""
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.schemas.analysis import (
    AnalysisResponse,
    EducationDetails,
    ExperienceDetails,
    ScoreBreakdown,
    SCORE_WEIGHTS,
)
from app.services.education_service import compute_education_score
from app.services.embedding_service import compute_similarity
from app.services.groq_service import generate_suggestions
from app.services.keyword_service import compare_skills, compute_experience_score
from app.services.text_extraction import extract_text_from_upload
from app.services.text_keywords import compute_keyword_match

router = APIRouter(tags=["analysis"])


async def _resolve_text(label: str, text: Optional[str], file: Optional[UploadFile]) -> str:
    """Either `text` or `file` must be provided (file takes priority if both given)."""
    if file is not None and file.filename:
        return await extract_text_from_upload(file)
    if text and text.strip():
        return text.strip()
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Please provide the {label} as either pasted text or an uploaded file.",
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    resume_text: Optional[str] = Form(None),
    jd_text: Optional[str] = Form(None),
    resume_file: Optional[UploadFile] = File(None),
    jd_file: Optional[UploadFile] = File(None),
):
    resume = await _resolve_text("resume", resume_text, resume_file)
    jd = await _resolve_text("job description", jd_text, jd_file)

    # 1. Semantic Similarity (25%) - Sentence Transformer embeddings + cosine similarity.
    similarity_ratio = compute_similarity(resume, jd)
    semantic_similarity = round(similarity_ratio * 100, 1)

    # 2. Skills Match (30%) - curated skill list, JD-required vs resume-present.
    matched_skills, missing_skills, skills_match = compare_skills(resume, jd)
    if not matched_skills and not missing_skills:
        # JD didn't mention any known curated skill keywords - fall back to semantic similarity.
        skills_match = semantic_similarity

    # 3. Experience Relevance (20%) - years-of-experience comparison, with fresher detection.
    experience_relevance, exp_details = compute_experience_score(resume, jd, similarity_ratio)

    # 4. Keyword Match (15%) - broader, dynamically-extracted JD terms vs resume.
    matched_keywords, missing_keywords, keyword_match = compute_keyword_match(resume, jd)
    if not matched_keywords and not missing_keywords:
        keyword_match = semantic_similarity

    # 5. Education Match (10%) - degree-level comparison.
    education_match, edu_details = compute_education_score(resume, jd)

    breakdown = ScoreBreakdown(
        skills_match=skills_match,
        semantic_similarity=semantic_similarity,
        experience_relevance=experience_relevance,
        keyword_match=keyword_match,
        education_match=education_match,
    )

    overall_score = round(
        skills_match * SCORE_WEIGHTS["skills_match"]
        + semantic_similarity * SCORE_WEIGHTS["semantic_similarity"]
        + experience_relevance * SCORE_WEIGHTS["experience_relevance"]
        + keyword_match * SCORE_WEIGHTS["keyword_match"]
        + education_match * SCORE_WEIGHTS["education_match"],
        1,
    )

    # 6. AI-generated improvement suggestions via Groq/Llama 3, informed by all gaps found.
    all_missing = missing_skills + [k for k in missing_keywords if k not in missing_skills]
    suggestions = generate_suggestions(resume, jd, all_missing)

    return AnalysisResponse(
        overall_score=overall_score,
        score_breakdown=breakdown,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        experience_details=ExperienceDetails(**exp_details),
        education_details=EducationDetails(**edu_details),
        suggestions=suggestions,
    )
