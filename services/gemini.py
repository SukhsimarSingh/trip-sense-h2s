import os
from typing import Dict, Any, List
from datetime import datetime
from google import genai
from google.genai import types
import streamlit as st

from dotenv import load_dotenv
load_dotenv()

from services.tools import tools
from services.prompt_loader import load_system_prompt, render_user_prompt
from services.logging import initialize_metrics, log_request, estimate_tokens, logger

# Model Constants
THINKING_BUDGET = 0  # Enable thinking for better reasoning
TEMPERATURE = 0.2  # Slightly higher for better formatting while maintaining accuracy
MAX_OUTPUT_TOKENS = 2048  # Increased for detailed responses
TOP_P = 0.8  # Nucleus sampling for controlled creativity
model_name = "gemini-2.5-flash"
SYSTEM_INSTRUCTION = load_system_prompt()

safety_settings = [
    {
        "category": types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        "threshold": types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    },
    {
        "category": types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        "threshold": types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    },
]

@st.cache_resource
def get_gemini_client():
    """Initialize and cache the Gemini client to avoid recreating on every page load."""
    try:
        try:
            api_key = os.getenv("GEMINI_API_KEY")
        except:
            api_key = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=api_key)
        logger.info("Gemini client initialized and cached")
        return client
    except Exception as e:
        logger.error(f"Error initializing Gemini client: {e}")
        raise

