"""Enhanced unit converter module that handles complex engineering units."""

import json
import os
import re
from typing import Dict, Union, Any, Optional, List, Tuple
import pandas as pd
from pydantic import BaseModel, Field
from ePy_docs.core.setup import load_setup_config, get_output_directories, get_absolute_output_directories
from ePy_docs.files.reader import ReadFiles
from ePy_docs.components.page import ConfigurationError


def initialize_units_system(units_config: Dict[str, Any], sync_files: bool = True):
    """Initialize complete units system with all categories and conversion capabilities.
    
    Args:
        units_config: Configuration dictionary from units.json
        sync_files: Whether to sync configuration files
        
    Returns:
        Dict containing all units data and converter instance
        
    Raises:
        RuntimeError: If initialization fails
    """
    from ePy_docs.core.setup import _load_cached_config
    
    try:
        # Extract all units dynamically
        def extract_all_units(config):
            """Extract all units from configuration dynamically."""
            units_dict = {}
            categories = config.get('categories', {})
            
            for category_name, category_data in categories.items():
                if not isinstance(category_data, dict):
                    continue
                    
                category_units = {}
                for unit_type, unit_info in category_data.items():
                    if unit_type == 'description':  # Skip description fields
                        continue
                        
                    unit_value = get_unit_from_config(config, category_name, unit_type)
                    if unit_value:
                        category_units[unit_type] = unit_value
                
                if category_units:  # Only add if category has units
                    units_dict[category_name] = category_units
            
            return units_dict
        
        # Get all available units dynamically
        all_units = extract_all_units(units_config)
        
        # Pre-sync all units configuration files if needed
        if sync_files:
            try:
                _load_cached_config('units/conversion', sync_files=True)
                _load_cached_config('units/aliases', sync_files=True) 
                _load_cached_config('units/format', sync_files=True)
                _load_cached_config('units/prefix', sync_files=True)
            except Exception as sync_error:
                print(f"Warning: Could not sync some units config files: {sync_error}")
        
        # Create unit converter
        converter = UnitConverter.create_default()
        
        # Extract backward compatibility units
        compatibility_units = {}
        if 'structure_dimensions' in all_units:
            compatibility_units['length_unit'] = all_units['structure_dimensions'].get('length')
            compatibility_units['area_unit'] = all_units['structure_dimensions'].get('structure_area')
        
        if 'section_dimensions' in all_units:
            compatibility_units['volume_unit'] = all_units['section_dimensions'].get('length3')
        
        if 'forces' in all_units:
            compatibility_units['force_unit'] = all_units['forces'].get('force')
            compatibility_units['moment_unit'] = all_units['forces'].get('moment')
        
        return {
            'all_units': all_units,
            'compatibility_units': compatibility_units,
            'converter': converter,
            'categories': list(all_units.keys()),
            'total_units': sum(len(units) for units in all_units.values())
        }
        
    except Exception as e:
        raise RuntimeError(f"Units system initialization failed: {e}")

