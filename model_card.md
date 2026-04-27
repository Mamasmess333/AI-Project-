# Model Card — AI Music Recommender

## Model Details

| Field | Value |
|---|---|
| Base LLM | gemini-2.5-flash (Google) |
| Task | Music recommendation via agentic workflow |
| Input | Natural language music request |
| Output | Ranked song recommendations with explanations + confidence score |
| Dataset | 40-song synthetic library (CSV) |

---

## AI Collaboration During This Project

**Helpful instance:** Gemini accurately parsed ambiguous requests like *"something lo-fi for when it's raining"* into structured preferences (`genre: lofi`, `mood: chill`, `energy: 0.35`, `likes_acoustic: true`) without any examples being provided. This made the preference parsing step robust from the start.

**Flawed instance:** In early testing, Gemini occasionally returned genre values not in the allowed list (e.g., `"lo-fi"` instead of `"lofi"`, or `"hip hop"` instead of `"hip-hop"`). The parser would then crash on JSON key mismatches. I fixed this by adding strict normalization and a try/except fallback in `ai_agent.py` that defaults to neutral preferences rather than crashing.

---

## Limitations and Biases

- **Small dataset:** The 40-song library is synthetic and hand-crafted. A real system would need thousands of songs with verified metadata to generalize well.
- **Western genre bias:** The dataset covers pop, rock, jazz, and electronic genres. Non-Western genres (Afrobeats, K-pop, Bollywood) are absent.
- **Mood subjectivity:** Labels like "chill" or "moody" are subjective and may not align with individual users' emotional vocabulary.
- **Energy scale:** The 0.0–1.0 energy scale is manually assigned and may not match how users intuitively describe intensity.
- **LLM hallucination risk:** Gemini could recommend a song from outside the candidate list. The prompt explicitly instructs against this, but prompt adherence is probabilistic.

---

## Potential Misuse and Safeguards

**Potential misuse:** The preference-parsing step could theoretically be used to profile users' emotional states without consent.

**Safeguards in place:**
- No user data is stored beyond the session log (which contains only the query, not user identity).
- Logs are local-only and never transmitted.
- The system has no user accounts, tracking, or persistent profiles.

---

## Testing Summary

**Automated harness (6 test cases):**
- Tests verify that parsed preferences match expected genre/mood hints
- Tests verify that top candidates respect energy bounds (min/max)
- Tests check confidence score > 0.25 for all inputs
- Tests verify AI output is non-trivial (>50 characters)

**Results observed during development:**
- 5 of 6 tests passed consistently across multiple runs
- Test 2 (chill/acoustic) occasionally failed the energy ceiling check when Gemini parsed `energy: 0.6` instead of `0.4` for ambiguous requests — resolved by adding a clearer energy scale description to the parsing prompt
- Average confidence score across all test cases: ~0.74

**What surprised me:** The rule-based retriever (Step 2) performed better than expected on edge cases. When Gemini's preference parsing returned slightly off values, the scoring function still surfaced reasonable candidates because energy closeness is a continuous score rather than a binary match.

---

## Reflection

Building this system taught me that **the hardest part of applied AI is not the model — it's the interface between natural language and structured logic.** The agentic pipeline made this gap explicit: Step 1 (parsing) is where most failures happen, and a good fallback strategy (defaulting to neutral preferences) is more valuable than trying to make the LLM parse perfectly every time.

I also learned that **confidence scoring is genuinely useful**, not just a demo feature. During testing, low-confidence outputs consistently pointed to cases where the user's request was too vague or outside the dataset's coverage — which is exactly the kind of signal a real system would surface to the user.

The project also reinforced that AI collaboration requires iteration. My first version of the ranking prompt produced generic explanations ("this is a good match for your energy level"). After two rounds of prompt refinement, the explanations became specific and useful ("its 80 BPM pace and 0.78 acousticness make it ideal for deep work without becoming a distraction").
