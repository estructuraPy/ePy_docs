"""Enhanced unit converter module that handles complex engineering units."""

import json
import os
import re
from typing import Dict, Union, Any, Optional, List, Tuple
import pandas as pd
from pydantic import BaseModel, Field
import ePy_suite
from ePy_suite.project.setup import DirectoryConfig
from ePy_suite.files.utils.reader import ReadFiles

def _normalize_unit_str(unit_str: str) -> str:
    """Normalize unit representation to handle special characters and formats."""
    if not unit_str:
        return unit_str
        
    superscript_map = {
        '²': '^2', '³': '^3', '⁴': '^4', '⁵': '^5', 'ⁿ': '^n', 'ᵏ': '^k'
    }
    
    result = unit_str
    for sup, repl in superscript_map.items():
        if sup in result:
            result = result.replace(sup, repl)
    
    result = re.sub(r'\s*([\/\*\^\-\·])\s*', r'\1', result)
    result = result.replace('per', '/')
    result = result.replace('·', '-').replace('*', '-')
    
    # Basic patterns for common formats
    result = re.sub(r'(\w+)/(\w+)2\b', r'\1/\2^2', result, flags=re.IGNORECASE)
    result = re.sub(r'(\w+)/(\w+)²\b', r'\1/\2^2', result, flags=re.IGNORECASE)
    result = re.sub(r'(\w+)(\s+)(\w+)\b', r'\1-\3', result, flags=re.IGNORECASE)
        
    return result

def format_unit_display(unit_str: str) -> str:
    """Convert caret notation to Unicode superscripts and format degrees properly.
    
    Args:
        unit_str: Unit string with caret notation (e.g., 'm^2', 'deg')
        
    Returns:
        Formatted unit string with Unicode superscripts (e.g., 'm²', 'º')
    """
    if not unit_str:
        return unit_str
      # Handle degrees - convert 'deg' and 'degrees' to 'º'
    result = unit_str.replace('degrees', 'º').replace('deg', 'º')
    
    # Convert caret notation to Unicode superscripts
    superscript_map = {
        '^0': '⁰',
        '^1': '¹', 
        '^2': '²',
        '^3': '³',
        '^4': '⁴',
        '^5': '⁵',
        '^6': '⁶',
        '^7': '⁷',
        '^8': '⁸',
        '^9': '⁹',
        '^-1': '⁻¹',
        '^-2': '⁻²',
        '^-3': '⁻³'
    }
    
    # Apply superscript conversions
    for caret, unicode_sup in superscript_map.items():
        result = result.replace(caret, unicode_sup)
    
    # Handle more complex patterns like 'm^2/s^3'
    # Use regex to catch any remaining ^n patterns
    def replace_caret_number(match):
        number = match.group(1)
        # Handle negative numbers
        if number.startswith('-'):
            return '⁻' + superscript_map.get(f'^{number[1:]}', number).replace('^', '')
        return superscript_map.get(f'^{number}', f'^{number}')
    
    # Match ^followed by number (including negative)
    result = re.sub(r'\^(-?\d+)', replace_caret_number, result)
    
    return result

def _format_to_significant_figures(value: float, sig_figs: int = 5) -> float:
    """Format a number to specified significant figures while maintaining decimal notation."""
    import math
    
    if value == 0:
        return 0.0
    
    magnitude = math.floor(math.log10(abs(value)))
    factor = 10 ** (sig_figs - 1 - magnitude)
    rounded = round(value * factor) / factor
    
    return float(rounded)