def _normalize_unit_str(unit_str: str, superscript_mappings: Dict[str, str] = None, 
                       operator_mappings: Dict[str, str] = None) -> str:
    """Normalize unit representation using configuration mappings."""
    if not unit_str:
        return unit_str
        
    result = unit_str
    
    # Apply superscript mappings from config if available
    if superscript_mappings:
        for sup, repl in superscript_mappings.items():
            if sup in result:
                result = result.replace(sup, repl)
    
    # Apply operator mappings from config if available  
    if operator_mappings:
        for original, replacement in operator_mappings.items():
            result = result.replace(original, replacement)
    
    # Always apply basic regex patterns for common normalizations
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
        format_type: Target format type
        format_mappings: Configuration mappings for different formats
        
    Returns:
        Formatted unit string according to format type
    """
    if not unit_str or not format_mappings:
        return unit_str
        
    # Get format-specific mappings from config
    format_config = format_mappings.get(format_type, {})
    if not format_config:
        return unit_str
    
    result = unit_str
    
    # Apply superscript conversions FIRST (before multiplication operators)
    # This ensures that ^-1 is processed before the hyphen is replaced with middle dot
    superscript_mappings = format_config.get('superscripts', {})
    for caret, formatted_sup in superscript_mappings.items():
        result = result.replace(caret, formatted_sup)
    
    # Apply multiplication operators from config for moment units
    # This comes AFTER superscripts to avoid interfering with ^-1, ^-2, etc.
    multiplication_operators = format_mappings.get('multiplication_operators', {})
    if multiplication_operators and format_type in multiplication_operators:
        operator = multiplication_operators[format_type]
        result = result.replace('-', operator)
    
    # Apply degree conversions from config
    degree_mappings = format_config.get('degrees', {})
    for original, replacement in degree_mappings.items():
        result = result.replace(original, replacement)
    
    # Apply regex patterns from config
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

# def _format_to_significant_figures(value: float, sig_figs: int, precision_config: Dict[str, Any] = None) -> float:
#     """Format a number to specified significant figures using configuration."""
#     import math
    
#     if not precision_config:
#         return value
    
#     if value == 0:
#         return 0.0
    
#     # Use configuration values instead of hardcoded ones
#     default_precision = precision_config.get('default_precision', sig_figs)
#     rounding_method = precision_config.get('rounding_method', 'round_half_up')
    
#     magnitude = math.floor(math.log10(abs(value)))
#     factor = 10 ** (default_precision - 1 - magnitude)
    
#     if rounding_method == 'round_half_up':
#         rounded = round(value * factor) / factor
#     else:
#         rounded = round(value * factor) / factor
    
#     return float(rounded)

def _apply_unit_precision(value: float, unit: str, converter: 'UnitConverter') -> float:
    """Apply precision rounding with strict 5 significant figures maximum limit.
    
    Args:
        value: Numerical value to round
        unit: Unit string to determine precision
        converter: UnitConverter instance with precision configuration
        
    Returns:
        Value rounded to maximum 5 significant figures, further limited by unit precision
    """
    import math
    
    if value == 0:
        return 0.0
    
    # STEP 1: Force 5 significant figures maximum
    # Calculate the order of magnitude
    magnitude = math.floor(math.log10(abs(value)))
    
    # Calculate factor to round to 5 significant figures
    # We want to keep 5 digits total, so we round to position (magnitude - 4)
    round_to_position = magnitude - 4
    factor = 10 ** (-round_to_position)
    
    # Round to 5 significant figures
    value_5_sig = round(value * factor) / factor
    
    # STEP 2: Apply unit-specific decimal precision as additional constraint
    decimal_precision = converter._get_unit_precision(unit)
    
    # Final rounding with decimal precision (this can further reduce precision)
    final_result = round(value_5_sig, decimal_precision)
    
    return final_result

class UnitConverter(BaseModel):
    """Enhanced unit converter with configuration-driven behavior."""
    units_database: Dict[str, Any] = Field(default_factory=dict)
    prefix_database: Dict[str, Any] = Field(default_factory=dict)
    aliases_database: Dict[str, Any] = Field(default_factory=dict)
    format_mappings: Dict[str, Any] = Field(default_factory=dict)
    conversion_config: Dict[str, Any] = Field(default_factory=dict)
    precision_config: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)

    @classmethod
    def from_files(cls, conversion_file: str, prefix_file: str, aliases_file: str, 
                   format_file: str = None, units_file: str = None) -> 'UnitConverter':
        """Create converter instance from specific configuration files.
        
        Args:
            conversion_file: Path to conversion.json
            prefix_file: Path to prefix.json  
            aliases_file: Path to aliases.json
            format_file: Optional path to format configuration
            units_file: Optional path to units.json for precision configuration
            
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
        
        # Load data from files using file management API
        try:
            from ePy_docs.api.file_management import read_json
            units_database = read_json(conversion_file)
            prefix_database = read_json(prefix_file)
            aliases_database = read_json(aliases_file)
        except Exception as e:
            raise ValueError(f"Failed to load unit conversion data: {e}")
        
        format_mappings = {}
        if format_file and os.path.exists(format_file):
            try:
                format_mappings = read_json(format_file)
            except Exception as e:
                print(f"Warning: Could not load format mappings: {e}")
        
        # Load precision configuration from units.json
        precision_config = {}
        if units_file and os.path.exists(units_file):
            try:
                units_data = read_json(units_file)
                categories = units_data.get('categories', {})
                # Build precision mapping from [unit, precision] format
                for category_name, category_data in categories.items():
                    if isinstance(category_data, dict):
                        for unit_type, unit_config in category_data.items():
                            if unit_type != 'description' and isinstance(unit_config, list) and len(unit_config) == 2:
                                unit_str, precision = unit_config
                                precision_config[unit_str] = precision
            except Exception as e:
                print(f"Warning: Could not load precision configuration: {e}")
        
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
            conversion_config=units_database.get('conversion_accuracy', {}),
            precision_config=precision_config
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

    def _get_unit_precision(self, unit: str) -> int:
        """Get the precision (decimal places) for a given unit from configuration.
        
        Args:
            unit: Unit string to get precision for
            
        Returns:
            Number of decimal places for the unit (default: 3)
        """
        if not unit or not self.precision_config:
            return 3  # Default precision
        
        # Normalize unit for lookup
        normalized_unit = self._normalize_unit_with_aliases(unit)
        
        # Direct lookup
        if normalized_unit in self.precision_config:
            return self.precision_config[normalized_unit]
        
        # Check original unit string
        if unit in self.precision_config:
            return self.precision_config[unit]
        
        # For complex units, try to find a matching pattern
        # This handles cases like "kgf/cm^2" matching "kgf/cm²" in config
        for config_unit, precision in self.precision_config.items():
            if format_unit_display(config_unit, "unicode", self.format_mappings) == normalized_unit:
                return precision
        
        return 3  # Default precision


    def _normalize_unit_with_aliases(self, unit_str: str) -> str:
        """Normalize unit string using aliases database."""
        if not unit_str:
            return unit_str
        
        # Normalize Unicode characters for CONSISTENCY
        # Convert both DOT OPERATOR (U+22C5) and MIDDLE DOT (U+00B7) to MIDDLE DOT for consistency
        # This ensures all moment units use the same character throughout the system
        unit_str = unit_str.replace('⋅', '·')  # Convert ⋅ to ·
        
        if not self.aliases_database:
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

        # Search in conversion database - handle both old format with "categories" and new direct format
        categories_to_search = {}
        if "categories" in self.units_database:
            categories_to_search = self.units_database["categories"]
        else:
            # Direct format: each key (like "pressure", "stress") is a category
            categories_to_search = {k: v for k, v in self.units_database.items() 
                                  if isinstance(v, dict) and "conversions" in v}
        
        for category_data in categories_to_search.values():
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
            return _apply_unit_precision(value, target_unit, self)
            
        current_unit_norm = self._normalize_unit_with_aliases(current_unit)
        target_unit_norm = self._normalize_unit_with_aliases(target_unit)
        
        if current_unit_norm == target_unit_norm:
            return _apply_unit_precision(value, target_unit, self)

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
                    return _apply_unit_precision(result, target_unit, self)
            
            if target_unit_norm in conversions and isinstance(conversions[target_unit_norm], dict):
                if current_unit_norm in conversions[target_unit_norm]:
                    factor = 1.0 / conversions[target_unit_norm][current_unit_norm]
                    result = value * factor
                    return _apply_unit_precision(result, target_unit, self)
                    
            # Try conversion through base unit (for simple factor-based conversions)
            if (current_unit_norm in conversions and isinstance(conversions[current_unit_norm], (int, float)) and
                target_unit_norm in conversions and isinstance(conversions[target_unit_norm], (int, float))):
                from_factor = conversions[current_unit_norm]
                to_factor = conversions[target_unit_norm]
                # Convert: value * from_factor / to_factor
                conversion_factor = from_factor / to_factor
                result = value * conversion_factor
                return _apply_unit_precision(result, target_unit, self)
        
        # Try composite unit conversion
        composite_result = self._convert_composite_unit(value, current_unit_norm, target_unit_norm)
        if composite_result is not None:
            return _apply_unit_precision(composite_result, target_unit, self)
        
        # Try direct conversion factor
        direct_factor = self.get_direct_conversion_factor(current_unit, target_unit)
        if direct_factor is not None:
            result = value * direct_factor
            return _apply_unit_precision(result, target_unit, self)
                
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
        """Save the units database to a JSON file using file management API."""
        try:
            from ePy_docs.api.file_management import write_json
            write_json(self.units_database, filepath, indent=2)
        except Exception:
            # Fallback to direct file writing
            import json
            with open(filepath, "w") as file:
                json.dump(self.units_database, file, indent=2)

    @classmethod
    def create_default(cls, base_dir: Optional[str] = None) -> 'UnitConverter':
        """Create a UnitConverter instance with configuration from setup.json.
        
        Args:
            base_dir: Base directory path (ignored, uses setup.json configuration)
        
        Returns:
            UnitConverter instance with loaded configuration.
            
        Raises:
            ConfigurationError: If required configuration files are missing.
            
        Usage:
            converter = UnitConverter.create_default()
        """
        from ePy_docs.files.data import _load_cached_json
        
        # Load setup configuration with absolute paths
        setup_config = load_setup_config()
        output_dirs = get_absolute_output_directories()
        
        # Get configuration path from setup.json  
        config_dir = output_dirs['configuration']
        units_config_dir = os.path.join(config_dir, 'units')
        
        # Load units configuration files
        conversion_path = os.path.join(units_config_dir, 'conversion.json')
        if not os.path.exists(conversion_path):
            raise ConfigurationError(f"Conversion configuration not found: {conversion_path}")
        
        conversion_config = _load_cached_json(conversion_path)
        if not conversion_config:
            raise ConfigurationError(f"Failed to load conversion configuration from: {conversion_path}")
        
        # Load auxiliary configuration files
        aliases_path = os.path.join(units_config_dir, 'aliases.json')
        prefix_path = os.path.join(units_config_dir, 'prefix.json')
        format_path = os.path.join(units_config_dir, 'format.json')
        units_json_path = os.path.join(units_config_dir, 'units.json')
        
        # Load data
        aliases_data = _load_cached_json(aliases_path) if os.path.exists(aliases_path) else {}
        prefix_data = _load_cached_json(prefix_path) if os.path.exists(prefix_path) else {}
        format_data = _load_cached_json(format_path) if os.path.exists(format_path) else {}
        
        precision_config = {}
        if os.path.exists(units_json_path):
            units_json_data = _load_cached_json(units_json_path) or {}
            
            # Build precision configuration from units.json categories
            categories = units_json_data.get('categories', {})
            for category_name, category_data in categories.items():
                if isinstance(category_data, dict):
                    for unit_type, unit_config in category_data.items():
                        if unit_type != 'description' and isinstance(unit_config, list) and len(unit_config) == 2:
                            unit_str, precision = unit_config
                            precision_config[unit_str] = precision
        
        return cls(
            units_database=conversion_config,
            prefix_database=prefix_data,
            aliases_database=aliases_data,
            format_mappings=format_data,
            precision_config=precision_config
        )
    

