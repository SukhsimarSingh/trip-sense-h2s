import streamlit as st
from services.firebase_auth import get_user_id
from services.trip_storage import load_trip, list_trips, update_trip
from services.serpapi_service import search_flights, search_hotels, search_events, get_demo_flights, get_demo_hotels, get_demo_events
from styles.page_headers import BOOK_HEADER
from datetime import datetime
import random

# Payment Modal
@st.dialog("💳 Complete Payment", width="large")
def show_payment_modal(trip_id, amount, trip_name):
    """Display payment modal for booking confirmation"""
    st.markdown(f"### Booking: {trip_name}")
    st.markdown(f"**Total Amount:** ${amount:,.2f}")
    
    st.markdown("---")
    
    # Mock payment form
    with st.form("payment_form"):
        st.markdown("#### Payment Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            card_number = st.text_input(
                "Card Number *",
                placeholder="1234 5678 9012 3456",
                max_chars=19
            )
            expiry = st.text_input(
                "Expiry Date *",
                placeholder="MM/YY",
                max_chars=5
            )
        
        with col2:
            cardholder_name = st.text_input(
                "Cardholder Name *",
                placeholder="John Doe"
            )
            cvv = st.text_input(
                "CVV *",
                placeholder="123",
                type="password",
                max_chars=3
            )
        
        billing_address = st.text_area(
            "Billing Address *",
            placeholder="Enter your billing address"
        )
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cancel_btn = st.form_submit_button(":material/close: Cancel", use_container_width=True)
            if cancel_btn:
                st.session_state.show_payment_modal = False
                st.rerun()
        
        with col2:
            submit_btn = st.form_submit_button(":material/credit_card: Pay Now", type="primary", use_container_width=True)
            
            if submit_btn:
                # Validate fields
                if not card_number or not expiry or not cardholder_name or not cvv or not billing_address:
                    st.error(":material/warning: Please fill in all required fields")
                elif len(card_number.replace(" ", "")) < 13:
                    st.error(":material/warning: Invalid card number")
                elif len(cvv) != 3:
                    st.error(":material/warning: Invalid CVV")
                else:
                    # Mock payment processing
                    with st.spinner("Processing payment..."):
                        import time
                        time.sleep(2)
                    
                    # Generate mock transaction ID
                    transaction_id = f"TXN{random.randint(100000, 999999)}"
                    
                    # Save booking info
                    save_booking_info(
                        trip_id=trip_id,
                        transaction_id=transaction_id,
                        amount=amount,
                        payment_method="Credit Card",
                        card_last4=card_number[-4:] if len(card_number) >= 4 else "****"
                    )
                    
                    # Mark payment as completed
                    st.session_state[f'payment_completed_{trip_id}'] = True
                    st.session_state[f'transaction_id_{trip_id}'] = transaction_id
                    st.session_state.show_payment_modal = False
                    
                    # Mark trip as booked
                    user_id = get_user_id()
                    update_trip(
                        trip_id=trip_id,
                        updates={
                            "is_booked": True,
                            "booked_at": datetime.now().isoformat(),
                            "transaction_id": transaction_id
                        },
                        user_id=user_id
                    )
                    
                    st.success(f":material/check_circle: Payment successful! Transaction ID: {transaction_id}")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()

def save_booking_info(trip_id, transaction_id, amount, payment_method, card_last4):
    """Save booking information to Firestore"""
    try:
        from services.firebase_service import get_firestore_client
        from services.firebase_auth import get_user_id
        
        db = get_firestore_client()
        user_id = get_user_id()
        
        # Get current trip data to include booking selections
        trip_data = load_trip(trip_id, user_id=user_id)
        
        # Collect selected booking details
        selected_flight = st.session_state.get(f'selected_flight_data_{trip_id}', {})
        selected_hotel = st.session_state.get(f'selected_hotel_data_{trip_id}', {})
        selected_event = st.session_state.get(f'selected_event_data_{trip_id}', {})
        contact_info = st.session_state.get('booking_contact_info', {})
        
        booking_data = {
            'trip_id': trip_id,
            'user_id': user_id,
            'transaction_id': transaction_id,
            'amount': amount,
            'payment_method': payment_method,
            'card_last4': card_last4,
            'booked_at': datetime.now().isoformat(),
            'status': 'confirmed',
            'trip_details': {
                'trip_name': trip_data.get('trip_name', 'Untitled Trip'),
                'origin': trip_data.get('origin', ''),
                'destination': trip_data.get('destination', ''),
                'start_date': trip_data.get('start_date', ''),
                'end_date': trip_data.get('end_date', ''),
                'group_size': trip_data.get('group_size', 1)
            },
            'selections': {
                'flight': selected_flight,
                'hotel': selected_hotel,
                'event': selected_event
            },
            'contact_info': contact_info
        }
        
        # Save to Firestore 'bookings' collection
        booking_ref = db.collection('bookings').document(f"{user_id}_{trip_id}")
        booking_ref.set(booking_data)
        
        print(f"✅ [BOOKING] Booking info saved to Firestore for trip {trip_id}")
        
    except Exception as e:
        print(f"❌ [BOOKING] Error saving booking info: {e}")

