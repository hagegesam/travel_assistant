# Travel Assistant (Conversation‑First, Prompt‑Engineered)

A small, **conversation‑first** travel assistant focused on **prompt engineering**, **context management**, and **data augmentation** (weather + country info).

- Interface: **CLI**
- LLM: **Ollama** (default, local & free). Tested with `llama3`.
- External APIs:
  - **Open‑Meteo** (no key) for weather
  - **REST Countries** (no key) for country info
- Context: Persisted per session in `./session_state.json` (destination, dates/season, party, budget, preferences).

This project is intentionally simple: the value is in **prompts**, **flow**, and **error‑handling** rather than heavy infra.

---

## Quick Start

1) Install [Ollama](https://ollama.com/) and pull a model (e.g. `llama3`):

```bash
ollama pull llama3
```

2) Create a Python env & install deps:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3) Run the CLI:

```bash
python -m app.main --session demo
```

Then chat freely. Examples:
```
> I’m thinking about a 4-day trip in April. Where should I go if I like food and history?
> What should I pack if I choose Rome?
> And what are must-see attractions near my hotel in Trastevere?
```

---

## Design Overview

### Conversation‑First Flow
We run a **two‑phase** call per user message:
1. **Router Pass** (LLM): extract structured control JSON (intent, entities, flags).
2. **Data Pass** (client): call external APIs if needed (e.g., weather for packing).
3. **Answer Pass** (LLM): provide final user‑visible reply, blending fetched data + context.

We persist a **Context Card** (destination, dates/season, party, budget, prefs). The assistant adapts when user changes plans (“actually May, not April”).

### Prompt Engineering Highlights
- Clear **System Prompt** persona and policies (concise, helpful, travel‑savvy).
- **Hidden reasoning** (“think step‑by‑step, but don’t reveal the scratchpad”) to meet the *chain‑of‑thought* requirement safely.
- **Router Prompt** enforces strict JSON output for tool decisions (no CoT leakage).
- **Answer Prompt** blends context + tool results; instructs the model to be **concise by default**, with **opt‑in expansion** (“Say ‘Want more detail?’”).

### Decision Framework (API vs. LLM)
- Use **external APIs** for **time‑sensitive or numeric facts** (weather, temps, currency code).
- Use **LLM** for **opinionated/open‑ended** queries (attractions, vibe, itinerary ideas).
- Router sets flags: `needs_weather`, `needs_country_info` based on user message + context.

### Error Handling
- If API fails: graceful fallback + low‑confidence phrasing.
- If router JSON fails: retry once, then default to best‑effort assumptions.
- Hallucination guardrails: “If unsure, ask a brief clarifying question or say you’re not sure.”

---

## Demonstration Targets (Assignment Mapping)

- **3+ Query Types**: destination recommendations, packing suggestions (weather‑aware), local attractions/food tips.
- **Context Maintenance**: destination/date changes, preferences, travel party, budget.
- **Enhanced Prompting**: system + router + answer prompts, hidden reasoning directive.
- **Data Augmentation**: Open‑Meteo & REST Countries; blending in final answers.
- **Simple Technical Impl.**: Python CLI, Ollama HTTP API.
- **Transcripts**: see `sample_transcripts/`.

---

## Configuration

- Default model: `LLM_MODEL=llama3`
- Ollama endpoint: `OLLAMA_BASE=http://localhost:11434`
- Edit in `.env` or environment variables.

---

## Run Sample Script (Non‑Interactive)

You can also pass a one‑off prompt:
```bash
python -m app.main --session demo -m "Plan 3 days in Lisbon in June with a focus on food and light hiking."
```

---

## Notes on “Chain‑of‑Thought”

We *guide* multi‑step reasoning in the prompts but instruct the model to **keep reasoning hidden** and produce only the final, concise answer. This shows you can design CoT‑style prompts responsibly without exposing raw chain‑of‑thought to users.

---

## License

MIT
