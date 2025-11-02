"""
CSS and HTML styling elements for the AI Trip Planner app.
This module contains all the styling components to keep the main app files clean.
"""

# Base64 encoded SVG icons for HTML embedding
LOGO_BASE64 = """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSIyNHB4IiBmaWxsPSIjNjY3ZWVhIj48cGF0aCBkPSJNNzg0LTEyMCA1MzAtMzc0bDU2LTU2IDI1NCAyNTQtNTYgNTZabS01NDYtMjhxLTYwLTYwLTg5LTEzNXQtMjktMTUzcTAtNzggMjktMTUydDg5LTEzNHE2MC02MCAxMzQuNS04OS41VDUyNS04NDFxNzggMCAxNTIuNSAyOS41VDgxMi03MjJMMjM4LTE0OFptOC0xMjIgNTQtNTRxLTE2LTIxLTMwLjUtNDNUMjQzLTQxMXEtMTItMjItMjEtNDR0LTE2LTQzcS0xMSA1OS0xLjUgMTE4VDI0Ni0yNzBabTExMi0xMTAgMjIyLTIyNHEtNDMtMzMtODYuNS01My41dC04MS41LTI4cS0zOC03LjUtNjguNS0yLjVUMjk2LTY2NnEtMTcgMTgtMjIgNDguNXQyLjUgNjlxNy41IDM4LjUgMjggODEuNXQ1My41IDg3Wm0yNzgtMjgwIDU2LTU0cS01My0zMi0xMTItNDJ0LTExOCAycTIyIDcgNDQgMTZ0NDQgMjAuNXEyMiAxMS41IDQzLjUgMjZUNjM2LTY2MFoiLz48L3N2Zz4="""

CHAT_ICON_BASE64 = """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSIyNHB4IiBmaWxsPSIjNjY3ZWVhIj48cGF0aCBkPSJNNDgwLTgwcS04MyAwLTE1Ni0zMS41VDE5Ny0xOTdxLTU0LTU0LTg1LjUtMTI3VDgwLTQ4MHEwLTgzIDMxLjUtMTU2VDE5Ny03NjNxNTQtNTQgMTI3LTg1LjVUNDgwLTg4MHExNDYgMCA1NS41IDkxLjVUODcyLTU1OWgtODJxLTE5LTczLTY4LjUtMTMwLjVUNjAwLTc3NnYxNnEwIDMzLTIzLjUgNTYuNVQ1MjAtNjgwaC04MHY4MHEwIDE3LTExLjUgMjguNVQ0MDAtNTYwaC04MHY4MGg4MHYxMjBoLTQwTDE2OC01NTJxLTMgMTgtNS41IDM2dC0yLjUgMzZxMCAxMzEgOTIgMjI1dDIyOCA5NXY4MFptMzY0LTIwTDcxNi0yMjhxLTIxIDEyLTQ1IDIwdC01MSA4cS03NSAwLTEyNy41LTUyLjVUNDQwLTM4MHEwLTc1IDUyLjUtMTI3LjVUNjIwLTU2MHE3NSAwIDEyNy41IDUyLjVUODAwLTM4MHEwIDI3LTggNTF0LTIwIDQ1bDEyOCAxMjgtNTYgNTZaTTYyMC0yODBxNDIgMCA3MS0yOXQyOS03MXEwLTQyLTI5LTcxdC03MS0yOXEtNDIgMC03MSAyOXQtMjkgNzFxMCA0MiAyOSA3MXQ3MSAyOVoiLz48L3N2Zz4="""

PLAN_ICON_BASE64 = """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSIyNHB4IiBmaWxsPSIjNjY3ZWVhIj48cGF0aCBkPSJNMTIwLTEyMHYtODBoNzIwdjgwSDEyMFptNzAtMjAwTDQwLTU3MGw5Ni0yNiAxMTIgOTQgMTQwLTM3LTIwNy0yNzYgMTE2LTMxIDI5OSAyNTEgMTcwLTQ2cTMyLTkgNjAuNSA3LjVUODY0LTU4NXE5IDMyLTcuNSA2MC41VDgwOC00ODdMMTkwLTMyMFoiLz48L3N2Zz4="""

SAVED_ICON_BASE64 = """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSIyNHB4IiBmaWxsPSIjNjY3ZWVhIj48cGF0aCBkPSJNMjQwLTgwcS0zMyAwLTU2LjUtMjMuNVQxNjAtMTYwdi02NDBxMC0zMyAyMy41LTU2LjVUMjQwLTg4MGg0ODBxMzMgMCA1Ni41IDIzLjVUODAwLTgwMHY2NDBxMCAzMy0yMy41IDU2LjVUNzIwLTgwSDI0MFptMC04MGg0ODB2LTY0MGgtODB2MjgwbC0xMDAtNjAtMTAwIDYwdi0yODBIMjQwdjY0MFptMCAwdi02NDAgNjQwWm0yMDAtMzYwIDEwMC02MCAxMDAgNjAtMTAwLTYwLTEwMCA2MFoiLz48L3N2Zz4="""

