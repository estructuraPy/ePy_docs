"""
Column width calculation system for multi-column documents.

Handles width calculations for tables and figures based on:
- Document type (paper, report, book)
- Number of columns in the layout
- Requested column span (columns parameter)
"""

from typing import Union, List, Dict, Any, Tuple


class ColumnWidthCalculator:
    """Calculate widths for figures and tables in multi-column layouts."""
    
    def __init__(self):
        """Initialize with column width configurations."""
        self._config_cache = None
    
    def _get_config(self) -> Dict[str, Any]:
        """Load document types configuration with caching."""
        if self._config_cache is None:
            from ePy_docs.core._config import get_config_section
            self._config_cache = get_config_section('document_types')
        return self._config_cache
    
    def get_document_type_info(self, document_type: str) -> Dict[str, Any]:
        """Get configuration for a specific document type.
        
        Args:
            document_type: Type of document ('paper', 'report', 'book')
            
        Returns:
            Dictionary with document type configuration
            
        Raises:
            ValueError: If document_type is not valid
        """
        config = self._get_config()
        doc_types = config.get('document_types', {})
        
        if document_type not in doc_types:
            valid_types = list(doc_types.keys())
            raise ValueError(
                f"Invalid document_type '{document_type}'. "
                f"Valid types: {valid_types}"
            )
        
        return doc_types[document_type]
    
    def get_width_config(self, document_type: str) -> Dict[str, Any]:
        """Get width configuration based on document type margins.
        
        Args:
            document_type: Type of document ('paper', 'report', 'book')
            
        Returns:
            Dictionary with column width configurations
        """
        config = self._get_config()
        width_configs = config.get('column_widths', {})
        
        # Map document types to width configurations
        if document_type == 'book':
            return width_configs.get('letter_book_margins', {})
        else:  # paper, report
            return width_configs.get('letter_1in_margins', {})
    
    def calculate_width(self, 
                       document_type: str,
                       layout_columns: int,
                       requested_columns: Union[float, List[float], None] = None) -> float:
        """Calculate width in inches for a table or figure.
        
        Args:
            document_type: Type of document ('paper', 'report', 'book')
            layout_columns: Number of columns in the document layout (1, 2, or 3)
            requested_columns: Width specification:
                - None: Use single column width
                - float: Number of columns to span (e.g., 1.0, 1.5, 2.0)
                - List[float]: Specific widths in inches
                
        Returns:
            Width in inches
            
        Examples:
            >>> calc = ColumnWidthCalculator()
            >>> # Single column in 2-column layout
            >>> calc.calculate_width('paper', layout_columns=2, requested_columns=1.0)
            3.1
            >>> # Two columns in 2-column layout (full width)
            >>> calc.calculate_width('paper', layout_columns=2, requested_columns=2.0)
            6.5
            >>> # 1.5 columns in 2-column layout
            >>> calc.calculate_width('paper', layout_columns=2, requested_columns=1.5)
            4.75
        """
        width_config = self.get_width_config(document_type)
        
        # If requested_columns is a list, return first value (for split tables)
        if isinstance(requested_columns, list):
            return requested_columns[0] if requested_columns else 6.5
        
        # Default to single column if not specified
        if requested_columns is None:
            requested_columns = 1.0
        
        # Get column configuration
        col_key = f"{layout_columns}_column{'s' if layout_columns > 1 else ''}"
        col_config = width_config.get(col_key, {})
        
        if not col_config:
            # Fallback to total width
            return width_config.get('total_width', 6.5)
        
        single_width = col_config.get('single', 6.5)
        gap = col_config.get('gap', 0.3)
        
        # Calculate width based on requested columns
        if requested_columns == int(requested_columns):
            # Exact number of columns
            if requested_columns == 1:
                return single_width
            elif requested_columns == 2:
                return col_config.get('double', single_width * 2 + gap)
            elif requested_columns == 3:
                return col_config.get('triple', single_width * 3 + gap * 2)
        else:
            # Fractional columns (e.g., 1.5 columns)
            full_columns = int(requested_columns)
            fraction = requested_columns - full_columns
            
            base_width = full_columns * single_width + (full_columns - 1) * gap
            extra_width = fraction * (single_width + gap)
            
            return base_width + extra_width
        
        return single_width
    
    def get_width_string(self, width_inches: float) -> str:
        """Convert width in inches to string format for markdown.
        
        Args:
            width_inches: Width in inches
            
        Returns:
            String like "6.5in" or "3.1in"
        """
        return f"{width_inches:.2f}in".rstrip('0').rstrip('.')
    
    def validate_columns(self, 
                        document_type: str,
                        layout_columns: int,
                        requested_columns: Union[float, List[float], None]) -> None:
        """Validate that requested column span is valid.
        
        Args:
            document_type: Type of document
            layout_columns: Number of columns in layout
            requested_columns: Requested column span
            
        Raises:
            ValueError: If requested columns exceed layout columns
        """
        if requested_columns is None:
            return
        
        if isinstance(requested_columns, list):
            return  # Custom widths, no validation needed
        
        if requested_columns > layout_columns:
            raise ValueError(
                f"Requested {requested_columns} columns but layout only has "
                f"{layout_columns} columns for document_type '{document_type}'"
            )


# Global instance
_calculator = ColumnWidthCalculator()


def calculate_content_width(document_type: str = 'report',
                            layout_columns: int = 1,
                            columns: Union[float, List[float], None] = None) -> float:
    """Calculate width for content (tables, figures).
    
    This is the main entry point for width calculations.
    
    Args:
        document_type: Type of document ('paper', 'report', 'book')
        layout_columns: Number of columns in the document layout
        columns: Column span specification
        
    Returns:
        Width in inches
    """
    return _calculator.calculate_width(document_type, layout_columns, columns)


def get_width_string(width_inches: float) -> str:
    """Convert width to markdown string format.
    
    Args:
        width_inches: Width in inches
        
    Returns:
        String like "6.5in"
    """
    return _calculator.get_width_string(width_inches)


def validate_columns_parameter(document_type: str,
                               layout_columns: int,
                               columns: Union[float, List[float], None]) -> None:
    """Validate columns parameter.
    
    Args:
        document_type: Type of document
        layout_columns: Number of columns in layout
        columns: Requested column span
        
    Raises:
        ValueError: If invalid
    """
    _calculator.validate_columns(document_type, layout_columns, columns)