class UnitConverter(BaseModel):
    """Enhanced unit converter with specialized handling for engineering units."""
    units_database: Dict[str, Any] = Field(default_factory=dict)
    prefix_database: Dict[str, Any] = Field(default_factory=dict)
    aliases_database: Dict[str, Any] = Field(default_factory=dict)
    dir_config: Optional[DirectoryConfig] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        # Ensure no None values are passed to Pydantic
        for key in ['units_database', 'prefix_database', 'aliases_database']:
            if key in data and data[key] is None:
                data[key] = {}
              # Load default data if none provided
        if not any(data.get(key) for key in ['units_database', 'prefix_database', 'aliases_database']):
            try:
                # Initialize DirectoryConfig without automatic template sync
                temp_dir_config = DirectoryConfig.minimal()
                all_configs = temp_dir_config.load_all_configs()
                
                data['units_database'] = all_configs.get('units', {})
                data['prefix_database'] = ReadFiles.load_file_data(temp_dir_config, 'prefix.json')
                data['aliases_database'] = ReadFiles.load_file_data(temp_dir_config, 'aliases.json')
                
            except Exception as e:
                print(f"Warning: Could not load default unit data: {e}")
                for key in ['units_database', 'prefix_database', 'aliases_database']:
                    data[key] = data.get(key, {})
        
        super().__init__(**data)
        # Initialize DirectoryConfig without automatic template sync
        self.dir_config = DirectoryConfig.minimal()

    @classmethod
    def from_file(cls, units_file_path: Optional[str] = None, prefix_file_path: Optional[str] = None, aliases_file_path: Optional[str] = None):
        """Create converter instance from files using ReadFiles for consistent handling."""
        # Initialize DirectoryConfig without automatic template sync
        dir_config = DirectoryConfig.minimal()
          # Default file paths with fallback logic similar to create_default()
        if units_file_path is None:
            # Try different locations for conversion.json based on json_templates setting
            potential_paths = []
            
            # If json_templates is enabled, check the config directory first
            if dir_config.settings.json_templates and dir_config.folders.config:
                potential_paths.append(os.path.join(dir_config.folders.config, 'conversion.json'))
            
            # If templates folder is configured, check there
            if dir_config.folders.templates:
                potential_paths.append(os.path.join(dir_config.folders.templates, 'conversion.json'))
            
            # Add fallback to the units package directory (always available)
            units_pkg_dir = os.path.dirname(__file__)
            potential_paths.append(os.path.join(units_pkg_dir, 'conversion.json'))
            
            # Find the first existing path
            units_file_path = None
            for path in potential_paths:
                if os.path.exists(path):
                    units_file_path = path
                    break
            
            if not units_file_path:
                # Last resort fallback
                units_file_path = os.path.join(units_pkg_dir, 'conversion.json')
        
        if prefix_file_path is None:
            if dir_config.folders.templates:
                prefix_file_path = os.path.join(dir_config.folders.templates, 'prefix.json')
            else:
                # Fallback to units package directory
                units_pkg_dir = os.path.dirname(__file__)
                prefix_file_path = os.path.join(units_pkg_dir, 'prefix.json')
        
        if aliases_file_path is None:
            if dir_config.folders.templates:
                aliases_file_path = os.path.join(dir_config.folders.templates, 'aliases.json')
            else:
                # Fallback to units package directory  
                units_pkg_dir = os.path.dirname(__file__)
                aliases_file_path = os.path.join(units_pkg_dir, 'aliases.json')
        
        # Load data from files
        file_data = {}
        for key, file_path in [
            ('units_database', units_file_path),
            ('prefix_database', prefix_file_path),
            ('aliases_database', aliases_file_path)
        ]:
            if os.path.exists(file_path):
                reader = ReadFiles(file_path=file_path)
                file_data[key] = reader.load_json() or {}
            else:
                file_data[key] = {}
        
        return cls(**file_data)

    def _get_prefix_factor(self, prefix_symbol: str) -> float:
        """Get the numerical factor for a given prefix symbol."""
        if not prefix_symbol:
            return 1.0
        
        prefix_data = self.prefix_database.get("prefix", {}) or self.units_database.get("prefix", {})
            
        for prefix_type in ["multiples", "submultiples"]:
            if prefix_type in prefix_data:
                for prefix_name, prefix_info in prefix_data[prefix_type].items():
                    if prefix_info["symbol"] == prefix_symbol:
                        return prefix_info["factor"]
        return 1.0

    def _extract_prefix_and_base(self, unit: str) -> Tuple[str, str]:
        """Extract prefix and base unit using the prefix definitions."""
        special_units = ["°C", "°F", "K", "1/sec", "Hz", "rad/sec", "cyc/min", "percent"]
        if unit in special_units:
            return ("", unit)
        
        prefix_data = self.prefix_database.get("prefix", {}) or self.units_database.get("prefix", {})
        multiples = prefix_data.get("multiples", {})
        submultiples = prefix_data.get("submultiples", {})
        
        for prefix_type in [multiples, submultiples]:
            for prefix_name, prefix_info in prefix_type.items():
                symbol = prefix_info["symbol"]
                if unit.startswith(symbol) and len(unit) > len(symbol):
                    base_unit = unit[len(symbol):]
                    return (symbol, base_unit)
        
        return ("", unit)

    def _get_units_by_category(self, category_name: str) -> List[str]:
        """Get all units from a specific category in the conversion database."""
        categories = self.units_database.get("categories", {})
        category_data = categories.get(category_name, {})
        conversions = category_data.get("conversions", {})
        
        units = set()
        for base_unit in conversions.keys():
            units.add(base_unit)
            if isinstance(conversions[base_unit], dict):
                for target_unit in conversions[base_unit].keys():
                    if not target_unit.startswith("offset_"):
                        units.add(target_unit)
        
        return list(units)

    def _normalize_unit_with_aliases(self, unit_str: str) -> str:
        """Normalize unit string using aliases database."""
        normalized = _normalize_unit_str(unit_str)
        
        # Load aliases if not already loaded
        if not self.aliases_database:
            self.aliases_database = ReadFiles.load_file_data(self.dir_config, 'aliases.json')
        
        unit_aliases = self.aliases_database.get("unit_aliases", {})
        all_aliases = {}
        
        # Collect all aliases from all categories
        for cat_aliases in unit_aliases.values():
            if isinstance(cat_aliases, dict):
                all_aliases.update(cat_aliases)
        
        # Check for direct match
        if normalized in all_aliases:
            return all_aliases[normalized]
              # Check for case-insensitive match
        normalized_lower = normalized.lower()
        for alias, standard in all_aliases.items():
            if alias.lower() == normalized_lower:
                return standard
                
        return normalized

    def _parse_composite_unit(self, unit_str: str) -> Optional[Dict[str, Any]]:
        """Parse composite units into their component parts."""
        unit_str = _normalize_unit_str(unit_str)
        
        # Pattern for division units like N/mm
        division_match = re.match(r'^([^/]+)/([^/]+)$', unit_str)
        if division_match:
            return {
                'type': 'composite',
                'numerator': division_match.group(1).strip(),
                'denominator': division_match.group(2).strip(),
                'operation': 'division'
            }
        
        # Pattern for multiplication units like kgf-m, kgf·m
        multiplication_match = re.match(r'^([^-·*]+)[-·*]([^-·*]+)$', unit_str)
        if multiplication_match:
            return {
                'type': 'composite',
                'part1': multiplication_match.group(1).strip(),
                'part2': multiplication_match.group(2).strip(),
                'operation': 'multiplication'
            }
        
        # Pattern for concatenated units like kgfcm, Nm, etc.
        # Try to match common patterns for moment/torque units
        concatenated_patterns = [
            (r'^(kgf)(cm|m|mm)$', 'multiplication'),  # kgfcm, kgfm, kgfmm
            (r'^(N)(m|mm|cm)$', 'multiplication'),    # Nm, Nmm, Ncm
            (r'^(lbf)(ft|in)$', 'multiplication'),    # lbfft, lbfin
            (r'^(tf)(m|cm|mm)$', 'multiplication'),   # tfm, tfcm, tfmm
        ]
        
        for pattern, operation in concatenated_patterns:
            match = re.match(pattern, unit_str, re.IGNORECASE)
            if match:
                return {
                    'type': 'composite',
                    'part1': match.group(1),
                    'part2': match.group(2),
                    'operation': operation
                }
        
        return None

    def get_direct_conversion_factor(self, current_unit: str, target_unit: str) -> Optional[float]:
        """Get the direct conversion factor between two simple units."""
        current_unit = _normalize_unit_str(current_unit)
        target_unit = _normalize_unit_str(target_unit)
        
        if current_unit == target_unit:
            return 1.0
        
        # Handle power units
        if "^" in current_unit and "^" in target_unit:
            current_match = re.match(r'(.+)\^(\d+)', current_unit)
            target_match = re.match(r'(.+)\^(\d+)', target_unit)
            
            if current_match and target_match:
                current_base = current_match.group(1)
                target_base = target_match.group(1)
                current_power = int(current_match.group(2))
                target_power = int(target_match.group(2))
                
                if current_power == target_power:
                    base_factor = self.get_direct_conversion_factor(current_base, target_base)
                    if base_factor is not None:
                        return base_factor ** current_power
        
        # Handle prefix units
        current_prefix_symbol, current_base_unit = self._extract_prefix_and_base(current_unit)
        target_prefix_symbol, target_base_unit = self._extract_prefix_and_base(target_unit)

        if current_base_unit == target_base_unit:
            current_factor = self._get_prefix_factor(current_prefix_symbol)
            target_factor = self._get_prefix_factor(target_prefix_symbol)
            
            if target_factor == 0:
                return None
            return current_factor / target_factor

        # Search in conversion database
        for category_data in self.units_database.get("categories", {}).values():
            if not isinstance(category_data, dict) or "conversions" not in category_data:
                continue
            
            conversions = category_data["conversions"]
            
            if current_unit in conversions and isinstance(conversions[current_unit], dict) and target_unit in conversions[current_unit]:
                return conversions[current_unit][target_unit]
                
            if current_base_unit in conversions and isinstance(conversions[current_base_unit], dict) and target_base_unit in conversions[current_base_unit]:
                base_factor = conversions[current_base_unit][target_base_unit]
                current_prefix_factor = self._get_prefix_factor(current_prefix_symbol)
                target_prefix_factor = self._get_prefix_factor(target_prefix_symbol)
                
                if target_prefix_factor == 0:
                    return None
                return base_factor * (current_prefix_factor / target_prefix_factor)

        return None

    def _convert_composite_unit(self, value: float, from_unit: str, to_unit: str) -> Union[float, str]:
        """Convert composite units by breaking them into components."""
        from_components = self._parse_composite_unit(from_unit)
        to_components = self._parse_composite_unit(to_unit)
        
        if not from_components or not to_components:
            return f"Cannot parse composite units: {from_unit} -> {to_unit}"
        
        if from_components['operation'] != to_components['operation']:
            return f"Incompatible composite unit operations: {from_unit} -> {to_unit}"
        
        try:
            if from_components['operation'] == 'division':
                # Convert numerator and denominator separately
                num_result = self.universal_unit_converter(1.0, from_components['numerator'], to_components['numerator'])
                den_result = self.universal_unit_converter(1.0, from_components['denominator'], to_components['denominator'])
                
                if isinstance(num_result, str) or isinstance(den_result, str):
                    return f"Cannot convert components: {from_unit} -> {to_unit}"
                
                return value * (num_result / den_result)
                
            elif from_components['operation'] == 'multiplication':
                # Convert both parts separately
                part1_result = self.universal_unit_converter(1.0, from_components['part1'], to_components['part1'])
                part2_result = self.universal_unit_converter(1.0, from_components['part2'], to_components['part2'])
                
                if isinstance(part1_result, str) or isinstance(part2_result, str):
                    return f"Cannot convert components: {from_unit} -> {to_unit}"
                
                return value * (part1_result * part2_result)
        
        except Exception as e:
            return f"Error in composite conversion: {e}"
        
        return f"Unsupported composite unit conversion: {from_unit} -> {to_unit}"

    def universal_unit_converter(self, value: float, current_unit: str, target_unit: str) -> Union[float, str]:
        """Universal unit converter that uses conversion.json and aliases.json databases."""
        if current_unit == target_unit:
            return value
            
        current_unit_norm = self._normalize_unit_with_aliases(current_unit)
        target_unit_norm = self._normalize_unit_with_aliases(target_unit)
        
        if current_unit_norm == target_unit_norm:
            return value

        # Try direct conversion from database
        categories = self.units_database.get("categories", {})
        for category_name, category_data in categories.items():
            if not isinstance(category_data, dict):
                continue
                
            conversions = category_data.get("conversions", {})
            if not isinstance(conversions, dict):
                continue
            
            # Forward direction
            if current_unit_norm in conversions and isinstance(conversions[current_unit_norm], dict):
                if target_unit_norm in conversions[current_unit_norm]:
                    factor = conversions[current_unit_norm][target_unit_norm]
                    result = value * factor
                    return _format_to_significant_figures(result, 5)
            
            # Reverse direction
            if target_unit_norm in conversions and isinstance(conversions[target_unit_norm], dict):
                if current_unit_norm in conversions[target_unit_norm]:
                    factor = 1.0 / conversions[target_unit_norm][current_unit_norm]
                    result = value * factor
                    return _format_to_significant_figures(result, 5)
        
        # Try composite unit conversion
        composite_result = self._convert_composite_unit(value, current_unit_norm, target_unit_norm)
        if isinstance(composite_result, (int, float)):
            return _format_to_significant_figures(composite_result, 5)
        elif not isinstance(composite_result, str) or not composite_result.startswith(("Cannot parse", "Unsupported")):
            return composite_result
        
        # Try direct conversion factor
        direct_factor = self.get_direct_conversion_factor(current_unit, target_unit)
        if direct_factor is not None:
            result = value * direct_factor
            return _format_to_significant_figures(result, 5)
                
        return f"Conversion from {current_unit} to {target_unit} not supported."

    def add_unit_conversion(self, category: str, from_unit: str, to_unit: str, factor: float, bidirectional: bool = True) -> None:
        """Add a new unit conversion to the database."""
        if category not in self.units_database["categories"]:
            self.units_database["categories"][category] = {"conversions": {}}
        if "conversions" not in self.units_database["categories"][category]:
            self.units_database["categories"][category]["conversions"] = {}
        if from_unit not in self.units_database["categories"][category]["conversions"]:
            self.units_database["categories"][category]["conversions"][from_unit] = {}
        
        self.units_database["categories"][category]["conversions"][from_unit][to_unit] = factor
        
        if bidirectional:
            if to_unit not in self.units_database["categories"][category]["conversions"]:
                self.units_database["categories"][category]["conversions"][to_unit] = {}
            self.units_database["categories"][category]["conversions"][to_unit][from_unit] = 1.0 / factor

    def save_units_conversion(self, filepath: str) -> None:
        """Save the units database to a JSON file."""
        with open(filepath, "w") as file:            json.dump(self.units_database, file, indent=2)
        print(f"Units conversion data saved to {filepath}")

    @classmethod
    def create_default(cls, dir_config: Optional['DirectoryConfig'] = None) -> 'UnitConverter':
        """Create a UnitConverter instance with default configuration.
        
        Args:
            dir_config: Optional DirectoryConfig to use. If None, will try to get current project config
        
        Returns:
            UnitConverter instance with default settings
            
        Assumptions:            Default configuration files are available in the expected locations
        """
        try:
            from ePy_suite.project.setup import DirectoryConfig, get_current_project_config
            
            # Try to get configuration files - use provided config or current project config
            if dir_config is None:
                dir_config = get_current_project_config()
                if dir_config is None:
                    dir_config = DirectoryConfig.minimal()            # Load units configuration using the proper method
            units_config = dir_config.load_config_file('units')            # Load conversion data from conversion.json
            conversion_config = None
            conversion_path = None
              # Try different locations for conversion.json based on json_templates setting
            potential_paths = []
            
            # If json_templates is enabled, check the config directory first
            if dir_config.settings.json_templates and dir_config.folders.config:
                potential_paths.append(os.path.join(dir_config.folders.config, 'conversion.json'))
            
            # If templates folder is configured, check there
            if dir_config.folders.templates:
                potential_paths.append(os.path.join(dir_config.folders.templates, 'conversion.json'))
            
            # Add fallback to the units package directory (always available)
            units_pkg_dir = os.path.dirname(__file__)  # This is the src/ePy_suite/units directory
            potential_paths.append(os.path.join(units_pkg_dir, 'conversion.json'))
            
            # Find the first existing path
            for path in potential_paths:
                if os.path.exists(path):
                    conversion_path = path
                    break
            
            if conversion_path:
                from ePy_suite.files.utils.reader import ReadFiles
                reader = ReadFiles(file_path=conversion_path)
                conversion_config = reader.load_json()
                # Conversion data loaded silently
            else:
                raise FileNotFoundError(f"Conversion file not found: {conversion_path}")
            
            # Use conversion config for units database if available, otherwise use units config
            units_database = conversion_config if conversion_config else units_config
            
            # Determine the base path for other configuration files
            if dir_config.settings.json_templates and dir_config.folders.config:
                # Use local config directory when sync is enabled
                base_config_path = dir_config.folders.config
            else:
                # Use templates directory when sync is disabled
                base_config_path = dir_config.folders.templates
            
            # Try to load prefix configuration
            prefix_file_paths = [
                os.path.join(base_config_path, 'units', 'prefix.json'),
                os.path.join(base_config_path, 'prefix.json')
            ]
            
            prefix_file_path = None
            for path in prefix_file_paths:
                if os.path.exists(path):
                    prefix_file_path = path
                    break
            
            # Try to load aliases configuration
            aliases_file_paths = [
                os.path.join(base_config_path, 'units', 'aliases.json'),
                os.path.join(base_config_path, 'aliases.json')
            ]
            
            aliases_file_path = None
            for path in aliases_file_paths:
                if os.path.exists(path):
                    aliases_file_path = path
                    break
            
            # Load prefix and aliases data
            prefix_data = {}
            aliases_data = {}
            
            if prefix_file_path and os.path.exists(prefix_file_path):
                from ePy_suite.files.utils.reader import ReadFiles
                reader = ReadFiles(file_path=prefix_file_path)
                prefix_data = reader.load_json() or {}
                
            if aliases_file_path and os.path.exists(aliases_file_path):
                from ePy_suite.files.utils.reader import ReadFiles
                reader = ReadFiles(file_path=aliases_file_path)
                aliases_data = reader.load_json() or {}
              # Create instance with loaded data
            return cls(
                units_database=units_database,
                prefix_database=prefix_data,
                aliases_database=aliases_data
            )
            
        except Exception as e:
            print(f"Warning: Could not create UnitConverter with configuration files: {e}")
            # Return basic instance without configuration files
            return cls()
    

