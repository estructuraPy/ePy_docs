"""Text formatting utilities for ePy_docs.

Provides text formatting, wrapping, superscripts, and content generation
utilities with centralized configuration management.
"""

import re
import textwrap
from typing import Dict, Any, Optional
import pandas as pd


class TextFormatter:
    """Unified text formatting engine with cached configuration."""
    
    def __init__(self):
        self._config = None
        self._superscript_cache = {}
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get format configuration with caching."""
        if self._config is None:
            from ePy_docs.core._config import get_config_section, clear_global_cache
            # Load from 'format' section which contains merged assets data
            # (shared_superscripts and format_specific are merged from assets.epyson)
            self._config = get_config_section('format')
            
            # Validate that required keys exist, if not clear cache and reload
            if 'format_specific' not in self._config or 'shared_superscripts' not in self._config:
                clear_global_cache()
                self._config = get_config_section('format')
        return self._config
    
    def wrap_text(self, text: str, layout_style: str) -> str:
        """Wrap text according to layout configuration."""
        if not isinstance(text, str):
            text = str(text)
        
        # Get max width from config
        text_wrapping = self.config.get('text_wrapping', {})
        max_width = text_wrapping.get('max_chars_per_line', 80)
        
        if len(text) <= max_width:
            return text
        
        # Handle existing line breaks
        if '\n' in text:
            lines = text.split('\n')
            wrapped_lines = []
            for line in lines:
                if len(line) <= max_width:
                    wrapped_lines.append(line)
                else:
                    wrapped_lines.extend(textwrap.wrap(line, width=max_width))
            return '\n'.join(wrapped_lines)
        
        # Wrap text using textwrap
        wrapped_lines = textwrap.wrap(text, width=max_width)
        return '\n'.join(wrapped_lines)
    
    def format_superscripts(self, text: str, output_format: str = 'matplotlib') -> str:
        """Format superscripts using cached configuration."""
        cache_key = output_format
        
        if cache_key not in self._superscript_cache:
            self._superscript_cache[cache_key] = self._build_superscript_config(output_format)
        
        superscript_config = self._superscript_cache[cache_key]
        
        # Apply mappings
        result_text = text
        for pattern, replacement in superscript_config.items():
            result_text = result_text.replace(pattern, replacement)
        
        return result_text
    
    def _build_superscript_config(self, output_format: str) -> Dict[str, str]:
        """Build superscript configuration for given format."""
        config = self.config
        
        # Check format_specific section
        if 'format_specific' in config and output_format in config['format_specific']:
            format_spec = config['format_specific'][output_format]
            superscript_config = {}
            
            # Build from shared superscripts
            if 'extends' in format_spec:
                shared_superscripts = config.get('shared_superscripts', {})
                for category in format_spec['extends']:
                    if category in shared_superscripts:
                        superscript_config.update(shared_superscripts[category])
            
            # Apply prefix/suffix if present
            if 'prefix' in format_spec and 'suffix' in format_spec:
                prefix, suffix = format_spec['prefix'], format_spec['suffix']
                formatted_config = {}
                for pattern, value in superscript_config.items():
                    if pattern.startswith('^'):
                        content = pattern[1:]  # Remove ^
                        formatted_config[pattern] = f"{prefix}{content}{suffix}"
                    else:
                        formatted_config[pattern] = value
                superscript_config = formatted_config
            
            return superscript_config
        
        # Fallback to old structure
        elif output_format in config:
            format_config = config[output_format]
            if 'superscripts' in format_config:
                return format_config['superscripts']
        
        raise ValueError(f"Output format '{output_format}' not supported")
    
    def clean_cell_value(self, value, layout_style: str) -> str:
        """Clean and format cell values."""
        if pd.isna(value):
            return "---"
        
        value_str = str(value).strip().lower()
        
        # Get missing indicators from config
        missing_indicators = self.config.get('missing_value_indicators', 
                                          ['nan', 'none', 'null', '', 'n/a', 'na'])
        
        if value_str in missing_indicators:
            return "---"
        
        return self.wrap_text(str(value), layout_style)
    
    def prepare_dataframe_with_wrapping(self, df: pd.DataFrame, layout_style: str) -> pd.DataFrame:
        """Prepare DataFrame with text wrapping applied."""
        df_wrapped = df.copy()
        
        # Wrap cell content
        for col in df_wrapped.columns:
            df_wrapped[col] = df_wrapped[col].apply(
                lambda x: self.clean_cell_value(x, layout_style)
            )
        
        # Wrap column headers
        column_mapping = {}
        for col in df_wrapped.columns:
            wrapped_col_name = self.wrap_text(str(col), layout_style)
            if wrapped_col_name != str(col):
                column_mapping[col] = wrapped_col_name
        
        if column_mapping:
            df_wrapped.rename(columns=column_mapping, inplace=True)
        
        return df_wrapped
    
    def format_table_cell_text(self, text: str, output_format: str = 'matplotlib') -> str:
        """Format table cell text with superscripts and citations."""
        if not isinstance(text, str):
            text = str(text)
        
        # Process superscripts
        formatted_text = self.format_superscripts(text, output_format)
        
        # Process citations for matplotlib tables
        if output_format == 'matplotlib':
            formatted_text = re.sub(r'\[@([^\]]+)\]', r'(\1)', formatted_text)
        
        return formatted_text


# Global formatter instance
_formatter = TextFormatter()

# Content generation utilities
def add_equation_to_content(latex_code: str, caption: str = None, label: str = None) -> str:
    """Generate display equation markdown."""
    if label:
        eq_content = f"$${latex_code}$$ {{#{label}}}"
    else:
        eq_content = f"$${latex_code}$$"
    
    markdown_parts = []
    if caption:
        markdown_parts.append(f"**{caption}**\n")
    markdown_parts.append(eq_content)
    
    return "\n".join(markdown_parts) + "\n\n"

def add_inline_equation_to_content(latex_code: str) -> str:
    """Generate inline equation markdown."""
    return f"${latex_code}$"

def add_reference_to_content(ref_type: str, ref_id: str, custom_text: str = None) -> str:
    """Generate reference markdown."""
    if custom_text:
        return f"[{custom_text}](#{ref_id})"
    return f"[@{ref_id}]"

def add_citation_to_content(citation_key: str, page: str = None) -> str:
    """Generate citation markdown."""
    if page:
        return f"[@{citation_key}, p. {page}]"
    return f"[@{citation_key}]"

# Public API functions (for backward compatibility)
def get_format_config() -> Dict[Any, Any]:
    """Load format configuration."""
    return _formatter.config

def wrap_text(text: str, layout_style: str) -> str:
    """Wrap text according to layout configuration."""
    return _formatter.wrap_text(text, layout_style)

def format_superscripts(text: str, output_format: str = 'matplotlib') -> str:
    """Format superscripts using configuration."""
    return _formatter.format_superscripts(text, output_format)

def prepare_dataframe_with_wrapping(df: pd.DataFrame, layout_style: str) -> pd.DataFrame:
    """Prepare DataFrame with text wrapping."""
    return _formatter.prepare_dataframe_with_wrapping(df, layout_style)

def format_table_cell_text(text: str, output_format: str = 'matplotlib') -> str:
    """Format table cell text."""
    return _formatter.format_table_cell_text(text, output_format)

def get_wrapping_config(layout_style: str) -> Dict[str, Any]:
    """Get text wrapping configuration."""
    return _formatter.config.get('text_wrapping', {})

def add_equation_to_content(latex_code: str, caption: str = None, label: str = None) -> str:
    """Generate display equation markdown.
    
    Args:
        latex_code: LaTeX equation code
        caption: Optional equation caption
        label: Optional equation label for referencing
        
    Returns:
        Complete markdown content for the equation
    """
    if label:
        eq_content = f"$${latex_code}$$ {{#{label}}}"
    else:
        eq_content = f"$${latex_code}$$"
    
    markdown_parts = []
    
    if caption:
        markdown_parts.append(f"**{caption}**\n")
    
    markdown_parts.append(eq_content)
    
    return "\n".join(markdown_parts) + "\n\n"

def add_inline_equation_to_content(latex_code: str) -> str:
    """Generate inline equation markdown.
    
    Args:
        latex_code: LaTeX equation code for inline display
        
    Returns:
        Inline equation markdown
    """
    return f"${latex_code}$"

def add_reference_to_content(ref_type: str, ref_id: str, custom_text: str = None) -> str:
    """Generate reference markdown.
    
    Args:
        ref_type: Type of reference (figure, table, equation, etc.)
        ref_id: Reference identifier
        custom_text: Optional custom reference text
        
    Returns:
        Reference markdown
    """
    if custom_text:
        return f"[{custom_text}](#{ref_id})"
    return f"[@{ref_id}]"

def add_citation_to_content(citation_key: str, page: str = None) -> str:
    """Generate citation markdown.
    
    Args:
        citation_key: Citation key from bibliography
        page: Optional page number
        
    Returns:
        Citation markdown
    """
    if page:
        return f"[@{citation_key}, p. {page}]"
    return f"[@{citation_key}]"


def format_table_cell_text(text: str, output_format: str = 'matplotlib') -> str:
    """Format table cell text for proper rendering of superscripts and citations.
    
    Processes text to render:
    - Superscripts (e.g., m², m³, x¹, etc.)
    - Citations ([@key])
    
    NOTE: LaTeX expressions ($...$) are NOT rendered in tables to preserve readability.
    
    Args:
        text: Raw cell text
        output_format: Target format ('matplotlib', 'html', 'latex')
        
    Returns:
        Formatted text ready for rendering
    """
    import re
    
    if not isinstance(text, str):
        text = str(text)
    
    # Step 1: Process superscripts using format_superscripts
    formatted_text = format_superscripts(text, output_format)
    
    # Step 2: LaTeX is NOT rendered in tables - keep as plain text
    # This preserves readability and prevents rendering issues
    # Users can see the LaTeX code directly in the table
    
    # Step 3: Process citations [@key] - convert to plain text for tables
    if output_format == 'matplotlib':
        # For matplotlib tables, convert citations to plain text
        formatted_text = re.sub(r'\[@([^\]]+)\]', r'(\1)', formatted_text)
    
    return formatted_text
