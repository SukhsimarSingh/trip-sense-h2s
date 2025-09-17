"""
Integration module for connecting the AI trip planner with Streamlit app.
This module provides the interface between app.py and the AI planning system.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from .gemini_client import get_gemini_client
from .tools import tools
from .router import TOOL_ROUTER
from .prompt_loader import load_system_prompt, render_user_prompt
from .trip_storage import trip_storage
from google.genai import types as genai_types

logger = logging.getLogger(__name__)

THINKING_BUDGET = 0
TEMPERATURE= 0.7
MAX_OUTPUT_TOKENS=2048

class TripPlannerAI:
    """Main interface for AI trip planning functionality."""
    
    def __init__(self):
        self.client = None
        self.model_name = os.getenv("GEMINI_MODEL", "models/gemini-1.5-pro")
        self.system_instruction = None
        self.current_trip_data = None  # Store current trip form data
        self.current_itinerary_data = None  # Store current AI-generated itinerary
        self._initialize()
    
    def _initialize(self):
        """Initialize the AI client and system instruction."""
        try:
            self.client = get_gemini_client()
            self.system_instruction = load_system_prompt()
        except Exception as e:
            logger.error(f"Failed to initialize TripPlannerAI: {e}")
            self.client = None
            self.system_instruction = "You are an expert AI trip planner. Plan realistic itineraries with travel times, costs, and flexible options."
    
    def is_available(self) -> bool:
        """Check if the AI client is available."""
        return self.client is not None
    
    def generate_initial_plan(self, trip_data: Dict[str, Any]) -> str:
        """Generate initial trip plan from form data."""
        # Store the trip data for potential saving later
        self.current_trip_data = trip_data.copy()
        
        if not self.is_available():
            demo_response = self._generate_demo_response(trip_data)
            # Store demo itinerary data for saving
            self.current_itinerary_data = {
                "demo_response": demo_response,
                "generated_at": datetime.now().isoformat(),
                "demo_mode": True
            }
            return demo_response
        
        try:
            # Render the user prompt with trip data
            user_prompt = render_user_prompt("initial_prompt.txt", trip_data)
            
            # Generate content with tools
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=genai_types.GenerateContentConfig(
                    thinking_config=genai_types.ThinkingConfig(thinking_budget=THINKING_BUDGET),
                    system_instruction=self.system_instruction,
                    temperature=TEMPERATURE,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                    tools=[tools]
                ),
            )
            
            # Handle tool calls if present
            result = self._process_response_with_tools(response, user_prompt)
            
            # Store the generated itinerary for potential saving
            self.current_itinerary_data = {
                "user_prompt": user_prompt,
                "ai_response": result,
                "generated_at": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating initial plan: {e}")
            return f"I apologize, but I encountered an error while planning your trip: {str(e)}"
    
    def chat_response(self, chat_history: List[Dict[str, str]], user_message: str) -> str:
        """Generate response for chat interaction."""
        if not self.is_available():
            return self._generate_demo_chat_response(user_message)
        
        try:
            # Build conversation context
            conversation_text = self._build_conversation_context(chat_history, user_message)
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=conversation_text,
                config=genai_types.GenerateContentConfig(
                    thinking_config=genai_types.ThinkingConfig(thinking_budget=THINKING_BUDGET),
                    system_instruction=self.system_instruction,
                    temperature=TEMPERATURE,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                    tools=[tools]
                ),
            )
            
            return self._process_response_with_tools(response, user_message)
            
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def _process_response_with_tools(self, response, original_prompt: str) -> str:
        """Process response and handle any tool calls."""
        try:
            # Check if there are tool calls in the response
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    parts = candidate.content.parts
                    
                    # Look for function calls
                    function_calls = [part.function_call for part in parts if hasattr(part, 'function_call') and part.function_call]
                    
                    if function_calls:
                        # Execute tool calls
                        tool_results = []
                        save_trip_called = False
                        
                        for call in function_calls:
                            tool_name = call.name
                            tool_args = dict(call.args) if hasattr(call, 'args') else {}
                            
                            if tool_name in TOOL_ROUTER:
                                try:
                                    # Handle save_trip specially
                                    if tool_name == "save_trip":
                                        result = self._handle_save_trip(tool_args)
                                        save_trip_called = True
                                        # Return user-friendly message for save_trip
                                        if result.get("status") == "saved":
                                            return f"✅ {result.get('message', 'Trip saved successfully!')}"
                                        else:
                                            return f"❌ {result.get('message', 'Failed to save trip.')}"
                                    else:
                                        result = TOOL_ROUTER[tool_name](tool_args)
                                    
                                    tool_results.append({
                                        "function_call": {"name": tool_name},
                                        "function_response": {"name": tool_name, "response": result}
                                    })
                                except Exception as e:
                                    logger.error(f"Error executing tool {tool_name}: {e}")
                                    # Provide user-friendly error messages
                                    error_msg = str(e)
                                    if "Places API" in error_msg and "not enabled" in error_msg:
                                        user_friendly_error = "Location search is currently unavailable. I can still help you plan your trip with general recommendations!"
                                    elif "GOOGLE_MAPS_API_KEY not set" in error_msg:
                                        user_friendly_error = "Location services are not configured. I'll provide general travel recommendations instead."
                                    else:
                                        user_friendly_error = f"I encountered an issue with {tool_name.replace('_', ' ')}, but I can still help you plan your trip!"
                                    
                                    tool_results.append({
                                        "function_call": {"name": tool_name},
                                        "function_response": {"name": tool_name, "response": {"error": user_friendly_error}}
                                    })
                        
                        # Generate final response with tool results (only if not save_trip)
                        if tool_results and not save_trip_called:
                            try:
                                # Build proper conversation history for final response
                                conversation_parts = [original_prompt]
                                
                                # Add tool results summary
                                tool_summary = self._create_tool_summary(tool_results)
                                conversation_parts.append(f"Based on the search results: {tool_summary}")
                                conversation_parts.append("Please provide a helpful, conversational response based on this information.")
                                
                                final_prompt = "\n\n".join(conversation_parts)
                                
                                final_response = self.client.models.generate_content(
                                    model=self.model_name,
                                    contents=final_prompt,
                                    config=genai_types.GenerateContentConfig(
                                        thinking_config=genai_types.ThinkingConfig(thinking_budget=THINKING_BUDGET),
                                        system_instruction=self.system_instruction,
                                        temperature=TEMPERATURE,
                                        max_output_tokens=MAX_OUTPUT_TOKENS
                                    )
                                )
                                return final_response.text or "I've processed your request with the available tools."
                            except Exception as e:
                                logger.error(f"Error in final response generation: {e}")
                                # Fallback to a summary of tool results
                                return self._create_tool_summary(tool_results)
            
            # Return the original response text if no tool calls
            response_text = response.text or ""
            if response_text:
                return response_text
            else:
                # Fallback conversational response
                return self._generate_conversational_fallback(original_prompt)
            
        except Exception as e:
            logger.error(f"Error processing response with tools: {e}")
            # Try to get basic response text
            try:
                return response.text or self._generate_conversational_fallback(original_prompt)
            except:
                return "I'm here to help you plan your trip! Could you please rephrase your request?"
    
    def _build_conversation_context(self, chat_history: List[Dict[str, str]], user_message: str) -> str:
        """Build conversation context from chat history."""
        context_lines = []
        
        # Include last 5 messages for context
        recent_messages = chat_history[-2:] if len(chat_history) > 2 else chat_history
        
        for message in recent_messages:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if isinstance(content, dict):
                # Handle tool responses
                if "tool" in content:
                    content = f"Used tool {content.get('tool', 'unknown')} with result: {content.get('result', {})}"
                else:
                    content = str(content)
            
            if role == "assistant":
                context_lines.append(f"Assistant: {content}")
            elif role == "user":
                context_lines.append(f"User: {content}")
        
        context_lines.append(f"User: {user_message}")
        return "\n".join(context_lines)
    
    def _generate_demo_response(self, trip_data: Dict[str, Any]) -> str:
        """Generate demo response when AI is not available."""
        destination = trip_data.get("destination", "your destination")
        duration = trip_data.get("duration", "N/A")
        travel_type = trip_data.get("travel_type", "Mixed Experience")
        budget = trip_data.get("budget", "Medium Budget")
        
        return f"""*Note: This is a demo response. Configure your Gemini API key for personalized AI-powered recommendations.*
