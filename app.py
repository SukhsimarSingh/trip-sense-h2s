import os
import json
import logging
from datetime import datetime
from typing import Dict, List

import dotenv
dotenv.load_dotenv()
import streamlit as st

from src.ai.integration import trip_planner_ai

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trip_planner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL")

# =========================
# Streamlit App Layout
# =========================
st.set_page_config(page_title="AI Trip Planner", page_icon="🧭", layout="wide")

# Initialize session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "trip_data" not in st.session_state:
    st.session_state.trip_data = {}

# Initialize metrics tracking
if "metrics" not in st.session_state:
    st.session_state.metrics = {
        "total_requests": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_cost_estimate": 0.0,
        "requests_log": [],
        "session_start": datetime.now().isoformat()
    }

# Universal Sidebar - Available on all pages
def render_sidebar():
    """Render the universal sidebar with navigation and status."""
    with st.sidebar:
        # App Title and Navigation
        st.markdown("# 🧭 AI Trip Planner")
        st.markdown("---")
        
        # Navigation Menu
        st.subheader("📍 Navigation")
        
        # Current page indicator and navigation buttons
        pages = {
            "landing": {"label": "🏠 Home", "icon": "🏠"},
            "form": {"label": "📝 Plan Trip", "icon": "📝"},
            "chatbot": {"label": "💬 Chat & Refine", "icon": "💬"},
            "trips": {"label": "📚 Saved Trips", "icon": "📚"}
        }
        
        current_page = st.session_state.page
        
        for page_key, page_info in pages.items():
            if page_key == current_page:
                # Highlight current page
                st.markdown(f"**➤ {page_info['label']}**")
            else:
                # Navigation button for other pages
                if st.button(page_info["label"], key=f"nav_{page_key}", use_container_width=True):
                    # Special handling for certain page transitions
                    if page_key == "form":
                        # Reset trip data when starting new trip planning
                        st.session_state.trip_data = {}
                        if "messages" in st.session_state:
                            del st.session_state.messages
                    elif page_key == "chatbot" and not st.session_state.trip_data:
                        # If trying to go to chatbot without trip data, redirect to form
                        st.session_state.page = "form"
                        st.rerun()
                        return
                    
                    st.session_state.page = page_key
                    st.rerun()
        
        st.markdown("---")
        
        # System Status
        st.subheader("⚡ System Status")
        gemini_status = trip_planner_ai.is_available()
        maps_status = bool(GOOGLE_MAPS_API_KEY)
        
        st.write(f"🤖 **Gemini AI:** {'✅ Ready' if gemini_status else '❌ Not configured'}")
        st.write(f"🗺️ **Maps API:** {'✅ Ready' if maps_status else '❌ Not configured'}")
        
        if not gemini_status or not maps_status:
            st.info("💡 Demo mode available without API keys!")
        
        # Current Trip Details (if available)
        if st.session_state.trip_data:
            st.markdown("---")
            st.subheader("🎯 Current Trip")
            trip_data = st.session_state.trip_data
            
            st.write(f"📍 **Destination:** {trip_data.get('destination', 'N/A')}")
            st.write(f"📅 **Duration:** {trip_data.get('duration', 'N/A')} days")
            st.write(f"🎨 **Type:** {trip_data.get('travel_type', 'N/A')}")
            st.write(f"💰 **Budget:** {trip_data.get('budget', 'N/A')}")
            
            if st.button("🔄 Start New Trip", use_container_width=True):
                st.session_state.page = "landing"
                st.session_state.trip_data = {}
                if "messages" in st.session_state:
                    del st.session_state.messages
                st.rerun()
        
        # Usage Metrics (show on chatbot page or if there are metrics)
        if current_page == "chatbot" or st.session_state.metrics["total_requests"] > 0:
            st.markdown("---")
            st.subheader("📊 Usage Stats")
            metrics = st.session_state.metrics
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Requests", metrics["total_requests"])
                st.metric("Input Tokens", f"{metrics['total_input_tokens']:,}")
            with col2:
                st.metric("Output Tokens", f"{metrics['total_output_tokens']:,}")
                st.metric("Est. Cost", f"${metrics['total_cost_estimate']:.4f}")
            
            # Session info
            session_duration = datetime.now() - datetime.fromisoformat(metrics["session_start"])
            st.caption(f"Session: {session_duration.total_seconds()/60:.1f} minutes")
            
            # Detailed logs expander
            with st.expander("📋 Request Log"):
                if metrics["requests_log"]:
                    for i, log in enumerate(reversed(metrics["requests_log"][-10:])):  # Show last 10
                        status_icon = "✅" if log["success"] else "❌"
                        st.write(f"{status_icon} **{log['type'].title()}** - {datetime.fromisoformat(log['timestamp']).strftime('%H:%M:%S')}")
                        st.write(f"   Tokens: {log['input_tokens']} → {log['output_tokens']} | Cost: ${log['cost_estimate']:.6f}")
                        if log.get("error"):
                            st.error(f"   Error: {log['error']}")
                else:
                    st.write("No requests yet")
            
            # Export logs button
            if st.button("📥 Export Logs", use_container_width=True):
                log_data = {
                    "session_metrics": metrics,
                    "export_timestamp": datetime.now().isoformat()
                }
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(log_data, indent=2),
                    file_name=f"trip_planner_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        # Footer
        st.markdown("---")
        st.markdown("*Built with ❤️ for travelers*")

