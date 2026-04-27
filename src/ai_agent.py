"""
Agentic workflow orchestrator for the AI Music Recommender.

Three observable steps:
  Step 1 — Preference Parser  (Gemini: natural language → structured prefs)
  Step 2 — Song Retriever     (Rule-based: score all 40 songs, return top 10)
  Step 3 — AI Ranker          (Gemini: re-rank candidates, write explanations)

Confidence evaluation follows as a post-processing pass.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from evaluator import compute_confidence, confidence_label
from llm_client import GeminiClient
from logger import get_logger, log_event
from recommender import load_songs, recommend_songs

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")

_logger = get_logger("ai_agent")


def _divider(char="─", width=52):
    print(char * width)


def run_agentic_workflow(query: str, llm: GeminiClient) -> dict:
    """
    Runs the full 3-step agentic pipeline and returns a result dict:
    {
        "query": str,
        "parsed_prefs": dict,
        "candidates": list,
        "ai_output": str,
        "confidence": float,
        "confidence_label": str,
    }
    """
    print()
    _divider("═")
    print("  AI Music Recommender — Agentic Workflow")
    _divider("═")
    print(f'  Your request: "{query}"')
    print()

    # ── Step 1: Parse preferences ──────────────────────────────────
    print("[STEP 1/3] Parsing your preferences with Gemini...")
    try:
        prefs = llm.parse_preferences(query)
        print(
            f"  → genre: {prefs.get('genre')}  |  mood: {prefs.get('mood')}  "
            f"|  energy: {prefs.get('energy')}  |  acoustic: {prefs.get('likes_acoustic')}"
        )
        log_event(_logger, "preferences_parsed", {"query": query, "prefs": prefs})
    except Exception as exc:
        _logger.error(f"Preference parsing failed: {exc}")
        print(f"  ! Could not parse preferences: {exc}")
        print("  Falling back to neutral defaults.")
        prefs = {"genre": "any", "mood": "any", "energy": 0.5, "likes_acoustic": False}

    # ── Step 2: Retrieve candidates ────────────────────────────────
    print()
    print("[STEP 2/3] Retrieving candidate songs from library...")
    songs = load_songs(DATA_PATH)
    candidates = recommend_songs(prefs, songs, k=10)
    print(f"  → Retrieved {len(candidates)} candidates from {len(songs)}-song library")
    log_event(_logger, "candidates_retrieved", {"count": len(candidates), "prefs": prefs})

    # ── Step 3: AI ranking ─────────────────────────────────────────
    print()
    print("[STEP 3/3] Gemini is ranking and personalizing recommendations...")
    try:
        ai_output = llm.rank_and_explain(query, candidates)
        log_event(_logger, "ai_ranking_complete", {"query": query, "output_length": len(ai_output)})
    except Exception as exc:
        _logger.error(f"AI ranking failed: {exc}")
        print(f"  ! AI ranking failed: {exc}")
        ai_output = _fallback_output(candidates)

    # ── Confidence evaluation ──────────────────────────────────────
    conf = compute_confidence(candidates, prefs)
    label = confidence_label(conf)

    return {
        "query": query,
        "parsed_prefs": prefs,
        "candidates": candidates,
        "ai_output": ai_output,
        "confidence": conf,
        "confidence_label": label,
    }


def display_result(result: dict):
    print()
    _divider()
    print("  Your Personalized Recommendations")
    _divider()
    print()
    print(result["ai_output"])
    print()
    _divider()
    print(f"  Confidence Score: {result['confidence']:.2f}/1.00  —  {result['confidence_label']}")
    _divider()
    print()


def _fallback_output(candidates: list) -> str:
    lines = ["Top picks based on rule-based scoring:\n"]
    for song, score, explanation in candidates[:5]:
        lines.append(f"🎵 {song['title']} by {song['artist']}")
        lines.append(f"Why: {explanation}\n")
    return "\n".join(lines)
