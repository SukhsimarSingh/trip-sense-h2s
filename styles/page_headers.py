"""
Page header components for different sections of the Trip Sense app.
"""

from styles.icons import PLAN_ICON_BASE64, CHAT_ICON_BASE64, SAVED_ICON_BASE64, PAID_ICON_BASE64

# Form Page Header
FORM_PAGE_HTML = f"""
    <div style="text-align: center; padding: 3rem 0;">
        <h1>
        <img src="{PLAN_ICON_BASE64}" style="width: 3.5rem; height: 3.5rem; vertical-align: middle; margin-right: 0.5rem;"/> Tell Us About Your Dream Trip</h1>
        <br>
        <p style="color: #666; font-size: 1.1rem;">Fill in the details below to get personalized recommendations</p>
    </div>
"""

# Chatbot Page Header
CHATBOT_HEADER = f"""
    <div style="text-align: center; padding: 3rem 0;">
        <h1>
        <img src="{CHAT_ICON_BASE64}" style="width: 3.5rem; height: 3.5rem; vertical-align: middle; margin-right: 0.5rem;"/>
        Your AI Trip Assistant
        </h1>
    </div>
"""

# Trips Page Header
TRIPS_HEADER = f"""
    <div style="text-align: center; padding: 3rem 0;">
        <h1>
        <img src="{SAVED_ICON_BASE64}" style="width: 3.5rem; height: 3.5rem; vertical-align: middle; margin-right: 0.5rem;"/> Saved Trips</h1>
        <br>
    </div>
"""

# Book Page Header
BOOK_HEADER = f"""
    <div style="text-align: center; padding: 3rem 0;">
        <h1>
        <img src="{PAID_ICON_BASE64}" style="width: 3.5rem; height: 3.5rem; vertical-align: middle; margin-right: 0.5rem;"/> Book Your Trip</h1>
        <br>
        <p style="color: #666; font-size: 1.1rem;">Turn your dream trip into reality with our booking guide</p>
    </div>
"""