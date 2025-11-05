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
    """Get absolute paths for output directories."""
    base_path = Path.cwd()
    
    # Load document types configuration to get output directories dynamically
    try:
        config_loader = ModularConfigLoader()
        doc_types_config = config_loader.load_external('document_types')
        doc_types = doc_types_config.get('document_types', {})
    except:
        # Fallback to hardcoded values if config loading fails
        doc_types = {
            'paper': {'output_dir': 'paper'},
            'report': {'output_dir': 'report'},
            'book': {'output_dir': 'book'},
            'presentations': {'output_dir': 'presentations'}
        }
    
    # Get output directory for the specified document type
    if document_type in doc_types:
        output_dir_name = doc_types[document_type].get('output_dir', document_type)
    else:
        # Fallback to document_type name if not found
        output_dir_name = document_type
    
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
    
    # Add dynamic directories for each document type
    for doc_type, config in doc_types.items():
        dir_name = config.get('output_dir', doc_type)
        base_directories[doc_type] = str(base_path / 'results' / dir_name)
        base_directories[f'tables_{doc_type}'] = str(base_path / 'results' / dir_name / 'tables')
        base_directories[f'figures_{doc_type}'] = str(base_path / 'results' / dir_name / 'figures')
    
    return base_directories

class ModularConfigLoader:
    """Enhanced loader for modular configuration architecture."""
    
    def __init__(self, config_dir: Optional[Path] = None, project_file: Optional[Path] = None):
        if config_dir is None:
            package_root = Path(__file__).parent.parent
            self.config_dir = package_root / 'config'
        else:
            self.config_dir = Path(config_dir)
        
        self.project_file = project_file
        self._cache = {}
        self._master_config = None
        self._project_config = None
    
    def load_master(self) -> Dict[str, Any]:
        """Load master configuration file."""
        if self._master_config is None:
            master_path = self.config_dir / "master.epyson"
            self._master_config = self._load_json_file(master_path)
        return self._master_config
    
    def load_project(self) -> Dict[str, Any]:
        """Load project-specific configuration."""
        if self._project_config is None:
            if self.project_file is not None:
                project_path = Path(self.project_file)
            else:
                master = self.load_master()
                default_file = master.get('project_config', {}).get('default_file', 'config/project.epyson')
                project_path = self.config_dir / Path(default_file).name

            self._project_config = self._load_json_file(project_path)
            if self._project_config is None:
                self._project_config = {}

        return self._project_config
    
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
        master = self.load_master()
        
        # Determine layout to load
        if layout_name is None:
            layout_name = master.get('layouts', {}).get('default', 'academic')
        
        # Validate layout exists
        available_layouts = master.get('layouts', {}).get('available', [])
        if layout_name not in available_layouts:
            raise ValueError(
                f"Layout '{layout_name}' not available. "
                f"Available layouts: {', '.join(available_layouts)}"
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
                "colors": defaults.get("colors", {}).copy() if "colors" in defaults else {},
                "typography": defaults.get("typography", {}).copy() if "typography" in defaults else {},
                "styling": defaults.get("styling", {}).copy() if "styling" in defaults else {},
                "images": defaults.get("images", {}).copy() if "images" in defaults else {}
            }
            
            # Apply color tones from defaults
            if "color_tones" in defaults and "palette" in config:
                palette = config["palette"]
                for element, tone in defaults["color_tones"].items():
                    if element not in expanded_callout["colors"]:
                        expanded_callout["colors"][element] = {}
                    expanded_callout["colors"][element]["palette"] = palette
                    expanded_callout["colors"][element]["tone"] = tone
            
            # Override with color_tone_overrides from specific callout
            if "color_tone_overrides" in config:
                palette = config["palette"]
                for element, tone in config["color_tone_overrides"].items():
                    if element not in expanded_callout["colors"]:
                        expanded_callout["colors"][element] = {}
                    expanded_callout["colors"][element]["tone"] = tone
            
            # Merge specific overrides (styling, images, etc.)
            if "styling" in config:
                expanded_callout["styling"].update(config["styling"])
            
            if "images" in config:
                # Deep merge images
                for key, value in config["images"].items():
                    if key == "border" and isinstance(value, dict):
                        if "border" not in expanded_callout["images"]:
                            expanded_callout["images"]["border"] = {}
                        expanded_callout["images"]["border"].update(value)
                    else:
                        expanded_callout["images"][key] = value
            
            expanded[callout_type] = expanded_callout
        
        return expanded

    def load_external(self, config_name: str) -> Dict[str, Any]:
        """Load external configuration file.
        
        Args:
            config_name: Name of external config (e.g., 'generation', 'mapper')
        
        Returns:
            Dict with configuration data
        """
        cache_key = f"external:{config_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Load external config
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
        return {
            "layout": {
                "name": layout.get("layout_name", layout_name),
                "available": master.get("layouts", {}).get("available", []),
            },
            "callouts": layout.get("callouts", {}),
            "colors": layout.get("colors", {}),
            "text": layout.get("text", {}),
            "images": layout.get("images", {}),
            "tables": layout.get("tables", {}),
            "notes": layout.get("notes", {}),
            "pages": layout.get("pages", {}),
            "format": layout.get("format", {}),
            "paper": layout.get("paper", {}),
            "report": layout.get("report", {}),
        }

    def _merge_external_configs(self, master: Dict[str, Any], complete_config: Dict[str, Any]) -> None:
        """Load and merge external configurations into the complete config."""
        external_configs = master.get("external_configs", {})
        
        # Handle consolidated configuration architecture (v3.0)
        if "core" in external_configs:
            try:
                core_data = self.load_external("core")
                # Merge core configurations
                if "code" in core_data:
                    complete_config["code"] = core_data["code"]
                if "generation" in core_data:
                    complete_config["generation"] = core_data["generation"]
                if "reader" in core_data:
                    complete_config["reader"] = core_data["reader"]
                if "references" in core_data:
                    complete_config["references"] = core_data["references"]
            except FileNotFoundError:
                pass
        
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
        """Get list of available layouts.
        
        Returns:
            List of layout names
        """
        master = self.load_master()
        return master.get('layouts', {}).get('available', [])
    
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
            section_name: Name of the section (e.g., 'tables', 'text', 'colors')
            layout_name: Optional layout name. If None, uses default.
            
        Returns:
            Dict with the configuration data for that section
        """
        config = self.load_complete_config(layout_name)
        return config.get(section_name, {})
    
    # Layout-specific convenience methods (moved from _layouts.py)
    def get_layout_margins(self, layout_name: str = 'classic') -> Dict[str, float]:
        """Get margins (in cm) for specified layout."""
        layout = self.load_layout(layout_name)
        return layout.get('layout_config', {}).get('margins', {})
    
    def get_layout_font_family(self, layout_name: str = 'classic') -> str:
        """Get font family for specified layout."""
        layout = self.load_layout(layout_name)
        return layout.get('font_family', 'sans_technical')
    
    def get_layout_colors(self, layout_name: str = 'classic') -> Dict[str, str]:
        """Get color scheme for specified layout."""
        layout = self.load_layout(layout_name)
        
        # Helper function to convert RGB list to hex
        def rgb_to_hex(rgb_list):
            if isinstance(rgb_list, list) and len(rgb_list) == 3:
                return '#{:02X}{:02X}{:02X}'.format(int(rgb_list[0]), int(rgb_list[1]), int(rgb_list[2]))
            return '#FFFFFF'  # Default fallback
        
        # Load palettes for color resolution
        complete_config = self.load_complete_config(layout_name)
        palettes = complete_config.get('colors', {}).get('palettes', {})
        
        # Get colors from layout - extract from default_palette
        colors_config = layout.get('colors', {}).get('layout_config', {})
        default_palette = colors_config.get('default_palette', 'academic')
        
        # Get colors from the palette
        if default_palette in palettes:
            palette = palettes[default_palette]
            return {
                'primary': rgb_to_hex(palette.get('primary', [37, 99, 235])),      # Blue
                'secondary': rgb_to_hex(palette.get('secondary', [124, 58, 237])),  # Purple  
                'background': rgb_to_hex(palette.get('background', [255, 255, 255])) if 'background' in palette else '#FFFFFF'
            }
        else:
            # Default colors if palette not found
            return {
                'primary': '#2563EB',
                'secondary': '#7C3AED',
                'background': '#FFFFFF'
            }
    
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
        layout = self.load_layout(layout_name)
        
        # Check if layout has custom font configuration
        if 'font_css' in layout:
            return layout['font_css']
        
        # Check if layout uses a custom font family that requires a file
        font_family_key = layout.get('font_family', 'sans_technical')
        complete_config = self.load_complete_config(layout_name)
        format_config = complete_config.get('format', {})
        font_families = format_config.get('font_families', {})
        
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
                    # Generate @font-face CSS with relative path from output directory
                    return f"""
