"""Tables public API with centralized configuration.

This module provides the public API for table processing and rendering.
All image generation logic is delegated to the auxiliary module _tables_image.

Public functions:
- get_tables_config(): Load table configuration
- detect_table_category(): Detect table category for auto-highlighting  
- create_table_image(): Create table image
- add_table_to_content(): Add simple table to markdown content
- add_colored_table_to_content(): Add colored table to markdown content
"""

import os
import pandas as pd
from typing import Dict, Any, Union, List, Optional, Tuple

# Import from internal data module
from ePy_docs.internals.data_processing._data import load_cached_files
from ePy_docs.config.setup import _resolve_config_path, get_absolute_output_directories

# Import auxiliary image generation functions
from ePy_docs.internals.formatting._tables_image import (
    _create_table_image,
    _process_table_for_report,
    _create_split_table_images
)


def get_tables_config() -> Dict[str, Any]:
    '''Load centralized table configuration.
    
    Returns:
        Complete tables configuration dictionary.
    '''
    from ePy_docs.config.config_manager import ConfigManager
    cm = ConfigManager()
    return cm.get_config('tables')


def detect_table_category(df: pd.DataFrame) -> tuple[str, Optional[List[str]]]:
    '''Detect table category based on column names and content using category_rules.
    
    Args:
        df: DataFrame to analyze.
        
    Returns:
        Tuple of (category_name, highlight_columns).
    '''
    config = get_tables_config()
    category_rules = config.get('category_rules', {})
    
    # Analyze column names for category detection
    column_names_lower = [col.lower() for col in df.columns]
    column_text = ' '.join(column_names_lower)
    
    category_scores = {}
    potential_highlight_columns = {}
    
    for category, rules in category_rules.items():
        if category == 'general':
            continue  # Skip general category in scoring
            
        score = 0
        highlight_cols = []
        
        # Score based on name keywords
        for keyword in rules.get('name_keywords', []):
            keyword_lower = keyword.lower()
            if keyword_lower in column_text:
                score += 2  # Higher weight for exact matches
                # Find columns containing this keyword
                for col in df.columns:
                    if keyword_lower in col.lower():
                        highlight_cols.append(col)
            elif any(keyword_lower in col_name for col_name in column_names_lower):
                score += 1  # Lower weight for partial matches
        
        # Score based on coordinate patterns (for nodes category)
        if 'coordinate_patterns' in rules:
            for pattern in rules['coordinate_patterns']:
                if pattern.lower() in column_text:
                    score += 3  # High weight for coordinate patterns
                    for col in df.columns:
                        if pattern.lower() in col.lower():
                            highlight_cols.append(col)
        
        if score > 0:
            category_scores[category] = score
            potential_highlight_columns[category] = list(set(highlight_cols))  # Remove duplicates
    
    # Return highest scoring category or general if no match
    if category_scores:
        best_category = max(category_scores, key=category_scores.get)
        return best_category, potential_highlight_columns.get(best_category, [])
    else:
        return 'general', []


