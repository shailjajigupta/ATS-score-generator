"""
Generic keyword extraction from free text - distinct from the curated
SKILL_KEYWORDS list. This captures domain/role-specific terms the fixed
skills list won't (e.g. "cross-functional", "distributed systems",
"stakeholder management", industry terms), giving the "Keyword Match"
score a broader net than the "Skills Match" score.
"""
import re
from collections import Counter
from typing import List, Tuple

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "else", "for", "to",
    "of", "in", "on", "at", "by", "with", "as", "is", "are", "was", "were",
    "be", "been", "being", "this", "that", "these", "those", "it", "its",
    "we", "you", "your", "our", "they", "their", "will", "would", "should",
    "can", "could", "may", "might", "must", "shall", "have", "has", "had",
    "do", "does", "did", "not", "no", "yes", "from", "into", "about", "than",
    "so", "such", "also", "any", "all", "each", "other", "some", "more",
    "most", "us", "who", "what", "when", "where", "why", "how", "job",
    "role", "team", "work", "working", "company", "years", "year", "including",
    "etc", "e.g", "eg", "strong", "excellent", "including", "looking",
}

WORD_PATTERN = re.compile(r"[A-Za-z][A-Za-z\-\.]{2,}")


def extract_keyword_terms(text: str, top_n: int = 25) -> List[str]:
    """
    Extracts the most frequent meaningful words from `text` (lowercased,
    stopwords and very short words removed). This is a simple frequency-based
    extractor, not a full NLP keyword/phrase extractor - kept intentionally
    simple per the project brief.
    """
    raw_words = WORD_PATTERN.findall(text.lower())
    words = [w.strip(".-") for w in raw_words]
    filtered = [w for w in words if w not in STOPWORDS and len(w) > 3]
    counts = Counter(filtered)
    return [word for word, _ in counts.most_common(top_n)]


def compute_keyword_match(resume_text: str, jd_text: str) -> Tuple[List[str], List[str], float]:
    """
    Extracts the JD's most frequent meaningful terms as "expected keywords",
    then checks how many also appear in the resume.

    Returns: (matched_keywords, missing_keywords, keyword_score 0-100)
    """
    jd_keywords = extract_keyword_terms(jd_text)
    if not jd_keywords:
        return [], [], 0.0

    resume_words = {w.strip(".-") for w in WORD_PATTERN.findall(resume_text.lower())}

    matched = sorted(k for k in jd_keywords if k in resume_words)
    missing = sorted(k for k in jd_keywords if k not in resume_words)

    score = (len(matched) / len(jd_keywords)) * 100
    return matched, missing, round(score, 1)
