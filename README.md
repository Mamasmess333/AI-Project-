# AI Music Recommender — Applied AI System

> **CodePath AI110 | Final Project (Module 5)**
> **Author:** Andrew Alvarez | GitHub: [@Mamasmess333](https://github.com/Mamasmess333)

## Demo Walkthrough

🎬 **Loom Video:** [Add your Loom link here after recording]

---

## Base Project

**Original project:** Music Recommender Simulation (Module 2)

The Module 2 project was a rule-based music recommender that scored songs against explicit user preferences (genre, mood, energy level, acoustic preference) using a weighted feature-matching algorithm. It accepted structured dictionary inputs and returned ranked songs from a 10-song CSV dataset. It had no AI integration — all logic was deterministic and hand-coded.

---

## What This System Does

This project extends the Module 2 recommender into a **full agentic AI system** that:

1. Accepts **natural language** requests ("something chill for studying")
2. Uses **Claude (claude-sonnet-4-6)** to parse preferences into structured data
3. Runs the original **rule-based retriever** to candidate-filter a 40-song library
4. Uses **Claude again** to re-rank candidates and write personalized explanations
5. Computes a **confidence score** (0.0–1.0) for each result set
6. **Logs every step** to `logs/recommender.log`
7. Includes an **automated test harness** with 6 predefined test cases

---

## System Architecture

![Architecture Diagram](assets/architecture.png)

> *See `assets/architecture.md` for the Mermaid source if the image is unavailable.*

**Data flow:**
```
User (natural language)
  → [Step 1] Preference Parser  (Claude)
  → [Step 2] Song Retriever     (Rule-based scoring, 40 songs)
  → [Step 3] AI Ranker          (Claude + retrieved context)
  → Confidence Evaluator
  → Final output: top 3–5 songs + explanations + score
```

---

## AI Features Implemented

| Feature | Details |
|---|---|
| **Agentic Workflow** (required) | 3 observable steps with printed progress at each stage |
| **Agentic Enhancement** (stretch +2) | Intermediate steps are logged, printed, and independently recoverable |
| **Test Harness** (stretch +2) | `tests/test_harness.py` runs 6 cases and prints pass/fail summary |

---

## Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/Mamasmess333/applied-ai-system-project.git
cd applied-ai-system-project
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API key

```bash
cp .env.example .env
# Open .env and replace the placeholder with your real ANTHROPIC_API_KEY
```

### 5. Run the system

```bash
python src/main.py
```

### 6. Run the test harness (optional)

```bash
python tests/test_harness.py
```

---

## Sample Interactions

### Example 1 — Study session

```
Your request: "something lo-fi and acoustic for a late-night study session"

[STEP 1/3] Parsing your preferences with Claude...
  → genre: lofi  |  mood: focused  |  energy: 0.38  |  acoustic: True

[STEP 2/3] Retrieving candidate songs from library...
  → Retrieved 10 candidates from 40-song library

[STEP 3/3] Claude is ranking and personalizing recommendations...

────────────────────────────────────────────────────
  Your Personalized Recommendations
────────────────────────────────────────────────────

🎵 Study Mode by LoRoom
Why: Its 74 BPM tempo and 0.82 acousticness create the perfect quiet backdrop for sustained concentration without pulling your attention away.

🎵 Library Rain by Paper Lanterns
Why: Named for exactly the vibe you described — the gentle pace and high acousticness (0.86) make it ideal for late-night sessions.

🎵 Focus Flow by LoRoom
Why: Built for focus with a measured 80 BPM and predominantly acoustic texture, keeping your mind in flow state.

────────────────────────────────────────────────────
  Confidence Score: 0.89/1.00  —  Strong match
────────────────────────────────────────────────────
```

### Example 2 — Workout

```
Your request: "high energy to get me through leg day"

[STEP 1/3] Parsing your preferences with Claude...
  → genre: any  |  mood: intense  |  energy: 0.9  |  acoustic: False

[STEP 2/3] Retrieving candidate songs from library...
  → Retrieved 10 candidates from 40-song library

[STEP 3/3] Claude is ranking and personalizing recommendations...

🎵 Bass Drop City by Max Pulse
Why: At 0.95 energy and 140 BPM this is built for the heaviest sets — pure drive with no acoustic softness to break the intensity.

🎵 Voltage Rush by Voltline
Why: 155 BPM and relentless rock energy make this perfect for pushing through the final reps when everything else fades.

🎵 Gym Hero by Max Pulse
Why: Named for exactly this moment — 0.93 energy and high danceability mean your body stays in rhythm even when your legs want to quit.

────────────────────────────────────────────────────
  Confidence Score: 0.91/1.00  —  Strong match
────────────────────────────────────────────────────
```

### Example 3 — Ambiguous request (low confidence)

```
Your request: "music"

[STEP 1/3] Parsing your preferences with Claude...
  → genre: any  |  mood: any  |  energy: 0.5  |  acoustic: False

[STEP 2/3] Retrieving candidate songs from library...
  → Retrieved 10 candidates from 40-song library

[STEP 3/3] Claude is ranking and personalizing recommendations...

🎵 Rooftop Lights by Indigo Parade
Why: A versatile indie pop track with balanced energy (0.76) and high valence — a safe starting point for any listener.

────────────────────────────────────────────────────
  Confidence Score: 0.38/1.00  —  Partial match — try rephrasing your request
────────────────────────────────────────────────────
```

---

## Design Decisions

**Why a 3-step agentic pipeline instead of one big prompt?**
Separating parsing from ranking makes failures observable and recoverable. If Step 1 (parsing) fails, we fall back to neutral defaults rather than crashing. If Step 3 (ranking) fails, we fall back to the rule-based output. Each step has its own logging and error handling.

**Why keep the original rule-based retriever?**
The original Module 2 scoring function is deterministic and fast. Using it as Step 2 gives the system a reliable pre-filter before handing candidates to Claude. This is cheaper (fewer tokens), faster, and more predictable than asking Claude to rank all 40 songs directly.

**Why TF-IDF / inverted index instead of vector embeddings?**
The song library is small (40 songs) and the features are categorical. A vector embedding store would add infrastructure complexity without meaningful accuracy gains at this scale. The rule-based scorer is fully explainable and needs no external embedding API.

**Trade-offs:**
- The 40-song dataset limits recommendation diversity. A production version would need thousands of real tracks.
- Parsing accuracy depends on Claude's interpretation of vague requests. A more robust version would add few-shot examples to the parsing prompt.

---

## Testing Summary

Run `python tests/test_harness.py` to execute all 6 test cases.

**Test cases:**
1. High-energy workout → expects intense/energetic results, energy > 0.7
2. Chill acoustic study → expects lofi/focused results, energy < 0.55
3. Happy/danceable → expects happy mood, energy > 0.6
4. Moody synthwave → expects synthwave genre, moody mood
5. Relaxing jazz → expects jazz genre, relaxed mood, energy < 0.6
6. Intense rock → expects rock genre, intense mood, energy > 0.7

**Observed results:** 5/6 tests pass consistently. Test 2 occasionally produces `energy: 0.6` from parsing when the user says "chill" without saying "calm" or "low energy" — the confidence score correctly drops to reflect this mismatch.

---

## Reflection and Ethics

See [`model_card.md`](model_card.md) for the full reflection including:
- Limitations and biases
- Potential misuse and safeguards
- Testing surprises
- AI collaboration notes

---

## Repository Structure

```
applied-ai-system-project/
├── src/
│   ├── main.py          # Entry point
│   ├── recommender.py   # Original rule-based scoring (base project)
│   ├── llm_client.py    # Claude API — parsing + ranking
│   ├── ai_agent.py      # Agentic workflow orchestrator
│   ├── evaluator.py     # Confidence scoring
│   └── logger.py        # Structured JSON logging
├── data/
│   └── songs.csv        # 40-song library
├── tests/
│   └── test_harness.py  # Automated evaluation script
├── assets/
│   ├── architecture.md  # Mermaid diagram source
│   └── architecture.png # Exported diagram
├── logs/                # Auto-created; contains recommender.log
├── README.md
├── model_card.md
├── requirements.txt
└── .env.example
```

---

## Portfolio Reflection

This project taught me that the hardest part of building an AI system is not the model — it's the interface between what users say naturally and what a structured system needs to receive. The 3-step pipeline made this explicit: natural language goes in, structured logic processes it, and AI explains the result. That separation — human input → deterministic filter → AI explanation — is a pattern I'll carry into every AI system I build.

As an AI engineer, I want to build systems that are both powerful and auditable. Every design decision in this project was made with that goal: observable steps, logged behavior, explainable scores, and graceful fallbacks when the AI doesn't perform as expected.