# Simplified standalone functions

def _get_default_units_mapping_from_aliases() -> Dict[str, Tuple[str, str]]:
    """Get default units mapping from aliases.json file."""
    try:
        # Initialize DirectoryConfig without automatic template sync
        dir_config = DirectoryConfig.minimal()
        aliases_data = ReadFiles.load_file_data(dir_config, 'aliases.json')
        
        if not aliases_data:
            print(f"Warning: aliases.json not found or empty")
            return {}
        
        unit_aliases = aliases_data.get("unit_aliases", {})
        mapping = {}
        
        # Build mapping based on available categories
        category_mappings = {
            "force": ["FX", "FY", "FZ"],
            "moment": ["MX", "MY", "MZ"],
            "length": ["X", "Y", "Z", "DX", "DY", "DZ"],
            "stress": ["SIG_X", "SIG_Y", "SIG_Z", "TAU_XY", "TAU_XZ", "TAU_YZ"],
            "area": ["AREA"],
            "volume": ["VOLUME"],
            "temperature": ["TEMP", "TEMPERATURE"],
            "angle": ["ANGLE", "ROTATION"]
        }
        
        for category, columns in category_mappings.items():
            if category in unit_aliases:
                for col in columns:
                    mapping[col] = (category, "target_units")
        
        return mapping
        
    except Exception as e:
        print(f"Warning: Could not get default mappings from aliases.json: {e}")
        return {}

