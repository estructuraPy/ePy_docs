"""
Table Core Module

Consolidates table configuration, styling, and cell formatting logic.
- TableConfigManager: Handles configuration loading
- FontManager: Handles font selection and sizing
- ColorManager: Handles color palettes and application
- CellFormatter: Handles cell content formatting and layout
"""

import matplotlib.pyplot as plt
from matplotlib import rcParams
from typing import Dict, Any, Tuple, List, Optional, Union
import warnings
import logging
import pandas as pd
from ePy_docs.core._images import convert_rgb_to_matplotlib, get_palette_color_by_tone
from ePy_docs.core._data import TableContentAnalyzer
from ePy_docs.core._format import TableTextWrapper, SuperscriptFormatter, FormatConfig

# ============================================================================
# MATPLOTLIB CONFIGURATION
# ============================================================================

def configure_matplotlib_for_tables():
    """Configure matplotlib globally to handle Unicode and suppress warnings."""
    warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
    warnings.filterwarnings('ignore', message='.*Font.*does not have a glyph.*')
    warnings.filterwarnings('ignore', message='.*Substituting symbol.*')
    
    logging.getLogger('matplotlib.mathtext').setLevel(logging.ERROR)
    logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)
    
    rcParams['font.family'] = 'DejaVu Sans'
    rcParams['font.sans-serif'] = ['DejaVu Sans', 'STIXGeneral', 'Arial Unicode MS', 'Liberation Sans']
    rcParams['mathtext.default'] = 'regular'
    rcParams['mathtext.fontset'] = 'dejavusans'
    rcParams['axes.unicode_minus'] = False
    rcParams['figure.max_open_warning'] = 0
    rcParams['svg.fonttype'] = 'none'
    rcParams['pdf.fonttype'] = 42
    rcParams['ps.fonttype'] = 42


# ============================================================================
# CONFIGURATION MANAGER
# ============================================================================

class TableConfigManager:
    """Handles all table configuration loading and validation."""
    
    def __init__(self, config_provider=None):
        self._config_provider = config_provider
        self._cache = {}
        self._config_cache = None
    
    def get_tables_config(self) -> Dict[str, Any]:
        """Load centralized table configuration (deprecated)."""
        if self._config_cache is not None:
            return self._config_cache
        self._config_cache = {}
        return self._config_cache
    
    def get_layout_config(self, layout_style: str, document_type: str) -> Tuple[Dict, Dict, Dict, Dict, Dict, str, Dict]:
        """Load complete layout configuration for table rendering."""
        cache_key = f"{layout_style}_{document_type}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            from ePy_docs.core._config import load_layout, get_config_section
            layout_config = load_layout(layout_style, resolve_refs=True)
            
            font_family = layout_config.get('font_family')
            font_family_ref = layout_config.get('font_family_ref')
            
            if not font_family and not font_family_ref:
                raise ValueError(f"Layout '{layout_style}' must have 'font_family' or 'font_family_ref'")
            
            font_config = {}
            font_family_info = {}
            
            if font_family and isinstance(font_family, dict):
                font_family_info = {
                    'primary': font_family.get('primary'),
                    'fallback': font_family.get('fallback')
                }
            elif font_family_ref:
                font_families = layout_config.get('font_families', {})
                if font_family_ref not in font_families:
                    raise ValueError(f"Font family '{font_family_ref}' not found in layout")
                font_info = font_families[font_family_ref]
                font_family_info = {
                    'primary': font_info.get('primary'),
                    'fallback': font_info.get('fallback')
                }
            
            typography = layout_config.get('typography', {})
            if not typography:
                raise ValueError(f"Layout '{layout_style}' has no 'typography' section")
            
            if font_family_ref or font_family_info:
                if typography:
                    font_config = {
                        'primary': font_family_info['primary'],
                        'fallback': font_family_info['fallback'],
                        'role_assignments': typography.get('role_assignments', {}),
                        'scales': typography.get('scales', {}),
                        'line_spacing': typography.get('line_spacing', {}),
                        'element_typography': typography.get('element_typography', {})
                    }
                else:
                    font_config = {
                        'primary': font_family_info['primary'],
                        'fallback': font_family_info['fallback'],
                        'element_typography': {'tables': {'content': {'size': 10}, 'header': {'size': 11}}}
                    }
            
            colors_config = layout_config.get('colors', {})
            if 'palette' in layout_config:
                embedded_palette = layout_config['palette']
                flattened_palette = {}
                if 'colors' in embedded_palette: flattened_palette.update(embedded_palette['colors'])
                for section in ['page', 'code', 'table']:
                    if section in embedded_palette:
                        for key, value in embedded_palette[section].items():
                            flattened_palette[f'{section}_{key}'] = value
                if 'border_color' in embedded_palette: flattened_palette['border_color'] = embedded_palette['border_color']
                if 'caption_color' in embedded_palette: flattened_palette['caption_color'] = embedded_palette['caption_color']
                
                colors_config['palette'] = flattened_palette
                colors_config['palettes'] = {layout_style: flattened_palette}
            
            colors_data = get_config_section('colors')
            if 'color_palettes' in colors_data:
                if 'palettes' not in colors_config: colors_config['palettes'] = {}
                colors_config['palettes'].update(colors_data['color_palettes'])
                colors_config['color_palettes'] = colors_data['color_palettes']
            
            table_config = layout_config.get('tables', {})
            style_config = table_config.get('styling', {})
            if not table_config:
                raise ValueError(f"Layout '{layout_style}' has no 'tables' configuration")
            
            code_config = layout_config.get('code', {})
            text_wrapping_config = layout_config.get('format', {}).get('text_wrapping', {'max_width': 80})
            
            result = (font_config, colors_config, style_config, table_config, code_config, font_family, text_wrapping_config)
            self._cache[cache_key] = result
            return result
            
        except Exception as e:
            raise RuntimeError(f"Layout configuration loading failed for {layout_style}: {e}")
    
    def clear_cache(self):
        self._cache.clear()
        self._config_cache = None


