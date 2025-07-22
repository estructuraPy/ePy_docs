"""Enhanced unit converter module that handles complex engineering units."""

import json
import os
import re
from typing import Dict, Union, Any, Optional, List, Tuple
import pandas as pd
from pydantic import BaseModel, Field
from ePy_docs.project.setup import DirectoryConfig
from ePy_docs.files.reader import ReadFiles

def _normalize_unit_str(unit_str: str, superscript_mappings: Dict[str, str] = None, 
                       operator_mappings: Dict[str, str] = None) -> str:
    """Normalize unit representation using configuration mappings."""
    if not unit_str:
        return unit_str
    
    if not superscript_mappings or not operator_mappings:
        return unit_str
        
    result = unit_str
    
    # Apply superscript mappings from config
    for sup, repl in superscript_mappings.items():
        if sup in result:
            result = result.replace(sup, repl)
    
    # Apply operator mappings from config
    for original, replacement in operator_mappings.items():
        result = result.replace(original, replacement)
    
    # Apply regex patterns if defined in config
    result = re.sub(r'\s*([\/\*\^\-\·])\s*', r'\1', result)
    result = re.sub(r'(\w+)/(\w+)2\b', r'\1/\2^2', result, flags=re.IGNORECASE)
    result = re.sub(r'(\w+)/(\w+)²\b', r'\1/\2^2', result, flags=re.IGNORECASE)
    # Remove the aggressive space-to-dash conversion - this should be handled by create_moment_unit instead
    # result = re.sub(r'(\w+)(\s+)(\w+)\b', r'\1-\3', result, flags=re.IGNORECASE)
        
    return result

def format_unit_display(unit_str: str, format_type: str = "unicode", 
                        format_mappings: Dict[str, Any] = None) -> str:
    """Convert caret notation to appropriate format using configuration mappings.
    
    Args:
        unit_str: Unit string with caret notation
        format_type: Type of format - 'unicode', 'html', 'latex', or 'plain'
        format_mappings: Configuration mappings for different formats
        
    Returns:
        Formatted unit string according to format type
    """
    if not unit_str:
        return unit_str
    
    if not format_mappings:
        return unit_str
        
    # Get format-specific mappings from config
    format_config = format_mappings.get(format_type, {})
    if not format_config:
        return unit_str
    
    result = unit_str
    
    # Apply degree conversions from config
    degree_mappings = format_config.get('degrees', {})
    for original, replacement in degree_mappings.items():
        result = result.replace(original, replacement)
    
    # Apply superscript conversions from config
    superscript_mappings = format_config.get('superscripts', {})
    for caret, formatted_sup in superscript_mappings.items():
        result = result.replace(caret, formatted_sup)
    
    # Apply regex patterns from config if available
    regex_patterns = format_config.get('regex_patterns', [])
    for pattern_config in regex_patterns:
        pattern = pattern_config.get('pattern')
        replacement = pattern_config.get('replacement')
        if pattern and replacement:
            result = re.sub(pattern, replacement, result)
    
    return result


def format_unit_for_output(unit_str: str, output_format: str = None, 
                          format_mappings: Dict[str, Any] = None) -> str:
    """Format units for specific output formats using configuration mappings.
    
    Args:
        unit_str: Unit string to format
        output_format: Target output format
        format_mappings: Configuration mappings for formats
        
    Returns:
        Formatted unit string optimized for the target format
    """
    if not unit_str or not output_format or not format_mappings:
        return unit_str
    
    output_format = output_format.lower()
    
    # Get format mapping from config
    format_map = format_mappings.get('output_format_mapping', {})
    target_format = format_map.get(output_format)
    
    if not target_format:
        return unit_str
    
    return format_unit_display(unit_str, target_format, format_mappings)

def _format_to_significant_figures(value: float, sig_figs: int, precision_config: Dict[str, Any] = None) -> float:
    """Format a number to specified significant figures using configuration."""
    import math
    
    if not precision_config:
        return value
    
    if value == 0:
        return 0.0
    
    # Use configuration values instead of hardcoded ones
    default_precision = precision_config.get('default_precision', sig_figs)
    rounding_method = precision_config.get('rounding_method', 'round_half_up')
    
    magnitude = math.floor(math.log10(abs(value)))
    factor = 10 ** (default_precision - 1 - magnitude)
    
    if rounding_method == 'round_half_up':
        rounded = round(value * factor) / factor
    else:
        rounded = round(value * factor) / factor
    
    return float(rounded)

