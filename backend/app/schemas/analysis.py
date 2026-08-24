from typing import List, Optional
from pydantic import BaseModel


class ExperienceDetails(BaseModel):
    required_years: Optional[int] = None
    candidate_years: Optional[int] = None
    resume_self_identifies_as_fresher: bool = False
    method: str


class EducationDetails(BaseModel):
    required_degree: Optional[str] = None
    candidate_degree: Optional[str] = None
    method: str


class ScoreBreakdown(BaseModel):
    """The 5 weighted parameters that combine into the overall score."""
    skills_match: float
    semantic_similarity: float
    experience_relevance: float
    keyword_match: float
    education_match: float


SCORE_WEIGHTS = {
    "skills_match": 0.30,
    "semantic_similarity": 0.25,
    "experience_relevance": 0.20,
    "keyword_match": 0.15,
    "education_match": 0.10,
}


class AnalysisResponse(BaseModel):
    overall_score: float
    score_breakdown: ScoreBreakdown
    weights: dict = SCORE_WEIGHTS

    matched_skills: List[str]
    missing_skills: List[str]

    matched_keywords: List[str]
    missing_keywords: List[str]

    experience_details: ExperienceDetails
    education_details: EducationDetails

    suggestions: str