def load_units_config() -> dict:
    """Load units configuration using DirectoryConfig."""
    try:
        # Initialize DirectoryConfig without automatic template sync
        dir_config = DirectoryConfig.minimal()
        return dir_config.load_config_file('units')
    except Exception as e:
        print(f"Warning: Could not load units config: {e}")
        return {}

def get_available_unit_categories() -> List[str]:
    """Get list of available unit categories from aliases.json."""
    try:
        # Initialize DirectoryConfig without automatic template sync
        dir_config = DirectoryConfig.minimal()
        aliases_data = ReadFiles.load_file_data(dir_config, 'aliases.json')
        
        if aliases_data and "unit_aliases" in aliases_data:
            return list(aliases_data["unit_aliases"].keys())
        
        return []
        
    except Exception as e:
        return []

def get_aliases_for_category(category: str) -> Dict[str, str]:
    """Get aliases for a specific category from aliases.json."""
    try:
        # Initialize DirectoryConfig without automatic template sync
        dir_config = DirectoryConfig.minimal()
        aliases_data = ReadFiles.load_file_data(dir_config, 'aliases.json')
        
        if aliases_data and "unit_aliases" in aliases_data:
            unit_aliases = aliases_data["unit_aliases"]
            return unit_aliases.get(category, {})
        
        return {}
        
    except Exception as e:
        print(f"Warning: Could not get aliases for category {category}: {e}")
        return {}

