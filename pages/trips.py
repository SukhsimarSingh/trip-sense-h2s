import streamlit as st
from services.trip_storage import trip_storage
from services.logging import logger
from datetime import datetime
import re
from services.export import generate_trip_pdf
from styles.styles import TRIPS_HEADER

@st.dialog(title="Trip Details", width="large")
def show_trip_modal(trip_id):
    """Display trip details in a modal popup"""
    # Load full trip data
    full_trip = trip_storage.load_trip(trip_id)
    if not full_trip:
        st.error("Could not load trip details")
        if st.button("Close"):
            st.session_state.show_trip_modal = False
            st.session_state.selected_trip_id = None
            st.rerun()
        return
    
    trip_data = full_trip.get('trip_data', {})
    form_data = trip_data.get('form_data', {})
    itinerary = trip_data.get('itinerary', {})
    
    # Trip header with name and destination
    trip_name = trip_data.get('trip_name', 'Untitled Trip')
    origin = form_data.get('origin', 'Unknown Origin')
    destination = form_data.get('destination', 'Unknown Destination')
    st.markdown(f"### 🗺️ {trip_name}")
    st.markdown(f"**🛫 From:** {origin}")
    st.markdown(f"**📍 To:** {destination}")
    
    # Create tabs for better organization
    tab1, tab2 = st.tabs(["📋 Overview", "🗓️ Itinerary"])
    
    with tab1:
        # Trip overview in two columns
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = form_data.get('start_date', 'N/A')
            end_date = form_data.get('end_date', 'N/A')
            st.write(f"**🗓️ Travel Dates:** {start_date} to {end_date}")

            st.write(f"**👥 Group Details:** {form_data.get('group_size', 'N/A')} people")
            st.write(f"**🎯 Type:** {form_data.get('travel_type', 'N/A')}")
            
            st.write(f"**💰 Budget:** {form_data.get('budget', 'N/A')}")
            st.write(f"**🏨 Stay:** {form_data.get('accommodation', 'N/A')}")
        
        with col2:
            st.write(f"**🌍 Season:** {form_data.get('season', 'N/A')}")
            if isinstance(form_data.get('travel_months', 'N/A'), list):
                travel_months = ', '.join(form_data.get('travel_months', 'N/A'))
            st.write(f"**🗓️ Months:** {travel_months}")

            st.write(f"**🗓️ Duration:** {form_data.get('duration', 'N/A')} days")
            
            st.write(f"**📝 Trip Summary:** {trip_data.get('trip_summary', 'No summary provided')}")
            
            # Special requests if any
            special_requests = form_data.get('special_requests', '').strip()
            if special_requests:
                st.write(f"**✨ Special Requests:** {special_requests}")

    with tab2:
        # Show itinerary
        if itinerary and not itinerary.get('demo_mode'):
            if itinerary.get('ai_response'):
                st.markdown(itinerary['ai_response'])
            else:
                st.info("No detailed itinerary available for this trip.")
        elif itinerary and itinerary.get('demo_mode'):
            if itinerary.get('demo_response'):
                st.markdown(itinerary['demo_response'])
            else:
                st.info("No demo itinerary available.")
        else:
            st.info("No itinerary has been generated for this trip yet.")
    
    # Action buttons at the bottom
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    
    with col1:
        if st.button("🔄 Recreate Trip", use_container_width=True):
            # Set up session state to recreate this trip
            st.session_state.trip_data = form_data.copy()
            st.session_state.initial_prompt = None  # Will be regenerated
            st.session_state.show_trip_modal = False
            st.session_state.selected_trip_id = None
            st.switch_page("pages/chatbot.py")
    
    with col2:
        if st.button("📝 Edit Trip", use_container_width=True):
            # Pre-populate form with existing data
            st.session_state.form_data = form_data.copy()
            st.session_state.show_trip_modal = False
            st.session_state.selected_trip_id = None
            st.switch_page("pages/form.py")
    
    with col3:
        # PDF Download/Generate button
        pdf_key = f"pdf_ready_{trip_id}"
        
        # Check if PDF is already generated for this trip
        if st.session_state.get(pdf_key):
            # Show download button for ready PDF
            st.download_button(
                label="📄 Download PDF",
                data=st.session_state[pdf_key]['data'],
                file_name=st.session_state[pdf_key]['filename'],
                mime="application/pdf",
                use_container_width=True
            )
        else:
            # Show generate button
            if st.button("📄 Generate PDF", use_container_width=True):
                try:
                    with st.spinner("Generating PDF..."):
                        logger.info(f"Starting PDF generation for trip: {trip_name} (ID: {trip_id})")
                        pdf_buffer = generate_trip_pdf(trip_data, form_data, itinerary, trip_name, trip_id)
                        
                        if pdf_buffer is None:
                            raise Exception("PDF generation returned None")
                        
                        # Create filename
                        safe_trip_name = re.sub(r'[^\w\s-]', '', trip_name).strip()
                        safe_trip_name = re.sub(r'[-\s]+', '-', safe_trip_name)
                        filename = f"{safe_trip_name}_{trip_id[:8]}.pdf"
                        
                        # Get PDF data
                        pdf_data = pdf_buffer.getvalue()
                        if len(pdf_data) == 0:
                            raise Exception("Generated PDF is empty")
                        
                        # Store PDF data in session state
                        st.session_state[pdf_key] = {
                            'data': pdf_data,
                            'filename': filename
                        }
                        
                        logger.info(f"PDF generated successfully: {filename} ({len(pdf_data)} bytes)")
                        st.success(f"PDF generated successfully! ({len(pdf_data):,} bytes)")
                        st.rerun()
                        
                except Exception as e:
                    logger.error(f"Error generating PDF: {e}")
                    st.error("Unable to generate PDF. Please try again later.")
    
    with col4:
        # Generate New button (only show if PDF is ready)
        if st.session_state.get(pdf_key):
            if st.button("🔄 Generate New", use_container_width=True, key=f"regenerate_{trip_id}"):
                st.session_state.pop(pdf_key, None)
                st.rerun()
        else:
            # Empty space when no PDF is generated
            st.write("")
    
    with col5:
        if st.button("❌ Close", use_container_width=True):
            st.session_state.show_trip_modal = False
            st.session_state.selected_trip_id = None
            # Clean up any PDF data for this trip to prevent memory leaks
            pdf_key = f"pdf_ready_{trip_id}"
            st.session_state.pop(pdf_key, None)
            st.rerun()