@font-face {{
    font-family: '{primary_font}';
    src: url('fonts/{font_filename}') format('opentype');
    font-weight: normal;
    font-style: normal;
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
    
    This allows using a custom loader with specific project_file.
    
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


def load_layout(layout_name: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to load a layout configuration.
    
    Args:
        layout_name: Layout to load. If None, uses default.
    
    Returns:
        Dict with layout configuration
    """
    loader = get_loader()
    return loader.load_layout(layout_name)


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
def get_layout(layout_name: str = 'classic') -> Dict[str, Any]:
    """Get layout configuration."""
    loader = get_loader()
    return loader.load_layout(layout_name)


def get_layout_margins(layout_name: str = 'classic') -> Dict[str, float]:
    """Get margins (in cm) for specified layout."""
    loader = get_loader()
    return loader.get_layout_margins(layout_name)


def get_layout_font_family(layout_name: str = 'classic') -> str:
    """Get font family for specified layout."""
    loader = get_loader()
    return loader.get_layout_font_family(layout_name)


def get_layout_colors(layout_name: str = 'classic') -> Dict[str, str]:
    """Get color scheme for specified layout."""
    loader = get_loader()
    return loader.get_layout_colors(layout_name)


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
    loader = get_loader()
    layout = loader.load_layout(layout_name)
    font_family = layout.get('font_family')
    
    if not font_family:
        return ""
    
    # Load font families configuration
    complete_config = loader.load_complete_config(layout_name)
    font_families = complete_config.get('format', {}).get('font_families', {})
    font_config = font_families.get(font_family)
    
    if not font_config:
        return ""
    
    # Get primary font and fallbacks
    primary_font = font_config.get('primary', '')
    
    # Check if layout has custom font file
    custom_font = layout.get('custom_font')
    if custom_font and font_family == 'handwritten_personal':
        font_path = "./fonts/" if fonts_dir is None else f"{fonts_dir.as_posix()}/"
        return f"""
\\usepackage{{fontspec}}
\\setmainfont{{{custom_font}}}[
    Path = {font_path},
    Extension = .otf,
    UprightFont = *,
    BoldFont = {custom_font},
    ItalicFont = {custom_font},
    BoldItalicFont = {custom_font}
]
"""
    
    # For other fonts with font files (like handwritten)
    if primary_font:
        font_file_template = font_config.get('font_file_template')
        if font_file_template:
            # Extract font filename
            font_filename = font_file_template.format(font_name=primary_font)
            
            # Get fallback for missing glyphs
            fallback_policy = font_config.get('fallback_policy', {})
            context_specific = fallback_policy.get('context_specific', {})
            latex_fallback = context_specific.get('pdf_latex', font_config.get('fallback', 'DejaVu Sans'))
            
            # Parse fallback (take first font if comma-separated)
            if ',' in latex_fallback:
                latex_fallback = latex_fallback.split(',')[0].strip()
            
            # Extract base font name (without _regular, _bold, etc.)
            base_font_name = font_filename.rsplit('.', 1)[0]  # Remove extension
            
            # Use absolute path if provided, otherwise relative
            if fonts_dir:
                # Convert Windows path to forward slashes for LaTeX
                font_path = fonts_dir.as_posix() + "/"
            else:
                font_path = "./fonts/"
            
            # Use absolute path if provided, otherwise relative
            if fonts_dir:
                # Convert Windows path to forward slashes for LaTeX
                font_path = fonts_dir.as_posix() + "/"
            else:
                font_path = "./fonts/"
            
            # Only define fallbacks for non-ASCII characters (Greek letters, etc.)
            # ASCII symbols will use the font's built-in glyphs or system fallback
            greek_chars = {
                'σ': '\\ensuremath{\\sigma}',
                'ε': '\\ensuremath{\\varepsilon}',
                'π': '\\ensuremath{\\pi}',
                'Δ': '\\ensuremath{\\Delta}',
                'α': '\\ensuremath{\\alpha}',
                'β': '\\ensuremath{\\beta}',
                'γ': '\\ensuremath{\\gamma}',
                'μ': '\\ensuremath{\\mu}',
                'τ': '\\ensuremath{\\tau}',
                'ω': '\\ensuremath{\\omega}',
                'θ': '\\ensuremath{\\theta}',
                'λ': '\\ensuremath{\\lambda}',
                'ρ': '\\ensuremath{\\rho}',
                'φ': '\\ensuremath{\\phi}',
                'Σ': '\\ensuremath{\\Sigma}',
                'Π': '\\ensuremath{\\Π}',
                'Ω': '\\ensuremath{\\Omega}',
                'Θ': '\\ensuremath{\\Theta}',
                'Λ': '\\ensuremath{\\Lambda}',
                'Φ': '\\ensuremath{\\Phi}',
            }
            
            # Build newunicodechar commands for Greek letters
            unicode_mappings = [
                f"\\newunicodechar{{{char}}}{{{replacement}}}"
                for char, replacement in greek_chars.items()
            ]
            
            unicode_char_defs = '\n'.join(unicode_mappings)
            
            # Use provided path (absolute or relative)
            return f"""
\\usepackage{{fontspec}}
\\defaultfontfeatures{{Ligatures=TeX}}

% Define main handwritten font for all text
\\setmainfont{{{base_font_name}}}[
    Path = {font_path},
    Extension = .otf,
    BoldFont = {base_font_name},
    ItalicFont = {base_font_name},
    BoldItalicFont = {base_font_name}
]

% Use same font for sans-serif (headings, TOC, etc.)
\\setsansfont{{{base_font_name}}}[
    Path = {font_path},
    Extension = .otf,
    BoldFont = {base_font_name},
    ItalicFont = {base_font_name},
    BoldItalicFont = {base_font_name}
]

% Define fallback font family for missing glyphs
\\newfontfamily\\fallbackfont{{{latex_fallback}}}

% Greek letters use math mode (automatically uses math fonts)
\\usepackage{{newunicodechar}}
{unicode_char_defs}
"""
    
    return ""
