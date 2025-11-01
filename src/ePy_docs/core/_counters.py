"""
Counter Manager
===============

Centralized counter management for document generation.
Provides a unified interface for managing table, figure, and note counters.
"""

from typing import Dict


# Define constants for counter types
TABLE_COUNTER = 'table'
FIGURE_COUNTER = 'figure'
NOTE_COUNTER = 'note'


class CounterManager:
    """
    Manages all counters used in document generation.
    
    Provides centralized counter management with methods to increment
    and retrieve counter values.
    """
    
    def __init__(self):
        """Initialize all counters to zero."""
        self._counters: Dict[str, int] = {
            TABLE_COUNTER: 0,
            FIGURE_COUNTER: 0,
            NOTE_COUNTER: 0
        }
    
    def _validate_counter_type(self, counter_type: str) -> None:
        """Validate the counter type to ensure it is recognized.

        Args:
            counter_type: The counter type to validate.

        Raises:
            ValueError: If the counter type is not recognized.
        """
        valid_types = {TABLE_COUNTER, FIGURE_COUNTER, NOTE_COUNTER}
        if counter_type not in valid_types:
            raise ValueError(f"Invalid counter type: {counter_type}. Valid types are: {', '.join(valid_types)}")

    def increment(self, counter_type: str) -> int:
        """
        Increment a counter and return the new value.
        
        Args:
            counter_type: Type of counter ('table', 'figure', or 'note')
            
        Returns:
            int: The new counter value
            
        Raises:
            ValueError: If counter_type is not recognized
        """
        self._validate_counter_type(counter_type)
        self._counters[counter_type] += 1
        return self._counters[counter_type]
    
    def get(self, counter_type: str) -> int:
        """
        Get the current value of a counter.
        
        Args:
            counter_type: Type of counter ('table', 'figure', or 'note')
            
        Returns:
            int: The current counter value
            
        Raises:
            ValueError: If counter_type is not recognized
        """
        self._validate_counter_type(counter_type)
        return self._counters[counter_type]
    
    def reset(self, counter_type: str = None):
        """
        Reset counters to zero.
        
        Args:
            counter_type: Specific counter to reset, or None to reset all
        """
        if counter_type is None:
            for key in self._counters:
                self._counters[key] = 0
        else:
            self._validate_counter_type(counter_type)
            self._counters[counter_type] = 0
    
    @property
    def table_counter(self) -> int:
        """Get the current table counter value."""
        return self.get(TABLE_COUNTER)
    
    @property
    def figure_counter(self) -> int:
        """Get the current figure counter value."""
        return self.get(FIGURE_COUNTER)
    
    @property
    def note_counter(self) -> int:
        """Get the current note counter value."""
        return self.get(NOTE_COUNTER)
