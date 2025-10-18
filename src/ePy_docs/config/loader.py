"""Configuration loader for ePy_docs.

Implements a three-tier configuration strategy:
1. .epyson (source): Human-editable JSON configuration
2. .epyx (cache): Compiled/cached configuration for performance
3. .json (output): Generated configuration for runtime

Priority: .epyx (if fresh) > .epyson > .json
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class ConfigLoader:
    """Loads configuration files with caching strategy."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize configuration loader.
        
        Args:
            base_path: Base path for resources. If None, uses package installation path.
        """
        if base_path is None:
            # Auto-detect: use package installation directory
            self.base_path = Path(__file__).parent.parent / "resources"
        else:
            self.base_path = Path(base_path)
        
        self._cache = {}
    
    def load_config(self, config_name: str, subdir: str = "configs") -> Dict[str, Any]:
        """Load configuration file with caching.
        
        Args:
            config_name: Name of config file (without extension)
            subdir: Subdirectory within resources/ (default: "configs")
        
        Returns:
            Dict with configuration data
        
        Priority:
            1. Check .epyx cache (if fresher than .epyson)
            2. Load .epyson source
            3. Fallback to .json
        """
        # Check memory cache first
        cache_key = f"{subdir}/{config_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        config_dir = self.base_path / subdir
        
        # Define file paths
        epyson_path = config_dir / f"{config_name}.epyson"
        epyx_path = config_dir / f"{config_name}.epyx"
        json_path = config_dir / f"{config_name}.json"
        
        config_data = None
        
        # Strategy 1: Try .epyx cache if fresher than .epyson
        if epyx_path.exists() and epyson_path.exists():
            if self._is_cache_fresh(epyx_path, epyson_path):
                config_data = self._load_json_file(epyx_path)
        
        # Strategy 2: Load .epyson source
        if config_data is None and epyson_path.exists():
            config_data = self._load_json_file(epyson_path)
            # Optionally compile to .epyx for next time
            if config_data:
                self._compile_cache(config_data, epyx_path)
        
        # Strategy 3: Fallback to .json
        if config_data is None and json_path.exists():
            config_data = self._load_json_file(json_path)
        
        # Default: empty dict
        if config_data is None:
            config_data = {}
        
        # Store in memory cache
        self._cache[cache_key] = config_data
        
        return config_data
    
    def _is_cache_fresh(self, cache_path: Path, source_path: Path) -> bool:
        """Check if cache file is fresher than source.
        
        Args:
            cache_path: Path to .epyx cache file
            source_path: Path to .epyson source file
        
        Returns:
            True if cache is fresher than source
        """
        try:
            cache_mtime = os.path.getmtime(cache_path)
            source_mtime = os.path.getmtime(source_path)
            return cache_mtime >= source_mtime
        except OSError:
            return False
    
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
    
    def _compile_cache(self, config_data: Dict[str, Any], cache_path: Path) -> None:
        """Compile configuration to .epyx cache.
        
        Args:
            config_data: Configuration dictionary
            cache_path: Path to .epyx cache file
        """
        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Warning: Could not write cache {cache_path}: {e}")
    
    def clear_cache(self, config_name: Optional[str] = None) -> None:
        """Clear memory cache.
        
        Args:
            config_name: Specific config to clear, or None to clear all
        """
        if config_name:
            keys_to_remove = [k for k in self._cache.keys() if config_name in k]
            for key in keys_to_remove:
                del self._cache[key]
        else:
            self._cache.clear()
    
    def invalidate_cache(self, config_name: str, subdir: str = "configs") -> None:
        """Invalidate .epyx cache file by deleting it.
        
        Args:
            config_name: Name of config file (without extension)
            subdir: Subdirectory within resources/
        """
        epyx_path = self.base_path / subdir / f"{config_name}.epyx"
        try:
            if epyx_path.exists():
                os.remove(epyx_path)
            # Also clear from memory
            self.clear_cache(config_name)
        except OSError as e:
            print(f"Warning: Could not delete cache {epyx_path}: {e}")


# Global loader instance
_global_loader = None

def get_loader() -> ConfigLoader:
    """Get global ConfigLoader instance."""
    global _global_loader
    if _global_loader is None:
        _global_loader = ConfigLoader()
    return _global_loader


def load_config(config_name: str, subdir: str = "configs") -> Dict[str, Any]:
    """Convenience function to load configuration.
    
    Args:
        config_name: Name of config file (without extension)
        subdir: Subdirectory within resources/
    
    Returns:
        Dict with configuration data
    """
    loader = get_loader()
    return loader.load_config(config_name, subdir)
