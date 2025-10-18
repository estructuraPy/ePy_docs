"""
Layout configuration management and coordination module.
Provides centralized layout configuration coordination across all components.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from ePy_docs.internals.data_processing._data import load_cached_files
from ePy_docs.config.setup import _resolve_config_path

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
    
    def _load_component_layout_styles(self, component_name: str) -> Dict[str, Any]:
        """Load layout_styles from a specific component."""
        if component_name not in self._component_configs:
            try:
                config_path = _resolve_config_path(f'components/{component_name}' if component_name != 'colors' else component_name, False)
                full_config = load_cached_files(config_path)
                self._component_configs[component_name] = full_config.get('layout_styles', {})
            except Exception:
                self._component_configs[component_name] = {}
        
        return self._component_configs[component_name]
    
    def get_available_layout_styles(self) -> List[str]:
        """Get all available layout styles."""
        all_layouts = set()
        
        components = ['colors', 'text', 'tables', 'images', 'notes', 'pages']
        
        for component in components:
            component_layouts = self._load_component_layout_styles(component)
            all_layouts.update(component_layouts.keys())
        
        return sorted(list(all_layouts))
    
    def coordinate_layout_style(self, layout_name: str) -> LayoutConfiguration:
        """Coordinate layout style across all components.
        
        Args:
            layout_name: Name of the layout style to coordinate
            
        Returns:
            Complete configuration coordination across all components
            
        Raises:
            ValueError: If layout style doesn't exist in any component
        """
        if layout_name in self._layout_cache:
            return self._layout_cache[layout_name]
        
        # Load configurations from all components
        colors_config = self._load_component_layout_styles('colors').get(layout_name, {})
        text_config = self._load_component_layout_styles('text').get(layout_name, {})
        tables_config = self._load_component_layout_styles('tables').get(layout_name, {})
        images_config = self._load_component_layout_styles('images').get(layout_name, {})
        notes_config = self._load_component_layout_styles('notes').get(layout_name, {})
        pages_config = self._load_component_layout_styles('pages').get(layout_name, {})
        
        # Verify existence in at least one component
        if not any([colors_config, text_config, tables_config, images_config, notes_config, pages_config]):
            available = self.get_available_layout_styles()
            raise ValueError(f"Layout style '{layout_name}' not found. Available: {available}")
        
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
