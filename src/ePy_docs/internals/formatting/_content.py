"""
CONTENT Module - Unified content processing

Configuration: Centralized cache via _load_cached_files
Styling: Organization by layout_styles
Compatibility: No backward compatibility, no fallbacks

Unified content processing for text, tables, and images.
"""

from typing import Dict, Any, Optional, Union, List, Tuple
import os
import pandas as pd
import re
import shutil
from pathlib import Path

# Import from internal data module
from ePy_docs.internals.data_processing._data import load_cached_files
from ePy_docs.config.setup import _resolve_config_path, get_absolute_output_directories

# Import auxiliary image generation functions
from ePy_docs.internals.formatting._tables_image import (
    _create_table_image,
    _process_table_for_report,
    _create_split_table_images
)


def get_content_config(content_type: str) -> Dict[str, Any]:
    """Get content configuration for different types."""
    from ePy_docs.config.setup import get_config_section
    return get_config_section(content_type)


def add_content_type(content_type: str, content_data: Any, **kwargs) -> Tuple[str, int, List[str]]:
    """
    Generic function to add content of different types.

    Args:
        content_type: Type of content ('text', 'table', 'image', 'equation', etc.)
        content_data: The content data (string, DataFrame, path, etc.)
        **kwargs: Additional parameters specific to content type

    Returns:
        Tuple of (markdown_content, updated_counter, generated_images)
    """
    if content_type == 'text':
        return _add_text_content(content_data, **kwargs)
    elif content_type == 'table':
        return _add_table_content(content_data, **kwargs)
    elif content_type == 'colored_table':
        return _add_colored_table_content(content_data, **kwargs)
    elif content_type == 'image':
        return _add_image_content(content_data, **kwargs)
    elif content_type == 'header':
        return _add_header_content(content_data, **kwargs)
    elif content_type == 'list':
        return _add_list_content(content_data, **kwargs)
    else:
        raise ValueError(f"Unsupported content type: {content_type}")


def _add_text_content(text: str, **kwargs) -> Tuple[str, int, List[str]]:
    """Add text content."""
    processed_content = _process_text_content(text)
    return processed_content, 0, []  # No counter increment, no images


def _add_table_content(df: pd.DataFrame, **kwargs) -> Tuple[str, int, List[str]]:
    """Add simple table content."""
    title = kwargs.get('title')
    dpi = kwargs.get('dpi', 300)
    palette_name = kwargs.get('palette_name', 'YlOrRd')
    hide_columns = kwargs.get('hide_columns')
    layout_style = kwargs.get('layout_style', "corporate")
    document_type = kwargs.get('document_type', "report")
    table_counter = kwargs.get('table_counter', 0)

    try:
        from ePy_docs.internals.data_processing._dataframes import prepare_dataframe_for_display
        df, _ = prepare_dataframe_for_display(df, apply_unit_conversion=False)

        # Increment counter FIRST
        table_counter += 1

        output_dirs = get_absolute_output_directories(document_type=document_type)
        tables_dir = output_dirs.get('tables', 'results/tables')
        os.makedirs(tables_dir, exist_ok=True)

        img_path = _create_table_image(
            data=df,
            title=title,
            output_dir=tables_dir,
            filename=None,
            layout_style=layout_style,
            highlight_columns=[],
            palette_name=palette_name,
            auto_detect_categories=False,
            document_type=document_type
        )

        qmd_execution_dir = output_dirs.get('output')

        try:
            rel_path = os.path.relpath(img_path, qmd_execution_dir)
            rel_path = rel_path.replace(os.sep, '/')
        except (ValueError, TypeError):
            img_path_obj = Path(img_path)
            tables_dir_name = os.path.basename(output_dirs['tables'])
            rel_path = f"{tables_dir_name}/{img_path_obj.name}"

        # Caption WITHOUT "Tabla X:" prefix
        caption = title if title else f"Tabla {table_counter}"
        table_id = f"tbl-{table_counter}"
        markdown_content = f"\n\n![{caption}]({rel_path}){{#{table_id}}}\n\n"

        return markdown_content, table_counter, [img_path]

    except Exception as e:
        fallback_content = f"\n\n**Table: {title or 'Table'}**\n\n*(Table image could not be generated)*\n\nError: {str(e)}\n\n"
        return fallback_content, table_counter, []


