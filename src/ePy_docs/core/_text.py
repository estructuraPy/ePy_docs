"""
TEXT Module - Typography and text formatting

Configuration: Centralized cache via _load_cached_files
Styling: Organization by layout_styles
Compatibility: No backward compatibility, no fallbacks
"""

from typing import Dict, Any, Optional, Union, List
import re

def get_text_config(layout_style: Optional[str] = None) -> Dict[str, Any]:
    """Get text configuration from centralized config.
    
    Args:
        layout_style: Optional layout style name to load specific configuration
        
    Returns:
        Text configuration dictionary
    """
    from ePy_docs.core._config import get_config_section
    return get_config_section('text', layout_name=layout_style)


def add_header_to_content(text: str, level: int = 1, color: Optional[str] = None, 
                         document_type: Optional[str] = None) -> str:
    """Generate header markdown.
    
    Args:
        text: Header text
        level: Header level (1-6)
        color: Optional color (ignored in pure markdown)
        document_type: Document type ('report', 'book', 'paper', etc.)
        
    Returns:
        Markdown header content with {.unnumbered} for reports
    """
    if level < 1 or level > 6:
        level = 1
    
    header_prefix = "#" * level
    
    # Add {.unnumbered} for reports to avoid chapter numbering
    # Books and other types should keep numbering
    if document_type == 'report':
        return f"\n\n{header_prefix} {text} {{.unnumbered}}\n\n"
    else:
        return f"\n\n{header_prefix} {text}\n\n"


def add_h1_to_content(text: str, color: Optional[str] = None, document_type: Optional[str] = None) -> str:
    """Generate H1 header markdown."""
    return add_header_to_content(text, 1, color, document_type)


def add_h2_to_content(text: str, color: Optional[str] = None, document_type: Optional[str] = None) -> str:
    """Generate H2 header markdown."""
    return add_header_to_content(text, 2, color, document_type)


def add_h3_to_content(text: str, add_newline: bool = True, color: Optional[str] = None, 
                     document_type: Optional[str] = None) -> str:
    """Generate H3 header markdown."""
    unnumbered = " {.unnumbered}" if document_type == 'report' else ""
    content = f"\n\n### {text}{unnumbered}"
    if add_newline:
        content += "\n\n"
    else:
        content += "\n"
    return content


def add_text_to_content(content: str) -> str:
    """Generate text content with mathematical notation.
    
    Args:
        content: Text content
        
    Returns:
        Processed markdown content
    """
    if not isinstance(content, str):
        content = str(content)
    
    processed_content = content
    
    # Process mathematical notation using FORMAT module
    try:
        from ePy_docs.core._format import SuperscriptFormatter, FormatConfig
        
        formatter = SuperscriptFormatter(FormatConfig())
        
        # First, process ${variable} patterns
        def process_math_variable(match):
            variable_content = match.group(1)
            # For variables in math expressions, just clean the variable name
            return f"${variable_content}$"
        
        # Process ${variable} patterns
        processed_content = re.sub(r'\$\{([^}]+)\}', process_math_variable, processed_content)
        
        # Apply superscript formatting only to text OUTSIDE of LaTeX equations
        parts = re.split(r'(\$[^$]*\$)', processed_content)
        
        formatted_parts = []
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Even indices are regular text
                formatted_part = formatter.format_superscripts(part, 'html')
                formatted_parts.append(formatted_part)
            else:  # Odd indices are LaTeX equations - preserve them exactly
                formatted_parts.append(part)
        
        processed_content = ''.join(formatted_parts)
        
    except Exception as e:
        # If mathematical processing fails, continue without it
        pass
    
    # Apply bullet conversion
    processed_content = processed_content.replace('• ', '- ')
    
    # Preserve line breaks and add proper spacing
    if '\n' in processed_content:
        return f"{processed_content}\n\n"
    else:
        return f"{processed_content}\n\n"


def add_content_to_buffer(content: str) -> str:
    """Add plain content preserving original formatting.
    
    Args:
        content: Content to add
        
    Returns:
        Content as-is for buffer appending
    """
    return content if content else ""