FORM_ICON_BASE64 = """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSIyNHB4IiBmaWxsPSIjNjY3ZWVhIj48cGF0aCBkPSJNODgwLTgwIDcyMC0yNDBIMzIwcS0zMyAwLTU2LjUtMjMuNVQyNDAtMzIwdi00MGg0NDBxMzMgMCA1Ni41LTIzLjVUNzYwLTQ0MHYtMjgwaDQwcTMzIDAgNTYuNSAyMy41VDg4MC02NDB2NTYwWk0xNjAtNDczbDQ3LTQ3aDM5M3YtMjgwSDE2MHYzMjdaTTgwLTI4MHYtNTIwcTAtMzMgMjMuNS01Ni41VDE2MC04ODBoNDQwcTMzIDAgNTYuNSAyMy41VDY4MC04MDB2MjgwcTAgMzMtMjMuNSA1Ni41VDYwMC00NDBIMjQwTDgwLTI4MFptODAtMjQwdi0yODAgMjgwWiIvPjwvc3ZnPg=="""

CHECK_ICON_BASE64 = """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSIyNHB4IiBmaWxsPSIjNjY3ZWVhIj48cGF0aCBkPSJtNDI0LTI5NiAyODItMjgyLTU2LTU2LTIyNiAyMjYtMTE0LTExNC01NiA1NiAxNzAgMTcwWm01NiAyMTZxLTgzIDAtMTU2LTMxLjVUMTk3LTE5N3EtNTQtNTQtODUuNS0xMjdUODAtNDgwcTAtODMgMzEuNS0xNTZUMTk3LTc2M3E1NC01NCAxMjctODUuNVQ0ODAtODgwcTgzIDAgMTU2IDMxLjVUNzYzLTc2M3E1NCA1NCA4NS41IDEyN1Q4ODAtNDgwcTAgODMtMzEuNSAxNTZUNzYzLTE5N3EtNTQgNTQtMTI3IDg1LjVUNDgwLTgwWm0wLTgwcTEzNCAwIDIyNy05M3Q5My0yMjdxMC0xMzQtOTMtMjI3dC0yMjctOTNxLTEzNCAwLTIyNyA5M3QtOTMgMjI3cTAgMTM0IDkzIDIyN3QyMjcgOTNabTAtMzIwWiIvPjwvc3ZnPg=="""

HEART_ICON_BASE64 = """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSIyNHB4IiBmaWxsPSIjNjY3ZWVhIj48cGF0aCBkPSJNNDgwLTM4OHE1MS00NyA4Mi41LTc3LjVUNjExLTUxOHExNy0yMiAyMy0zOC41dDYtMzUuNXEwLTM2LTI2LTYydC02Mi0yNnEtMjEgMC00MC41IDguNVQ0ODAtNjQ4cS0xMi0xNS0zMS0yMy41dC00MS04LjVxLTM2IDAtNjIgMjZ0LTI2IDYycTAgMTkgNS41IDM1dDIyLjUgMzhxMTcgMjIgNDggNTIuNXQ4NCA3OC41Wk0yMDAtMTIwdi02NDBxMC0zMyAyMy41LTU2LjVUMjgwLTg0MGg0MDBxMzMgMCA1Ni41IDIzLjVUNzYwLTc2MHY2NDBMNDgwLTI0MCAyMDAtMTIwWm04MC0xMjIgMjAwLTg2IDIwMCA4NnYtNTE4SDI4MHY1MThabTAtNTE4aDQwMC00MDBaIi8+PC9zdmc+"""