# Simplified standalone functions

# def _get_default_units_mapping_from_aliases() -> Dict[str, Tuple[str, str]]:
#     """Get default units mapping from aliases.json file."""
#     try:
#         # Load configuration using setup.json
#         aliases_data = ReadFiles.load_file_data(dir_config, 'aliases.json')
        
#         if not aliases_data:
#             print(f"Warning: aliases.json not found or empty")
#             return {}
        
#         unit_aliases = aliases_data.get("unit_aliases", {})
#         mapping = {}
        
#         # Build mapping based on available categories
#         category_mappings = {
#             "force": ["FX", "FY", "FZ"],
#             "moment": ["MX", "MY", "MZ"],
#             "length": ["X", "Y", "Z", "DX", "DY", "DZ"],
#             "stress": ["SIG_X", "SIG_Y", "SIG_Z", "TAU_XY", "TAU_XZ", "TAU_YZ"],
#             "area": ["AREA"],
#             "volume": ["VOLUME"],
#             "temperature": ["TEMP", "TEMPERATURE"],
#             "angle": ["ANGLE", "ROTATION"]
#         }
        
#         for category, columns in category_mappings.items():
#             if category in unit_aliases:
#                 for col in columns:
#                     mapping[col] = (category, "target_units")
        
#         return mapping
        
