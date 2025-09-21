import streamlit as st
from styles.styles import (
    LANDING_PAGE_HTML, 
    WIDGETS
)

# Main landing page content
with st.container(horizontal_alignment="center"):

    st.markdown(body=LANDING_PAGE_HTML, unsafe_allow_html=True)

    plan_button = st.button("Start Planning Your Trip", type="primary", key="start_planning", help="Click to begin your travel planning journey")

    if plan_button:
        st.switch_page("pages/form.py")

    st.markdown("<br>", unsafe_allow_html=True)
    # st.markdown("---")
    with st.container(horizontal_alignment="center", horizontal=True, width=1000):
        st.markdown(body=WIDGETS, unsafe_allow_html=True)