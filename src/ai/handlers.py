from __future__ import annotations

import os
import requests
from typing import Any, Dict, List, Literal, Optional, TypedDict
from .trip_storage import trip_storage

# ----------------------------------
# Config & endpoints
# ----------------------------------
MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
PLACES_SEARCH_TEXT = "https://places.googleapis.com/v1/places:searchText"
PLACES_SEARCH_NEARBY = "https://places.googleapis.com/v1/places:searchNearby"
WEATHER_DAYS_URL = "https://weather.googleapis.com/v1/forecast:days"

BASE_FIELD_MASK = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.location",
        "places.formattedAddress",
        "places.rating",
        "places.userRatingCount",
        "places.priceLevel",
        "places.googleMapsUri",
        "places.primaryType",
        "places.primaryTypeDisplayName",
        "places.currentOpeningHours.weekdayDescriptions",
    ]
)

# Note: MAPS_API_KEY will be checked in individual functions to allow demo mode

_SESSION = requests.Session()


# ----------------------------------
# Output typing (optional but handy)
# ----------------------------------
class Place(TypedDict, total=False):
    id: str
    name: str
    latitude: float
    longitude: float
    address: str
    rating: float
    user_ratings_total: int
    price_level: int
    maps_url: str
    primary_type: str
    primary_type_display_name: str
    weekday_descriptions: List[str]


def _normalize_place(p: Dict[str, Any]) -> Place:
    loc = p.get("location", {})
    return Place(
        id=p.get("id", ""),
        name=(p.get("displayName", {}) or {}).get("text", ""),
        latitude=loc.get("latitude"),
        longitude=loc.get("longitude"),
        address=p.get("formattedAddress", ""),
        rating=p.get("rating", 0.0),
        user_ratings_total=p.get("userRatingCount", 0),
        price_level=p.get("priceLevel", 0),
        maps_url=p.get("googleMapsUri", ""),
        primary_type=p.get("primaryType", ""),
        primary_type_display_name=p.get("primaryTypeDisplayName", ""),
        weekday_descriptions=(p.get("currentOpeningHours", {}) or {}).get(
            "weekdayDescriptions", []
        ),
    )


# ----------------------------------
# Shared HTTP helpers
# ----------------------------------
def _post(url: str, body: Dict[str, Any], field_mask: str = BASE_FIELD_MASK) -> Dict[str, Any]:
    """Internal POST with field mask and consistent errors."""
    if not MAPS_API_KEY:
        raise RuntimeError("GOOGLE_MAPS_API_KEY not set. Configure it to use location-based tools.")
    
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": MAPS_API_KEY,
        "X-Goog-FieldMask": field_mask,
    }
    r = _SESSION.post(url, json=body, headers=headers, timeout=20)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        # Handle specific Google API errors
        try:
            error_data = r.json()
            if error_data.get("error", {}).get("code") == 403:
                error_message = error_data.get("error", {}).get("message", "")
                if "Places API" in error_message and "disabled" in error_message:
                    raise RuntimeError("Google Places API is not enabled. Please enable it in your Google Cloud Console to use location-based features.")
                elif "PERMISSION_DENIED" in str(error_data):
                    raise RuntimeError("Google API access denied. Please check your API key permissions.")
        except (ValueError, KeyError):
            pass  # Fall back to generic error
        
        raise RuntimeError(f"Google API error ({url}): {r.text}") from e
    return r.json()


# =====================================================================================
# 1) search_text  — declaration + function
# =====================================================================================

search_text_declaration: Dict[str, Any] = {
    "name": "search_text",
    "description": "Resolve a free-text place (e.g., 'Paris', 'Bangalore MG Road') to one or more matching Places with coordinates.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Free text query for a place, landmark, city, or area.",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum results to return (1-5).",
            },
        },
        "required": ["query"],
    },
}


def search_text(args: Dict[str, Any]) -> List[Place]:
    """Search a place by free text using Places (New) searchText API.

    Args:
        args: Dictionary containing:
            - query: The free text query (e.g., "Paris", "Bangalore MG Road").
            - max_results: Maximum results to return (1-5), defaults to 3.

    Returns:
        A list of normalized Place dicts.
    """
    query = args.get("query", "")
    max_results = args.get("max_results", 3)
    max_results = max(1, min(int(max_results), 5))
    
    data = _post(
        PLACES_SEARCH_TEXT,
        {"textQuery": query, "maxResultCount": max_results},
        field_mask="places.id,places.displayName,places.location,places.googleMapsUri",
    )
    return [_normalize_place(p) for p in data.get("places", [])]


# =====================================================================================
# 2) get_nearby_attractions  — declaration + function
# =====================================================================================

