import streamlit as st
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
], position = "top")
pg.run()