"""
Keyword/skill matching between a resume and a job description, plus a
simple regex-based "years of experience" comparison.
"""
import re
from typing import List, Optional, Tuple

from app.services.skills_data import SKILL_KEYWORDS


def _build_pattern(keyword: str) -> re.Pattern:
    # Word-boundary match, case-insensitive. Escape special regex chars
    # (keywords like "c++", ".net", "ci/cd" contain regex-special characters).
    escaped = re.escape(keyword)
    return re.compile(rf"(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])", re.IGNORECASE)


def find_skills_in_text(text: str, keywords: List[str] = SKILL_KEYWORDS) -> List[str]:
    """Returns the subset of `keywords` that appear in `text` (case-insensitive)."""
    found = []
    for keyword in keywords:
        if _build_pattern(keyword).search(text):
            found.append(keyword)
    return found


def compare_skills(resume_text: str, jd_text: str) -> Tuple[List[str], List[str], float]:
    """
    Finds which curated skills appear in the JD (the "required" skills for
    this role), then checks which of those also appear in the resume.

    Returns: (matched_skills, missing_skills, skills_score 0-100)
    """
    required_skills = find_skills_in_text(jd_text)

    if not required_skills:
        # JD didn't mention any of our known skill keywords - can't score
        # skills meaningfully, so treat resume/JD overall similarity as the
        # fallback (handled by the caller) and return an empty breakdown.
        return [], [], 0.0

    resume_skills = set(find_skills_in_text(resume_text, required_skills))

    matched = sorted(s for s in required_skills if s in resume_skills)
    missing = sorted(s for s in required_skills if s not in resume_skills)

    skills_score = (len(matched) / len(required_skills)) * 100
    return matched, missing, round(skills_score, 1)


YEARS_PATTERN = re.compile(r"(\d+)\+?\s*(?:years|yrs)\b", re.IGNORECASE)

FRESHER_PATTERN = re.compile(
    r"\b(fresher|entry.?level|recent graduate|no prior experience|no professional experience)\b",
    re.IGNORECASE,
)


def extract_years_of_experience(text: str) -> Optional[int]:
    """
    Finds mentions like '5 years', '3+ years', '10 yrs' and returns the
    largest number found (a reasonable proxy for "years of experience").
    Returns None if no such mention is found.
    """
    matches = YEARS_PATTERN.findall(text)
    if not matches:
        return None
    return max(int(m) for m in matches)


def mentions_fresher(text: str) -> bool:
    """True if the text explicitly self-identifies as a fresher/entry-level candidate."""
    return bool(FRESHER_PATTERN.search(text))


def compute_experience_score(resume_text: str, jd_text: str, overall_similarity: float) -> Tuple[float, dict]:
    """
    Compares years of experience required (from the JD) against years the
    candidate has (from the resume).

    - If the JD states a required number of years:
        - If the resume also states a number, compare them directly.
        - If the resume states no number but self-identifies as a fresher/
          entry-level, treat candidate years as 0 (an honest low score,
          rather than quietly matching the overall similarity score).
        - Otherwise (resume just doesn't mention years explicitly), fall
          back to a rough half-credit heuristic - we can't confirm the
          requirement is met, but we also shouldn't assume zero experience
          just because it wasn't phrased as "X years".
    - If the JD doesn't state a required number of years at all, there's
      nothing concrete to compare, so we fall back to overall similarity
      (this is a genuine "no signal" case, not a scoring bug).

    Returns: (experience_score 0-100, details dict for transparency)
    """
    required_years = extract_years_of_experience(jd_text)
    candidate_years = extract_years_of_experience(resume_text)
    resume_is_fresher = mentions_fresher(resume_text)

    details = {
        "required_years": required_years,
        "candidate_years": candidate_years,
        "resume_self_identifies_as_fresher": resume_is_fresher,
    }

    if required_years is None:
        details["method"] = "semantic_similarity_fallback"
        return round(overall_similarity * 100, 1), details

    if candidate_years is None and resume_is_fresher:
        candidate_years = 0

    if candidate_years is not None:
        details["method"] = "years_comparison"
        if required_years == 0:
            return 100.0, details
        ratio = candidate_years / required_years
        score = min(100.0, ratio * 100)
        return round(score, 1), details

    # JD wants a specific number of years, but the resume gives no signal
    # either way (no explicit years, no fresher self-identification).
    # Give partial credit rather than silently borrowing the overall score.
    details["method"] = "no_years_stated_partial_credit"
    return 50.0, details
