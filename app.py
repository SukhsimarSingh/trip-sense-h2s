import os
import json
import re
import time
from typing import Dict, Any, List, Optional

import dotenv
dotenv.load_dotenv()

import streamlit as st

# --- Optional providers (only used if API keys/creds exist) ---
try:
    from google import genai
    from google.genai import types as genai_types
    HAS_GEMINI = True
except Exception:
    HAS_GEMINI = False

try:
    import googlemaps
    HAS_GMAPS = True
except Exception:
    HAS_GMAPS = False

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    HAS_FIREBASE = True
except Exception:
    HAS_FIREBASE = False

# =========================
# Config & Clients
# =========================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
FIREBASE_CREDENTIALS_JSON = os.getenv("FIREBASE_CREDENTIALS_JSON")  # path or JSON string

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

if HAS_GEMINI and GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    gemini_client = None

if HAS_GMAPS and GOOGLE_MAPS_API_KEY:
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
else:
    gmaps = None

if HAS_FIREBASE and FIREBASE_CREDENTIALS_JSON:
    try:
        if os.path.exists(FIREBASE_CREDENTIALS_JSON):
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_JSON)
        else:
            cred = credentials.Certificate(json.loads(FIREBASE_CREDENTIALS_JSON))
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception:
        db = None
else:
    db = None

# =========================
# Streamlit App Layout
# =========================
st.set_page_config(page_title="Trip Planner (Gemini + Maps)", page_icon="🧭", layout="wide")
st.title("🧭 Trip Planner — Gemini + Google Maps + Firebase")

# Sidebar status
with st.sidebar:
    st.subheader("Status")
    st.write(f"Gemini SDK: {'✅' if gemini_client else '❌'}")
    st.write(f"Google Maps: {'✅' if gmaps else '❌'}")
    st.write(f"Firebase: {'✅' if db else '❌'}")
    st.markdown("---")
    st.caption("Tip: Create a `.env` with GEMINI_API_KEY, GOOGLE_MAPS_API_KEY, and optional FIREBASE_CREDENTIALS_JSON.")

# =========================
# System Prompt & Tool Protocol
# =========================
SYSTEM_INSTRUCTION = (
    "You are an expert AI trip planner. Plan realistic itineraries with travel times, costs, and flexible options.\n"
    "If a tool is needed (maps, save, etc.), respond with a single JSON object only, no extra text, using this schema:\n"
    "{\n  'tool': 'search_places'|'directions'|'time_distance'|'save_itinerary'|'fetch_weather',\n"
    "  'params': { ... }\n}\n"
    "Examples:\n"
    "1) { 'tool':'search_places', 'params': {'query': 'cafes in Manali', 'limit': 5} }\n"
    "2) { 'tool':'directions', 'params': {'origin': 'Delhi', 'destination': 'Manali', 'mode': 'driving'} }\n"
    "3) { 'tool':'save_itinerary', 'params': {'name': 'Himachal 5D', 'itinerary': {...}} }\n"
    "When no tool is necessary, answer conversationally. Keep responses concise and user-friendly."
)

# =========================
# Session State
# =========================
if "messages" not in st.session_state:
    st.session_state.messages: List[Dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "assistant", "content": "Hi! I can help plan trips. Tell me destination, dates, budget, interests."},
    ]

# =========================
# Helper: Render chat
# =========================
def render_chat():
    for m in st.session_state.messages:
        if m["role"] == "system":
            continue
        with st.chat_message("assistant" if m["role"] == "assistant" else "user"):
            if isinstance(m["content"], dict):
                st.json(m["content"])
            else:
                st.markdown(m["content"])

# =========================
# Tooling Layer (Maps, Weather, Firebase)
# =========================

