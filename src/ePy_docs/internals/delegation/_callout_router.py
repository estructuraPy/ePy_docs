"""
Callout Routing Logic
=====================

Handles routing of callout types to appropriate methods.
This module contains the business logic for unified callout handling.
"""

from typing import Callable, Dict


def route_callout_to_method(callout_type: str, method_map: Dict[str, Callable]) -> Callable:
    """
    Route a callout type to the appropriate method.
    
    Args:
        callout_type: Type of callout (note, tip, warning, etc.)
        method_map: Dictionary mapping callout types to methods
        
    Returns:
        Callable: The method to call for this callout type
    """
    # Normalize type to lowercase
    normalized_type = callout_type.lower()
    
    # Default to 'note' method if type not recognized
    return method_map.get(normalized_type, method_map.get('note'))


def get_callout_type_methods() -> list:
    """
    Get the list of valid callout type method names.
    
    Returns:
        list: Method names for callout types
    """
    return [
        'note', 'tip', 'warning', 'caution', 'important',
        'error', 'success', 'information', 'recommendation',
        'advice', 'risk'
    ]
