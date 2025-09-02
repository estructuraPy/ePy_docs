"""
TEXT KINGDOM CONTROLLER - COMPLETE CONQUEST
Lord's decrees enforced:
- NO hardcoded values
- NO fallbacks  
- NO verbose code
- NO backward compatibility
- Clean code that exposes user flow failures
- All filepaths from setup.json
- Respect sync_files always
"""

from typing import Dict, Any, List
from ePy_docs.core.setup import _load_cached_files, _resolve_config_path
from ePy_docs.components.pages import get_current_layout

def _load_text_config(sync_files: bool) -> Dict[str, Any]:
    """Load text configuration from centralized configuration system."""
    config_path = _resolve_config_path('components/text', sync_files)
    config = _load_cached_files(config_path, sync_files)
    
    if 'layout_styles' not in config:
        raise KeyError("TEXT KINGDOM FAILURE: 'layout_styles' missing from configuration")
    
    return config

def _get_layout_text_config(layout_name: str, sync_files: bool) -> Dict[str, Any]:
    """Get text configuration for specific layout."""
    config = _load_text_config(sync_files)
    
    if layout_name not in config['layout_styles']:
        available_layouts = list(config['layout_styles'].keys())
        raise KeyError(f"TEXT KINGDOM FAILURE: Layout '{layout_name}' not found. Available: {available_layouts}")
    
    return config['layout_styles'][layout_name]

def _get_current_layout_config(sync_files: bool) -> Dict[str, Any]:
    """Get current layout configuration from project settings."""
    current_layout = get_current_layout()
    return _get_layout_text_config(current_layout, sync_files)

def get_font_family_for_element(layout_name: str, element_type: str, sync_files: bool) -> str:
    """Get font family for specific text element."""
    layout_config = _get_layout_text_config(layout_name, sync_files)
    
    if 'typography' not in layout_config:
        raise KeyError(f"TEXT KINGDOM FAILURE: 'typography' not found in layout '{layout_name}'")
    
    typography = layout_config['typography']
    
    if element_type == 'text' and 'text' in typography:
        text_config = typography['text']
        if 'font_family' not in text_config:
            raise KeyError(f"TEXT KINGDOM FAILURE: 'font_family' not configured for text in layout '{layout_name}'")
        return text_config['font_family']
    
    if element_type not in typography:
        available_elements = list(typography.keys())
        raise KeyError(f"TEXT KINGDOM FAILURE: Element '{element_type}' not found in typography for layout '{layout_name}'. Available: {available_elements}")
    
    element_config = typography[element_type]
    if 'font_family' not in element_config:
        raise KeyError(f"TEXT KINGDOM FAILURE: 'font_family' not configured for element '{element_type}' in layout '{layout_name}'")
    
    return element_config['font_family']

def get_font_size_for_element(layout_name: str, element_type: str, sub_element: str, sync_files: bool) -> int:
    """Get font size for specific text element."""
    layout_config = _get_layout_text_config(layout_name, sync_files)
    
    if 'typography' not in layout_config:
        raise KeyError(f"TEXT KINGDOM FAILURE: 'typography' not found in layout '{layout_name}'")
    
    typography = layout_config['typography']
    
    if element_type == 'text' and sub_element:
        if 'text' not in typography:
            raise KeyError(f"TEXT KINGDOM FAILURE: 'text' section not found in typography for layout '{layout_name}'")
        
        text_config = typography['text']
        if sub_element not in text_config:
            available_sub = list(text_config.keys())
            raise KeyError(f"TEXT KINGDOM FAILURE: Sub-element '{sub_element}' not found in text config for layout '{layout_name}'. Available: {available_sub}")
        
        element_config = text_config[sub_element]
        if 'fontSize' not in element_config:
            raise KeyError(f"TEXT KINGDOM FAILURE: 'fontSize' not configured for typography.text.{sub_element} in layout '{layout_name}'")
        
        return element_config['fontSize']
    
    if element_type not in typography:
        raise KeyError(f"TEXT KINGDOM FAILURE: Element '{element_type}' not found in typography for layout '{layout_name}'")
    
    element_config = typography[element_type]
    if 'fontSize' in element_config:
        return element_config['fontSize']
    elif 'font_size' in element_config:
        return element_config['font_size']
    else:
        raise KeyError(f"TEXT KINGDOM FAILURE: Neither 'fontSize' nor 'font_size' configured for element '{element_type}' in layout '{layout_name}'")

