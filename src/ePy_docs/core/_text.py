"""
TEXT Module - Typography and text formatting

Configuration: Centralized cache via _load_cached_files
Styling: Organization by layout_styles
Compatibility: No backward compatibility, no fallbacks
"""

from typing import Dict, Any, Optional
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


def add_header_to_content(text: str, level: int = 1, color: Optional[str] = None) -> str:
    """Generate header markdown.
    
    Args:
        text: Header text
        level: Header level (1-6)
        color: Optional color (ignored in pure markdown)
        
    Returns:
        Markdown header content
    """
    if level < 1 or level > 6:
        level = 1
    
    header_prefix = "#" * level
    return f"\n{header_prefix} {text}\n\n"


def add_h1_to_content(text: str, color: Optional[str] = None) -> str:
    """Generate H1 header markdown."""
    return add_header_to_content(text, 1, color)


def add_h2_to_content(text: str, color: Optional[str] = None) -> str:
    """Generate H2 header markdown."""
    return add_header_to_content(text, 2, color)


def add_h3_to_content(text: str, add_newline: bool = True, color: Optional[str] = None) -> str:
    """Generate H3 header markdown."""
    content = f"\n### {text}"
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
        from ePy_docs.core._format import format_superscripts
        
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
                formatted_part = format_superscripts(part, 'html')
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
        from ePy_docs.core._format import format_superscripts
        
        def process_math_variable(match):
            variable_content = match.group(1)
            formatted_content = format_superscripts(variable_content, 'html')
            return f"${formatted_content}$"
        
        # Process ${variable} patterns
        result = re.sub(r'\$\{([^}]+)\}', process_math_variable, result)
        
        # Apply general superscript processing
        result = format_superscripts(result, 'html')
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
    valid_types = ['report', 'paper']
    if document_type not in valid_types:
        raise ValueError(f"Invalid document_type: {document_type}. Must be one of {valid_types}")
    
    # Set default layout style
    if layout_style is None:
        layout_style = 'classic' if document_type == 'report' else 'academic'
    
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
    output_dir = str(output_paths['report'])
    
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
    
    def __init__(self, document_type: str = "report", layout_style: str = None, project_file: str = None):
        """Initialize core writer with all business logic."""
        # Lazy imports
        from ePy_docs.core._validators import (
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
        
        # State management
        self.content_buffer = []
        self._counters = {'table': 0, 'figure': 0, 'note': 0}
        self.generated_images = []
        self._is_generated = False

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
        self.content_buffer.append(content)
        
    def get_content(self) -> str:
        return ''.join(self.content_buffer)
    
    # Headers
    def add_h1(self, text: str):
        self._check_not_generated()
        self._validate_string(text, "heading", allow_empty=False, allow_none=False)
        content = add_header_to_content(text, level=1)
        self.content_buffer.append(content)
        
    def add_h2(self, text: str):
        self._check_not_generated()
        self._validate_string(text, "heading", allow_empty=False, allow_none=False)
        content = add_header_to_content(text, level=2)
        self.content_buffer.append(content)
        
    def add_h3(self, text: str):
        self._check_not_generated()
        self._validate_string(text, "heading", allow_empty=False, allow_none=False)
        content = add_header_to_content(text, level=3)
        self.content_buffer.append(content)
        
    def add_h4(self, text: str):
        self._check_not_generated()
        self._validate_string(text, "heading", allow_empty=False, allow_none=False)
        content = add_header_to_content(text, level=4)
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
    def add_table(self, df, title=None, show_figure=True, **kwargs):
        self._check_not_generated()
        self._validate_dataframe(df, "df")
        if title is not None:
            self._validate_string(title, "title", allow_empty=False, allow_none=False)
            
        from ePy_docs.core._tables import create_table_image_and_markdown
        
        markdown, image_path, new_table_counter = create_table_image_and_markdown(
            df=df,
            caption=title,
            layout_style=self.layout_style,
            table_number=self._counters['table'] + 1,
            show_figure=show_figure,
            **kwargs
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
    
    def add_colored_table(self, df, title=None, show_figure=True, **kwargs):
        self._check_not_generated()
        from ePy_docs.core._tables import create_table_image_and_markdown
        
        markdown, image_path, new_table_counter = create_table_image_and_markdown(
            df=df,
            caption=title,
            layout_style=self.layout_style,
            table_number=self._counters['table'] + 1,
            colored=True,
            show_figure=show_figure,
            **kwargs
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
        
        from ePy_docs.core._format import add_equation_to_content
        self.content_buffer.append(add_equation_to_content(latex_code, caption, label))
    
    def add_inline_equation(self, latex_code: str):
        self._check_not_generated()
        self._validate_string(latex_code, "equation", allow_empty=False, allow_none=False)
        
        from ePy_docs.core._format import add_inline_equation_to_content
        self.content_buffer.append(add_inline_equation_to_content(latex_code))
    
    # Callouts - simplified routing
    def add_callout(self, content: str, type: str = "note", title: str = None):
        self._check_not_generated()
        self._validate_callout_type(type)
        self._validate_string(content, "message", allow_empty=False, allow_none=False)
        if title is not None:
            self._validate_string(title, "title", allow_empty=False, allow_none=False)
        
        # Direct method routing
        method_map = {
            'note': self.add_note, 'tip': self.add_tip, 'warning': self.add_warning,
            'caution': self.add_caution, 'important': self.add_important, 'error': self.add_error,
            'success': self.add_success, 'information': self.add_information,
            'recommendation': self.add_recommendation, 'advice': self.add_advice, 'risk': self.add_risk
        }
        
        if type in method_map:
            method_map[type](content, title)
    
    def _add_note_type(self, content: str, title: str, note_type: str, func_name: str):
        """Generic note addition helper."""
        from ePy_docs.core._notes import __dict__ as notes_dict
        func = notes_dict.get(func_name)
        if func:
            markdown, new_note_counter = func(content, title, self._counters['note'] + 1)
            self.content_buffer.append(markdown)
            self._counters['note'] = new_note_counter
    
    def add_note(self, content: str, title: str = None):
        self._add_note_type(content, title, "note", "add_note_to_content")
        
    def add_tip(self, content: str, title: str = None):
        self._add_note_type(content, title, "tip", "add_tip_to_content")
        
    def add_warning(self, content: str, title: str = None):
        self._add_note_type(content, title, "warning", "add_warning_to_content")
        
    def add_error(self, content: str, title: str = None):
        self._add_note_type(content, title, "error", "add_error_to_content")
        
    def add_success(self, content: str, title: str = None):
        self._add_note_type(content, title, "success", "add_success_to_content")
        
    def add_caution(self, content: str, title: str = None):
        self._add_note_type(content, title, "caution", "add_caution_to_content")
        
    def add_important(self, content: str, title: str = None):
        self._add_note_type(content, title, "important", "add_important_to_content")
        
    def add_information(self, content: str, title: str = None):
        self._add_note_type(content, title, "information", "add_information_to_content")
        
    def add_recommendation(self, content: str, title: str = None):
        self._add_note_type(content, title, "recommendation", "add_recommendation_to_content")
        
    def add_advice(self, content: str, title: str = None):
        self._add_note_type(content, title, "advice", "add_advice_to_content")
        
    def add_risk(self, content: str, title: str = None):
        self._add_note_type(content, title, "risk", "add_risk_to_content")
    
    # Code
    def add_chunk(self, code: str, language: str = 'python', **kwargs):
        from ePy_docs.core._code import format_display_chunk
        self.add_content(format_display_chunk(code, language, **kwargs))
        
    def add_chunk_executable(self, code: str, language: str = 'python', **kwargs):
        from ePy_docs.core._code import format_executable_chunk
        self.add_content(format_executable_chunk(code, language, **kwargs))
    
    # Images
    def add_plot(self, fig, title: str = None, caption: str = None, source: str = None):
        from ePy_docs.core._images import add_plot_content
        
        markdown, new_figure_counter = add_plot_content(
            fig=fig, title=title, caption=caption,
            figure_counter=self._counters['figure'] + 1,
            document_type=self.document_type
        )
        
        self.content_buffer.append(markdown)
        self._counters['figure'] = new_figure_counter
        
    def add_image(self, path: str, caption: str = None, width: str = None, **kwargs):
        self._check_not_generated()
        self._validate_image_path(path)
        if caption is not None:
            self._validate_string(caption, "caption", allow_empty=False, allow_none=False)
        if width is not None:
            self._validate_image_width(width)
        
        from ePy_docs.core._images import add_image_content
        
        markdown, new_figure_counter, generated_images = add_image_content(
            path, caption=caption, width=width, alt_text=kwargs.get('alt_text'),
            responsive=kwargs.get('responsive', True), document_type=self.document_type,
            figure_counter=self._counters['figure'] + 1, **kwargs
        )
        
        self._counters['figure'] = new_figure_counter
        self.content_buffer.append(markdown)
        self.generated_images.extend(generated_images)
    
    # References
    def add_reference(self, ref_type: str, ref_id: str, custom_text: str = None):
        self._validate_reference_key(ref_type)
        self._validate_string(ref_id, "citation", allow_empty=False, allow_none=False)
        
        from ePy_docs.core._format import add_reference_to_content
        self.content_buffer.append(add_reference_to_content(ref_type, ref_id, custom_text))
        
    def add_citation(self, citation_key: str, page: str = None):
        self._validate_reference_key(citation_key)
        if page is not None:
            self._validate_string(page, "page", allow_empty=False, allow_none=False)
        
        from ePy_docs.core._format import add_citation_to_content
        self.content_buffer.append(add_citation_to_content(citation_key, page))
    
    # Files
    def add_markdown_file(self, file_path: str, fix_image_paths: bool = True, convert_tables: bool = True):
        from ePy_docs.core._markdown import process_markdown_file
        
        process_markdown_file(
            file_path=file_path, fix_image_paths=fix_image_paths, convert_tables=convert_tables,
            output_dir=self.output_dir, figure_counter=self._counters['figure'] + 1,
            writer_instance=self
        )
        
    def add_quarto_file(self, file_path: str, include_yaml: bool = False, 
                       fix_image_paths: bool = True, convert_tables: bool = True):
        from ePy_docs.core._quarto import process_quarto_file
        
        process_quarto_file(
            file_path=file_path, include_yaml=include_yaml, fix_image_paths=fix_image_paths,
            convert_tables=convert_tables, output_dir=self.output_dir,
            figure_counter=self._counters['figure'] + 1,
            document_type=self.document_type, writer_instance=self
        )
    
    # Generation
    def generate(self, markdown: bool = False, html: bool = True, pdf: bool = True,
                qmd: bool = True, tex: bool = False, output_filename: str = None):
        if output_filename is not None:
            self._validate_string(output_filename, "filename", allow_empty=False, allow_none=False)
        
        from ePy_docs.core._quarto import prepare_generation, generate_documents
        
        content, project_title = prepare_generation(self, output_filename)
        
        result = generate_documents(
            content=content, title=project_title, html=html, pdf=pdf,
            output_filename=output_filename, layout_name=self.layout_style,
            output_dir=self.output_dir, document_type=self.document_type
        )
        
        self._is_generated = True
        return result