"""
Enhanced configuration loader for modular ePy_docs architecture.
Supports automatic loading and merging of layout-specific configurations.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
import os


class ModularConfigLoader:
    """Enhanced loader for modular configuration architecture."""
    
    def __init__(self, config_dir: Optional[Path] = None, project_file: Optional[Path] = None):
        """Initialize modular configuration loader.
        
        Args:
            config_dir: Base configuration directory. Defaults to src/ePy_docs/config/
            project_file: External project configuration file path (JSON or .epyson).
                         If None, uses default project.epyson from config_dir.
        """
        if config_dir is None:
            # Auto-detect: use package config directory
            self.config_dir = Path(__file__).parent
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
        """Load project-specific configuration.
        
        Can load from:
        1. External file provided via project_file parameter (JSON or .epyson)
        2. Default project.epyson in config directory
        
        Returns:
            Dict with project configuration
        """
        if self._project_config is None:
            # Determine project file path
            if self.project_file is not None:
                # Use externally provided project file
                project_path = Path(self.project_file)
            else:
                # Use default from master config
                master = self.load_master()
                default_file = master.get('project_config', {}).get('default_file', 'config/project.epyson')
                project_path = self.config_dir / Path(default_file).name
            
            # Load project configuration
            self._project_config = self._load_json_file(project_path)
            
            if self._project_config is None:
                # Return empty dict if not found (project config is optional)
                print(f"⚠️ Warning: Project config not found at {project_path}. Using empty config.")
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
        
        # Cache and return
        self._cache[cache_key] = layout_config
        return layout_config
    
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
    
    def load_complete_config(self, layout_name: Optional[str] = None) -> Dict[str, Any]:
        """Load complete merged configuration for a layout.
        
        This creates a unified configuration dict combining:
        - Master config (system orchestrator)
        - Project config (external project-specific info)
        - Layout-specific config (colors, text, images, etc.)
        - External configs (generation, mapper, code, etc.)
        
        Args:
            layout_name: Layout to load. If None, uses default.
        
        Returns:
            Dict with complete merged configuration
        """
        master = self.load_master()
        project = self.load_project()
        layout = self.load_layout(layout_name)
        
        # Build complete config
        complete_config = {
            # Metadata from master (system)
            "description": master.get("description", ""),
            "version": master.get("version", ""),
            "last_updated": master.get("last_updated", ""),
            
            # System info
            "system": master.get("system", {}),
            
            # Project info (external config)
            "project": project.get("project", {}),
            "location": project.get("location", {}),
            "client": project.get("client", {}),
            "consultants": project.get("consultants", {}),
            "team": project.get("team", {}),
            "copyright": project.get("copyright", {}),
            "authors": project.get("authors", []),
            "metadata": project.get("metadata", {}),
            
            # Layout info
            "layout": {
                "name": layout.get("layout_name", layout_name),
                "available": master.get("layouts", {}).get("available", []),
            },
            
            # Layout-specific configurations
            "colors": layout.get("colors", {}),
            "text": layout.get("text", {}),
            "images": layout.get("images", {}),
            "tables": layout.get("tables", {}),
            "notes": layout.get("notes", {}),
            "pages": layout.get("pages", {}),
            "format": layout.get("format", {}),
            
            # Paper and report configurations (now integrated in layouts)
            "paper": layout.get("paper", {}),
            "report": layout.get("report", {}),
        }
        
        # Load and merge external configs
        external_configs = master.get("external_configs", {})
        for config_name in external_configs.keys():
            try:
                external_data = self.load_external(config_name)
                
                # Special handling for palettes: merge into colors section
                if config_name == 'palettes':
                    # Merge palettes into colors configuration
                    if 'palettes' in external_data:
                        if 'colors' not in complete_config:
                            complete_config['colors'] = {}
                        complete_config['colors']['palettes'] = external_data['palettes']
                
                # Special handling for format: merge everything into format section
                elif config_name == 'format':
                    # Merge all format configs (font_families, math_formatting, unicode, html, etc.)
                    if 'format' not in complete_config:
                        complete_config['format'] = {}
                    complete_config['format'].update(external_data)
                
                else:
                    # Add under the config name key
                    if config_name in external_data:
                        complete_config[config_name] = external_data[config_name]
                    else:
                        complete_config[config_name] = external_data
            except FileNotFoundError:
                # External config not found, skip
                pass
        
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
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load {file_path}: {e}")
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


# Global loader instance
_global_loader = None


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


# Convenience functions for common operations
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
