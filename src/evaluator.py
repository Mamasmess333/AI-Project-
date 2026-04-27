"""
Confidence scoring for the AI Music Recommender.
Evaluates how well the retrieved candidates match user preferences.
"""

from typing import Dict, List, Tuple

MAX_RULE_SCORE = 6.5  # genre(2) + mood(2) + energy(1.5) + acoustic(1)


def compute_confidence(candidates: List[Tuple[Dict, float, str]], prefs: Dict) -> float:
    """
    Returns a confidence score 0.0-1.0 based on:
    - Top candidate's rule-based score relative to theoretical max
    - Whether genre and mood exactly matched in the top 3 results
    - Number of good candidates found
    """
    if not candidates:
        return 0.0

    top_score = candidates[0][1]
    base = min(top_score / MAX_RULE_SCORE, 1.0)

    genre = prefs.get("genre", "any").lower()
    mood = prefs.get("mood", "any").lower()

    top3 = [s for s, _, _ in candidates[:3]]
    genre_hit = genre == "any" or any(s["genre"].lower() == genre for s in top3)
    mood_hit = mood == "any" or any(s["mood"].lower() == mood for s in top3)

    bonus = 0.0
    if genre_hit:
        bonus += 0.12
    if mood_hit:
        bonus += 0.10
    if len(candidates) >= 5:
        bonus += 0.05

    return round(min(base + bonus, 1.0), 2)


def confidence_label(score: float) -> str:
    if score >= 0.80:
        return "Strong match"
    if score >= 0.55:
        return "Good match"
    if score >= 0.35:
        return "Partial match"
    return "Low confidence — try rephrasing your request"
