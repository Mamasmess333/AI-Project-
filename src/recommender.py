"""
Rule-based music recommender (base project — Module 2).
Scores songs against user preferences using explicit feature matching.
Extended version adds expanded dataset support and returns richer tuples.
"""

import csv
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class Song:
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def load_songs(csv_path: str) -> List[Dict]:
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    score = 0.0
    reasons = []

    if song["genre"].lower() == user_prefs.get("genre", "").lower():
        score += 2.0
        reasons.append(f"genre matches ({song['genre']})")
    elif user_prefs.get("genre", "any").lower() == "any":
        score += 0.5

    if song["mood"].lower() == user_prefs.get("mood", "").lower():
        score += 2.0
        reasons.append(f"mood matches ({song['mood']})")
    elif user_prefs.get("mood", "any").lower() == "any":
        score += 0.5

    target_energy = float(user_prefs.get("energy", 0.5))
    closeness = 1.0 - abs(song["energy"] - target_energy)
    score += 1.5 * closeness
    if closeness >= 0.85:
        reasons.append(f"energy ({song['energy']:.2f}) closely matches target ({target_energy:.2f})")

    likes_acoustic = bool(user_prefs.get("likes_acoustic", False))
    if likes_acoustic:
        score += song["acousticness"]
        if song["acousticness"] >= 0.6:
            reasons.append(f"strong acoustic feel ({song['acousticness']:.2f})")
    else:
        score += (1.0 - song["acousticness"])
        if song["acousticness"] <= 0.3:
            reasons.append(f"produced/electronic sound ({song['acousticness']:.2f} acousticness)")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 10) -> List[Tuple[Dict, float, str]]:
    scored = []
    for song in songs:
        s, reasons = score_song(user_prefs, song)
        explanation = ("Recommended because: " + "; ".join(reasons) + ".") if reasons else "Selected for overall compatibility."
        scored.append((song, s, explanation))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
