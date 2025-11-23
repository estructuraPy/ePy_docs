"""Text formatting utilities for ePy_docs.

SOLID-compliant module with specialized classes:
- FormatConfig: Configuration management with strict validation
- FormatValidator: Input validation and sanitization
- TextProcessor: Core text processing and wrapping
- SuperscriptFormatter: Specialized superscript handling  
- ContentGenerator: Document content generation utilities

Version: 4.0.0 - Zero hardcoding, fail-fast validation
"""

import re
import textwrap
from typing import Dict, Any, Optional, List
import pandas as pd


# ============================================================================
# CONFIGURATION AND VALIDATION
# ============================================================================

class FormatConfig:
    """Centralized format configuration management with strict validation."""
    
    def __init__(self):
        self._config = None
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get format configuration with strict validation.
        
        Returns:
            Complete format configuration dictionary
            
        Raises:
            ValueError: If format configuration cannot be loaded or is invalid
        """
        if self._config is None:
            from ePy_docs.core._config import get_config_section
            
            self._config = get_config_section('format')
            
            if not self._config:
                raise ValueError(
                    "Failed to load format configuration. Ensure format.epyson exists in config directory."
                )
            
            # Validate required sections
            required_sections = ['format_specific', 'shared_superscripts', 'text_wrapping', 'missing_value_indicators']
            missing = [sec for sec in required_sections if sec not in self._config]
            
            if missing:
                raise ValueError(
                    f"Missing required sections in format.epyson: {missing}. "
                    f"Configuration must define: {required_sections}"
                )
        
        return self._config
    
    def get_wrapping_config(self) -> Dict[str, Any]:
        """Get text wrapping configuration with strict validation.
        
        Returns:
            Text wrapping configuration dictionary
            
        Raises:
            ValueError: If text_wrapping section is missing or invalid
        """
        config = self.config
        
        if 'text_wrapping' not in config:
            raise ValueError("Missing 'text_wrapping' section in format.epyson")
        
        wrapping_config = config['text_wrapping']
        
        if 'max_chars_per_line' not in wrapping_config:
            raise ValueError("Missing 'max_chars_per_line' in text_wrapping configuration")
        
        return wrapping_config
    
    def get_missing_indicators(self) -> List[str]:
        """Get missing value indicators with strict validation.
        
        Returns:
            List of missing value indicator strings
            
        Raises:
            ValueError: If missing_value_indicators section is missing
        """
        config = self.config
        
        if 'missing_value_indicators' not in config:
            raise ValueError("Missing 'missing_value_indicators' section in format.epyson")
        
        return config['missing_value_indicators']
    
    def get_superscript_config(self, output_format: str) -> Dict[str, str]:
        """Get superscript configuration for given format with strict validation.
        
        Args:
            output_format: Target output format
            
        Returns:
            Superscript mapping dictionary
            
        Raises:
            ValueError: If output format is not supported or configuration is invalid
        """
        config = self.config
        
        if 'format_specific' not in config:
            raise ValueError("Missing 'format_specific' section in format.epyson")
        
        if output_format not in config['format_specific']:
            available_formats = list(config['format_specific'].keys())
            raise ValueError(
                f"Unsupported output format '{output_format}'. Available formats: {available_formats}"
            )
        
        return self._build_format_specific_config(config, output_format)
    
    def _build_format_specific_config(self, config: Dict, output_format: str) -> Dict[str, str]:
        """Build superscript configuration from shared superscripts with validation.
        
        Args:
            config: Complete format configuration
            output_format: Target format
            
        Returns:
            Built superscript configuration
            
        Raises:
            ValueError: If shared_superscripts section is missing or invalid
        """
        format_spec = config['format_specific'][output_format]
        superscript_config = {}
        
        # Validate shared_superscripts section exists
        if 'shared_superscripts' not in config:
            raise ValueError("Missing 'shared_superscripts' section in format.epyson")
        
        shared_superscripts = config['shared_superscripts']
        
        # Build from shared superscripts
        if 'extends' in format_spec:
            for category in format_spec['extends']:
                if category not in shared_superscripts:
                    available = list(shared_superscripts.keys())
                    raise ValueError(
                        f"Missing shared superscript category '{category}' for format '{output_format}'. "
                        f"Available categories: {available}"
                    )
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


class FormatValidator:
    """Input validation and sanitization for formatting operations."""
    
    @staticmethod
    def sanitize_text(text: Any) -> str:
        """Convert input to string and sanitize."""
        if text is None or pd.isna(text):
            return ""
        
        # Handle pandas Series (defensive programming)
        if hasattr(text, 'iloc'):
            text = text.iloc[0] if len(text) > 0 else ""
        
        return str(text).strip()
    
    @staticmethod
    def is_missing_value(text: str, missing_indicators: List[str]) -> bool:
        """Check if text represents a missing value."""
        text_lower = text.lower()
        return text_lower in missing_indicators
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> None:
        """Validate DataFrame input."""
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
        
        if df.empty:
            raise ValueError("DataFrame cannot be empty")


# ============================================================================
# CORE TEXT PROCESSING
# ============================================================================

class TextProcessor:
    """Core text processing and wrapping functionality."""
    
    def __init__(self, config: FormatConfig):
        self.config = config
    
    def wrap_text(self, text: str, max_width: Optional[int] = None) -> str:
        """Wrap text according to configuration with strict validation.
        
        Args:
            text: Text to wrap
            max_width: Maximum width override (optional)
            
        Returns:
            Wrapped text with preserved formatting
        """
        text = FormatValidator.sanitize_text(text)
        if not text:
            return text
        
        wrapping_config = self.config.get_wrapping_config()
        
        # Use max_width override or configuration value
        if max_width is None:
            if 'max_chars_per_line' not in wrapping_config:
                raise ValueError("Missing 'max_chars_per_line' in text_wrapping configuration")
            max_width = wrapping_config['max_chars_per_line']
        
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
    
    def clean_cell_value(self, value: Any) -> str:
        """Clean and format cell values with missing value handling.
        
        Args:
            value: Cell value to clean
            
        Returns:
            Cleaned string or missing indicator
        """
        text = FormatValidator.sanitize_text(value)
        
        if not text or FormatValidator.is_missing_value(text, self.config.get_missing_indicators()):
            return "---"
        
        return self.wrap_text(text)
    
    def process_dataframe_content(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process DataFrame content with text wrapping and cleaning.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with processed content
            
        Raises:
            TypeError: If input is not a DataFrame
            ValueError: If DataFrame is empty
        """
        FormatValidator.validate_dataframe(df)
        
        df_processed = df.copy()
        
        # Process cell content
        for col in df_processed.columns:
            df_processed[col] = df_processed[col].apply(self.clean_cell_value)
        
        # Process column headers
        column_mapping = {}
        for col in df_processed.columns:
            wrapped_col_name = self.wrap_text(str(col))
            if wrapped_col_name != str(col):
                column_mapping[col] = wrapped_col_name
        
        if column_mapping:
            df_processed.rename(columns=column_mapping, inplace=True)
        
        return df_processed