class UnitConverter(BaseModel):
    """Enhanced unit converter with configuration-driven behavior."""
    units_database: Dict[str, Any] = Field(default_factory=dict)
    prefix_database: Dict[str, Any] = Field(default_factory=dict)
    aliases_database: Dict[str, Any] = Field(default_factory=dict)
    format_mappings: Dict[str, Any] = Field(default_factory=dict)
    conversion_config: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)

    @classmethod
    def from_files(cls, conversion_file: str, prefix_file: str, aliases_file: str, 
                   format_file: str = None) -> 'UnitConverter':
        """Create converter instance from specific configuration files.
        
        Args:
            conversion_file: Path to conversion.json
            prefix_file: Path to prefix.json  
            aliases_file: Path to aliases.json
            format_file: Optional path to format configuration
            
        Returns:
            UnitConverter instance
            
        Raises:
            FileNotFoundError: If required files don't exist
            ValueError: If files contain invalid data
        """
        if not os.path.exists(conversion_file):
            raise FileNotFoundError(f"Conversion file not found: {conversion_file}")
        if not os.path.exists(prefix_file):
            raise FileNotFoundError(f"Prefix file not found: {prefix_file}")
        if not os.path.exists(aliases_file):
            raise FileNotFoundError(f"Aliases file not found: {aliases_file}")
        
        # Load data from files
        with open(conversion_file, 'r', encoding='utf-8') as f:
            units_database = json.load(f)
        
        with open(prefix_file, 'r', encoding='utf-8') as f:
            prefix_database = json.load(f)
            
        with open(aliases_file, 'r', encoding='utf-8') as f:
            aliases_database = json.load(f)
        
        format_mappings = {}
        if format_file and os.path.exists(format_file):
            with open(format_file, 'r', encoding='utf-8') as f:
                format_mappings = json.load(f)
        
        # Validate required structure
        if 'categories' not in units_database:
            raise ValueError("units_database missing 'categories' key")
        if 'prefixes' not in prefix_database:
            raise ValueError("prefix_database missing 'prefixes' key")
        if 'categories' not in aliases_database:
            raise ValueError("aliases_database missing 'categories' key")
        
        return cls(
            units_database=units_database,
            prefix_database=prefix_database,
            aliases_database=aliases_database,
            format_mappings=format_mappings,
            conversion_config=units_database.get('conversion_accuracy', {})
        )

    def _get_prefix_factor(self, prefix_symbol: str) -> Optional[float]:
        """Get the numerical factor for a given prefix symbol from configuration."""
        if not prefix_symbol or not self.prefix_database:
            return None
        
        prefix_data = self.prefix_database.get("prefixes", {})
        if not prefix_data:
            return None
            
        for prefix_type in ["multiples", "submultiples"]:
            type_data = prefix_data.get(prefix_type, {})
            for prefix_name, prefix_info in type_data.items():
                if prefix_info.get("symbol") == prefix_symbol:
                    return prefix_info.get("factor")
        
        return None

    def _extract_prefix_and_base(self, unit: str) -> Tuple[Optional[str], str]:
        """Extract prefix and base unit using prefix definitions from configuration."""
        if not unit or not self.prefix_database:
            return (None, unit)
        
        # Check for special units that should not be split
        special_units = self.conversion_config.get('special_units', [])
        if unit in special_units:
            return (None, unit)
        
        prefix_data = self.prefix_database.get("prefixes", {})
        if not prefix_data:
            return (None, unit)
        
        multiples = prefix_data.get("multiples", {})
        submultiples = prefix_data.get("submultiples", {})
        
        for prefix_type in [multiples, submultiples]:
            for prefix_name, prefix_info in prefix_type.items():
                symbol = prefix_info.get("symbol")
                if symbol and unit.startswith(symbol) and len(unit) > len(symbol):
                    base_unit = unit[len(symbol):]
                    return (symbol, base_unit)
        
        return (None, unit)

    def _get_units_by_category(self, category_name: str) -> List[str]:
        """Get all units from a specific category in the conversion database."""
        if not self.units_database:
            return []
            
        categories = self.units_database.get("categories", {})
        category_data = categories.get(category_name, {})
        conversions = category_data.get("conversions", {})
        
        if not conversions:
            return []
        
        units = set()
        for base_unit, conversion_data in conversions.items():
            units.add(base_unit)
            if isinstance(conversion_data, dict):
                for target_unit in conversion_data.keys():
                    if not target_unit.startswith("offset_"):
                        units.add(target_unit)
        
        return list(units)

    def _normalize_unit_with_aliases(self, unit_str: str) -> str:
        """Normalize unit string using aliases database."""
        if not unit_str or not self.aliases_database:
            return unit_str
        
        # Get superscript and operator mappings from aliases database
        superscript_mappings = self.aliases_database.get("special_characters", {}).get("mappings", {})
        # For now, we'll use the same special_characters for simple operator replacements
        # This avoids the list problem and focuses on simple character substitutions
        operator_mappings = self.aliases_database.get("special_characters", {}).get("mappings", {})
        
        normalized = _normalize_unit_str(unit_str, superscript_mappings, operator_mappings)
        
        # Apply category aliases
        categories = self.aliases_database.get("categories", {})
        for category_name, category_data in categories.items():
            aliases = category_data.get("aliases", {})
            if normalized.lower() in [alias.lower() for alias in aliases.keys()]:
                for alias, standard in aliases.items():
                    if alias.lower() == normalized.lower():
                        return standard
                        
        return normalized

    def _parse_composite_unit(self, unit_str: str) -> Optional[Dict[str, Any]]:
        """Parse composite units using patterns from configuration."""
        if not unit_str or not self.units_database:
            return None
        
        # Get parsing rules from config
        compound_units_config = self.units_database.get("compound_units", {})
        parsing_rules = compound_units_config.get("parsing_rules", {})
        
        if not parsing_rules:
            return None
        
        # Normalize unit string first
        superscript_mappings = self.aliases_database.get("special_characters", {}).get("mappings", {})
        # Use special_characters for simple replacements to avoid list problems
        operator_mappings = self.aliases_database.get("special_characters", {}).get("mappings", {})
        unit_str = _normalize_unit_str(unit_str, superscript_mappings, operator_mappings)
        
        # Check division patterns
        division_operators = parsing_rules.get("division", [])
        for div_op in division_operators:
            if div_op in unit_str:
                parts = unit_str.split(div_op, 1)
                if len(parts) == 2:
                    return {
                        'type': 'composite',
                        'numerator': parts[0].strip(),
                        'denominator': parts[1].strip(),
                        'operation': 'division'
                    }
        
        # Check multiplication patterns
        multiplication_operators = parsing_rules.get("multiplication", [])
        for mult_op in multiplication_operators:
            if mult_op in unit_str:
                parts = unit_str.split(mult_op, 1)
                if len(parts) == 2:
                    return {
                        'type': 'composite',
                        'part1': parts[0].strip(),
                        'part2': parts[1].strip(),
                        'operation': 'multiplication'
                    }
        
        return None

    def get_direct_conversion_factor(self, current_unit: str, target_unit: str) -> Optional[float]:
        """Get direct conversion factor from configuration database."""
        if not current_unit or not target_unit or not self.units_database:
            return None
        
        # Get superscript and operator mappings
        superscript_mappings = self.aliases_database.get("special_characters", {}).get("mappings", {})
        # Use special_characters for simple replacements to avoid list problems
        operator_mappings = self.aliases_database.get("special_characters", {}).get("mappings", {})
        
        current_unit = _normalize_unit_str(current_unit, superscript_mappings, operator_mappings)
        target_unit = _normalize_unit_str(target_unit, superscript_mappings, operator_mappings)
        
        if current_unit == target_unit:
            return 1.0
        
        # Handle power units from config
        exponentiation_patterns = self.units_database.get("compound_units", {}).get("parsing_rules", {}).get("exponentiation", [])
        for exp_pattern in exponentiation_patterns:
            current_match = re.search(f'(.+){re.escape(exp_pattern)}(\\d+)', current_unit)
            target_match = re.search(f'(.+){re.escape(exp_pattern)}(\\d+)', target_unit)
            
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
        current_prefix, current_base = self._extract_prefix_and_base(current_unit)
        target_prefix, target_base = self._extract_prefix_and_base(target_unit)

        if current_base == target_base:
            current_factor = self._get_prefix_factor(current_prefix) or 1.0
            target_factor = self._get_prefix_factor(target_prefix) or 1.0
            
            if target_factor == 0:
                return None
            return current_factor / target_factor

        # Search in conversion database
        categories = self.units_database.get("categories", {})
        for category_data in categories.values():
            if not isinstance(category_data, dict) or "conversions" not in category_data:
                continue
            
            conversions = category_data["conversions"]
            
            # Check for flat format - both units to base unit
            if current_unit in conversions and target_unit in conversions:
                current_factor = conversions[current_unit]
                target_factor = conversions[target_unit]
                
                if isinstance(current_factor, (int, float)) and isinstance(target_factor, (int, float)):
                    if target_factor == 0:
                        return None
                    return current_factor / target_factor
                    
            # Handle prefix units with base unit conversion
            if current_base and target_base and current_base in conversions and target_base in conversions:
                current_base_factor = conversions[current_base]
                target_base_factor = conversions[target_base]
                
                if isinstance(current_base_factor, (int, float)) and isinstance(target_base_factor, (int, float)):
                    current_prefix_factor = self._get_prefix_factor(current_prefix) or 1.0
                    target_prefix_factor = self._get_prefix_factor(target_prefix) or 1.0
                    
                    if target_base_factor == 0 or target_prefix_factor == 0:
                        return None
                        
                    base_conversion = current_base_factor / target_base_factor
                    prefix_conversion = current_prefix_factor / target_prefix_factor
                    return base_conversion * prefix_conversion

        return None

    def _convert_composite_unit(self, value: float, from_unit: str, to_unit: str) -> Optional[float]:
        """Convert composite units using configuration-defined parsing rules."""
        if not from_unit or not to_unit:
            return None
            
        from_components = self._parse_composite_unit(from_unit)
        to_components = self._parse_composite_unit(to_unit)
        
        if not from_components or not to_components:
            return None
        
        if from_components['operation'] != to_components['operation']:
            return None
        
        if from_components['operation'] == 'division':
            num_result = self.universal_unit_converter(1.0, from_components['numerator'], to_components['numerator'])
            den_result = self.universal_unit_converter(1.0, from_components['denominator'], to_components['denominator'])
            
            if num_result is None or den_result is None:
                return None
            
            return value * (num_result / den_result)
            
        elif from_components['operation'] == 'multiplication':
            part1_result = self.universal_unit_converter(1.0, from_components['part1'], to_components['part1'])
            part2_result = self.universal_unit_converter(1.0, from_components['part2'], to_components['part2'])
            
            if part1_result is None or part2_result is None:
                return None
            
            return value * (part1_result * part2_result)
        
        return None

    def universal_unit_converter(self, value: float, current_unit: str, target_unit: str) -> Optional[float]:
        """Universal unit converter using configuration databases."""
        if not current_unit or not target_unit:
            return None
            
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
            
            if current_unit_norm in conversions and isinstance(conversions[current_unit_norm], dict):
                if target_unit_norm in conversions[current_unit_norm]:
                    factor = conversions[current_unit_norm][target_unit_norm]
                    result = value * factor
                    return _format_to_significant_figures(result, 5, self.conversion_config)
            
            if target_unit_norm in conversions and isinstance(conversions[target_unit_norm], dict):
                if current_unit_norm in conversions[target_unit_norm]:
                    factor = 1.0 / conversions[target_unit_norm][current_unit_norm]
                    result = value * factor
                    return _format_to_significant_figures(result, 5, self.conversion_config)
        
        # Try composite unit conversion
        composite_result = self._convert_composite_unit(value, current_unit_norm, target_unit_norm)
        if composite_result is not None:
            return _format_to_significant_figures(composite_result, 5, self.conversion_config)
        
        # Try direct conversion factor
        direct_factor = self.get_direct_conversion_factor(current_unit, target_unit)
        if direct_factor is not None:
            result = value * direct_factor
            return _format_to_significant_figures(result, 5, self.conversion_config)
                
        return None

    def add_unit_conversion(self, category: str, from_unit: str, to_unit: str, factor: float, bidirectional: bool = True) -> bool:
        """Add unit conversion to database if category exists."""
        if not self.units_database or "categories" not in self.units_database:
            return False
            
        if category not in self.units_database["categories"]:
            return False
            
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
            from ePy_docs.project.setup import DirectoryConfig, get_current_project_config
            
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
            units_pkg_dir = os.path.dirname(__file__)
            potential_paths.append(os.path.join(units_pkg_dir, 'conversion.json'))
            
            # Find the first existing path
            for path in potential_paths:
                if os.path.exists(path):
                    conversion_path = path
                    break
            
            if conversion_path:
                from ePy_docs.files.reader import ReadFiles
                reader = ReadFiles(file_path=conversion_path)
                conversion_config = reader.load_json()
                # Conversion data loaded silently
            else:
                raise FileNotFoundError(f"Conversion file not found: {conversion_path}")
            
            # Use conversion config for units database if available, otherwise use units config
            units_database = conversion_config if conversion_config else units_config
            
            # Get units package directory for fallback paths
            units_pkg_dir = os.path.dirname(__file__)
            
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
            
            # Try to load format configuration
            format_file_paths = [
                os.path.join(base_config_path, 'units', 'format.json'),
                os.path.join(base_config_path, 'format.json'),
                os.path.join(units_pkg_dir, 'format.json')  # Always check units package directory as fallback
            ]
            
            format_file_path = None
            for path in format_file_paths:
                if os.path.exists(path):
                    format_file_path = path
                    break
            
            # Load prefix, aliases, and format data
            prefix_data = {}
            aliases_data = {}
            format_data = {}
            
            if prefix_file_path and os.path.exists(prefix_file_path):
                from ePy_docs.files.reader import ReadFiles
                reader = ReadFiles(file_path=prefix_file_path)
                prefix_data = reader.load_json() or {}
                
            if aliases_file_path and os.path.exists(aliases_file_path):
                from ePy_docs.files.reader import ReadFiles
                reader = ReadFiles(file_path=aliases_file_path)
                aliases_data = reader.load_json() or {}
                
            if format_file_path and os.path.exists(format_file_path):
                from ePy_docs.files.reader import ReadFiles
                reader = ReadFiles(file_path=format_file_path)
                format_data = reader.load_json() or {}
              # Create instance with loaded data
            return cls(
                units_database=units_database,
                prefix_database=prefix_data,
                aliases_database=aliases_data,
                format_mappings=format_data
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
        from ePy_docs.project.setup import DirectoryConfig
        dir_config = DirectoryConfig.minimal()
        return dir_config.load_config_file('units')
    except Exception as e:
        print(f"Warning: Could not load units config: {e}")
        return {}

def get_available_unit_categories() -> List[str]:
    """Get list of available unit categories from aliases.json."""
    try:
        # Initialize DirectoryConfig without automatic template sync
        from ePy_docs.project.setup import DirectoryConfig
        dir_config = DirectoryConfig.minimal()
        aliases_data = ReadFiles.load_file_data(dir_config, 'aliases.json')
        
        if aliases_data and "categories" in aliases_data:
            return list(aliases_data["categories"].keys())
        
        return []
    except Exception:
        return []

def get_aliases_for_category(aliases_path: str, category: str) -> Dict[str, str]:
    """Get aliases for a specific category from aliases file."""
    if not os.path.exists(aliases_path):
        return {}
        
    try:
        with open(aliases_path, 'r', encoding='utf-8') as f:
            aliases_data = json.load(f)
        
        categories = aliases_data.get("categories", {})
        category_data = categories.get(category, {})
        return category_data.get("aliases", {})
        
    except Exception:
        return {}

def get_unit_from_config(units_config: Dict[str, Any], category: str, key: str) -> Optional[str]:
    """Get unit from configuration by category and key."""
    if not units_config:
        return None
        
    try:
        category_data = units_config.get("categories", {}).get(category, {})
        if not isinstance(category_data, dict):
            return None
            
        unit_data = category_data.get(key, None)
          
        if isinstance(unit_data, str):
            return unit_data
        elif isinstance(unit_data, list) and unit_data:
            return unit_data[0]
        elif isinstance(unit_data, dict):
            return unit_data.get("unit", None)
            
        return None
        
    except (KeyError, TypeError, AttributeError):
        return None

def create_compound_unit(base_unit: str, power: int, format_config: Dict[str, Any] = None) -> str:
    """Create compound units using configuration-defined formatting."""
    if not base_unit:
        return ""
        
    if power == 1:
        return base_unit
    
    if not format_config:
        return f"{base_unit}^{power}"
    
    # Get power formatting from config
    power_formats = format_config.get("power_formats", {})
    power_str = str(power)
    
    if power_str in power_formats:
        return f"{base_unit}{power_formats[power_str]}"
    
    # Get default pattern from config
    default_pattern = format_config.get("default_power_pattern", "{base}^{power}")
    return default_pattern.format(base=base_unit, power=power)


def create_composite_unit(numerator_unit: str, denominator_unit: str, 
                         numerator_power: int = 1, denominator_power: int = 1,
                         format_config: Dict[str, Any] = None) -> str:
    """Create composite units using configuration."""
    if not numerator_unit or not denominator_unit:
        return ""
    
    num_unit = create_compound_unit(numerator_unit, numerator_power, format_config)
    den_unit = create_compound_unit(denominator_unit, denominator_power, format_config)
    
    if not format_config:
        return f"{num_unit}/{den_unit}"
    
    # Get division pattern from config  
    division_pattern = format_config.get("division_pattern", "{numerator}/{denominator}")
    return division_pattern.format(numerator=num_unit, denominator=den_unit)


def create_moment_unit(force_unit: str, length_unit: str, format_config: Dict[str, Any] = None) -> str:
    """Create moment units using configuration-defined multiplication operator."""
    if not force_unit or not length_unit:
        return ""
    
    if not format_config:
        return f"{force_unit}-{length_unit}"
    
    # Get multiplication pattern from config
    multiplication_pattern = format_config.get("moment_pattern", "{force}-{length}")
    return multiplication_pattern.format(force=force_unit, length=length_unit)


def get_dimensional_units(base_unit: str, format_config: Dict[str, Any] = None) -> Dict[str, str]:
    """Get dimensional units using configuration mappings."""
    if not base_unit:
        return {}
    
    if not format_config:
        # Basic fallback
        return {
            'area': create_compound_unit(base_unit, 2),
            'volume': create_compound_unit(base_unit, 3),
            'length': base_unit
        }
    
    # Get dimensional mappings from config
    dimensional_mappings = format_config.get("dimensional_mappings", {})
    if not dimensional_mappings:
        return {}
    
    result = {}
    for property_name, power_info in dimensional_mappings.items():
        if isinstance(power_info, int):
            result[property_name] = create_compound_unit(base_unit, power_info, format_config)
        elif isinstance(power_info, dict):
            power = power_info.get("power", 1)
            result[property_name] = create_compound_unit(base_unit, power, format_config)
    
    return result


def get_structural_units(force_unit: str, length_unit: str, format_config: Dict[str, Any] = None) -> Dict[str, str]:
    """Get structural units using configuration."""
    if not force_unit or not length_unit:
        return {}
    
    base_dimensional = get_dimensional_units(length_unit, format_config)
    
    if not format_config:
        # Basic fallback
        structural_units = base_dimensional.copy()
        structural_units.update({
            'force': force_unit,
            'moment': create_moment_unit(force_unit, length_unit),
            'pressure': create_composite_unit(force_unit, length_unit, 1, 2)
        })
        return structural_units
    
    # Get structural mappings from config
    structural_mappings = format_config.get("structural_mappings", {})
    if not structural_mappings:
        return base_dimensional
    
    structural_units = base_dimensional.copy()
    
    for unit_type, unit_config in structural_mappings.items():
        if unit_type == "force_units":
            for prop_name in unit_config:
                structural_units[prop_name] = force_unit
        elif unit_type == "moment_units":
            for prop_name in unit_config:
                structural_units[prop_name] = create_moment_unit(force_unit, length_unit, format_config)
        elif unit_type == "pressure_units":
            for prop_name in unit_config:
                structural_units[prop_name] = create_composite_unit(force_unit, length_unit, 1, 2, format_config)
    
    return structural_units


def get_foundation_units(force_unit: str, length_unit: str, format_config: Dict[str, Any] = None) -> Dict[str, str]:
    """Get foundation units using configuration."""
    if not force_unit or not length_unit:
        return {}
    
    structural_units = get_structural_units(force_unit, length_unit, format_config)
    
    if not format_config:
        return structural_units
    
    # Get foundation-specific mappings from config
    foundation_mappings = format_config.get("foundation_mappings", {})
    if not foundation_mappings:
        return structural_units
    
    foundation_units = structural_units.copy()
    
    for unit_type, unit_config in foundation_mappings.items():
        if unit_type == "geometry_units":
            for prop_name in unit_config:
                foundation_units[prop_name] = length_unit
        elif unit_type == "pressure_units":
            for prop_name in unit_config:
                foundation_units[prop_name] = create_composite_unit(force_unit, length_unit, 1, 2, format_config)
    
    return foundation_units
