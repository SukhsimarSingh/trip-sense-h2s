# import json
# import os
# from datetime import datetime
from typing import Dict, Any, List, Optional
# from pathlib import Path
import uuid

# # Storage directory (DISABLED - trips will not be saved to disk)
# TRIPS_DIR = Path("saved_trips")
# # TRIPS_DIR.mkdir(exist_ok=True)  # Disabled to prevent file creation

# class TripStorage:
#     """Handles saving and loading of trip data."""
    
#     @staticmethod
#     def save_trip(trip_data: Dict[str, Any], user_id: str = "default") -> str:
#         """
#         Save a trip to storage. (DISABLED - returns trip_id without saving)
        
#         Args:
#             trip_data: The trip data to save
#             user_id: User identifier (default for demo)
            
#         Returns:
#             trip_id: Unique identifier for the saved trip
#         """
#         # Validate input data
#         if not isinstance(trip_data, dict):
#             raise ValueError("trip_data must be a dictionary")
        
#         # Sanitize user_id to prevent path traversal
#         user_id = str(user_id).replace('/', '_').replace('\\', '_').replace('..', '_')[:50]
        
#         trip_id = str(uuid.uuid4())[:8]  # Short UUID
#         timestamp = datetime.now().isoformat()
        
#         # Validate required fields
#         if not trip_data.get('trip_name'):
#             trip_data['trip_name'] = f"Trip_{trip_id}"
        
#         # Create trip record with size limit check
#         trip_record = {
#             "trip_id": trip_id,
#             "user_id": user_id,
#             "created_at": timestamp,
#             "trip_data": trip_data
#         }
        
#         # Check file size (limit to 1MB per trip)
#         record_json = json.dumps(trip_record, ensure_ascii=False)
#         if len(record_json.encode('utf-8')) > 1024 * 1024:  # 1MB limit
#             raise ValueError("Trip data too large (max 1MB)")
        
#         # Save to file
#         filename = f"{user_id}_{trip_id}.json"
#         filepath = TRIPS_DIR / filename
        
#         # Atomic write using temporary file
#         temp_filepath = filepath.with_suffix('.tmp')
#         try:
#             with open(temp_filepath, 'w', encoding='utf-8') as f:
#                 json.dump(trip_record, f, indent=2, ensure_ascii=False)
#             temp_filepath.rename(filepath)
#         except Exception as e:
#             # Clean up temp file if it exists
#             if temp_filepath.exists():
#                 temp_filepath.unlink()
#             raise e
        
#         return trip_id
    
#     @staticmethod
#     def load_trip(trip_id: str, user_id: str = "default") -> Optional[Dict[str, Any]]:
#         """Load a specific trip by ID."""
#         filename = f"{user_id}_{trip_id}.json"
#         filepath = TRIPS_DIR / filename
        
#         if not filepath.exists():
#             return None
        
#         try:
#             with open(filepath, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         except (json.JSONDecodeError, IOError):
#             return None
    
#     @staticmethod
#     def list_trips(user_id: str = "default") -> List[Dict[str, Any]]:
#         """List all trips for a user."""
#         # Sanitize user_id
#         user_id = str(user_id).replace('/', '_').replace('\\', '_').replace('..', '_')[:50]
        
#         trips = []
#         pattern = f"{user_id}_*.json"
        
#         for filepath in TRIPS_DIR.glob(pattern):
#             try:
#                 # Skip files that are too large (corrupted)
#                 if filepath.stat().st_size > 2 * 1024 * 1024:  # 2MB limit
#                     continue
                    
#                 with open(filepath, 'r', encoding='utf-8') as f:
#                     trip_record = json.load(f)
#                     # Add summary info
#                     trip_data = trip_record.get("trip_data", {})
                    
#                     # Extract form data from nested structure
#                     form_data = trip_data.get("form_data", {})
                    
#                     summary = {
#                         "trip_id": trip_record.get("trip_id"),
#                         "created_at": trip_record.get("created_at"),
#                         "trip_name": trip_data.get("trip_name", "Untitled Trip"),
#                         "trip_summary": trip_data.get("trip_summary", ""),
#                         "origin": form_data.get("origin", "Unknown"),
#                         "destination": form_data.get("destination", "Unknown"),
#                         "start_date": form_data.get("start_date", "Unknown"),
#                         "end_date": form_data.get("end_date", "Unknown"),
#                         "season": form_data.get("season", "Unknown"),
#                         "travel_months": form_data.get("travel_months", "Unknown"),
#                         "travel_type": form_data.get("travel_type", "Unknown"),
#                         "budget": form_data.get("budget", "Unknown"),
#                         "group_size": form_data.get("group_size", "Unknown"),
#                         "accommodation": form_data.get("accommodation", "Unknown"),
#                         "special_requests": form_data.get("special_requests", "Unknown")
#                     }
                    
#                     trips.append(summary)
#             except (json.JSONDecodeError, IOError):
#                 continue
        
#         # Sort by creation date (newest first) and limit to 100 trips per user
#         trips.sort(key=lambda x: x.get("created_at", ""), reverse=True)
#         return trips[:100]  # Limit to prevent memory issues
    
#     @staticmethod
#     def delete_trip(trip_id: str, user_id: str = "default") -> bool:
#         """Delete a trip by ID."""
#         filename = f"{user_id}_{trip_id}.json"
#         filepath = TRIPS_DIR / filename
        
#         if filepath.exists():
#             try:
#                 filepath.unlink()
#                 return True
#             except OSError:
#                 return False
#         return False

# # Global storage instance
# trip_storage = TripStorage()

# Minimal working TripStorage class for compatibility (doesn't save to disk)
class TripStorage:
    """Handles saving and loading of trip data. (DISABLED - no file operations)"""
    
    @staticmethod
    def save_trip(trip_data: Dict[str, Any], user_id: str = "default") -> str:
        """Generate trip ID without saving to disk."""
        trip_id = str(uuid.uuid4())[:8]
        print(f"Trip saving disabled - would have saved trip '{trip_data.get('trip_name', 'Unnamed')}' with ID: {trip_id}")
        return trip_id
    
    @staticmethod
    def load_trip(trip_id: str, user_id: str = "default") -> Optional[Dict[str, Any]]:
        """Returns None since no trips are saved."""
        print(f"Trip loading disabled - cannot load trip ID: {trip_id}")
        return None
    
    @staticmethod
    def list_trips(user_id: str = "default") -> List[Dict[str, Any]]:
        """Returns empty list since no trips are saved."""
        print("Trip listing disabled - returning empty list")
        return []
    
    @staticmethod
    def delete_trip(trip_id: str, user_id: str = "default") -> bool:
        """Returns False since no trips exist to delete."""
        print(f"Trip deletion disabled - cannot delete trip ID: {trip_id}")
        return False

# Global storage instance
trip_storage = TripStorage()