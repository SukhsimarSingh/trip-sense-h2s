import streamlit as st

# Set page config
st.set_page_config(page_title="Trip Sense", page_icon=":material/beach_access:", layout="wide")

# Routes
landing = st.Page("pages/landing.py", title="Home", icon=":material/home:", default=True)
chatbot = st.Page("pages/chatbot.py", title="Chat", icon=":material/chat:")
form = st.Page("pages/form.py", title="Plan", icon=":material/assignment:")
trips = st.Page("pages/trips.py", title="Trips", icon=":material/trip:")

# Navbar
pg = st.navigation([
    landing,
    form,
    chatbot,
    trips
], position = "top")
pg.run()