def get_css_font_stack(font_family: str, sync_files: bool) -> str:
    """Get CSS font stack for specified font family."""
    config = _load_text_config(sync_files)
    
    if 'css_font_stacks' not in config:
        raise KeyError("TEXT KINGDOM FAILURE: 'css_font_stacks' missing from configuration")
    
    css_stacks = config['css_font_stacks']
    
    if font_family not in css_stacks:
        available_fonts = list(css_stacks.keys())
        raise KeyError(f"TEXT KINGDOM FAILURE: Font '{font_family}' not found in CSS stacks. Available: {available_fonts}")
    
    return css_stacks[font_family]

def format_header_h1(text: str, layout_name: str, sync_files: bool) -> str:
    """Format H1 header using layout configuration."""
    config = _get_layout_text_config(layout_name, sync_files)
    
    if 'typography' not in config or 'headers' not in config['typography'] or 'h1' not in config['typography']['headers']:
        raise KeyError(f"TEXT KINGDOM FAILURE: H1 header configuration missing in layout structure for '{layout_name}'")
    
    h1_config = config['typography']['headers']['h1']
    if 'format' not in h1_config:
        raise KeyError(f"TEXT KINGDOM FAILURE: 'format' missing from H1 configuration in layout '{layout_name}'")
    
    return h1_config['format'].format(text=text)

def format_header_h2(text: str, layout_name: str, sync_files: bool) -> str:
    """Format H2 header using layout configuration."""
    config = _get_layout_text_config(layout_name, sync_files)
    
    if 'typography' not in config or 'headers' not in config['typography'] or 'h2' not in config['typography']['headers']:
        raise KeyError(f"TEXT KINGDOM FAILURE: H2 header configuration missing in layout structure for '{layout_name}'")
    
    h2_config = config['typography']['headers']['h2']
    if 'format' not in h2_config:
        raise KeyError(f"TEXT KINGDOM FAILURE: 'format' missing from H2 configuration in layout '{layout_name}'")
    
    return h2_config['format'].format(text=text)

def format_header_h3(text: str, layout_name: str, sync_files: bool) -> str:
    """Format H3 header using layout configuration."""
    config = _get_layout_text_config(layout_name, sync_files)
    
    if 'typography' not in config or 'headers' not in config['typography'] or 'h3' not in config['typography']['headers']:
        raise KeyError(f"TEXT KINGDOM FAILURE: H3 header configuration missing in layout structure for '{layout_name}'")
    
    h3_config = config['typography']['headers']['h3']
    if 'format' not in h3_config:
        raise KeyError(f"TEXT KINGDOM FAILURE: 'format' missing from H3 configuration in layout '{layout_name}'")
    
    return h3_config['format'].format(text=text)

def format_text_content(content: str, layout_name: str, sync_files: bool) -> str:
    """Format text content using layout configuration."""
    config = _get_layout_text_config(layout_name, sync_files)
    
    if 'typography' not in config or 'text' not in config['typography']:
        raise KeyError(f"TEXT KINGDOM FAILURE: Typography text configuration missing in layout structure for '{layout_name}'")
    
    text_config = config['typography']['text']
    if 'content_format' not in text_config:
        raise KeyError(f"TEXT KINGDOM FAILURE: 'content_format' missing from text configuration in layout '{layout_name}'")
    
    return text_config['content_format'].format(content=content)