# Display page header
st.markdown(BOOK_HEADER, unsafe_allow_html=True)

# Get user trips for the selector
user_id = get_user_id()
print(f"🔍 [BOOK PAGE] Loading trips list for user: {user_id}")

all_trips = list_trips(user_id=user_id)
print(f"✅ [BOOK PAGE] Loaded {len(all_trips)} trips")

# Filter out already booked trips
unbooked_trips = [trip for trip in all_trips if not trip.get('is_booked', False)]
print(f"📋 [BOOK PAGE] {len(unbooked_trips)} unbooked trips available")

# Check if user has any unbooked trips
if not unbooked_trips:
    if all_trips:
        # User has trips but they're all booked
        st.info(":material/celebration: All your trips are already booked!")
        st.success("View your booked trips in the **Trips** section or create a new trip to plan.")
    else:
        # User has no trips at all
        st.warning("No saved trips yet. Create a trip to start booking!")
        st.info("Use the **Plan** button on top to start planning.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button(":material/add: Create Your First Trip", type="primary", use_container_width=True):
            st.switch_page("pages/form.py")
    
    st.stop()

# Trip Selector Dropdown
st.markdown("### :material/flight_takeoff: Select Trip to Book")

# Create trip options for selectbox
trip_options = {}
default_index = 0

for idx, trip in enumerate(unbooked_trips):
    trip_id = trip.get('trip_id')
    trip_label = f"{trip.get('trip_name', 'Untitled Trip')} - {trip.get('origin', '?')} → {trip.get('destination', '?')}"
    trip_options[trip_label] = trip_id
    
    # Set default index if this trip was pre-selected
    if st.session_state.get('selected_booking_trip') == trip_id:
        default_index = idx

# Display the selectbox
selected_trip_label = st.selectbox(
    "Choose a trip:",
    options=list(trip_options.keys()),
    index=default_index,
    label_visibility="collapsed",
    key="trip_selector"
)

# Get the selected trip ID
selected_trip_id = trip_options[selected_trip_label]

# Update session state with the selected trip
st.session_state.selected_booking_trip = selected_trip_id

st.markdown("---")

# Load the selected trip details
trip_id = selected_trip_id

print(f"🔍 [BOOK PAGE] Loading trip details for: {trip_id}")
full_trip = load_trip(trip_id, user_id=user_id)
print(f"✅ [BOOK PAGE] Trip details loaded")

if not full_trip:
    st.error("Could not load trip details")
    if st.button(":material/arrow_back: Go Back to Trips"):
        del st.session_state.selected_booking_trip
        st.switch_page("pages/trips.py")
    st.stop()

trip_data = full_trip.get('trip_data', {})
form_data = trip_data.get('form_data', {})
itinerary = trip_data.get('itinerary', {})

# Trip header
trip_name = trip_data.get('trip_name', 'Your Trip')
origin = form_data.get('origin', '')
destination = form_data.get('destination', '')
start_date = form_data.get('start_date', '')
end_date = form_data.get('end_date', '')
group_size = form_data.get('group_size', 2)

st.markdown(f"### :material/luggage: {trip_name}")

# Trip overview in bordered container
with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**:material/pin_drop: Travel Plan**")
        st.write(f"{origin} → {destination}")
        st.write(f"**:material/calendar_month: Travel Dates**")
        st.write(f"{start_date} to {end_date}")        
    
    with col2:
        st.write(f"**:material/payments: Budget**")
        st.write(f"{form_data.get('budget', 'N/A')}")
        st.write(f"**:material/hotel: Accommodation**")
        st.write(f"{form_data.get('accommodation', 'N/A')}")
    
    with col3:
        st.write(f"**:material/group: Travelers**")
        st.write(f"{group_size} people")
        st.write(f"**:material/schedule: Duration**")
        st.write(f"{form_data.get('duration', 'N/A')} days")

st.markdown("---")

# Traveler Information Form
st.markdown("### :material/person: Traveler Information")
st.info(":material/lightbulb_2: **Get Ready to Book!** Fill in your details below. You'll need this information when booking flights, hotels, and transportation.")

with st.container(border=True):
    st.markdown("#### Primary Contact Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        lead_name = st.text_input("Full Name *", placeholder="John Doe", key="lead_name")
        lead_email = st.text_input("Email Address *", placeholder="john@example.com", key="lead_email")
    
    with col2:
        lead_phone = st.text_input("Phone Number *", placeholder="+1 234 567 8900", key="lead_phone")
        lead_country = st.selectbox("Country *", 
            ["India", "United States", "United Kingdom", "Canada", "Australia", "Singapore", "UAE", "Other"],
            key="lead_country"
        )

# Passenger Details
if group_size > 1:
    st.markdown("---")
    with st.container(border=True):
        st.markdown(f"#### Passenger Details ({group_size} Travelers)")
        st.caption("Enter details for all passengers (including yourself)")
        
        # Initialize passenger data in session state
        if "passenger_details" not in st.session_state:
            st.session_state.passenger_details = [{} for _ in range(group_size)]
        
        # Ensure we have the right number of passenger slots
        if len(st.session_state.passenger_details) != group_size:
            st.session_state.passenger_details = [{} for _ in range(group_size)]
        
        for i in range(group_size):
            with st.expander(f"Passenger {i + 1}" + (" (Primary Contact)" if i == 0 else ""), expanded=(i < 2)):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Pre-fill first passenger with lead details
                    default_name = lead_name if i == 0 and lead_name else ""
                    st.text_input(
                        "Full Name *",
                        value=default_name,
                        placeholder="As per ID/Passport",
                        key=f"passenger_{i}_name"
                    )
                
                with col2:
                    st.number_input(
                        "Age *",
                        min_value=0,
                        max_value=120,
                        value=30,
                        key=f"passenger_{i}_age"
                    )
                
                with col3:
                    st.selectbox(
                        "Gender *",
                        ["Male", "Female", "Other"],
                        key=f"passenger_{i}_gender"
                    )

st.markdown("---")

# Save button for traveler info
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    save_info_btn = st.button(":material/save: Save Traveler Information", type="primary", use_container_width=True)
    
    if save_info_btn:
        # Validate required fields
        if not lead_name or not lead_email or not lead_phone:
            st.error(":material/warning: Please fill in all required contact details (marked with *)")
        else:
            # Collect all passenger details
            passengers = []
            for i in range(group_size):
                passenger_name = st.session_state.get(f"passenger_{i}_name", "")
                passenger_age = st.session_state.get(f"passenger_{i}_age", 0)
                passenger_gender = st.session_state.get(f"passenger_{i}_gender", "")
                
                passengers.append({
                    "name": passenger_name,
                    "age": passenger_age,
                    "gender": passenger_gender
                })
            
            # Store in session state
            st.session_state.booking_contact_info = {
                "name": lead_name,
                "email": lead_email,
                "phone": lead_phone,
                "country": lead_country,
                "passengers": passengers,
                "group_size": group_size,
                "saved": True
            }
            st.success(f":material/check_circle: Traveler information saved for {group_size} traveler(s)! You can now proceed with the booking guide below.")
            st.balloons()

st.markdown("---")

# Check if user has saved their information
if st.session_state.get("booking_contact_info", {}).get("saved"):
    # Show booking guide
    st.markdown("### :material/checklist: Step-by-Step Booking Guide")
    st.write("Follow this comprehensive guide to book all components of your trip")
    
    # Initialize trip-specific booking progress (unique per trip)
    progress_key = f'booking_progress_{trip_id}'
    
    # Reset progress if this is a different trip than last time
    if st.session_state.get('current_booking_trip_id') != trip_id:
        # Clear old trip's progress and info
        st.session_state.current_booking_trip_id = trip_id
        st.session_state.pop(progress_key, None)
        print(f"🔄 [BOOKING] Switched to new trip {trip_id}, resetting progress")
    
    if progress_key not in st.session_state:
        st.session_state[progress_key] = {
            'flights': False,
            'accommodation': False,
            'activities': False,
            'insurance': False,
            'documents': False
        }
        print(f"✨ [BOOKING] Initialized fresh progress for trip {trip_id}")
    
    progress = st.session_state[progress_key]
    total_steps = len(progress)
    completed_steps = sum(progress.values())
    
    # Progress bar
    st.progress(completed_steps / total_steps, text=f"Progress: {completed_steps}/{total_steps} steps completed")
    
    st.markdown("---")
    
    # Show saved contact info and estimated costs
    saved_info = st.session_state.get("booking_contact_info", {})
    
    col_info, col_cost = st.columns([1, 1])
    
    with col_info:
        with st.expander(":material/person: Your Saved Information", expanded=False):
            st.markdown("**Primary Contact:**")
            st.write(f"• **Name:** {saved_info.get('name', 'N/A')}")
            st.write(f"• **Email:** {saved_info.get('email', 'N/A')}")
            st.write(f"• **Phone:** {saved_info.get('phone', 'N/A')}")
            st.write(f"• **Country:** {saved_info.get('country', 'N/A')}")
            
            # Show all travelers
            passengers = saved_info.get('passengers', [])
            if passengers and len(passengers) > 0:
                st.markdown("---")
                st.markdown(f"**All Travelers ({len(passengers)}):**")
                for idx, passenger in enumerate(passengers, 1):
                    if passenger.get('name'):
                        st.write(f"{idx}. {passenger.get('name', 'N/A')} - {passenger.get('age', 'N/A')}yrs ({passenger.get('gender', 'N/A')})")
    
    with col_cost:
        with st.expander(":material/payments: Estimated Booking Cost", expanded=False):
            # Calculate estimated costs based on trip data
            duration = form_data.get('duration', 5)
            budget_type = form_data.get('budget', 'Medium Budget')
            
            # Base estimates per person per category
            cost_multipliers = {
                'Budget': {'flight': 200, 'hotel': 50, 'activity': 30, 'transport': 20},
                'Medium Budget': {'flight': 400, 'hotel': 100, 'activity': 60, 'transport': 40},
                'Luxury': {'flight': 800, 'hotel': 250, 'activity': 150, 'transport': 80}
            }
            
            multiplier = cost_multipliers.get(budget_type, cost_multipliers['Medium Budget'])
            
            # Calculate estimates
            flight_cost = multiplier['flight'] * group_size
            hotel_cost = multiplier['hotel'] * duration * group_size
            activity_cost = multiplier['activity'] * duration * group_size
            transport_cost = multiplier['transport'] * duration * group_size
            
            total_estimate = flight_cost + hotel_cost + activity_cost + transport_cost
            
            st.markdown("**Per Category (All Travelers):**")
            st.write(f":material/flight: **Flights:** ${flight_cost:,.0f}")
            st.write(f":material/hotel: **Hotels:** ${hotel_cost:,.0f} ({duration} nights)")
            st.write(f":material/flag: **Activities:** ${activity_cost:,.0f}")
            st.write(f":material/directions_car: **Transportation:** ${transport_cost:,.0f}")
            
            st.markdown("---")
            st.markdown(f"### **Total Estimate:** ${total_estimate:,.0f}")
            st.caption(f"For {group_size} traveler(s) × {duration} days")
            st.caption("*Estimates based on your budget preference. Actual costs may vary.")
    
    st.markdown("---")
    
    # Booking checklist steps
    with st.container(border=True):
        # Step 1: Flights
        with st.expander(":material/flight: **Flights**", expanded=not progress['flights']):
            st.write(f"**Route:** {origin} → {destination}")
            st.write(f"**Date:** {start_date}")
            st.write(f"**Passengers:** {group_size}")
            
            st.markdown("---")
            
            # Real-time flight search
            col_search, col_manual = st.columns([1, 1])
            
            with col_search:
                if st.button(":material/search: Find Real-Time Flights", key=f"search_flights_{trip_id}", use_container_width=True):
                    with st.spinner("Searching for flights..."):
                        flight_results = search_flights(
                            origin=origin,
                            destination=destination,
                            departure_date=start_date,
                            return_date=end_date,
                            adults=group_size
                        )
                        st.session_state[f'flight_results_{trip_id}'] = flight_results
            
            with col_manual:
                st.link_button(":material/language: Search on EaseMyTrip", "https://www.easemytrip.com/flights.html", use_container_width=True)
            
            # Display flight results if available
            flight_cache_key = f'flight_results_{trip_id}'
            if flight_cache_key in st.session_state:
                flight_data = st.session_state[flight_cache_key]
                
                if flight_data.get('demo_mode'):
                    if flight_data.get('error') and 'airport' in flight_data.get('error', '').lower():
                        # Airport code error - show helpful message
                        st.error(f":material/error: {flight_data.get('message', 'Unknown error')}")
                        if flight_data.get('suggestion'):
                            st.info(f":material/lightbulb: **Tip:** {flight_data.get('suggestion')}")
                            st.caption("Common airport codes: Chennai=MAA, Mumbai=BOM, Delhi=DEL, Paris=CDG, London=LHR, New York=JFK")
                        flights_to_show = []
                    else:
                        st.warning(":material/warning: SerpAPI not configured. Showing demo data. Add SERPAPI_API_KEY to .env for real data.")
                        flights_to_show = get_demo_flights()
                elif flight_data.get('success'):
                    flights_to_show = flight_data.get('best_flights', [])[:3]
                else:
                    st.error(f":material/error: Error: {flight_data.get('message', 'Unknown error')}")
                    flights_to_show = get_demo_flights()
                
                if flights_to_show:
                    st.markdown("**:material/flight: Available Flights:**")
                    st.caption("Select one flight option:")
                    
                    # Initialize flight selection in session state
                    flight_selection_key = f'selected_flight_{trip_id}'
                    if flight_selection_key not in st.session_state:
                        st.session_state[flight_selection_key] = None
                    
                    # Create flight options for radio group
                    flight_options = []
                    for idx, flight in enumerate(flights_to_show, 1):
                        airline = flight.get('airline', 'N/A')
                        price = flight.get('price', 'N/A')
                        departure = flight.get('departure_time', 'N/A')
                        arrival = flight.get('arrival_time', 'N/A')
                        flight_options.append(f"Flight {idx}: {airline} - {price} ({departure} → {arrival})")
                    
                    # Single radio group for all flights
                    # Validate stored index is within range
                    stored_index = st.session_state[flight_selection_key]
                    default_index = None
                    if stored_index is not None and 0 <= stored_index < len(flights_to_show):
                        default_index = stored_index
                    
                    selected_option = st.radio(
                        "Choose your flight:",
                        options=range(len(flights_to_show)),
                        format_func=lambda x: flight_options[x],
                        key=f"flight_radio_group_{trip_id}",
                        index=default_index
                    )
                    
                    # Update selection when changed
                    if selected_option is not None:
                        st.session_state[flight_selection_key] = selected_option
                        st.session_state[f'selected_flight_data_{trip_id}'] = flights_to_show[selected_option]
                    
                    # Display selected flight details
                    if selected_option is not None:
                        st.markdown("---")
                        st.markdown("**Selected Flight Details:**")
                        flight = flights_to_show[selected_option]
                        
                        with st.container(border=True):
                            col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
                            
                            with col1:
                                # Show airline logo if available
                                airline_logo = flight.get('airline_logo', '')
                                if airline_logo:
                                    st.image(airline_logo, width=60)
                                else:
                                    st.markdown(":material/flight:")
                            
                            with col2:
                                st.write(f"**{flight.get('airline', 'N/A')}** - {flight.get('flight_number', '')}")
                                st.caption(f":material/flight_takeoff: {flight.get('departure_time', 'N/A')} → :material/flight_land: {flight.get('arrival_time', 'N/A')}")
                                st.caption(f"{flight.get('departure_airport', '')} → {flight.get('arrival_airport', '')}")
                            
                            with col3:
                                st.write(f":material/schedule: **{flight.get('duration', 'N/A')}**")
                                stops = flight.get('stops', 0)
                                # Safely convert stops to int
                                try:
                                    stops_int = int(stops) if stops else 0
                                    if stops_int == 0:
                                        st.caption(":material/check_circle: Direct flight")
                                    else:
                                        st.caption(f":material/swap_horiz: {stops_int} stop(s)")
                                except (ValueError, TypeError):
                                    st.caption(f":material/swap_horiz: {stops} stop(s)")
                                
                                # Show carbon emissions if available
                                emissions = flight.get('carbon_emissions', {})
                                if emissions:
                                    diff = emissions.get('difference_percent', 0)
                                    try:
                                        diff_val = float(diff) if diff else 0
                                        if diff_val < 0:
                                            st.caption(f":material/eco: {abs(diff_val):.0f}% less CO₂")
                                    except (ValueError, TypeError):
                                        pass  # Skip if conversion fails
                            
                            with col4:
                                st.markdown(f"### {flight.get('price', 'N/A')}")
                                st.caption(flight.get('travel_class', 'Economy'))
                    
                    # Confirm Flight Selection Button
                    st.markdown("---")
                    flight_confirmed_key = f'flight_confirmed_{trip_id}'
                    
                    if st.session_state.get(flight_confirmed_key):
                        selected_flight = st.session_state.get(f'selected_flight_data_{trip_id}')
                        if selected_flight:
                            st.success(f":material/check_circle: Flight Confirmed: {selected_flight.get('airline', 'N/A')} - {selected_flight.get('price', 'N/A')}")
                    else:
                        if st.button(":material/check: Confirm Flight Selection", key=f"confirm_flight_{trip_id}", type="primary", disabled=st.session_state[flight_selection_key] is None):
                            st.session_state[flight_confirmed_key] = True
                            st.session_state[progress_key]['flights'] = True
                            st.success("Flight selection confirmed!")
                            st.rerun()
            
            # Checkbox removed - auto-completed when flight is confirmed
        
        # Step 2: Accommodation
        with st.expander(":material/hotel: **Accommodation**", expanded=progress['flights'] and not progress['accommodation']):
            st.write(f"**Location:** {destination}")
            st.write(f"**Check-in:** {start_date}")
            st.write(f"**Check-out:** {end_date}")
            st.write(f"**Guests:** {group_size}")
            
            st.markdown("---")
            
            # Real-time hotel search
            col_search, col_manual = st.columns([1, 1])
            
            with col_search:
                if st.button(":material/search: Find Real-Time Hotels", key=f"search_hotels_{trip_id}", use_container_width=True):
                    with st.spinner("Searching for hotels..."):
                        hotel_results = search_hotels(
                            location=destination,
                            check_in=start_date,
                            check_out=end_date,
                            adults=group_size
                        )
                        st.session_state[f'hotel_results_{trip_id}'] = hotel_results
            
            with col_manual:
                st.link_button(":material/language: Search on EaseMyTrip", "https://www.easemytrip.com/hotels/", use_container_width=True)
            
            # Display hotel results if available
            hotel_cache_key = f'hotel_results_{trip_id}'
            if hotel_cache_key in st.session_state:
                hotel_data = st.session_state[hotel_cache_key]
                
                if hotel_data.get('demo_mode'):
                    st.warning(":material/warning: SerpAPI not configured. Showing demo data. Add SERPAPI_API_KEY to .env for real data.")
                    hotels_to_show = get_demo_hotels()
                elif hotel_data.get('success'):
                    hotels_to_show = hotel_data.get('hotels', [])[:3]
                else:
                    st.error(f":material/error: Error: {hotel_data.get('message', 'Unknown error')}")
                    hotels_to_show = get_demo_hotels()
                
                if hotels_to_show:
                    st.markdown("**:material/hotel: Available Hotels:**")
                    st.caption("Select one hotel option:")
                    
                    # Initialize hotel selection in session state
                    hotel_selection_key = f'selected_hotel_{trip_id}'
                    if hotel_selection_key not in st.session_state:
                        st.session_state[hotel_selection_key] = None
                    
                    # Create hotel options for radio group
                    hotel_options = []
                    for idx, hotel in enumerate(hotels_to_show, 1):
                        name = hotel.get('name', 'N/A')
                        total = hotel.get('total_rate', 'N/A')
                        rating = hotel.get('rating', 'N/A')
                        hotel_options.append(f"Hotel {idx}: {name} - {total} (Rating: {rating}/5)")
                    
                    # Single radio group for all hotels
                    # Validate stored index is within range
                    stored_index = st.session_state[hotel_selection_key]
                    default_index = None
                    if stored_index is not None and 0 <= stored_index < len(hotels_to_show):
                        default_index = stored_index
                    
                    selected_option = st.radio(
                        "Choose your hotel:",
                        options=range(len(hotels_to_show)),
                        format_func=lambda x: hotel_options[x],
                        key=f"hotel_radio_group_{trip_id}",
                        index=default_index
                    )
                    
                    # Update selection when changed
                    if selected_option is not None:
                        st.session_state[hotel_selection_key] = selected_option
                        st.session_state[f'selected_hotel_data_{trip_id}'] = hotels_to_show[selected_option]
                    
                    # Display selected hotel details
                    if selected_option is not None:
                        st.markdown("---")
                        st.markdown("**Selected Hotel Details:**")
                        hotel = hotels_to_show[selected_option]
                        
                        with st.container(border=True):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                # Hotel name and type
                                hotel_type = hotel.get('type', 'Hotel')
                                hotel_class = hotel.get('extracted_hotel_class', 0)
                                # Safely convert hotel_class to int
                                try:
                                    hotel_class_int = int(hotel_class) if hotel_class else 0
                                    stars = "⭐" * hotel_class_int if hotel_class_int > 0 else ""
                                except (ValueError, TypeError):
                                    stars = ""
                                
                                st.write(f"**{hotel.get('name', 'N/A')}** {stars}")
                                st.caption(f"📍 {hotel_type}")
                                
                                # Rating and reviews
                                rating = hotel.get('rating', 0)
                                reviews = hotel.get('reviews', 0)
                                # Safely handle rating and reviews display
                                try:
                                    if rating and rating != 'N/A':
                                        rating_val = float(rating) if isinstance(rating, str) else rating
                                        reviews_val = int(reviews) if reviews and reviews != 'N/A' else 0
                                        st.caption(f"⭐ {rating_val}/5 · {reviews_val:,} reviews")
                                except (ValueError, TypeError):
                                    pass  # Skip if conversion fails
                                
                                # Amenities
                                amenities = hotel.get('amenities', [])[:5]
                                if amenities:
                                    amenity_icons = {
                                        'Free Wi-Fi': '📶',
                                        'Pool': '🏊',
                                        'Parking': '🅿️',
                                        'Gym': '💪',
                                        'Restaurant': '🍽️',
                                        'Air conditioning': '❄️',
                                        'Spa': '🧖'
                                    }
                                    amenity_str = " • ".join([
                                        amenity_icons.get(a, '✓') + " " + a 
                                        for a in amenities[:4]
                                    ])
                                    st.caption(amenity_str)
                                
                                # Eco certified badge
                                if hotel.get('eco_certified'):
                                    st.caption("🌱 Eco Certified")
                            
                            with col2:
                                per_night = hotel.get('rate_per_night', 'N/A')
                                total = hotel.get('total_rate', 'N/A')
                                
                                st.markdown(f"### {per_night}")
                                st.caption("per night")
                                st.markdown(f"**Total: {total}**")
                                
                                # Show nearby places if available
                                nearby = hotel.get('nearby_places', [])
                                if nearby:
                                    st.caption(f"📍 Near {len(nearby)} attractions")
                    
                    # Confirm Hotel Selection Button
                    st.markdown("---")
                    hotel_confirmed_key = f'hotel_confirmed_{trip_id}'
                    
                    if st.session_state.get(hotel_confirmed_key):
                        selected_hotel = st.session_state.get(f'selected_hotel_data_{trip_id}')
                        if selected_hotel:
                            st.success(f":material/check_circle: Hotel Confirmed: {selected_hotel.get('name', 'N/A')} - {selected_hotel.get('total_rate', 'N/A')}")
                    else:
                        if st.button(":material/check: Confirm Hotel Selection", key=f"confirm_hotel_{trip_id}", type="primary", disabled=st.session_state[hotel_selection_key] is None):
                            st.session_state[hotel_confirmed_key] = True
                            st.session_state[progress_key]['accommodation'] = True
                            st.success("Hotel selection confirmed!")
                            st.rerun()
            
            # Checkbox removed - auto-completed when hotel is confirmed
        
        # Step 3: Activities & Events
        with st.expander(":material/local_activity: **Activities & Events**", expanded=progress['accommodation'] and not progress['activities']):
            st.write(f"**Destination:** {destination}")
            st.write(f"**Travel Style:** {form_data.get('travel_type', 'N/A')}")
            
            # Show suggested activities from itinerary
            if itinerary and itinerary.get('days'):
                st.markdown("**Suggested from your itinerary:**")
                days = itinerary.get('days', [])[:2]
                for i, day in enumerate(days, 1):
                    activities = day.get('activities', [])[:2]
                    for activity in activities:
                        st.write(f"• {activity.get('name', 'Activity')}")
            
            st.markdown("---")
            
            # Real-time event search
            col_search, col_manual = st.columns([1, 1])
            
            with col_search:
                if st.button(":material/search: Find Local Events", key=f"search_events_{trip_id}", use_container_width=True):
                    with st.spinner("Searching for events..."):
                        event_results = search_events(
                            location=destination,
                            start_date=start_date,
                            end_date=end_date
                        )
                        st.session_state[f'event_results_{trip_id}'] = event_results
            
            with col_manual:
                st.link_button(":material/language: Browse on EaseMyTrip", "https://www.easemytrip.com/activities/", use_container_width=True)
            
            # Display event results if available
            event_cache_key = f'event_results_{trip_id}'
            if event_cache_key in st.session_state:
                event_data = st.session_state[event_cache_key]
                
                if event_data.get('demo_mode'):
                    st.warning(":material/warning: SerpAPI not configured. Showing demo data. Add SERPAPI_API_KEY to .env for real data.")
                    events_to_show = get_demo_events()
                elif event_data.get('success'):
                    events_to_show = event_data.get('events', [])[:5]
                else:
                    st.error(f":material/error: Error: {event_data.get('message', 'Unknown error')}")
                    events_to_show = get_demo_events()
                
                if events_to_show:
                    st.markdown("**Happening During Your Trip:**")
                    st.caption("Select one event/activity:")
                    
                    # Initialize event selection in session state
                    event_selection_key = f'selected_event_{trip_id}'
                    if event_selection_key not in st.session_state:
                        st.session_state[event_selection_key] = None
                    
                    # Create event options for radio group
                    event_options = []
                    for idx, event in enumerate(events_to_show, 1):
                        title = event.get('title', 'N/A')
                        venue = event.get('venue', 'N/A')
                        date = event.get('date', 'N/A')
                        event_options.append(f"Event {idx}: {title} at {venue} ({date})")
                    
                    # Single radio group for all events
                    # Validate stored index is within range
                    stored_index = st.session_state[event_selection_key]
                    default_index = None
                    if stored_index is not None and 0 <= stored_index < len(events_to_show):
                        default_index = stored_index
                    
                    selected_option = st.radio(
                        "Choose your event/activity:",
                        options=range(len(events_to_show)),
                        format_func=lambda x: event_options[x],
                        key=f"event_radio_group_{trip_id}",
                        index=default_index
                    )
                    
                    # Update selection when changed
                    if selected_option is not None:
                        st.session_state[event_selection_key] = selected_option
                        st.session_state[f'selected_event_data_{trip_id}'] = events_to_show[selected_option]
                    
                    # Display selected event details
                    if selected_option is not None:
                        st.markdown("---")
                        st.markdown("**Selected Event Details:**")
                        event = events_to_show[selected_option]
                        
                        with st.container(border=True):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.write(f"**{event.get('title', 'N/A')}**")
                                venue = event.get('venue', 'N/A')
                                st.caption(f":material/location_on: {venue}")
                            
                            with col2:
                                date = event.get('date', 'N/A')
                                time = event.get('time', 'N/A')
                                st.caption(f":material/calendar_today: {date}")
                                if time != 'N/A':
                                    st.caption(f":material/schedule: {time}")
                    
                    # Confirm Event Selection Button
                    st.markdown("---")
                    events_confirmed_key = f'events_confirmed_{trip_id}'
                    
                    if st.session_state.get(events_confirmed_key):
                        selected_event = st.session_state.get(f'selected_event_data_{trip_id}')
                        if selected_event:
                            st.success(f":material/check_circle: Event Confirmed: {selected_event.get('title', 'Event')}")
                    else:
                        if st.button(":material/check: Confirm Event Selection", key=f"confirm_events_{trip_id}", type="primary", disabled=st.session_state[event_selection_key] is None):
                            st.session_state[events_confirmed_key] = True
                            st.session_state[progress_key]['activities'] = True
                            st.success("Event selection confirmed!")
                            st.rerun()
            
            # Checkbox removed - auto-completed when events are confirmed
        
        # Step 4: Travel Insurance
        with st.expander(":material/security: **Travel Insurance**", expanded=progress['activities'] and not progress['insurance']):
            st.write("**Coverage includes:**")
            st.write("• Trip cancellations")
            st.write("• Medical emergencies")
            st.write("• Lost baggage")
            
            insurance_checked = st.checkbox(":material/check_circle: Insurance Secured", key=f"insurance_check_{trip_id}", value=progress['insurance'])
            if insurance_checked and not progress['insurance']:
                st.session_state[progress_key]['insurance'] = True
                st.success("You're protected! :material/verified_user:")
        
        # Step 5: Documents
        with st.expander(":material/description: **Documents**", expanded=progress['insurance'] and not progress['documents']):
            st.write("**Essential items:**")
            st.checkbox("Valid passport", key=f"doc_passport_{trip_id}")
            st.checkbox("Visa (if required)", key=f"doc_visa_{trip_id}")
            st.checkbox("Flight tickets", key=f"doc_flights_{trip_id}")
            st.checkbox("Hotel confirmations", key=f"doc_hotels_{trip_id}")
            
            documents_checked = st.checkbox(":material/check_circle: All Documents Ready", key=f"documents_check_{trip_id}", value=progress['documents'])
            if documents_checked and not progress['documents']:
                st.session_state[progress_key]['documents'] = True
                st.success("You're ready to go! :material/celebration:")
                st.balloons()
    
    # Check if main selections are confirmed (flights, hotels, events)
    flight_confirmed = st.session_state.get(f'flight_confirmed_{trip_id}', False)
    hotel_confirmed = st.session_state.get(f'hotel_confirmed_{trip_id}', False)
    events_confirmed = st.session_state.get(f'events_confirmed_{trip_id}', False)
    
    all_confirmed = flight_confirmed and hotel_confirmed and events_confirmed and progress['insurance'] and progress['documents']
    payment_completed = st.session_state.get(f'payment_completed_{trip_id}', False)
    
    if all_confirmed and not payment_completed:
        st.markdown("---")
        st.success(":material/check_circle: **All selections confirmed! Ready for payment.**")
        
        # Calculate total amount
        selected_flight = st.session_state.get(f'selected_flight_data_{trip_id}', {})
        selected_hotel = st.session_state.get(f'selected_hotel_data_{trip_id}', {})
        
        # Parse prices (remove currency symbols and commas)
        def parse_price(price_str):
            if isinstance(price_str, str):
                import re
                numbers = re.findall(r'[\d,]+', price_str)
                if numbers:
                    return float(numbers[0].replace(',', ''))
            return 0
        
        flight_price = parse_price(selected_flight.get('price', '$0'))
        hotel_price = parse_price(selected_hotel.get('total_rate', '$0'))
        
        total_amount = flight_price + hotel_price
        
        st.markdown(f"### :material/payments: Total Amount: ${total_amount:,.2f}")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(":material/credit_card: Proceed to Payment", type="primary", use_container_width=True, key="proceed_to_payment"):
                st.session_state.show_payment_modal = True
                st.session_state.payment_amount = total_amount
                st.rerun()
    
    elif payment_completed:
        st.markdown("---")
        st.success(":material/celebration: **Congratulations! Your trip is fully booked!**")
        st.markdown("### :material/luggage: You're Ready to Go!")
        st.info(":material/bookmark: This trip has been moved to your **Booked Trips** section.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(":material/description: View Booked Trips", use_container_width=True):
                st.session_state.selected_trip_id = trip_id
                st.session_state.show_trip_modal = True
                if 'selected_booking_trip' in st.session_state:
                    del st.session_state.selected_booking_trip
                # Clean up trip-specific progress
                if progress_key in st.session_state:
                    del st.session_state[progress_key]
                if 'booking_contact_info' in st.session_state:
                    del st.session_state.booking_contact_info
                if 'current_booking_trip_id' in st.session_state:
                    del st.session_state.current_booking_trip_id
                st.switch_page("pages/trips.py")
        with col2:
            if st.button(":material/flight: Plan Another Trip", use_container_width=True):
                if 'selected_booking_trip' in st.session_state:
                    del st.session_state.selected_booking_trip
                # Clean up trip-specific progress
                if progress_key in st.session_state:
                    del st.session_state[progress_key]
                if 'booking_contact_info' in st.session_state:
                    del st.session_state.booking_contact_info
                if 'current_booking_trip_id' in st.session_state:
                    del st.session_state.current_booking_trip_id
                st.switch_page("pages/form.py")

else:
    st.warning(":material/warning: Please save your traveler information above before proceeding with the booking guide.")
    st.info(":material/arrow_upward: Fill in the form above and click ':material/save: Save Traveler Information' to continue.")

# End of booking guide section

# Navigation buttons at bottom
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button(":material/arrow_back: Back to Trips", use_container_width=True, key="back_btn"):
        # Clear booking state - but keep progress for this trip
        if 'selected_booking_trip' in st.session_state:
            del st.session_state.selected_booking_trip
        # Don't delete progress here - user might want to come back
        st.switch_page("pages/trips.py")
with col2:
    if st.button(":material/view_list: View Trip Details", use_container_width=True, type="primary", key="view_trip_btn"):
        # Navigate to trips page and open the modal for this trip
        st.session_state.selected_trip_id = trip_id
        st.session_state.show_trip_modal = True
        if 'selected_booking_trip' in st.session_state:
            del st.session_state.selected_booking_trip
        st.switch_page("pages/trips.py")

# Show payment modal if triggered
if st.session_state.get('show_payment_modal', False):
    show_payment_modal(
        trip_id=trip_id,
        amount=st.session_state.get('payment_amount', 0),
        trip_name=trip_name
    )