def clear_json_cache():
    """Clear the JSON cache to force reloading of files."""
    from ePy_suite.utils.data import _JSON_DATA_CACHE
    _JSON_DATA_CACHE.clear()
    print("JSON cache cleared - all conversion data will be reloaded")

def reload_conversion_data():
    """Reload conversion data from file, bypassing cache."""
    clear_json_cache()
    converter = UnitConverter.create_default()
    print("Conversion data reloaded from files")
    return converter

def get_unit_from_config(units_config: Dict[str, Any], category: str, key: str) -> Optional[str]:
    """Get unit from configuration by category and key.
    
    Args:
        units_config: Units configuration dictionary
        category: Category name (e.g., 'forces', 'structure_dimensions')
        key: Key within category (e.g., 'force', 'length')
        
    Returns:
        Unit string if found, None otherwise
        
    Assumptions:
        Configuration follows expected structure with categories and keys
        Unit information is stored as strings or in structured format
    """
    try:
        category_data = units_config.get("categories", {}).get(category, {})
        if isinstance(category_data, dict):
            unit_data = category_data.get(key, None)
              # Handle different formats
            if isinstance(unit_data, str):
                raw_unit = unit_data
            elif isinstance(unit_data, list) and unit_data:
                raw_unit = unit_data[0]  # Return first unit as default
            elif isinstance(unit_data, dict):
                raw_unit = unit_data.get("unit", None)
            else:
                raw_unit = None
            
            # If we have a unit, normalize it using the alias system
            if raw_unit:
                # Try to create a UnitConverter to use the alias normalization
                try:
                    from ePy_suite.project.setup import get_current_project_config
                    current_config = get_current_project_config()
                    if current_config:
                        converter = UnitConverter.create_default(current_config)
                        normalized_unit = converter._normalize_unit_with_aliases(raw_unit)
                        return normalized_unit
                    else:
                        # Fallback to basic normalization
                        return _normalize_unit_str(raw_unit)
                except Exception:
                    # If normalization fails, return the raw unit
                    return raw_unit
            
            return raw_unit
        
        print(f"Unit for {category} - {key} not found in configuration.")
        return None
        
    except (KeyError, TypeError, AttributeError) as e:
        print(f"Error accessing unit for {category} - {key}: {e}")
        return None