def tool_search_places(params: Dict[str, Any]) -> Dict[str, Any]:
    """Search places with Google Places Text Search (via googlemaps)."""
    if not gmaps:
        return {"error": "Google Maps not configured"}
    query = params.get("query", "")
    limit = int(params.get("limit", 5))
    try:
        results = gmaps.places(query=query)
        places = []
        for r in results.get("results", [])[:limit]:
            places.append({
                "name": r.get("name"),
                "address": r.get("formatted_address"),
                "rating": r.get("rating"),
                "user_ratings_total": r.get("user_ratings_total"),
                "location": r.get("geometry", {}).get("location", {}),
                "place_id": r.get("place_id"),
            })
        return {"places": places}
    except Exception as e:
        return {"error": str(e)}


def tool_directions(params: Dict[str, Any]) -> Dict[str, Any]:
    if not gmaps:
        return {"error": "Google Maps not configured"}
    origin = params.get("origin")
    destination = params.get("destination")
    mode = params.get("mode", "driving")
    try:
        routes = gmaps.directions(origin, destination, mode=mode)
        if not routes:
            return {"error": "No routes found"}
        leg = routes[0]["legs"][0]
        polyline = routes[0].get("overview_polyline", {}).get("points")
        return {
            "summary": routes[0].get("summary"),
            "distance": leg.get("distance", {}).get("text"),
            "duration": leg.get("duration", {}).get("text"),
            "start_address": leg.get("start_address"),
            "end_address": leg.get("end_address"),
            "polyline": polyline,
        }
    except Exception as e:
        return {"error": str(e)}


def tool_time_distance(params: Dict[str, Any]) -> Dict[str, Any]:
    if not gmaps:
        return {"error": "Google Maps not configured"}
    origins = params.get("origins")
    destinations = params.get("destinations")
    mode = params.get("mode", "driving")
    try:
        matrix = gmaps.distance_matrix(origins, destinations, mode=mode)
        out = []
        for i, row in enumerate(matrix.get("rows", [])):
            for j, elem in enumerate(row.get("elements", [])):
                out.append({
                    "origin": origins[i],
                    "destination": destinations[j],
                    "distance": elem.get("distance", {}).get("text"),
                    "duration": elem.get("duration", {}).get("text"),
                    "status": elem.get("status"),
                })
        return {"pairs": out}
    except Exception as e:
        return {"error": str(e)}


def tool_save_itinerary(params: Dict[str, Any]) -> Dict[str, Any]:
    if not db:
        return {"error": "Firebase not configured"}
    name = params.get("name", f"Trip-{int(time.time())}")
    itinerary = params.get("itinerary", {})
    try:
        doc = db.collection("itineraries").document()
        doc.set({"name": name, "itinerary": itinerary, "created_at": time.time()})
        return {"ok": True, "id": doc.id}
    except Exception as e:
        return {"error": str(e)}


def tool_fetch_weather(params: Dict[str, Any]) -> Dict[str, Any]:
    # Stub: plug any free weather API here. Returning a mocked response for now.
    return {
        "location": params.get("location", "Unknown"),
        "forecast": [
            {"day": "Day 1", "summary": "Sunny", "temp_c": 24},
            {"day": "Day 2", "summary": "Partly cloudy", "temp_c": 22},
            {"day": "Day 3", "summary": "Light rain", "temp_c": 20},
        ],
    }

TOOL_ROUTER = {
    "search_places": tool_search_places,
    "directions": tool_directions,
    "time_distance": tool_time_distance,
    "save_itinerary": tool_save_itinerary,
    "fetch_weather": tool_fetch_weather,
}

# =========================
# LLM Call
# =========================

def call_gemini(chat_history: List[Dict[str, str]], user_text: str) -> str:
    """Send a prompt with lightweight history to Gemini. Returns response text."""
    if not gemini_client:
        return "(Local demo) Describe your trip: destination, days, budget, interests."

    # Build contents: concatenate last N messages for simplicity
    last_k = 8
    convo_text = []
    for m in chat_history[-last_k:]:
        if m.get("role") == "assistant":
            convo_text.append(f"Assistant: {m.get('content')}")
        elif m.get("role") == "user":
            convo_text.append(f"User: {m.get('content')}")
    convo_text.append(f"User: {user_text}")
    joined = "\n".join(convo_text)

    try:
        resp = gemini_client.models.generate_content(
            model=MODEL_NAME,
            contents=joined,
            config=genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                # Disable private chain-of-thought; we only need final output
                thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
                temperature=0.7,
                max_output_tokens=2048,
            ),
        )
        return resp.text or "(No response text)"
    except Exception as e:
        return f"[Gemini error] {e}"

