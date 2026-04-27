# System Architecture — AI Music Recommender

## Mermaid Diagram Source

Copy this into [Mermaid Live Editor](https://mermaid.live) and export as PNG → save as `assets/architecture.png`.

```mermaid
flowchart TD
    A["👤 User Input\n(Natural Language)"] --> B

    subgraph Agent["Agentic Workflow — 3 Observable Steps"]
        B["Step 1: Preference Parser\nClaude claude-sonnet-4-6\nNL → structured prefs"]
        B --> C["Structured Preferences\ngenre · mood · energy · acoustic"]
        C --> D["Step 2: Song Retriever\nRule-Based Scoring Engine\n40-song library"]
        D --> E["Top 10 Candidates\n(scored + ranked)"]
        E --> F["Step 3: AI Ranker\nClaude claude-sonnet-4-6\nRe-rank + explain"]
    end

    F --> G["Confidence Evaluator\nScore 0.0–1.0"]
    G --> H["✅ Final Output\nTop 3–5 recs + explanations\n+ confidence score"]

    I["📁 Logger\nlogs/recommender.log"] -. "logs every step" .-> B
    I -. "logs every step" .-> D
    I -. "logs every step" .-> F

    J["🧪 Test Harness\ntests/test_harness.py\n6 predefined cases"] --> B
```

## Component Summary

| Component | File | Role |
|---|---|---|
| Preference Parser | `src/llm_client.py` | Claude converts NL to structured dict |
| Song Retriever | `src/recommender.py` | Rule-based scoring over 40-song dataset |
| AI Ranker | `src/llm_client.py` | Claude re-ranks candidates with explanations |
| Confidence Evaluator | `src/evaluator.py` | Scores match quality 0.0–1.0 |
| Agent Orchestrator | `src/ai_agent.py` | Runs and displays all 3 steps |
| Logger | `src/logger.py` | Structured JSON logging to file |
| Test Harness | `tests/test_harness.py` | Automated 6-case evaluation script |