get_nearby_attractions_declaration: Dict[str, Any] = {
    "name": "get_nearby_attractions",
    "description": "Find nearby attractions/sights around a location.",
    "parameters": {
        "type": "object",
        "properties": {
            "lat": {"type": "number", "description": "Latitude in decimal degrees."},
            "lng": {"type": "number", "description": "Longitude in decimal degrees."},
            "radius_m": {
                "type": "integer",
                "description": "Search radius in meters (typ. 2000–15000).",
            },
            "max_results": {"type": "integer", "description": "Max results (<=20)."},
            "min_rating": {
                "type": "number",
                "description": "Optional minimum rating filter (0.0–5.0).",
            },
            "included_types": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Override place types. Default: ['tourist_attraction','museum','park','art_gallery','shopping_mall']",
            },
        },
        "required": ["lat", "lng", "radius_m"],
    },
}


def get_nearby_attractions(args: Dict[str, Any]) -> List[Place]:
    """Return popular attractions near a point.
    
    Args:
        args: Dictionary containing:
            - lat: Latitude in decimal degrees.
            - lng: Longitude in decimal degrees.
            - radius_m: Search radius in meters.
            - max_results: Limit results (optional).
            - min_rating: Minimum rating filter (optional).
            - included_types: List of place types to include (optional).
    """
    lat = float(args.get("lat", 0))
    lng = float(args.get("lng", 0))
    radius_m = int(args.get("radius_m", 1000))
    max_results = args.get("max_results")
    min_rating = args.get("min_rating")
    included_types = args.get("included_types")
    
    types = included_types or [
        "tourist_attraction",
        "museum",
        "park",
        "art_gallery",
        "shopping_mall",
    ]
    return _nearby(lat, lng, radius_m, types, max_results, min_rating)


# =====================================================================================
# 3) get_nearby_restaurants  — declaration + function
# =====================================================================================

get_nearby_restaurants_declaration: Dict[str, Any] = {
    "name": "get_nearby_restaurants",
    "description": "Find nearby restaurants around a location.",
    "parameters": {
        "type": "object",
        "properties": {
            "lat": {"type": "number"},
            "lng": {"type": "number"},
            "radius_m": {"type": "integer"},
            "max_results": {"type": "integer"},
            "min_rating": {"type": "number"},
            "vegetarian_only": {
                "type": "boolean",
                "description": "If true, bias toward vegetarian-friendly results.",
            },
        },
        "required": ["lat", "lng", "radius_m"],
    },
}


def get_nearby_restaurants(args: Dict[str, Any]) -> List[Place]:
    """Return nearby restaurants; can bias toward vegetarian terms.
    
    Args:
        args: Dictionary containing:
            - lat: Latitude in decimal degrees.
            - lng: Longitude in decimal degrees.
            - radius_m: Search radius in meters.
            - max_results: Limit results (optional).
            - min_rating: Minimum rating filter (optional).
            - vegetarian_only: If true, bias toward vegetarian-friendly results.
    """
    lat = float(args.get("lat", 0))
    lng = float(args.get("lng", 0))
    radius_m = int(args.get("radius_m", 1000))
    max_results = args.get("max_results")
    min_rating = args.get("min_rating")
    vegetarian_only = args.get("vegetarian_only", False)
    term_bias = "vegetarian" if vegetarian_only else None
    return _nearby(lat, lng, radius_m, ["restaurant"], max_results, min_rating, term_bias)


# =====================================================================================
# 4) get_hotels  — declaration + function
# =====================================================================================

Accommodation = Literal[
    "Any", "Hotels", "Hostels", "Vacation Rentals", "Resorts", "Boutique Properties"
]

get_hotels_declaration: Dict[str, Any] = {
    "name": "get_hotels",
    "description": "Find nearby lodging (hotels/hostels/resorts/boutique).",
    "parameters": {
        "type": "object",
        "properties": {
            "lat": {"type": "number"},
            "lng": {"type": "number"},
            "radius_m": {"type": "integer"},
            "max_results": {"type": "integer"},
            "min_rating": {"type": "number"},
            "accommodation_filter": {
                "type": "string",
                "enum": [
                    "Any",
                    "Hotels",
                    "Hostels",
                    "Vacation Rentals",
                    "Resorts",
                    "Boutique Properties",
                ],
            },
        },
        "required": ["lat", "lng", "radius_m"],
    },
}


def get_hotels(args: Dict[str, Any]) -> List[Place]:
    """Return nearby lodging filtered by accommodation type.
    
    Args:
        args: Dictionary containing:
            - lat: Latitude in decimal degrees.
            - lng: Longitude in decimal degrees.
            - radius_m: Search radius in meters.
            - max_results: Limit results (optional).
            - min_rating: Minimum rating filter (optional).
            - accommodation_filter: Type of accommodation to filter by.
    """
    lat = float(args.get("lat", 0))
    lng = float(args.get("lng", 0))
    radius_m = int(args.get("radius_m", 1000))
    max_results = args.get("max_results")
    min_rating = args.get("min_rating")
    accommodation_filter = args.get("accommodation_filter", "Any")
    type_map = {
        "Any": ["lodging"],
        "Hotels": ["lodging", "hotel"],
        "Hostels": ["lodging", "hostel"],
        "Vacation Rentals": ["lodging", "vacation_rental"],
        "Resorts": ["lodging", "resort"],
        "Boutique Properties": ["lodging", "boutique_hotel"],
    }
    included_types = type_map.get(accommodation_filter, ["lodging"])
    return _nearby(lat, lng, radius_m, included_types, max_results, min_rating)