#     except Exception as e:
#         print(f"Warning: Could not get default mappings from aliases.json: {e}")
#         return {}

def load_units_config() -> dict:
    """Load units configuration using setup.json paths."""
    setup_config = load_setup_config()
    output_dirs = get_absolute_output_directories()
    config_dir = output_dirs['configuration']
    units_config_path = os.path.join(config_dir, 'units', 'units.json')
    
    from ePy_docs.files.data import _load_cached_json
    return _load_cached_json(units_config_path)

def get_available_unit_categories() -> List[str]:
    """Get list of available unit categories from aliases.json."""
    setup_config = load_setup_config()
    output_dirs = get_absolute_output_directories()
    config_dir = output_dirs['configuration']
    aliases_path = os.path.join(config_dir, 'units', 'aliases.json')
    
    from ePy_docs.files.data import _load_cached_json
    aliases_data = _load_cached_json(aliases_path)
    
    return list(aliases_data["categories"].keys())

def get_aliases_for_category(aliases_path: str, category: str) -> Dict[str, str]:
    """Get aliases for a specific category from aliases file using file management API."""
    if not os.path.exists(aliases_path):
        return {}
        
    try:
        from ePy_docs.api.file_management import read_json
        aliases_data = read_json(aliases_path)
        
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
        raise ConfigurationError("Format configuration is required for dimensional units")
    
    # Get dimensional mappings from config
    dimensional_mappings = format_config.get("dimensional_mappings", {})
    if not dimensional_mappings:
        raise ConfigurationError("Dimensional mappings not found in format configuration")
    
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
        raise ConfigurationError("Format configuration is required for structural units")
    
    # Get structural mappings from config
    structural_mappings = format_config.get("structural_mappings", {})
    if not structural_mappings:
        raise ConfigurationError("Structural mappings not found in format configuration")
    
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