# Render sidebar on all pages
render_sidebar()

# =========================
# System Prompt & Tool Protocol
# =========================
# System instruction is now loaded from prompts/system.yaml via the integration module
try:
    from src.ai.prompt_loader import load_system_prompt
    SYSTEM_INSTRUCTION = load_system_prompt()
except Exception:
    SYSTEM_INSTRUCTION = """You are an expert AI trip planner. Plan realistic itineraries with travel times, costs, and flexible options."""

# =========================
# Session State
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "assistant", "content": "Hi! I can help plan trips. Tell me destination, dates, budget, interests."},
    ]

def render_chat():
    for m in st.session_state.messages:
        if m["role"] == "system":
            continue
        with st.chat_message("assistant" if m["role"] == "assistant" else "user"):
            if isinstance(m["content"], dict):
                # Convert dict content to user-friendly text instead of showing JSON
                if "tool" in m["content"]:
                    tool_name = m["content"].get("tool", "unknown")
                    result = m["content"].get("result", {})
                    if tool_name == "save_trip":
                        if result.get("status") == "saved":
                            st.success(f"✅ {result.get('message', 'Trip saved successfully!')}")
                        else:
                            st.error(f"❌ {result.get('message', 'Failed to save trip.')}")
                    else:
                        st.info(f"🔧 Used {tool_name.replace('_', ' ').title()}")
                else:
                    # For other dict content, try to extract meaningful text
                    content_str = str(m["content"])
                    if len(content_str) > 200:
                        st.info("ℹ️ Processed your request with available tools.")
                    else:
                        st.markdown(content_str)
            else:
                st.markdown(m["content"])


# =========================
# Metrics & Logging Functions
# =========================

def estimate_tokens(text: str) -> int:
    """Rough estimation of tokens (1 token ≈ 4 characters for English)."""
    return len(text) // 4

def calculate_cost_estimate(input_tokens: int, output_tokens: int) -> float:
    """Calculate estimated cost based on token usage."""
    # Input: $0.15 per 1M tokens, Output: $0.60 per 1M tokens
    input_cost = (input_tokens / 1_000_000) * 0.15
    output_cost = (output_tokens / 1_000_000) * 0.60
    return input_cost + output_cost

def log_request(request_type: str, input_tokens: int, output_tokens: int, success: bool, error_msg: str = None):
    """Log API request with metrics."""
    timestamp = datetime.now().isoformat()
    cost = calculate_cost_estimate(input_tokens, output_tokens)
    
    # Update session metrics
    st.session_state.metrics["total_requests"] += 1
    st.session_state.metrics["total_input_tokens"] += input_tokens
    st.session_state.metrics["total_output_tokens"] += output_tokens
    st.session_state.metrics["total_cost_estimate"] += cost
    
    # Log entry
    log_entry = {
        "timestamp": timestamp,
        "type": request_type,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_estimate": cost,
        "success": success,
        "error": error_msg
    }
    
    st.session_state.metrics["requests_log"].append(log_entry)
    
    # File logging
    logger.info(f"API Request - Type: {request_type}, Input Tokens: {input_tokens}, "
                f"Output Tokens: {output_tokens}, Cost: ${cost:.6f}, Success: {success}")
    
    if error_msg:
        logger.error(f"API Error: {error_msg}")


