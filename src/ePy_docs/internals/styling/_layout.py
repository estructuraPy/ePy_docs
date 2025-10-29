"""
Layout configuration management and coordination module.
Provides centralized layout configuration coordination across all components.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from ePy_docs.internals.data_processing._data import load_cached_files

@dataclass
class LayoutConfiguration:
    """Complete layout configuration coordination."""
    name: str
    colors: Dict[str, Any]
    typography: Dict[str, Any] 
    tables: Dict[str, Any]
    images: Dict[str, Any]
    notes: Dict[str, Any]
    pages: Dict[str, Any]

class LayoutCoordinator:
    """Layout configuration coordinator across all components."""
    
    def __init__(self):
        self._layout_cache = {}
        self._component_configs = {}
        self._layout_file_cache = {}  # Cache for loaded layout files
    
    def _load_layout_from_file(self, layout_name: str) -> Dict[str, Any]:
        """Load a complete layout configuration from its .epyson file.
        
        Args:
            layout_name: Name of the layout to load
            
        Returns:
            Complete layout configuration dictionary
        """
        if layout_name in self._layout_file_cache:
            return self._layout_file_cache[layout_name]
        
        import json
        from pathlib import Path
        
        # Path to layout file
        config_dir = Path(__file__).parent.parent.parent / 'config' / 'layouts'
        layout_file = config_dir / f'{layout_name}.epyson'
        
        if not layout_file.exists():
            return {}
        
        try:
            with open(layout_file, 'r', encoding='utf-8') as f:
                layout_config = json.load(f)
            
            self._layout_file_cache[layout_name] = layout_config
            return layout_config
        except Exception as e:
            return {}
    
    def _load_component_layout_styles(self, component_name: str) -> Dict[str, Any]:
        """Load layout_config from a specific component.
        
        NEW ARCHITECTURE: Each layout file has layout_config directly.
        This method wraps it to look like the old layout_styles dict.
        """
        if component_name not in self._component_configs:
            try:
                from ePy_docs.config.modular_loader import get_config_section
                from ePy_docs.config.modular_loader import ModularConfigLoader
                
                # Get the complete config (which includes the current layout's layout_config)
                full_config = get_config_section(component_name)
                
                # NEW: layout_config is directly in the section, not nested in layout_styles
                if 'layout_config' in full_config:
                    # Get layout name from ModularConfigLoader
                    loader = ModularConfigLoader()
                    layout_name = loader.get_default_layout()
                    
                    # Wrap layout_config to look like old structure: {layout_name: layout_config}
                    layout_section = {layout_name: full_config['layout_config']}
                else:
                    layout_section = {}
                
                self._component_configs[component_name] = layout_section
            except Exception as e:
                self._component_configs[component_name] = {}
        
        return self._component_configs[component_name]
    
    def get_available_layout_styles(self) -> List[str]:
        """Get all available layout styles by scanning layouts directory."""
        import os
        from pathlib import Path
        
        # Get the config directory path
        config_dir = Path(__file__).parent.parent.parent / 'config' / 'layouts'
        
        if not config_dir.exists():
            # Fallback to old method if layouts directory doesn't exist
            all_layouts = set()
            components = ['colors', 'text', 'tables', 'images', 'notes', 'pages']
            for component in components:
                component_layouts = self._load_component_layout_styles(component)
                all_layouts.update(component_layouts.keys())
            return sorted(list(all_layouts))
        
        # Scan layouts directory for .epyson files
        layout_files = config_dir.glob('*.epyson')
        layout_names = [f.stem for f in layout_files]
        
        return sorted(layout_names)
    
    def coordinate_layout_style(self, layout_name: str) -> LayoutConfiguration:
        """Coordinate layout style across all components.
        
        Args:
            layout_name: Name of the layout style to coordinate
            
        Returns:
            Complete configuration coordination across all components
            
        Raises:
            ValueError: If layout style doesn't exist
        """
        if layout_name in self._layout_cache:
            return self._layout_cache[layout_name]
        
        # Validate layout_name and fallback if invalid
        available = self.get_available_layout_styles()
        if layout_name not in available:
            # Layout not found, use fallback
            fallback_layout = 'classic' if 'classic' in available else available[0] if available else 'academic'
            print(f"Warning: Layout '{layout_name}' not found. Using '{fallback_layout}' instead. Available: {available}")
            layout_name = fallback_layout
        
        # Load the complete layout file
        layout_file_config = self._load_layout_from_file(layout_name)
        
        if not layout_file_config:
            raise ValueError(f"Failed to load layout file for '{layout_name}'")
        
        # Extract component configurations from layout file
        colors_config = layout_file_config.get('colors', {}).get('layout_config', {})
        text_config = layout_file_config.get('text', {}).get('layout_config', {})
        tables_config = layout_file_config.get('tables', {}).get('layout_config', {})
        images_config = layout_file_config.get('images', {}).get('layout_config', {})
        notes_config = layout_file_config.get('notes', {}).get('layout_config', {})
        pages_config = layout_file_config.get('pages', {})
        
        coordination = LayoutConfiguration(
            name=layout_name,
            colors=colors_config,
            typography=text_config,
            tables=tables_config,
            images=images_config,
            notes=notes_config,
            pages=pages_config
        )
        
        self._layout_cache[layout_name] = coordination
        return coordination
    
    def get_coordinated_typography(self, layout_name: str, element: str) -> Dict[str, Any]:
        """Get coordinated typography between color and text components."""
        coordination = self.coordinate_layout_style(layout_name)
        
        result = {}
        
        # From TEXT: fonts, sizes, formats
        if 'typography' in coordination.typography:
            text_typography = coordination.typography['typography']
            
            if 'headers' in text_typography and element in text_typography['headers']:
                result.update(text_typography['headers'][element])
            elif element in text_typography:
                result.update(text_typography[element])
        
        # From COLORS: colors per element
        if 'typography' in coordination.colors:
            color_typography = coordination.colors['typography'] 
            if element in color_typography:
                result['color'] = color_typography[element]
        
        return result
    
    def get_coordinated_table_style(self, layout_name: str) -> Dict[str, Any]:
        """Get coordinated table style across multiple components."""
        coordination = self.coordinate_layout_style(layout_name)
        
        result = {}
        
        # From TABLES: specific table configurations
        if 'styling' in coordination.tables:
            result.update(coordination.tables['styling'])
        
        # From COLORS: table colors
        if 'tables' in coordination.colors:
            result['colors'] = coordination.colors['tables']
        elif 'typography' in coordination.colors:
            result['colors'] = coordination.colors['typography']
        
        return result

# Global layout coordinator instance
_layout_coordinator = None

def get_layout_coordinator() -> LayoutCoordinator:
    """Get global layout coordinator instance."""
    global _layout_coordinator
    if _layout_coordinator is None:
        _layout_coordinator = LayoutCoordinator()
    return _layout_coordinator


def coordinate_layout(layout_name: str) -> LayoutConfiguration:
    """Main function for layout coordination across all components.
    
    Args:
        layout_name: Name of the layout style to coordinate
        
    Returns:
        Complete coordination across all components
    """
    coordinator = get_layout_coordinator()
    return coordinator.coordinate_layout_style(layout_name)

def get_coordinated_typography(element: str, layout_name: str) -> Dict[str, Any]:
    """Get coordinated typography for a specific element."""
    coordinator = get_layout_coordinator()
    return coordinator.get_coordinated_typography(layout_name, element)

def get_coordinated_table_style(layout_name: str) -> Dict[str, Any]:
    """Get coordinated table style.""" 
    coordinator = get_layout_coordinator()
    return coordinator.get_coordinated_table_style(layout_name)
