"""Firebase Authentication service for Trip Sense using REST API."""
import streamlit as st
import requests
import json
import os
from pathlib import Path

# Firebase REST API endpoints
FIREBASE_REST_API = "https://identitytoolkit.googleapis.com/v1/accounts"

def get_firebase_api_key():
    """Get Firebase API key from config."""
    # Try to load from .streamlit/firebase_config.json
    config_path = Path(".streamlit/firebase_config.json")
    
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            return config.get("apiKey")
    
    # Or from environment variable
    firebase_config_str = os.getenv("FIREBASE_WEB_CONFIG")
    if firebase_config_str:
        config = json.loads(firebase_config_str)
        return config.get("apiKey")
    
    return None

def sign_up(email: str, password: str):
    """Create a new user account using Firebase REST API."""
    api_key = get_firebase_api_key()
    if not api_key:
        return {"success": False, "message": "Firebase not configured. Please add firebase_config.json"}
    
    try:
        url = f"{FIREBASE_REST_API}:signUp?key={api_key}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(url, json=payload)
        data = response.json()
        
        if response.status_code == 200:
            # Send verification email
            send_verification_email(data['idToken'])
            return {"success": True, "user": data, "message": "Account created! Please check your email for verification."}
        else:
            error_msg = data.get('error', {}).get('message', 'Unknown error')
            if "EMAIL_EXISTS" in error_msg:
                return {"success": False, "message": "Email already registered"}
            elif "WEAK_PASSWORD" in error_msg:
                return {"success": False, "message": "Password should be at least 6 characters"}
            else:
                return {"success": False, "message": f"Sign up failed: {error_msg}"}
    except Exception as e:
        return {"success": False, "message": f"Sign up failed: {str(e)}"}

def sign_in(email: str, password: str):
    """Sign in with email and password using Firebase REST API."""
    api_key = get_firebase_api_key()
    if not api_key:
        return {"success": False, "message": "Firebase not configured. Please add firebase_config.json"}
    
    try:
        url = f"{FIREBASE_REST_API}:signInWithPassword?key={api_key}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(url, json=payload)
        data = response.json()
        
        if response.status_code == 200:
            # Store in session
            st.session_state.user = data
            st.session_state.user_email = email
            st.session_state.user_id = data['localId']
            st.session_state.user_token = data['idToken']
            st.session_state.authenticated = True
            
            return {"success": True, "user": data}
        else:
            error_msg = data.get('error', {}).get('message', 'Unknown error')
            if "INVALID_LOGIN_CREDENTIALS" in error_msg or "INVALID_EMAIL" in error_msg or "INVALID_PASSWORD" in error_msg:
                return {"success": False, "message": "Invalid email or password"}
            elif "EMAIL_NOT_FOUND" in error_msg:
                return {"success": False, "message": "Email not registered"}
            else:
                return {"success": False, "message": f"Sign in failed: {error_msg}"}
    except Exception as e:
        return {"success": False, "message": f"Sign in failed: {str(e)}"}

def sign_out():
    """Sign out the current user."""
    # Clear user-specific data
    user_id = st.session_state.get('user_id')
    if user_id:
        load_key = f"firestore_trips_loaded_{user_id}"
        st.session_state.pop(load_key, None)
    
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.user_email = None
    st.session_state.user_id = None
    st.session_state.saved_trip_data = []  # Clear trips on logout

def is_authenticated():
    """Check if user is authenticated. Always returns True in guest mode."""
    return True

def get_user_id():
    """Get current user ID. Returns 'guest' in guest mode."""
    return 'guest'

def get_user_email():
    """Get current user email. Returns 'guest' in guest mode."""
    return 'guest'

def send_verification_email(id_token: str):
    """Send email verification."""
    api_key = get_firebase_api_key()
    if not api_key:
        return
    
    try:
        url = f"{FIREBASE_REST_API}:sendOobCode?key={api_key}"
        payload = {
            "requestType": "VERIFY_EMAIL",
            "idToken": id_token
        }
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Failed to send verification email: {e}")

def reset_password(email: str):
    """Send password reset email using Firebase REST API."""
    api_key = get_firebase_api_key()
    if not api_key:
        return {"success": False, "message": "Firebase not configured"}
    
    try:
        url = f"{FIREBASE_REST_API}:sendOobCode?key={api_key}"
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return {"success": True, "message": "Password reset email sent!"}
        else:
            data = response.json()
            error_msg = data.get('error', {}).get('message', 'Unknown error')
            return {"success": False, "message": f"Failed: {error_msg}"}
    except Exception as e:
        return {"success": False, "message": f"Failed to send reset email: {str(e)}"}

