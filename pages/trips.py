import streamlit as st
from services.logging import logger
from services.firebase_auth import get_user_id
from datetime import datetime
import re
from services.export import generate_trip_pdf
from services.trip_storage import list_trips, load_trip
from styles.styles import TRIPS_HEADER

@st.dialog(title="Trip Details", width="large")
def show_trip_modal(trip_id):
    """Display trip details in a modal popup"""
    # Load full trip data using the proper function
    user_id = get_user_id()
    full_trip = load_trip(trip_id, user_id=user_id)
    
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
    is_booked = full_trip.get('is_booked', False)
    
    st.markdown(f"### :material/map: {trip_name}")
    
    # Show booking status badge
    if is_booked:
        booked_date = full_trip.get('booked_at', '')
        if booked_date:
            try:
                date_obj = datetime.fromisoformat(booked_date.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime("%B %d, %Y")
                st.success(f"✅ Trip Booked on {formatted_date}")
            except:
                st.success("✅ Trip Booked")
    
    st.markdown(f"**From:** {origin}")
    st.markdown(f"**To:** {destination}")
    
    # Create tabs for better organization
    tab1, tab2 = st.tabs([":material/view_list: Overview", ":material/calendar_month: Itinerary"])
    
    with tab1:
        # Trip overview in two columns
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = form_data.get('start_date', 'N/A')
            end_date = form_data.get('end_date', 'N/A')
            st.write(f"**Travel Dates:** {start_date} to {end_date}")

            st.write(f"**Group Details:** {form_data.get('group_size', 'N/A')} people")
            st.write(f"**Type:** {form_data.get('travel_type', 'N/A')}")
            
            st.write(f"**Budget:** {form_data.get('budget', 'N/A')}")
            st.write(f"**Stay:** {form_data.get('accommodation', 'N/A')}")
        
        with col2:
            st.write(f"**Season:** {form_data.get('season', 'N/A')}")
            if isinstance(form_data.get('travel_months', 'N/A'), list):
                travel_months = ', '.join(form_data.get('travel_months', 'N/A'))
            st.write(f"**Months:** {travel_months}")

            st.write(f"**Duration:** {form_data.get('duration', 'N/A')} days")
            
            st.write(f"**Trip Summary:** {trip_data.get('trip_summary', 'No summary provided')}")
            
            # Special requests if any
            special_requests = form_data.get('special_requests', '').strip()
            if special_requests:
                st.write(f"**Special Requests:** {special_requests}")

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
        if st.button(":material/refresh: Recreate Trip", use_container_width=True):
            # Set up session state to recreate this trip
            st.session_state.trip_data = form_data.copy()
            
            # Generate new initial prompt from the form data
            from services.prompt_loader import render_user_prompt
            context = {
                'origin': form_data.get('origin', ''),
                'destination': form_data.get('destination', ''),
                'start_date': form_data.get('start_date', ''),
                'end_date': form_data.get('end_date', ''),
                'season': form_data.get('season', ''),
                'travel_months': form_data.get('travel_months', ''),
                'travel_type': form_data.get('travel_type', ''),
                'budget': form_data.get('budget', ''),
                'group_size': form_data.get('group_size', ''),
                'accommodation': form_data.get('accommodation', ''),
                'special_requests': form_data.get('special_requests', '').strip() if form_data.get('special_requests', '').strip() else None
            }
            st.session_state.initial_prompt = render_user_prompt(context)
            
            # Reset processing flags and clear old conversation
            st.session_state.initial_prompt_processed = False
            st.session_state.main_trip_itinerary = None
            st.session_state.messages = []  # Clear old conversation
            
            # Close modal and navigate
            st.session_state.show_trip_modal = False
            st.session_state.selected_trip_id = None
            st.switch_page("pages/chatbot.py")
    
    with col2:
        if st.button(":material/edit: Edit Trip", use_container_width=True):
            # Pre-populate form with existing data
            st.session_state.form_data = form_data.copy()
            st.session_state.show_trip_modal = False
            st.session_state.selected_trip_id = None
            st.switch_page("pages/form.py")
    
    with col3:
        # PDF Download/Generate button
        pdf_key = f"pdf_ready_{trip_id}"
        
        # Check if PDF is already generated for this trip and data is valid
        pdf_data_valid = False
        if st.session_state.get(pdf_key):
            try:
                # Verify the PDF data is still accessible and valid
                pdf_info = st.session_state[pdf_key]
                if pdf_info.get('data') and len(pdf_info['data']) > 0:
                    pdf_data_valid = True
            except (KeyError, TypeError, AttributeError):
                # Clean up corrupted PDF data
                st.session_state.pop(pdf_key, None)
                pdf_data_valid = False
        
        if pdf_data_valid:
            # Show download button for ready PDF
            try:
                st.download_button(
                    label=":material/download: Download PDF",
                    data=st.session_state[pdf_key]['data'],
                    file_name=st.session_state[pdf_key]['filename'],
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                    key=f"download_pdf_{trip_id}"  # Unique key to prevent conflicts
                )
            except Exception as e:
                # If download fails, clear the corrupted data and show generate button
                logger.warning(f"PDF download failed for trip {trip_id}: {e}")
                st.session_state.pop(pdf_key, None)
                st.error("PDF file is no longer available. Please generate a new one.")
                pdf_data_valid = False
        
        if not pdf_data_valid:
            # Show generate button
            if st.button(":material/download: Generate PDF", use_container_width=True, key=f"generate_pdf_{trip_id}"):
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
                        
                        # Store PDF data in session state with validation
                        st.session_state[pdf_key] = {
                            'data': pdf_data,
                            'filename': filename,
                            'generated_at': datetime.now().isoformat()  # Add timestamp for debugging
                        }
                        
                        logger.info(f"PDF generated successfully: {filename} ({len(pdf_data)} bytes)")
                        st.success(f"PDF generated successfully! ({len(pdf_data):,} bytes)")
                        st.rerun()
                        
                except Exception as e:
                    logger.error(f"Error generating PDF for trip {trip_id}: {e}")
                    st.error(f"Unable to generate PDF: {str(e)}")
                    # Clear any partial data
                    st.session_state.pop(pdf_key, None)
    
    with col4:
        # Generate New button (only show if PDF is ready)
        if st.session_state.get(pdf_key):
            if st.button(":material/refresh: Generate New", use_container_width=True, key=f"regenerate_{trip_id}"):
                st.session_state.pop(pdf_key, None)
                st.rerun()
        else:
            # Empty space when no PDF is generated
            st.write("")
    
    with col5:
        if st.button(":material/close: Close", use_container_width=True):
            st.session_state.show_trip_modal = False
            st.session_state.selected_trip_id = None
            # Clean up any PDF data for this trip to prevent memory leaks
            pdf_key = f"pdf_ready_{trip_id}"
            st.session_state.pop(pdf_key, None)
            st.rerun()

# Initialize session state for trips page
def initialize_trips_session():
    """Initialize trips page session state and prevent unwanted regeneration"""
    # Clean up any stale PDF data that might cause media file errors
    cleanup_stale_pdf_data()

def cleanup_stale_pdf_data():
    """Clean up stale PDF data from session state to prevent media file errors"""
    try:
        # Find all PDF keys in session state
        pdf_keys_to_remove = []
        for key in st.session_state.keys():
            if key.startswith('pdf_ready_'):
                try:
                    # Try to access the PDF data to see if it's still valid
                    pdf_info = st.session_state[key]
                    if not pdf_info.get('data') or len(pdf_info['data']) == 0:
                        pdf_keys_to_remove.append(key)
                except (KeyError, TypeError, AttributeError):
                    pdf_keys_to_remove.append(key)
        
        # Remove stale PDF data
        for key in pdf_keys_to_remove:
            st.session_state.pop(key, None)
            logger.info(f"Cleaned up stale PDF data: {key}")
            
    except Exception as e:
        logger.warning(f"Error during PDF cleanup: {e}")
    # Only initialize once per session to prevent duplicate operations
    if st.session_state.get('trips_page_initialized'):
        return
    
    # Clear UI-specific flags on page navigation (preserve trip data)
    ui_keys_to_clear = ["chatbot_initialized", "chatbot_session_fully_initialized"]
    for key in ui_keys_to_clear:
        st.session_state.pop(key, None)
    
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
    # Get all trips for the logged-in user
    user_id = get_user_id()
    all_trips = list_trips(user_id=user_id)
    
    # Separate trips into saved and booked
    saved_trips = [trip for trip in all_trips if not trip.get('is_booked', False)]
    booked_trips = [trip for trip in all_trips if trip.get('is_booked', False)]
    
    if not all_trips:
        st.warning("No saved trips yet. Create a trip and save it to see it here!")
        st.info("Use the **Plan** button on top to start planning.")
        
        # Add helpful button for new trip planning
        with st.container(horizontal_alignment="center", horizontal=True):
            if st.button("Create Your First Trip", type="primary"):
                st.switch_page("pages/form.py")
    else:
        # Display booked trips section first
        if booked_trips:
            st.markdown("### ✅ Booked Trips")
            st.write(f"**{len(booked_trips)} trip(s) ready to go:**")
            st.markdown("---")
            
            # Display booked trips
            for trip in booked_trips:
                with st.container(border=True):                
                    
                    trip_name = trip.get('trip_name', 'Untitled Trip')
                    st.subheader(f"✈️ {trip_name}")
                    
                    # Show booking badge
                    booked_date = trip.get('booked_at', '')
                    if booked_date:
                        try:
                            date_obj = datetime.fromisoformat(booked_date.replace('Z', '+00:00'))
                            formatted_date = date_obj.strftime("%B %d, %Y")
                            st.success(f"🎉 Booked on {formatted_date}")
                        except:
                            st.success("🎉 Booked")

                    col1, col2, col3 = st.columns([3, 2, 1])

                    with col1:
                        st.write(f"**:material/map: From:** {trip.get('origin', 'Unknown')}")
                        st.write(f"**:material/pin_drop: To:** {trip.get('destination', 'Unknown')}")
                        st.write(f"**:material/calendar_month: Duration:** {trip.get('start_date', 'N/A')} to {trip.get('end_date', 'N/A')}")
                        if trip.get('trip_summary'):
                            st.write(f"**:material/description: Summary:** {trip.get('trip_summary')}")
                    
                    with col2:
                        created_date = trip.get('created_at', '')
                        if created_date:
                            try:
                                date_obj = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                                formatted_date = date_obj.strftime("%B %d, %Y")
                                st.write(f"**:material/bookmark: Created:** {formatted_date}")
                            except:
                                st.write(f"**:material/bookmark: Created:** {created_date[:10]}")
                        
                            st.write(f"**:material/group: Travelers:** {trip.get('group_size', 'N/A')}")
                            st.write(f"**:material/payments: Budget:** {trip.get('budget', 'N/A')}")
                            st.write(f"**:material/travel_explore: Type:** {trip.get('travel_type', 'N/A')}")
                                    
                    with col3:
                        if st.button(":material/view_list: View Details", key=f"view_booked_{trip.get('trip_id')}"):
                            st.session_state.selected_trip_id = trip.get('trip_id')
                            st.session_state.show_trip_modal = True
                            st.rerun()
                        
                        if st.button(":material/delete: Delete", key=f"delete_booked_{trip.get('trip_id')}"):
                            # Find and remove the trip from session state
                            trip_id = trip.get('trip_id')
                            if "saved_trip_data" in st.session_state:
                                st.session_state.saved_trip_data = [
                                    t for t in st.session_state.saved_trip_data 
                                    if t.get('trip_id') != trip_id
                                ]
                                st.success("Trip deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete trip")
            
            st.markdown("<br>", unsafe_allow_html=True)
        
        # Display saved trips section
        if saved_trips:
            st.markdown("### 📝 Saved Trips")
            st.write(f"**{len(saved_trips)} trip(s) ready to book:**")
            st.markdown("---")
            
            # Display saved trips
            for trip in saved_trips:
                with st.container(border=True):                
                    
                    trip_name = trip.get('trip_name', 'Untitled Trip')
                    st.subheader(f"{trip_name}")

                    col1, col2, col3 = st.columns([3, 2, 1])

                    with col1:
                        st.write(f"**:material/map: From:** {trip.get('origin', 'Unknown')}")
                        st.write(f"**:material/pin_drop: To:** {trip.get('destination', 'Unknown')}")
                        st.write(f"**:material/calendar_month: Duration:** {trip.get('start_date', 'N/A')} to {trip.get('end_date', 'N/A')}")
                        if trip.get('trip_summary'):
                            st.write(f"**:material/description: Summary:** {trip.get('trip_summary')}")
                    
                    with col2:
                        created_date = trip.get('created_at', '')
                        if created_date:
                            try:
                                date_obj = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                                formatted_date = date_obj.strftime("%B %d, %Y")
                                st.write(f"**:material/bookmark: Saved:** {formatted_date}")
                            except:
                                st.write(f"**:material/bookmark: Saved:** {created_date[:10]}")
                        
                            st.write(f"**:material/group: Travelers:** {trip.get('group_size', 'N/A')}")
                            st.write(f"**:material/payments: Budget:** {trip.get('budget', 'N/A')}")
                            st.write(f"**:material/travel_explore: Type:** {trip.get('travel_type', 'N/A')}")
                                    
                    with col3:
                        if st.button(":material/view_list: View Details", key=f"view_{trip.get('trip_id')}"):
                            st.session_state.selected_trip_id = trip.get('trip_id')
                            st.session_state.show_trip_modal = True
                            st.rerun()

                        # Only show Book button for unbooked trips
                        if not trip.get('is_booked', False):
                            if st.button(":material/paid: Book Trip", key=f"book_{trip.get('trip_id')}", type="primary"):
                                # Set the trip to book and navigate to booking page
                                st.session_state.selected_booking_trip = trip.get('trip_id')
                                st.session_state.show_trip_modal = False
                                st.session_state.selected_trip_id = None
                                st.switch_page("pages/book.py")
                        
                        if st.button(":material/delete: Delete", key=f"delete_{trip.get('trip_id')}"):
                            # Find and remove the trip from session state
                            trip_id = trip.get('trip_id')
                            if "saved_trip_data" in st.session_state:
                                st.session_state.saved_trip_data = [
                                    t for t in st.session_state.saved_trip_data 
                                    if t.get('trip_id') != trip_id
                                ]
                                st.success("Trip deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete trip")
        
        # Show trip details modal if selected
        if st.session_state.get('show_trip_modal') and st.session_state.get('selected_trip_id'):
            show_trip_modal(st.session_state.selected_trip_id)
                
except Exception as e:
    st.error(f"Error loading saved trips: {e}")
    st.info("Use the sidebar navigation to go to other pages.")