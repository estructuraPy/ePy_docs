"""
Configuration and Path Management Module

Unified module for configuration loading, path resolution, and project configuration management.
This module consolidates all configuration-related functionality.
"""

import json
import inspect
from pathlib import Path
from typing import Dict, Any, Optional, List
from typing import Dict, Any, Optional

def get_caller_directory() -> Path:
    """Get the directory of the script/notebook that called the library."""
    frame_stack = inspect.stack()
    
    for frame_info in frame_stack:
        frame_file = Path(frame_info.filename)
        
        if 'ePy_docs' not in str(frame_file):
            if frame_file.name == '<stdin>' or frame_file.name.startswith('<ipython'):
                return Path.cwd()
            else:
                return frame_file.parent
    
    return Path.cwd()


def get_absolute_output_directories(document_type: str = "report") -> Dict[str, str]:
    """Get absolute paths for output directories.
    
    Args:
        document_type: Type of document (must exist in documents.epyson)
        
    Raises:
        ValueError: If document_type not found or configuration invalid
    """
    base_path = Path.cwd()
    
    # Load document configuration from individual file
    config_loader = ModularConfigLoader()
    
    # Try to load from documents/{type}.epyson
    try:
        type_config = config_loader.load_external(f'documents.{document_type}')
    except FileNotFoundError:
        # List available document types
        documents_dir = config_loader.config_dir / 'documents'
        available_types = [f.stem for f in documents_dir.glob('*.epyson')] if documents_dir.exists() else []
        available = ', '.join(available_types) if available_types else 'none'
        raise ValueError(f"Document type '{document_type}' not found. Available: {available}")
    
    # Validate required fields
    if 'output_dir' not in type_config:
        raise ValueError(f"Missing 'output_dir' in configuration for document type '{document_type}'")
    
    output_dir_name = type_config['output_dir']
    
    tables_dir = Path('results') / output_dir_name / 'tables'
    figures_dir = Path('results') / output_dir_name / 'figures'
    output_dir = Path('results') / output_dir_name
    
    # Build base directories that all document types need
    base_directories = {
        'data': str(base_path / 'data'),
        'results': str(base_path / 'results'),
        'configuration': str(base_path / 'data' / 'configuration'),
        'brand': str(base_path / 'data' / 'user' / 'brand'),
        'templates': str(base_path / 'data' / 'user' / 'templates'),
        'user': str(base_path / 'data' / 'user'),
        'examples': str(base_path / 'data' / 'examples'),
        'tables': str(base_path / tables_dir),
        'figures': str(base_path / figures_dir),
        'output': str(base_path / output_dir),
    }
    
    # Load all available document types for dynamic directories
    documents_dir = config_loader.config_dir / 'documents'
    if documents_dir.exists():
        for doc_file in documents_dir.glob('*.epyson'):
            doc_name = doc_file.stem
            try:
                doc_config = config_loader.load_external(f'documents.{doc_name}')
                dir_name = doc_config.get('output_dir', doc_name)
                base_directories[doc_name] = str(base_path / 'results' / dir_name)
                base_directories[f'tables_{doc_name}'] = str(base_path / 'results' / dir_name / 'tables')
                base_directories[f'figures_{doc_name}'] = str(base_path / 'results' / dir_name / 'figures')
            except Exception:
                # Skip documents that can't be loaded
                continue
    
    return base_directories

