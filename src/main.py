"""
Applied AI Music Recommender — main entry point.

Usage:
    python src/main.py

Requires ANTHROPIC_API_KEY in .env or shell environment.
Falls back to rule-based mode if the API key is missing.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv

load_dotenv()

from ai_agent import display_result, run_agentic_workflow
from llm_client import ClaudeClient
from logger import get_logger, log_event
from recommender import load_songs, recommend_songs

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")
_logger = get_logger("main")


def _try_create_client():
    try:
        return ClaudeClient(), True
    except RuntimeError as exc:
        print(f"\n[Warning] AI features disabled: {exc}")
        print("Running in rule-based fallback mode.\n")
        return None, False


def _rule_based_mode():
    print("\nRule-Based Mode (no API key)")
    print("Enter preferences manually.\n")
    genre = input("Genre (pop/rock/jazz/lofi/ambient/synthwave/indie pop/folk/any): ").strip() or "any"
    mood = input("Mood (happy/chill/intense/relaxed/moody/focused/energetic/any): ").strip() or "any"
    try:
        energy = float(input("Energy 0.0-1.0 (e.g. 0.5): ").strip() or "0.5")
    except ValueError:
        energy = 0.5
    acoustic = input("Likes acoustic? (y/n): ").strip().lower() == "y"

    prefs = {"genre": genre, "mood": mood, "energy": energy, "likes_acoustic": acoustic}
    songs = load_songs(DATA_PATH)
    results = recommend_songs(prefs, songs, k=5)

    print("\nTop Recommendations:\n")
    for song, score, explanation in results:
        print(f"🎵 {song['title']} by {song['artist']}  (score: {score:.2f})")
        print(f"   {explanation}\n")


def main():
    print("\n╔══════════════════════════════════════╗")
    print("║   AI Music Recommender               ║")
    print("║   Powered by Claude + Rule-Based RAG ║")
    print("╚══════════════════════════════════════╝")

    llm, has_llm = _try_create_client()

    while True:
        print("\nOptions:")
        if has_llm:
            print("  1) Get recommendations (AI mode — natural language)")
        print("  2) Get recommendations (rule-based mode)")
        print("  q) Quit")

        choice = input("\nYour choice: ").strip().lower()

        if choice == "q":
            print("\nGoodbye!\n")
            break

        elif choice == "1" and has_llm:
            query = input('\nDescribe the music you want (e.g. "something chill for studying"): ').strip()
            if not query:
                print("Please enter a request.")
                continue
            log_event(_logger, "user_query", {"query": query, "mode": "agentic"})
            result = run_agentic_workflow(query, llm)
            display_result(result)

        elif choice == "2":
            _rule_based_mode()

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