# ============================================================================
# SPECIALIZED FORMATTING
# ============================================================================

class SuperscriptFormatter:
    """Specialized superscript handling with caching."""
    
    def __init__(self, config: FormatConfig):
        self.config = config
        self._cache = {}
    
    def format_superscripts(self, text: str, output_format: str = 'matplotlib') -> str:
        """Format superscripts using cached configuration.
        
        Args:
            text: Text to format
            output_format: Target output format
            
        Returns:
            Text with formatted superscripts
            
        Raises:
            ValueError: If output format is not supported
        """
        text = FormatValidator.sanitize_text(text)
        if not text:
            return text
        
        # Use cached configuration
        if output_format not in self._cache:
            self._cache[output_format] = self.config.get_superscript_config(output_format)
        
        superscript_config = self._cache[output_format]
        
        # Apply mappings
        result_text = text
        for pattern, replacement in superscript_config.items():
            result_text = result_text.replace(pattern, replacement)
        
        return result_text
    
    def format_table_cell_text(self, text: str, output_format: str = 'matplotlib') -> str:
        """Format table cell text with superscripts and citations.
        
        Args:
            text: Raw cell text
            output_format: Target format
            
        Returns:
            Formatted text ready for rendering
        """
        text = FormatValidator.sanitize_text(text)
        if not text:
            return text
        
        # Process superscripts
        formatted_text = self.format_superscripts(text, output_format)
        
        # Process citations for matplotlib tables
        if output_format == 'matplotlib':
            formatted_text = re.sub(r'\[@([^\]]+)\]', r'(\1)', formatted_text)
        
        return formatted_text


