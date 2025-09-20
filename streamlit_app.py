import streamlit as st
from styles.styles import (
    LANDING_PAGE_HTML, 
    PERSONALISED_WIDGET, 
    PLANNING_WIDGET, 
    INTERACTIVE_WIDGET
)
# Display session state for debugging
# st.write(st.session_state)

# Navigation
landing = st.Page("pages/landing.py", title="Home", icon=":material/home:", default=True)
chatbot = st.Page("pages/chatbot.py", title="Chat", icon=":material/chat:")
form = st.Page("pages/form.py", title="Plan", icon=":material/assignment:")
trips = st.Page("pages/trips.py", title="Trips", icon=":material/trip:")


pg = st.navigation([
    landing,
    form,
    chatbot,
    trips
])
pg.run()