# ============================================================================
# FONT MANAGER
# ============================================================================

class FontManager:
    """Manages font selection and cell font configuration."""
    
    def __init__(self, config_manager):
        self._config_manager = config_manager
    
    def configure_cell_font(self, cell, text_value, is_header: bool, font_list: List[str], 
                           layout_style: str, code_config: Dict):
        """Configure specific font for each cell based on its content."""
        is_code_content = self._detect_code_content(text_value, is_header)
        cell.get_text().set_fontfamily(font_list)
        
        if is_header:
            self._apply_header_font(cell, font_list)
        elif self._is_missing_value(text_value):
            self._apply_missing_value_font(cell, font_list)
        elif is_code_content:
            self._apply_code_font(cell, font_list, layout_style, code_config)
        else:
            self._apply_normal_font(cell, font_list)
    
    def auto_adjust_font_size(self, cell, original_font_size: float, num_columns: Optional[int] = None, 
                             num_rows: Optional[int] = None, text_content: str = None,
                             font_config: Dict = None) -> float:
        """Auto-adjust font size based on table dimensions and content."""
        if not font_config or 'auto_adjustment' not in font_config:
            raise ValueError("Missing 'auto_adjustment' in font_config")
        
        rules = font_config['auto_adjustment']
        adjusted_size = original_font_size
        
        if num_columns and 'column_threshold' in rules:
            threshold = rules['column_threshold']
            if num_columns > threshold:
                adjusted_size *= max(rules['column_min_factor'], 1.0 - (num_columns - threshold) * rules['column_factor_per_unit'])
        
        if num_rows and 'row_threshold' in rules:
            threshold = rules['row_threshold']
            if num_rows > threshold:
                adjusted_size *= max(rules['row_min_factor'], 1.0 - (num_rows - threshold) * rules['row_factor_per_unit'])
        
        if text_content and 'content_length_threshold' in rules:
            threshold = rules['content_length_threshold']
            if len(str(text_content)) > threshold:
                adjusted_size *= rules['content_length_factor']
        
        min_size = rules.get('minimum_font_size', 6)
        adjusted_size = max(adjusted_size, min_size)
        
        cell.get_text().set_fontsize(adjusted_size)
        return adjusted_size
    
    def _detect_code_content(self, text_value, is_header: bool) -> bool:
        if is_header or text_value is None: return False
        cell_str = str(text_value)
        code_indicators = ['def ', 'function', 'class ', '()', '{}', '[]', 'import ', 'from ', '=', '==']
        return sum(1 for indicator in code_indicators if indicator in cell_str) >= 2
    
    def _is_missing_value(self, text_value) -> bool:
        if pd.isna(text_value): return True
        return str(text_value).strip().lower() in ['', 'nan', 'none', 'null', '-', '--', '---', 'n/a', 'na']
    
    def _apply_header_font(self, cell, font_list):
        cell.get_text().set_fontfamily(font_list)
        cell.get_text().set_style('normal')
        cell.get_text().set_weight('bold')
    
    def _apply_missing_value_font(self, cell, font_list):
        cell.get_text().set_fontfamily(font_list)
        cell.get_text().set_style('italic')
    
    def _apply_code_font(self, cell, font_list, layout_style, code_config):
        try:
            mono_fonts = ['Courier New', 'Consolas', 'Monaco', 'monospace']
            if layout_style in code_config.get('layout_config', {}):
                code_layout = code_config['layout_config']
                if 'mono_font' in code_layout:
                    mono_fonts = [code_layout['mono_font']['family']] + mono_fonts
            cell.get_text().set_fontfamily(mono_fonts + font_list)
            cell.get_text().set_style('normal')
        except Exception:
            cell.get_text().set_fontfamily(font_list)
            cell.get_text().set_style('normal')
    
    def _apply_normal_font(self, cell, font_list):
        cell.get_text().set_fontfamily(font_list)
        cell.get_text().set_style('normal')


