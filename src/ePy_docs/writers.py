"""
Unified Document Writers API - PURE DELEGATION LAYER

CONSTITUTIONAL PRINCIPLE: TRANSPARENCY DIMENSION - DELEGATION KINGDOM
This API is a PURE INTERFACE that only delegates to specialized modules.
ZERO business logic exists here - only method routing and parameter passing.

Architecture:
- DocumentWriter: Unified interface for all document types (report/paper)
- Explicit document_type parameter for clarity
- NO logic, NO validation, NO conditionals - pure delegation only
- All business logic delegated to internals/api/* modules

Performance:
- Lazy imports for faster startup
- All validation delegated to utils.validation module
- All logic delegated to internals.api modules
"""

from typing import List
import pandas as pd

# Import validation functions from utils module (used for parameter validation only)
from ePy_docs.utils.validators import (
    validate_dataframe as _validate_dataframe,
    validate_string as _validate_string,
    validate_list as _validate_list,
    validate_image_path as _validate_image_path,
    validate_image_width as _validate_image_width,
    validate_callout_type as _validate_callout_type,
    validate_reference_key as _validate_reference_key,
)

from ePy_docs.utils.counters import CounterManager


# =============================================================================
# DOCUMENT WRITER - PURE DELEGATION INTERFACE
# =============================================================================

