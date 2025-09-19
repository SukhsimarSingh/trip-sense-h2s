import streamlit as st
from datetime import datetime
import re

from services.gemini import TripSenseAI
from services.prompt_loader import load_system_prompt
from services.logging import logger, initialize_metrics
from services.trip_storage import trip_storage

SYSTEM_INSTRUCTION = load_system_prompt()

# Initialize metrics tracking
initialize_metrics()

def clean_and_render_markdown(content: str) -> None:
    """Clean and render markdown content with proper formatting."""
    if not content:
        st.markdown("*No content to display*")
        return
    
    # Clean and normalize content
    content = str(content).strip()
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    # Fix encoding issues
    content = content.replace('â€™', "'").replace('â€œ', '"').replace('â€', '"')
    content = content.replace('â€"', '–').replace('â€"', '—')
    
    # Fix markdown formatting
    content = re.sub(r'(\n|^)(#{1,6})\s*', r'\1\2 ', content)  # Header spacing
    content = re.sub(r'\*\*([^*]+)\*\*', r'**\1**', content)   # Bold formatting
    
    # Render with fallback
    try:
        st.markdown(content, unsafe_allow_html=True)
    except Exception as e:
        logger.warning(f"Markdown rendering failed: {e}")
        st.code(content, language="markdown")

# Initialize chatbot-specific session state
def initialize_chatbot_session():
    """Initialize chatbot session state variables"""
    if "chatbot_initialized" not in st.session_state:
        st.session_state.chatbot_initialized = True
        logger.info("Chatbot session initialized")
        
    if "trip_data" not in st.session_state:
        st.session_state.trip_data = {}
        logger.debug("Trip data initialized")

    if "initial_prompt" not in st.session_state:
        st.session_state.initial_prompt = None
        logger.debug("Initial prompt state initialized")

    # Initialize messages only if not already initialized for this session
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I can help plan trips. Tell me destination, dates, budget, interests."},
        ]
        logger.info("Chat messages initialized with welcome message")
    
    # Flag to track if initial prompt has been processed
    if "initial_prompt_processed" not in st.session_state:
        st.session_state.initial_prompt_processed = False
        logger.debug("Initial prompt processing flag initialized")
    
    # Track the main trip itinerary separately from chat responses
    if "main_trip_itinerary" not in st.session_state:
        st.session_state.main_trip_itinerary = None
        logger.debug("Main trip itinerary tracking initialized")

# Initialize the chatbot session
initialize_chatbot_session()

# Function to clean up chatbot session state when navigating away
def cleanup_chatbot_session():
    """Clean up chatbot-specific session state"""
    keys_to_remove = [
        "messages", 
        "initial_prompt_processed", 
        "chatbot_initialized"
    ]
    removed_keys = []
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
            removed_keys.append(key)
    
    # Set initial_prompt_processed to True to prevent regeneration
    # when returning to chatbot with existing trip data
    if st.session_state.get('trip_data') and st.session_state.get('initial_prompt'):
        st.session_state.initial_prompt_processed = True
        logger.debug("Set initial_prompt_processed to True to prevent regeneration")
    
    if removed_keys:
        logger.info(f"Cleaned up chatbot session state: {removed_keys}")
    else:
        logger.debug("No chatbot session state to clean up")

# Chat interface UI
def render_chat():
    for m in st.session_state.messages:
        # Only display user and assistant messages (system messages are handled internally)
        if m["role"] in ["user", "assistant"]:
            with st.chat_message(m["role"]):
                clean_and_render_markdown(m["content"])

# Uncomment below line for debugging session state
# st.write(st.session_state)

# Safety check: If no trip data, redirect to form
if not st.session_state.get('trip_data') or not st.session_state.get('initial_prompt'):
    st.warning("No trip data found. Please create a new trip plan.")
    st.info("Use the **Plan Trip** button in the sidebar to start planning.")
    
    # Clear any partial session state
    cleanup_chatbot_session()
    
    if st.button("📝 Create New Trip Plan", type="primary"):
        st.switch_page("pages/form.py")
    
    st.stop()  # Stop execution here

trip_data = st.session_state.trip_data
initial_prompt = st.session_state.initial_prompt

if st.session_state.trip_data:
    start_date_str = datetime.fromisoformat(trip_data['start_date']).strftime('%b %d')
    end_date_str = datetime.fromisoformat(trip_data['end_date']).strftime('%b %d, %Y')
    trip_description = f"Planning your trip to {trip_data.get('destination', 'your destination')} from {start_date_str} to {end_date_str}"
else:
    trip_description = f"Please fill the form to get the itinerary!"