# =========================
# LLM Call
# =========================

def call_gemini(chat_history: List[Dict[str, str]], user_text: str) -> str:
    """Send a prompt with lightweight history to Gemini. Returns response text."""
    # Calculate input tokens for logging
    input_tokens = estimate_tokens(user_text)
    
    try:
        # Use the integrated AI trip planner
        response_text = trip_planner_ai.chat_response(chat_history, user_text)
        output_tokens = estimate_tokens(response_text)
        
        # Log successful request
        log_request("gemini", input_tokens, output_tokens, True)
        
        return response_text
        
    except Exception as e:
        error_msg = str(e)
        # Log failed request
        log_request("gemini", input_tokens, 0, False, error_msg)
        return f"[Gemini error] {error_msg}"
    

# =========================
# Page Navigation & UI
# =========================

landing_page_html = """
    <div style="text-align: center; padding: 3rem 0;">
        <h1 style="font-size: 3.5rem; margin-bottom: 1rem; background: linear-gradient(45deg, #FF6B6B, #4ECDC4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🧭 AI Trip Planner
        </h1>
        <br>
        <h3 style="color: #666; margin-bottom: 2rem; font-weight: 300;">
            Plan your perfect adventure with AI-powered recommendations
        </h3>
        <br>
        <p style="font-size: 1.2rem; color: #888; max-width: 600px; margin: 0 auto 3rem auto; line-height: 1.6;">
            From budget-friendly getaways to luxury escapes, our AI assistant helps you discover amazing destinations, 
            create detailed itineraries, and find the best places to visit based on your preferences.
        </p>
    </div>
    """

personalised_widget = """
                <div style="color: #666; text-align: center; padding: 2rem 1rem; border-radius: 20px; margin: 2rem 1rem;">
                    <h4>🎯 Personalized</h4>
                    <p>Tailored recommendations based on your travel style, budget, and interests</p>
                </div>
                """

planning_widget = """
                <div style="color: #666; text-align: center; padding: 2rem 1rem; border-radius: 20px; margin: 2rem 1rem;">
                    <h4>🗺️ Smart Planning</h4>
                    <p>AI-powered itineraries with real-time maps, directions, and local insights</p>
                </div>
                """

interactive_widget = """
                <div style="color: #666; text-align: center; padding: 2rem 1rem; border-radius: 20px; margin: 2rem 1rem;">
                    <h4>💬 Interactive</h4>
                    <p>Chat with our AI assistant to refine your plans and get instant answers</p>
                </div>
                """

def show_landing_page():
    """Display the landing page with hero section and call-to-action.""" 

    with st.container(horizontal_alignment="center"):
        st.markdown(body=landing_page_html, unsafe_allow_html=True)

        if st.button("🚀 Start Planning Your Trip", key="start_planning", help="Click to begin your travel planning journey"):
            st.session_state.page = "form"
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")

        with st.container(horizontal=True, horizontal_alignment="center"):
            st.markdown(body=personalised_widget, unsafe_allow_html=True, width="content")

            st.markdown(body=planning_widget, unsafe_allow_html=True, width="content")

            st.markdown(body=interactive_widget, unsafe_allow_html=True, width="content")


form_page_html = """
        <div style="text-align: center; padding: 3rem 0;">
            <h1 style="color: #666;">✈️ Tell Us About Your Dream Trip</h1>
            <br>
            <p style="color: #666; font-size: 1.1rem;">Fill in the details below to get personalized recommendations</p>
        </div>
        """

