"""
Converts text to embeddings using Sentence Transformers and computes
cosine similarity between them.

The model is loaded lazily (on first use, not at import time) so that
importing the FastAPI app doesn't require network access or a slow model
download - it only happens once, the first time /analyze is actually called.
"""
from functools import lru_cache

import numpy as np

from app.core.config import settings


@lru_cache(maxsize=1)
def get_model():
    """
    Loads (and caches) the Sentence Transformer model. Cached with lru_cache
    so the (relatively slow) model load only happens once per server process.
    """
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.EMBEDDING_MODEL)


def compute_similarity(text_a: str, text_b: str) -> float:
    """
    Returns cosine similarity between the embeddings of text_a and text_b,
    as a float in roughly [0, 1] (can dip slightly negative for very
    dissimilar text, which we clip to 0).
    """
    model = get_model()
    embeddings = model.encode([text_a, text_b], convert_to_numpy=True, normalize_embeddings=True)

    # Since embeddings are normalized, cosine similarity is just the dot product.
    similarity = float(np.dot(embeddings[0], embeddings[1]))
    return max(0.0, min(1.0, similarity))