class ModularConfigLoader:
    """Enhanced loader for modular configuration architecture."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            package_root = Path(__file__).parent.parent
            self.config_dir = package_root / 'config'
        else:
            self.config_dir = Path(config_dir)
        
        self._cache = {}
        self._master_config = None
    
    def load_master(self) -> Dict[str, Any]:
        """Load core configuration (deprecated - returns empty dict).
        
        Core configuration (core.epyson) has been eliminated.
        Default layout is now hardcoded in load_layout().
        """
        if self._master_config is None:
            self._master_config = {}
        return self._master_config
    
    def load_project(self) -> Dict[str, Any]:
        """Load project-specific configuration.
        
        Returns empty configuration as project files are no longer supported.
        For runtime configuration, use DocumentWriter.set_* methods.
        """
        # Check if there's a current DocumentWriter instance with project info
        import inspect
        
        # Look for DocumentWriter instance in call stack
        for frame_info in inspect.stack():
            frame_locals = frame_info.frame.f_locals
            for name, obj in frame_locals.items():
                if hasattr(obj, '_project_info') and hasattr(obj, '_authors'):
                    # Found a DocumentWriter instance
                    config = {}
                    if hasattr(obj, '_project_info') and obj._project_info:
                        config['project'] = obj._project_info
                    if hasattr(obj, '_authors') and obj._authors:
                        config['authors'] = obj._authors
                    if hasattr(obj, '_client_info') and obj._client_info:
                        config['client'] = obj._client_info
                    return config
        
        return {}
    
    def load_layout(self, layout_name: Optional[str] = None) -> Dict[str, Any]:
        """Load complete configuration for a specific layout.
        
        Args:
            layout_name: Name of layout (e.g., 'academic', 'technical').
                        If None, uses default from master config.
        
        Returns:
            Dict with complete layout configuration including:
            - colors (palettes + layout-specific config)
            - text (fonts + layout-specific config)
            - images, tables, notes, pages, format
        """
        # Determine layout to load
        if layout_name is None:
            # Default layout (hardcoded, core.epyson eliminated)
            layout_name = "classic"
        
        # Validate layout exists by checking filesystem
        available_layouts = self.list_layouts()
        
        if not available_layouts:
            raise ValueError(
                "No layouts found in config/layouts/ directory. "
                "Please ensure layout .epyson files are present."
            )
        
        if layout_name not in available_layouts:
            raise ValueError(
                f"Layout '{layout_name}' not found. "
                f"Available layouts: {', '.join(sorted(available_layouts))}"
            )
        
        # Check cache
        cache_key = f"layout:{layout_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Load layout configuration file
        layout_path = self.config_dir / "layouts" / f"{layout_name}.epyson"
        layout_config = self._load_json_file(layout_path)
        
        if layout_config is None:
            raise FileNotFoundError(f"Layout config not found: {layout_path}")
        
        # Expand callouts with _defaults if present
        if "callouts" in layout_config and "_defaults" in layout_config["callouts"]:
            layout_config["callouts"] = self._expand_callouts_defaults(layout_config["callouts"])
        
        # Cache and return
        self._cache[cache_key] = layout_config
        return layout_config
    
    def _expand_callouts_defaults(self, callouts: Dict[str, Any]) -> Dict[str, Any]:
        """Expand callouts configuration by merging _defaults with specific overrides.
        
        Args:
            callouts: Callouts dict with optional _defaults key
            
        Returns:
            Expanded callouts dict without _defaults key
        """
        if "_defaults" not in callouts:
            return callouts
        
        defaults = callouts["_defaults"]
        expanded = {}
        
        for callout_type, config in callouts.items():
            if callout_type == "_defaults":
                continue
            
            # Start with a copy of defaults
            expanded_callout = {
                "colors": {},
                "typography": defaults.get("typography", {}).copy() if "typography" in defaults else {},
                "styling": defaults.get("styling", {}).copy() if "styling" in defaults else {},
                "figures": defaults.get("figures", {}).copy() if "figures" in defaults else {}
            }
            
            # Deep copy colors from defaults
            if "colors" in defaults:
                for key, value in defaults["colors"].items():
                    if isinstance(value, dict):
                        expanded_callout["colors"][key] = value.copy()
                    else:
                        expanded_callout["colors"][key] = value
            
            # Apply color tones from defaults
            if "color_tones" in defaults and "palette" in config:
                palette = config["palette"]
                for element, tone in defaults["color_tones"].items():
                    if element not in expanded_callout["colors"]:
                        expanded_callout["colors"][element] = {}
                    # Only set if not already explicitly set in colors config
                    if "colors" not in config or element not in config["colors"]:
                        expanded_callout["colors"][element]["palette"] = palette
                        expanded_callout["colors"][element]["tone"] = tone
            
            # Override with color_tone_overrides from specific callout
            if "color_tone_overrides" in config:
                palette = config["palette"]
                for element, tone in config["color_tone_overrides"].items():
                    if element not in expanded_callout["colors"]:
                        expanded_callout["colors"][element] = {}
                    expanded_callout["colors"][element]["tone"] = tone
            
            # Merge specific overrides (colors first to allow text palette overrides)
            if "colors" in config:
                # Deep merge colors configuration, allowing specific overrides
                for key, value in config["colors"].items():
                    if isinstance(value, dict):
                        if key not in expanded_callout["colors"]:
                            expanded_callout["colors"][key] = {}
                        expanded_callout["colors"][key].update(value)
                    else:
                        expanded_callout["colors"][key] = value
            
            # Merge specific overrides (styling, figures, etc.)
            if "styling" in config:
                expanded_callout["styling"].update(config["styling"])
            
            if "figures" in config:
                # Deep merge figures
                for key, value in config["figures"].items():
                    if key == "border" and isinstance(value, dict):
                        if "border" not in expanded_callout["figures"]:
                            expanded_callout["figures"]["border"] = {}
                        expanded_callout["figures"]["border"].update(value)
                    else:
                        expanded_callout["figures"][key] = value
            
            expanded[callout_type] = expanded_callout
        
        return expanded

    def load_external(self, config_name: str) -> Dict[str, Any]:
        """Load external configuration file.
        
        Args:
            config_name: Name of external config (e.g., 'generation', 'mapper', 'documents', 'documents.paper', 'colors')
        
        Returns:
            Dict with configuration data
            
        Note:
            'colors' is loaded from assets/ directory, all others from config/
        """
        cache_key = f"external:{config_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Special case: colors.epyson lives in config/assets/ directory
        if config_name == 'colors':
            package_root = self.config_dir.parent
            external_path = package_root / 'config' / 'assets' / 'colors.epyson'
        # Handle subdirectory paths (e.g., 'documents.paper' -> 'documents/paper.epyson')
        elif '.' in config_name:
            parts = config_name.split('.')
            external_path = self.config_dir / parts[0] / f"{parts[1]}.epyson"
        else:
            external_path = self.config_dir / f"{config_name}.epyson"
        
        external_config = self._load_json_file(external_path)
        
        if external_config is None:
            raise FileNotFoundError(f"External config not found: {external_path}")
        
        # Cache and return
        self._cache[cache_key] = external_config
        return external_config
    
    def _merge_master_config(self, master: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure metadata and system info from master config."""
        return {
            "description": master.get("description", ""),
            "version": master.get("version", ""),
            "last_updated": master.get("last_updated", ""),
            "system": master.get("system", {}),
        }

    def _merge_project_config(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure project-specific information."""
        return {
            "project": project.get("project", {}),
            "location": project.get("location", {}),
            "client": project.get("client", {}),
            "consultants": project.get("consultants", {}),
            "team": project.get("team", {}),
            "copyright": project.get("copyright", {}),
            "authors": project.get("authors", []),
            "metadata": project.get("metadata", {}),
        }

    def _merge_layout_config(self, layout: Dict[str, Any], layout_name: str, master: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure layout-specific information."""
        # Resolve text configuration from references
        text_config = layout.get("text", {})
        if "font_family_ref" in layout:
            text_config["font_family"] = layout["font_family_ref"]
        
        return {
            "layout": {
                "name": layout.get("layout_name", layout_name),
                "available": master.get("layouts", {}).get("available", []),
                "text": text_config,
            },
            "callouts": layout.get("callouts", {}),
            "colors": layout.get("colors", {}),
            "figures": layout.get("figures", {}),
            "tables": layout.get("tables", {}),
            "notes": layout.get("notes", {}),
            "pages": layout.get("pages", {}),
            "format": layout.get("format", {}),
        }

    def _merge_external_configs(self, master: Dict[str, Any], complete_config: Dict[str, Any]) -> None:
        """Load and merge external configurations into the complete config."""
        external_configs = master.get("external_configs", {})
        config_modules = master.get("config_modules", {})
        
        # Handle config_modules (v3.0 architecture)
        if config_modules:
            # Load text configuration (contains font_families)
            if "text" in config_modules:
                try:
                    text_data = self.load_external("text")
                    if "shared_defaults" in text_data:
                        complete_config["shared_defaults"] = text_data["shared_defaults"]
                    if "variants" in text_data:
                        complete_config["text_variants"] = text_data["variants"]
                except FileNotFoundError:
                    pass
            
            # Load other config modules as needed
            for module_name in ["colors", "tables", "images", "documents"]:
                if module_name in config_modules:
                    try:
                        module_data = self.load_external(module_name)
                        complete_config[module_name] = module_data
                    except FileNotFoundError:
                        continue
        
        # Core configuration has been eliminated (core.epyson no longer used)
        
        if "assets" in external_configs:
            try:
                assets_data = self.load_external("assets")
                # Merge assets configurations
                if "font_families" in assets_data:
                    if "format" not in complete_config:
                        complete_config["format"] = {}
                    complete_config["format"]["font_families"] = assets_data["font_families"]
                if "shared_weights" in assets_data:
                    if "format" not in complete_config:
                        complete_config["format"] = {}
                    complete_config["format"]["shared_weights"] = assets_data["shared_weights"]
                if "shared_styles" in assets_data:
                    if "format" not in complete_config:
                        complete_config["format"] = {}
                    complete_config["format"]["shared_styles"] = assets_data["shared_styles"]
                if "math_formatting" in assets_data:
                    if "format" not in complete_config:
                        complete_config["format"] = {}
                    complete_config["format"]["math_formatting"] = assets_data["math_formatting"]
                if "shared_superscripts" in assets_data:
                    if "format" not in complete_config:
                        complete_config["format"] = {}
                    complete_config["format"]["shared_superscripts"] = assets_data["shared_superscripts"]
                if "subscripts" in assets_data:
                    if "format" not in complete_config:
                        complete_config["format"] = {}
                    complete_config["format"]["subscripts"] = assets_data["subscripts"]
                if "format_specific" in assets_data:
                    if "format" not in complete_config:
                        complete_config["format"] = {}
                    complete_config["format"]["format_specific"] = assets_data["format_specific"]
                if "palettes" in assets_data:
                    if "colors" not in complete_config:
                        complete_config["colors"] = {}
                    complete_config["colors"]["palettes"] = assets_data["palettes"]
                if "unit_systems" in assets_data:
                    complete_config["mapping"] = {
                        "unit_systems": assets_data["unit_systems"],
                        "shared_concepts": assets_data.get("shared_concepts", {}),
                        "discipline_aliases": assets_data.get("discipline_aliases", {}),
                        "documentation_types": assets_data.get("documentation_types", {}),
                        "specific_mappings": assets_data.get("specific_mappings", {}),
                        "user_extensions": assets_data.get("user_extensions", {})
                    }
            except FileNotFoundError:
                pass
        
        # Load document_types configuration
        if "document_types" in external_configs:
            try:
                doc_types_data = self.load_external("document_types")
                if doc_types_data:
                    complete_config["document_types"] = doc_types_data
            except FileNotFoundError:
                pass
        
        # Fallback: handle legacy individual config files if they still exist
        for config_name in external_configs.keys():
            if config_name in ["core", "assets", "project"]:
                continue  # Already handled above or handled separately
                
            try:
                external_data = self.load_external(config_name)
                if config_name == "palettes":
                    if "palettes" in external_data:
                        if "colors" not in complete_config:
                            complete_config["colors"] = {}
                        complete_config["colors"]["palettes"] = external_data["palettes"]
                elif config_name == "format":
                    if "format" not in complete_config:
                        complete_config["format"] = {}
                    complete_config["format"].update(external_data)
                else:
                    complete_config[config_name] = external_data.get(config_name, external_data)
            except FileNotFoundError:
                pass

    def load_complete_config(self, layout_name: Optional[str] = None) -> Dict[str, Any]:
        """Load complete merged configuration for a layout."""
        master = self.load_master()
        project = self.load_project()
        layout = self.load_layout(layout_name)

        complete_config = {}
        complete_config.update(self._merge_master_config(master))
        complete_config.update(self._merge_project_config(project))
        complete_config.update(self._merge_layout_config(layout, layout_name, master))
        self._merge_external_configs(master, complete_config)

        return complete_config
    
    def get_available_layouts(self) -> list:
        """Get list of available layouts by scanning the layouts directory.
        
        Returns:
            List of layout names found in config/layouts/
        """
        return sorted(self.list_layouts())
    
    def get_default_layout(self) -> str:
        """Get default layout name.
        
        Returns:
            Default layout name
        """
        master = self.load_master()
        return master.get('layouts', {}).get('default', 'academic')
    
    def get_config_section(self, section_name: str, layout_name: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific configuration section.
        
        Args:
            section_name: Name of the section (e.g., 'tables', 'text', 'colors', 'reader')
            layout_name: Optional layout name. If None, uses default.
            
        Returns:
            Dict with the configuration data for that section
        """
        # Special case: certain sections are layout-independent, load directly
        # Note: 'tables', 'images', 'format', 'figures', 'quarto', 'notes' are now embedded in layouts or hardcoded
        layout_independent_sections = ['reader', 'text', 'colors', 'code', 'documents', 'pdf', 'html', 'fonts']
        if section_name in layout_independent_sections:
            return self.load_external(section_name)
        
        config = self.load_complete_config(layout_name)
        return config.get(section_name, {})
    
    # Layout-specific convenience methods (moved from _layouts.py)
    def get_layout_margins(self, layout_name: str = 'classic') -> Dict[str, float]:
        """Get margins (in cm) for specified layout.
        
        Raises:
            ValueError: If margins not found in layout configuration
        """
        layout = self.load_layout(layout_name)
        
        # Margins should be at root level of layout
        margins = layout.get('margins')
        
        if not margins:
            raise ValueError(
                f"Missing 'margins' in layout '{layout_name}' configuration. "
                f"All layouts must define margins with keys: top, bottom, left, right"
            )
        
        # Validate all required keys exist
        required_keys = {'top', 'bottom', 'left', 'right'}
        missing_keys = required_keys - set(margins.keys())
        if missing_keys:
            raise ValueError(
                f"Missing margin keys {missing_keys} in layout '{layout_name}'. "
                f"Required keys: {required_keys}"
            )
        
        return margins
    
    def get_layout_font_family(self, layout_name: str = 'classic') -> str:
        """Get font family for specified layout.
        
        Raises:
            ValueError: If font_family not found in layout configuration
        """
        layout = self.load_layout(layout_name)
        
        if 'font_family' not in layout:
            raise ValueError(f"Missing 'font_family' in layout '{layout_name}' configuration")
        
        return layout['font_family']
    
    def get_layout_colors(self, layout_name: str = 'classic', palette_name: str = None) -> Dict[str, str]:
        """Get color scheme for specified layout or palette.
        
        Args:
            layout_name: Layout name (used if palette_name not provided)
            palette_name: Direct palette name (overrides layout's palette_ref)
        
        Raises:
            ValueError: If palette or required colors not found in configuration
        """
        # Helper function to convert RGB list to hex
        def rgb_to_hex(rgb_list):
            if not isinstance(rgb_list, list) or len(rgb_list) != 3:
                raise ValueError(f"Invalid RGB format: {rgb_list}. Expected list of 3 integers")
            return '#{:02X}{:02X}{:02X}'.format(int(rgb_list[0]), int(rgb_list[1]), int(rgb_list[2]))
        
        # Helper function to flatten hierarchical palette structure
        def flatten_palette(palette):
            """Flatten hierarchical palette to flat structure for backward compatibility."""
            flat = {}
            for key, value in palette.items():
                if key == 'description':
                    flat[key] = value
                elif isinstance(value, dict):
                    # Hierarchical section (colors, page, code, table)
                    for subkey, subvalue in value.items():
                        if key == 'colors':
                            flat[subkey] = subvalue
                        else:
                            flat[f"{key}_{subkey}"] = subvalue
                else:
                    flat[key] = value
            return flat
        
        # Get palette name or palette data
        if palette_name is None:
            layout = self.load_layout(layout_name)
            
            # Check if layout has embedded palette (new structure)
            if 'palette' in layout:
                # Layout has embedded palette - use it directly
                palette_data = layout['palette']
                
                # Flatten the embedded palette structure
                result = {}
                
                # Add colors (primary, secondary, etc.)
                if 'colors' in palette_data:
                    result.update(palette_data['colors'])
                
                # Add page colors with prefix
                if 'page' in palette_data:
                    for key, value in palette_data['page'].items():
                        result[f'page_{key}'] = value
                
                # Add code colors with prefix
                if 'code' in palette_data:
                    for key, value in palette_data['code'].items():
                        result[f'code_{key}'] = value
                
                # Add table colors with prefix
                if 'table' in palette_data:
                    for key, value in palette_data['table'].items():
                        result[f'table_{key}'] = value
                
                # Add border and caption colors
                if 'border_color' in palette_data:
                    result['border_color'] = palette_data['border_color']
                if 'caption_color' in palette_data:
                    result['caption_color'] = palette_data['caption_color']
                
                # Convert RGB lists to hex
                for color_key, color_value in result.items():
                    if isinstance(color_value, (list, tuple)) and len(color_value) == 3:
                        result[color_key] = rgb_to_hex(color_value)
                
                return result
            
            # Check for palette_ref (legacy structure)
            elif 'palette_ref' in layout:
                palette_name = layout['palette_ref']
            else:
                raise ValueError(f"Layout '{layout_name}' has neither 'palette' nor 'palette_ref'")
        
        # Load colors configuration
        colors_config = self.load_external('colors')
        
        # Build palettes dictionary from both layout_palettes and color_palettes
        palettes = {}
        if 'layout_palettes' in colors_config:
            for name, palette in colors_config['layout_palettes'].items():
                palettes[name] = flatten_palette(palette)
        if 'color_palettes' in colors_config:
            palettes.update(colors_config['color_palettes'])
        
        # Filter out metadata keys (for legacy flat structures)
        metadata_keys = {'description', 'version', 'last_updated'}
        palettes = {k: v for k, v in palettes.items() if k not in metadata_keys}
        
        if palette_name not in palettes:
            available = ', '.join(palettes.keys())
            raise ValueError(f"Palette '{palette_name}' not found. Available: {available}")
        
        palette = palettes[palette_name]
        
        # Validate required colors exist
        required_colors = ['primary', 'secondary', 'page_background']
        for color_key in required_colors:
            if color_key not in palette:
                raise ValueError(f"Missing '{color_key}' in palette '{palette_name}'")
        
        # Return ALL colors from palette, not just 3 hardcoded ones
        result = {}
        for color_key, color_value in palette.items():
            # Skip description field
            if color_key == 'description':
                continue
            # Convert RGB lists to hex
            if isinstance(color_value, list) and len(color_value) == 3:
                result[color_key] = rgb_to_hex(color_value)
            elif isinstance(color_value, str):
                # Already hex format
                result[color_key] = color_value
        
        return result
    
    def requires_lualatex(self, layout_name: str = 'classic') -> bool:
        """Check if layout requires LuaLaTeX (for custom fonts)."""
        layout = self.load_layout(layout_name)
        return layout.get('requires_lualatex', False)
    
    def list_layouts(self) -> List[str]:
        """Get list of available layout names."""
        layouts_dir = self.config_dir / 'layouts'
        if layouts_dir.exists():
            return [f.stem for f in layouts_dir.glob('*.epyson')]
        return []
    
    def get_font_path(self, font_filename: str) -> Path:
        """Get absolute path to font file in package assets."""
        package_root = self.config_dir.parent
        font_path = package_root / 'config' / 'assets' / 'fonts' / font_filename
        
        if not font_path.exists():
            raise FileNotFoundError(f"Font file not found: {font_path}")
        
        return font_path
    
    def get_font_css_config(self, layout_name: str = 'classic') -> str:
        """Get CSS @font-face configuration for layout."""
        # Load complete configuration to get resolved references
        complete_config = self.load_complete_config(layout_name)
        
        # Check if layout has custom font configuration in raw layout
        layout = self.load_layout(layout_name)
        if 'font_css' in layout:
            return layout['font_css']
        
        # Get font family from resolved layout configuration
        layout_config = complete_config.get('layout', {})
        text_config = layout_config.get('text', {})
        font_family_key = text_config.get('font_family', 'technical')
        
        # Get font families from embedded layout configuration
        font_families = layout.get('font_families', {})
        
        if font_family_key in font_families:
            font_config = font_families[font_family_key]
            primary_font = font_config.get('primary', '')
            
            # Check if there's a font_file_template (indicates custom font file needed)
            if 'font_file_template' in font_config:
                font_file_template = font_config['font_file_template']
                font_filename = font_file_template.replace('{font_name}', primary_font)
                
                # Try to find the font file
                try:
                    font_path = self.get_font_path(font_filename)
                    
                    # Determine format based on file extension
                    font_format = 'opentype' if font_filename.lower().endswith('.otf') else 'truetype'
                    
                    # Get fallback fonts for better symbol support
                    fallback_fonts = font_config.get('fallback', 'Arial, sans-serif')
                    
                    # Generate enhanced @font-face CSS with fallback support
                    return f"""
@font-face {{
    font-family: '{primary_font}';
    src: url('fonts/{font_filename}') format('{font_format}');
    font-weight: normal;
    font-style: normal;
    font-display: swap;
}}

/* Enhanced font stack with symbol fallback */
.custom-font-stack {{
    font-family: '{primary_font}', {fallback_fonts};
    font-feature-settings: "liga" 1, "kern" 1;
}}
"""
                except FileNotFoundError:
                    pass
        
        return ""  # No custom fonts needed
    
    def _load_json_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load JSON file safely.
        
        Args:
            file_path: Path to JSON file
        
        Returns:
            Dict with data or None if error
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def clear_cache(self) -> None:
        """Clear all cached configurations."""
        self._cache.clear()
        self._master_config = None
    
    def reload_layout(self, layout_name: str) -> Dict[str, Any]:
        """Reload a layout configuration (bypass cache).
        
        Args:
            layout_name: Name of layout to reload
        
        Returns:
            Dict with fresh layout configuration
        """
        cache_key = f"layout:{layout_name}"
        if cache_key in self._cache:
            del self._cache[cache_key]
        
        return self.load_layout(layout_name)


_global_loader = None


def set_config_loader(loader: ModularConfigLoader):
    """Set the global config loader instance.
    
    Args:
        loader: ModularConfigLoader instance to use globally
    """
    global _global_loader
    _global_loader = loader


def get_loader(config_dir: Optional[Path] = None) -> ModularConfigLoader:
    """Get global ModularConfigLoader instance.
    
    Args:
        config_dir: Optional config directory. Only used on first call.
    
    Returns:
        Global ModularConfigLoader instance
    """
    global _global_loader
    if _global_loader is None:
        _global_loader = ModularConfigLoader(config_dir)
    return _global_loader


def load_layout(layout_name: Optional[str] = None, resolve_refs: bool = True) -> Dict[str, Any]:
    """Convenience function to load a layout configuration.
    
    Args:
        layout_name: Layout to load. If None, uses default.
        resolve_refs: If True, resolves all _ref fields to full configs.
                     This provides backward compatibility for tests expecting expanded configs.
    
    Returns:
        Dict with layout configuration. If resolve_refs=True, resolves:
        - palette_ref → colors
        - font_family_ref → font_family + text
        - tables_ref → tables
        - callouts_ref → callouts
        - images_ref → images
        - notes_ref → notes
    """
    loader = get_loader()
    layout = loader.load_layout(layout_name)
    
    if resolve_refs:
        # Resolve palette_ref → colors
        if 'palette_ref' in layout:
            colors_config = loader.load_external('colors')
            palette_name = layout['palette_ref']
            # Filter out metadata keys
            metadata_keys = {'description', 'version', 'last_updated'}
            palettes = {k: v for k, v in colors_config.items() if k not in metadata_keys}
            
            if palette_name in palettes:
                palette = palettes[palette_name]
                
                # Create colors structure with layout_config
                layout['colors'] = {
                    'palette': palette
                }
                
                # If there's a colors section with layout_config, preserve it
                if 'colors' in layout and isinstance(layout['colors'], dict):
                    existing_colors = layout['colors']
                else:
                    existing_colors = {}
                
                # Merge layout_config if exists
                layout_config = existing_colors.get('layout_config', {})
                layout_config['default_palette'] = palette_name
                
                # Add tables config from layout if it exists in colors
                if 'layout_config' in existing_colors and 'tables' in existing_colors['layout_config']:
                    layout_config['tables'] = existing_colors['layout_config']['tables']
                
                layout['colors'] = {
                    'layout_config': layout_config,
                    'palette': palette
                }
        
        # Resolve font_family_ref → font_family from embedded font_families
        if 'font_family_ref' in layout:
            font_ref = layout['font_family_ref']
            
            # Check if layout has embedded font_families
            if 'font_families' in layout and font_ref in layout['font_families']:
                # Use embedded font_families (new model - no fonts.epyson dependency)
                layout['font_family'] = font_ref
                layout['text'] = layout['font_families'][font_ref]
            else:
                # Legacy fallback: try to load from fonts.epyson if it exists
                try:
                    fonts_config = loader.load_external('fonts')
                    font_families = fonts_config.get('font_families', {})
                    
                    if font_ref in font_families:
                        layout['font_family'] = font_ref
                        layout['text'] = font_families[font_ref]
                except FileNotFoundError:
                    # fonts.epyson doesn't exist - this is expected with new model
                    # Keep font_family_ref for later resolution
                    pass
        
        # Resolve tables_ref → tables (removed - handled later with nested path support)
        
        # Callouts are now integrated directly in each layout file (no more callouts_ref)
        
        # Images, tables, notes, and figures are now embedded in layouts (no refs needed)
        
        # Embed global format configuration (data_formats)
        # format.epyson now contains a single 'data_formats' section for all layouts
        try:
            format_config = loader.load_external('format')
            if 'data_formats' in format_config:
                if 'format' not in layout:
                    layout['format'] = {}
                layout['format']['data_formats'] = format_config['data_formats']
        except FileNotFoundError:
            # format.epyson doesn't exist - skip format embedding
            pass
        
        # Tables configuration is now embedded directly in each layout file (no more tables_ref)
        
        # Images are now embedded directly in each layout file (no more images_ref)
        
        # Notes validation now uses hardcoded Quarto types (no more notes.epyson or notes_ref)
        
        # Quarto configuration (html_theme, docx_reference) is now embedded directly in each layout file
        
        # Resolve html_ref → html
        if 'html_ref' in layout:
            ref_parts = layout['html_ref'].split('.')
            if len(ref_parts) == 2:
                config_name, variant_name = ref_parts
                html_config = loader.load_external(config_name)
                if variant_name in html_config:
                    layout['html'] = html_config[variant_name]
    
    return layout


def load_complete_config(layout_name: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to load complete merged configuration.
    
    Args:
        layout_name: Layout to load. If None, uses default.
    
    Returns:
        Dict with complete configuration
    """
    loader = get_loader()
    return loader.load_complete_config(layout_name)


def get_available_layouts() -> list:
    """Get list of available layouts.
    
    Returns:
        List of layout names
    """
    loader = get_loader()
    return loader.get_available_layouts()


def get_document_type_config(document_type: str) -> Dict[str, Any]:
    """Get configuration for a specific document type.
    
    Loads configuration from documents/{document_type}.epyson file.
    
    Args:
        document_type: Name of document type (report, book, paper, notebook)
        
    Returns:
        Document type configuration dictionary
        
    Raises:
        ValueError: If document type not found or file doesn't exist
    """
    from pathlib import Path
    import json
    
    # Get package config directory
    package_root = Path(__file__).parent.parent
    config_dir = package_root / 'config' / 'documents'
    doc_file = config_dir / f"{document_type}.epyson"
    
    if not doc_file.exists():
        available_files = [f.stem for f in config_dir.glob('*.epyson')]
        raise ValueError(
            f"Unknown document type '{document_type}'. "
            f"Available types: {available_files}"
        )
    
    # Load from .epyson file
    try:
        with open(doc_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Error parsing {doc_file.name}: {e}"
        )
    except Exception as e:
        raise ValueError(
            f"Error loading document type config '{document_type}': {e}"
        )


def get_config_section(section_name: str, layout_name: Optional[str] = None) -> Dict[str, Any]:
    """Get a specific configuration section.
    
    Convenience function that can be used without creating a loader instance.
    
    Args:
        section_name: Name of the section (e.g., 'tables', 'text', 'colors')
        layout_name: Optional layout name. If None, uses default.
        
    Returns:
        Dict with the configuration data for that section
    """
    loader = get_loader()
    return loader.get_config_section(section_name, layout_name)


def clear_global_cache():
    """Clear the global configuration cache.
    
    Forces reload of all configurations on next access.
    Useful when configuration files have been modified.
    """
    global _global_loader
    if _global_loader is not None:
        _global_loader.clear_cache()


def get_current_project_config():
    """Get current project configuration.
    
    Returns a minimal configuration object for backward compatibility.
    """
    # Simple object with sync_files=False
    return type('ProjectConfig', (), {
        'settings': type('Settings', (), {'sync_files': False})()
    })()


def load_epyson(file_path: str) -> Dict[str, Any]:
    """Load a .epyson (JSON) configuration file.
    
    Args:
        file_path: Path to the .epyson file
        
    Returns:
        Dict with configuration data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    path = Path(file_path)
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


# Layout Functions - Delegated to ModularConfigLoader (moved from _layouts.py)
def get_layout(layout_name: str = 'classic', resolve_refs: bool = True) -> Dict[str, Any]:
    """Get layout configuration.
    
    Args:
        layout_name: Name of layout to load
        resolve_refs: If True, resolves palette_ref and font_family_ref to full configs
        
    Returns:
        Dict with layout configuration
    """
    return load_layout(layout_name, resolve_refs=resolve_refs)


# Alias for backward compatibility
def get_layout_config(layout_name: str = 'classic', resolve_refs: bool = True) -> Dict[str, Any]:
    """Alias for get_layout() - backward compatibility.
    
    Args:
        layout_name: Name of layout to load
        resolve_refs: If True, resolves palette_ref and font_family_ref to full configs
        
    Returns:
        Dict with layout configuration
    """
    return get_layout(layout_name, resolve_refs=resolve_refs)


def get_layout_margins(layout_name: str = 'classic') -> Dict[str, float]:
    """Get margins (in cm) for specified layout."""
    loader = get_loader()
    return loader.get_layout_margins(layout_name)


def get_layout_font_family(layout_name: str = 'classic') -> str:
    """Get font family for specified layout."""
    loader = get_loader()
    return loader.get_layout_font_family(layout_name)


def get_layout_colors(layout_name: str = 'classic', palette_name: str = None) -> Dict[str, str]:
    """Get color scheme for specified layout or palette."""
    loader = get_loader()
    return loader.get_layout_colors(layout_name, palette_name)


def requires_lualatex(layout_name: str = 'classic') -> bool:
    """Check if layout requires LuaLaTeX (for custom fonts)."""
    loader = get_loader()
    return loader.requires_lualatex(layout_name)


def list_layouts() -> List[str]:
    """Get list of available layout names."""
    loader = get_loader()
    return loader.list_layouts()


def get_font_path(font_filename: str) -> Path:
    """Get absolute path to font file in package assets."""
    loader = get_loader()
    return loader.get_font_path(font_filename)


def get_font_css_config(layout_name: str = 'classic') -> str:
    """Get CSS @font-face configuration for layout."""
    loader = get_loader()
    return loader.get_font_css_config(layout_name)


def get_font_latex_config(layout_name: str = 'classic', fonts_dir: Path = None) -> str:
    """Generate LaTeX fontspec configuration for layout.
    
    Args:
        layout_name: Name of the layout
        fonts_dir: Absolute path to fonts directory (if None, uses relative path)
    """
    # Use the global load_layout function that supports resolve_refs
    layout = load_layout(layout_name, resolve_refs=True)

    # Get font configuration from resolved layout (after font_family_ref resolution)
    # After resolution, 'font_family' is the string key and 'text' has the full config
    font_family_key = layout.get('font_family')
    font_config = layout.get('text', {})
    
    if not font_family_key or not font_config:
        return ""
    
    # Extract font information from resolved config
    primary_font = font_config.get('primary', '')
    latex_primary = font_config.get('latex_primary', primary_font)
    fallback_fonts = font_config.get('fallback', [])
    font_file_path = font_config.get('font_file_path', '')
    
    # If system_default or no primary, return empty
    if not primary_font or primary_font == 'system_default':
        return ""
    
    # Check if layout has custom font file (handwritten case)
    if font_file_path:
        font_path = "./fonts/" if fonts_dir is None else f"{fonts_dir.as_posix()}/"
        font_name = font_file_path.split('/')[-1].rsplit('.', 1)[0]  # Extract name without extension
        extension = font_file_path.split('.')[-1]  # Get extension
        
        return f"""
\\usepackage{{fontspec}}
\\setmainfont{{{font_name}}}[
    Path = {font_path},
    Extension = .{extension},
    UprightFont = *,
    BoldFont = {font_name},
    ItalicFont = {font_name},
    BoldItalicFont = {font_name}
]
\\setmonofont{{Latin Modern Mono}}
"""
    
    # For system fonts (most layouts), generate fontspec config
    if latex_primary:
        # Use latex_primary if available (for fonts with different LaTeX names)
        font_to_use = latex_primary
    else:
        font_to_use = primary_font
    
    # Generate basic fontspec configuration
    return f"""
\\usepackage{{fontspec}}
\\setmainfont{{{font_to_use}}}
\\setmonofont{{Latin Modern Mono}}
"""
    
    # Legacy: font_family is a string (font_family_ref) - shouldn't happen anymore
    return ""