# HTML version with embedded logo and image carousel
LANDING_PAGE_HTML = f"""
    <style>
        .hero-container {{
            position: relative;
            width: 100vw;
            height: 250px;
            margin-left: calc(-50vw + 50%);
            margin-right: calc(-50vw + 50%);
            overflow: hidden;
            margin-bottom: 3rem;
        }}
        
        .background-carousel {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }}
        
        .carousel-image {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-size: cover;
            background-position: center;
            opacity: 0;
            animation: imageSlide 20s infinite;
        }}
        
        .carousel-image:nth-child(1) {{
            background-image: url('https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1600');
            animation-delay: 0s;
        }}
        
        .carousel-image:nth-child(2) {{
            background-image: url('https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1600');
            animation-delay: 5s;
        }}
        
        .carousel-image:nth-child(3) {{
            background-image: url('https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=1600');
            animation-delay: 10s;
        }}
        
        .carousel-image:nth-child(4) {{
            background-image: url('https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1600');
            animation-delay: 15s;
        }}
        
        @keyframes imageSlide {{
            0% {{ opacity: 0; }}
            5% {{ opacity: 1; }}
            25% {{ opacity: 1; }}
            30% {{ opacity: 0; }}
            100% {{ opacity: 0; }}
        }}
        
        .hero-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(0, 0, 0, 0.35) 0%, rgba(0, 0, 0, 0.25) 100%);
            z-index: 1;
        }}
        
        .hero-content {{
            position: relative;
            z-index: 2;
            text-align: center;
            color: white;
            padding: 4rem 2rem;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }}
        
        .hero-title {{
            font-size: 4rem;
            margin-bottom: 1.5rem;
            font-weight: 700;
            text-shadow: 2px 4px 8px rgba(0, 0, 0, 0.5);
            letter-spacing: 1px;
        }}
        
        .hero-subtitle {{
            font-size: 1.5rem;
            font-weight: 400;
            text-shadow: 1px 2px 4px rgba(0, 0, 0, 0.5);
            max-width: 700px;
            line-height: 1.6;
        }}
        
        .hero-logo {{
            width: 4rem;
            height: 4rem;
            vertical-align: middle;
            margin-right: 1rem;
            filter: brightness(0) invert(1) drop-shadow(2px 4px 8px rgba(0, 0, 0, 0.5));
        }}
        
        @media (max-width: 768px) {{
            .hero-title {{
                font-size: 2.5rem;
            }}
            .hero-subtitle {{
                font-size: 1.1rem;
            }}
            .hero-logo {{
                width: 3rem;
                height: 3rem;
            }}
            .hero-container {{
                height: 400px;
            }}
        }}
    </style>
    
    <div class="hero-container">
        <div class="background-carousel">
            <div class="carousel-image"></div>
            <div class="carousel-image"></div>
            <div class="carousel-image"></div>
            <div class="carousel-image"></div>
        </div>
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <h1 class="hero-title">
                <img src="{LOGO_BASE64}" class="hero-logo"/>
                Trip Sense
            </h1>
            <p class="hero-subtitle">
                Plan your perfect adventure with AI-powered recommendations
            </p>
        </div>
    </div>
    
    <div style="text-align: center; max-width: 900px; margin: 0 auto 3rem auto; padding: 0 2rem;">
        <p style="font-size: 1rem; line-height: 1.8; color: #666;">
            From budget-friendly getaways to luxury escapes, our AI assistant helps you discover amazing destinations, 
            create detailed itineraries, and find the best places to visit based on your preferences.
        </p>
    </div>
"""

WIDGETS = f"""
<div style="display: flex; justify-content: center; gap: 1rem;">
    <div style="text-align: center;border: 1px solid #d3d2ca; border-radius: 1.5rem; padding: 2rem 1rem; margin: 1rem 1rem;">
        <h4>
        <img src="{HEART_ICON_BASE64}" style="width: 1.5rem; height: 1.5rem; vertical-align: middle; margin-right: 0.5rem;"/> Personalized</h4>
        <p>Tailored recommendations based on your travel style, budget, and interests</p>
    </div>
    <div style="text-align: center;border: 1px solid #d3d2ca; border-radius: 1.5rem; padding: 2rem 1rem; margin: 1rem 1rem;">
        <h4>
        <img src="{CHECK_ICON_BASE64}" style="width: 1.5rem; height: 1.5rem; vertical-align: middle; margin-right: 0.5rem;"/> Smart Planning</h4>
        <p>AI-powered itineraries with real-time maps, directions, and local insights</p>
    </div>
    <div style="text-align: center;border: 1px solid #d3d2ca; border-radius: 1.5rem; padding: 2rem 1rem; margin: 1rem 1rem;">
        <h4>
        <img src="{FORM_ICON_BASE64}" style="width: 1.5rem; height: 1.5rem; vertical-align: middle; margin-right: 0.5rem;"/> Interactive</h4>
        <p>Chat with our AI assistant to refine your plans and get instant answers</p>
    </div>
</div>
"""

# Form Page Styles
FORM_PAGE_HTML = f"""
    <div style="text-align: center; padding: 3rem 0;">
        <h1>
        <img src="{PLAN_ICON_BASE64}" style="width: 3.5rem; height: 3.5rem; vertical-align: middle; margin-right: 0.5rem;"/> Tell Us About Your Dream Trip</h1>
        <br>
        <p style="color: #666; font-size: 1.1rem;">Fill in the details below to get personalized recommendations</p>
    </div>
"""

CHATBOT_HEADER = f"""
    <div style="text-align: center; padding: 3rem 0;">
        <h1>
        <img src="{CHAT_ICON_BASE64}" style="width: 3.5rem; height: 3.5rem; vertical-align: middle; margin-right: 0.5rem;"/>
        Your AI Trip Assistant
        </h1>
    </div>
"""
    
TRIPS_HEADER = f"""
    <div style="text-align: center; padding: 3rem 0;">
        <h1>
        <img src="{SAVED_ICON_BASE64}" style="width: 3.5rem; height: 3.5rem; vertical-align: middle; margin-right: 0.5rem;"/> Saved Trips</h1>
        <br>
    </div>
"""