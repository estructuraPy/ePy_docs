"""
Configuration and Path Management Module
=========================================

Unified module for:
- Configuration loading (modular layouts, palettes, formats)
- Path resolution (output directories, caller detection)
- Project configuration management

This module consolidates all configuration-related functionality
previously split between config/modular_loader.py and config/paths.py.
"""

import json
import inspect
from pathlib import Path
from typing import Dict, Any, Optional


# =============================================================================
# PATH UTILITIES
# =============================================================================

def get_caller_directory() -> Path:
    """Get the directory of the script/notebook that called the library.
    
    Uses the call stack to find the first frame outside of ePy_docs package.
    This allows automatic detection of the user's working directory.
    
    Returns:
        Path to the directory containing the calling script/notebook
    """
    # Get current frame stack
    frame_stack = inspect.stack()
    
    # Find the first frame that's not from ePy_docs package
    for frame_info in frame_stack:
        frame_file = Path(frame_info.filename)
        
        # Skip frames from ePy_docs package
        if 'ePy_docs' not in str(frame_file):
            # Return directory of the calling file
            if frame_file.name == '<stdin>' or frame_file.name.startswith('<ipython'):
                # Jupyter notebook or interactive session - use current directory
                return Path.cwd()
            else:
                # Regular Python script - use script's directory
                return frame_file.parent
    
    # Fallback to current directory if no external caller found
    return Path.cwd()


def get_absolute_output_directories(document_type: str = "report") -> Dict[str, str]:
    """Get absolute paths for output directories.
    
    Args:
        document_type: Type of document ("report" or "paper") to determine correct paths
        
    Returns:
        Dictionary with absolute paths for different output directories
    """
    # Simple relative paths matching project structure
    # Select correct tables/figures directories based on document type
    base_path = Path.cwd()
    
    if document_type == "paper":
        tables_dir = Path('results') / 'paper' / 'tables'
        figures_dir = Path('results') / 'paper' / 'figures'
        output_dir = Path('results') / 'paper'
    else:  # document_type == "report" or fallback
        tables_dir = Path('results') / 'report' / 'tables'
        figures_dir = Path('results') / 'report' / 'figures'
        output_dir = Path('results') / 'report'
    
    return {
        'data': str(base_path / 'data'),
        'results': str(base_path / 'results'),
        'configuration': str(base_path / 'data' / 'configuration'),
        'brand': str(base_path / 'data' / 'user' / 'brand'),
        'templates': str(base_path / 'data' / 'user' / 'templates'),
        'user': str(base_path / 'data' / 'user'),
        'report': str(base_path / 'results' / 'report'),
        'paper': str(base_path / 'results' / 'paper'),
        'examples': str(base_path / 'data' / 'examples'),
        # Document-specific directories (active based on document_type)
        'tables': str(base_path / tables_dir),
        'figures': str(base_path / figures_dir),
        'output': str(base_path / output_dir),
        # All specific table and figure directories (for direct access)
        'tables_report': str(base_path / 'results' / 'report' / 'tables'),
        'figures_report': str(base_path / 'results' / 'report' / 'figures'),
        'tables_paper': str(base_path / 'results' / 'paper' / 'tables'),
        'figures_paper': str(base_path / 'results' / 'paper' / 'figures')
    }


# =============================================================================
# CONFIGURATION LOADER
# =============================================================================

class ModularConfigLoader:
    """Enhanced loader for modular configuration architecture."""
    
    def __init__(self, config_dir: Optional[Path] = None, project_file: Optional[Path] = None):
        """Initialize modular configuration loader.
        
        Args:
            config_dir: Base configuration directory. Defaults to package config/
            project_file: External project configuration file path (JSON or .epyson).
                         If None, uses default project.epyson from config_dir.
        """
        if config_dir is None:
            # Auto-detect: use package config directory
            package_root = Path(__file__).parent.parent
            self.config_dir = package_root / 'config'
        else:
            self.config_dir = Path(config_dir)
        
        self.project_file = project_file
        self._cache = {}
        self._master_config = None
        self._project_config = None
    
    def load_master(self) -> Dict[str, Any]:
        """Load master configuration file.
        
        Returns:
            Dict with master configuration
        """
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
        for config_name in external_configs.keys():
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


# =============================================================================
# GLOBAL LOADER INSTANCE AND CONVENIENCE FUNCTIONS
# =============================================================================

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
