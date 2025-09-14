import os
import json
import re
import time
from typing import Dict, Any, List, Optional
from serpapi import GoogleSearch

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
SYSTEM_INSTRUCTION = """You are an expert AI trip planner with access to real-time tools.

CRITICAL: When users ask for specific places, attractions, or themed spots, you MUST respond with ONLY a JSON tool call, no other text.

TOOL USAGE RULES:
- User wants nightclubs, bars, pubs → {"tool": "search_theme_based_spots", "params": {"theme": "nightlife", "location": "CITY"}}
- User wants beaches, hidden spots → {"tool": "search_theme_based_spots", "params": {"theme": "beaches", "location": "CITY"}}  
- User wants restaurants, cafes → {"tool": "search_places", "params": {"query": "restaurants", "location": "CITY"}}
- User wants hotels, accommodation → {"tool": "search_places", "params": {"query": "hotels", "location": "CITY"}}
- User needs directions → {"tool": "directions", "params": {"origin": "START", "destination": "END"}}
- User wants weather → {"tool": "fetch_weather", "params": {"location": "CITY"}}

EXAMPLES:
Query: "find nightclubs in Goa" 
Response: {"tool": "search_theme_based_spots", "params": {"theme": "nightlife", "location": "Goa"}}

Query: "show me hidden beaches in Goa"
Response: {"tool": "search_theme_based_spots", "params": {"theme": "hidden beaches", "location": "Goa"}}

Query: "best restaurants in Baga"
Response: {"tool": "search_places", "params": {"query": "restaurants", "location": "Baga, Goa"}}

For general planning advice, respond conversationally.
"""

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

def tool_search_spots(params: Dict[str, Any]) -> Dict[str, Any]:
    params = {
        "q": params.get("theme", "Unknown"),
        "location": params.get("location", "Unknown"),
        "hl": "en",
        "gl": "us",
        "google_domain": "google.com",
        "api_key": "2a17ba0d377323a7bfb4b227bd8e93161ed365abfda0deb69b493088e59e33f6"
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    print("THEME BASED SEARCH : ", results)
    return results

TOOL_ROUTER = {
    "search_places": tool_search_places,
    "directions": tool_directions,
    "time_distance": tool_time_distance,
    "save_itinerary": tool_save_itinerary,
    "fetch_weather": tool_fetch_weather,
    "search_theme_based_spots": tool_search_spots,
}

# =========================
# LLM Call
# =========================

def call_gemini(chat_history: List[Dict[str, str]], user_text: str) -> str:
    """Enhanced Gemini call with better tool triggering"""
    
    if not gemini_client:
        return "(Local demo) Please configure Gemini API key"

    print(f"\n[GEMINI DEBUG] User input: {user_text}")
    
    # Check for tool-requiring keywords
    tool_triggers = [
        'find', 'search', 'show', 'get', 'list', 'where', 
        'nightclub', 'beach', 'restaurant', 'hotel', 'bar', 'cafe',
        'hidden', 'secret', 'best', 'top', 'popular'
    ]
    
    user_lower = user_text.lower()
    needs_tool = any(trigger in user_lower for trigger in tool_triggers)
    
    print(f"[GEMINI DEBUG] Needs tool: {needs_tool}")
    
    if needs_tool:
        # Force tool usage prompt
        prompt = f"""
            {SYSTEM_INSTRUCTION}

            IMPORTANT: The user request below requires real-time data. Respond with ONLY a JSON tool call.

            User: {user_text}

            Analyze and respond with the appropriate tool call in JSON format:
            """
    else:
        # Regular conversation with context
        context = []
        for m in chat_history[-6:]:
            if m.get("role") == "assistant":
                context.append(f"Assistant: {m.get('content', '')}")
            elif m.get("role") == "user":
                context.append(f"User: {m.get('content', '')}")
        
        context.append(f"User: {user_text}")
        prompt = f"{SYSTEM_INSTRUCTION}\n\n" + "\n".join(context)

    try:
        resp = gemini_client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.1,  # Low temperature for consistent tool calls
                max_output_tokens=1000,
            ),
        )     
        response_text = resp.text or "No response"
        print(f"[GEMINI DEBUG] Response: {response_text}")
        return response_text
    except Exception as e:
        print(f"[GEMINI DEBUG] Error: {e}")
        return f"[Gemini error] {e}"
    