def create_compound_unit(base_unit: str, power: int) -> str:
    """Create compound units by raising base unit to a power.
    
    Args:
        base_unit: The base unit (e.g., 'm', 'ft', 'mm')
        power: The power to raise the unit to
        
    Returns:
        String representation of the compound unit
        
    Examples:
        create_compound_unit('m', 2) -> 'm²'
        create_compound_unit('ft', 4) -> 'ft⁴'
        create_compound_unit('kN', 1) -> 'kN'
        create_compound_unit('MPa', 1) -> 'MPa'
    """
    if power == 1:
        return base_unit
    elif power == 2:
        return f"{base_unit}²"
    elif power == 3:
        return f"{base_unit}³"
    elif power == 4:
        return f"{base_unit}⁴"
    elif power == 5:
        return f"{base_unit}⁵"
    elif power == 6:
        return f"{base_unit}⁶"
    elif power == -1:
        return f"1/{base_unit}"
    elif power == -2:
        return f"1/{base_unit}²"
    elif power == -3:
        return f"1/{base_unit}³"
    else:
        return f"{base_unit}^{power}"


def create_composite_unit(numerator_unit: str, denominator_unit: str, 
                         numerator_power: int = 1, denominator_power: int = 1) -> str:
    """Create composite units with numerator and denominator.
    
    Args:
        numerator_unit: The numerator unit (e.g., 'kN', 'N', 'kgf')
        denominator_unit: The denominator unit (e.g., 'm', 'mm', 'cm')
        numerator_power: Power for the numerator unit
        denominator_power: Power for the denominator unit
        
    Returns:
        String representation of the composite unit
        
    Examples:
        create_composite_unit('kN', 'm', 1, 2) -> 'kN/m²'
        create_composite_unit('N', 'mm', 1, 2) -> 'N/mm²'
        create_composite_unit('kgf', 'cm', 1, 1) -> 'kgf/cm'
        create_composite_unit('MPa', 'm', 1, 1) -> 'MPa/m'
    """
    num_unit = create_compound_unit(numerator_unit, numerator_power)
    den_unit = create_compound_unit(denominator_unit, denominator_power)
    
    return f"{num_unit}/{den_unit}"


