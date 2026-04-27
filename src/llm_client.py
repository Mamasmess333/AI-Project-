"""
Gemini API client for the AI Music Recommender.
Handles preference parsing (Step 1) and AI ranking/explanation (Step 3).
"""

import json
import os
import google.generativeai as genai

MODEL = "gemini-2.5-flash"

_SYSTEM_PROMPT = (
    "You are an expert music curator and recommendation engine. "
    "You help users discover music that perfectly matches their mood, energy, and taste. "
    "You are precise, warm, and always ground your recommendations in the provided song data."
)


class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Missing GEMINI_API_KEY. Add it to your .env file or shell environment."
            )
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(MODEL, system_instruction=_SYSTEM_PROMPT)

    def parse_preferences(self, natural_query: str) -> dict:
        """Step 1 — Convert free-text request into structured preference dict."""
        prompt = f"""A user wants music. Parse their request into structured preferences.

User request: "{natural_query}"

Reply with ONLY a valid JSON object — no markdown, no explanation — using these exact keys:
- "genre": one of [pop, rock, jazz, lofi, ambient, synthwave, indie pop, electronic, folk, any]
- "mood": one of [happy, chill, intense, relaxed, moody, focused, energetic, sad, any]
- "energy": float 0.0 (very calm) to 1.0 (very high energy)
- "likes_acoustic": boolean

Example output: {{"genre": "lofi", "mood": "focused", "energy": 0.4, "likes_acoustic": true}}"""

        response = self.model.generate_content(prompt)
        raw = (response.text or "").strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(raw)

    def rank_and_explain(self, query: str, candidates: list) -> str:
        """Step 3 — Re-rank candidates and write personalized explanations."""
        lines = []
        for i, (song, score, _) in enumerate(candidates, 1):
            lines.append(
                f"{i}. \"{song['title']}\" by {song['artist']} "
                f"[genre={song['genre']}, mood={song['mood']}, "
                f"energy={song['energy']:.2f}, acousticness={song['acousticness']:.2f}, "
                f"rule_score={score:.2f}]"
            )
        candidate_text = "\n".join(lines)

        prompt = f"""User's music request: "{query}"

Candidate songs retrieved from our library (already pre-filtered by rule-based scoring):
{candidate_text}

Select the 3 to 5 best matches and write a personalized 1-2 sentence explanation for each.
Format each entry exactly like this (use the real song title and artist):

🎵 [Title] by [Artist]
Why: [Your explanation of why this fits the user's request]

Rank from best to least match. Only pick songs from the list above."""

        response = self.model.generate_content(prompt)
        return (response.text or "").strip()