# =========================
# Tool-call Parser
# =========================
TOOL_JSON_RE = re.compile(r"\{\s*'tool'\s*:\s*'(?P<tool>[^']+)'\s*,\s*'params'\s*:\s*(?P<params>\{.*\})\s*\}\s*$", re.S)


def try_parse_tool_call(text: str) -> Optional[Dict[str, Any]]:
    """Enhanced parser with debugging"""
    
    print(f"\n[PARSER DEBUG] Input text: {text[:200]}...")
    
    text = text.strip()
    
    # Strategy 1: Direct JSON
    if text.startswith('{') and text.endswith('}'):
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "tool" in data:
                print(f"[PARSER DEBUG] SUCCESS - Direct JSON: {data}")
                return data
        except:
            pass
    
    # Strategy 2: Single quotes to double quotes
    if text.startswith('{'):
        try:
            normalized = text.replace("'", '"')
            data = json.loads(normalized)
            if isinstance(data, dict) and "tool" in data:
                print(f"[PARSER DEBUG] SUCCESS - Quote normalized: {data}")
                return data
        except:
            pass
    
    # Strategy 3: Extract JSON pattern
    json_match = re.search(r'\{[^{}]*"tool"[^{}]*\}', text)
    if json_match:
        try:
            data = json.loads(json_match.group())
            if isinstance(data, dict) and "tool" in data:
                print(f"[PARSER DEBUG] SUCCESS - Pattern match: {data}")
                return data
        except:
            pass
    
    # Strategy 4: Manual extraction
    tool_match = re.search(r'"tool"\s*:\s*"([^"]+)"', text)
    if tool_match:
        tool_name = tool_match.group(1)
        params = {}
        
        # Try to extract params
        params_match = re.search(r'"params"\s*:\s*(\{[^}]*\})', text)
        if params_match:
            try:
                params = json.loads(params_match.group(1))
            except:
                pass
        
        result = {"tool": tool_name, "params": params}
        print(f"[PARSER DEBUG] SUCCESS - Manual extraction: {result}")
        return result
    
    print("[PARSER DEBUG] FAILED - No valid tool call found")
    return None

# =========================
# FIXED CHAT INPUT HANDLER (Replace your current chat input section)
# =========================

# Replace this section in your Streamlit app:
render_chat()

