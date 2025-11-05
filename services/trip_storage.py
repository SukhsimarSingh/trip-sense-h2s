import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid
import streamlit as st
from services.firebase_service import get_firestore_client

def save_trip(trip_data: Dict[str, Any], user_id: str = "default") -> str:
    """
    Save a trip to Firebase Firestore (or session state as fallback).
    
    Args:
        trip_data: The trip data to save
        user_id: User identifier (default for demo)
        
    Returns:
        trip_record: Complete trip record with auto-generated ID
    """
    # Validate input data
    if not isinstance(trip_data, dict):
        raise ValueError("trip_data must be a dictionary")
    
    # Sanitize user_id to prevent path traversal
    user_id = str(user_id).replace('/', '_').replace('\\', '_').replace('..', '_')[:50]
    
    timestamp = datetime.now().isoformat()
    
    # Try to save to Firebase first (let Firestore auto-generate ID)
    db = get_firestore_client()
    if db:
        try:
            # Create a new document reference with auto-generated ID
            doc_ref = db.collection('trips').document()
            trip_id = doc_ref.id  # Get the auto-generated ID
            
            # Validate required fields
            if not trip_data.get('trip_name'):
                trip_data['trip_name'] = f"Trip_{trip_id[:8]}"
            
            # Create trip record with Firestore-generated ID
            trip_record = {
                "trip_id": trip_id,
                "user_id": user_id,
                "created_at": timestamp,
                "trip_data": trip_data
            }
            
            # Save to Firestore
            doc_ref.set(trip_record)
            print(f"Trip {trip_id} saved to Firebase")
            
            # Also save to session state for immediate availability
            _save_to_session(trip_record)
            
            return trip_record
            
        except Exception as e:
            print(f"Error saving to Firebase: {e}")
            # Fall through to session state with UUID fallback
    
    # Fallback: No Firebase or error - use UUID and session state
    trip_id = str(uuid.uuid4())[:8]
    
    if not trip_data.get('trip_name'):
        trip_data['trip_name'] = f"Trip_{trip_id}"
    
    trip_record = {
        "trip_id": trip_id,
        "user_id": user_id,
        "created_at": timestamp,
        "trip_data": trip_data
    }
    
    _save_to_session(trip_record)
    return trip_record

def _save_to_session(trip_record: Dict[str, Any]):
    """Save trip to session state."""
    if "saved_trip_data" not in st.session_state:
        st.session_state.saved_trip_data = []
    st.session_state.saved_trip_data.append(trip_record)

def _load_trips_from_firestore_once(user_id: str):
    """Load trips from Firestore ONCE per session per user and cache in session state."""
    # Create a unique key for this user's load status
    load_key = f"firestore_trips_loaded_{user_id}"
    
    # Check if already loaded for this user this session
    if st.session_state.get(load_key):
        print(f"Trips already loaded for {user_id}, using cache (0 reads)")
        return
    
    # Initialize session state for trips if not exists
    if "saved_trip_data" not in st.session_state:
        st.session_state.saved_trip_data = []
    
    # Try to load from Firestore
    db = get_firestore_client()
    if db:
        try:
            print(f"Loading trips from Firestore for user: {user_id}")
            from google.cloud.firestore_v1.base_query import FieldFilter
            
            # Use limit to reduce reads if you have many trips
            # For now, loading all trips
            trips_ref = db.collection('trips').where(filter=FieldFilter('user_id', '==', user_id))
            docs = trips_ref.stream()
            
            firestore_trips = [doc.to_dict() for doc in docs]
            
            if firestore_trips:
                # Clear existing trips for this user before loading new ones
                st.session_state.saved_trip_data = [
                    t for t in st.session_state.saved_trip_data 
                    if t.get('user_id') != user_id
                ]
                
                # Add all trips from Firestore
                st.session_state.saved_trip_data.extend(firestore_trips)
                
                print(f"Loaded {len(firestore_trips)} trips from Firestore ({len(firestore_trips)} reads)")
            else:
                print("No trips found in Firestore (0 reads)")
            
            # Mark as loaded for this user
            st.session_state[load_key] = True
            
        except Exception as e:
            print(f"Error loading from Firestore: {e}")
            # Don't mark as loaded so it can retry
    else:
        print("Firebase not configured, using session state only")
        # Mark as loaded to prevent retries
        st.session_state[load_key] = True
    