# ============================================================================
# COLOR MANAGER
# ============================================================================

class ColorManager:
    """Manages color palette and cell coloring operations."""
    
    def __init__(self, config_manager):
        self._config_manager = config_manager
        self._color_cache = {}
    
    def load_colors_configuration(self, layout_style: str) -> Dict:
        if layout_style in self._color_cache: return self._color_cache[layout_style]
        try:
            from ePy_docs.core._config import get_config_section
            color_config = get_config_section('colors')
            layouts_config = color_config.get('layouts', {})
            style_colors = layouts_config.get(layout_style, layouts_config.get('minimal'))
            if not style_colors: raise ValueError(f"Layout '{layout_style}' not found")
            self._color_cache[layout_style] = style_colors
            return style_colors
        except Exception as e:
            raise RuntimeError(f"Color configuration loading failed for {layout_style}: {e}")
    
    def apply_table_colors(self, table, df: pd.DataFrame, style_config: Dict, 
                          colors_config: Dict, highlight_columns: Union[str, List[str], None] = None,
                          palette_name: str = None, colored: bool = False) -> None:
        # Set default palette if None
        if palette_name is None:
            palette_name = 'blues'
        
        # Case 1: highlight_columns specified → color only those columns
        if highlight_columns:
            if isinstance(highlight_columns, str):
                highlight_columns = [highlight_columns]
            valid_columns = [col for col in highlight_columns if col in df.columns]
            for col_name in valid_columns:
                self._apply_column_highlighting(table, df, col_name, colors_config, palette_name)
        
        # Case 2: colored=True without highlight_columns → color all columns independently
        elif colored:
            for col_name in df.columns:
                self._apply_column_highlighting(table, df, col_name, colors_config, palette_name)
    
    def _apply_column_highlighting(self, table, df: pd.DataFrame, column_name: str, 
                                  colors_config: Dict, palette_name: str = None):
        if column_name not in df.columns: return
        col_index = df.columns.get_loc(column_name)
        column_data = df[column_name]
        colors = self._generate_color_gradient(column_data, colors_config, palette_name)
        for row_idx, color in enumerate(colors):
            cell = table[(row_idx + 1, col_index)]
            cell.set_facecolor(color)
            cell.get_text().set_color(self._get_contrasting_text_color(color, palette_name, colors_config))
    
    def _generate_color_gradient(self, column_data: pd.Series, colors_config: Dict, 
                                palette_name: str = None) -> List[str]:
        palette_colors = self._get_palette_colors(palette_name or 'blues', colors_config)
        numeric_data = pd.to_numeric(column_data, errors='coerce')
        if numeric_data.isna().all():
            return self._generate_categorical_colors(column_data, palette_colors)
        
        min_val, max_val = numeric_data.min(), numeric_data.max()
        if min_val == max_val: return [palette_colors[0]] * len(column_data)
        
        colors = []
        for value in numeric_data:
            if pd.isna(value):
                colors.append(palette_colors[0] if palette_colors else get_palette_color_by_tone('neutrals', 'primary'))
            else:
                normalized = (value - min_val) / (max_val - min_val)
                color_index = int(normalized * (len(palette_colors) - 1))
                colors.append(palette_colors[color_index])
        return colors
    
    def _get_palette_colors(self, palette_name: str, colors_config: Dict) -> List[str]:
        palettes = colors_config.get('palettes', {})
        if palette_name not in palettes:
            raise ValueError(f"Palette '{palette_name}' not found")
        palette = palettes[palette_name]
        tones = ['primary', 'secondary', 'tertiary', 'quaternary', 'quinary', 'senary']
        colors = []
        for tone in tones:
            if tone in palette:
                color_rgb = palette[tone]
                if isinstance(color_rgb, (list, tuple)) and len(color_rgb) >= 3:
                    r, g, b = [int(c * 255) if c <= 1 else int(c) for c in color_rgb[:3]]
                    colors.append(f'#{r:02X}{g:02X}{b:02X}')
                elif isinstance(color_rgb, str):
                    colors.append(color_rgb)
        if not colors:
            raise ValueError(f"Palette '{palette_name}' has no valid colors")
        return colors
    
    def _get_text_colors_for_palette(self, palette_name: str, colors_config: Dict) -> Dict[str, str]:
        """Get text colors for each tone in a palette."""
        palettes = colors_config.get('palettes', {})
        if palette_name not in palettes:
            raise ValueError(f"Palette '{palette_name}' not found")
        palette = palettes[palette_name]
        
        if 'text_colors' not in palette:
            raise ValueError(f"Palette '{palette_name}' does not have 'text_colors' defined")
        
        return palette['text_colors']
    
    def _generate_categorical_colors(self, column_data: pd.Series, palette_colors: List[str]) -> List[str]:
        unique_values = column_data.unique()
        color_map = {val: palette_colors[i % len(palette_colors)] for i, val in enumerate(unique_values)}
        return [color_map[val] for val in column_data]
    
    def _get_contrasting_text_color(self, background_color: str, palette_name: str, colors_config: Dict) -> str:
        """Get contrasting text color from palette definition."""
        text_colors = self._get_text_colors_for_palette(palette_name, colors_config)
        
        # Find which tone this background color belongs to
        palettes = colors_config.get('palettes', {})
        palette = palettes[palette_name]
        tones = ['primary', 'secondary', 'tertiary', 'quaternary', 'quinary', 'senary']
        
        for tone in tones:
            if tone in palette:
                palette_color = palette[tone]
                # Convert to hex for comparison
                if isinstance(palette_color, (list, tuple)) and len(palette_color) >= 3:
                    r, g, b = [int(c * 255) if c <= 1 else int(c) for c in palette_color[:3]]
                    hex_color = f'#{r:02X}{g:02X}{b:02X}'
                elif isinstance(palette_color, str):
                    hex_color = palette_color.upper()
                else:
                    continue
                
                if hex_color.upper() == background_color.upper():
                    # Found matching tone, return its text color
                    if tone not in text_colors:
                        raise ValueError(f"Text color for tone '{tone}' not found in palette '{palette_name}'")
                    return text_colors[tone]
        
        raise ValueError(f"Background color '{background_color}' not found in palette '{palette_name}'")