def process_text_content(text: str) -> str:
    """Centralized text processing for consistent markdown.
    
    Args:
        text: Input text
        
    Returns:
        Processed text with consistent formatting
    """
    if not text:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
        
    result = text.strip()
    
    # Process mathematical notation
    try:
        from ePy_docs.core._format import SuperscriptFormatter, FormatConfig
        
        formatter = SuperscriptFormatter(FormatConfig())
        
        def process_math_variable(match):
            variable_content = match.group(1)
            formatted_content = formatter.format_superscripts(variable_content, 'html')
            return f"${formatted_content}$"
        
        # Process ${variable} patterns
        result = re.sub(r'\$\{([^}]+)\}', process_math_variable, result)
        
        # Apply general superscript processing
        result = formatter.format_superscripts(result, 'html')
    except Exception:
        pass
    
    # Enhanced header processing
    for i in range(6, 0, -1):
        header_pattern = r'(^|\n)#{' + str(i) + r'}\s+(.+?)(\n|$)'
        replacement = r'\1' + '#' * i + r' \2\n\n'
        result = re.sub(header_pattern, replacement, result)
    
    # Preserve image syntax with better spacing
    result = re.sub(r'([^\n])(!\[.*?\]\(.*?\)(\s*\{[^}]*\})?)', r'\1\n\n\2', result)
    result = re.sub(r'(!\[.*?\]\(.*?\)(\s*\{[^}]*\})?)([^\n])', r'\1\n\n\3', result)
    
    # Normalize line endings
    result = re.sub(r'\r\n', '\n', result)
    
    # Clean up multiple blank lines
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    # Clean trailing whitespace
    result = re.sub(r'[ \t]+$', '', result, flags=re.MULTILINE)
    
    return result if result.strip() else result.strip()


def format_list(items: list, ordered: bool = False) -> str:
    """
    Format a list as markdown (ordered or unordered).
    
    Args:
        items: List of strings to format
        ordered: If True, creates numbered list; if False, creates bulleted list
        
    Returns:
        Formatted markdown list string
        
    Example:
        >>> format_list(["Item 1", "Item 2"], ordered=False)
        '\\n- Item 1\\n- Item 2\\n\\n'
        >>> format_list(["First", "Second"], ordered=True)
        '\\n1. First\\n2. Second\\n\\n'
    """
    if ordered:
        list_content = "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
    else:
        list_content = "\n".join(f"- {item}" for item in items)
    
    return f"\n{list_content}\n\n"


# =============================================================================
# WRITER INITIALIZATION HELPER
# =============================================================================

def validate_and_setup_writer(document_type: str, layout_style: str = None, project_file: str = None):
    """
    Validate and setup writer configuration.
    
    Args:
        document_type: Type of document ('report' or 'paper')
        layout_style: Layout style name
        project_file: Path to custom project configuration file (JSON or .epyson).
                     If None, uses default project.epyson from config directory.
        
    Returns:
        Tuple of (document_type, layout_style, output_dir, config)
    """
    # Validate document type
    valid_types = ['report', 'paper', 'book', 'presentation', 'notebook']
    if document_type not in valid_types:
        raise ValueError(f"Invalid document_type: {document_type}. Must be one of {valid_types}")
    
    # Set default layout style
    if layout_style is None:
        layout_style = 'minimal'
    
    # Initialize config loader with optional project_file
    from ePy_docs.core._config import ModularConfigLoader
    from pathlib import Path
    
    project_path = Path(project_file) if project_file else None
    config_loader = ModularConfigLoader(project_file=project_path)
    
    # Store config loader globally for other functions to use
    from ePy_docs.core._config import set_config_loader
    set_config_loader(config_loader)
    
    # Get output directory from config
    from ePy_docs.core._config import get_absolute_output_directories
    output_paths = get_absolute_output_directories()
    output_dir = str(output_paths[f'{document_type}'])
    
    # Basic config (can be expanded if needed)
    config = {
        'document_type': document_type,
        'layout_style': layout_style,
        'output_dir': output_dir,
        'project_file': project_file
    }
    
    return document_type, layout_style, output_dir, config


def route_callout_to_method(callout_type: str, method_map: dict) -> callable:
    """
    Route callout type to appropriate method.
    
    Args:
        callout_type: Type of callout
        method_map: Dictionary mapping types to methods
        
    Returns:
        Method to call
    """
    if callout_type not in method_map:
        raise ValueError(f"Unknown callout type: {callout_type}")
    return method_map[callout_type]


