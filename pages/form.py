import streamlit as st
from datetime import datetime, timedelta
from styles.styles import (
    FORM_PAGE_HTML,
    BASIC_INFO_HEADER,
    ADDITIONAL_PREFERENCES_HEADER
)
from services.prompt_loader import render_user_prompt

def get_season_from_date(date: datetime) -> str:
    """Determine season based on date."""
    month = date.month
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Autumn"

def get_travel_months(start_date: datetime, end_date: datetime) -> list[str]:
    """Get list of travel months between start and end date."""
    travel_months = []
    current_date = start_date
    while current_date <= end_date:
        month_name = current_date.strftime("%B")
        if month_name not in travel_months:
            travel_months.append(month_name)
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1, day=1)
        if current_date > end_date:
            break
    return travel_months

if "form_data" not in st.session_state:
    st.session_state.form_data = {}

# Display session state for debugging
# st.write(st.session_state)

form_data = st.session_state.form_data

with st.container(horizontal_alignment="center"):
    st.markdown(body=FORM_PAGE_HTML, unsafe_allow_html=True)

    with st.form(key="trip_form", clear_on_submit=False):
        st.markdown(BASIC_INFO_HEADER, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            destination = st.text_input(
                "📍 Where do you want to go?",
                value=form_data.get('destination', ''),
                placeholder="e.g., Paris, Tokyo, Himachal Pradesh",
                help="Enter your desired destination city, country, or region"
            )

            today = datetime.now()   
            
            # Set default dates from form_data if available
            default_start = today
            default_end = today + timedelta(days=2)
            
            if form_data.get('start_date') and form_data.get('end_date'):
                try:
                    default_start = datetime.fromisoformat(form_data['start_date']).date()
                    default_end = datetime.fromisoformat(form_data['end_date']).date()
                except:
                    pass  # Use default dates if parsing fails

            date_range = st.date_input(
                "📅 When are you going?",
                (default_start, default_end),
                format="DD.MM.YYYY",
                help="Select the dates for your trip"
                )

            # Extract start and end dates with validation
            if len(date_range) == 2:
                start_date = date_range[0]
                end_date = date_range[1]
            elif len(date_range) == 1:
                start_date = date_range[0]
                end_date = date_range[0] + timedelta(days=2)
            else:
                start_date = today
                end_date = today + timedelta(days=2)
            
            # Ensure end_date is after start_date
            if end_date <= start_date:
                end_date = start_date + timedelta(days=1)
            
            duration = (end_date - start_date).days
        
        with col2:
            travel_type_options = [
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
            ]
            travel_type_index = 9  # Default to Mixed Experience
            if form_data.get('travel_type') in travel_type_options:
                travel_type_index = travel_type_options.index(form_data.get('travel_type'))
            
            travel_type = st.selectbox(
                "🎯 What type of experience are you looking for?",
                options=travel_type_options,
                index=travel_type_index,
                help="Choose the type of activities you're most interested in"
            )
            
            budget_options = ["Low Budget (Budget-friendly options)", "Medium Budget (Comfortable spending)", "High Budget (Luxury experience)"]
            budget_index = 1  # Default to Medium
            if form_data.get('budget') in budget_options:
                budget_index = budget_options.index(form_data.get('budget'))
            
            budget = st.selectbox(
                "💰 What's your budget range?",
                options=budget_options,
                index=budget_index,
                help="Select your preferred budget range for the trip"
            )
        
        # Additional preferences
        st.markdown(ADDITIONAL_PREFERENCES_HEADER, unsafe_allow_html=True)
        
        with st.container(horizontal=True, horizontal_alignment="center"):
            group_size = st.number_input(
                "👥 Number of travelers",
                min_value=1,
                max_value=100,
                value=form_data.get('group_size', 2),
                help="How many people will be traveling?"
            )
            
            accommodation_options = ["Any", "Hotels", "Hostels", "Vacation Rentals", "Resorts", "Boutique Properties"]
            accommodation_index = 0  # Default to Any
            if form_data.get('accommodation') in accommodation_options:
                accommodation_index = accommodation_options.index(form_data.get('accommodation'))
        
            accommodation = st.selectbox(
                "🏨 Preferred accommodation",
                options=accommodation_options,
                index=accommodation_index,
                help="What type of accommodation do you prefer?"
            )
        
        special_requests = st.text_area(
            "📝 Any special requests or interests?",
            value=form_data.get('special_requests', ''),
            placeholder="e.g., vegetarian food options, accessibility needs, specific attractions to visit...",
            help="Tell us about any specific requirements or interests"
        )

        season = get_season_from_date(start_date)
        travel_months = get_travel_months(start_date, end_date)
        
        # Form submission
        st.markdown("<br>", unsafe_allow_html=True)

        # Always save form data to session state (for persistence)
        current_form_data = {
            "destination": destination,
            "duration": duration,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "season": season,
            "travel_months": travel_months,
            "travel_type": travel_type,
            "budget": budget,
            "group_size": group_size,
            "accommodation": accommodation,
            "special_requests": special_requests
        }
        st.session_state.form_data = current_form_data

        with st.container(horizontal=True, horizontal_alignment="center"):

            back_button = st.form_submit_button("⬅️ Back to Home", type="secondary", width="content")
            
            if back_button:
                st.session_state.form_data = {}
                st.switch_page("app.py")

            submitted = st.form_submit_button("Generate My Trip Plan", type="primary", width="content")
            
            if submitted:
                if not destination.strip():
                    st.error("Please enter a destination!")
                else:
                    # Store the trip data when submitted
                    st.session_state.trip_data = current_form_data.copy()
                                        
                    # Prepare template context
                    context = {
                        'destination': destination,
                        'duration': duration,
                        'start_date': start_date.strftime("%B %d, %Y"),
                        'end_date': end_date.strftime("%B %d, %Y"),
                        'season': season,
                        'travel_months': ", ".join(travel_months),
                        'group_size': group_size,
                        'travel_type': travel_type,
                        'budget': budget,
                        'accommodation': accommodation,
                        'special_requests': special_requests.strip() if special_requests.strip() else None
                    }
                    
                    # Render the prompt using the template
                    initial_prompt = render_user_prompt(context)
                    
                    # Store the initial prompt for future use
                    st.session_state.initial_prompt = initial_prompt
                    
                    # Show success message and navigate to chatbot
                    st.success("🎉 Trip plan generated! Redirecting to your AI assistant...")
                    st.info("💡 Your AI assistant will help you refine and customize your itinerary.")
                    
                    # Navigate to chatbot page
                    st.switch_page("pages/chatbot.py")