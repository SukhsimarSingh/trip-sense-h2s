"""
Logging configuration and metrics tracking for the AI Trip Planner.
"""

import logging
from datetime import datetime
from typing import Dict, List
import streamlit as st


def setup_logging():
    """Configure logging for the application."""
    import sys
    import os
    
    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Create console handler (stdout for Cloud Run/Cloud Logging)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    # Add file handler only if not in Cloud Run or if writable
    # Cloud Run sets K_SERVICE environment variable
    if not os.getenv('K_SERVICE'):
        try:
            file_handler = logging.FileHandler('trip_planner.log', encoding='utf-8')
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except (PermissionError, OSError) as e:
            # If file logging fails, just use console (Cloud Run will capture it)
            console_handler.stream.write(f"Note: File logging disabled ({e})\n")
    
    return logging.getLogger(__name__)


# Initialize logger
logger = setup_logging()


def initialize_metrics():
    """Initialize metrics tracking in session state."""
    if "metrics" not in st.session_state:
        st.session_state.metrics = {
            "total_requests": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost_estimate": 0.0,
            "requests_log": [],
            "session_start": datetime.now().isoformat()
        }


def estimate_tokens(text: str) -> int:
    """Rough estimation of tokens (1 token ≈ 4 characters for English)."""
    return len(text) // 4


def calculate_cost_estimate(input_tokens: int, output_tokens: int) -> float:
    """Calculate estimated cost based on token usage."""
    # Input: $0.15 per 1M tokens, Output: $0.60 per 1M tokens
    input_cost = (input_tokens / 1_000_000) * 0.15
    output_cost = (output_tokens / 1_000_000) * 0.60
    return input_cost + output_cost


def log_request(request_type: str, input_tokens: int, output_tokens: int, success: bool, error_msg: str = None):
    """Log API request with metrics."""
    timestamp = datetime.now().isoformat()
    cost = calculate_cost_estimate(input_tokens, output_tokens)
    
    # Update session metrics
    st.session_state.metrics["total_requests"] += 1
    st.session_state.metrics["total_input_tokens"] += input_tokens
    st.session_state.metrics["total_output_tokens"] += output_tokens
    st.session_state.metrics["total_cost_estimate"] += cost
    
    # Log entry
    log_entry = {
        "timestamp": timestamp,
        "type": request_type,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_estimate": cost,
        "success": success,
        "error": error_msg
    }
    
    st.session_state.metrics["requests_log"].append(log_entry)
    
    # File logging
    logger.info(f"API Request - Type: {request_type}, Input Tokens: {input_tokens}, "
                f"Output Tokens: {output_tokens}, Cost: ${cost:.6f}, Success: {success}")
    
    if error_msg:
        logger.error(f"API Error: {error_msg}")