# Initialize session state for trips page
def initialize_trips_session():
    """Initialize trips page session state and prevent unwanted regeneration"""
    # Only initialize once per session to prevent duplicate operations
    if st.session_state.get('trips_page_initialized'):
        return
    
    # Only clear data if we're actually navigating to trips page (not on rerun)
    previous_page = st.session_state.get('current_page', '')
    is_page_navigation = previous_page != "trips"
    
    # Clear only UI-specific flags, preserve all trip data
    ui_keys = ["chatbot_initialized", "chatbot_session_fully_initialized"]
    cleared_keys = []
    
    for key in ui_keys:
        if key in st.session_state:
            del st.session_state[key]
            cleared_keys.append(key)
    
    # Only clean up PDF data on actual page navigation, not on rerun
    if is_page_navigation:
        pdf_keys_to_remove = [key for key in st.session_state.keys() if key.startswith('pdf_ready_')]
        for key in pdf_keys_to_remove:
            del st.session_state[key]
            cleared_keys.append(key)
        
        if cleared_keys:
            logger.debug(f"Trips page navigation: Cleared UI keys: {cleared_keys}")
    
    # Set trips page as active and mark as initialized
    st.session_state.current_page = "trips"
    st.session_state.trips_page_initialized = True

# Initialize the trips session
initialize_trips_session()

# Check if user just saved a trip (show success message)
if st.session_state.get('trip_just_saved'):
    st.success("Trip saved successfully! You can view it below.")
    # Clear the flag
    del st.session_state.trip_just_saved

# Header with trip info
st.markdown(TRIPS_HEADER, unsafe_allow_html=True)

# Import trip storage
try: 
    # Get saved trips
    saved_trips = trip_storage.list_trips()
    
    if not saved_trips:
        st.info("No saved trips yet. Create a trip and save it to see it here!")
        st.info("Use the **📝 Plan Trip** button in the sidebar to start planning.")
        
        # Add helpful button for new trip planning
        with st.container(horizontal_alignment="center", horizontal=True):
            if st.button("Create Your First Trip", type="primary"):
                st.switch_page("pages/form.py")
    else:
        st.write(f"**Found {len(saved_trips)} saved trip(s):**")
        
        # Display trips in a nice format
        for trip in saved_trips:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    trip_name = trip.get('trip_name', 'Untitled Trip')
                    st.subheader(f"{trip_name}")
                    st.write(f"**🛫 From:** {trip.get('origin', 'Unknown')}")
                    st.write(f"**📍 To:** {trip.get('destination', 'Unknown')}")
                    st.write(f"**📅 Duration:** {trip.get('start_date', 'N/A')} to {trip.get('end_date', 'N/A')}")
                    st.write(f"**🎯 Type:** {trip.get('travel_type', 'N/A')}")
                    if trip.get('trip_summary'):
                        st.write(f"**📝 Summary:** {trip.get('trip_summary')}")
                
                with col2:
                    created_date = trip.get('created_at', '')
                    if created_date:
                        try:
                            date_obj = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                            formatted_date = date_obj.strftime("%B %d, %Y")
                            st.write(f"**Saved:** {formatted_date}")
                        except:
                            st.write(f"**Saved:** {created_date[:10]}")
                    
                    st.write(f"**Trip ID:** {trip.get('trip_id', 'N/A')}")
                
                with col3:
                    if st.button("📖 View Details", key=f"view_{trip.get('trip_id')}"):
                        st.session_state.selected_trip_id = trip.get('trip_id')
                        st.session_state.show_trip_modal = True
                        st.rerun()
                    
                    if st.button("🗑️ Delete", key=f"delete_{trip.get('trip_id')}"):
                        if trip_storage.delete_trip(trip.get('trip_id')):
                            st.success("Trip deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete trip")
        
        # Show trip details modal if selected
        if st.session_state.get('show_trip_modal') and st.session_state.get('selected_trip_id'):
            show_trip_modal(st.session_state.selected_trip_id)
        
        # Navigation is now available in the sidebar
                
except Exception as e:
    st.error(f"Error loading saved trips: {e}")
    st.info("Use the sidebar navigation to go to other pages.")