def create_table_image(data: Union[pd.DataFrame, List[List]], 
                      title: str = None, output_dir: str = None, 
                      filename: str = None, layout_style: str = "corporate", 
                      highlight_columns: Optional[List[str]] = None,
                      palette_name: Optional[str] = None,
                      auto_detect_categories: bool = False,
                      document_type: str = "report") -> str:
    '''Create table as image using centralized configuration.
    
    Delegates to _create_table_image auxiliary function.
    '''
    return _create_table_image(
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


def add_table_to_content(df: pd.DataFrame, title: str = None,
                        dpi: int = 300, palette_name: str = 'YlOrRd',
                        hide_columns: Union[str, List[str]] = None,
                        layout_style: str = "corporate",
                        document_type: str = "report",
                        table_counter: int = 0,
                        **kwargs) -> Tuple[str, int, List[str]]:
    '''Generate table markdown content with images.
    
    Args:
        df: DataFrame to display
        title: Optional title for the table
        dpi: Image resolution
        palette_name: Color palette (not used for simple tables)
        hide_columns: Column name(s) to hide from the table
        layout_style: Layout style from 8 universal options
        document_type: Document type for output directory resolution
        table_counter: Current table counter for numbering
    
    Returns:
        Tuple of (markdown_content, updated_table_counter, generated_image_paths)
    '''
    try:
        # Increment counter FIRST to ensure it updates even if image generation fails
        table_counter += 1
        
        output_dirs = get_absolute_output_directories(document_type=document_type)
        tables_dir = output_dirs.get('tables', 'results/tables')
        os.makedirs(tables_dir, exist_ok=True)
        
        img_path = create_table_image(
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
        
        from pathlib import Path
        qmd_execution_dir = output_dirs.get('output')
        
        try:
            rel_path = os.path.relpath(img_path, qmd_execution_dir)
            rel_path = rel_path.replace(os.sep, '/')
        except (ValueError, TypeError):
            img_path_obj = Path(img_path)
            tables_dir_name = os.path.basename(output_dirs['tables'])
            rel_path = f"{tables_dir_name}/{img_path_obj.name}"
        
        # Caption WITHOUT "Tabla X:" prefix (Quarto adds numbering automatically)
        caption = title if title else f"Tabla {table_counter}"
        table_id = f"tbl-{table_counter}"
        markdown_content = f"\n\n![{caption}]({rel_path}){{#{table_id}}}\n\n"
        
        return markdown_content, table_counter, [img_path]
        
    except Exception as e:
        fallback_content = f"\n\n**Table: {title or 'Table'}**\n\n*(Table image could not be generated)*\n\nError: {str(e)}\n\n"
        return fallback_content, table_counter, []


def add_colored_table_to_content(df: pd.DataFrame, title: str = None,
                                palette_name: str = None, 
                                highlight_columns: Optional[List[str]] = None,
                                dpi: int = 300,
                                hide_columns: Union[str, List[str]] = None,
                                split_large_tables: bool = True,
                                max_rows_per_table: Optional[int] = None,
                                layout_style: str = "corporate",
                                document_type: str = "report",
                                table_counter: int = 0,
                                **kwargs) -> Tuple[str, int, List[str]]:
    '''Generate colored table markdown content with images.
    
    Args:
        df: DataFrame to display
        title: Optional title for the table
        palette_name: Color palette for numeric columns
        highlight_columns: Columns to apply intelligent coloring to
        dpi: Image resolution
        hide_columns: Column name(s) to hide from the table
        split_large_tables: Whether to automatically split large tables
        max_rows_per_table: Maximum rows per table before splitting
        layout_style: Layout style from 8 universal options
        document_type: Document type for output directory resolution
        table_counter: Current table counter for numbering
        
    Returns:
        Tuple of (markdown_content, updated_table_counter, generated_image_paths)
    '''
    # Apply unit conversion if requested
    # Check if unit conversion libraries are available
    # Units are now handled by user - no conversion applied
    from ePy_docs.internals.data_processing._dataframes import prepare_dataframe_for_display
    df, _ = prepare_dataframe_for_display(df, apply_unit_conversion=False)

    if palette_name is None:
        palette_name = 'YlOrRd'
    
    output_dirs = get_absolute_output_directories(document_type=document_type)
    tables_dir = output_dirs['tables']
    os.makedirs(tables_dir, exist_ok=True)
    
    markdown_parts = []
    generated_images = []
    
    try:
        if split_large_tables:
            # Count tables before creating images
            num_tables = len(df) // (max_rows_per_table or 20) + (1 if len(df) % (max_rows_per_table or 20) else 0)
            table_counter += max(1, num_tables)  # Increment counter first
            
            img_paths = _create_split_table_images(
                df=df,
                output_dir=tables_dir,
                base_table_number=table_counter - num_tables + 1,
                title=title,
                highlight_columns=highlight_columns,
                palette_name=palette_name,
                dpi=dpi,
                hide_columns=hide_columns,
                filter_by=None,
                sort_by=None,
                max_rows_per_table=max_rows_per_table,
                layout_style=layout_style,
                document_type=document_type
            )
        else:
            table_counter += 1  # Increment counter FIRST
            
            img_path = create_table_image(
                data=df,
                title=title,
                output_dir=tables_dir,
                filename=None,
                layout_style=layout_style,
                highlight_columns=highlight_columns,
                palette_name=palette_name,
                auto_detect_categories=True,
                document_type=document_type
            )
            img_paths = [img_path]
    except Exception as e:
        # Counter already incremented, so return updated value
        markdown_parts.append(f"\n**Table: {title}**\n\n")
        markdown_parts.append("*(Table image could not be generated)*\n\n")
        markdown_parts.append(f"Error: {str(e)}\n\n")
        return ''.join(markdown_parts), table_counter, []

    config = get_tables_config()
    display_config = config['display']
    
    for i, img_path in enumerate(img_paths):
        from pathlib import Path
        qmd_execution_dir = output_dirs.get('output')
        
        try:
            rel_path = os.path.relpath(img_path, qmd_execution_dir)
            rel_path = rel_path.replace(os.sep, '/')
        except (ValueError, TypeError):
            tables_dir_name = os.path.basename(output_dirs['tables'])
            rel_path = f"{tables_dir_name}/{Path(img_path).name}"
            
        markdown_parts.append("\n\n")
        
        table_number = table_counter - len(img_paths) + i + 1
        # Caption WITHOUT "Tabla X:" prefix (Quarto adds it automatically with {#tbl-X})
        caption = title if title else f"Tabla {table_number}"
        table_id = f"tbl-{table_number}"
        
        if display_config.get('html_responsive', False):
            fig_width = display_config['max_width_inches_html']
            from ePy_docs.internals.styling._colors import get_color_from_path as colors_get_color
            border_color = colors_get_color('blues.medium', format_type='hex')
            shadow_color = colors_get_color('blues.medium', format_type='hex')
            html_classes = "quarto-figure-center table-figure"
            
            # Simplificar atributos para mejor compatibilidad con Quarto
            # Los estilos inline muy largos pueden causar problemas de renderizado
            figure_markdown = f'![{caption}]({rel_path}){{#{table_id} fig-width={fig_width} .{html_classes}}}'
            markdown_parts.append(f'{figure_markdown}\n\n')
        else:
            fig_width = display_config['max_width_inches']
            html_classes = "quarto-figure-center"
            
            # Build Quarto figure markdown as single string
            figure_markdown = f'![{caption}]({rel_path}){{#{table_id} fig-width={fig_width} .{html_classes}}}'
            markdown_parts.append(f'{figure_markdown}\n\n')
        
        generated_images.append(img_path)
    
    return ''.join(markdown_parts), table_counter, generated_images
