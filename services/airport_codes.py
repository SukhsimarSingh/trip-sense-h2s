"""
Airport code mapping and lookup service.
Helps convert city names to airport codes for SerpAPI.
"""

# Common city to airport code mappings
CITY_TO_AIRPORT = {
    # India
    "chennai": "MAA",
    "mumbai": "BOM",
    "delhi": "DEL",
    "bangalore": "BLR",
    "kolkata": "CCU",
    "hyderabad": "HYD",
    "ahmedabad": "AMD",
    "pune": "PNQ",
    "goa": "GOI",
    "jaipur": "JAI",
    "kochi": "COK",
    "thiruvananthapuram": "TRV",
    "lucknow": "LKO",
    "chandigarh": "IXC",
    "coimbatore": "CJB",
    "guwahati": "GAU",
    
    # USA
    "new york": "JFK",
    "los angeles": "LAX",
    "chicago": "ORD",
    "houston": "IAH",
    "phoenix": "PHX",
    "philadelphia": "PHL",
    "san antonio": "SAT",
    "san diego": "SAN",
    "dallas": "DFW",
    "san jose": "SJC",
    "austin": "AUS",
    "jacksonville": "JAX",
    "fort worth": "DFW",
    "columbus": "CMH",
    "charlotte": "CLT",
    "san francisco": "SFO",
    "indianapolis": "IND",
    "seattle": "SEA",
    "denver": "DEN",
    "washington": "IAD",
    "boston": "BOS",
    "nashville": "BNA",
    "detroit": "DTW",
    "las vegas": "LAS",
    "portland": "PDX",
    "memphis": "MEM",
    "miami": "MIA",
    "atlanta": "ATL",
    "orlando": "MCO",
    
    # Europe
    "london": "LHR",
    "paris": "CDG",
    "berlin": "BER",
    "madrid": "MAD",
    "rome": "FCO",
    "amsterdam": "AMS",
    "barcelona": "BCN",
    "munich": "MUC",
    "milan": "MXP",
    "vienna": "VIE",
    "zurich": "ZRH",
    "brussels": "BRU",
    "dublin": "DUB",
    "copenhagen": "CPH",
    "stockholm": "ARN",
    "oslo": "OSL",
    "helsinki": "HEL",
    "prague": "PRG",
    "warsaw": "WAW",
    "budapest": "BUD",
    "athens": "ATH",
    "istanbul": "IST",
    "lisbon": "LIS",
    "manchester": "MAN",
    "edinburgh": "EDI",
    "geneva": "GVA",
    "frankfurt": "FRA",
    "nice": "NCE",
    
    # Asia
    "tokyo": "NRT",
    "beijing": "PEK",
    "shanghai": "PVG",
    "hong kong": "HKG",
    "singapore": "SIN",
    "dubai": "DXB",
    "bangkok": "BKK",
    "kuala lumpur": "KUL",
    "seoul": "ICN",
    "taipei": "TPE",
    "manila": "MNL",
    "jakarta": "CGK",
    "hanoi": "HAN",
    "ho chi minh": "SGN",
    "osaka": "KIX",
    "nagoya": "NGO",
    "fukuoka": "FUK",
    "sapporo": "CTS",
    "chengdu": "CTU",
    "guangzhou": "CAN",
    "shenzhen": "SZX",
    "doha": "DOH",
    "abu dhabi": "AUH",
    "riyadh": "RUH",
    "jeddah": "JED",
    "tehran": "IKA",
    "karachi": "KHI",
    "lahore": "LHE",
    "islamabad": "ISB",
    "dhaka": "DAC",
    "kathmandu": "KTM",
    "colombo": "CMB",
    
    # Australia & Oceania
    "sydney": "SYD",
    "melbourne": "MEL",
    "brisbane": "BNE",
    "perth": "PER",
    "adelaide": "ADL",
    "auckland": "AKL",
    "wellington": "WLG",
    "christchurch": "CHC",
    
    # Middle East & Africa
    "cairo": "CAI",
    "johannesburg": "JNB",
    "cape town": "CPT",
    "nairobi": "NBO",
    "lagos": "LOS",
    "casablanca": "CMN",
    "addis ababa": "ADD",
    "tel aviv": "TLV",
    "amman": "AMM",
    "beirut": "BEY",
    
    # South America
    "sao paulo": "GRU",
    "rio de janeiro": "GIG",
    "buenos aires": "EZE",
    "lima": "LIM",
    "bogota": "BOG",
    "santiago": "SCL",
    "caracas": "CCS",
    "quito": "UIO",
    
    # Canada
    "toronto": "YYZ",
    "vancouver": "YVR",
    "montreal": "YUL",
    "calgary": "YYC",
    "ottawa": "YOW",
    "edmonton": "YEG",
    
    # Country names to major airport
    "france": "CDG",  # Paris
    "germany": "FRA",  # Frankfurt
    "italy": "FCO",  # Rome
    "spain": "MAD",  # Madrid
    "uk": "LHR",  # London
    "united kingdom": "LHR",
    "netherlands": "AMS",  # Amsterdam
    "switzerland": "ZRH",  # Zurich
    "austria": "VIE",  # Vienna
    "belgium": "BRU",  # Brussels
    "portugal": "LIS",  # Lisbon
    "greece": "ATH",  # Athens
    "turkey": "IST",  # Istanbul
    "russia": "SVO",  # Moscow
    "poland": "WAW",  # Warsaw
    "czech republic": "PRG",  # Prague
    "hungary": "BUD",  # Budapest
    "denmark": "CPH",  # Copenhagen
    "sweden": "ARN",  # Stockholm
    "norway": "OSL",  # Oslo
    "finland": "HEL",  # Helsinki
    "ireland": "DUB",  # Dublin
    "scotland": "EDI",  # Edinburgh
    "wales": "CWL",  # Cardiff
    "japan": "NRT",  # Tokyo
    "china": "PEK",  # Beijing
    "south korea": "ICN",  # Seoul
    "thailand": "BKK",  # Bangkok
    "malaysia": "KUL",  # Kuala Lumpur
    "indonesia": "CGK",  # Jakarta
    "vietnam": "SGN",  # Ho Chi Minh
    "philippines": "MNL",  # Manila
    "cambodia": "PNH",  # Phnom Penh
    "myanmar": "RGN",  # Yangon
    "bangladesh": "DAC",  # Dhaka
    "sri lanka": "CMB",  # Colombo
    "nepal": "KTM",  # Kathmandu
    "pakistan": "KHI",  # Karachi
    "uae": "DXB",  # Dubai
    "saudi arabia": "RUH",  # Riyadh
    "qatar": "DOH",  # Doha
    "kuwait": "KWI",  # Kuwait City
    "oman": "MCT",  # Muscat
    "bahrain": "BAH",  # Manama
    "egypt": "CAI",  # Cairo
    "south africa": "JNB",  # Johannesburg
    "kenya": "NBO",  # Nairobi
    "nigeria": "LOS",  # Lagos
    "morocco": "CMN",  # Casablanca
    "australia": "SYD",  # Sydney
    "new zealand": "AKL",  # Auckland
    "brazil": "GRU",  # Sao Paulo
    "argentina": "EZE",  # Buenos Aires
    "chile": "SCL",  # Santiago
    "peru": "LIM",  # Lima
    "colombia": "BOG",  # Bogota
    "mexico": "MEX",  # Mexico City
    "canada": "YYZ",  # Toronto
    "usa": "JFK",  # New York
    "united states": "JFK",
    "india": "DEL",  # Delhi
}

