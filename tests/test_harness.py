"""
Automated test harness for the AI Music Recommender.
Runs predefined inputs through the full agentic pipeline and prints a pass/fail summary.

Usage:
    python tests/test_harness.py

Requires ANTHROPIC_API_KEY in .env or shell environment.
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dotenv import load_dotenv

load_dotenv()

from ai_agent import run_agentic_workflow
from evaluator import compute_confidence
from llm_client import ClaudeClient
from recommender import load_songs, recommend_songs

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")

TEST_CASES = [
    {
        "id": 1,
        "query": "I need high energy music for my workout",
        "expected_genre_hint": None,
        "min_energy": 0.7,
        "expected_mood_hint": "intense",
        "description": "High-energy workout request",
    },
    {
        "id": 2,
        "query": "something chill and acoustic to study to",
        "expected_genre_hint": "lofi",
        "min_energy": None,
        "max_energy": 0.55,
        "expected_mood_hint": "focused",
        "description": "Chill/acoustic study request",
    },
    {
        "id": 3,
        "query": "I'm in a great mood and want to dance",
        "expected_genre_hint": None,
        "min_energy": 0.6,
        "expected_mood_hint": "happy",
        "description": "Happy/danceable request",
    },
    {
        "id": 4,
        "query": "moody synthwave for a night drive",
        "expected_genre_hint": "synthwave",
        "min_energy": None,
        "expected_mood_hint": "moody",
        "description": "Synthwave mood request",
    },
    {
        "id": 5,
        "query": "relaxing jazz for a quiet evening at home",
        "expected_genre_hint": "jazz",
        "min_energy": None,
        "max_energy": 0.6,
        "expected_mood_hint": "relaxed",
        "description": "Jazz/relaxed request",
    },
    {
        "id": 6,
        "query": "intense rock to get pumped up",
        "expected_genre_hint": "rock",
        "min_energy": 0.7,
        "expected_mood_hint": "intense",
        "description": "Intense rock request",
    },
]


def _check(case: dict, result: dict) -> tuple[bool, list[str]]:
    issues = []
    prefs = result["parsed_prefs"]
    candidates = result["candidates"]

    if not candidates:
        issues.append("no candidates returned")
        return False, issues

    if len(result["ai_output"].strip()) < 50:
        issues.append("AI output suspiciously short")

    conf = result["confidence"]
    if conf < 0.25:
        issues.append(f"confidence too low ({conf:.2f})")

    if case.get("expected_genre_hint"):
        if prefs.get("genre", "").lower() != case["expected_genre_hint"].lower():
            issues.append(
                f"genre mismatch: expected '{case['expected_genre_hint']}', got '{prefs.get('genre')}'"
            )

    if case.get("expected_mood_hint"):
        if prefs.get("mood", "").lower() != case["expected_mood_hint"].lower():
            issues.append(
                f"mood mismatch: expected '{case['expected_mood_hint']}', got '{prefs.get('mood')}'"
            )

    top_energy = candidates[0][0]["energy"]
    if case.get("min_energy") and top_energy < case["min_energy"]:
        issues.append(f"top song energy {top_energy:.2f} below min {case['min_energy']:.2f}")
    if case.get("max_energy") and top_energy > case["max_energy"]:
        issues.append(f"top song energy {top_energy:.2f} above max {case['max_energy']:.2f}")

    return len(issues) == 0, issues


def run_harness():
    print("\n" + "=" * 58)
    print("   AI Music Recommender — Automated Test Harness")
    print("=" * 58)

    try:
        llm = ClaudeClient()
    except RuntimeError as exc:
        print(f"\n[FATAL] Cannot run harness without API key: {exc}\n")
        sys.exit(1)

    passed = 0
    failed = 0
    results_log = []

    for case in TEST_CASES:
        print(f"\n[Test {case['id']}/6] {case['description']}")
        print(f"  Query: \"{case['query']}\"")

        try:
            result = run_agentic_workflow(case["query"], llm)
            ok, issues = _check(case, result)
        except Exception as exc:
            ok = False
            issues = [f"exception: {exc}"]
            result = {}

        status = "PASS" if ok else "FAIL"
        symbol = "✓" if ok else "✗"
        print(f"  {symbol} {status}", end="")

        if issues:
            print(f"  — {'; '.join(issues)}")
        else:
            conf = result.get("confidence", 0)
            print(f"  — confidence={conf:.2f}")

        if ok:
            passed += 1
        else:
            failed += 1

        results_log.append({"id": case["id"], "status": status, "issues": issues})
        time.sleep(0.5)  # avoid hammering the API

    print()
    print("=" * 58)
    print(f"  Results: {passed}/{len(TEST_CASES)} passed  |  {failed} failed")
    if failed == 0:
        print("  All tests passed.")
    else:
        print(f"  {failed} test(s) need attention — see issues above.")
    print("=" * 58)
    print()

    return passed, failed


if __name__ == "__main__":
    run_harness()
