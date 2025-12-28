"""
Utility functions for FMC API automation.
"""

import logging
import time
from functools import wraps
from typing import Callable, Any
import colorlog


def setup_logging(log_level: str = 'INFO') -> logging.Logger:
    """
    Set up colored logging with proper formatting.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    
    logger = colorlog.getLogger('FMC_Automation')
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    return logger


def rate_limit(max_per_minute: int = 100):
    """
    Decorator to enforce rate limiting on API calls.
    
    Args:
        max_per_minute: Maximum number of calls allowed per minute
    """
    min_interval = 60.0 / max_per_minute
    last_called = [0.0]
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        
        return wrapper
    return decorator


def sanitize_name(name: str) -> str:
    """
    Sanitize object names for FMC API compatibility.
    Removes special characters and ensures valid naming.
    
    Args:
        name: Original name
    
    Returns:
        Sanitized name
    """
    # Replace spaces with underscores
    sanitized = name.replace(' ', '_')
    # Remove special characters except underscore and hyphen
    sanitized = ''.join(c for c in sanitized if c.isalnum() or c in '_-')
    return sanitized


def chunk_list(lst: list, chunk_size: int) -> list:
    """
    Split a list into chunks of specified size.
    Useful for bulk operations with API limits.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
    
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def format_api_error(response) -> str:
    """
    Format API error response for better readability.
    
    Args:
        response: Response object from requests
    
    Returns:
        Formatted error message
    """
    try:
        error_data = response.json()
        error_msg = f"Status: {response.status_code}\n"
        
        if 'error' in error_data:
            error_msg += f"Error: {error_data['error'].get('messages', [])}\n"
        elif 'items' in error_data:
            for item in error_data['items']:
                if 'error' in item:
                    error_msg += f"Error: {item['error']}\n"
        else:
            error_msg += f"Response: {error_data}\n"
        
        return error_msg
    except:
        return f"Status: {response.status_code}, Response: {response.text}"


def validate_ip_address(ip: str) -> bool:
    """
    Validate IPv4 address format.
    
    Args:
        ip: IP address string
    
    Returns:
        True if valid, False otherwise
    """
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except (ValueError, TypeError):
        return False


def validate_ip_network(network: str) -> bool:
    """
    Validate IPv4 network in CIDR notation.
    
    Args:
        network: Network string (e.g., '192.168.1.0/24')
    
    Returns:
        True if valid, False otherwise
    """
    try:
        ip, prefix = network.split('/')
        if not validate_ip_address(ip):
            return False
        
        prefix_len = int(prefix)
        return 0 <= prefix_len <= 32
    except (ValueError, AttributeError):
        return False