# =====================================================================================
# 5) get_weather  — declaration + function
# =====================================================================================

get_weather_declaration: Dict[str, Any] = {
    "name": "get_weather",
    "description": "Get daily weather forecast (1-10 days) for a location.",
    "parameters": {
        "type": "object",
        "properties": {
            "lat": {"type": "number"},
            "lng": {"type": "number"},
            "days": {"type": "integer", "description": "Days of forecast, 1-10."},
            "unit_system": {
                "type": "string",
                "enum": ["METRIC", "IMPERIAL"],
                "description": "Units for temperature/wind.",
            },
        },
        "required": ["lat", "lng"],
    },
}


def get_weather(args: Dict[str, Any]) -> Dict[str, Any]:
    """Daily forecast from Google Weather API.
    
    Args:
        args: Dictionary containing:
            - lat: Latitude in decimal degrees.
            - lng: Longitude in decimal degrees.
            - days: Days of forecast (1-10), defaults to 3.
            - unit_system: Units for temperature/wind ("METRIC" or "IMPERIAL").
    """
    lat = float(args.get("lat", 0))
    lng = float(args.get("lng", 0))
    days = int(args.get("days", 3))
    unit_system = args.get("unit_system", "METRIC")
    if not MAPS_API_KEY:
        raise RuntimeError("GOOGLE_MAPS_API_KEY not set. Configure it to use weather tools.")
    
    params = {
        "location": f"{lat},{lng}",
        "days": max(1, min(int(days), 10)),
        "unitSystem": unit_system,
        "languageCode": "en",
    }
    r = _SESSION.get(
        WEATHER_DAYS_URL,
        params=params,
        headers={"X-Goog-Api-Key": MAPS_API_KEY},
        timeout=20,
    )
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f"Weather API error: {r.text}") from e
    return r.json()


# =====================================================================================
# Internal Nearby helper (shared by attractions/restaurants/hotels)
# =====================================================================================

def _nearby(
    lat: float,
    lng: float,
    radius_m: int,
    included_types: List[str],
    max_results: Optional[int],
    min_rating: Optional[float],
    term_bias: Optional[str] = None,
) -> List[Place]:
    """Internal wrapper for Places Nearby with rating filter and optional term bias."""
    body: Dict[str, Any] = {
        "includedTypes": included_types,
        "maxResultCount": max(1, min(int(max_results or 20), 20)),
        "locationRestriction": {
            "circle": {"center": {"latitude": lat, "longitude": lng}, "radius": int(radius_m)}
        },
        "rankPreference": "POPULARITY",
    }
    if term_bias:
        # Light relevance nudge (e.g., "vegetarian")
        body["textQuery"] = term_bias

    data = _post(PLACES_SEARCH_NEARBY, body)
    places = data.get("places", [])

    if min_rating is not None:
        try:
            threshold = float(min_rating)
            places = [p for p in places if p.get("rating", 0) >= threshold]
        except (TypeError, ValueError):
            pass

    return [_normalize_place(p) for p in places]


# =====================================================================================
# 6) save_trip  — declaration + function
# =====================================================================================

save_trip_declaration: Dict[str, Any] = {
    "name": "save_trip",
    "description": "Save the current trip itinerary for the user.",
    "parameters": {
        "type": "object",
        "properties": {
            "trip_name": {
                "type": "string",
                "description": "A name for the trip (e.g., 'Paris Adventure 2024')",
            },
            "trip_summary": {
                "type": "string", 
                "description": "A brief summary of the trip itinerary",
            },
        },
        "required": ["trip_name"],
    },
}


def save_trip(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Save the current trip data.
    
    Args:
        args: Dictionary containing:
            - trip_name: Name for the trip
            - trip_summary: Brief summary of the trip (optional)
        
    Returns:
        Dictionary with save status and trip_id
    """
    trip_name = args.get("trip_name", "")
    trip_summary = args.get("trip_summary", "")
    # This will be populated by the integration layer with actual trip data
    # For now, return a placeholder response
    return {
        "status": "saved",
        "message": f"Trip '{trip_name}' has been saved successfully!",
        "trip_name": trip_name,
        "trip_summary": trip_summary,
        "save_timestamp": "placeholder"  # Will be filled by integration
    }