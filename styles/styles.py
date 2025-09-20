"""
CSS and HTML styling elements for the AI Trip Planner app.
This module contains all the styling components to keep the main app files clean.
"""

# Base64 encoded SVG icons for HTML embedding
LOGO_BASE64 = """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSIyNHB4IiBmaWxsPSIjY2I3ODVjIj48cGF0aCBkPSJNNzg0LTEyMCA1MzAtMzc0bDU2LTU2IDI1NCAyNTQtNTYgNTZabS01NDYtMjhxLTYwLTYwLTg5LTEzNXQtMjktMTUzcTAtNzggMjktMTUydDg5LTEzNHE2MC02MCAxMzQuNS04OS41VDUyNS04NDFxNzggMCAxNTIuNSAyOS41VDgxMi03MjJMMjM4LTE0OFptOC0xMjIgNTQtNTRxLTE2LTIxLTMwLjUtNDNUMjQzLTQxMXEtMTItMjItMjEtNDR0LTE2LTQzcS0xMSA1OS0xLjUgMTE4VDI0Ni0yNzBabTExMi0xMTAgMjIyLTIyNHEtNDMtMzMtODYuNS01My41dC04MS41LTI4cS0zOC03LjUtNjguNS0yLjVUMjk2LTY2NnEtMTcgMTgtMjIgNDguNXQyLjUgNjlxNy41IDM4LjUgMjggODEuNXQ1My41IDg3Wm0yNzgtMjgwIDU2LTU0cS01My0zMi0xMTItNDJ0LTExOCAycTIyIDcgNDQgMTZ0NDQgMjAuNXEyMiAxMS41IDQzLjUgMjZUNjM2LTY2MFoiLz48L3N2Zz4="""

CHAT_ICON_BASE64 = """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSIyNHB4IiBmaWxsPSIjY2I3ODVjIj48cGF0aCBkPSJNNDgwLTgwcS04MyAwLTE1Ni0zMS41VDE5Ny0xOTdxLTU0LTU0LTg1LjUtMTI3VDgwLTQ4MHEwLTgzIDMxLjUtMTU2VDE5Ny03NjNxNTQtNTQgMTI3LTg1LjVUNDgwLTg4MHExNDYgMCAyNTUuNSA5MS41VDg3Mi01NTloLTgycS0xOS03My02OC41LTEzMC41VDYwMC03NzZ2MTZxMCAzMy0yMy41IDU2LjVUNTIwLTY4MGgtODB2ODBxMCAxNy0xMS41IDI4LjVUNDAwLTU2MGgtODB2ODBoODB2MTIwaC00MEwxNjgtNTUycS0zIDE4LTUuNSAzNnQtMi41IDM2cTAgMTMxIDkyIDIyNXQyMjggOTV2ODBabTM2NC0yMEw3MTYtMjI4cS0yMSAxMi00NSAyMHQtNTEgOHEtNzUgMC0xMjcuNS01Mi41VDQ0MC0zODBxMC03NSA1Mi41LTEyNy41VDYyMC01NjBxNzUgMCAxMjcuNSA1Mi41VDgwMC0zODBxMCAyNy04IDUxdC0yMCA0NWwxMjggMTI4LTU2IDU2Wk02MjAtMjgwcTQyIDAgNzEtMjl0MjktNzFxMC00Mi0yOS03MXQtNzEtMjlxLTQyIDAtNzEgMjl0LTI5IDcxcTAgNDIgMjkgNzF0NzEgMjlaIi8+PC9zdmc+"""

PLAN_ICON_BASE64 = """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSIyNHB4IiBmaWxsPSIjY2I3ODVjIj48cGF0aCBkPSJNMTIwLTEyMHYtODBoNzIwdjgwSDEyMFptNzAtMjAwTDQwLTU3MGw5Ni0yNiAxMTIgOTQgMTQwLTM3LTIwNy0yNzYgMTE2LTMxIDI5OSAyNTEgMTcwLTQ2cTMyLTkgNjAuNSA3LjVUODY0LTU4NXE5IDMyLTcuNSA2MC41VDgwOC00ODdMMTkwLTMyMFoiLz48L3N2Zz4="""

SAVED_ICON_BASE64 = """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSIyNHB4IiBmaWxsPSIjY2I3ODVjIj48cGF0aCBkPSJNMjQwLTgwcS0zMyAwLTU2LjUtMjMuNVQxNjAtMTYwdi02NDBxMC0zMyAyMy41LTU2LjVUMjQwLTg4MGg0ODBxMzMgMCA1Ni41IDIzLjVUODAwLTgwMHY2NDBxMCAzMy0yMy41IDU2LjVUNzIwLTgwSDI0MFptMC04MGg0ODB2LTY0MGgtODB2MjgwbC0xMDAtNjAtMTAwIDYwdi0yODBIMjQwdjY0MFptMCAwdi02NDAgNjQwWm0yMDAtMzYwIDEwMC02MCAxMDAgNjAtMTAwLTYwLTEwMCA2MFoiLz48L3N2Zz4="""