def get_decimal_config_from_format_json(data_type: str = "conversion_factors") -> dict:
    """Get decimal formatting configuration from format.json file.
    
    Args:
        data_type: Type of data to format. Options: 'conversion_factors', 'general_numeric', 
                  'engineering_values', 'percentage_values'
    
    Returns:
        Dictionary with decimal_places and format_string configuration
    """
    import os
    
    try:
        # Get the directory of this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        format_file_path = os.path.join(current_dir, 'format.json')
        
        try:
            from ePy_docs.api.file_management import read_json
            format_config = read_json(format_file_path)
        except Exception:
            # Fallback to direct file reading
            import json
            with open(format_file_path, 'r', encoding='utf-8') as f:
                format_config = json.load(f)
        
        decimal_formatting = format_config.get('decimal_formatting', {})
        
        if data_type == "engineering_values":
            return decimal_formatting.get('engineering_values', {})
        
        config = decimal_formatting.get(data_type, {})
        if not config:
            # Fallback to conversion_factors if specific type not found
            config = decimal_formatting.get('conversion_factors', {
                'decimal_places': 3,
                'format_string': '.3f'
            })
        
        return config
        
    except Exception as e:
        raise ConfigurationError(f"Failed to load decimal configuration: {e}")


def get_decimal_places_for_conversion_factors() -> int:
    """Get decimal places specifically for conversion factors from configuration.
    
    Returns:
        Number of decimal places to use for conversion factors
    """
    config = get_decimal_config_from_format_json("conversion_factors")
    return config.get('decimal_places', 3)


def get_format_string_for_conversion_factors() -> str:
    """Get format string specifically for conversion factors from configuration.
    
    Automatically selects the format that provides maximum precision.
    
    Returns:
        Format string for conversion factors (typically '.6g' for best precision)
    """
    return get_format_for_conversion_factors()


