import streamlit as st
from styles.styles import (
    LANDING_PAGE_HTML, 
    PERSONALISED_WIDGET, 
    PLANNING_WIDGET, 
    INTERACTIVE_WIDGET,
    MATERIAL_ICONS_CSS
)

# Set page config
st.set_page_config(page_title="Trip Sense", page_icon=":material/beach_access:", layout="wide")

# Load Material Icons CSS
st.markdown(MATERIAL_ICONS_CSS, unsafe_allow_html=True)

# Main landing page content
with st.container(horizontal_alignment="center"):
    st.markdown(body=LANDING_PAGE_HTML, unsafe_allow_html=True)

    plan_button = st.button("Start Planning Your Trip", type="primary", key="start_planning", help="Click to begin your travel planning journey")

    if plan_button:
        st.switch_page("pages/form.py")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    with st.container(horizontal_alignment="center", horizontal=True):
        st.markdown(body=PERSONALISED_WIDGET, unsafe_allow_html=True, width="content")

        st.markdown(body=PLANNING_WIDGET, unsafe_allow_html=True, width="content")

        st.markdown(body=INTERACTIVE_WIDGET, unsafe_allow_html=True, width="content")