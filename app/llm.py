# app/llm.py
from __future__ import annotations
import os, json, requests
from typing import Dict, Any, Optional

OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")

def _ollama_generate(prompt: str, system: Optional[str] = None, stream: bool = False) -> str:
    """Call Ollama's /api/generate endpoint with an optional system prompt."""
    url = f"{OLLAMA_BASE}/api/generate"
    payload = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": stream,
    }
    if system:
        payload["system"] = system
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    # Ollama returns a line-delimited JSON stream even with stream=False; join 'response' fields.
    text = ""
    for line in resp.iter_lines(decode_unicode=True):
        if not line:
            continue
        try:
            data = json.loads(line)
            if "response" in data:
                text += data["response"]
        except json.JSONDecodeError:
            continue
    return text.strip()

def gen_router_json(context_card: str, user_message: str) -> Dict[str, Any]:
    from .prompts import ROUTER_PROMPT
    prompt = f"CONTEXT CARD:\n{context_card}\n\nLAST USER MESSAGE:\n{user_message}\n\n{ROUTER_PROMPT}"
    out = _ollama_generate(prompt)
    # Try to extract JSON
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        # Attempt naive fix by finding first/last braces
        start = out.find("{")
        end = out.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(out[start:end+1])
            except Exception:
                pass
        return {"intent": "other", "needs_weather": False, "needs_country_info": False, "clarifying_questions": ["Could you rephrase or add details?"]}

def gen_final_answer(system_prompt: str, context_card: str, router_json: Dict[str, Any], tool_results: Dict[str, Any], user_message: str) -> str:
    from .prompts import ANSWER_PROMPT
    payload = f"""CONTEXT CARD:
{context_card}

ROUTER JSON:
{json.dumps(router_json, ensure_ascii=False, indent=2)}

TOOL RESULTS:
{json.dumps(tool_results, ensure_ascii=False, indent=2)}

LATEST USER MESSAGE:
{user_message}

{ANSWER_PROMPT}
"""
    return _ollama_generate(payload, system=system_prompt)
