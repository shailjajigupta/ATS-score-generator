"""
Education/degree-requirement matching between a JD and a resume, using a
simple degree hierarchy (higher degree = higher level).
"""
import re
from typing import Optional, Tuple

# Ordered highest-first is not required; level is what matters for comparison.
DEGREE_PATTERNS = [
    (4, re.compile(r"\b(ph\.?d|doctorate)\b", re.IGNORECASE)),
    (3, re.compile(r"\b(master'?s?|m\.?tech|m\.?s\.?|mba|m\.?sc)\b", re.IGNORECASE)),
    (2, re.compile(r"\b(bachelor'?s?|b\.?tech|b\.?e\.?|b\.?s\.?|b\.?sc|undergraduate degree)\b", re.IGNORECASE)),
    (1, re.compile(r"\b(associate degree|diploma)\b", re.IGNORECASE)),
    (0, re.compile(r"\bhigh school\b", re.IGNORECASE)),
]

DEGREE_LABELS = {
    4: "PhD / Doctorate",
    3: "Master's degree",
    2: "Bachelor's degree",
    1: "Diploma / Associate degree",
    0: "High school",
}


def extract_degree_level(text: str) -> Optional[int]:
    """Returns the highest degree level mentioned in `text`, or None if no degree is mentioned."""
    levels_found = [level for level, pattern in DEGREE_PATTERNS if pattern.search(text)]
    return max(levels_found) if levels_found else None


def compute_education_score(resume_text: str, jd_text: str) -> Tuple[float, dict]:
    """
    Compares the degree level required by the JD against the degree level
    stated in the resume.

    Returns: (education_score 0-100, details dict for transparency)
    """
    required_level = extract_degree_level(jd_text)
    candidate_level = extract_degree_level(resume_text)

    details = {
        "required_degree": DEGREE_LABELS.get(required_level) if required_level is not None else None,
        "candidate_degree": DEGREE_LABELS.get(candidate_level) if candidate_level is not None else None,
    }

    if required_level is None:
        # JD doesn't state a specific degree requirement - nothing to penalize.
        details["method"] = "no_requirement_stated"
        return 100.0, details

    if candidate_level is None:
        # JD wants a specific degree, but the resume doesn't mention one at all.
        details["method"] = "resume_omits_education"
        return 30.0, details

    if candidate_level >= required_level:
        details["method"] = "meets_or_exceeds_requirement"
        return 100.0, details

    # Below the required level - partial credit, scaled by how far below.
    details["method"] = "below_requirement"
    gap = required_level - candidate_level
    score = max(0.0, 100 - gap * 35)
    return round(score, 1), details
