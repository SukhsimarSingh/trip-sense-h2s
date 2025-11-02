"""
Landing page HTML and CSS components for Trip Sense.
Includes hero carousel, description, and feature cards.
"""

from styles.icons import LOGO_BASE64, HEART_ICON_BASE64, CHECK_ICON_BASE64, FORM_ICON_BASE64


def get_hero_section():
    """Returns the hero section with auto-changing background carousel."""
    return f"""
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


def get_feature_cards():
    """Returns the feature cards section with mobile-responsive layout."""
    return f"""
<style>
    .features-container {{
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        flex-wrap: wrap;
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 1rem;
    }}
    
    .feature-card {{
        text-align: center;
        border: 2px solid #e2e8f0;
        border-radius: 1.5rem;
        padding: 2rem 1.5rem;
        flex: 1;
        min-width: 250px;
        max-width: 350px;
        transition: all 0.3s ease;
        background: white;
    }}
    
    .feature-card:hover {{
        border-color: #667eea;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.15);
        transform: translateY(-5px);
    }}
    
    .feature-card h4 {{
        font-size: 1.3rem;
        margin-bottom: 0.8rem;
        color: #333;
        font-weight: 600;
    }}
    
    .feature-card p {{
        color: #666;
        line-height: 1.6;
        font-size: 0.95rem;
        margin: 0;
    }}
    
    .feature-icon {{
        width: 1.5rem;
        height: 1.5rem;
        vertical-align: middle;
        margin-right: 0.5rem;
    }}
    
    /* Mobile responsive styles */
    @media (max-width: 768px) {{
        .features-container {{
            flex-direction: column;
            gap: 1rem;
            padding: 0 1rem;
        }}
        
        .feature-card {{
            min-width: 100%;
            max-width: 100%;
            padding: 1.5rem 1rem;
        }}
        
        .feature-card h4 {{
            font-size: 1.1rem;
        }}
        
        .feature-card p {{
            font-size: 0.9rem;
        }}
    }}
</style>

<div class="features-container">
    <div class="feature-card">
        <h4>
            <img src="{HEART_ICON_BASE64}" class="feature-icon"/> Personalized
        </h4>
        <p>Tailored recommendations based on your travel style, budget, and interests</p>
    </div>
    <div class="feature-card">
        <h4>
            <img src="{CHECK_ICON_BASE64}" class="feature-icon"/> Smart Planning
        </h4>
        <p>AI-powered itineraries with real-time maps, directions, and local insights</p>
    </div>
    <div class="feature-card">
        <h4>
            <img src="{FORM_ICON_BASE64}" class="feature-icon"/> Interactive
        </h4>
        <p>Chat with our AI assistant to refine your plans and get instant answers</p>
    </div>
</div>
"""


# Compose the full landing page HTML
LANDING_PAGE_HTML = get_hero_section()
WIDGETS = get_feature_cards()