def _add_colored_table_content(df: pd.DataFrame, **kwargs) -> Tuple[str, int, List[str]]:
    """Add colored table content."""
    title = kwargs.get('title')
    palette_name = kwargs.get('palette_name')
    highlight_columns = kwargs.get('highlight_columns')
    dpi = kwargs.get('dpi', 300)
    hide_columns = kwargs.get('hide_columns')
    split_large_tables = kwargs.get('split_large_tables', True)
    max_rows_per_table = kwargs.get('max_rows_per_table')
    layout_style = kwargs.get('layout_style', "corporate")
    document_type = kwargs.get('document_type', "report")
    table_counter = kwargs.get('table_counter', 0)
    
    # Check if unit conversion libraries are available
    try:
        from ePy_units import UnitConverter
        unit_conversion_available = True
    except ImportError:
        unit_conversion_available = False

    apply_unit_conversion = kwargs.get('apply_unit_conversion', unit_conversion_available)

    # Units are now handled by user - no conversion applied
    from ePy_docs.internals.data_processing._dataframes import prepare_dataframe_for_display
    df, _ = prepare_dataframe_for_display(df, apply_unit_conversion=False)

    # Increment counter
    table_counter += 1

    output_dirs = get_absolute_output_directories(document_type=document_type)
    tables_dir = output_dirs.get('tables', 'results/tables')
    os.makedirs(tables_dir, exist_ok=True)

    # Detect categories if not specified
    if highlight_columns is None:
        category_name, highlight_columns = _detect_table_category(df)

    img_paths = _create_table_image(
        data=df,
        title=title,
        output_dir=tables_dir,
        filename=None,
        layout_style=layout_style,
        highlight_columns=highlight_columns or [],
        palette_name=palette_name,
        auto_detect_categories=True,
        document_type=document_type,
        split_large_tables=split_large_tables,
        max_rows_per_table=max_rows_per_table
    )

    if isinstance(img_paths, str):
        img_paths = [img_paths]

    qmd_execution_dir = output_dirs.get('output')

    markdown_parts = []
    for i, img_path in enumerate(img_paths):
        try:
            rel_path = os.path.relpath(img_path, qmd_execution_dir)
            rel_path = rel_path.replace(os.sep, '/')
        except (ValueError, TypeError):
            img_path_obj = Path(img_path)
            tables_dir_name = os.path.basename(output_dirs['tables'])
            rel_path = f"{tables_dir_name}/{img_path_obj.name}"

        if len(img_paths) > 1:
            caption = f"{title or f'Tabla {table_counter}'} (Parte {i+1})"
        else:
            caption = title if title else f"Tabla {table_counter}"

        table_id = f"tbl-{table_counter}" if i == 0 else f"tbl-{table_counter}-{i+1}"
        markdown_parts.append(f"\n\n![{caption}]({rel_path}){{#{table_id}}}\n\n")

    return ''.join(markdown_parts), table_counter, img_paths


