"""
Counter Manager
===============

Centralized counter management for document generation.
Provides a unified interface for managing table, figure, and note counters.
"""

from typing import Dict


class CounterManager:
    """
    Manages all counters used in document generation.
    
    Provides centralized counter management with methods to increment
    and retrieve counter values.
    """
    
    def __init__(self):
        """Initialize all counters to zero."""
        self._counters: Dict[str, int] = {
            'table': 0,
            'figure': 0,
            'note': 0
        }
    
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
        if counter_type not in self._counters:
            raise ValueError(f"Unknown counter type: {counter_type}")
        
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
        if counter_type not in self._counters:
            raise ValueError(f"Unknown counter type: {counter_type}")
        
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
        elif counter_type in self._counters:
            self._counters[counter_type] = 0
        else:
            raise ValueError(f"Unknown counter type: {counter_type}")
    
    @property
    def table_counter(self) -> int:
        """Get the current table counter value."""
        return self.get('table')
    
    @property
    def figure_counter(self) -> int:
        """Get the current figure counter value."""
        return self.get('figure')
    
    @property
    def note_counter(self) -> int:
        """Get the current note counter value."""
        return self.get('note')