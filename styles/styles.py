"""
CSS and HTML styling elements for the AI Trip Planner app.
This module re-exports all styling components from organized submodules.
"""

# Import all components from submodules
from styles.icons import (
    LOGO_BASE64,
    CHAT_ICON_BASE64,
    PLAN_ICON_BASE64,
    SAVED_ICON_BASE64,
    FORM_ICON_BASE64,
    CHECK_ICON_BASE64,
    HEART_ICON_BASE64,
    PAID_ICON_BASE64
)

from styles.landing import (
    LANDING_PAGE_HTML,
    WIDGETS
)

from styles.page_headers import (
    FORM_PAGE_HTML,
    CHATBOT_HEADER,
    TRIPS_HEADER,
    BOOK_HEADER
)

# Re-export everything for backward compatibility
__all__ = [
    # Icons
    'LOGO_BASE64',
    'CHAT_ICON_BASE64',
    'PLAN_ICON_BASE64',
    'SAVED_ICON_BASE64',
    'FORM_ICON_BASE64',
    'CHECK_ICON_BASE64',
    'HEART_ICON_BASE64',
    # Landing page components
    'LANDING_PAGE_HTML',
    'WIDGETS',
    # Page headers
    'FORM_PAGE_HTML',
    'CHATBOT_HEADER',
    'TRIPS_HEADER',
    'BOOK_HEADER'
]