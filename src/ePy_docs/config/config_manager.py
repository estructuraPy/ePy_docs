"""Configuration management for ePy_docs."""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Centralized configuration management for ePy_docs."""
    
    def __init__(self):
        # Usar __file__ para encontrar el directorio del paquete instalado
        self.package_path = Path(__file__).parent.parent
        self.config_path = Path(__file__).parent
        self.resources_path = self.package_path / "resources" / "configs"
        self._configs = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        """Load all configuration files from master.epyson."""
        master_path = self.config_path / 'master.epyson'
        
        if not master_path.exists():
            print(f"⚠️ Warning: master.epyson not found at {master_path}")
            return
        
        try:
            with open(master_path, 'r', encoding='utf-8') as f:
                master_config = json.load(f)
                # Assign sections to configs
                self._configs = master_config
        except Exception as e:
            print(f"⚠️ Error loading master.epyson: {e}")
            return
    
    def _create_default_config(self, config_file: str):
        """Create default configuration files."""
        config_name = config_file.replace('.epyson', '')
        default_configs = {
            'setup': {
                'default_layout': 'classic',
                'sync_files': False,
                'output_formats': ['html', 'pdf']
            },
            'project_info': {
                'project': {
                    'name': 'Análisis Estructural',
                    'code': 'STRUCT-2025'
                }
            },
            'colors': {
                'primary': '#2E86AB',
                'secondary': '#A23B72',
                'accent': '#F18F01'
            }
        }
        
        if config_name in default_configs:
            config_path = self.resources_path / config_file
            os.makedirs(config_path.parent, exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(default_configs[config_name], f, indent=2, ensure_ascii=False)
            self._configs[config_name] = default_configs[config_name]
    
    def get_config(self, config_name: str = None) -> Dict[str, Any]:
        """Get configuration by name or all configs."""
        if config_name:
            return self._configs.get(config_name, {})
        return {
            'project_config': self._configs.get('project_info', {}),
            'report_config': self._configs.get('report', {}),
            **self._configs
        }
    
    def update_config(self, config_name: str, config_data: Dict[str, Any]):
        """Update a specific configuration."""
        self._configs[config_name] = config_data
        master_path = self.config_path / 'master.epyson'
        with open(master_path, 'w', encoding='utf-8') as f:
            json.dump(self._configs, f, indent=2, ensure_ascii=False)