st.markdown(f"""
<div style="text-align: center; padding: 2rem 0;">
    <h1 style="color: #666;">Your AI Trip Assistant</h1>
    <br>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{trip_description}</p>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    # Process initial prompt only once
    if (initial_prompt and trip_data and not st.session_state.initial_prompt_processed):
        
        logger.info(f"Processing initial prompt for trip to {trip_data.get('destination', 'Unknown')}")
        logger.debug(f"Initial prompt length: {len(initial_prompt)} characters")
        
        # Add Initial prompt in the messages in the session
        st.session_state.messages.append({"role": "user", "content": initial_prompt})
        
        # Mark as processed to prevent duplicates
        st.session_state.initial_prompt_processed = True

        with st.spinner("Creating your personalized itinerary..."):
            try:
                model_response = TripSenseAI().generate_initial_plan(trip_data)
                
                # Validate response
                if model_response and len(model_response.strip()) > 10:  # Ensure meaningful response
                    st.session_state.messages.append({"role": "assistant", "content": model_response})
                    # Store this as the main trip itinerary (not follow-up responses)
                    st.session_state.main_trip_itinerary = model_response
                    logger.info(f"Initial plan response added to messages ({len(model_response)} characters)")
                    logger.info("Stored as main trip itinerary for saving")
                    # Force rerun to display the initial response
                    st.rerun()
                else:
                    logger.warning(f"Invalid or empty response from initial plan generation: '{model_response}'")
                    error_msg = "I'm having trouble generating your trip plan right now. Please try refreshing the page or contact support."
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    st.error("Failed to generate trip plan. Please try again.")
                    
            except Exception as e:
                logger.error(f"Exception in initial plan generation: {e}")
                error_msg = "I encountered an error while generating your trip plan. Please try again."
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.error("An error occurred. Please try again.")

    # Chat interface
    render_chat()
    
    # Add chat input for user interaction
    if prompt := st.chat_input("Ask me anything about your trip..."):
        logger.info(f"User sent message: '{prompt[:100]}{'...' if len(prompt) > 100 else ''}'")
        logger.debug(f"Current message history length: {len(st.session_state.messages)}")
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        logger.debug("User message added to chat history")
        
        # Generate AI response
        with st.spinner("Thinking..."):
            try:
                response = TripSenseAI().chat_response(st.session_state.messages, prompt)
                
                # Validate response
                if response and len(response.strip()) > 5:  # Ensure meaningful response
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    logger.info(f"AI response generated and added to messages ({len(response)} characters)")
                else:
                    logger.warning(f"Invalid or empty chat response: '{response}'")
                    error_msg = "I'm having trouble responding right now. Could you please rephrase your question?"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
            except Exception as e:
                logger.error(f"Exception in chat response generation: {e}")
                error_msg = "I encountered an error processing your message. Please try again."
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        # Rerun to display the new messages
        logger.debug("Triggering UI rerun to display new messages")
        st.rerun()


# Navigation buttons
with st.container(horizontal_alignment="center", horizontal=True):
    if st.button("Back to Form", key="back_to_form"):
        cleanup_chatbot_session()
        st.switch_page("pages/form.py")

    if st.button("Home", key="back_to_home"):
        cleanup_chatbot_session()
        st.switch_page("app.py")

    if st.button("Save Trip", key="save_trip"):
        try:
            # Validate that we have trip data
            if not st.session_state.get('trip_data'):
                st.error("No trip data to save. Please create a trip plan first.")
            else:
                # Get the main trip itinerary (not the latest chat response)
                main_itinerary = st.session_state.get('main_trip_itinerary')
                
                if main_itinerary:
                    # Use the stored main itinerary
                    trip_itinerary = main_itinerary
                    logger.info("Using stored main trip itinerary for saving")
                else:
                    # Fallback: try to find the first substantial AI response (likely the trip plan)
                    messages = st.session_state.get('messages', [])
                    ai_responses = [msg['content'] for msg in messages if msg['role'] == 'assistant']
                    
                    # Filter out short responses (likely not the main itinerary)
                    substantial_responses = [resp for resp in ai_responses if len(resp.strip()) > 200]
                    trip_itinerary = substantial_responses[0] if substantial_responses else (ai_responses[0] if ai_responses else "No detailed itinerary available.")
                    logger.warning("No stored main itinerary found, using fallback method")
                
                # Create a default trip name if not provided
                destination = st.session_state.trip_data.get('destination', 'Unknown Destination')
                default_trip_name = f"Trip to {destination}"
                
                # Structure the trip data properly
                structured_trip_data = {
                    "trip_name": default_trip_name,
                    "trip_summary": f"Trip to {destination} planned with AI assistant",
                    "form_data": st.session_state.trip_data.copy(),
                    "itinerary": {
                        "ai_response": trip_itinerary,
                        "demo_mode": False,
                        "generated_at": datetime.now().isoformat()
                    }
                }
                
                # Save the trip
                trip_id = trip_storage.save_trip(structured_trip_data)
                st.success(f"Trip saved successfully! Trip ID: {trip_id}")
                logger.info(f"Manual trip save successful with ID: {trip_id}")
                
                # Clear session state after successful save
                cleanup_chatbot_session()
                # Also clear trip-related data
                keys_to_clear = ["trip_data", "initial_prompt", "form_data", "main_trip_itinerary"]
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                        logger.info(f"Cleared session state key: {key}")
                
                # Navigate to saved trips page
                st.switch_page("pages/trips.py")
                
        except Exception as e:
            st.error(f"Failed to save trip: {str(e)}")
            logger.error(f"Manual trip save failed: {e}")
            st.rerun()

    if st.button("Saved Trips", key="saved_trips"):
        st.switch_page("pages/trips.py")