def show_form_page():
    # """Display the travel information form."""

    with st.container(horizontal_alignment="center"):
        st.markdown(body=form_page_html, unsafe_allow_html=True)

        with st.form("trip_form", clear_on_submit=False, ):
            st.markdown("""<h5 style="color: #666;"> Basic Info</h5>""", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                destination = st.text_input(
                    "📍 Where do you want to go?",
                    placeholder="e.g., Paris, Tokyo, Himachal Pradesh",
                    help="Enter your desired destination city, country, or region"
                )
                
                duration = st.number_input(
                        "📅 How long is your trip?",
                        value=2,
                        step=1,
                        help="Select the number of days for your trip"
                    )
            
            with col2:
                travel_type = st.selectbox(
                    "🎯 What type of experience are you looking for?",
                    options=[
                        "Adventure & Outdoor Activities",
                        "Cultural & Historical Sites", 
                        "Relaxation & Wellness",
                        "Food & Culinary Experiences",
                        "Nightlife & Entertainment",
                        "Family-Friendly Activities",
                        "Photography & Sightseeing",
                        "Shopping & Markets",
                        "Nature & Wildlife",
                        "Mixed Experience"
                    ],
                    index=9,  # Default to Mixed Experience
                    help="Choose the type of activities you're most interested in"
                )
                
                budget = st.selectbox(
                    "💰 What's your budget range?",
                    options=["Low Budget (Budget-friendly options)", "Medium Budget (Comfortable spending)", "High Budget (Luxury experience)"],
                    index=1,  # Default to Medium
                    help="Select your preferred budget range for the trip"
                )
            
            # Additional preferences
            st.markdown("""<h5 style="color: #666;">Additional Preferences (Optional)</h5>""", unsafe_allow_html=True)
            
            with st.container(horizontal=True, horizontal_alignment="center"):
                group_size = st.number_input(
                    "👥 Number of travelers",
                    min_value=1,
                    max_value=100,
                    value=2,
                    help="How many people will be traveling?"
                )
            
                accommodation = st.selectbox(
                    "🏨 Preferred accommodation",
                    options=["Any", "Hotels", "Hostels", "Vacation Rentals", "Resorts", "Boutique Properties"],
                    help="What type of accommodation do you prefer?"
                )
            
            special_requests = st.text_area(
                "📝 Any special requests or interests?",
                placeholder="e.g., vegetarian food options, accessibility needs, specific attractions to visit...",
                help="Tell us about any specific requirements or interests"
            )
            
            # Form submission
            st.markdown("<br>", unsafe_allow_html=True)

            with st.container(horizontal=True, horizontal_alignment="center"):
                if st.form_submit_button("⬅️ Back to Home", type="secondary", width="content"):
                    st.session_state.page = "landing"
                    st.rerun()

                submitted = st.form_submit_button("🎯 Generate My Trip Plan", type="primary", width="content")

            if submitted:
                if not destination.strip():
                    st.error("Please enter a destination!")
                    return
                
                # Store form data
                st.session_state.trip_data = {
                    "destination": destination,
                    "duration": duration,
                    "travel_type": travel_type,
                    "budget": budget,
                    "group_size": group_size,
                    "accommodation": accommodation,
                    "special_requests": special_requests
                }
                
                # Initialize chat with trip data
                initial_prompt = f"""I want to plan a {duration}-day trip to {destination} for {group_size} people. 
                My travel style is: {travel_type}
                Budget: {budget}
                Accommodation preference: {accommodation}
                {f'Special requests: {special_requests}' if special_requests else ''}
                Please create a detailed itinerary with recommendations for places to visit, activities, restaurants, and travel tips."""

                st.session_state.messages = [
                    {"role": "system", "content": SYSTEM_INSTRUCTION},
                    {"role": "assistant", "content": f"Great! I'll help you plan an amazing {duration}-day trip to {destination}. Let me create a personalized itinerary based on your preferences."},
                ]
                
                # Store the initial prompt to be processed when the chatbot page loads
                st.session_state.initial_prompt = initial_prompt
                
                st.session_state.page = "chatbot"
                st.rerun()

def show_chatbot_page():
    """Display the chatbot interface with trip planning."""
    # Handle initial prompt if it exists
    if hasattr(st.session_state, 'initial_prompt') and st.session_state.initial_prompt:
        initial_prompt = st.session_state.initial_prompt
        st.session_state.initial_prompt = None  # Clear it so it doesn't run again
        
        # Add user message and get AI response
        st.session_state.messages.append({"role": "user", "content": initial_prompt})
        
        # Get AI response using the integrated trip planner
        with st.spinner("Creating your personalized itinerary..."):
            model_text = trip_planner_ai.generate_initial_plan(st.session_state.trip_data)
            st.session_state.messages.append({"role": "assistant", "content": model_text})
    
    # Header with trip info
    st.markdown(f"""
        <div style="text-align: center; padding: 3rem 0;">
            <h1 style="color: #666;">🤖 Your AI Trip Assistant</h1>
            <br>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Planning your {st.session_state.trip_data.get('duration', 'N/A')}-day trip to {st.session_state.trip_data.get('destination', 'your destination')}</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        # Chat interface
        render_chat()

        user_input = st.chat_input("Ask me anything about your trip or request changes...")
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.chat_message("assistant"):
                with st.spinner("Planning your perfect trip..."):
                    model_text = call_gemini(st.session_state.messages, user_input)

                # Display the response (tool calls are handled internally)
                st.markdown(model_text)
                st.session_state.messages.append({"role": "assistant", "content": model_text})

    # Save dialog
    if st.session_state.get('show_save_dialog', False):
        st.markdown("---")
        st.subheader("💾 Save Your Trip")
        
        with st.form("save_trip_form"):
            trip_name = st.text_input(
                "Trip Name *", 
                placeholder="e.g., Tokyo Adventure 2024",
                help="Give your trip a memorable name"
            )
            trip_summary = st.text_area(
                "Trip Summary (Optional)", 
                placeholder="Brief description of your trip...",
                help="Add a short description of what makes this trip special"
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.form_submit_button("💾 Save Trip", type="primary"):
                    if trip_name.strip():
                        # Save the trip using the integration
                        try:
                            save_result = trip_planner_ai._handle_save_trip({
                                'trip_name': trip_name.strip(),
                                'trip_summary': trip_summary.strip()
                            })
                            
                            if save_result.get("status") == "saved":
                                st.success(f"✅ {save_result.get('message')}")
                                st.session_state.show_save_dialog = False
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"❌ {save_result.get('message')}")
                        except Exception as e:
                            st.error(f"Failed to save trip: {str(e)}")
                    else:
                        st.error("Please enter a trip name!")
            
            with col2:
                if st.form_submit_button("❌ Cancel"):
                    st.session_state.show_save_dialog = False
                    st.rerun()
            
            with col3:
                if st.form_submit_button("📚 View Saved Trips"):
                    st.session_state.show_save_dialog = False
                    st.session_state.page = "trips"
                    st.rerun()

    with st.container(horizontal_alignment="center", horizontal=True):

        if st.button("⬅️ Back to Form", type="secondary", width="content"):
            st.session_state.page = "form"
            st.rerun()

        elif st.button("💾 Save Itinerary", type="primary"):
            # Show save dialog
            st.session_state.show_save_dialog = True
            st.rerun()


def show_trips_page():
    """Show the saved trips"""
    # Header with trip info
    st.markdown(f"""
        <div style="text-align: center;">
            <h1 style="color: #666;">📚 Saved Trips</h1>
            <br>
            <p style="opacity: 0.9;">Here you can find your saved trips, click on each trip to get details</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Import trip storage
    try:
        from src.ai.trip_storage import trip_storage
        
        # Get saved trips
        saved_trips = trip_storage.list_trips()
        
        if not saved_trips:
            st.info("🗺️ No saved trips yet. Create a trip and save it to see it here!")
            st.info("💡 Use the **📝 Plan Trip** button in the sidebar to start planning.")
        else:
            st.write(f"**Found {len(saved_trips)} saved trip(s):**")
            
            # Display trips in a nice format
            for trip in saved_trips:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        trip_name = trip.get('trip_name', 'Untitled Trip')
                        st.subheader(f"🗺️ {trip_name}")
                        st.write(f"**📍 Destination:** {trip.get('destination', 'Unknown')}")
                        st.write(f"**📅 Duration:** {trip.get('duration', 'N/A')} days")
                        st.write(f"**🎯 Type:** {trip.get('travel_type', 'N/A')}")
                        if trip.get('trip_summary'):
                            st.write(f"**📝 Summary:** {trip.get('trip_summary')}")
                    
                    with col2:
                        created_date = trip.get('created_at', '')
                        if created_date:
                            try:
                                from datetime import datetime
                                date_obj = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                                formatted_date = date_obj.strftime("%B %d, %Y")
                                st.write(f"**Saved:** {formatted_date}")
                            except:
                                st.write(f"**Saved:** {created_date[:10]}")
                        
                        st.write(f"**Trip ID:** {trip.get('trip_id', 'N/A')}")
                    
                    with col3:
                        if st.button("📖 View Details", key=f"view_{trip.get('trip_id')}"):
                            st.session_state.selected_trip_id = trip.get('trip_id')
                            st.session_state.show_trip_details = True
                        
                        if st.button("🗑️ Delete", key=f"delete_{trip.get('trip_id')}"):
                            if trip_storage.delete_trip(trip.get('trip_id')):
                                st.success("Trip deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete trip")
            
            # Show trip details if selected
            if st.session_state.get('show_trip_details') and st.session_state.get('selected_trip_id'):
                st.markdown("---")
                st.subheader("📋 Trip Details")
                
                # Load full trip data
                full_trip = trip_storage.load_trip(st.session_state.selected_trip_id)
                if full_trip:
                    trip_data = full_trip.get('trip_data', {})
                    form_data = trip_data.get('form_data', {})
                    itinerary = trip_data.get('itinerary', {})
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**🗺️ Trip Information:**")
                        st.write(f"• **Name:** {trip_data.get('trip_name', 'Untitled')}")
                        st.write(f"• **Destination:** {form_data.get('destination', 'N/A')}")
                        st.write(f"• **Duration:** {form_data.get('duration', 'N/A')} days")
                        st.write(f"• **Travel Type:** {form_data.get('travel_type', 'N/A')}")
                        st.write(f"• **Budget:** {form_data.get('budget', 'N/A')}")
                        st.write(f"• **Group Size:** {form_data.get('group_size', 'N/A')} people")
                        st.write(f"• **Accommodation:** {form_data.get('accommodation', 'N/A')}")
                    
                    with col2:
                        st.write("**📝 Trip Summary:**")
                        summary = trip_data.get('trip_summary', 'No summary provided')
                        st.write(summary)
                        
                        st.write("**📅 Created:**")
                        created_date = full_trip.get('created_at', '')
                        if created_date:
                            try:
                                from datetime import datetime
                                date_obj = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                                formatted_date = date_obj.strftime("%B %d, %Y at %I:%M %p")
                                st.write(formatted_date)
                            except:
                                st.write(created_date)
                    
                    # Show itinerary if available
                    if itinerary and not itinerary.get('demo_mode'):
                        st.write("**🗓️ Itinerary:**")
                        if itinerary.get('ai_response'):
                            st.markdown(itinerary['ai_response'])
                        else:
                            st.write("No detailed itinerary available")
                    elif itinerary and itinerary.get('demo_mode'):
                        st.write("**🗓️ Demo Itinerary:**")
                        if itinerary.get('demo_response'):
                            st.markdown(itinerary['demo_response'])
                    
                    # Special requests
                    if form_data.get('special_requests'):
                        st.write("**✨ Special Requests:**")
                        st.write(form_data['special_requests'])
                    
                    if st.button("❌ Close Details"):
                        st.session_state.show_trip_details = False
                        st.session_state.selected_trip_id = None
                        st.rerun()
                else:
                    st.error("Could not load trip details")
                    st.session_state.show_trip_details = False
            
            # Navigation is now available in the sidebar
                    
    except Exception as e:
        st.error(f"Error loading saved trips: {e}")
        st.info("💡 Use the sidebar navigation to go to other pages.")

# =========================
# Main App Router
# =========================
if st.session_state.page == "landing":
    show_landing_page()
elif st.session_state.page == "form":
    show_form_page()
elif st.session_state.page == "chatbot":
    show_chatbot_page()
elif st.session_state.page == "trips":
    show_trips_page()