def create_moment_unit(force_unit: str, length_unit: str) -> str:
    """Create moment/torque units by combining force and length units.
    
    Args:
        force_unit: The force unit (e.g., 'kN', 'N', 'kgf', 'lbf')
        length_unit: The length unit (e.g., 'm', 'mm', 'cm', 'ft', 'in')
        
    Returns:
        String representation of the moment unit
        
    Examples:
        create_moment_unit('kN', 'm') -> 'kN⋅m'
        create_moment_unit('N', 'mm') -> 'N⋅mm'
        create_moment_unit('kgf', 'cm') -> 'kgf⋅cm'
        create_moment_unit('lbf', 'ft') -> 'lbf⋅ft'
    """
    return f"{force_unit}⋅{length_unit}"


def get_dimensional_units(base_unit: str) -> Dict[str, str]:
    """Get standard dimensional units for geometric properties based on a base length unit.
    
    Uses the exact function names from RectangularSection class to maintain consistency.
    
    Args:
        base_unit: Base length unit (e.g., 'm', 'ft', 'mm')
        
    Returns:
        Dictionary mapping property types to their dimensional units using RectangularSection function names
    """
    return {
        # Basic geometric properties
        'area': create_compound_unit(base_unit, 2),                    # L² - from area()
        'length': create_compound_unit(base_unit, 1),                  # L
        'volume': create_compound_unit(base_unit, 3),                  # L³
        
        # Moment of inertia properties - from moment_of_inertia()
        'moment_of_inertia': create_compound_unit(base_unit, 4),       # L⁴
        'moment_of_inertia_yy': create_compound_unit(base_unit, 4),    # L⁴
        'moment_of_inertia_zz': create_compound_unit(base_unit, 4),    # L⁴
        
        # Section modulus properties - from elastic_section_modulus()
        'elastic_section_modulus': create_compound_unit(base_unit, 3), # L³
        'elastic_section_modulus_yy': create_compound_unit(base_unit, 3), # L³
        'elastic_section_modulus_zz': create_compound_unit(base_unit, 3), # L³
        
        # Plastic section modulus properties - from plastic_section_modulus()
        'plastic_section_modulus': create_compound_unit(base_unit, 3), # L³
        'plastic_section_modulus_yy': create_compound_unit(base_unit, 3), # L³
        'plastic_section_modulus_zz': create_compound_unit(base_unit, 3), # L³
        
        # Radius of gyration properties - from radius_of_gyration()
        'radius_of_gyration': create_compound_unit(base_unit, 1),      # L
        'radius_of_gyration_yy': create_compound_unit(base_unit, 1),   # L
        'radius_of_gyration_zz': create_compound_unit(base_unit, 1),   # L
        
        # Polar moment - from polar_moment_of_inertia()
        'polar_moment_of_inertia': create_compound_unit(base_unit, 4), # L⁴
        
        # Short names for compatibility with existing code
        'Iy': create_compound_unit(base_unit, 4),                      # L⁴
        'Iz': create_compound_unit(base_unit, 4),                      # L⁴
        'Sy': create_compound_unit(base_unit, 3),                      # L³
        'Sz': create_compound_unit(base_unit, 3),                      # L³
        'Zy': create_compound_unit(base_unit, 3),                      # L³
        'Zz': create_compound_unit(base_unit, 3),                      # L³
        'ry': create_compound_unit(base_unit, 1),                      # L
        'rz': create_compound_unit(base_unit, 1),                      # L
        'polar_moment': create_compound_unit(base_unit, 4),            # L⁴
    }


