from google.genai.types import Tool, FunctionDeclaration, Schema
from .handlers import (
    search_text_declaration,
    get_nearby_attractions_declaration,
    get_nearby_restaurants_declaration,
    get_hotels_declaration,
    get_weather_declaration,
    save_trip_declaration,
)

# Convert the dictionary declarations to FunctionDeclaration objects
search_text = FunctionDeclaration(**search_text_declaration)
get_nearby_attractions = FunctionDeclaration(**get_nearby_attractions_declaration)
get_nearby_restaurants = FunctionDeclaration(**get_nearby_restaurants_declaration)
get_hotels = FunctionDeclaration(**get_hotels_declaration)
get_weather = FunctionDeclaration(**get_weather_declaration)
save_trip = FunctionDeclaration(**save_trip_declaration)

tools = Tool(function_declarations=[
    search_text, get_nearby_attractions, get_nearby_restaurants, get_hotels, get_weather, save_trip
])