"""
Paper API for Article Generation

Clean article writer using paper.json configuration.
Focused exclusively on academic/technical articles, not reports.
All configuration is done through paper.json layouts and setup.
"""

import os
from typing import Dict, List, Any, Optional, Union, Tuple

import pandas as pd
import matplotlib.pyplot as plt

from ePy_docs.components.notes import NoteRenderer
from ePy_docs.components.setup import _resolve_config_path, get_absolute_output_directories
from ePy_docs.components.project_info import get_project_config_data
from ePy_docs.files import _load_cached_files
from ePy_docs.components.images import display_in_notebook
from ePy_docs.components.quarto import process_mathematical_text


def _load_paper_config(sync_files: bool = True) -> dict:
    """Load paper.json configuration."""
    config_path = _resolve_config_path('paper.json', sync_files=sync_files)
    
    if sync_files:
        try:
            cached_files = _load_cached_files(config_path)
            paper_config = cached_files.get(config_path)
        except (TypeError, KeyError):
            paper_config = None
    else:
        paper_config = None
    
    if paper_config is None:
        with open(config_path, 'r', encoding='utf-8') as f:
            import json
            paper_config = json.load(f)
    
    return paper_config


def _get_paper_layout_config(layout_style: str, sync_files: bool = True) -> dict:
    """Get layout configuration from paper.json."""
    paper_config = _load_paper_config(sync_files)
    
    if layout_style not in paper_config.get('layouts', {}):
        # Default to 'academic' if layout not found
        layout_style = 'academic'
    
    return paper_config['layouts'][layout_style]


def process_mathematical_text(latex_code, layout_name, sync_files):
    """Mathematical text processing compatibility function."""
    return latex_code