def get_engineering_decimal_config(value_type: str = "forces") -> dict:
    """Get decimal configuration for engineering values from format.json.
    
    Args:
        value_type: Type of engineering value ('forces', 'moments', 'stresses', 'dimensions')
    
    Returns:
        Dictionary with decimal_places and format_string for the specified value type
    """
    engineering_config = get_decimal_config_from_format_json("engineering_values")
    
    # Get specific configuration for the value type
    specific_config = engineering_config.get(value_type, {})
    
    if not specific_config:
        raise ConfigurationError(f"Engineering configuration for '{value_type}' not found")
    
    return specific_config


# def get_significant_figures_config(data_type: str = "conversion_factors") -> dict:
#     """Get significant figures configuration from format.json.
    
#     Args:
#         data_type: Type of data ('conversion_factors', 'engineering_values')
    
#     Returns:
#         Dictionary with significant_figures and format_string for the specified data type
#     """
#     import os
#     import json
    
#     try:
#         # Get the directory of this file
#         current_dir = os.path.dirname(os.path.abspath(__file__))
#         format_file_path = os.path.join(current_dir, 'format.json')
        
#         with open(format_file_path, 'r', encoding='utf-8') as f:
#             format_config = json.load(f)
        
#         decimal_formatting = format_config.get('decimal_formatting', {})
#         significant_config = decimal_formatting.get('significant_figures', {})
        
#         # Get specific configuration for the data type
#         specific_config = significant_config.get(data_type, {})
        
#         # Fallback to default values if not found
#         if not specific_config:
#             return {
#                 'significant_figures': 6,
#                 'format_string': '.6g'
#             }
        
#         return specific_config
#     except Exception as e:
#         # Fallback configuration if file reading fails
#         return {
#             'significant_figures': 6,
#             'format_string': '.6g',
#             'description': f'Fallback config due to error: {str(e)}'
#         }


# def get_significant_figures_for_conversion_factors() -> int:
#     """Get number of significant figures for conversion factors from JSON config.
    
#     Returns:
#         Number of significant figures (default: 6)
#     """
#     config = get_significant_figures_config("conversion_factors")
#     return config.get('significant_figures', 6)


def get_format_for_conversion_factors() -> str:
    """Get automatic format string for conversion factors based on JSON config.
    
    Automatically chooses the format that provides the most decimal precision
    between decimal places (.3f) and significant figures (.6g)
    
    Returns:
        Format string that gives the most precision for the value
    """
    import os
    
    try:
        # Get the directory of this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        format_file_path = os.path.join(current_dir, 'format.json')
        
        try:
            from ePy_docs.api.file_management import read_json
            format_config = read_json(format_file_path)
        except Exception:
            # Fallback to direct file reading
            import json
            with open(format_file_path, 'r', encoding='utf-8') as f:
                format_config = json.load(f)
        
        decimal_formatting = format_config.get('decimal_formatting', {})
        
        # Get both format options
        decimal_config = decimal_formatting.get('conversion_factors', {})
        sig_config = decimal_formatting.get('significant_figures', {}).get('conversion_factors', {})
        
        decimal_format = decimal_config.get('format_string', '.3f')
        sig_format = sig_config.get('format_string', '.6g')
        
        # For conversion factors, significant figures (.6g) typically gives better precision
        # than fixed decimals (.3f), so prefer .6g
        return sig_format
        
    except Exception as e:
        # Fallback to significant figures for best precision
        return '.6g'


def format_conversion_factor(value: float) -> str:
    """Format a conversion factor value with optimal precision from JSON config.
    
    This function automatically applies the best formatting for conversion factors
    based on the JSON configuration, avoiding hardcoded .6f formatting.
    
    Args:
        value: The conversion factor value to format
        
    Returns:
        Formatted string with optimal precision (e.g., "100000" instead of "100000.000000")
        
    Example:
        Instead of: f"{100000.0:.6f}"  # gives "100000.000000"
        Use: format_conversion_factor(100000.0)  # gives "100000"
    """
    format_string = get_format_for_conversion_factors()
    return f"{value:{format_string}}"


def get_conversion_format() -> str:
    """Short alias for get_format_for_conversion_factors().
    
    Returns:
        Format string for conversion factors
    """
    return get_format_for_conversion_factors()
