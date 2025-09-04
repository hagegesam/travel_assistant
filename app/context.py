# app/context.py
from __future__ import annotations
import json, os
from typing import Dict, Any

STATE_PATH = os.getenv("SESSION_STATE_PATH", "session_state.json")

DEFAULT_CONTEXT = {
    "destination": None,
    "date_info": {"month": None, "year": None},
    "preferences": {"budget": None, "style": []},
    "party": None,
}

def load_context(session_id: str) -> Dict[str, Any]:
    if not os.path.exists(STATE_PATH):
        return {session_id: DEFAULT_CONTEXT.copy()}
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if session_id not in data:
                data[session_id] = DEFAULT_CONTEXT.copy()
            return data
        except Exception:
            return {session_id: DEFAULT_CONTEXT.copy()}

def save_context(session_id: str, ctx: Dict[str, Any]) -> None:
    data = load_context(session_id)
    data[session_id] = ctx
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def to_context_card(ctx: Dict[str, Any]) -> str:
    dest = ctx.get("destination") or "unknown"
    di = ctx.get("date_info") or {}
    month = di.get("month") or "unknown"
    year = di.get("year") or "unknown"
    prefs = ctx.get("preferences") or {}
    budget = prefs.get("budget") or "unknown"
    style = ", ".join(prefs.get("style") or []) or "unknown"
    party = ctx.get("party") or "unknown"
    return f"Destination: {dest}\nWhen: {month} {year}\nBudget: {budget}\nStyle: {style}\nParty: {party}"

def merge_router_into_context(ctx: Dict[str, Any], router_json: Dict[str, Any]) -> Dict[str, Any]:
    # Update destination (take first if provided)
    dests = router_json.get("destinations") or []
    if dests:
        ctx["destination"] = dests[0]
    # Update date
    di = router_json.get("date_info") or {}
    if di.get("month") and di["month"] != "unknown":
        ctx["date_info"]["month"] = di["month"]
    if di.get("year") and di["year"] != "unknown":
        ctx["date_info"]["year"] = di["year"]
    # Budget and style
    prefs = router_json.get("preferences") or {}
    if prefs.get("budget") and prefs["budget"] != "unknown":
        ctx["preferences"]["budget"] = prefs["budget"]
    if prefs.get("style"):
        # merge unique
        existing = set(ctx["preferences"].get("style") or [])
        for s in prefs["style"]:
            if s not in existing:
                existing.add(s)
        ctx["preferences"]["style"] = list(existing)
    # Party
    p = router_json.get("party")
    if p and p != "unknown":
        ctx["party"] = p
    return ctx