def _prepare_multiindex_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare DataFrame with MultiIndex for proper table display.
    
    Handles both MultiIndex columns and MultiIndex rows by flattening them
    appropriately for table visualization while preserving hierarchy information.
    Special handling for engineering data with complete case information.
    
    Args:
        df: DataFrame with potential MultiIndex in columns and/or rows
        
    Returns:
        DataFrame prepared for table display with proper column/row labels
    """
    processed_df = df.copy()
    
    # Handle MultiIndex columns
    if isinstance(processed_df.columns, pd.MultiIndex):
        # Create hierarchical column names by joining index levels
        new_columns = []
        for col in processed_df.columns:
            # Join non-empty levels with a separator, handling various data types
            col_parts = []
            for part in col:
                part_str = str(part).strip()
                if part_str and part_str.lower() not in ['nan', 'none', '']:
                    col_parts.append(part_str)
            
            if col_parts:
                # Use different separators for better visual hierarchy
                if len(col_parts) == 1:
                    new_columns.append(col_parts[0])
                elif len(col_parts) == 2:
                    new_columns.append(f"{col_parts[0]} - {col_parts[1]}")
                else:
                    new_columns.append(' | '.join(col_parts))
            else:
                new_columns.append('Column')  # Fallback name
        
        processed_df.columns = new_columns
    
    # Handle MultiIndex rows (index) - Special handling for engineering data
    if isinstance(processed_df.index, pd.MultiIndex):
        # For MultiIndex rows, we'll create separate columns for each level
        # This preserves all information and makes it more readable
        
        # Get level names, use defaults if not named
        level_names = []
        for i, name in enumerate(processed_df.index.names):
            if name is not None:
                level_names.append(name)
            else:
                level_names.append(f'Level_{i}')
        
        # Create DataFrame with MultiIndex levels as separate columns
        index_data = {}
        for i, level_name in enumerate(level_names):
            index_data[level_name] = [idx[i] for idx in processed_df.index]
        
        # Create new DataFrame with index levels as columns
        index_df = pd.DataFrame(index_data)
        
        # Reset the original index and concatenate with index columns
        processed_df = processed_df.reset_index(drop=True)
        processed_df = pd.concat([index_df, processed_df], axis=1)
        
    else:
        # Handle single-level index
        # Reset index to make row labels a regular column for table display
        # Only reset if index has meaningful labels or has a name
        if (processed_df.index.name is not None or 
            not processed_df.index.equals(pd.RangeIndex(len(processed_df)))):
            
            # Set a proper name for the index column if it doesn't have one
            if processed_df.index.name is None:
                processed_df.index.name = 'Index'
            
            processed_df = processed_df.reset_index()
    
    return processed_df

class PaperWriter:
    """Clean writer for academic/technical articles using paper.json configuration.
    
    Maintains same API as ReportWriter but generates articles instead of reports.
    Automatically constructs file paths from setup.json and paper.json.
    All configuration loaded from paper.json layouts instead of report configurations.
    
    IMPORTANTE: Use ONLY add_colored_table() for tables.
    The old add_table() function has been EXILED to DIMENSION ESPEJO
    for violating DIMENSIÓN TRANSPARENCIA (contained HTML fallbacks).
    """
    
    def __init__(self, layout_style: str = "academic", sync_files: bool = True, **kwargs):
        """Initialize PaperWriter using paper.json configuration.
        
        Args:
            layout_style: Paper layout from paper.json ('academic', 'technical', 'scientific', etc.)
            sync_files: Whether to use synchronized configuration files
        """
        # Initialize complete paper configuration system
        from ePy_docs.components.configurator import initialize_paper_config
        
        paper_config_dict = initialize_paper_config(layout_style=layout_style, sync_files=sync_files)
        
        # Store configuration for constitutional access
        self.config = paper_config_dict
        self.layout_style = layout_style
        self.sync_files = sync_files
        self.table_counter = 0
        self.figure_counter = 0
        self.output_dir = ""
        self.show_in_notebook = True
        
        # Create note_renderer with paper layout style
        self.note_renderer = NoteRenderer(layout_style=layout_style, sync_files=sync_files)
        
        # CONSTITUTIONAL ACCESS: Only PaperWriter has access to paper_name
        self._paper_name = self._get_paper_name_from_json()
        
        # Use CONSTITUTIONAL file_path with paper_name (NO hardcoding)
        constitutional_filename = f"{self._paper_name}.md"
        auto_file_path = os.path.join(paper_config_dict['output_dir'], constitutional_filename)
        
        # Initialize file writer functionality directly (no intermediate classes)
        self.file_path = os.path.abspath(auto_file_path)
        self.content_buffer: List[str] = []
        
        # Use absolute paper directory from configuration
        self.output_dir = os.path.abspath(paper_config_dict['output_dir'])
        os.makedirs(self.output_dir, exist_ok=True)
        
        # CONSTITUTIONAL ACCESS: Only PaperWriter has access to paper_name
        self._paper_name = self._get_paper_name_from_json()
    
    def _get_paper_name_from_json(self) -> str:
        """PRIVATE: Get paper_name directly from paper.json - ONLY paper.py has access.
        
        Following GOVERNING DIMENSIONS constitutional access pattern:
        - ONLY PaperWriter can access paper_name from paper.json
        - configurator.py and other components are FORBIDDEN from this access
        
        Returns:
            Paper name from paper.json for current layout_style
        """
        from ePy_docs.files import _load_cached_files
        from ePy_docs.components.setup import _resolve_config_path
        
        try:
            # Direct access to paper.json (constitutional privilege)
            config_path = _resolve_config_path('components/paper', self.sync_files)
            paper_config = _load_cached_files(config_path, self.sync_files)
            
            # Get paper_name for current layout_style
            layout_config = paper_config.get('layouts', {}).get(self.layout_style, {})
            paper_name = layout_config.get('paper_name')
            
            if paper_name:
                return paper_name
            else:
                # Fallback to project name only if paper_name is null
                project_config = self.config.get('project_config', {})
                project_name = project_config.get('project', {}).get('name', 'Paper')
                return project_name
                
        except Exception as e:
            raise ValueError(f"CONSTITUTIONAL VIOLATION: PaperWriter failed to access paper_name: {e}")
    
    @property 
    def paper_name(self) -> str:
        """Get the paper name - CONSTITUTIONAL ACCESS ONLY for PaperWriter."""
        return self._paper_name
    
    # Content management methods (integrated directly)
    def add_content(self, content: str) -> None:
        """Add content to the buffer preserving original formatting."""
        if content:
            # Ensure content ends with double newlines for proper markdown spacing
            if not content.endswith('\n\n'):
                if content.endswith('\n'):
                    content = content + '\n'
                else:
                    content = content + '\n\n'
            self.content_buffer.append(content)
    
    def get_content(self) -> str:
        """Get the complete accumulated content as a single string."""
        return ''.join(self.content_buffer)

    def get_layout_config(self) -> dict:
        """Get current layout configuration from paper.json."""
        return _get_paper_layout_config(self.layout_style, self.sync_files)

    # Headers - SAME AS REPORTS using basic markdown
    def add_h1(self, text: str) -> None:
        """Add H1 header using basic markdown."""
        self.add_content(f"# {text}\n\n")

    def add_h2(self, text: str) -> None:
        """Add H2 header using basic markdown."""
        self.add_content(f"## {text}\n\n")

    def add_h3(self, text: str) -> None:
        """Add H3 header using basic markdown."""
        self.add_content(f"### {text}\n\n")

    # Text and lists - IDENTICAL TO REPORTS
    def add_text(self, content: str) -> None:
        """Add text content."""
        self.add_content(content)

    def add_list(self, items: List[str], ordered: bool = False) -> None:
        """Add bulleted or numbered list."""
        if ordered:
            formatted_items = [f"{i+1}. {item}" for i, item in enumerate(items)]
        else:
            formatted_items = [f"- {item}" for item in items]
        
        list_content = '\n'.join(formatted_items) + '\n'
        self.add_content(list_content)

    # Code chunks - IDENTICAL TO REPORTS
    def add_chunk(self, code: str, language: str = 'python', 
                  caption: Optional[str] = None, label: Optional[str] = None) -> None:
        """Add non-executable code chunk to article (display only).
        
        Args:
            code: Code content as multiline string
            language: Programming language (python, javascript, sql, etc.)
            caption: Optional caption for the code block
            label: Optional label for cross-referencing
        """
        from ePy_docs.components.code import format_display_chunk
        
        chunk_content = format_display_chunk(code, language, caption, label)
        self.add_content(chunk_content)

    def add_chunk_executable(self, code: str, language: str = 'python', 
                            caption: Optional[str] = None, label: Optional[str] = None) -> None:
        """Add executable code chunk to article (will be executed by Quarto).
        
        Args:
            code: Code content as multiline string
            language: Programming language (python, javascript, r, etc.)
            caption: Optional caption for the code block
            label: Optional label for cross-referencing
        """
        from ePy_docs.components.code import format_executable_chunk
        
        chunk_content = format_executable_chunk(code, language, caption, label)
        self.add_content(chunk_content)

    # Tables - Configuration from paper.json + tables.json  
    def add_table(self, df: pd.DataFrame, title: str = None,
                  hide_columns: Union[str, List[str]] = None,
                  filter_by: Union[Tuple, List[Tuple]] = None,
                  sort_by: Union[str, Tuple, List] = None,
                  max_rows_per_table: Optional[Union[int, List[int]]] = None,
                  palette_name: Optional[str] = None,
                  n_rows: Optional[Union[int, List[int]]] = None,
                  source: Optional[str] = None) -> None:
        """PURIFIED add_table - Simple case of add_colored_table without highlights.
        
        This is a clean wrapper around add_colored_table that respects all DIMENSIONES RECTORAS.
        No fallbacks, no mercado negro, pure configuration from JSON files.
        """
        # Delegate to add_colored_table with no highlights - PURE DIMENSIÓN TRANSPARENCIA
        self.add_colored_table(
            df=df,
            title=title,
            highlight_columns=None,  # NO HIGHLIGHTS - simple table
            hide_columns=hide_columns,
            filter_by=filter_by,
            sort_by=sort_by,
            max_rows_per_table=max_rows_per_table,
            palette_name=palette_name,
            n_rows=n_rows,
            source=source,
            _auto_detect_categories=False  # NO auto-detection for simple tables
        )

    # Academic equations with proper numbering
    def add_equation(self, latex_code: str, caption: str = None, label: str = None) -> str:
        """Add numbered equation for academic papers."""
        self.equation_counter += 1
        
        processed_equation = process_mathematical_text(latex_code, self.layout_style, self.sync_files)
        
        if label is None:
            label = f"eq-{self.equation_counter}"
        
        equation_markdown = f"$${processed_equation}$$ {{#{label}}}"
        
        if caption:
            equation_markdown += f"\n\n: {caption}"
            
        equation_markdown += "\n\n"
        self.add_content(equation_markdown)
        return label

    def add_inline_equation(self, latex_code: str) -> None:
        """Add inline equation (not numbered)."""
        processed_equation = process_mathematical_text(latex_code, self.layout_style, self.sync_files)
        inline_equation = f"${processed_equation}$"
        
        # Add inline without line breaks
        if self.content_buffer and not self.content_buffer[-1].endswith('\n\n'):
            self.content_buffer[-1] = self.content_buffer[-1].rstrip() + inline_equation
        else:
            self.content_buffer.append(inline_equation)

    def add_equation_block(self, equations: List[str], caption: str = None,
                          label: str = None, align: bool = True) -> str:
        """Add block of multiple aligned equations."""
        self.equation_counter += 1
        
        if label is None:
            label = f"eq-block-{self.equation_counter}"
        
        processed_equations = [process_mathematical_text(eq, self.layout_style, self.sync_files) 
                             for eq in equations]
        
        if align:
            equations_text = " \\\\\n".join(processed_equations)
            equation_markdown = f"$$\\begin{{aligned}}\n{equations_text}\n\\end{{aligned}}$$ {{#{label}}}"
        else:
            equations_text = " \\\\\n".join(processed_equations)
            equation_markdown = f"$$\\begin{{gather}}\n{equations_text}\n\\end{{gather}}$$ {{#{label}}}"
            
        if caption:
            equation_markdown += f"\n\n: {caption}"
            
        equation_markdown += "\n\n"
        self.add_content(equation_markdown)
        return label

    # Complete notes and callouts collection from ReportWriter
    def add_note(self, content: str, title: str = None) -> str:
        """Add informational note callout with visual display."""
        self.note_renderer.display_callout(content, "note", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "note", title)
        self.add_content(callout_markdown)
        return "note"

    def add_tip(self, content: str, title: str = None) -> str:
        """Add tip callout with visual display."""
        self.note_renderer.display_callout(content, "tip", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "tip", title)
        self.add_content(callout_markdown)
        return "tip"

    def add_warning(self, content: str, title: str = None) -> str:
        """Add warning callout with visual display."""
        self.note_renderer.display_callout(content, "warning", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "warning", title)
        self.add_content(callout_markdown)
        return "warning"

    def add_error(self, content: str, title: str = None) -> str:
        """Add error callout with visual display."""
        self.note_renderer.display_callout(content, "error", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "error", title)
        self.add_content(callout_markdown)
        return "error"
        
    def add_success(self, content: str, title: str = None) -> str:
        """Add success callout with visual display."""
        self.note_renderer.display_callout(content, "success", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "success", title)
        self.add_content(callout_markdown)
        return "success"

    def add_caution(self, content: str, title: str = None) -> str:
        """Add caution callout with visual display."""
        self.note_renderer.display_callout(content, "caution", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "caution", title)
        self.add_content(callout_markdown)
        return "caution"

    def add_important(self, content: str, title: str = None) -> str:
        """Add important callout with visual display."""
        self.note_renderer.display_callout(content, "important", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "important", title)
        self.add_content(callout_markdown)
        return "important"

    def add_information(self, content: str, title: str = None) -> str:
        """Add information callout with visual display."""
        self.note_renderer.display_callout(content, "info", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "info", title)
        self.add_content(callout_markdown)
        return "info"

    def add_recommendation(self, content: str, title: str = None) -> str:
        """Add recommendation callout with visual display."""
        self.note_renderer.display_callout(content, "rec", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "rec", title)
        self.add_content(callout_markdown)
        return "rec"

    def add_advice(self, content: str, title: str = None) -> str:
        """Add advice callout with visual display."""
        self.note_renderer.display_callout(content, "advice", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "advice", title)
        self.add_content(callout_markdown)
        return "advice"

    def add_risk(self, content: str, title: str = None) -> str:
        """Add risk callout with visual display."""
        self.note_renderer.display_callout(content, "risk", title)
        callout_markdown = self.note_renderer.create_note_markdown(content, "risk", title)
        self.add_content(callout_markdown)
        return "risk"

    # Code chunks - same as ReportWriter
    def add_chunk(self, code: str, language: str = 'python', 
                  caption: Optional[str] = None, label: Optional[str] = None) -> None:
        """Add non-executable code chunk to article (display only).
        
        Args:
            code: Code content as multiline string
            language: Programming language (python, javascript, sql, etc.)
            caption: Optional caption for the code block
            label: Optional label for cross-referencing
        """
        from ePy_docs.components.code import format_display_chunk
        
        chunk_content = format_display_chunk(code, language, caption, label)
        self.add_content(chunk_content)

    def add_chunk_executable(self, code: str, language: str = 'python', 
                            caption: Optional[str] = None, label: Optional[str] = None) -> None:
        """Add executable code chunk to article (will be executed by Quarto).
        
        Args:
            code: Code content as multiline string
            language: Programming language (python, javascript, r, etc.)
            caption: Optional caption for the code block
            label: Optional label for cross-referencing
        """
        from ePy_docs.components.code import format_executable_chunk
        
        chunk_content = format_executable_chunk(code, language, caption, label)
        self.add_content(chunk_content)

    # Images and plots - enhanced for articles
    def add_plot(self, fig: plt.Figure, title: str = None, caption: str = None, source: str = None) -> str:
        """Add matplotlib plot to article using paper.json configuration."""
        import os
        
        self.figure_counter += 1
        
        # Create figures directory if it doesn't exist
        figures_dir = os.path.join(self.output_dir, "figures")
        os.makedirs(figures_dir, exist_ok=True)
        
        # Save plot image
        img_filename = f"fig-{self.figure_counter}.png"
        img_path = os.path.join(figures_dir, img_filename)
        
        # Save the matplotlib figure
        fig.savefig(img_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        
        # Create relative path for markdown
        rel_path = os.path.relpath(img_path, self.output_dir).replace('\\', '/')
        
        # Create figure ID for cross-referencing
        figure_id = f"fig-{self.figure_counter}"
        
        # Format caption
        if title and caption:
            full_caption = f"{title}. {caption}"
        elif title:
            full_caption = title
        elif caption:
            full_caption = caption
        else:
            full_caption = f"Figura {self.figure_counter}"
        
        # Add source if provided
        if source:
            full_caption += f". Fuente: {source}"
        
        # Create Quarto-compatible figure markdown
        figure_markdown = f"\n![{full_caption}]({rel_path}){{#{figure_id}}}\n\n: {full_caption}\n\n"
        
        self.add_content(figure_markdown)
        display_in_notebook(img_path, self.show_in_notebook)
        
        return img_path

    def add_image(self, path: str, caption: str = None, width: str = None,
                  alt_text: str = None, align: str = None, label: str = None, source: str = None) -> str:
        """Add external image to article using paper.json configuration."""
        from ePy_docs.components.images import copy_and_process_image, format_image_markdown
        
        self.figure_counter += 1
        
        # Copy and process image using paper output directory
        dest_path = copy_and_process_image(path, self.output_dir, self.figure_counter)
        
        # Format image markdown using images.json configuration
        figure_markdown, figure_id = format_image_markdown(
            dest_path, self.figure_counter, caption, width, alt_text, align, label, source, self.output_dir
        )
        
        self.add_content(figure_markdown)
        display_in_notebook(dest_path, self.show_in_notebook)
        
        return figure_id

    # File import methods - same as ReportWriter
    def add_quarto_file(self, file_path: str, include_yaml: bool = False, fix_image_paths: bool = True) -> None:
        """Import and include content from an existing Quarto (.qmd) file.
        
        Args:
            file_path: Path to the .qmd file to import
            include_yaml: Whether to include YAML frontmatter (default: False)
            fix_image_paths: Whether to automatically fix image paths (default: True)
        """
        from ePy_docs.files.importer import process_quarto_file, format_imported_content
        
        content, self.figure_counter = process_quarto_file(
            file_path=file_path,
            include_yaml=include_yaml,
            fix_image_paths=fix_image_paths,
            output_dir=self.output_dir,
            figure_counter=self.figure_counter
        )
        
        formatted_content = format_imported_content(content)
        self.add_content(formatted_content)

    def add_markdown_file(self, file_path: str, fix_image_paths: bool = True) -> None:
        """Import and include content from an existing Markdown (.md) file.
        
        Args:
            file_path: Path to the .md file to import
            fix_image_paths: Whether to automatically fix image paths (default: True)
        """
        from ePy_docs.files.importer import process_markdown_file, format_imported_content
        
        content, self.figure_counter = process_markdown_file(
            file_path=file_path,
            fix_image_paths=fix_image_paths,
            output_dir=self.output_dir,
            figure_counter=self.figure_counter
        )
        
        formatted_content = format_imported_content(content)
        self.add_content(formatted_content)

    # Cross-references and citations - same as ReportWriter
    def add_reference(self, ref_type: str, ref_id: str, custom_text: str = None) -> str:
        """Add cross-reference to figure, table, equation, or note."""
        from ePy_docs.components.references import format_cross_reference
        
        if ref_type == 'note':
            reference = self.note_renderer.create_cross_reference(ref_id, custom_text)
        else:
            reference = format_cross_reference(ref_type, ref_id, custom_text)
        
        self.add_content(reference)
        return reference

    def add_citation(self, citation_key: str, page: str = None) -> str:
        """Add inline citation."""
        from ePy_docs.components.references import format_citation
        
        citation = format_citation(citation_key, page)
        # Add inline content without line breaks
        if self.content_buffer and not self.content_buffer[-1].endswith('\n\n'):
            self.content_buffer[-1] = self.content_buffer[-1].rstrip() + citation
        else:
            self.content_buffer.append(citation)
        return citation

    # Document Generation for articles
    def generate(self, markdown: bool = False, html: bool = True, pdf: bool = True, 
                qmd: bool = True, tex: bool = False,
                output_filename: str = None) -> None:
        """Generate article in requested formats using paper.json configuration.
        
        Args:
            markdown: Generate .md file
            html: Generate .html file
            pdf: Generate .pdf file
            qmd: Generate .qmd file (Quarto Markdown)
            tex: Generate .tex file (LaTeX)
            output_filename: Custom filename for output files (without extension)
        """
        
        # Prepare content
        content = ''.join(self.content_buffer)
        
        # Use clean generator for HTML/PDF (academic formatting)
        if html or pdf:
            from ePy_docs.components.generator import generate_documents_clean
            from ePy_docs.components.project_info import get_constitutional_project_info
            
            # Get project title from constitutional configuration
            constitutional_info = get_constitutional_project_info(document_type="paper", sync_files=self.sync_files)
            title = constitutional_info['project']['name']  # Use constitutional paper title
            
            # CONSTITUTIONAL: Use paper_name instead of hardcoded fallback
            constitutional_filename = output_filename or self.paper_name
            
            generate_documents_clean(
                content=content,
                title=title,
                html=html,
                pdf=pdf,
                output_filename=constitutional_filename,
                sync_files=self.sync_files,
                layout_name=self.layout_style,
                output_dir=self.output_dir,
                document_type="paper"
            )
        
        # Use original generator for markdown/qmd/tex if needed
        if markdown or qmd or tex:
            from ePy_docs.components.generator import generate_documents
            from ePy_docs.components.pages import set_current_layout
            
            # Temporarily set the layout for compatibility with original generator
            set_current_layout(self.layout_style)
        # Use original generator for markdown/qmd/tex if needed
        if markdown or qmd or tex:
            from ePy_docs.components.generator import generate_documents
            from ePy_docs.components.pages import set_current_layout
            
            # Temporarily set the layout for compatibility with original generator
            set_current_layout(self.layout_style)
            
            # CONSTITUTIONAL: Use paper_name instead of hardcoded fallback
            constitutional_filename = output_filename or self.paper_name
            
            generate_documents(
                content=content,
                file_path=self.file_path,
                markdown=markdown,
                html=False,  # Already handled above
                pdf=False,   # Already handled above
                qmd=qmd,
                tex=tex,
                output_filename=constitutional_filename,
                sync_files=self.sync_files,
                output_dir=self.output_dir,
                document_type="paper"
            )

    def add_colored_table(self, df: pd.DataFrame, title: str = None,
                          highlight_columns: Optional[List[str]] = None,
                          hide_columns: Union[str, List[str]] = None,
                          filter_by: Union[Tuple, List[Tuple]] = None,
                          sort_by: Union[str, Tuple, List] = None,
                          max_rows_per_table: Optional[Union[int, List[int]]] = None,
                          palette_name: Optional[str] = None,
                          n_rows: Optional[int] = None,
                          source: Optional[str] = None,
                          _auto_detect_categories: bool = True) -> None:
        """Add colored table to article using paper.json configuration + tables.json.
        
        Args:
            df: DataFrame to process.
            title: Table title.
            highlight_columns: Columns to highlight (not yet implemented).
            hide_columns: Columns to hide from display.
            filter_by: Filter criteria for rows.
            sort_by: Sort criteria.
            max_rows_per_table: Maximum rows per table or list for multiple subtables [20, 20, 20].
            palette_name: Color palette (not yet implemented).
            n_rows: Number of rows to display (simple integer limit).
            source: Data source attribution.
            _auto_detect_categories: Internal parameter for category detection.
        """
        from ePy_docs.components.tables import process_table_for_report
        
        # Process DataFrame
        processed_df = df.copy()
        
        # Handle MultiIndex DataFrames for proper table display
        if isinstance(df.columns, pd.MultiIndex) or isinstance(df.index, pd.MultiIndex):
            processed_df = _prepare_multiindex_dataframe(processed_df)
        
        # Apply hiding columns
        if hide_columns:
            columns_to_hide = [hide_columns] if isinstance(hide_columns, str) else hide_columns
            processed_df = processed_df.drop(columns=[col for col in columns_to_hide if col in processed_df.columns])
        
        # Apply filtering - PURIFIED: Handle single values and lists properly
        if filter_by:
            filters = [filter_by] if isinstance(filter_by, tuple) else filter_by
            for column, values in filters:
                if column in processed_df.columns:
                    if isinstance(values, (list, tuple)):
                        # Multiple values: use isin for proper filtering
                        processed_df = processed_df[processed_df[column].isin(values)]
                    else:
                        # Single value: direct comparison
                        processed_df = processed_df[processed_df[column] == values]
        
        # Apply sorting
        if sort_by:
            if isinstance(sort_by, str):
                processed_df = processed_df.sort_values(sort_by)
            elif isinstance(sort_by, tuple) and len(sort_by) == 2:
                column, order = sort_by
                ascending = order.lower() in ['asc', 'ascending']
                processed_df = processed_df.sort_values(column, ascending=ascending)
        
        # Apply row limiting sequentially: first n_rows, then max_rows_per_table
        create_multi_tables = False
        rows_distribution = None
        
        # Step 1: Apply n_rows if provided (simple row limiting)
        if n_rows and isinstance(n_rows, int):
            processed_df = processed_df.head(n_rows)
        
        # Step 2: Apply max_rows_per_table to the current DataFrame (after n_rows if applied)
        if max_rows_per_table and isinstance(max_rows_per_table, list):
            # Multiple subtables functionality
            create_multi_tables = True
            rows_distribution = max_rows_per_table
        elif max_rows_per_table and isinstance(max_rows_per_table, int):
            # Additional row limit on top of n_rows (if n_rows was applied)
            processed_df = processed_df.head(max_rows_per_table)
        
        if create_multi_tables:
            # Create multiple subtables based on max_rows_per_table list
            current_row = 0
            part_number = 1
            
            for table_size in rows_distribution:
                if current_row >= len(processed_df):
                    break
                    
                # Get data slice for this subtable
                end_row = min(current_row + table_size, len(processed_df))
                subtable_data = processed_df.iloc[current_row:end_row]
                
                if len(subtable_data) == 0:
                    break
                
                # Process this subtable as a regular table
                self.table_counter += 1
                image_path, figure_id = process_table_for_report(
                    data=subtable_data,
                    title=None,  # We'll handle title in caption
                    output_dir=None,  # Use Reino SETUP tables directory
                    figure_counter=self.table_counter,
                    layout_style=self.layout_style,
                    sync_files=False,
                    highlight_columns=highlight_columns,
                    palette_name=palette_name,
                    auto_detect_categories=_auto_detect_categories,
                    document_type="paper"
                )
                
                # Generate simple caption for multi-table - adapted for articles
                if title:
                    caption_text = f"Table {self.table_counter}: {title} (Part {part_number})"
                else:
                    caption_text = f"Table {self.table_counter} (Part {part_number})"
                
                # Add source if provided
                if source:
                    caption_text += f". Source: {source}"
                
                # Generate relative path for markdown
                if os.path.isabs(image_path):
                    rel_path = os.path.relpath(image_path, self.output_dir).replace('\\', '/')
                else:
                    abs_image_path = os.path.abspath(image_path)
                    abs_output_dir = os.path.abspath(self.output_dir)
                    rel_path = os.path.relpath(abs_image_path, abs_output_dir).replace('\\', '/')
                
                # Create Quarto-compatible table markdown with cross-reference
                table_markdown = f"\n{caption_text}\n\n![{caption_text}]({rel_path}){{#{figure_id}}}\n\n"
                
                # Add to content
                self.add_content(table_markdown)
                
                # Display in notebook using official REINO IMAGES function
                display_in_notebook(image_path, self.show_in_notebook)
                
                current_row = end_row
                part_number += 1
            
            # Handle remaining data if any
            if current_row < len(processed_df):
                remaining_data = processed_df.iloc[current_row:]
                if len(remaining_data) > 0:
                    # Process remaining data as final subtable
                    self.table_counter += 1
                    image_path, figure_id = process_table_for_report(
                        data=remaining_data,
                        title=None,
                        output_dir=None,
                        figure_counter=self.table_counter,
                        layout_style=self.layout_style,
                        sync_files=False,
                        highlight_columns=highlight_columns,
                        palette_name=palette_name,
                        auto_detect_categories=_auto_detect_categories,
                        document_type="paper"
                    )
                    
                    # Generate caption for remaining data
                    if title:
                        caption_text = f"Table {self.table_counter}: {title} (Part {part_number})"
                    else:
                        caption_text = f"Table {self.table_counter} (Part {part_number})"
                    
                    if source:
                        caption_text += f". Source: {source}"
                    
                    # Generate relative path for markdown
                    if os.path.isabs(image_path):
                        rel_path = os.path.relpath(image_path, self.output_dir).replace('\\', '/')
                    else:
                        abs_image_path = os.path.abspath(image_path)
                        abs_output_dir = os.path.abspath(self.output_dir)
                        rel_path = os.path.relpath(abs_image_path, abs_output_dir).replace('\\', '/')
                    
                    # Create Quarto-compatible table markdown with cross-reference
                    table_markdown = f"\n{caption_text}\n\n![{caption_text}]({rel_path}){{#{figure_id}}}\n\n"
                    
                    # Add to content
                    self.add_content(table_markdown)
                    
                    # Display in notebook using official REINO IMAGES function
                    display_in_notebook(image_path, self.show_in_notebook)
        else:
            # Single table generation using paper.json + tables.json configuration
            self.table_counter += 1
            
            image_path, figure_id = process_table_for_report(
                data=processed_df,
                title=title,
                output_dir=None,  # Use Reino SETUP tables directory
                figure_counter=self.table_counter,
                layout_style=self.layout_style,
                sync_files=False,
                highlight_columns=highlight_columns,
                palette_name=palette_name,
                auto_detect_categories=_auto_detect_categories,
                document_type="paper"
            )
            
            # Format table for article with proper Quarto cross-referencing
            caption_text = title if title else f"Table {self.table_counter}"
            if source:
                caption_text += f" {source}"
            
            # Generate relative path for markdown
            if os.path.isabs(image_path):
                rel_path = os.path.relpath(image_path, self.output_dir).replace('\\', '/')
            else:
                abs_image_path = os.path.abspath(image_path)
                abs_output_dir = os.path.abspath(self.output_dir)
                rel_path = os.path.relpath(abs_image_path, abs_output_dir).replace('\\', '/')
            
            # Create Quarto-compatible table markdown with cross-reference
            table_markdown = f"\n: {caption_text}\n\n![{caption_text}]({rel_path}){{#{figure_id}}}\n\n"
            
            # Add to content using pure WriteFiles method
            self.add_content(table_markdown)
            
            # Display in notebook using official REINO IMAGES function
            display_in_notebook(image_path, self.show_in_notebook)

    def save_file(self, file_path: Optional[str] = None, format_type: str = "md") -> str:
        """Save paper using constitutional paper_name from paper.json.
        
        This method has EXCLUSIVE ACCESS to paper_name from paper.json.
        NO OTHER component should access paper_name directly.
        
        Args:
            file_path: Optional specific path, if None uses paper_name from paper.json
            format_type: File format (md, pdf, qmd)
            
        Returns:
            Path where file was saved
        """
        if file_path is None:
            # Use constitutional paper_name access
            filename = f"{self.paper_name}.{format_type}"
            file_path = os.path.join(self.output_dir, filename)
        
        # Get content and save
        content = self.get_content()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Constitutional paper saved: {file_path}")
        print(f"Paper name used: {self.paper_name}")
        
        return file_path

