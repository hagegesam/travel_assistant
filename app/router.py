# app/router.py
from __future__ import annotations
from typing import Dict, Any, Tuple, Optional
from .llm import gen_router_json

def route_message(context_card: str, user_message: str) -> Dict[str, Any]:
    return gen_router_json(context_card, user_message)