user_input = st.chat_input("Tell me where, when, budget, interests…")
if user_input:
    print(f"\n{'='*60}")
    print(f"NEW USER INPUT: {user_input}")
    print(f"{'='*60}")
    
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Planning your trip..."):
            
            # Get LLM response
            model_text = call_gemini(st.session_state.messages, user_input)
            
            print(f"[MAIN DEBUG] LLM returned: {model_text}")

        # Try to interpret as tool call
        tool_call = try_parse_tool_call(model_text)
        
        if tool_call:
            tool_name = tool_call.get("tool")
            params = tool_call.get("params", {})
            fn = TOOL_ROUTER.get(tool_name)
            
            print(f"[MAIN DEBUG] Tool call detected: {tool_name} with {params}")
            
            if not fn:
                st.warning(f"Unknown tool: {tool_name}")
                st.json(tool_call)
                st.session_state.messages.append({"role": "assistant", "content": tool_call})
            else:
                # Execute tool
                st.info(f"🔧 Searching with {tool_name}...")
                result = fn(params)
                
                print(f"[MAIN DEBUG] Tool result: {result}")
                
                # Display results based on tool type
                if "error" in result:
                    st.error(f"❌ Error: {result['error']}")
                else:
                    # Success display
                    if tool_name == "search_theme_based_spots":
                        spots = result.get("spots", [])
                        theme = result.get("theme_searched", params.get("theme", "spots"))
                        
                        st.success(f"✅ Found {len(spots)} {theme} spots!")
                        
                        if spots:
                            for spot in spots[:6]:  # Show top 6
                                with st.expander(f"🎯 {spot.get('name', 'Unknown')} - ⭐ {spot.get('rating', 'N/A')}"):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        if spot.get('address'):
                                            st.write(f"📍 **Address:** {spot['address']}")
                                        if spot.get('type'):
                                            st.write(f"🏷️ **Type:** {spot['type']}")
                                        if spot.get('rating'):
                                            st.write(f"⭐ **Rating:** {spot['rating']}")
                                    with col2:
                                        if spot.get('phone'):
                                            st.write(f"📞 **Phone:** {spot['phone']}")
                                        if spot.get('website'):
                                            st.write(f"🌐 **Website:** [Visit]({spot['website']})")
                                        if spot.get('hours'):
                                            st.write(f"🕒 **Hours:** {spot['hours']}")
                                    
                                    if spot.get('description'):
                                        st.write(f"📝 **Description:** {spot['description']}")
                        else:
                            st.warning("No results found. Try a different search term.")
                    
                    elif tool_name == "search_places":
                        places = result.get("places", [])
                        st.success(f"✅ Found {len(places)} places!")
                        
                        for place in places[:5]:
                            with st.expander(f"📍 {place.get('name', 'Unknown')} - ⭐ {place.get('rating', 'N/A')}"):
                                st.write(f"🏠 **Address:** {place.get('address', 'N/A')}")
                                if place.get('phone'):
                                    st.write(f"📞 **Phone:** {place['phone']}")
                                if place.get('website'):
                                    st.write(f"🌐 **Website:** [Visit]({place['website']})")
                        
                        # Show map if we have locations
                        locs = [p.get("location", {}) for p in places if p.get("location")]
                        if locs:
                            st.map(
                                data={"lat": [l.get("lat") for l in locs], "lon": [l.get("lng") for l in locs]},
                                latitude="lat",
                                longitude="lon",
                                zoom=11,
                            )
                    
                    elif tool_name == "directions":
                        routes = result.get("routes", [])
                        if routes:
                            route = routes[0]
                            st.info(f"🗺️ {route.get('summary','')} • {route.get('distance','?')} • {route.get('duration','?')}")
                        else:
                            st.json(result)
                    
                    else:
                        st.json(result)

                # Store tool call result
                st.session_state.messages.append({"role": "assistant", "content": {"tool": tool_name, "params": params, "result": result}})
                
                # Generate follow-up advice if tool succeeded
                if "error" not in result and len(result.get("spots", result.get("places", []))) > 0:
                    st.markdown("---")
                    with st.spinner("Generating travel advice..."):
                        advice_prompt = f"Based on the {tool_name} results, provide brief travel tips and suggestions for the user's trip to help them make the most of these {tool_name.replace('_', ' ')} options."
                        advice = call_gemini(st.session_state.messages, advice_prompt)
                        
                        # Make sure advice is not another tool call
                        if not try_parse_tool_call(advice):
                            st.markdown("### 💡 Travel Tips:")
                            st.markdown(advice)
                            st.session_state.messages.append({"role": "assistant", "content": advice})

        else:
            # No tool call - regular response
            print("[MAIN DEBUG] No tool call detected - responding normally")
            st.markdown(model_text)
            st.session_state.messages.append({"role": "assistant", "content": model_text})
            
            # Suggest specific tool queries
            if any(word in user_input.lower() for word in ['nightclub', 'beach', 'restaurant', 'find', 'show']):
                st.info("💡 **Try specific requests like:**\n- 'Find nightclubs in Goa'\n- 'Show hidden beaches in Goa'\n- 'Search for beach restaurants in North Goa'")

# =========================
# TEST YOUR SPECIFIC QUERY
# =========================

# Add this button for testing
if st.button("🧪 Test Goa Query", key="test_goa"):
    test_query = "find nightclubs and hidden beaches in Goa for New Year celebration"
    st.session_state.messages.append({"role": "user", "content": test_query})
    st.rerun()