class TripSenseAI:
    def __init__(self):
        # Initialize metrics tracking
        initialize_metrics()
        
        # Initialize all attributes directly
        try:
            self.client = get_gemini_client()  # Use cached client
            self.model_name = model_name
            self.system_instruction = SYSTEM_INSTRUCTION
            self.thinking_budget = THINKING_BUDGET
            self.temperature = TEMPERATURE
            self.max_output_tokens = MAX_OUTPUT_TOKENS
            self.top_p = TOP_P
            self.tools = tools
            self.safety_settings = safety_settings
            
            logger.info(f"TripSenseAI initialized successfully with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize TripSenseAI: {e}")
            raise

    def _execute_function_call(self, function_call):
        """Execute a function call and return the result."""
        function_name = function_call.name
        function_args = dict(function_call.args)
        
        logger.info(f"Executing function: {function_name} with args: {function_args}")
        start_time = datetime.now()
        
        try:
            # Now that we fixed the naming conflict in tools.py, we can directly import and use the functions
            import services.tools as tools_module
            
            # Map function names to their actual implementations
            function_map = {
                "search_text": tools_module.search_text,
                "get_nearby_attractions": tools_module.get_nearby_attractions,
                "get_nearby_restaurants": tools_module.get_nearby_restaurants,
                "get_hotels": tools_module.get_hotels,
                "get_weather": tools_module.get_weather,
                "save_trip": tools_module.save_trip
            }
            
            if function_name in function_map:
                func = function_map[function_name]
                if callable(func):
                    # Execute with timeout handling
                    result = func(function_args)
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"Function {function_name} executed successfully in {execution_time:.2f}s")
                    
                    # Validate result
                    if result is None:
                        logger.warning(f"Function {function_name} returned None")
                        return {"error": f"Function {function_name} returned no data"}
                    
                    # Log result summary for debugging (only for complex results)
                    if isinstance(result, list) and len(result) > 10:
                        logger.debug(f"Function {function_name} returned large list: {len(result)} items")
                    elif isinstance(result, dict) and len(result) > 5:
                        logger.debug(f"Function {function_name} returned large dict with keys: {list(result.keys())}")
                    
                    return result
                else:
                    logger.error(f"Function {function_name} is not callable: {type(func)}")
                    return {"error": f"Function {function_name} is not callable"}
            else:
                logger.error(f"Unknown function: {function_name}")
                return {"error": f"Unknown function: {function_name}"}
                
        except TimeoutError as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Function {function_name} timed out after {execution_time:.2f}s: {e}")
            return {"error": f"Function {function_name} timed out"}
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error executing function {function_name} after {execution_time:.2f}s: {e}")
            return {"error": f"Error executing {function_name}: {str(e)}"}

    def _build_conversation_context(self, chat_history: List[Dict[str, str]], user_message: str, max_history: int = 3) -> str:
        """Build conversation context from chat history and new message.
        
        Note: Gemini maintains conversation history automatically, so we only need
        minimal context for follow-up responses after function calls.
        """
        context_parts = []
        
        # Add only the last few messages for context (reduced from 10 to 3)
        recent_history = chat_history[-max_history:] if len(chat_history) > max_history else chat_history
        
        for message in recent_history:
            if message["role"] == "user":
                context_parts.append(f"User: {message['content']}")
            elif message["role"] == "assistant":
                context_parts.append(f"Assistant: {message['content']}")
        
        # Add the new user message
        context_parts.append(f"User: {user_message}")
        
        return "\n".join(context_parts)

    def _create_generation_config(self, use_tools=True):
        """Create a standard generation config for API calls with anti-hallucination settings."""
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=self.thinking_budget),
            system_instruction=self.system_instruction,
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
            top_p=self.top_p,
            safety_settings=self.safety_settings,
        )
        
        if use_tools:
            config.tools = [self.tools]
            
        return config

    def _process_response_with_functions(self, response, original_prompt, request_type="general"):
        """Process a response that may contain function calls and generate follow-up if needed."""
        has_function_calls = False
        function_calls = []
        text_parts = []
        
        if response.candidates and response.candidates[0].content.parts:
            logger.info(f"Processing response with {len(response.candidates[0].content.parts)} parts")
            
            for i, part in enumerate(response.candidates[0].content.parts):
                if hasattr(part, 'function_call') and part.function_call:
                    has_function_calls = True
                    function_call = part.function_call
                    logger.debug(f"Found function call {i+1}: {function_call.name} with args: {function_call.args}")
                    
                    # Execute the function call
                    function_result = self._execute_function_call(function_call)
                    function_calls.append({
                        "name": function_call.name,
                        "args": dict(function_call.args),
                        "result": function_result
                    })
                elif hasattr(part, 'text') and part.text:
                    text_parts.append(part.text)
        
        logger.info(f"Response analysis: {len(function_calls)} function calls, {len(text_parts)} text parts")
        
        # Return both the processing results and whether follow-up is needed
        return {
            "has_function_calls": has_function_calls,
            "function_calls": function_calls,
            "text_parts": text_parts,
            "original_prompt": original_prompt,
            "request_type": request_type
        }

    def _generate_follow_up_response(self, process_result, start_time, input_tokens, chat_history=None, user_message=None):
        """Generate a follow-up response using function call results with optimized context."""
        function_calls = process_result["function_calls"]
        text_parts = process_result["text_parts"]
        original_prompt = process_result["original_prompt"]
        request_type = process_result["request_type"]
        
        logger.info(f"FOLLOW-UP RESPONSE GENERATION - Request Type: {request_type}")
        logger.info(f"Processing {len(function_calls)} function results for follow-up response")
        
        # Log which functions were called for the follow-up
        if function_calls:
            function_names = [fc["name"] for fc in function_calls]
            logger.info(f"Functions processed: {', '.join(function_names)}")
        
        function_results_text = "\n".join([
            f"Function {fc['name']} returned: {fc['result']}" 
            for fc in function_calls
        ])
        
        # Include any text from the original response
        original_text = "\n".join(text_parts) if text_parts else ""
        
        # Create optimized follow-up prompt based on request type
        if request_type == "initial_plan":
            # For initial plan, use the original trip data context
            follow_up_prompt = original_prompt + "\n\nFunction Results:\n" + function_results_text + "\n\nPlease provide a comprehensive trip plan based on the above information."
        else:  
            # For chat responses, use limited recent context (max 3 messages) instead of full conversation
            if chat_history and user_message:
                limited_context = self._build_conversation_context(chat_history, user_message, max_history=3)
                follow_up_prompt = f"{limited_context}\n\nFunction Results:\n{function_results_text}\n\nPlease provide a helpful response based on the above information."
                logger.info(f"Using limited context with {min(len(chat_history), 3)} previous messages for follow-up")
            else:
                # Fallback to original prompt if chat context not available
                follow_up_prompt = f"{original_prompt}\n\nFunction Results:\n{function_results_text}\n\nPlease provide a helpful response based on the above information."
                logger.warning("Chat context not available for follow-up, using original prompt")
            
        if original_text:
            follow_up_prompt += f"\n\nOriginal response: {original_text}"
        
        # Calculate tokens for follow-up request
        follow_up_input_tokens = estimate_tokens(follow_up_prompt)  # Removed system prompt from token calculation
        logger.info(f"Follow-up request estimated input tokens: {follow_up_input_tokens} (excluding system prompt)")
        
        try:
            logger.info("Making follow-up API call to Gemini")
            follow_up_response = self.client.models.generate_content(
                model=self.model_name,
                contents=follow_up_prompt,
                config=self._create_generation_config(use_tools=False)  # No tools in follow-up to avoid loops
            )
            
            logger.info("Received follow-up response from Gemini API")
            
            if follow_up_response.text:
                follow_up_output_tokens = estimate_tokens(follow_up_response.text)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Log metrics for follow-up response
                total_input_tokens = input_tokens + follow_up_input_tokens
                log_request(f"{request_type}_with_functions", total_input_tokens, follow_up_output_tokens, True)
                logger.info(f"Follow-up response generated successfully in {execution_time:.2f}s")
                logger.info(f"Total tokens - Input: {total_input_tokens}, Output: {follow_up_output_tokens}")
                
                return follow_up_response.text
            else:
                logger.warning("Follow-up response was empty")
                fallback_msg = "I've gathered information about your request and am ready to help!"
                fallback_tokens = estimate_tokens(fallback_msg)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                log_request(f"{request_type}_follow_up_fallback", input_tokens + follow_up_input_tokens, fallback_tokens, True)
                logger.warning(f"Using follow-up fallback after {execution_time:.2f}s")
                
                return fallback_msg
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error in follow-up response generation after {execution_time:.2f}s: {e}")
            
            # Log error for follow-up
            log_request(f"{request_type}_follow_up", input_tokens + follow_up_input_tokens, 0, False, str(e))
            
            # Return a meaningful response even if follow-up fails
            error_fallback = f"I found some information but encountered an issue. Here's what I found:\n\n{function_results_text}"
            return error_fallback

    def generate_initial_plan(self, trip_data):
        logger.info(f"Starting initial trip plan generation for destination: {trip_data.get('destination', 'Unknown')}")
        logger.debug(f"Trip data: {trip_data}")
        
        start_time = datetime.now()
        input_tokens = 0
        output_tokens = 0
        
        try:
            enhanced_trip_data = trip_data.copy()
            user_prompt = render_user_prompt(enhanced_trip_data)
            input_tokens = estimate_tokens(user_prompt + str(self.system_instruction))
            
            logger.info(f"Generated user prompt, estimated input tokens: {input_tokens}")

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=self._create_generation_config(use_tools=True)
            )
            
            logger.info(f"Received response from Gemini API")

            # Process response using common method
            process_result = self._process_response_with_functions(response, user_prompt, "initial_plan")
            
            # If we have function calls, generate a follow-up response
            if process_result["has_function_calls"] and process_result["function_calls"]:
                return self._generate_follow_up_response(process_result, start_time, input_tokens)
            
            # Return text parts if no function calls
            if process_result["text_parts"]:
                final_response = "\n".join(process_result["text_parts"])
                output_tokens = estimate_tokens(final_response)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Log metrics
                log_request("initial_plan", input_tokens, output_tokens, True)
                logger.info(f"Initial plan generated successfully in {execution_time:.2f}s")
                logger.info(f"Tokens - Input: {input_tokens}, Output: {output_tokens}")
                
                return final_response
            
            # Fallback if no content
            fallback_response = "I'm ready to help you plan your trip! Please provide more details about your destination and preferences."
            output_tokens = estimate_tokens(fallback_response)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log metrics for fallback
            log_request("initial_plan_fallback", input_tokens, output_tokens, True)
            logger.warning(f"Using fallback response after {execution_time:.2f}s")
            
            return fallback_response

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)
            
            # Log error metrics
            log_request("initial_plan", input_tokens, 0, False, error_msg)
            logger.error(f"Error generating initial plan after {execution_time:.2f}s: {e}")
            
            return f"I apologize, but I encountered an error while generating your trip plan. Please try again or contact support if the issue persists."


    def chat_response(self, chat_history: List[Dict[str, str]], user_message: str) -> str:
        logger.info(f"Processing chat message: '{user_message[:50]}{'...' if len(user_message) > 50 else ''}'")
        logger.debug(f"Chat history length: {len(chat_history)} messages")
        
        start_time = datetime.now()
        input_tokens = 0
        output_tokens = 0
        
        try:
            conversation_text = self._build_conversation_context(chat_history, user_message)
            input_tokens = estimate_tokens(conversation_text)  # Removed system prompt from token calculation
            
            logger.info(f"Built conversation context, estimated input tokens: {input_tokens} (excluding system prompt)")
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=conversation_text,
                config=self._create_generation_config(use_tools=True)
            )
            
            logger.info(f"Received chat response from Gemini API")
            
            # Process response using common method
            process_result = self._process_response_with_functions(response, conversation_text, "chat_response")
            
            # If we have function calls, generate a follow-up response
            if process_result["has_function_calls"] and process_result["function_calls"]:
                return self._generate_follow_up_response(process_result, start_time, input_tokens, chat_history, user_message)
            
            # Return text parts if no function calls
            if process_result["text_parts"]:
                final_response = "\n".join(process_result["text_parts"])
                output_tokens = estimate_tokens(final_response)
                execution_time = (datetime.now() - start_time).total_seconds()
                
                # Log metrics
                log_request("chat_response", input_tokens, output_tokens, True)
                logger.info(f"Chat response generated successfully in {execution_time:.2f}s")
                logger.info(f"Tokens - Input: {input_tokens}, Output: {output_tokens}")
                
                return final_response
            
            # Fallback if no content
            fallback_response = "I'm here to help with your trip planning. What would you like to know?"
            output_tokens = estimate_tokens(fallback_response)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log metrics for fallback
            log_request("chat_response_fallback", input_tokens, output_tokens, True)
            logger.warning(f"Using chat fallback response after {execution_time:.2f}s")
            
            return fallback_response
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_msg = str(e)
            
            # Log error metrics
            log_request("chat_response", input_tokens, 0, False, error_msg)
            logger.error(f"Error generating chat response after {execution_time:.2f}s: {e}")
            
            return f"I apologize, but I encountered an error while processing your request. Please try again."