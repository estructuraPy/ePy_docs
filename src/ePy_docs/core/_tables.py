"""
SOLID Architecture Tables Module - True SOLID Principles Implementation

This module implements pure SOLID architecture for table processing:
- Single Responsibility: Each class handles one specific aspect of table processing
- Open/Closed: Extensible via configuration, not code modification  
- Liskov Substitution: Clean interface implementations
- Interface Segregation: Focused, minimal interfaces
- Dependency Inversion: Depends on abstractions, not concrete implementations

Architecture Components:
- TableConfigManager: Configuration loading and validation
- FontManager: Font selection and cell font configuration
- ColorManager: Color palette management and cell coloring  
- CellFormatter: Cell formatting, content detection, and styling
- ImageRenderer: Table image generation with matplotlib
- MarkdownGenerator: Markdown content generation
- TableOrchestrator: Main coordinator with facade pattern

Performance: Optimized caching, lazy loading, and resource management
Memory: Efficient matplotlib usage with proper cleanup
Extensibility: Configuration-driven behavior, zero hardcoded values
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
from matplotlib.transforms import Bbox
from typing import Dict, Any, Union, List, Optional, Tuple, Protocol
from pathlib import Path
from abc import ABC, abstractmethod

from ePy_docs.core._data import (
    DataProcessor, TableAnalyzer, TablePreparation, 
    TableDimensionCalculator, TableContentAnalyzer
)
from ePy_docs.core._format import TextProcessor, FormatConfig, TableTextWrapper
from ePy_docs.core._config import get_absolute_output_directories, get_layout
from ePy_docs.core._images import convert_rgb_to_matplotlib, get_palette_color_by_tone, setup_matplotlib_fonts

# Import from consolidated table core module
from ._table_core import (
    configure_matplotlib_for_tables, TableConfigManager,
    FontManager, ColorManager, CellFormatter
)


# ============================================================================
# SOLID ARCHITECTURE - IMAGE RENDERING AND TABLE PROCESSOR
# ============================================================================


class ImageRenderer:
    """
    SOLID: Single Responsibility - Handles matplotlib table image generation.
    
    Responsibilities:
    - Matplotlib figure and table creation
    - Image rendering and saving
    - DPI and size optimization
    - Memory management and cleanup
    """
    
    def __init__(self, config_manager: TableConfigManager):
        """Initialize with configuration manager dependency."""
        self._config_manager = config_manager
    
    def _process_superscripts_static(self, text: str) -> str:
        """Process superscripts in text - delegate to CellFormatter static method."""
        return CellFormatter._process_superscripts_static(text)
    
    def create_table_image(self, data: Union[pd.DataFrame, List[List]], 
                          width_inches: float,
                          title: str = None, layout_style: str = "corporate",
                          output_dir: str = None, table_number: int = 1,
                          document_type: str = None,
                          highlight_columns: Optional[Union[str, List[str]]] = None,
                          colored: bool = False,
                          palette_name: Optional[str] = None) -> str:
        """Create table image and return the file path."""
        # Setup matplotlib and get configured font list
        configured_font_list = self._setup_matplotlib(layout_style)
        
        # Convert data to DataFrame if needed
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Validate required parameter
        if not document_type:
            raise ValueError("Missing required parameter 'document_type'")
        
        font_config, colors_config, style_config, table_config, code_config, font_family, text_wrapping_config = \
            self._config_manager.get_layout_config(layout_style, document_type)
        
        # Calculate dimensions
        width_inches = width_inches or self._calculate_width(df, style_config)
        height_inches = self._calculate_height(df, style_config)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(width_inches, height_inches))
        ax.axis('tight')
        ax.axis('off')
        
        try:
            # Create matplotlib table with layout colors
            table, bold_cells = self._create_matplotlib_table(ax, df, font_config, style_config, colors_config)
            
            # Apply formatting - use the configured font list from matplotlib setup
            cell_formatter = CellFormatter(
                FontManager(self._config_manager),
                ColorManager(self._config_manager)
            )
            
            # Use the font list that was configured in matplotlib setup
            font_list = configured_font_list if configured_font_list else self._get_font_list(font_family, font_config)
            cell_formatter.format_table_cells(
                table, df, font_list, font_config, layout_style, code_config, text_wrapping_config
            )
            
            # CRITICAL: Re-apply bold styling AFTER formatting may have reset it
            for (row, col) in bold_cells:
                if (row, col) in table.get_celld():
                    table[(row, col)].get_text().set_fontweight('bold')
            
            # CRITICAL: Apply fonts to the entire figure (including title and all text elements)
            from ePy_docs.core._images import apply_fonts_to_figure
            apply_fonts_to_figure(fig, font_list)
            
            # Apply colors if requested
            if highlight_columns or colored:
                color_manager = ColorManager(self._config_manager)
                color_manager.apply_table_colors(
                    table, df, style_config, colors_config,
                    highlight_columns, palette_name, colored
                )
            
            # Skip adding title to figure - use caption in markdown instead
            # This avoids duplicate titles (one in image, one in caption)
            
            # Save image
            output_path = self._save_image(fig, output_dir, table_number, title, document_type, colors_config)
            
            return output_path
            
        finally:
            # Clean up matplotlib resources thoroughly
            try:
                plt.close(fig)
                # Force garbage collection to free memory
                import gc
                gc.collect()
            except Exception:
                pass  # Ignore cleanup errors
    
    def _setup_matplotlib(self, layout_style: str):
        """Setup matplotlib with optimal settings and error handling."""
        try:
            # Ensure matplotlib uses non-interactive backend
            import matplotlib
            matplotlib.use('Agg', force=True)
            
            # Configure fonts from layout configuration
            font_list = setup_matplotlib_fonts(layout_style)
            
            # Explicitly enable font fallback settings
            from matplotlib import rcParams
            
            # Set the font family list from configuration - NO hardcoded fallbacks
            if font_list and isinstance(font_list, list):
                rcParams['font.sans-serif'] = font_list
            else:
                raise ValueError("No font configuration available from layout")
                
            rcParams['font.family'] = 'sans-serif'
            
            # CRITICAL: Enable font fallback to avoid errors
            rcParams['svg.fonttype'] = 'none'  # Use fonts as text, not paths
            rcParams['pdf.fonttype'] = 42  # Use TrueType fonts in PDF
            rcParams['ps.fonttype'] = 42   # PostScript fonts
            
            # Memory and performance settings
            rcParams['figure.max_open_warning'] = 0  # Disable warnings about too many figures
            rcParams['axes.unicode_minus'] = False   # Prevent Unicode minus issues
            
            # Ensure matplotlib uses proper font fallback policy
            import matplotlib.font_manager as fm
            if hasattr(fm, 'fontManager'):
                # Refresh font manager to apply changes - but safely
                try:
                    fm.fontManager._rebuild()
                except (AttributeError, OSError, RuntimeError):
                    pass  # Ignore font manager errors
            
            return font_list if font_list else ['Arial', 'sans-serif']
            
        except Exception as e:
            # No hardcoded fallbacks - raise error to force proper configuration
            raise ValueError(f"Font setup failed for layout '{layout_style}': {e}")
    
    def _create_matplotlib_table(self, ax, df: pd.DataFrame, font_config: Dict, style_config: Dict, colors_config: Dict = None):
        """Create the basic matplotlib table with layout-specific styling."""
        import re
        
        # Track bold cells (row_idx, col_idx) -> is_bold
        bold_cells = {}
        
        # Pre-process DF to find bold markers and strip them IN-PLACE so Formatter sees clean text
        for row_idx in range(len(df)):
            for col_idx in range(len(df.columns)):
                cell_value = df.iloc[row_idx, col_idx]
                original_cell = str(cell_value) if cell_value is not None else ""
                
                # Check for bold markdown
                cleaned_cell = original_cell
                is_bold = False
                
                if '**' in original_cell:
                    cleaned_cell = re.sub(r'\*\*(.*?)\*\*', r'\1', original_cell)
                    is_bold = True
                    bold_cells[(row_idx + 1, col_idx)] = True  # +1 for header offset
                elif '<strong>' in original_cell:
                     cleaned_cell = original_cell.replace('<strong>', '').replace('</strong>', '')
                     is_bold = True
                     bold_cells[(row_idx + 1, col_idx)] = True
                
                # Update DF in-place with CLEAN text
                if is_bold:
                    df.iloc[row_idx, col_idx] = cleaned_cell

        # Prepare data for table with superscript processing (now using clean DF)
        processed_headers = []
        for col_idx, col_name in enumerate(df.columns):
            header_str = str(col_name)
            # Check headers for bold too
            if '**' in header_str:
                header_str = re.sub(r'\*\*(.*?)\*\*', r'\1', header_str)
                bold_cells[(0, col_idx)] = True
            elif '<strong>' in header_str:
                header_str = header_str.replace('<strong>', '').replace('</strong>', '')
                bold_cells[(0, col_idx)] = True
            
            # Process superscripts
            processed_headers.append(self._process_superscripts_static(header_str))
            
            # Update DF column name (if possible, but changing columns is tricky inside loop)
            # Actually, we don't need to update df.columns for Formatter if Formatter uses df.columns directly
            # Formatter reads df.columns. If we don't update it, Formatter sees **Bold**.
            # We should try to rename columns if possible. But renaming columns in pandas returns new DF.
            # We can set df.columns = new_cols
        
        # Update columns in DF
        # We need original column names stripped of bold markers
        clean_col_names = []
        for col_name in df.columns:
            s = str(col_name)
            if '**' in s: s = re.sub(r'\*\*(.*?)\*\*', r'\1', s)
            if '<strong>' in s: s = s.replace('<strong>', '').replace('</strong>', '')
            clean_col_names.append(s)
        df.columns = clean_col_names
            
        processed_data = []
        for row_idx in range(len(df)):
            processed_row = []
            for col_idx in range(len(df.columns)):
                # Read from modified DF (clean text)
                cell_value = df.iloc[row_idx, col_idx]
                original_cell = str(cell_value) if cell_value is not None else ""
                processed_cell = self._process_superscripts_static(original_cell)
                processed_row.append(processed_cell)
            processed_data.append(processed_row)
        
        # Configure matplotlib globally for Unicode support
        configure_matplotlib_for_tables()
        
        # Create table with processed data
        table = ax.table(
            cellText=processed_data,  # Processed data rows
            colLabels=processed_headers,  # Processed header row
            cellLoc='center',
            loc='center',
            bbox=[0, 0, 1, 1]
        )
        
        # Ensure Unicode fonts are applied to all cells with superscripts or Greek letters
        for (row, col), cell in table.get_celld().items():
            cell_text = cell.get_text().get_text()
            # Check for Unicode characters or Greek letters
            if any(ord(c) > 127 for c in cell_text) or any(c in 'αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩσ' for c in cell_text):
                # Force DejaVu Sans font on cells with special characters
                cell.get_text().set_fontname('DejaVu Sans')
                cell.get_text().set_fontfamily(['DejaVu Sans', 'STIXGeneral'])
        
        # Basic table styling
        table.auto_set_font_size(False)
        
        # Get font size from configuration - expect new structure
        if 'element_typography' not in font_config:
            raise ValueError(
                "Missing 'element_typography' in font_config. "
                "Text configuration must include 'element_typography.tables.content.size'"
            )
        
        tables_typo = font_config['element_typography'].get('tables', {})
        if 'content' not in tables_typo or 'size' not in tables_typo['content']:
            raise ValueError(
                "Missing 'element_typography.tables.content.size' in font_config. "
                f"Available: {list(tables_typo.keys())}"
            )
        
        font_size = tables_typo['content']['size']
        table.set_fontsize(font_size)
        
        # CRITICAL: Apply font family to each cell individually
        # Get font list from configuration
        if 'primary' not in font_config:
            raise ValueError(
                f"font_config must have 'primary' key. Found: {list(font_config.keys())}"
            )
        
        font_list = [font_config['primary']]
        if 'fallback' in font_config:
            font_list.append(font_config['fallback'])
        
        # Apply font family and BOLD styling to all cells
        for (row, col), cell in table.get_celld().items():
            cell.get_text().set_fontfamily(font_list)
            # Apply bold if detected
            if (row, col) in bold_cells:
                 cell.get_text().set_fontweight('bold')
        
        # Intelligent scaling - let matplotlib auto-adjust column widths, focus on height
        table.auto_set_column_width(list(range(len(df.columns))))  # Auto-size all columns
        table.scale(1.2, 1.1)  # Moderate scaling with auto column sizing
        
        # Apply layout-specific colors
        self._apply_table_layout_colors(table, df, colors_config)
        
        return table, bold_cells
    
    def _apply_table_layout_colors(self, table, df: pd.DataFrame, colors_config: Dict = None):
        """Apply layout-specific colors to table headers and cells."""
        if not colors_config:
            return
        
        if 'palette' not in colors_config:
            return
        
        palette = colors_config['palette']
        
        # Get primary color for headers
        # Validate required colors exist in palette
        required_colors = ['table_header', 'table_header_text', 'table_stripe', 'table_background']
        missing_colors = [c for c in required_colors if c not in palette]
        if missing_colors:
            raise ValueError(
                f"Palette must have {required_colors}. Missing: {missing_colors}"
            )
        
        # Get table header colors
        header_color = palette['table_header']
        header_text_color = palette['table_header_text']
        
        if not isinstance(header_color, list) or len(header_color) < 3:
            raise ValueError(
                f"table_header color must be list with at least 3 RGB values. Got: {header_color}"
            )
        
        if not isinstance(header_text_color, list) or len(header_text_color) < 3:
            raise ValueError(
                f"table_header_text color must be list with at least 3 RGB values. Got: {header_text_color}"
            )
        
        header_rgb = [c/255.0 for c in header_color[:3]]  # Convert to matplotlib format
        header_text_rgb = [c/255.0 for c in header_text_color[:3]]
        
        # Get stripe color for alternate rows
        stripe_color = palette['table_stripe']
        stripe_text_color = palette.get('table_stripe_text', palette.get('page_text', [0, 0, 0]))
        
        if not isinstance(stripe_color, list) or len(stripe_color) < 3:
            raise ValueError(
                f"table_stripe color must be list with at least 3 RGB values. Got: {stripe_color}"
            )
        
        if not isinstance(stripe_text_color, list) or len(stripe_text_color) < 3:
            raise ValueError(
                f"table_stripe_text color must be list with at least 3 RGB values. Got: {stripe_text_color}"
            )
        
        stripe_rgb = [c/255.0 for c in stripe_color[:3]]
        stripe_text_rgb = [c/255.0 for c in stripe_text_color[:3]]
        
        # Get background color for regular rows
        background_color = palette['table_background']
        background_text_color = palette.get('table_background_text', palette.get('page_text', [0, 0, 0]))
        
        if not isinstance(background_color, list) or len(background_color) < 3:
            raise ValueError(
                f"table_background color must be list with at least 3 RGB values. Got: {background_color}"
            )
        
        if not isinstance(background_text_color, list) or len(background_text_color) < 3:
            raise ValueError(
                f"table_background_text color must be list with at least 3 RGB values. Got: {background_text_color}"
            )
        
        background_rgb = [c/255.0 for c in background_color[:3]]
        background_text_rgb = [c/255.0 for c in background_text_color[:3]]
        
        # Apply header colors
        num_cols = len(df.columns)
        for col in range(num_cols):
            header_cell = table[(0, col)]
            header_cell.set_facecolor(header_rgb)
            header_cell.get_text().set_color(header_text_rgb)
        
        # Apply alternating row colors with text colors
        num_rows = len(df)
        for row in range(1, num_rows + 1):  # Skip header row (0)
            if row % 2 == 0:  # Even rows - apply stripe
                for col in range(num_cols):
                    cell = table[(row, col)]
                    cell.set_facecolor(stripe_rgb)
                    cell.get_text().set_color(stripe_text_rgb)
            else:  # Odd rows - apply background
                for col in range(num_cols):
                    cell = table[(row, col)]
                    cell.set_facecolor(background_rgb)
                    cell.get_text().set_color(background_text_rgb)
    
    def _calculate_width(self, df: pd.DataFrame, style_config: Dict) -> float:
        """Calculate optimal table width based on content and configuration.
        
        Delegates to TableContentAnalyzer for consistent logic.
        
        Raises:
            ValueError: If width_in not found in style_config
        """
        if 'width_in' not in style_config:
            raise ValueError(
                f"Missing 'width_in' in style_config. "
                f"Tables configuration must include 'styling.width_in'. "
                f"Available keys: {list(style_config.keys())}"
            )
        
        base_width = style_config['width_in']
        return TableContentAnalyzer.calculate_optimal_width(df, base_width, style_config)
    
    def _calculate_height(self, df: pd.DataFrame, style_config: Dict) -> float:
        """Calculate optimal table height based on content and wrapping.
        
        Delegates to TableContentAnalyzer for consistent logic.
        """
        base_row_height = style_config.get('row_height_in', 0.3)
        return TableContentAnalyzer.calculate_optimal_height(df, base_row_height)
    
    def _get_font_list(self, font_family: str, font_config: Dict = None) -> List[str]:
        """Get font list for the specified font family from configuration.
        
        Raises:
            ValueError: If font configuration is incomplete
        """
        # Font config should have primary and fallback from text configuration
        if not font_config:
            raise ValueError("font_config is required")
        
        if 'primary' not in font_config:
            raise ValueError(
                f"Missing 'primary' in font_config. "
                f"Text configuration must include font primary and fallback. "
                f"Available keys: {list(font_config.keys())}"
            )
        
        fonts = [font_config['primary']]
        if 'fallback' in font_config:
            fonts.append(font_config['fallback'])
        
        return fonts
    
    def _add_title(self, fig, title: str, font_config: Dict):
        """Add title to the figure.
        
        Raises:
            ValueError: If title size not found in font_config
        """
        if 'element_typography' not in font_config:
            raise ValueError(
                "Missing 'element_typography' in font_config. "
                "Text configuration must include 'element_typography.tables.title.size'"
            )
        
        tables_typo = font_config['element_typography'].get('tables', {})
        if 'title' not in tables_typo or 'size' not in tables_typo['title']:
            raise ValueError(
                "Missing 'element_typography.tables.title.size' in font_config"
            )
        
        title_size = tables_typo['title']['size']
        fig.suptitle(title, fontsize=title_size, fontweight='bold', y=0.95)
    
    def _save_image(self, fig, output_dir: str, table_number: int, title: str = None, document_type: str = 'report', colors_config: Dict = None) -> str:
        """Save the figure and return the file path."""
        if not output_dir:
            abs_dirs = get_absolute_output_directories(document_type)
            if 'tables' not in abs_dirs:
                raise ValueError("Missing 'tables' directory in output configuration")
            output_dir = abs_dirs['tables']
        
        # Ensure output directory exists
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Generate filename - simplified to just table_number
        # Title information is preserved in the caption/markdown
        filename = f"table_{table_number}.png"
        
        output_path = Path(output_dir) / filename
        
        # Get background color from palette (default to white if not available)
        bg_color = 'white'
        if colors_config and 'palette' in colors_config:
            palette = colors_config['palette']
            if 'page_background' in palette:
                bg_rgb = palette['page_background']
                if isinstance(bg_rgb, list) and len(bg_rgb) >= 3:
                    # Convert RGB [0-255] to matplotlib format [0-1]
                    bg_color = [c/255.0 for c in bg_rgb[:3]]
        
        # Save with high quality
        fig.savefig(
            output_path,
            dpi=300,
            bbox_inches='tight',
            pad_inches=0.1,
            facecolor=bg_color,
            edgecolor='none'
        )
        
        return str(output_path)


class MarkdownGenerator:
    """
    SOLID: Single Responsibility - Generates markdown content for tables.
    
    Responsibilities:
    - Markdown formatting for single and split tables
    - Image reference generation
    - Caption and numbering management
    - Output format optimization
    """
    
    def __init__(self):
        """Initialize markdown generator."""
        pass
    
    def _escape_latex(self, text: str) -> str:
        """Escape LaTeX special characters in text.
        
        Args:
            text: Text to escape
            
        Returns:
            Text with LaTeX special characters escaped
        """
        if not text:
            return text
            
        # Escape special LaTeX characters
        replacements = {
            '\\': '\\textbackslash{}',
            '{': '\\{',
            '}': '\\}',
            '$': '\\$',
            '&': '\\&',
            '%': '\\%',
            '#': '\\#',
            '_': '\\_',
            '^': '\\textasciicircum{}',
            '~': '\\textasciitilde{}',
        }
        
        result = text
        # Handle backslash first to avoid escaping our escape sequences
        if '\\' in result:
            result = result.replace('\\', replacements['\\'])
        
        # Then handle other characters
        for char, replacement in replacements.items():
            if char != '\\' and char in result:
                result = result.replace(char, replacement)
        
        return result
    
    def generate_table_markdown(self, image_paths: Union[str, List[str]], 
                               caption: str = None, table_number: int = 1,
                               document_columns: int = 1, label: str = None, language: str = 'es') -> str:
        """Generate markdown content for table(s).
        
        Args:
            image_paths: Path or list of paths to table images
            caption: Table caption
            table_number: Table number for referencing
            document_columns: Total number of columns in the document layout
            label: Custom label for cross-referencing. If None, uses table_number.
            language: Language for translations ('en' or 'es')
        """
        
        if isinstance(image_paths, str):
            return self._generate_single_table_markdown(image_paths, caption, table_number, 
                                                       document_columns, label=label)
        else:
            return self._generate_split_table_markdown(image_paths, caption, table_number,
                                                       document_columns, label=label, language=language)
    
    def _generate_single_table_markdown(self, image_path: str, caption: str, table_number: int,
                                       document_columns: int = 1, label: str = None) -> str:
        """Generate markdown for a single table in Quarto format.
        
        Uses Quarto's Figure format but with a 'tbl-' label prefix. This makes
        Quarto treat the image as a Table (numbered as Tabla X) but without
        the visual borders of a pipe table.
        
        Args:
            image_path: Path to table image
            caption: Table caption
            table_number: Table number
            document_columns: Total columns in document
            label: Custom label for cross-referencing. If None, uses table_number.
                   May or may not include the 'tbl-' prefix; it will be normalized.
        """
        # Extract relative path for markdown
        rel_path = self._get_relative_path(image_path)
        
        # Full width for single-column documents
        width_str = "100%"
        
        # Normalize label: strip 'tbl-' prefix if already present to avoid double-prefixing
        if label:
            clean_label = label[4:] if label.startswith('tbl-') else label
            label_id = f"tbl-{clean_label}"
        else:
            label_id = f"tbl-{table_number}"
        
        # Quarto Figure format with tbl- prefix: ![Caption](path){#tbl-id}
        # This removes unwanted table borders while keeping Table numbering.
        if caption:
            return f"\n\n![{caption}]({rel_path}){{#{label_id} width={width_str}}}\n\n"
        else:
            return f"\n\n![]({rel_path}){{#{label_id} width={width_str}}}\n\n"
    
    def _generate_split_table_markdown(self, image_paths: List[str], caption: str, table_number: int,
                                      document_columns: int = 1, label: str = None, language: str = 'es') -> str:
        """Generate markdown for split tables in Quarto format.
        
        Args:
            image_paths: List of paths to table images
            caption: Table caption
            table_number: Starting table number
            document_columns: Total columns in document
            label: Custom label for cross-referencing. If None, uses table_number.
                  For split tables, appends part number (e.g., 'results-1', 'results-2')
            language: Language for 'Part' translation ('en' or 'es')
        """
        from ePy_docs.core._project import get_translation
        
        markdown_parts = []
        num_parts = len(image_paths)
        
        # Full width for single-column documents
        width_str = "100%"
        
        # Get translation for "Part"
        part_text = get_translation('part', language)
        
        for i, image_path in enumerate(image_paths):
            rel_path = self._get_relative_path(image_path)
            
            # Normalize label: strip 'tbl-' prefix if already present to avoid double-prefixing
            if label:
                clean_label = label[4:] if label.startswith('tbl-') else label
                label_id = f"tbl-{clean_label}-{i+1}" if num_parts > 1 else f"tbl-{clean_label}"
            else:
                label_id = f"tbl-{table_number + i}"
            
            # Quarto Figure format with tbl- prefix
            # This removes unwanted table borders while keeping Table numbering.
            if caption:
                part_caption = f"{caption} - {part_text} {i+1}/{num_parts}"
                markdown_parts.append(f"![{part_caption}]({rel_path}){{#{label_id} width={width_str}}}")
            else:
                markdown_parts.append(f"![]({rel_path}){{#{label_id} width={width_str}}}")
        
        # Add TWO line breaks before first table for proper PDF spacing
        return "\n\n" + "\n\n".join(markdown_parts) + "\n\n"
    
    def _get_relative_path(self, image_path: str) -> str:
        """Convert absolute path to relative path for markdown, optimized for new structure."""
        path = Path(image_path)
        
        try:
            # Get the filename
            filename = path.name
            
            # Try to make relative to current directory
            rel_path = path.relative_to(Path.cwd())
            rel_str = str(rel_path).replace('\\', '/')
            
            # New structure handling: results/document_type/tables/filename
            # QMD is in results/document_type/, so table path should be tables/filename
            if 'results/' in rel_str and '/tables/' in rel_str:
                # Extract the part after /tables/
                tables_index = rel_str.find('/tables/')
                return f"tables/{filename}"
            elif 'results/' in rel_str and '/figures/' in rel_str:
                # Extract the part after /figures/
                figures_index = rel_str.find('/figures/')
                return f"figures/{filename}"
            elif rel_str.startswith('results/'):
                # Legacy handling - if old structure, try to maintain compatibility
                if rel_str.count('/') == 1:  # results/filename
                    return f"tables/{filename}"
                else:
                    # Extract document type and assume it's a table
                    parts = rel_str.split('/')
                    if len(parts) >= 3:
                        return f"tables/{filename}"
            
            return rel_str
            
        except ValueError:
            # If can't make relative, assume it's a table
            return f"tables/{path.name}"


class TableOrchestrator:
    """
    SOLID: Facade Pattern - Main coordinator for table processing operations.
    
    Responsibilities:
    - Coordinate all table processing components
    - Provide simple public API
    - Handle component lifecycle and dependencies
    - Manage error handling and fallbacks
    """
    
    def __init__(self):
        """Initialize with dependency injection of all components."""
        self._config_manager = TableConfigManager()
        self._font_manager = FontManager(self._config_manager)
        self._color_manager = ColorManager(self._config_manager)
        self._cell_formatter = CellFormatter(self._font_manager, self._color_manager)
        self._image_renderer = ImageRenderer(self._config_manager)
        self._markdown_generator = MarkdownGenerator()
    
    def create_table_image_and_markdown(self, df: pd.DataFrame, caption: str = None,
                                       layout_style: str = "corporate", output_dir: str = None,
                                       table_number: int = 1, columns: Union[float, List[float], None] = None,
                                       document_type: str = None,
                                       document_columns: int = 1,
                                       max_rows_per_table: Union[int, List[int], None] = None,
                                       highlight_columns: Optional[Union[str, List[str]]] = None,
                                       colored: bool = False,
                                       palette_name: Optional[str] = None,
                                       hide_columns: Union[str, List[str], None] = None,
                                       filter_by: Dict[str, Any] = None,
                                       sort_by: Union[str, List[str], None] = None,
                                       label: str = None,
                                       language: str = 'es') -> Tuple[str, Union[str, List[str]], int]:
        """
        Main public API for table processing.
        
        Args:
            df: DataFrame containing table data
            caption: Table caption/title
            layout_style: Layout style name
            output_dir: Output directory for table image
            table_number: Table number for counter
            columns: Width specification for multi-column layouts
            document_type: Required - Type of document (paper, report, book, notebook)
            document_columns: Total number of columns in the document layout
            max_rows_per_table: Maximum rows per table before splitting (int or list)
            highlight_columns: Columns to highlight with color gradient
            colored: Whether to apply coloring to table
            palette_name: Color palette name for highlighting
            label: Custom label for cross-referencing (e.g., 'results'). Will be formatted as 'tbl-{label}'.
                   If None, uses table_number (e.g., 'tbl-1')
            
        Returns:
            Tuple of (markdown_content, image_path_or_paths, new_counter)
        """
        try:
            # Validate required parameter
            if not document_type:
                raise ValueError("Missing required parameter 'document_type'")
            
            # Prepare data (filter, sort, hide columns) - solo si hay parámetros para procesar
            from ePy_docs.core._data import TablePreparation
            if hide_columns or filter_by or sort_by:
                # Solo procesar si hay parámetros específicos
                processed_df = TablePreparation.prepare_table_data(
                    df, hide_columns=hide_columns, filter_by=filter_by, sort_by=sort_by
                )
            else:
                # Si no hay parámetros, usar el DataFrame tal como viene (ya puede estar procesado)
                processed_df = df
            
            # Calculate width from columns parameter
            width_inches = TableContentAnalyzer.calculate_width_from_columns(columns, document_type)
            
            # Validate and convert max_rows_per_table type
            if max_rows_per_table is not None:
                if isinstance(max_rows_per_table, float):
                    max_rows_per_table = int(max_rows_per_table)
                elif isinstance(max_rows_per_table, list):
                    max_rows_per_table = [int(x) if isinstance(x, float) else x for x in max_rows_per_table]
            
            # Check if table needs to be split
            should_split = False
            table_chunks = None
            
            if max_rows_per_table:
                # Handle list input for max_rows_per_table
                if isinstance(max_rows_per_table, list):
                    # Always split when list is provided
                    should_split = True
                else:
                    # Split only if table exceeds max_rows
                    should_split = len(processed_df) > max_rows_per_table
                
                if should_split:
                    from ePy_docs.core._data import TablePreparation
                    table_chunks = TablePreparation.split_for_rendering(processed_df, max_rows_per_table)
            
            else:
                # New dynamic height logic - Automatic splitting
                # Get styles to calculate height
                font_config, colors_config, style_config, table_config, code_config, font_family, text_wrapping_config = \
                    self._config_manager.get_layout_config(layout_style, document_type)
                 
                # New dynamic height logic - Automatic splitting
                # Get styles
                font_config, colors_config, style_config, table_config, code_config, font_family, text_wrapping_config = \
                    self._config_manager.get_layout_config(layout_style, document_type)
                 
                # Default max height 9.0 inches (fits A4 with margins) or config
                max_height = style_config.get('page_height_in', 9.0)
                
                # Use split_by_height to check if splitting is needed (more accurate than _calculate_height)
                from ePy_docs.core._data import TablePreparation
                base_height = style_config.get('row_height_in', 0.3)
                
                potential_chunks = TablePreparation.split_by_height(processed_df, max_height, base_height)
                
                if len(potential_chunks) > 1:
                    should_split = True
                    table_chunks = potential_chunks
                else:
                    should_split = False
            
            if should_split and table_chunks:
                return self._process_split_table(
                    processed_df, caption, layout_style, output_dir, table_number, 
                    width_inches, max_rows_per_table, document_type,
                    document_columns, highlight_columns, colored, palette_name, 
                    label=label, language=language, table_chunks=table_chunks
                )
            
            return self._process_single_table(
                processed_df, caption, layout_style, output_dir, table_number, 
                width_inches, document_type, document_columns,
                highlight_columns, colored, palette_name, label=label, language=language
            )
                
        except Exception as e:
            # Error handling with informative message
            raise RuntimeError(f"Table processing failed: {e}")
    
    def _process_single_table(self, df: pd.DataFrame, caption: str, layout_style: str,
                             output_dir: str, table_number: int, width_inches: float,
                             document_type: str,
                             document_columns: int, highlight_columns: Optional[Union[str, List[str]]],
                             colored: bool, palette_name: Optional[str], label: str = None, language: str = 'es') -> Tuple[str, str, int]:
        """Process a single table."""
        # Generate table image
        image_path = self._image_renderer.create_table_image(
            df, width_inches, caption, layout_style, output_dir, table_number,
            document_type, highlight_columns, colored, palette_name
        )
        
        # Generate markdown
        markdown_content = self._markdown_generator.generate_table_markdown(
            image_path, caption, table_number, document_columns, label=label, language=language
        )
        
        return markdown_content, image_path, table_number
    
    def _process_split_table(self, df: pd.DataFrame, caption: str, layout_style: str,
                            output_dir: str, table_number: int, width_inches: float,
                            max_rows_per_table: Union[int, List[int]],
                            document_type: str,
                            document_columns: int, highlight_columns: Optional[Union[str, List[str]]],
                            colored: bool, palette_name: Optional[str], label: str = None, 
                            language: str = 'es', table_chunks: List[pd.DataFrame] = None) -> Tuple[str, List[str], int]:
        """Process a table that needs to be split."""
        
        # Use provided chunks or split using legacy max_rows
        if table_chunks is None:
            # Split DataFrame into chunks using centralized logic from _data.py
            from ePy_docs.core._data import TablePreparation
            table_chunks = TablePreparation.split_for_rendering(df, max_rows_per_table)
        
        # Generate images for each chunk
        image_paths = []
        current_table_number = table_number
        
        for i, chunk in enumerate(table_chunks):
            # Calculate part caption
            if language == 'es':
                part_suffix = f" (Parte {i+1})"
            else:
                part_suffix = f" (Part {i+1})"
                
            part_caption = f"{caption}{part_suffix}" if caption else None
            
            image_path = self._image_renderer.create_table_image(
                chunk, width_inches, part_caption, layout_style, output_dir, 
                current_table_number,
                document_type, highlight_columns, colored, palette_name
            )
            
            image_paths.append(image_path)
            if i < len(table_chunks) - 1:  # Only increment if not last chunk
                current_table_number += 1
        
        # Generate combined markdown
        markdown_content = self._markdown_generator.generate_table_markdown(
            image_paths, caption, table_number, document_columns, label=label, language=language
        )
        
        return markdown_content, image_paths, current_table_number


# ============================================================================
# GLOBAL ORCHESTRATOR INSTANCE
# ============================================================================

table_orchestrator = TableOrchestrator()