# ============================================================================
# CONTENT GENERATION
# ============================================================================

class ContentGenerator:
    """Document content generation utilities."""
    
    @staticmethod
    def create_equation(latex_code: str, caption: str = None, label: str = None) -> str:
        """Generate display equation markdown.
        
        Args:
            latex_code: LaTeX equation code
            caption: Optional equation caption
            label: Optional equation label for referencing
            
        Returns:
            Complete markdown content for the equation
        """
        # Clean up double backslashes
        cleaned_latex = latex_code.replace('\\\\', '\\')
        
        if label:
            eq_content = f"$${cleaned_latex}$$ {{#{label}}}"
        else:
            eq_content = f"$${cleaned_latex}$$"
        
        markdown_parts = []
        if caption:
            markdown_parts.append(f"**{caption}**\n")
        markdown_parts.append(eq_content)
        
        return "\n".join(markdown_parts) + "\n\n"
    
    @staticmethod
    def create_inline_equation(latex_code: str) -> str:
        """Generate inline equation markdown.
        
        Args:
            latex_code: LaTeX equation code for inline display
            
        Returns:
            Inline equation markdown
        """
        # Clean up double backslashes
        cleaned_latex = latex_code.replace('\\\\', '\\')
        return f"${cleaned_latex}$"
    
    @staticmethod
    def create_reference(ref_type: str, label: str, custom_text: str = None) -> str:
        """Generate reference markdown.
        
        Args:
            ref_type: Type of reference (figure, table, equation, etc.)
            label: Reference label identifier (e.g., 'results', 'stress-plot', 'einstein')
            custom_text: Optional custom reference text
            
        Returns:
            Reference markdown
        """
        if custom_text:
            return f"[{custom_text}](#{label})"
        return f"[@{label}]"
    
    @staticmethod
    def create_citation(citation_key: str, page: str = None) -> str:
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
    
    @staticmethod
    def create_page_header(content: str) -> str:
        """Generate page header content.
        
        The header content will be stored and applied to the document header
        during PDF generation.
        
        Args:
            content: Text content for the header (supports markdown formatting)
            
        Returns:
            Empty string (header is stored separately for PDF generation)
        """
        return ""  # Header stored in document instance, not in content buffer
    
    @staticmethod
    def create_page_footer(content: str) -> str:
        """Generate page footer content.
        
        The footer content will be stored and applied to the document footer
        during PDF generation.
        
        Args:
            content: Text content for the footer (supports markdown formatting)
            
        Returns:
            Empty string (footer is stored separately for PDF generation)
        """
        return ""  # Footer stored in document instance, not in content buffer

# ============================================================================
# TABLE TEXT WRAPPING
# ============================================================================

class TableTextWrapper:
    """Specialized text wrapping for table cells."""
    
    @staticmethod
    def wrap_cell_content(text: str, max_width: int = 12) -> str:
        """Wrap text content with reasonable line breaks."""
        if len(text) <= max_width:
            return text
        
        text = text.strip()
        words = text.split()
        if len(words) > 1:
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                if len(test_line) <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    
                    if len(word) > max_width + 2:
                        for i in range(0, len(word), max_width):
                            chunk = word[i:i + max_width]
                            lines.append(chunk)
                        current_line = ""
                    else:
                        current_line = word
            
            if current_line:
                lines.append(current_line)
            
            return "\n".join(lines)
        
        if len(text) > max_width + 3:
            lines = []
            for i in range(0, len(text), max_width):
                lines.append(text[i:i + max_width])
            return "\n".join(lines)
        
        return text
