from typing import Dict, Any
import uuid
from datetime import datetime


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
    
    trip_id = str(uuid.uuid4())[:8]  # Short UUID
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


trip_record = save_trip({
    "trip_name": "Test Trip",
    "trip_summary": "This is a test trip",
    "form_data": {
        "origin": "Test Origin",
        "destination": "Test Destination"
    }
})

print(trip_record.get('trip_id'))