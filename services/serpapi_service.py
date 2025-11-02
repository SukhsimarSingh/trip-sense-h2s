"""
SerpAPI Service for real-time flight, hotel, and event search.
Official Documentation:
- Flights: https://serpapi.com/google-flights-api
- Hotels: https://serpapi.com/google-hotels-api
- Events: https://serpapi.com/google-events-api

Requires SERPAPI_API_KEY in .env file.
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import streamlit as st

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import airport code helper
from services.airport_codes import get_airport_code, format_location_display

def get_serpapi_key() -> Optional[str]:
    """Get SerpAPI key from environment."""
    api_key = os.getenv('SERPAPI_API_KEY')
    if api_key:
        # Show partial key for debugging (first 8 and last 4 characters)
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
        print(f"✅ [SERPAPI] API Key loaded: {masked_key}")
    else:
        print("⚠️ [SERPAPI] API Key not found in environment variables")
    return api_key

def search_flights(origin: str, destination: str, departure_date: str, return_date: str = None, adults: int = 1, children: int = 0) -> Dict[str, Any]:
    """
    Search for flights using SerpAPI Google Flights API.
    Documentation: https://serpapi.com/google-flights-api
    
    Args:
        origin: Origin airport code (e.g., "LAX")
        destination: Destination airport code (e.g., "JFK")
        departure_date: Departure date in YYYY-MM-DD format
        return_date: Optional return date for round trips in YYYY-MM-DD format
        adults: Number of adult passengers (default: 1)
        children: Number of children (default: 0)
        
    Returns:
        Dict containing flight results
    """
    try:
        from serpapi import GoogleSearch
        
        api_key = get_serpapi_key()
        if not api_key:
            return {
                'error': 'SerpAPI key not configured',
                'message': 'Please add SERPAPI_API_KEY to your .env file',
                'demo_mode': True
            }
        
        # Convert city names to airport codes
        origin_code, origin_name = get_airport_code(origin)
        dest_code, dest_name = get_airport_code(destination)
        
        # Check for warnings in conversion
        if "⚠️" in origin_name:
            print(f"⚠️ [SERPAPI] {origin_name}")
            return {
                'error': 'Invalid origin airport',
                'message': f'{origin_name}. Please use airport code (e.g., MAA for Chennai) or city name.',
                'demo_mode': True,
                'suggestion': 'Try using 3-letter airport codes like: MAA (Chennai), DEL (Delhi), BOM (Mumbai), CDG (Paris)'
            }
        
        if "⚠️" in dest_name:
            print(f"⚠️ [SERPAPI] {dest_name}")
            return {
                'error': 'Invalid destination airport',
                'message': f'{dest_name}. Please use airport code (e.g., CDG for Paris) or city name.',
                'demo_mode': True,
                'suggestion': 'Try using 3-letter airport codes like: CDG (Paris), LHR (London), JFK (New York)'
            }
        
        # Build search parameters according to official SerpAPI documentation
        params = {
            "engine": "google_flights",
            "departure_id": origin_code,
            "arrival_id": dest_code,
            "outbound_date": departure_date,
            "currency": "USD",
            "hl": "en",
            "gl": "us",
            "api_key": api_key
        }
        
        # Add passengers
        if adults > 0:
            params["adults"] = str(adults)
        if children > 0:
            params["children"] = str(children)
        
        # Add return date if provided (Round trip)
        if return_date:
            params["return_date"] = return_date
            params["type"] = "1"  # Round trip
        else:
            params["type"] = "2"  # One way
        
        print(f"🔍 [SERPAPI] Searching flights: {origin} ({origin_code}) → {destination} ({dest_code}) on {departure_date}")
        if return_date:
            print(f"   Return: {return_date}")
        print(f"   Passengers: {adults} adult(s)" + (f", {children} child(ren)" if children > 0 else ""))
        print(f"   Using airport codes: {origin_code} → {dest_code}")
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Check for API errors
        if 'error' in results:
            error_msg = results.get('error', 'Unknown error')
            print(f"❌ [SERPAPI] API Error: {error_msg}")
            return {
                'error': error_msg,
                'message': f'API Error: {error_msg}',
                'demo_mode': True,
                'raw_results': results
            }
        
        # Extract best flights
        best_flights = []
        if 'best_flights' in results:
            print(f"✅ [SERPAPI] Found {len(results['best_flights'])} best flights")
            
            for flight in results['best_flights'][:10]:  # Top 10 best options
                flights_list = flight.get('flights', [])
                if not flights_list:
                    continue
                
                # Get first flight segment details
                first_flight = flights_list[0]
                
                # Calculate total duration
                total_duration = flight.get('total_duration', 0)
                duration_str = f"{total_duration // 60}h {total_duration % 60}m" if total_duration else 'N/A'
                
                # Get departure and arrival info
                dep_airport = first_flight.get('departure_airport', {})
                arr_airport = first_flight.get('arrival_airport', {})
                
                # Calculate number of stops
                num_stops = len(flights_list) - 1
                
                best_flights.append({
                    'price': f"${flight.get('price', 'N/A')}",
                    'airline': first_flight.get('airline', 'N/A'),
                    'airline_logo': first_flight.get('airline_logo', ''),
                    'departure_time': dep_airport.get('time', 'N/A').split()[-1] if dep_airport.get('time') else 'N/A',  # Extract time only
                    'arrival_time': arr_airport.get('time', 'N/A').split()[-1] if arr_airport.get('time') else 'N/A',  # Extract time only
                    'departure_airport': dep_airport.get('id', origin),
                    'arrival_airport': arr_airport.get('id', destination),
                    'departure_airport_name': dep_airport.get('name', 'N/A'),
                    'arrival_airport_name': arr_airport.get('name', 'N/A'),
                    'duration': duration_str,
                    'stops': num_stops,
                    'layovers': flight.get('layovers', []),
                    'carbon_emissions': flight.get('carbon_emissions', {}),
                    'flight_number': first_flight.get('flight_number', 'N/A'),
                    'travel_class': first_flight.get('travel_class', 'Economy'),
                    'airplane': first_flight.get('airplane', 'N/A'),
                    'legroom': first_flight.get('legroom', 'N/A'),
                    'extensions': flight.get('extensions', []),
                    'type': 'best_flight',
                    'booking_token': flight.get('departure_token', '')
                })
        
        # Extract other flights
        other_flights = []
        if 'other_flights' in results:
            print(f"✅ [SERPAPI] Found {len(results['other_flights'])} other flights")
            
            for flight in results['other_flights'][:10]:  # Top 10 other options
                flights_list = flight.get('flights', [])
                if not flights_list:
                    continue
                
                first_flight = flights_list[0]
                total_duration = flight.get('total_duration', 0)
                duration_str = f"{total_duration // 60}h {total_duration % 60}m" if total_duration else 'N/A'
                
                dep_airport = first_flight.get('departure_airport', {})
                arr_airport = first_flight.get('arrival_airport', {})
                num_stops = len(flights_list) - 1
                
                other_flights.append({
                    'price': f"${flight.get('price', 'N/A')}",
                    'airline': first_flight.get('airline', 'N/A'),
                    'airline_logo': first_flight.get('airline_logo', ''),
                    'departure_time': dep_airport.get('time', 'N/A').split()[-1] if dep_airport.get('time') else 'N/A',
                    'arrival_time': arr_airport.get('time', 'N/A').split()[-1] if arr_airport.get('time') else 'N/A',
                    'departure_airport': dep_airport.get('id', origin),
                    'arrival_airport': arr_airport.get('id', destination),
                    'duration': duration_str,
                    'stops': num_stops,
                    'flight_number': first_flight.get('flight_number', 'N/A'),
                    'type': 'other_flight'
                })
        
        print(f"✅ [SERPAPI] Processed {len(best_flights)} best flights and {len(other_flights)} other flights")
        
        return {
            'success': True,
            'best_flights': best_flights,
            'other_flights': other_flights,
            'search_params': {
                'origin': origin,
                'destination': destination,
                'departure_date': departure_date,
                'return_date': return_date,
                'adults': adults,
                'children': children
            },
            'search_metadata': results.get('search_metadata', {}),
            'price_insights': results.get('price_insights', {})
        }
        
    except ImportError:
        print("❌ [SERPAPI] Library not installed")
        return {
            'error': 'SerpAPI library not installed',
            'message': 'Please install: pip install google-search-results',
            'demo_mode': True
        }
    except Exception as e:
        print(f"❌ [SERPAPI] Error searching flights: {e}")
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'message': f'Failed to fetch flight data: {str(e)}',
            'demo_mode': True
        }

def search_hotels(location: str, check_in: str, check_out: str, adults: int = 2, children: int = 0, currency: str = "USD") -> Dict[str, Any]:
    """
    Search for hotels using SerpAPI Google Hotels API.
    Documentation: https://serpapi.com/google-hotels-api
    
    Args:
        location: City or location name (e.g., "Austin, TX")
        check_in: Check-in date in YYYY-MM-DD format
        check_out: Check-out date in YYYY-MM-DD format
        adults: Number of adults (default: 2)
        children: Number of children (default: 0)
        currency: Currency code (default: USD)
        
    Returns:
        Dict containing hotel results
    """
    try:
        from serpapi import GoogleSearch
        
        api_key = get_serpapi_key()
        if not api_key:
            return {
                'error': 'SerpAPI key not configured',
                'message': 'Please add SERPAPI_API_KEY to your .env file',
                'demo_mode': True
            }
        
        # Build search parameters according to official SerpAPI documentation
        params = {
            "engine": "google_hotels",
            "q": location,
            "check_in_date": check_in,
            "check_out_date": check_out,
            "adults": str(adults),
            "currency": currency,
            "gl": "us",
            "hl": "en",
            "api_key": api_key
        }
        
        if children > 0:
            params["children"] = str(children)
        
        print(f"🔍 [SERPAPI] Searching hotels in {location}")
        print(f"   Check-in: {check_in}, Check-out: {check_out}")
        print(f"   Guests: {adults} adult(s)" + (f", {children} child(ren)" if children > 0 else ""))
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Check for API errors
        if 'error' in results:
            error_msg = results.get('error', 'Unknown error')
            print(f"❌ [SERPAPI] API Error: {error_msg}")
            return {
                'error': error_msg,
                'message': f'API Error: {error_msg}',
                'demo_mode': True,
                'raw_results': results
            }
        
        # Extract hotel properties
        hotels = []
        
        if 'properties' in results:
            print(f"✅ [SERPAPI] Found {len(results['properties'])} hotels")
            
            for hotel in results['properties'][:15]:  # Top 15 hotels
                # Extract rate information
                rate_per_night = hotel.get('rate_per_night', {})
                total_rate = hotel.get('total_rate', {})
                
                # Format prices
                price_per_night = rate_per_night.get('lowest', 'N/A')
                if isinstance(price_per_night, (int, float)):
                    price_per_night = f"${price_per_night}"
                
                total_price = total_rate.get('lowest', 'N/A')
                if isinstance(total_price, (int, float)):
                    total_price = f"${total_price}"
                
                hotels.append({
                    'name': hotel.get('name', 'N/A'),
                    'hotel_class': hotel.get('hotel_class', 'N/A'),
                    'rate_per_night': price_per_night,
                    'total_rate': total_price,
                    'rating': hotel.get('overall_rating', 'N/A'),
                    'reviews': hotel.get('reviews', 0),
                    'amenities': hotel.get('amenities', []),
                    'description': hotel.get('description', ''),
                    'images': hotel.get('images', []),
                    'link': hotel.get('link', ''),
                    'gps_coordinates': hotel.get('gps_coordinates', {}),
                    'check_in_time': hotel.get('check_in_time', 'N/A'),
                    'check_out_time': hotel.get('check_out_time', 'N/A'),
                    'extracted_hotel_class': hotel.get('extracted_hotel_class', 'N/A')
                })
        
        print(f"✅ [SERPAPI] Processed {len(hotels)} hotels")
        
        return {
            'success': True,
            'hotels': hotels,
            'search_params': {
                'location': location,
                'check_in': check_in,
                'check_out': check_out,
                'adults': adults,
                'children': children
            },
            'search_metadata': results.get('search_metadata', {})
        }
        
    except ImportError:
        print("❌ [SERPAPI] Library not installed")
        return {
            'error': 'SerpAPI library not installed',
            'message': 'Please install: pip install google-search-results',
            'demo_mode': True
        }
    except Exception as e:
        print(f"❌ [SERPAPI] Error searching hotels: {e}")
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'message': f'Failed to fetch hotel data: {str(e)}',
            'demo_mode': True
        }

def search_events(location: str, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
    """
    Search for events using SerpAPI Google Events API.
    Documentation: https://serpapi.com/google-events-api
    
    Args:
        location: City or location name (e.g., "Austin, TX")
        start_date: Optional start date in YYYY-MM-DD format
        end_date: Optional end date in YYYY-MM-DD format
        
    Returns:
        Dict containing event results
    """
    try:
        from serpapi import GoogleSearch
        
        api_key = get_serpapi_key()
        if not api_key:
            return {
                'error': 'SerpAPI key not configured',
                'message': 'Please add SERPAPI_API_KEY to your .env file',
                'demo_mode': True
            }
        
        # Build search parameters according to official SerpAPI documentation
        params = {
            "engine": "google_events",
            "q": f"Events in {location}",
            "hl": "en",
            "gl": "us",
            "api_key": api_key
        }
        
        # Add date filters if provided
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        print(f"🔍 [SERPAPI] Searching events in {location}")
        if start_date or end_date:
            print(f"   Date range: {start_date or 'N/A'} to {end_date or 'N/A'}")
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Check for API errors
        if 'error' in results:
            error_msg = results.get('error', 'Unknown error')
            print(f"❌ [SERPAPI] API Error: {error_msg}")
            return {
                'error': error_msg,
                'message': f'API Error: {error_msg}',
                'demo_mode': True,
                'raw_results': results
            }
        
        # Extract events
        events = []
        
        if 'events_results' in results:
            print(f"✅ [SERPAPI] Found {len(results['events_results'])} events")
            
            for event in results['events_results'][:20]:  # Top 20 events
                # Extract date and time information
                date_info = event.get('date', {})
                
                events.append({
                    'title': event.get('title', 'N/A'),
                    'description': event.get('description', ''),
                    'date': date_info.get('start_date', 'N/A'),
                    'time': date_info.get('when', 'N/A'),
                    'venue': event.get('venue', {}).get('name', 'N/A'),
                    'address': event.get('address', ['N/A']),
                    'link': event.get('link', ''),
                    'thumbnail': event.get('thumbnail', ''),
                    'ticket_info': event.get('ticket_info', []),
                    'venue_info': event.get('venue', {})
                })
        
        print(f"✅ [SERPAPI] Processed {len(events)} events")
        
        return {
            'success': True,
            'events': events,
            'search_params': {
                'location': location,
                'start_date': start_date,
                'end_date': end_date
            },
            'search_metadata': results.get('search_metadata', {})
        }
        
    except ImportError:
        print("❌ [SERPAPI] Library not installed")
        return {
            'error': 'SerpAPI library not installed',
            'message': 'Please install: pip install google-search-results',
            'demo_mode': True
        }
    except Exception as e:
        print(f"❌ [SERPAPI] Error searching events: {e}")
        import traceback
        traceback.print_exc()
        return {
            'error': str(e),
            'message': f'Failed to fetch event data: {str(e)}',
            'demo_mode': True
        }

def get_demo_flights() -> List[Dict[str, Any]]:
    """Get demo flight data when API is not available."""
    return [
        {
            'price': '$450',
            'airline': 'Demo Airlines',
            'departure_time': '10:00',
            'arrival_time': '14:00',
            'duration': '4h 0m',
            'stops': 0,
            'flight_number': 'DA 123',
            'type': 'demo'
        },
        {
            'price': '$380',
            'airline': 'Budget Air',
            'departure_time': '14:30',
            'arrival_time': '19:15',
            'duration': '4h 45m',
            'stops': 1,
            'flight_number': 'BA 456',
            'type': 'demo'
        },
        {
            'price': '$520',
            'airline': 'Comfort Airways',
            'departure_time': '08:00',
            'arrival_time': '12:30',
            'duration': '4h 30m',
            'stops': 0,
            'flight_number': 'CA 789',
            'type': 'demo'
        }
    ]

def get_demo_hotels() -> List[Dict[str, Any]]:
    """Get demo hotel data when API is not available."""
    return [
        {
            'name': 'Demo Grand Hotel',
            'rate_per_night': '$120',
            'total_rate': '$360',
            'rating': 4.5,
            'reviews': 1250,
            'amenities': ['WiFi', 'Pool', 'Breakfast', 'Gym'],
            'description': 'Comfortable hotel in city center with modern amenities',
            'type': 'demo'
        },
        {
            'name': 'Budget Inn',
            'rate_per_night': '$75',
            'total_rate': '$225',
            'rating': 4.0,
            'reviews': 850,
            'amenities': ['WiFi', 'Parking'],
            'description': 'Affordable option near major attractions',
            'type': 'demo'
        },
        {
            'name': 'Luxury Resort & Spa',
            'rate_per_night': '$250',
            'total_rate': '$750',
            'rating': 4.8,
            'reviews': 2100,
            'amenities': ['WiFi', 'Pool', 'Spa', 'Restaurant', 'Beach Access', 'Gym'],
            'description': 'Premium beachfront resort with world-class facilities',
            'type': 'demo'
        }
    ]

def get_demo_events() -> List[Dict[str, Any]]:
    """Get demo event data when API is not available."""
    return [
        {
            'title': 'Local Food Festival',
            'date': '2025-11-15',
            'time': '10:00 AM - 6:00 PM',
            'venue': 'City Park',
            'description': 'Enjoy local cuisine from top restaurants',
            'type': 'demo'
        },
        {
            'title': 'Live Music Concert',
            'date': '2025-11-20',
            'time': '7:00 PM',
            'venue': 'Downtown Arena',
            'description': 'Popular bands performing live',
            'type': 'demo'
        }
    ]