def list_trips(user_id: str = "default") -> List[Dict[str, Any]]:
    """List all trips for a user from session state (loaded from Firestore once per session)."""
    user_id = str(user_id).replace('/', '_').replace('\\', '_').replace('..', '_')[:50]
    
    # Load from Firestore ONCE per session (caches in session state)
    _load_trips_from_firestore_once(user_id)
    
    # Always read from session state (which now contains Firestore data)
    trip_records = st.session_state.get("saved_trip_data", [])
    
    trips = []
    seen_trip_ids = set()  # Track unique trip IDs to prevent duplicates
    
    for trip_record in trip_records:
        try:
            # Extract trip data
            trip_data = trip_record.get("trip_data", {})
            trip_id = trip_record.get("trip_id")
            
            # Skip if we've already seen this trip ID (deduplication)
            if trip_id in seen_trip_ids:
                continue
            seen_trip_ids.add(trip_id)
            
            # Extract form data from nested structure
            form_data = trip_data.get("form_data", {})
            
            # Create summary with proper data extraction
            summary = {
                "trip_id": trip_id,
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
                "special_requests": form_data.get("special_requests", "Unknown"),
                "is_booked": trip_record.get("is_booked", False),
                "booked_at": trip_record.get("booked_at", None)
            }
            
            trips.append(summary)
            
        except Exception as e:
            print(f"ERROR processing trip: {e}")
            continue
    
    # Sort by creation date (newest first), handle None values
    trips.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return trips

def load_trip(trip_id: str, user_id: str = "default") -> Optional[Dict[str, Any]]:
    """Load a specific trip by ID from session state (already cached from Firestore)."""
    # Ensure trips are loaded from Firestore (only happens once)
    user_id = str(user_id).replace('/', '_').replace('\\', '_').replace('..', '_')[:50]
    _load_trips_from_firestore_once(user_id)
    
    # Find trip in session state
    for trip_record in st.session_state.get("saved_trip_data", []):
        if trip_record.get("trip_id") == trip_id:
            return trip_record
    
    return None

def update_trip(trip_id: str, updates: Dict[str, Any], user_id: str = "default") -> bool:
    """
    Update a trip in both Firestore and session state.
    
    Args:
        trip_id: The trip ID to update
        updates: Dictionary of fields to update (can be nested using dot notation for trip_data fields)
        user_id: User identifier
        
    Returns:
        bool: True if successful, False otherwise
    """
    user_id = str(user_id).replace('/', '_').replace('\\', '_').replace('..', '_')[:50]
    
    # Update in Firestore first
    db = get_firestore_client()
    if db:
        try:
            doc_ref = db.collection('trips').document(trip_id)
            doc_ref.update(updates)
            print(f"Trip {trip_id} updated in Firestore")
        except Exception as e:
            print(f"Error updating trip in Firestore: {e}")
            return False
    
    # Update in session state
    for trip_record in st.session_state.get("saved_trip_data", []):
        if trip_record.get("trip_id") == trip_id:
            # Apply updates to the trip record
            for key, value in updates.items():
                trip_record[key] = value
            print(f"Trip {trip_id} updated in session state")
            return True
    
    print(f"Trip {trip_id} not found in session state")
    return False

def delete_trip(trip_id: str, user_id: str = "default") -> bool:
    """
    Delete a trip from both Firestore and session state.
    
    Args:
        trip_id: The trip ID to delete
        user_id: User identifier
        
    Returns:
        bool: True if successful, False otherwise
    """
    user_id = str(user_id).replace('/', '_').replace('\\', '_').replace('..', '_')[:50]
    
    # Delete from Firestore first
    db = get_firestore_client()
    if db:
        try:
            doc_ref = db.collection('trips').document(trip_id)
            doc_ref.delete()
            print(f"Trip {trip_id} deleted from Firestore")
        except Exception as e:
            print(f"Error deleting trip from Firestore: {e}")
            # Continue to delete from session state even if Firestore deletion fails
    
    # Delete from session state
    if "saved_trip_data" in st.session_state:
        initial_count = len(st.session_state.saved_trip_data)
        st.session_state.saved_trip_data = [
            t for t in st.session_state.saved_trip_data 
            if t.get('trip_id') != trip_id
        ]
        deleted = len(st.session_state.saved_trip_data) < initial_count
        if deleted:
            print(f"Trip {trip_id} deleted from session state")
            return True
        else:
            print(f"Trip {trip_id} not found in session state")
            return False
    
    return False