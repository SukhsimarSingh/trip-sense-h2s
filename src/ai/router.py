# src/ai/router.py
from __future__ import annotations

from typing import Any, Callable, Dict, List, TypedDict
import logging

from .handlers import (
    search_text,
    get_nearby_attractions,
    get_nearby_restaurants,
    get_hotels,
    get_weather,
    save_trip,
)

logger = logging.getLogger(__name__)

# --- Types -------------------------------------------------------------------

class ToolCall(TypedDict):
    name: str
    args: Dict[str, Any]

class ToolOutput(TypedDict, total=False):
    function_call: Dict[str, str]
    output: Any
    error: str

# Handlers take a single args dict and return JSON-serializable data.
Handler = Callable[[Dict[str, Any]], Any]

# --- Router table ------------------------------------------------------------

TOOL_ROUTER: Dict[str, Handler] = {
    "search_text": search_text,
    "get_nearby_attractions": get_nearby_attractions,
    "get_nearby_restaurants": get_nearby_restaurants,
    "get_hotels": get_hotels,
    "get_weather": get_weather,
    "save_trip": save_trip,
}

# --- Dispatch helpers --------------------------------------------------------

def dispatch_tool(name: str, args: Dict[str, Any]) -> ToolOutput:
    """Safely dispatch a single tool call to the matching handler."""
    handler = TOOL_ROUTER.get(name)
    if handler is None:
        msg = f"Unknown tool: {name}"
        logger.warning(msg)
        return {"function_call": {"name": name}, "error": msg}

    try:
        result = handler(args)  # handlers expect a single dict
        return {"function_call": {"name": name}, "output": result}
    except Exception as exc:  # keep going even if one tool fails
        logger.exception("Tool '%s' failed with args=%s", name, args)
        return {"function_call": {"name": name}, "error": str(exc)}

def execute_tool_calls(calls: List[ToolCall]) -> List[ToolOutput]:
    """Execute a batch of model-suggested tool calls."""
    outputs: List[ToolOutput] = []
    for call in calls:
        name = call.get("name", "")
        args = call.get("args", {}) or {}
        outputs.append(dispatch_tool(name, args))
    return outputs