# ============================================================================
# CELL FORMATTER
# ============================================================================

class CellFormatter:
    """Handles cell formatting, content detection and styling."""
    
    def __init__(self, font_manager: FontManager, color_manager: ColorManager):
        self._font_manager = font_manager
        self._color_manager = color_manager
    
    def _analyze_column_content(self, df: pd.DataFrame) -> Dict[int, Dict[str, Any]]:
        column_analysis = {}
        for col_idx in range(len(df.columns)):
            header_text = str(df.columns[col_idx])
            header_length = len(header_text)
            column_data = df.iloc[:, col_idx].astype(str)
            data_lengths = [len(str(val)) for val in column_data if str(val) not in ['nan', 'None', '']]
            
            if data_lengths:
                avg_length = sum(data_lengths) / len(data_lengths)
                max_length = max(data_lengths)
            else:
                avg_length = max_length = header_length
            
            numeric_count = sum(1 for val in column_data if str(val).replace('.', '').replace('-', '').isdigit())
            content_type = 'numeric' if numeric_count > len(column_data) * 0.5 else 'text'
            
            column_analysis[col_idx] = {
                'header_length': header_length,
                'avg_length': avg_length,
                'max_length': max_length,
                'content_type': content_type,
                'priority': max(header_length, avg_length)
            }
        return column_analysis
    
    def _calculate_column_widths(self, column_analysis: Dict[int, Dict[str, Any]], 
                                total_width: int, text_wrapping_config: Dict = None) -> Dict[int, int]:
        base_width = text_wrapping_config.get('max_width', 80) if text_wrapping_config else 80
        total_priority = sum(analysis['priority'] for analysis in column_analysis.values())
        column_widths = {}
        remaining_width = base_width
        
        for col_idx, analysis in column_analysis.items():
            if total_priority > 0:
                proportional_width = int((analysis['priority'] / total_priority) * base_width)
                if analysis['content_type'] == 'numeric':
                    allocated_width = max(min(proportional_width, 25), 8)
                else:
                    allocated_width = max(min(proportional_width, 50), 15)
            else:
                allocated_width = 20
            column_widths[col_idx] = allocated_width
            remaining_width -= allocated_width
        
        if remaining_width > 0:
            text_columns = [col for col, analysis in column_analysis.items() if analysis['content_type'] == 'text']
            if text_columns:
                extra_per_col = remaining_width // len(text_columns)
                for col_idx in text_columns:
                    column_widths[col_idx] += extra_per_col
        return column_widths

    def format_table_cells(self, table, df: pd.DataFrame, font_list: List[str],
                          font_config: Dict, layout_style: str, code_config: Dict, text_wrapping_config: Dict = None,
                          font_size: float = None, missing_value_style: str = 'italic') -> None:
        if font_size is None:
            font_size = font_config.get('element_typography', {}).get('tables', {}).get('content', {}).get('size', 10)
        
        num_rows, num_cols = df.shape
        num_rows += 1
        column_analysis = self._analyze_column_content(df)
        column_widths = self._calculate_column_widths(column_analysis, 80, text_wrapping_config)
        
        row_heights = {}
        for (row, col), cell in table.get_celld().items():
            if row not in row_heights: row_heights[row] = 1
            is_header = (row == 0)
            if is_header:
                text_value = df.columns[col] if col < len(df.columns) else ""
                text_value = self._apply_header_multiline(str(text_value))
            else:
                text_value = df.iloc[row - 1, col] if row - 1 < len(df) and col < len(df.columns) else ""
            
            cell_width = column_widths.get(col, 40)
            line_count = self._calculate_cell_lines(text_value, is_header, cell_width)
            row_heights[row] = max(row_heights[row], line_count)
        
        for (row, col), cell in table.get_celld().items():
            is_header = (row == 0)
            if is_header:
                text_value = df.columns[col] if col < len(df.columns) else ""
                header_max_length = column_widths.get(col, 25)
                text_value = self._apply_header_multiline(str(text_value), header_max_length)
            else:
                text_value = df.iloc[row - 1, col] if row - 1 < len(df) and col < len(df.columns) else ""
            
            self._font_manager.configure_cell_font(cell, text_value, is_header, font_list, layout_style, code_config)
            
            if 'auto_adjustment' in font_config:
                self._font_manager.auto_adjust_font_size(cell, font_size, num_cols, num_rows, str(text_value), font_config)
            
            max_lines_in_row = row_heights[row]
            cell_width = column_widths.get(col, 40)
            self._apply_unified_cell_styling(cell, is_header, text_value, max_lines_in_row, cell_width)
    
    def _apply_header_multiline(self, header_text: str, max_length: int = None) -> str:
        effective_max_length = max_length if max_length is not None else 25
        if len(header_text) <= effective_max_length: return header_text
        
        for delimiter in [' ', '_', '-', '.']:
            if delimiter in header_text:
                parts = header_text.split(delimiter)
                if len(parts) > 1:
                    mid_point = len(parts) // 2
                    line1 = delimiter.join(parts[:mid_point])
                    line2 = delimiter.join(parts[mid_point:])
                    if max(len(line1), len(line2)) < len(header_text):
                        return f"{line1}\n{line2}"
        mid = len(header_text) // 2
        return f"{header_text[:mid]}\n{header_text[mid:]}"
    
    def _calculate_cell_lines(self, text_value, is_header: bool, max_width: int = 40) -> int:
        return TableContentAnalyzer.calculate_cell_lines(text_value, is_header, max_width, self._wrap_text_content)
    
    def _apply_unified_cell_styling(self, cell, is_header: bool, text_value, max_lines_in_row: int, max_width: int = 40) -> None:
        text_str = str(text_value) if text_value is not None else ""
        processed_text = self._process_superscripts(text_str)
        wrap_width = max_width if is_header else max_width + min(max_width // 2, 15)
        
        if len(processed_text) > wrap_width:
            cell.get_text().set_text(self._wrap_text_content(processed_text, wrap_width))
        else:
            cell.get_text().set_text(processed_text)
        
        cell.get_text().set_horizontalalignment('center')
        cell.get_text().set_verticalalignment('center')
        cell.set_linewidth(0.5)
        
        if is_header:
            cell.get_text().set_weight('bold')
            height = 0.08 + (max_lines_in_row - 1) * 0.04
            cell.set_height(max(height, 0.08))
        else:
            height = 0.06 + (max_lines_in_row - 1) * 0.03
            cell.set_height(max(height, 0.06))
        
        if max_lines_in_row > 3:
            cell.get_text().set_fontsize(cell.get_text().get_fontsize() * 0.9)
    
    def _wrap_text_content(self, text: str, max_width: int = None) -> str:
        effective_max_width = max_width if max_width is not None else 80
        return TableTextWrapper.wrap_cell_content(text, effective_max_width)
    
    def detect_format_code_content(self, cell_value, code_config: Dict, available_languages: List[str]) -> str:
        if not cell_value or pd.isna(cell_value): return ""
        cell_str = str(cell_value)
        code_indicators = ['def ', 'function', 'class ', 'import ', 'from ', 'export ', 'const ', 'var ', 'let ', 'function(', 'return ', '{}', '[]', '()', '=>', '==', '!=']
        if sum(1 for indicator in code_indicators if indicator in cell_str) >= 2:
            if 'language_detection' in code_config:
                lang_detection = code_config['language_detection']
                for lang in available_languages:
                    if lang in lang_detection and any(ind in cell_str for ind in lang_detection[lang]):
                        return lang
            return 'generic'
        return ""
    
    def _process_superscripts(self, text: str) -> str:
        return self._process_superscripts_static(text)
    
    @staticmethod
    def _process_superscripts_static(text: str) -> str:
        if text is None: return ""
        try:
            if pd.isna(text): return ""
        except: pass
        text_str = str(text)
        if not text_str or '^' not in text_str: return text_str
        try:
            config = FormatConfig()
            formatter = SuperscriptFormatter(config)
            return formatter.format_superscripts(text_str, output_format='matplotlib')
        except Exception:
            return CellFormatter._fallback_superscript_processing(text_str)
    
    @staticmethod
    def _fallback_superscript_processing(text: str) -> str:
        if not text or '^' not in text: return text
        superscript_map = {
            '^0': '⁰', '^1': '¹', '^2': '²', '^3': '³', '^4': '⁴', '^5': '⁵', '^6': '⁶', '^7': '⁷', '^8': '⁸', '^9': '⁹',
            '^10': '¹⁰', '^11': '¹¹', '^12': '¹²', '^n': 'ⁿ', '^x': 'ˣ', '^y': 'ʸ', '^i': 'ⁱ', '^j': 'ʲ', '^k': 'ᵏ',
            '^+': '⁺', '^-': '⁻', '^=': '⁼'
        }
        result = text
        for pattern in sorted(superscript_map.keys(), key=len, reverse=True):
            result = result.replace(pattern, superscript_map[pattern])
        return result