# =============================================================================
# DOCUMENT WRITER CORE - ALL BUSINESS LOGIC
# =============================================================================

class DocumentWriterCore:
    """
    Core implementation of DocumentWriter with all business logic.
    This class is INTERNAL and should never be used directly by users.
    """
    
    def __init__(self, document_type: str = "report", layout_style: str = None, project_file: str = None, language: str = None, columns: int = None):
        """Initialize core writer with all business logic."""
        # Lazy imports
        from ePy_docs.core._validation import (
            validate_dataframe, validate_string, validate_list,
            validate_image_path, validate_image_width, validate_callout_type,
            validate_reference_key
        )
        
        # Store validators for later use
        self._validate_dataframe = validate_dataframe
        self._validate_string = validate_string
        self._validate_list = validate_list
        self._validate_image_path = validate_image_path
        self._validate_image_width = validate_image_width
        self._validate_callout_type = validate_callout_type
        self._validate_reference_key = validate_reference_key
        
        # Initialize using existing validation function
        (
            self.document_type,
            self.layout_style,
            self.output_dir,
            self.config
        ) = validate_and_setup_writer(document_type, layout_style, project_file)
        
        # Set language (override layout default if provided)
        self.language = self._resolve_language(language)
        
        # Set default columns (override layout default if provided)
        self.default_columns = columns  # None means use layout default
        
        # State management
        self.content_buffer = []
        self._counters = {'table': 0, 'figure': 0, 'note': 0}
        self.generated_images = []
        self._is_generated = False

    def _resolve_language(self, language: Optional[str] = None) -> str:
        """Resolve document language from parameter or layout config.
        
        Args:
            language: Explicit language parameter (overrides layout default)
            
        Returns:
            Language code (e.g., 'en', 'es', 'fr')
        """
        # If language is explicitly provided, use it
        if language:
            return language
            
        # Try to get from layout configuration (some layouts may specify default language)
        try:
            from ePy_docs.core._config import load_layout
            layout_config = load_layout(self.layout_style, resolve_refs=True)
            
            # Check if layout has a language preference
            if 'language' in layout_config:
                return layout_config['language']
        except Exception:
            pass  # Fallback to default if layout loading fails
        
        # Try to get from project configuration
        try:
            from ePy_docs.core._config import get_loader
            loader = get_loader()
            project_config = loader.load_project()
            
            if 'project' in project_config and 'lang' in project_config['project']:
                return project_config['project']['lang']
        except Exception:
            pass  # Fallback to default
        
        # Default to English
        return 'en'

    def _resolve_document_columns(self) -> int:
        """Resolve the actual number of columns for the document.
        
        Returns:
            Number of columns (1 or 2)
        """
        # Priority: 1) explicit parameter, 2) document type default, 3) fallback to 1
        if self.default_columns is not None:
            return self.default_columns
        
        # Get from document type configuration
        try:
            from ePy_docs.core._config import get_document_type_config
            doc_config = get_document_type_config(self.document_type)
            return doc_config.get('default_columns', 1)
        except Exception:
            return 1

    def _check_not_generated(self):
        """Check that document has not been generated yet."""
        if self._is_generated:
            raise RuntimeError("Cannot add content after document generation. Create a new writer instance.")


    # Counter management methods
    def _validate_counter_type(self, counter_type: str) -> None:
        """Validate that counter type is supported."""
        if counter_type not in ['table', 'figure', 'note']:
            raise ValueError(f"Invalid counter type: {counter_type}. Must be one of: table, figure, note")

    def increment_counter(self, counter_type: str) -> int:
        """Increment a counter and return the new value."""
        self._validate_counter_type(counter_type)
        self._counters[counter_type] += 1
        return self._counters[counter_type]

    def get_counter(self, counter_type: str) -> int:
        """Get the current value of a counter."""
        self._validate_counter_type(counter_type)
        return self._counters[counter_type]

    def reset_counter(self, counter_type: str) -> None:
        """Reset a counter to 0."""
        self._validate_counter_type(counter_type)
        self._counters[counter_type] = 0

    def reset_all_counters(self) -> None:
        """Reset all counters to 0."""
        for counter_type in self._counters:
            self._counters[counter_type] = 0
    
    # Properties
    @property
    def table_counter(self) -> int:
        """Get the current table counter value."""
        return self._counters['table']

    @property
    def figure_counter(self) -> int:
        """Get the current figure counter value."""
        return self._counters['figure']

    @property
    def note_counter(self) -> int:
        """Get the current note counter value."""
        return self._counters['note']    # Content methods
    def add_content(self, content: str):
        self._check_not_generated()
        self._validate_string(content, "content", allow_empty=True, allow_none=False)
        processed_content = add_text_to_content(content)
        self.content_buffer.append(processed_content)
        
    def get_content(self) -> str:
        return ''.join(self.content_buffer)
    
    # Headers
    def add_h1(self, text: str):
        self._check_not_generated()
        self._validate_string(text, "heading", allow_empty=False, allow_none=False)
        content = add_header_to_content(text, level=1, document_type=self.document_type)
        self.content_buffer.append(content)
        
    def add_h2(self, text: str):
        self._check_not_generated()
        self._validate_string(text, "heading", allow_empty=False, allow_none=False)
        content = add_header_to_content(text, level=2, document_type=self.document_type)
        self.content_buffer.append(content)
        
    def add_h3(self, text: str):
        self._check_not_generated()
        self._validate_string(text, "heading", allow_empty=False, allow_none=False)
        content = add_header_to_content(text, level=3, document_type=self.document_type)
        self.content_buffer.append(content)
        
    def add_h4(self, text: str):
        self._check_not_generated()
        self._validate_string(text, "heading", allow_empty=False, allow_none=False)
        content = add_header_to_content(text, level=4, document_type=self.document_type)
        self.content_buffer.append(content)
        
    def add_h5(self, text: str):
        self._check_not_generated()
        self._validate_string(text, "heading", allow_empty=False, allow_none=False)
        content = add_header_to_content(text, level=5)
        self.content_buffer.append(content)
        
    def add_h6(self, text: str):
        self._check_not_generated()
        self._validate_string(text, "heading", allow_empty=False, allow_none=False)
        content = add_header_to_content(text, level=6)
        self.content_buffer.append(content)
    
    def add_text(self, content: str):
        self._check_not_generated()
        processed_content = add_text_to_content(content)
        self.content_buffer.append(processed_content)
        
    def add_list(self, items, ordered: bool = False):
        self._check_not_generated()
        self._validate_list(items, "items", allow_empty=False)
        content = format_list(items, ordered=ordered)
        self.content_buffer.append(content)
        
    def add_unordered_list(self, items):
        return self.add_list(items, ordered=False)
        
    def add_ordered_list(self, items):
        return self.add_list(items, ordered=True)
    
    # Tables
    def add_table(self, df, title=None, show_figure=True,
                 columns: Union[float, List[float], None] = None,
                 column_span: Optional[int] = None,
                 max_rows_per_table: Union[int, List[int], None] = None,
                 hide_columns: Union[str, List[str], None] = None,
                 filter_by: Dict[str, Any] = None,
                 sort_by: Union[str, List[str], None] = None,
                 width_inches: float = None):
        self._check_not_generated()
        self._validate_dataframe(df, "df")
        if title is not None:
            self._validate_string(title, "title", allow_empty=False, allow_none=False)
            
        # Use default_columns if columns not specified
        final_columns = columns if columns is not None else self.default_columns
        document_columns = self._resolve_document_columns()
            
        from ePy_docs.core._tables import table_orchestrator
        
        markdown, image_path, new_table_counter = table_orchestrator.create_table_image_and_markdown(
            df=df,
            caption=title,
            layout_style=self.layout_style,
            table_number=self._counters['table'] + 1,
            columns=final_columns,
            document_type=self.document_type,
            column_span=column_span,
            document_columns=document_columns,
            max_rows_per_table=max_rows_per_table,
            highlight_columns=None,
            colored=False,
            palette_name=None
        )
        
        self._counters['table'] = new_table_counter
        self.content_buffer.append(markdown)
        
        if image_path:
            if isinstance(image_path, list):
                self.generated_images.extend(image_path)
            else:
                self.generated_images.append(image_path)
        
        if show_figure:
            if isinstance(image_path, list):
                self._display_images(image_path)
            else:
                self._display_last_image()
    
    def add_colored_table(self, df, title=None, show_figure=True,
                         columns: Union[float, List[float], None] = None,
                         column_span: Optional[int] = None,
                         highlight_columns: Union[str, List[str], None] = None,
                         palette_name: str = None,
                         max_rows_per_table: Union[int, List[int], None] = None,
                         hide_columns: Union[str, List[str], None] = None,
                         filter_by: Dict[str, Any] = None,
                         sort_by: Union[str, List[str], None] = None,
                         width_inches: float = None):
        self._check_not_generated()
        from ePy_docs.core._tables import table_orchestrator
        
        # Use default_columns if columns not specified
        final_columns = columns if columns is not None else self.default_columns
        document_columns = self._resolve_document_columns()
        
        markdown, image_path, new_table_counter = table_orchestrator.create_table_image_and_markdown(
            df=df,
            caption=title,
            layout_style=self.layout_style,
            table_number=self._counters['table'] + 1,
            columns=final_columns,
            document_type=self.document_type,
            column_span=column_span,
            document_columns=document_columns,
            max_rows_per_table=max_rows_per_table,
            highlight_columns=highlight_columns,
            colored=True,
            palette_name=palette_name
        )
        
        self._counters['table'] = new_table_counter
        self.content_buffer.append(markdown)
        
        if image_path:
            if isinstance(image_path, list):
                self.generated_images.extend(image_path)
            else:
                self.generated_images.append(image_path)
        
        if show_figure:
            if isinstance(image_path, list):
                self._display_images(image_path)
            else:
                self._display_last_image()
    
    def _display_last_image(self):
        """Display the last generated image in Jupyter notebooks."""
        if not self.generated_images:
            return
        
        try:
            from IPython.display import Image, display
            import os
            
            last_image = self.generated_images[-1]
            if os.path.exists(last_image):
                display(Image(filename=last_image))
        except (ImportError, Exception):
            pass
    
    def _display_images(self, image_paths):
        """Display multiple images in Jupyter notebooks."""
        if not image_paths:
            return
        
        try:
            from IPython.display import Image, display
            import os
            
            for img_path in image_paths:
                if os.path.exists(img_path):
                    display(Image(filename=img_path))
        except (ImportError, Exception):
            pass
    
    # Equations
    def add_equation(self, latex_code: str, caption: str = None, label: str = None):
        self._check_not_generated()
        self._validate_string(latex_code, "equation", allow_empty=False, allow_none=False)
        if caption is not None:
            self._validate_string(caption, "caption", allow_empty=False, allow_none=False)
        if label is not None:
            self._validate_string(label, "label", allow_empty=False, allow_none=False)
        
        from ePy_docs.core._format import ContentGenerator
        self.content_buffer.append(ContentGenerator.create_equation(latex_code, caption, label))
    
    def add_inline_equation(self, latex_code: str):
        self._check_not_generated()
        self._validate_string(latex_code, "equation", allow_empty=False, allow_none=False)
        
        from ePy_docs.core._format import ContentGenerator
        self.content_buffer.append(ContentGenerator.create_inline_equation(latex_code))
    
    # Callouts - simplified routing
    def add_callout(self, content: str, type: str = "note", title: str = None):
        self._check_not_generated()
        self._validate_callout_type(type)
        self._validate_string(content, "message", allow_empty=False, allow_none=False)
        if title is not None:
            self._validate_string(title, "title", allow_empty=False, allow_none=False)
        
        # Use unified add_note_to_content function
        from ePy_docs.core._notes import add_note_to_content
        markdown, new_note_counter = add_note_to_content(content, title, type, self._counters['note'] + 1)
        self.content_buffer.append(markdown)
        self._counters['note'] = new_note_counter
        return self
    
    def _add_note_by_type(self, content: str, title: str, note_type: str):
        """Internal method to add callout by type."""
        return self.add_callout(content, type=note_type, title=title)
    
    def add_note(self, content: str, title: str = None):
        return self._add_note_by_type(content, title, "note")
        
    def add_tip(self, content: str, title: str = None):
        return self._add_note_by_type(content, title, "tip")
        
    def add_warning(self, content: str, title: str = None):
        return self._add_note_by_type(content, title, "warning")
        
    def add_error(self, content: str, title: str = None):
        return self._add_note_by_type(content, title, "error")
        
    def add_success(self, content: str, title: str = None):
        return self._add_note_by_type(content, title, "success")
        
    def add_caution(self, content: str, title: str = None):
        return self._add_note_by_type(content, title, "caution")
        
    def add_important(self, content: str, title: str = None):
        return self._add_note_by_type(content, title, "important")
        
    def add_information(self, content: str, title: str = None):
        return self._add_note_by_type(content, title, "information")
        
    def add_recommendation(self, content: str, title: str = None):
        return self._add_note_by_type(content, title, "note")  # recommendation -> note
        
    def add_advice(self, content: str, title: str = None):
        return self._add_note_by_type(content, title, "tip")  # advice -> tip
        
    def add_risk(self, content: str, title: str = None):
        return self._add_note_by_type(content, title, "risk")
    
    # Code
    def add_chunk(self, code: str, language: str = 'python', **kwargs):
        from ePy_docs.core._code import format_display_chunk
        self.add_content(format_display_chunk(code, language, **kwargs))
        
    def add_chunk_executable(self, code: str, language: str = 'python', **kwargs):
        from ePy_docs.core._code import format_executable_chunk
        self.add_content(format_executable_chunk(code, language, **kwargs))
    
    # Images
    def add_plot(self, fig, title: str = None, caption: str = None, source: str = None, palette_name: Optional[str] = None, column_span: Optional[int] = None):
        from ePy_docs.core._images import add_plot_content
        
        markdown, new_figure_counter, generated_image_path = add_plot_content(
            fig=fig, title=title, caption=caption,
            figure_counter=self._counters['figure'] + 1,
            output_dir=None,  # Let _get_output_directory resolve to figures/ subdirectory
            document_type=self.document_type,
            layout_style=self.layout_style,
            palette_name=palette_name,
            column_span=column_span,
            document_columns=self._resolve_document_columns()
        )
        
        self.content_buffer.append(markdown)
        self._counters['figure'] = new_figure_counter
        
        # Track generated image
        if generated_image_path:
            self.generated_images.append(generated_image_path)
        
    def add_image(self, path: str, caption: str = None, width: str = None, **kwargs):
        self._check_not_generated()
        self._validate_image_path(path)
        if caption is not None:
            self._validate_string(caption, "caption", allow_empty=False, allow_none=False)
        if width is not None:
            self._validate_image_width(width)
        
        from ePy_docs.core._images import add_image_content
        
        # Extract parameters from kwargs to avoid duplicates
        responsive = kwargs.pop('responsive', True)
        alt_text = kwargs.pop('alt_text', None)
        column_span = kwargs.pop('column_span', None)
        
        markdown, new_figure_counter, generated_images = add_image_content(
            path, caption=caption, width=width, alt_text=alt_text,
            responsive=responsive, document_type=self.document_type,
            figure_counter=self._counters['figure'] + 1,
            layout_style=self.layout_style,
            column_span=column_span,
            document_columns=self._resolve_document_columns(),
            **kwargs
        )
        
        self._counters['figure'] = new_figure_counter
        self.content_buffer.append(markdown)
        self.generated_images.extend(generated_images)
    
    def _cleanup_temporary_images(self):
        """Clean up temporary image files, keeping only renamed versions.
        
        This method removes duplicate or temporary image files, keeping only
        the final renamed versions in the output directory structure.
        Respects the 'keep_only_renamed_versions' configuration setting.
        """
        # Check if cleanup is enabled in configuration
        try:
            from ePy_docs.core._config import get_config_section
            image_config = get_config_section('images')
            if not image_config.get('shared_defaults', {}).get('output_settings', {}).get('keep_only_renamed_versions', True):
                return
        except Exception:
            # If config fails, default to cleanup enabled
            pass
        import os
        from pathlib import Path
        from collections import defaultdict
        
        if not self.generated_images:
            return
        
        # Group images by directory
        image_groups = defaultdict(list)
        for img_path in self.generated_images:
            path_obj = Path(img_path)
            if path_obj.exists():
                image_groups[path_obj.parent].append(path_obj)
        
        # For each directory, keep only the properly named files
        for directory, images in image_groups.items():
            # Identify properly named files (figure_N.png, table_N.png)
            final_images = []
            temp_images = []
            
            for img_path in images:
                filename = img_path.name
                # Check if it's a properly renamed file
                if (filename.startswith('figure_') or 
                    filename.startswith('table_') or 
                    filename.startswith('plot_')):
                    final_images.append(img_path)
                else:
                    # Check if it's a matplotlib temporary file
                    if (filename.startswith('tmp') or 
                        'temp' in filename.lower() or
                        filename.startswith('matplotlib_')):
                        temp_images.append(img_path)
            
            # Remove temporary files
            for temp_img in temp_images:
                try:
                    if temp_img.exists():
                        temp_img.unlink()
                        # Remove from generated_images list
                        if str(temp_img) in self.generated_images:
                            self.generated_images.remove(str(temp_img))
                except (OSError, PermissionError):
                    # Ignore cleanup errors
                    pass
    
    # References
    def add_reference(self, ref_type: str, ref_id: str, custom_text: str = None):
        self._validate_reference_key(ref_type)
        self._validate_string(ref_id, "citation", allow_empty=False, allow_none=False)
        
        from ePy_docs.core._format import ContentGenerator
        self.content_buffer.append(ContentGenerator.create_reference(ref_type, ref_id, custom_text))
        return self
        
    def add_citation(self, citation_key: str, page: str = None):
        self._validate_reference_key(citation_key)
        if page is not None:
            self._validate_string(page, "page", allow_empty=False, allow_none=False)
        
        from ePy_docs.core._format import ContentGenerator
        citation = ContentGenerator.create_citation(citation_key, page)
        
        # Citations should stick to the previous content without line breaks
        # Remove trailing newlines from the last buffer item before adding citation
        if self.content_buffer:
            last_item = self.content_buffer[-1]
            # Remove trailing newlines to attach citation directly
            self.content_buffer[-1] = last_item.rstrip('\n')
            # Add space before citation if the last item doesn't end with space, punctuation, or bracket
            if self.content_buffer[-1] and not self.content_buffer[-1][-1] in ' \t.,:;!?]':
                self.content_buffer[-1] += ' '
        
        # Don't add trailing newlines - let the next element handle spacing
        self.content_buffer.append(citation)
        return self
    
    # Files
    def add_markdown_file(self, file_path: str, fix_image_paths: bool = True, convert_tables: bool = True):
        from ePy_docs.core._markdown import process_markdown_file
        
        process_markdown_file(
            file_path=file_path, fix_image_paths=fix_image_paths, convert_tables=convert_tables,
            output_dir=self.output_dir, figure_counter=self._counters['figure'] + 1,
            writer_instance=self
        )
        
    def add_quarto_file(self, file_path: str, include_yaml: bool = False, 
                       fix_image_paths: bool = True, convert_tables: bool = True,
                       execute_code_blocks: bool = True):
        from ePy_docs.core._quarto import process_quarto_file
        
        process_quarto_file(
            file_path=file_path, include_yaml=include_yaml, fix_image_paths=fix_image_paths,
            convert_tables=convert_tables, output_dir=self.output_dir,
            figure_counter=self._counters['figure'] + 1,
            document_type=self.document_type, writer_instance=self,
            execute_code_blocks=execute_code_blocks
        )
    
    # Generation
    def cleanup_temporary_images(self) -> int:
        """Manually clean up temporary image files.
        
        Returns:
            Number of temporary files removed
        """
        if not self.generated_images:
            return 0
            
        import os
        from pathlib import Path
        
        removed_count = 0
        temp_images = []
        
        for img_path in self.generated_images[:]:  # Create copy to iterate safely
            path_obj = Path(img_path)
            if path_obj.exists():
                filename = path_obj.name
                # Check if it's a temporary file
                if (filename.startswith('tmp') or 
                    'temp' in filename.lower() or
                    filename.startswith('matplotlib_')):
                    temp_images.append(path_obj)
        
        # Remove temporary files
        for temp_img in temp_images:
            try:
                if temp_img.exists():
                    temp_img.unlink()
                    removed_count += 1
                    # Remove from generated_images list
                    if str(temp_img) in self.generated_images:
                        self.generated_images.remove(str(temp_img))
            except (OSError, PermissionError):
                # Ignore cleanup errors
                pass
        
        return removed_count

    def generate(self, markdown: bool = False, html: bool = True, pdf: bool = True,
                qmd: bool = True, tex: bool = False, docx: bool = False, 
                output_filename: str = None, bibliography_path: str = None,
                csl_path: str = None):
        """Generate output documents in specified formats."""
        if output_filename is not None:
            self._validate_string(output_filename, "filename", allow_empty=False, allow_none=False)
        
        from ePy_docs.core._quarto import prepare_generation, create_and_render
        from ePy_docs.core._config import get_absolute_output_directories
        from pathlib import Path
        
        # Prepare content
        content, project_title = prepare_generation(self, output_filename)
        
        # Setup output directory
        if self.output_dir is None:
            output_paths = get_absolute_output_directories()
            output_dir = str(output_paths['report'])
        else:
            output_dir = self.output_dir
        
        # Setup output filename
        if output_filename is None:
            output_filename = project_title
        if output_filename.endswith('.qmd'):
            output_filename = output_filename[:-4]
        
        # Build output path
        output_path = Path(output_dir) / f"{output_filename}.qmd"
        
        # Determine output formats
        output_formats = []
        if html:
            output_formats.append('html')
        if pdf:
            output_formats.append('pdf')
        if tex:
            output_formats.append('tex')
        if docx:
            output_formats.append('docx')
        
        # Clean up temporary images before generation (if enabled)
        self._cleanup_temporary_images()
        
        # Generate using core module - direct call, no intermediate wrapper
        result_paths = create_and_render(
            output_path=output_path,
            content=content,
            title=project_title,
            layout_name=self.layout_style,
            document_type=self.document_type,
            output_formats=output_formats,
            language=self.language,
            bibliography_path=bibliography_path,
            csl_path=csl_path,
            columns=self.default_columns
        )
        
        # Build result dictionary with requested formats only
        result = {'qmd': result_paths.get('qmd')}
        
        if markdown:
            result['markdown'] = result_paths.get('markdown')
        if html:
            result['html'] = result_paths.get('html')
        if pdf:
            result['pdf'] = result_paths.get('pdf')
        if tex:
            result['tex'] = result_paths.get('tex')
        if docx:
            result['docx'] = result_paths.get('docx')
        
        self._is_generated = True
        return result

    @staticmethod
    def get_available_document_types() -> Dict[str, str]:
        """Get available document types and their descriptions.
        
        Returns:
            Dictionary with document type names as keys and descriptions as values.
        """
        from ePy_docs.core._config import get_config_section
        
        # Document types are in documents._index.epyson under 'document_types' key
        documents_config = get_config_section('documents')
        document_types_config = documents_config.get('document_types', {})
        
        if not document_types_config:
            return {}
        
        return {
            name: config.get('description', f'{name.title()} document type')
            for name, config in document_types_config.items()
        }

    @staticmethod
    def get_available_layouts() -> Dict[str, str]:
        """Get available layout styles and their descriptions.
        
        Returns:
            Dictionary with layout names as keys and descriptions as values.
        """
        from pathlib import Path
        from ePy_docs.core._config import get_loader
        
        # Get layouts directory
        config_dir = Path(__file__).parent.parent / 'config'
        layouts_dir = config_dir / 'layouts'
        
        layouts = {}
        if layouts_dir.exists():
            for layout_file in layouts_dir.glob('*.epyson'):
                layout_name = layout_file.stem
                try:
                    loader = get_loader()
                    layout_data = loader.load_layout(layout_name)
                    description = layout_data.get('description', f'{layout_name.title()} layout style')
                    layouts[layout_name] = description
                except Exception:
                    layouts[layout_name] = f'{layout_name.title()} layout style'
        
        return layouts

    @staticmethod
    def get_available_palettes() -> Dict[str, str]:
        """Get available color palettes and their descriptions.
        
        Returns:
            Dictionary with palette names as keys and descriptions as values.
            
        Raises:
            ValueError: If palettes not found in colors configuration
        """
        
        from ePy_docs.core._config import get_config_section
        colors_data = get_config_section('colors')
        
        if 'palettes' not in colors_data:
            raise ValueError(
                "Palettes not found in colors configuration. "
                "Expected 'palettes' key in colors.epyson."
            )
        
        color_palettes = colors_data['palettes']
        
        palettes = {}
        for palette_name, palette_config in color_palettes.items():
            if isinstance(palette_config, dict):
                if 'description' not in palette_config:
                    raise ValueError(
                        f"Description not found for palette '{palette_name}'. "
                        "Each palette must have a 'description' key."
                    )
                palettes[palette_name] = palette_config['description']
        
        return palettes