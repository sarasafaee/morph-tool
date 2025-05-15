# backend/classifier.py

"""
Module: classifier
Implements a basic analogy-based affix selection:
  score(candidate) = alpha * similarity(word, candidate)
Returns both the per-candidate scores and the best choice.
"""

from typing import List, Dict
from backend.similarity import calculate_similarity

def classify_word(
    word: str,
    candidates: List[str],
    alpha: float,
    method: str = 'levenshtein'
) -> Dict:
    """
    Rank each candidate by weighted similarity.

    Parameters
    ----------
    word : str
        The input base form (e.g. "analysis").
    candidates : List[str]
        List of affix strings or full-word candidates (e.g. ["-able", "-ible"]).
    alpha : float
        Activation weight in [0.0, 1.0].
    method : str
        Similarity method passed to calculate_similarity.

    Returns
    -------
    dict
        {
          "scores": {candidate: score, ...},
          "best": best_candidate
        }

    Raises
    ------
    ValueError
        If `candidates` is empty or `alpha` not in [0,1].
    """
    if not candidates:
        raise ValueError("Must provide at least one candidate")
    if not (0.0 <= alpha <= 1.0):
        raise ValueError("Alpha must be between 0.0 and 1.0")

    scores = {}
    for cand in candidates:
        sim = calculate_similarity(word, cand, method=method)
        scores[cand] = alpha * sim

    # pick the candidate with the highest score
    best = max(scores, key=scores.get)
    return {"scores": scores, "best": best}