def get_structural_units(force_unit: str, length_unit: str) -> Dict[str, str]:
    """Get comprehensive structural engineering units based on force and length units.
    
    Args:
        force_unit: Base force unit (e.g., 'kN', 'N', 'kgf', 'lbf')
        length_unit: Base length unit (e.g., 'm', 'mm', 'cm', 'ft', 'in')
        
    Returns:
        Dictionary mapping structural property types to their units
        
    Examples:
        get_structural_units('kN', 'm') returns units like 'kN', 'm', 'kN/m²', 'kN⋅m'
        get_structural_units('N', 'mm') returns units like 'N', 'mm', 'N/mm²', 'N⋅mm'
    """
    base_dimensional = get_dimensional_units(length_unit)
    
    # Add force-related units
    structural_units = base_dimensional.copy()
    structural_units.update({
        # Forces
        'force': force_unit,                                           # F
        'horizontal_force': force_unit,                                # F
        'vertical_force': force_unit,                                  # F
        'reaction': force_unit,                                        # F
        
        # Moments
        'moment': create_moment_unit(force_unit, length_unit),         # F⋅L
        'moment_x': create_moment_unit(force_unit, length_unit),       # F⋅L
        'moment_y': create_moment_unit(force_unit, length_unit),       # F⋅L
        'moment_z': create_moment_unit(force_unit, length_unit),       # F⋅L
        'torque': create_moment_unit(force_unit, length_unit),         # F⋅L
        
        # Pressures and stresses
        'pressure': create_composite_unit(force_unit, length_unit, 1, 2),    # F/L²
        'stress': create_composite_unit(force_unit, length_unit, 1, 2),      # F/L²
        'bearing_pressure': create_composite_unit(force_unit, length_unit, 1, 2), # F/L²
        'soil_pressure': create_composite_unit(force_unit, length_unit, 1, 2),    # F/L²
        
        # Distributed loads
        'distributed_load': create_composite_unit(force_unit, length_unit, 1, 1),      # F/L
        'distributed_moment': create_composite_unit(force_unit, length_unit, 1, 0),    # F⋅L/L = F
        
        # Stiffness and reaction coefficients
        'stiffness': create_composite_unit(force_unit, length_unit, 1, 1),             # F/L
        'rotational_stiffness': create_composite_unit(force_unit, length_unit, 1, 0),  # F⋅L/rad = F⋅L
        'reaction_coefficient': create_composite_unit(force_unit, length_unit, 1, 3),  # F/L³
        'horizontal_reaction_coefficient': create_composite_unit(force_unit, length_unit, 1, 3), # F/L³
        'vertical_reaction_coefficient': create_composite_unit(force_unit, length_unit, 1, 3),   # F/L³
        
        # Material properties
        'elastic_modulus': create_composite_unit(force_unit, length_unit, 1, 2),       # F/L²
        'shear_modulus': create_composite_unit(force_unit, length_unit, 1, 2),         # F/L²
        'deformation_modulus': create_composite_unit(force_unit, length_unit, 1, 2),   # F/L²
        
        # Dimensionless
        'safety_factor': '1',                                          # Dimensionless
        'load_factor': '1',                                            # Dimensionless
        'soil_ratio': '1',                                             # Dimensionless
        'angle': 'rad',                                                # Angle
        'angle_degrees': '°',                                          # Angle in degrees
    })
    
    return structural_units


def get_foundation_units(force_unit: str, length_unit: str) -> Dict[str, str]:
    """Get specific units for foundation engineering based on force and length units.
    
    Args:
        force_unit: Base force unit (e.g., 'kN', 'N', 'kgf', 'lbf')
        length_unit: Base length unit (e.g., 'm', 'mm', 'cm', 'ft', 'in')
        
    Returns:
        Dictionary mapping foundation-specific property types to their units
    """
    structural_units = get_structural_units(force_unit, length_unit)
    
    # Add foundation-specific units
    foundation_units = structural_units.copy()
    foundation_units.update({
        # Foundation geometry
        'foundation_width': length_unit,                               # L
        'foundation_length': length_unit,                              # L
        'foundation_depth': length_unit,                               # L
        'foundation_height': length_unit,                              # L
        'block_height': length_unit,                                   # L
        'thickness': length_unit,                                      # L
        
        # Eccentricities
        'eccentricity': length_unit,                                   # L
        'eccentricity_x': length_unit,                                 # L
        'eccentricity_y': length_unit,                                 # L
        'reduced_eccentricity': length_unit,                           # L
        
        # Foundation-specific pressures
        'vertical_pressure': create_composite_unit(force_unit, length_unit, 1, 2),     # F/L²
        'lateral_pressure': create_composite_unit(force_unit, length_unit, 1, 2),      # F/L²
        'biaxial_pressure': create_composite_unit(force_unit, length_unit, 1, 2),      # F/L²
        'uniaxial_pressure': create_composite_unit(force_unit, length_unit, 1, 2),     # F/L²
        
        # Soil properties
        'soil_bearing_capacity': create_composite_unit(force_unit, length_unit, 1, 2), # F/L²
        'allowable_bearing_pressure': create_composite_unit(force_unit, length_unit, 1, 2), # F/L²
        
        # Foundation analysis results
        'moment_strength': create_moment_unit(force_unit, length_unit),                # F⋅L
        'moment_strength_x': create_moment_unit(force_unit, length_unit),              # F⋅L
        'moment_strength_y': create_moment_unit(force_unit, length_unit),              # F⋅L
    })
    
    return foundation_units