def _add_image_content(img_path: str, **kwargs) -> Tuple[str, int, List[str]]:
    """Add image content."""
    title = kwargs.get('title')
    caption = kwargs.get('caption')
    image_id = kwargs.get('image_id')
    fig_width = kwargs.get('fig_width')
    alt_text = kwargs.get('alt_text')
    responsive = kwargs.get('responsive', True)
    document_type = kwargs.get('document_type', "report")
    figure_counter = kwargs.get('figure_counter', 0)

    # Increment counter
    figure_counter += 1

    # Copy image to output directory
    processed_path = _copy_image_to_output_directory(img_path, figure_counter, document_type)

    # Build attributes
    attributes = []

    if image_id:
        attributes.append(f'#{image_id}')

    if fig_width:
        attributes.append(f'fig-width={fig_width}')

    # Create markdown
    markdown_parts = []

    if title:
        markdown_parts.append(f"### {title}\n")

    if attributes:
        attr_string = ' {' + ' '.join(attributes) + '}'
        image_markdown = f"![{alt_text or caption or ''}]({processed_path}){attr_string}"
    else:
        image_markdown = f"![{alt_text or caption or ''}]({processed_path})"

    markdown_parts.append(image_markdown)

    return "\n\n" + "\n".join(markdown_parts) + "\n\n", figure_counter, [processed_path]


def _add_header_content(text: str, **kwargs) -> Tuple[str, int, List[str]]:
    """Add header content."""
    level = kwargs.get('level', 1)
    color = kwargs.get('color')

    if level < 1 or level > 6:
        level = 1

    header_prefix = "#" * level
    return f"\n{header_prefix} {text}\n\n", 0, []


def _add_list_content(items: List[str], **kwargs) -> Tuple[str, int, List[str]]:
    """Add list content."""
    ordered = kwargs.get('ordered', False)

    if ordered:
        list_content = "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
    else:
        list_content = "\n".join(f"- {item}" for item in items)

    return f"\n{list_content}\n\n", 0, []


# Helper functions from original modules

def _detect_table_category(df: pd.DataFrame) -> tuple[str, Optional[List[str]]]:
    """Detect table category based on column names and content."""
    config = get_content_config('tables')
    category_rules = config.get('category_rules', {})

    for category_name, rules in category_rules.items():
        keywords = rules.get('keywords', [])
        highlight_cols = rules.get('highlight_columns', [])

        # Check if any column contains keywords
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword.lower() in col_lower for keyword in keywords):
                return category_name, highlight_cols

    return 'default', None


def _copy_image_to_output_directory(img_path: str, figure_counter: int, document_type: str = "report") -> str:
    """Copy image to output directory with sequential naming."""
    if not img_path or not os.path.exists(img_path):
        return _process_image_path(img_path)

    output_dirs = get_absolute_output_directories(document_type=document_type)
    figures_dir = output_dirs['figures']
    os.makedirs(figures_dir, exist_ok=True)

    path_obj = Path(img_path)
    extension = path_obj.suffix

    sequential_filename = f"figure_{figure_counter}{extension}"
    dest_path = os.path.join(figures_dir, sequential_filename)

    shutil.copy2(img_path, dest_path)
    return dest_path


def _process_image_path(img_path: str) -> str:
    """Process image path for LaTeX compatibility."""
    if not img_path:
        return img_path

    # Convert backslashes to forward slashes for LaTeX
    return img_path.replace('\\', '/')


def _process_text_content(text: str) -> str:
    """Process text content with mathematical notation."""
    if not text:
        return ""

    if not isinstance(text, str):
        text = str(text)

    result = text.strip()

    # Process mathematical notation
    try:
        from ePy_docs.internals.formatting._format import format_superscripts

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


def _create_table_image(data: pd.DataFrame, title: str = None, output_dir: str = None,
                       filename: str = None, layout_style: str = "corporate",
                       highlight_columns: Optional[List[str]] = None,
                       palette_name: str = None, auto_detect_categories: bool = True,
                       document_type: str = "report", split_large_tables: bool = True,
                       max_rows_per_table: Optional[int] = None):
    """Create table image - unified from tables module."""
    from ePy_docs.internals.formatting._tables_image import _create_table_image as create_table_image_impl
    
    return create_table_image_impl(
        data=data,
        title=title,
        output_dir=output_dir,
        filename=filename,
        layout_style=layout_style,
        highlight_columns=highlight_columns,
        palette_name=palette_name,
        auto_detect_categories=auto_detect_categories,
        document_type=document_type
    )