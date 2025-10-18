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
        """Load all configuration files from their distributed locations."""
        # Primero cargar setup.epyson para obtener las rutas
        setup_path = self.config_path / 'setup.epyson'
        
        if not setup_path.exists():
            print(f"⚠️ Warning: setup.epyson not found at {setup_path}")
            return
        
        try:
            with open(setup_path, 'r', encoding='utf-8') as f:
                setup_config = json.load(f)
                self._configs['setup'] = setup_config
        except Exception as e:
            print(f"⚠️ Error loading setup.epyson: {e}")
            return
        
        # Obtener las rutas de archivos de configuración desde setup
        config_files = setup_config.get('config_files', {})
        
        if not config_files:
            print("⚠️ Warning: No config_files section found in setup.epyson")
            return
        
        # Cargar cada archivo de configuración usando las rutas del setup
        for config_name, relative_path in config_files.items():
            config_path = self.package_path / relative_path
            
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        self._configs[config_name] = json.load(f)
                except Exception as e:
                    print(f"⚠️ Warning: Could not load {config_name}.epyson: {e}")
            else:
                print(f"⚠️ Warning: Config file not found: {config_path}")
                # Create default config if not exists
                self._create_default_config(f"{config_name}.epyson")
    
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
        config_path = self.resources_path / f"{config_name}.epyson"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)