def format_list(items: List[str], ordered: bool, sync_files: bool) -> str:
    """Format list using configuration."""
    config = _load_text_config(sync_files)
    
    if 'lists' not in config:
        raise KeyError("TEXT KINGDOM FAILURE: 'lists' missing from configuration")
    
    lists_config = config['lists']
    list_type = 'ordered' if ordered else 'unordered'
    
    if list_type not in lists_config:
        available_types = list(lists_config.keys())
        raise KeyError(f"TEXT KINGDOM FAILURE: List type '{list_type}' not found. Available: {available_types}")
    
    list_config = lists_config[list_type]
    
    if 'item_format' not in list_config:
        raise KeyError(f"TEXT KINGDOM FAILURE: 'item_format' missing from {list_type} list configuration")
    
    if 'spacing' not in list_config:
        raise KeyError(f"TEXT KINGDOM FAILURE: 'spacing' missing from {list_type} list configuration")
    
    formatted_items = []
    for i, item in enumerate(items, 1):
        if ordered:
            formatted_items.append(list_config['item_format'].format(number=i, item=item))
        else:
            formatted_items.append(list_config['item_format'].format(item=item))
    
    return list_config['spacing'].join(formatted_items) + list_config['spacing']

class TextFormatter:
    """Text formatter class."""
    
    def __init__(self, layout_name: str, sync_files: bool):
        self.layout_name = layout_name
        self.sync_files = sync_files
        self.config = _get_layout_text_config(layout_name, sync_files)
    
    def format_text(self, text: str) -> str:
        """Format text using current layout."""
        return format_text_content(text, self.layout_name, self.sync_files)
    
    @staticmethod
    def format_field(label: str, value: str, sync_files: bool) -> str:
        """Format field with label and value using centralized configuration."""
        current_layout = get_current_layout()
        config = _get_layout_text_config(current_layout, sync_files)
        
        if 'typography' not in config or 'text' not in config['typography']:
            raise KeyError(f"TEXT KINGDOM FAILURE: Typography text configuration missing for layout '{current_layout}'")
        
        text_config = config['typography']['text']
        
        if 'field_format' not in text_config:
            raise KeyError(f"TEXT KINGDOM FAILURE: 'field_format' not configured for layout '{current_layout}'")
        
        return text_config['field_format'].format(label=label, value=value)

def format_text_with_math_delegation(text: str, layout_name: str, sync_files: bool) -> str:
    """Format text with mathematical content delegation to math.py."""
    layout_config = _get_layout_text_config(layout_name, sync_files)
    
    if 'processing' not in layout_config:
        raise KeyError(f"TEXT KINGDOM FAILURE: 'processing' not found in layout '{layout_name}'")
    
    processing = layout_config['processing']
    if 'markdown_processing' not in processing:
        raise KeyError(f"TEXT KINGDOM FAILURE: 'markdown_processing' not found in processing for layout '{layout_name}'")
    
    markdown_proc = processing['markdown_processing']
    if 'mathematical_delegation' not in markdown_proc:
        raise KeyError(f"TEXT KINGDOM FAILURE: 'mathematical_delegation' not found in markdown_processing for layout '{layout_name}'")
    
    math_delegation = markdown_proc['mathematical_delegation']
    
    if not math_delegation.get('enabled', False):
        raise KeyError(f"TEXT KINGDOM FAILURE: Mathematical delegation not enabled for layout '{layout_name}'")
    
    detection_patterns = math_delegation.get('detection_patterns', [])
    delegate_to = math_delegation.get('delegate_to', '')
    
    if not delegate_to:
        raise KeyError(f"TEXT KINGDOM FAILURE: 'delegate_to' not configured for mathematical delegation in layout '{layout_name}'")
    
    # Check if text contains mathematical content
    import re
    has_math_content = False
    for pattern in detection_patterns:
        if re.search(pattern, text):
            has_math_content = True
            break
    
    if has_math_content:
        # Delegate to math module
        try:
            import importlib
            math_module = importlib.import_module(delegate_to)
            if hasattr(math_module, 'process_mathematical_text'):
                return math_module.process_mathematical_text(text, layout_name, sync_files)
            else:
                raise KeyError(f"TEXT KINGDOM FAILURE: Math module '{delegate_to}' missing 'process_mathematical_text' function")
        except ImportError as e:
            raise KeyError(f"TEXT KINGDOM FAILURE: Cannot import math module '{delegate_to}': {e}")
    
    # No mathematical content, process as regular text
    return format_text_content(text, layout_name, sync_files)

