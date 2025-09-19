"""
CSS and HTML styling elements for the AI Trip Planner app.
This module contains all the styling components to keep the main app files clean.
"""

# Landing Page Styles
LANDING_PAGE_HTML = """
    <div style="text-align: center; padding: 3rem 0;">
        <h1 style="font-size: 3.5rem; margin-bottom: 1rem; background: linear-gradient(45deg, #FF6B6B, #4ECDC4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🧭 AI Trip Planner
        </h1>
        <br>
        <h3 style="color: #666; margin-bottom: 2rem; font-weight: 300;">
            Plan your perfect adventure with AI-powered recommendations
        </h3>
        <br>
        <p style="font-size: 1.2rem; color: #888; max-width: 600px; margin: 0 auto 3rem auto; line-height: 1.6;">
            From budget-friendly getaways to luxury escapes, our AI assistant helps you discover amazing destinations, 
            create detailed itineraries, and find the best places to visit based on your preferences.
        </p>
    </div>
"""

PERSONALISED_WIDGET = """
    <div style="color: #666; text-align: center; padding: 2rem 1rem; border-radius: 20px; margin: 2rem 1rem;">
        <h4>🎯 Personalized</h4>
        <p>Tailored recommendations based on your travel style, budget, and interests</p>
    </div>
"""

PLANNING_WIDGET = """
    <div style="color: #666; text-align: center; padding: 2rem 1rem; border-radius: 20px; margin: 2rem 1rem;">
        <h4>🗺️ Smart Planning</h4>
        <p>AI-powered itineraries with real-time maps, directions, and local insights</p>
    </div>
"""

INTERACTIVE_WIDGET = """
    <div style="color: #666; text-align: center; padding: 2rem 1rem; border-radius: 20px; margin: 2rem 1rem;">
        <h4>💬 Interactive</h4>
        <p>Chat with our AI assistant to refine your plans and get instant answers</p>
    </div>
"""

# Form Page Styles
FORM_PAGE_HTML = """
    <div style="text-align: center; padding: 3rem 0;">
        <h1 style="color: #666;">✈️ Tell Us About Your Dream Trip</h1>
        <br>
        <p style="color: #666; font-size: 1.1rem;">Fill in the details below to get personalized recommendations</p>
    </div>
"""

# Section Headers
BASIC_INFO_HEADER = """<h5 style="color: #666;"> Basic Info</h5>"""
ADDITIONAL_PREFERENCES_HEADER = """<h5 style="color: #666;">Additional Preferences (Optional)</h5>"""

# Common CSS Classes (if needed for future use)
CSS_STYLES = """
<style>
    .gradient-text {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .feature-widget {
        color: #666;
        text-align: center;
        padding: 2rem 1rem;
        border-radius: 20px;
        margin: 2rem 1rem;
    }
    
    .section-header {
        color: #666;
    }
    
    .form-container {
        text-align: center;
        padding: 3rem 0;
    }
    
    .subtitle {
        color: #666;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    .description {
        font-size: 1.2rem;
        color: #888;
        max-width: 600px;
        margin: 0 auto 3rem auto;
        line-height: 1.6;
    }
</style>
"""