class DocumentWriter:
    """
    Unified document writer - PURE DELEGATION to internals.
    
    Usage:
        writer = DocumentWriter("report", layout_style="classic")
        writer = DocumentWriter("paper", layout_style="academic")
    """
    
    def __init__(self, document_type: str = "report", layout_style: str = None):
        """Initialize - PURE DELEGATION to _writer_init module."""
        from ePy_docs.internals.delegation._writer_init import validate_and_setup_writer
        
        # Delegate all initialization logic
        (
            self.document_type,
            self.layout_style,
            self.output_dir,
            self.config
        ) = validate_and_setup_writer(document_type, layout_style)
        
        # State management (no logic, just initialization)
        self.content_buffer = []
        self.counter_manager = CounterManager()
        self.generated_images = []
        self._is_generated = False
    
    def _check_not_generated(self):
        """Check that document has not been generated yet."""
        if self._is_generated:
            raise RuntimeError("Cannot add content after document generation. Create a new writer instance.")
    
    # Backward compatibility properties for counters
    @property
    def table_counter(self) -> int:
        """Get the current table counter value."""
        return self.counter_manager.table_counter
    
    @table_counter.setter
    def table_counter(self, value: int):
        """Set the table counter value for backward compatibility."""
        self.counter_manager._counters['table'] = value
    
    @property
    def figure_counter(self) -> int:
        """Get the current figure counter value."""
        return self.counter_manager.figure_counter
    
    @figure_counter.setter
    def figure_counter(self, value: int):
        """Set the figure counter value for backward compatibility."""
        self.counter_manager._counters['figure'] = value
    
    @property
    def note_counter(self) -> int:
        """Get the current note counter value."""
        return self.counter_manager.note_counter
    
    @note_counter.setter
    def note_counter(self, value: int):
        """Set the note counter value for backward compatibility."""
        self.counter_manager._counters['note'] = value
    
    # === CONTENT MANAGEMENT ===
    
    def add_content(self, content: str) -> 'DocumentWriter':
        """PURE DELEGATION - validate and append."""
        self._check_not_generated()
        _validate_string(content, "content", allow_empty=True, allow_none=False)
        self.content_buffer.append(content)
        return self
    
    def get_content(self) -> str:
        """PURE DELEGATION - join buffer."""
        return ''.join(self.content_buffer)
    
    # === TEXT OPERATIONS ===
    
    def add_h1(self, text: str) -> 'DocumentWriter':
        """PURE DELEGATION to unified content module."""
        self._check_not_generated()
        _validate_string(text, "heading", allow_empty=False, allow_none=False)
        
        from ePy_docs.internals.formatting._content import add_content_type
        content, _, _ = add_content_type('header', text, level=1)
        self.content_buffer.append(content)
        return self
    
    def add_h2(self, text: str) -> 'DocumentWriter':
        """PURE DELEGATION to unified content module."""
        self._check_not_generated()
        _validate_string(text, "heading", allow_empty=False, allow_none=False)
        
        from ePy_docs.internals.formatting._content import add_content_type
        content, _, _ = add_content_type('header', text, level=2)
        self.content_buffer.append(content)
        return self
    
    def add_h3(self, text: str) -> 'DocumentWriter':
        """PURE DELEGATION to unified content module."""
        self._check_not_generated()
        _validate_string(text, "heading", allow_empty=False, allow_none=False)
        
        from ePy_docs.internals.formatting._content import add_content_type
        content, _, _ = add_content_type('header', text, level=3)
        self.content_buffer.append(content)
        return self
    
    def add_text(self, content: str) -> 'DocumentWriter':
        """PURE DELEGATION to unified content module."""
        self._check_not_generated()
        from ePy_docs.internals.formatting._content import add_content_type
        processed_content, _, _ = add_content_type('text', content)
        self.content_buffer.append(processed_content)
        return self
    
    def add_list(self, items: List[str], ordered: bool = False) -> 'DocumentWriter':
        """PURE DELEGATION to unified content module."""
        self._check_not_generated()
        _validate_list(items, "items", allow_empty=False)
        from ePy_docs.internals.formatting._content import add_content_type
        content, _, _ = add_content_type('list', items, ordered=ordered)
        self.content_buffer.append(content)
        return self
    
    def add_unordered_list(self, items: List[str]) -> 'DocumentWriter':
        """PURE DELEGATION - alias."""
        return self.add_list(items, ordered=False)
    
    def add_ordered_list(self, items: List[str]) -> 'DocumentWriter':
        """PURE DELEGATION - alias."""
        return self.add_list(items, ordered=True)
    
    # === TABLE OPERATIONS ===
    
    def add_table(self, df: pd.DataFrame, title: str = None, **kwargs) -> 'DocumentWriter':
        """PURE DELEGATION to unified content module."""
        self._check_not_generated()
        _validate_dataframe(df, "df")
        if title is not None:
            _validate_string(title, "title", allow_empty=False, allow_none=False)
        
        from ePy_docs.internals.formatting._content import add_content_type
        
        markdown_content, new_table_counter, generated_images = add_content_type(
            'table',
            df,
            title=title,
            layout_style=self.layout_style,
            document_type=self.document_type,
            table_counter=self.counter_manager.table_counter,
            **kwargs
        )
        
        # Update counter manager with the new value
        self.counter_manager._counters['table'] = new_table_counter
        
        self.content_buffer.append(markdown_content)
        self.generated_images.extend(generated_images)
        return self
    
    def add_colored_table(self, df: pd.DataFrame, title: str = None, **kwargs) -> 'DocumentWriter':
        """PURE DELEGATION to unified content module."""
        self._check_not_generated()
        from ePy_docs.internals.formatting._content import add_content_type
        
        markdown_content, new_table_counter, generated_images = add_content_type(
            'colored_table',
            df,
            title=title,
            layout_style=self.layout_style,
            document_type=self.document_type,
            table_counter=self.counter_manager.table_counter,
            **kwargs
        )
        
        # Update counter manager with the new value
        self.counter_manager._counters['table'] = new_table_counter
        
        self.content_buffer.append(markdown_content)
        self.generated_images.extend(generated_images)
        return self
        
        self.content_buffer.append(markdown_content)
        self.generated_images.extend(generated_images)
        return self
    
    # === EQUATION OPERATIONS ===
    
    def add_equation(self, latex_code: str, caption: str = None, label: str = None) -> 'DocumentWriter':
        """Delegate to FORMAT module."""
        self._check_not_generated()
        _validate_string(latex_code, "equation", allow_empty=False, allow_none=False)
        if caption is not None:
            _validate_string(caption, "caption", allow_empty=False, allow_none=False)
        if label is not None:
            _validate_string(label, "label", allow_empty=False, allow_none=False)
        
        from ePy_docs.internals.formatting._format import add_equation_to_content
        self.content_buffer.append(add_equation_to_content(latex_code, caption, label))
        return self
    
    def add_inline_equation(self, latex_code: str) -> 'DocumentWriter':
        """Delegate to FORMAT module."""
        self._check_not_generated()
        _validate_string(latex_code, "equation", allow_empty=False, allow_none=False)
        
        from ePy_docs.internals.formatting._format import add_inline_equation_to_content
        self.content_buffer.append(add_inline_equation_to_content(latex_code))
        return self
    
    # === NOTE OPERATIONS ===
    
    def add_callout(self, content: str, type: str = "note", title: str = None) -> 'DocumentWriter':
        """PURE DELEGATION to callout router."""
        self._check_not_generated()
        _validate_callout_type(type)
        _validate_string(content, "message", allow_empty=False, allow_none=False)
        if title is not None:
            _validate_string(title, "title", allow_empty=False, allow_none=False)
        
        from ePy_docs.internals.delegation._callout_router import route_callout_to_method
        
        # Build method map
        method_map = {
            'note': self.add_note, 'tip': self.add_tip,
            'warning': self.add_warning, 'caution': self.add_caution,
            'important': self.add_important, 'error': self.add_error,
            'success': self.add_success, 'information': self.add_information,
            'recommendation': self.add_recommendation, 'advice': self.add_advice,
            'risk': self.add_risk
        }
        
        # Route and call
        method = route_callout_to_method(type, method_map)
        method(content, title)
        return self
    
    def add_note(self, content: str, title: str = None) -> 'DocumentWriter':
        """Delegate to NOTES module."""
        from ePy_docs.internals.formatting._notes import add_note_to_content
        self.content_buffer.append(add_note_to_content(content, title, "note"))
        self.counter_manager.increment('note')
        return self
    
    def add_tip(self, content: str, title: str = None) -> 'DocumentWriter':
        """Delegate to NOTES module."""
        from ePy_docs.internals.formatting._notes import add_tip_to_content
        self.content_buffer.append(add_tip_to_content(content, title))
        self.counter_manager.increment('note')
        return self
    
    def add_warning(self, content: str, title: str = None) -> 'DocumentWriter':
        """Delegate to NOTES module."""
        from ePy_docs.internals.formatting._notes import add_warning_to_content
        self.content_buffer.append(add_warning_to_content(content, title))
        self.counter_manager.increment('note')
        return self
        
    def add_error(self, content: str, title: str = None) -> 'DocumentWriter':
        """Delegate to NOTES module."""
        from ePy_docs.internals.formatting._notes import add_error_to_content
        self.content_buffer.append(add_error_to_content(content, title))
        self.counter_manager.increment('note')
        return self
        
    def add_success(self, content: str, title: str = None) -> 'DocumentWriter':
        """Delegate to NOTES module."""
        from ePy_docs.internals.formatting._notes import add_success_to_content
        self.content_buffer.append(add_success_to_content(content, title))
        self.counter_manager.increment('note')
        return self
        
    def add_caution(self, content: str, title: str = None) -> 'DocumentWriter':
        """Delegate to NOTES module."""
        from ePy_docs.internals.formatting._notes import add_caution_to_content
        self.content_buffer.append(add_caution_to_content(content, title))
        self.counter_manager.increment('note')
        return self
        
    def add_important(self, content: str, title: str = None) -> 'DocumentWriter':
        """Delegate to NOTES module."""
        from ePy_docs.internals.formatting._notes import add_important_to_content
        self.content_buffer.append(add_important_to_content(content, title))
        self.counter_manager.increment('note')
        return self
        
    def add_information(self, content: str, title: str = None) -> 'DocumentWriter':
        """Delegate to NOTES module."""
        from ePy_docs.internals.formatting._notes import add_information_to_content
        self.content_buffer.append(add_information_to_content(content, title))
        self.counter_manager.increment('note')
        return self
        
    def add_recommendation(self, content: str, title: str = None) -> 'DocumentWriter':
        """Delegate to NOTES module."""
        from ePy_docs.internals.formatting._notes import add_recommendation_to_content
        self.content_buffer.append(add_recommendation_to_content(content, title))
        self.counter_manager.increment('note')
        return self
        
    def add_advice(self, content: str, title: str = None) -> 'DocumentWriter':
        """Delegate to NOTES module."""
        from ePy_docs.internals.formatting._notes import add_advice_to_content
        self.content_buffer.append(add_advice_to_content(content, title))
        self.counter_manager.increment('note')
        return self
        
    def add_risk(self, content: str, title: str = None) -> 'DocumentWriter':
        """Delegate to NOTES module."""
        from ePy_docs.internals.formatting._notes import add_risk_to_content
        self.content_buffer.append(add_risk_to_content(content, title))
        self.counter_manager.increment('note')
        return self
    
    # === CODE OPERATIONS ===
    
    def add_chunk(self, code: str, language: str = 'python', **kwargs) -> 'DocumentWriter':
        """Delegate to CODE module."""
        from ePy_docs.internals.formatting._code import format_display_chunk
        self.add_content(format_display_chunk(code, language, **kwargs))
        return self
    
    def add_chunk_executable(self, code: str, language: str = 'python', **kwargs) -> 'DocumentWriter':
        """Delegate to CODE module."""
        from ePy_docs.internals.formatting._code import format_executable_chunk
        self.add_content(format_executable_chunk(code, language, **kwargs))
        return self
    
    # === IMAGE OPERATIONS ===
        
    def add_plot(self, fig, title: str = None, caption: str = None, source: str = None) -> 'DocumentWriter':
        """Delegate to IMAGES module."""
        from ePy_docs.internals.formatting._images import add_plot_to_content
        from ePy_docs.internals.delegation._image_logic import save_plot_to_temp
        
        temp_path = save_plot_to_temp(fig)
        markdown = add_plot_to_content(
            img_path=temp_path,
            title=title,
            caption=caption
        )
        
        self.content_buffer.append(markdown)
        self.counter_manager.increment('figure')
        return self
        
    def add_image(self, path: str, caption: str = None, width: str = None, **kwargs) -> 'DocumentWriter':
        """PURE DELEGATION to unified content module."""
        self._check_not_generated()
        _validate_image_path(path)
        if caption is not None:
            _validate_string(caption, "caption", allow_empty=False, allow_none=False)
        if width is not None:
            _validate_image_width(width)
        
        from ePy_docs.internals.formatting._content import add_content_type
        from ePy_docs.internals.delegation._image_logic import parse_image_width
        
        markdown, new_figure_counter, generated_images = add_content_type(
            'image',
            path,
            caption=caption,
            fig_width=parse_image_width(width),
            alt_text=kwargs.get('alt_text'),
            responsive=kwargs.get('responsive', True),
            document_type=self.document_type,
            figure_counter=self.counter_manager.figure_counter,
            **kwargs
        )
        
        # Update counter manager with the new value
        self.counter_manager._counters['figure'] = new_figure_counter
        
        self.content_buffer.append(markdown)
        self.generated_images.extend(generated_images)
        return self
        
        self.content_buffer.append(markdown)
        return self
        
    # === REFERENCE OPERATIONS ===
        
    def add_reference(self, ref_type: str, ref_id: str, custom_text: str = None) -> 'DocumentWriter':
        """Delegate to FORMAT module."""
        _validate_reference_key(ref_type)
        _validate_string(ref_id, "citation", allow_empty=False, allow_none=False)
        
        from ePy_docs.internals.formatting._format import add_reference_to_content
        self.content_buffer.append(add_reference_to_content(ref_type, ref_id, custom_text))
        return self
        
    def add_citation(self, citation_key: str, page: str = None) -> 'DocumentWriter':
        """Delegate to FORMAT module."""
        _validate_reference_key(citation_key)
        if page is not None:
            _validate_string(page, "page", allow_empty=False, allow_none=False)
        
        from ePy_docs.internals.formatting._format import add_citation_to_content
        self.content_buffer.append(add_citation_to_content(citation_key, page))
        return self
    
    # === FILE OPERATIONS ===
        
    def add_markdown_file(self, file_path: str, fix_image_paths: bool = True, 
                         convert_tables: bool = True) -> 'DocumentWriter':
        """PURE DELEGATION to file processor."""
        from ePy_docs.internals.delegation._file_processor import process_markdown_with_tables
        
        process_markdown_with_tables(
            file_path=file_path,
            fix_image_paths=fix_image_paths,
            convert_tables=convert_tables,
            output_dir=self.output_dir,
            figure_counter=self.counter_manager.figure_counter,
            writer_instance=self
        )
        return self
    
    def add_quarto_file(self, file_path: str, include_yaml: bool = False, 
                       fix_image_paths: bool = True, convert_tables: bool = True) -> 'DocumentWriter':
        """PURE DELEGATION to file processor."""
        from ePy_docs.internals.delegation._file_processor import process_quarto_with_tables
        
        process_quarto_with_tables(
            file_path=file_path,
            include_yaml=include_yaml,
            fix_image_paths=fix_image_paths,
            convert_tables=convert_tables,
            output_dir=self.output_dir,
            figure_counter=self.counter_manager.figure_counter,
            document_type=self.document_type,
            writer_instance=self
        )
        return self
    
    # === GENERATION ===
    
    def generate(self, markdown: bool = False, html: bool = True, pdf: bool = True,
                qmd: bool = True, tex: bool = False, output_filename: str = None) -> dict:
        """PURE DELEGATION to generator."""
        if output_filename is not None:
            _validate_string(output_filename, "filename", allow_empty=False, allow_none=False)
        
        from ePy_docs.internals.delegation._generator_logic import prepare_generation
        from ePy_docs.internals.generation._generator import generate_documents_clean
        
        # Prepare generation (validates and gets config)
        content, project_title = prepare_generation(self, output_filename)
        
        # Generate documents
        result = generate_documents_clean(
            content=content,
            title=project_title, 
            html=html,
            pdf=pdf,
            output_filename=output_filename,
            layout_name=self.layout_style,
            output_dir=self.output_dir,
            document_type=self.document_type
        )
        
        # Mark as generated
        self._is_generated = True
        
        return result