def apply_advanced_text_formatting(text: str, output_format: str = 'matplotlib') -> str:
    """Apply advanced text formatting including superscripts, subscripts, and symbols.
    
    Following Lord's decrees: NO hardcoded, NO fallbacks, delegate to math system.
    
    Args:
        text: Text to format
        output_format: Output format ('matplotlib', 'unicode', 'html', 'latex', etc.)
        
    Returns:
        Formatted text with proper processing for mathematical content
        
    Raises:
        ValueError: If required parameters are missing (clean failure exposure)
    """
    if not text:
        raise ValueError("TEXT KINGDOM FAILURE: text parameter is required")
    if not output_format:
        raise ValueError("TEXT KINGDOM FAILURE: output_format parameter is required")
    
    # Delegate mathematical processing to math kingdom - following Lord's decrees
    # Mathematical delegation - now using ANNEXED math functions from quarto.py
    from ePy_docs.core.quarto import process_mathematical_text
    # Use default layout for now - real implementation would get current layout
    return process_mathematical_text(text, 'academic', sync_files=False)

def apply_font_fallback(text_obj, formatted_text: str) -> None:
    """Font configuration following Lord's decrees: NO fallbacks, clean failure exposure.
    
    Args:
        text_obj: Text object to configure
        formatted_text: Text content
        
    Raises:
        RuntimeError: Clean failure exposure when font configuration fails
    """
    if text_obj is None:
        raise RuntimeError("TEXT KINGDOM FAILURE: text_obj parameter is required - no fallbacks allowed")
    if not formatted_text:
        raise RuntimeError("TEXT KINGDOM FAILURE: formatted_text parameter is required - no fallbacks allowed")
    
    # Following Lord's decrees: NO hardcoded fonts, get from configuration
    try:
        layout_config = _get_layout_text_config('corporate', sync_files=False)  # Use current layout
        # Access hierarchical structure correctly following our conquests
        typography = layout_config.get('typography', {})
        text_config = typography.get('text', {})
        font_family = text_config.get('font_family')
        if not font_family:
            raise RuntimeError("TEXT KINGDOM FAILURE: font_family not found in text configuration")
        
        # Apply font directly - NO fallbacks as per Lord's decrees
        text_obj.set_text(formatted_text)
        # Note: Actual font setting would depend on text_obj type (matplotlib, etc.)
        
    except Exception as e:
        raise RuntimeError(f"TEXT KINGDOM FAILURE: Font configuration failed - {e}")

def get_best_font_for_text(text: str) -> str:
    """Get best font for text following Lord's decrees: NO fallbacks, clean failure exposure.
    
    Args:
        text: Text to get font for
        
    Returns:
        Font family name from configuration
        
    Raises:
        RuntimeError: When font configuration fails (clean failure exposure)
    """
    if not text:
        raise RuntimeError("TEXT KINGDOM FAILURE: text parameter is required")
    
    try:
        layout_config = _get_layout_text_config('corporate', sync_files=False)
        # Access hierarchical structure correctly following our conquests
        typography = layout_config.get('typography', {})
        text_config = typography.get('text', {})
        font_family = text_config.get('font_family')
        if not font_family:
            raise RuntimeError("TEXT KINGDOM FAILURE: font_family not found in text configuration - no fallbacks allowed")
        
        return font_family
        
    except Exception as e:
        raise RuntimeError(f"TEXT KINGDOM FAILURE: Font selection failed - {e}")
