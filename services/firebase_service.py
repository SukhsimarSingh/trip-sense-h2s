"""Firebase Firestore integration for Trip Sense."""
import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

def initialize_firebase():
    """Initialize Firebase Admin SDK."""
    if firebase_admin._apps:
        try:
            return firestore.client()
        except Exception as e:
            print(f"Error getting Firestore client: {e}")
            return None
    
    # Method 1: Cloud Run - credentials from environment variable (JSON string)
    firebase_creds = os.getenv("FIREBASE_CREDENTIALS")
    if firebase_creds:
        try:
            cred_dict = json.loads(firebase_creds)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print(f"Firebase initialized from environment variable")
            return firestore.client()
        except Exception as e:
            print(f"Error initializing Firebase from env var: {e}")
    
    # Method 2: Local - Check for firebase-key.json in project root
    local_key_path = "firebase-key.json"
    if os.path.exists(local_key_path):
        try:
            cred = credentials.Certificate(local_key_path)
            firebase_admin.initialize_app(cred)
            print(f"Firebase initialized from {local_key_path}")
            return firestore.client()
        except Exception as e:
            print(f"Error initializing Firebase from file: {e}")
    
    # Method 3: Try Application Default Credentials
    try:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
        print(f"Firebase initialized with Application Default Credentials")
        return firestore.client()
    except Exception as e:
        print(f"Firebase not configured: {e}")
        print("Tip: Place firebase-key.json in project root for local testing")
        return None

@st.cache_resource
def get_firestore_client():
    """Get cached Firestore client."""
    return initialize_firebase()