# =========================
# Tool-call Parser
# =========================
TOOL_JSON_RE = re.compile(r"\{\s*'tool'\s*:\s*'(?P<tool>[^']+)'\s*,\s*'params'\s*:\s*(?P<params>\{.*\})\s*\}\s*$", re.S)


def try_parse_tool_call(text: str) -> Optional[Dict[str, Any]]:
    # Accept both single and double quotes JSON-like
    candidate = text.strip()
    # Normalize single quotes -> double quotes for json parsing
    try:
        if candidate.startswith("{") and "'tool'" in candidate:
            jf = candidate.replace("'", '"')
            data = json.loads(jf)
            if isinstance(data, dict) and "tool" in data and "params" in data:
                return data
    except Exception:
        pass
    # Fallback regex
    m = TOOL_JSON_RE.search(text)
    if m:
        tool = m.group("tool")
        params = m.group("params")
        try:
            params = json.loads(params.replace("'", '"'))
        except Exception:
            params = {"raw": params}
        return {"tool": tool, "params": params}
    return None

# =========================
# Main Chat UI
# =========================
render_chat()

user_input = st.chat_input("Tell me where, when, budget, interests…")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            model_text = call_gemini(st.session_state.messages, user_input)

        # Try to interpret as tool call
        tool_call = try_parse_tool_call(model_text)
        if tool_call:
            tool_name = tool_call.get("tool")
            params = tool_call.get("params", {})
            fn = TOOL_ROUTER.get(tool_name)
            if not fn:
                st.warning(f"Unknown tool: {tool_name}")
                st.json(tool_call)
                st.session_state.messages.append({"role": "assistant", "content": tool_call})
            else:
                result = fn(params)
                st.success(f"Tool: {tool_name}")
                st.json({"params": params, "result": result})
                st.session_state.messages.append({"role": "assistant", "content": {"tool": tool_name, "params": params, "result": result}})

                # Helpful visualizations for certain tools
                if tool_name == "search_places" and isinstance(result, dict):
                    locs = [p.get("location", {}) for p in result.get("places", []) if p.get("location")]
                    if locs:
                        st.map(
                            data={"lat": [l.get("lat") for l in locs], "lon": [l.get("lng") for l in locs]},
                            latitude="lat",
                            longitude="lon",
                            zoom=11,
                        )
                if tool_name == "directions" and isinstance(result, dict):
                    st.info(f"{result.get('summary','')} • {result.get('distance','?')} • {result.get('duration','?')}")
        else:
            st.markdown(model_text)
            st.session_state.messages.append({"role": "assistant", "content": model_text})

# =========================
# Utility: Quick actions
# =========================
with st.expander("Quick prompts"):
    cols = st.columns(3)
    if cols[0].button("5-day Himachal on a budget"):
        st.session_state.messages.append({"role": "user", "content": "Plan a 5-day budget trip to Himachal for 3 friends in October. Hiking + cafes."})
        st.experimental_rerun()
    if cols[1].button("Show cafes in Manali"):
        st.session_state.messages.append({"role": "user", "content": "Find top-rated cafes in Manali near Mall Road."})
        st.experimental_rerun()
    if cols[2].button("Delhi → Manali drive time"):
        st.session_state.messages.append({"role": "user", "content": "What's the driving time from Delhi to Manali?"})
        st.experimental_rerun()

st.caption("This is a hackathon-ready chat interface. Add real tool-calling via Gemini function tools later if desired.")