FORM_ICON_BASE64 = """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSIyNHB4IiBmaWxsPSIjY2I3ODVjIj48cGF0aCBkPSJNODgwLTgwIDcyMC0yNDBIMzIwcS0zMyAwLTU2LjUtMjMuNVQyNDAtMzIwdi00MGg0NDBxMzMgMCA1Ni41LTIzLjVUNzYwLTQ0MHYtMjgwaDQwcTMzIDAgNTYuNSAyMy41VDg4MC02NDB2NTYwWk0xNjAtNDczbDQ3LTQ3aDM5M3YtMjgwSDE2MHYzMjdaTTgwLTI4MHYtNTIwcTAtMzMgMjMuNS01Ni41VDE2MC04ODBoNDQwcTMzIDAgNTYuNSAyMy41VDY4MC04MDB2MjgwcTAgMzMtMjMuNSA1Ni41VDYwMC00NDBIMjQwTDgwLTI4MFptODAtMjQwdi0yODAgMjgwWiIvPjwvc3ZnPg=="""

CHECK_ICON_BASE64 = """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSIyNHB4IiBmaWxsPSIjY2I3ODVjIj48cGF0aCBkPSJtNDI0LTI5NiAyODItMjgyLTU2LTU2LTIyNiAyMjYtMTE0LTExNC01NiA1NiAxNzAgMTcwWm01NiAyMTZxLTgzIDAtMTU2LTMxLjVUMTk3LTE5N3EtNTQtNTQtODUuNS0xMjdUODAtNDgwcTAtODMgMzEuNS0xNTZUMTk3LTc2M3E1NC01NCAxMjctODUuNVQ0ODAtODgwcTgzIDAgMTU2IDMxLjVUNzYzLTc2M3E1NCA1NCA4NS41IDEyN1Q4ODAtNDgwcTAgODMtMzEuNSAxNTZUNzYzLTE5N3EtNTQgNTQtMTI3IDg1LjVUNDgwLTgwWm0wLTgwcTEzNCAwIDIyNy05M3Q5My0yMjdxMC0xMzQtOTMtMjI3dC0yMjctOTNxLTEzNCAwLTIyNyA5M3QtOTMgMjI3cTAgMTM0IDkzIDIyN3QyMjcgOTNabTAtMzIwWiIvPjwvc3ZnPg=="""

HEART_ICON_BASE64 = """data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iMjRweCIgdmlld0JveD0iMCAtOTYwIDk2MCA5NjAiIHdpZHRoPSIyNHB4IiBmaWxsPSIjY2I3ODVjIj48cGF0aCBkPSJNNDgwLTM4OHE1MS00NyA4Mi41LTc3LjVUNjExLTUxOHExNy0yMiAyMy0zOC41dDYtMzUuNXEwLTM2LTI2LTYydC02Mi0yNnEtMjEgMC00MC41IDguNVQ0ODAtNjQ4cS0xMi0xNS0zMS0yMy41dC00MS04LjVxLTM2IDAtNjIgMjZ0LTI2IDYycTAgMTkgNS41IDM1dDIyLjUgMzhxMTcgMjIgNDggNTIuNXQ4NCA3OC41Wk0yMDAtMTIwdi02NDBxMC0zMyAyMy41LTU2LjVUMjgwLTg0MGg0MDBxMzMgMCA1Ni41IDIzLjVUNzYwLTc2MHY2NDBMNDgwLTI0MCAyMDAtMTIwWm04MC0xMjIgMjAwLTg2IDIwMCA4NnYtNTE4SDI4MHY1MThabTAtNTE4aDQwMC00MDBaIi8+PC9zdmc+"""

# HTML version with embedded logo
LANDING_PAGE_HTML = f"""
    <div style="text-align: center; padding: 3rem 0;">
        <h1 style="font-size: 3.5rem; margin-bottom: 1rem;">
        <img src="{LOGO_BASE64}" style="width: 3.5rem; height: 3.5rem; vertical-align: middle; margin-right: 0.5rem;"/> Trip Sense
        </h1>
        <br>
        <h3 style="margin-bottom: 2rem; font-weight: 300;">
            Plan your perfect adventure with AI-powered recommendations
        </h3>
        <br>
        <p style="font-size: 1.2rem; max-width: 600px; margin: 0 auto 2rem auto; line-height: 1.6;">
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