import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

def save_trip(trip_data: Dict[str, Any], user_id: str = "default") -> str:
    """
    Save a trip to storage. (DISABLED - returns trip_id without saving)
    
    Args:
        trip_data: The trip data to save
        user_id: User identifier (default for demo)
        
    Returns:
        trip_id: Unique identifier for the saved trip
    """
    # Validate input data
    if not isinstance(trip_data, dict):
        raise ValueError("trip_data must be a dictionary")
    
    # Sanitize user_id to prevent path traversal
    user_id = str(user_id).replace('/', '_').replace('\\', '_').replace('..', '_')[:50]
    
    trip_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()
    
    # Validate required fields
    if not trip_data.get('trip_name'):
        trip_data['trip_name'] = f"Trip_{trip_id}"
    
    # Create trip record with size limit check
    trip_record = {
        "trip_id": trip_id,
        "user_id": user_id,
        "created_at": timestamp,
        "trip_data": trip_data
    }
        
    return trip_record
    
def list_trips(user_id: str = "default") -> List[Dict[str, Any]]:
    """List all trips for a user from session state."""
    import streamlit as st
    
    # Initialize session trips if not exists
    if "saved_trip_data" not in st.session_state:
        st.session_state.saved_trip_data = []
    
    trips = []
    for trip_record in st.session_state.saved_trip_data:
        try:
            # Extract trip data
            trip_data = trip_record.get("trip_data", {})
            
            # Extract form data from nested structure
            form_data = trip_data.get("form_data", {})
            
            # Create summary with proper data extraction
            summary = {
                "trip_id": trip_record.get("trip_id"),
                "created_at": trip_record.get("created_at"),
                "trip_name": trip_data.get("trip_name", "Untitled Trip"),
                "trip_summary": trip_data.get("trip_summary", ""),
                "origin": form_data.get("origin", "Unknown"),
                "destination": form_data.get("destination", "Unknown"),
                "start_date": form_data.get("start_date", "Unknown"),
                "end_date": form_data.get("end_date", "Unknown"),
                "season": form_data.get("season", "Unknown"),
                "travel_months": form_data.get("travel_months", "Unknown"),
                "travel_type": form_data.get("travel_type", "Unknown"),
                "budget": form_data.get("budget", "Unknown"),
                "group_size": form_data.get("group_size", "Unknown"),
                "accommodation": form_data.get("accommodation", "Unknown"),
                "special_requests": form_data.get("special_requests", "Unknown")
            }
            
            trips.append(summary)
            
        except Exception as e:
            print(f"ERROR processing trip: {e}")
            continue
    
    # Sort by creation date (newest first)
    trips.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return trips

def load_trip(trip_id: str, user_id: str = "default") -> Optional[Dict[str, Any]]:
    """Load a specific trip by ID from session state."""
    import streamlit as st
    
    # Initialize session trips if not exists
    if "saved_trip_data" not in st.session_state:
        st.session_state.saved_trip_data = []
        return None
    
    for trip_record in st.session_state.saved_trip_data:
        if trip_record.get("trip_id") == trip_id:
            return trip_record
    
    return None