def get_airport_code(location: str) -> tuple[str, str]:
    """
    Convert location name to airport code.
    
    Args:
        location: City, country, or airport code
        
    Returns:
        Tuple of (airport_code, location_name)
        If already an airport code, returns (code, original_name)
        If found in mapping, returns (code, city_name)
        If not found, returns (original, warning_message)
    """
    if not location:
        return ("", "Invalid location")
    
    location_clean = location.strip()
    location_lower = location_clean.lower()
    
    # Check if it's already an airport code (3 uppercase letters)
    if len(location_clean) == 3 and location_clean.isupper() and location_clean.isalpha():
        return (location_clean, location_clean)
    
    # Try to find in mapping
    if location_lower in CITY_TO_AIRPORT:
        airport_code = CITY_TO_AIRPORT[location_lower]
        return (airport_code, location_clean)
    
    # Try partial matches for compound city names
    for city, code in CITY_TO_AIRPORT.items():
        if city in location_lower or location_lower in city:
            return (code, city.title())
    
    # Not found - return original with warning
    return (location_clean.upper(), f"⚠️ Could not find airport for '{location_clean}'")

def format_location_display(original: str, airport_code: str, city_name: str = None) -> str:
    """
    Format location for display.
    
    Args:
        original: Original input
        airport_code: Resolved airport code
        city_name: Resolved city name (optional)
        
    Returns:
        Formatted string for display
    """
    if city_name and city_name != airport_code:
        return f"{city_name} ({airport_code})"
    return airport_code

def get_popular_airports() -> dict[str, list[tuple[str, str]]]:
    """
    Get popular airports by region.
    
    Returns:
        Dict of region -> list of (city, code) tuples
    """
    return {
        "India": [
            ("Delhi", "DEL"),
            ("Mumbai", "BOM"),
            ("Bangalore", "BLR"),
            ("Chennai", "MAA"),
            ("Kolkata", "CCU"),
            ("Hyderabad", "HYD"),
            ("Goa", "GOI"),
        ],
        "USA": [
            ("New York", "JFK"),
            ("Los Angeles", "LAX"),
            ("Chicago", "ORD"),
            ("San Francisco", "SFO"),
            ("Miami", "MIA"),
            ("Boston", "BOS"),
            ("Las Vegas", "LAS"),
        ],
        "Europe": [
            ("London", "LHR"),
            ("Paris", "CDG"),
            ("Amsterdam", "AMS"),
            ("Frankfurt", "FRA"),
            ("Madrid", "MAD"),
            ("Rome", "FCO"),
            ("Barcelona", "BCN"),
        ],
        "Asia": [
            ("Dubai", "DXB"),
            ("Singapore", "SIN"),
            ("Tokyo", "NRT"),
            ("Bangkok", "BKK"),
            ("Hong Kong", "HKG"),
            ("Seoul", "ICN"),
            ("Kuala Lumpur", "KUL"),
        ]
    }