# {duration}-Day Trip to {destination}

## Day 1: Arrival & Exploration
- **Morning**: Arrive and check into accommodation
- **Afternoon**: Explore the city center and main attractions
- **Evening**: Try local cuisine at a recommended restaurant

## Day 2: {travel_type.split('&')[0].strip()} Focus
- **Morning**: Visit top-rated attractions based on your {travel_type.lower()} preference
- **Afternoon**: Continue exploring with {budget.lower()} options
- **Evening**: Relax and enjoy local entertainment

*For a fully personalized itinerary with real-time recommendations, weather updates, and booking links, please configure your Gemini API key.*

**Budget Estimate**: Varies based on your {budget.lower()} preference
**Best Time to Visit**: Check local weather and seasonal recommendations
**Transportation**: Local transport options available

Would you like me to help you refine any part of this itinerary?"""
    
    def _generate_demo_chat_response(self, user_message: str) -> str:
        """Generate demo chat response when AI is not available."""
        # Check if user is asking to save trip
        if any(keyword in user_message.lower() for keyword in ["save", "store", "keep"]) and any(keyword in user_message.lower() for keyword in ["trip", "itinerary", "plan"]):
            if self.current_trip_data:
                return "I can save your trip! However, you'll need to configure your Gemini API key for the AI to automatically handle save requests. For now, you can use the 'Save Itinerary' button or visit the Saved Trips page."
            else:
                return "I'd be happy to save a trip for you, but you'll need to create a trip first! Please generate a trip plan and then I can help you save it."
        
        # Use the conversational fallback for better responses
        return self._generate_conversational_fallback(user_message)
    
    def _handle_save_trip(self, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the save_trip tool call with actual trip data."""
        trip_name = tool_args.get("trip_name", "My Trip")
        trip_summary = tool_args.get("trip_summary", "")
        
        if not self.current_trip_data:
            return {
                "status": "error",
                "message": "No trip data available to save. Please generate a trip first.",
                "trip_name": trip_name
            }
        
        try:
            # Combine all trip data (itinerary might be None in demo mode)
            complete_trip_data = {
                "trip_name": trip_name,
                "trip_summary": trip_summary,
                "form_data": self.current_trip_data,
                "itinerary": self.current_itinerary_data or {"demo_mode": True},
                "saved_at": datetime.now().isoformat()
            }
            
            # Save to storage
            trip_id = trip_storage.save_trip(complete_trip_data)
            
            return {
                "status": "saved",
                "message": f"Trip '{trip_name}' has been saved successfully!",
                "trip_name": trip_name,
                "trip_id": trip_id,
                "save_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error saving trip: {e}")
            return {
                "status": "error",
                "message": f"Failed to save trip: {str(e)}",
                "trip_name": trip_name
            }
    
    def _create_tool_summary(self, tool_results: List[Dict[str, Any]]) -> str:
        """Create a user-friendly summary of tool results."""
        if not tool_results:
            return "I've processed your request."
        
        summary_parts = []
        for result in tool_results:
            tool_name = result.get("function_call", {}).get("name", "unknown")
            response = result.get("function_response", {}).get("response", {})
            
            # Handle errors in tool responses
            if isinstance(response, dict) and "error" in response:
                error_msg = response["error"]
                if "Location search is currently unavailable" in error_msg:
                    summary_parts.append("Location search is temporarily unavailable, but I can still provide general recommendations.")
                elif "Location services are not configured" in error_msg:
                    summary_parts.append("I'm working with general travel knowledge since location services aren't configured.")
                else:
                    summary_parts.append("I encountered a technical issue but can still help with your travel planning.")
                continue
            
            if tool_name == "search_text":
                places = response if isinstance(response, list) else []
                if places:
                    summary_parts.append(f"Found {len(places)} location(s) for your search.")
                else:
                    summary_parts.append("I searched for locations but didn't find specific results.")
            
            elif tool_name in ["get_nearby_attractions", "get_nearby_restaurants", "get_hotels"]:
                places = response if isinstance(response, list) else []
                if places:
                    place_type = tool_name.replace("get_nearby_", "").replace("_", " ")
                    summary_parts.append(f"Found {len(places)} {place_type} in the area.")
                else:
                    summary_parts.append(f"I searched for nearby options but didn't find specific results.")
            
            elif tool_name == "get_weather":
                if isinstance(response, dict) and response:
                    summary_parts.append("I've checked the weather forecast for your trip dates.")
                else:
                    summary_parts.append("I tried to get weather information but couldn't retrieve it.")
        
        return " ".join(summary_parts) if summary_parts else "I've processed your request with the available information."
    
    def _generate_conversational_fallback(self, user_message: str) -> str:
        """Generate a conversational fallback response."""
        message_lower = user_message.lower()
        
        # Trip planning related
        if any(word in message_lower for word in ["plan", "trip", "travel", "visit", "go to"]):
            return "I'd be happy to help you plan your trip! Could you tell me more about where you'd like to go and what kind of experience you're looking for?"
        
        # Recommendations
        elif any(word in message_lower for word in ["recommend", "suggest", "best", "good"]):
            return "I can definitely provide recommendations! What specifically are you looking for - restaurants, attractions, hotels, or something else?"
        
        # Questions about places
        elif any(word in message_lower for word in ["where", "what", "how", "when"]):
            return "Great question! I'm here to help with travel planning and recommendations. What would you like to know more about?"
        
        # Saving related
        elif any(word in message_lower for word in ["save", "store", "keep"]):
            return "I can help you save your trip! Just let me know what you'd like to name your trip and I'll save it for you."
        
        # General travel topics
        elif any(word in message_lower for word in ["hotel", "restaurant", "food", "eat", "stay", "accommodation"]):
            return "I can help you find great options for that! Could you let me know which city or area you're interested in?"
        
        # Weather
        elif any(word in message_lower for word in ["weather", "climate", "temperature"]):
            return "Weather is definitely important for trip planning! Which destination are you curious about?"
        
        # Default friendly response
        else:
            return "I'm here to help you plan amazing trips! Feel free to ask me about destinations, recommendations, or anything travel-related. What would you like to explore?"

# Global instance for use in app.py
trip_planner_ai = TripPlannerAI()