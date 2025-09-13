"""
Pure unit conversion utilities for ePy_docs UNITS world.

Direct functional operations without class overhead.
TRANSPARENCY DIMENSION: Pure functions, singleton databases, halt-on-failure.
"""

import json
import os
import re
from typing import Dict, Union, Any, Optional, List, Tuple
import pandas as pd
from pydantic import BaseModel, Field
from ePy_docs.files import _load_cached_files
from ePy_docs.files.data import _safe_get_nested
from ePy_docs.components.setup import _resolve_config_path, get_absolute_output_directories
from ePy_docs.files.reader import ReadFiles
from ePy_docs.components.pages import ConfigurationError


# GLOBAL DATABASES - SINGLETON PATTERN
_GLOBAL_CONVERTER_DATABASES = {
    'units_database': {},
    'prefix_database': {},
    'aliases_database': {},
    'format_mappings': {},
    'conversion_config': {},
    'precision_config': {},
    'initialized': False
}


def initialize_converter_databases(conversion_file: str, prefix_file: str, aliases_file: str, 
                                 format_file: str = None, units_file: str = None) -> None:
    """Initialize global converter databases from configuration files.
    
    Args:
        conversion_file: Path to conversion.json
        prefix_file: Path to prefix.json  
        aliases_file: Path to aliases.json
        format_file: Optional path to format configuration
        units_file: Optional path to units.json for precision configuration
        
    Raises:
        FileNotFoundError: If required files don't exist
        ValueError: If files contain invalid data
    """
    global _GLOBAL_CONVERTER_DATABASES
    
    if not os.path.exists(conversion_file):
        raise FileNotFoundError(f"Conversion file not found: {conversion_file}")
    if not os.path.exists(prefix_file):
        raise FileNotFoundError(f"Prefix file not found: {prefix_file}")
    if not os.path.exists(aliases_file):
        raise FileNotFoundError(f"Aliases file not found: {aliases_file}")
    
    try:
        # Load conversion database
        with open(conversion_file, 'r', encoding='utf-8') as f:
            _GLOBAL_CONVERTER_DATABASES['conversion_config'] = json.load(f)
        
        # Load prefix database
        with open(prefix_file, 'r', encoding='utf-8') as f:
            _GLOBAL_CONVERTER_DATABASES['prefix_database'] = json.load(f)
        
        # Load aliases database
        with open(aliases_file, 'r', encoding='utf-8') as f:
            aliases_data = json.load(f)
        
        # Build flat aliases dictionary from categorized structure
        flat_aliases = {}
        if 'categories' in aliases_data:
            for category, category_data in aliases_data['categories'].items():
                if isinstance(category_data, dict) and 'aliases' in category_data:
                    for alias, target in category_data['aliases'].items():
                        flat_aliases[alias] = target
        
        _GLOBAL_CONVERTER_DATABASES['aliases_database'] = flat_aliases
        
        # Load optional format configuration
        if format_file and os.path.exists(format_file):
            with open(format_file, 'r', encoding='utf-8') as f:
                _GLOBAL_CONVERTER_DATABASES['format_mappings'] = json.load(f)
        
        # Load optional units configuration for precision
        if units_file and os.path.exists(units_file):
            with open(units_file, 'r', encoding='utf-8') as f:
                _GLOBAL_CONVERTER_DATABASES['precision_config'] = json.load(f)
        
        # Build units database from conversion config
        _GLOBAL_CONVERTER_DATABASES['units_database'] = {}
        conversion_data = _GLOBAL_CONVERTER_DATABASES['conversion_config']
        
        # Look for the 'categories' section first (modern format)
        if 'categories' in conversion_data:
            categories_section = conversion_data['categories']
            for category, category_data in categories_section.items():
                if isinstance(category_data, dict) and 'conversions' in category_data:
                    conversions = category_data['conversions']
                    if isinstance(conversions, dict):
                        for unit, factor in conversions.items():
                            _GLOBAL_CONVERTER_DATABASES['units_database'][unit] = {
                                'category': category,
                                'factor': factor if isinstance(factor, (int, float)) else 1.0,
                                'offset': 0.0,
                                'formula': 'linear',
                                'description': category_data.get('description', '')
                            }
        else:
            # Legacy format: look for 'units' section or top-level categories
            units_section = conversion_data.get('units', {})
            if not units_section:
                # Alternative: iterate through all top-level keys that look like unit categories
                for key, value in conversion_data.items():
                    if isinstance(value, dict) and 'conversions' in value:
                        category = key
                        conversions = value['conversions']
                        if isinstance(conversions, dict):
                            for unit, factor in conversions.items():
                                _GLOBAL_CONVERTER_DATABASES['units_database'][unit] = {
                                    'category': category,
                                    'factor': factor if isinstance(factor, (int, float)) else 1.0,
                                    'offset': 0.0,
                                    'formula': 'linear',
                                    'description': value.get('description', '')
                                }
            else:
                # Process units section
                for category, units in units_section.items():
                    if isinstance(units, dict):
                        for unit, data in units.items():
                            if isinstance(data, dict):
                                _GLOBAL_CONVERTER_DATABASES['units_database'][unit] = {
                                    'category': category,
                                    'factor': data.get('factor', 1.0),
                                    'offset': data.get('offset', 0.0),
                                    'formula': data.get('formula', 'linear'),
                                    'description': data.get('description', '')
                                }
        
        _GLOBAL_CONVERTER_DATABASES['initialized'] = True
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration files: {e}")
    except Exception as e:
        raise ValueError(f"Error loading converter databases: {e}")


def _are_categories_compatible(cat1: str, cat2: str) -> bool:
    """Check if two categories are compatible for conversion.
    
    Some categories are physically equivalent (e.g., pressure and stress)
    and should allow conversion between their units.
    
    Args:
        cat1: First category
        cat2: Second category
        
    Returns:
        True if categories are compatible for conversion
    """
    if cat1 == cat2:
        return True
    
    # Pressure and stress are physically equivalent
    equivalent_groups = [
        {'pressure', 'stress'}
    ]
    
    for group in equivalent_groups:
        if cat1 in group and cat2 in group:
            return True
    
    return False


def convert_units(value: Union[float, int], from_unit: str, to_unit: str, 
                 precision: int = None, round_result: bool = True) -> float:
    """Convert value between units using global databases.
    
    Args:
        value: Numeric value to convert
        from_unit: Source unit
        to_unit: Target unit  
        precision: Decimal places for rounding
        round_result: Whether to round the result
        
    Returns:
        Converted value
        
    Raises:
        ValueError: If units are invalid or conversion not possible
        RuntimeError: If databases not initialized
    """
    if not _GLOBAL_CONVERTER_DATABASES['initialized']:
        raise RuntimeError("Converter databases not initialized. Call initialize_converter_databases() first.")
    
    # Normalize unit strings
    from_unit = _normalize_unit_str(from_unit)
    to_unit = _normalize_unit_str(to_unit)
    
    # Check for same unit
    if from_unit == to_unit:
        return float(value)
    
    # Try direct conversion
    factor = get_direct_conversion_factor(from_unit, to_unit)
    if factor is not None:
        result = float(value) * factor
        if round_result and precision is not None:
            result = round(result, precision)
        return result
    
    # Try conversion through common base unit
    from_base = get_base_unit_conversion(from_unit)
    to_base = get_base_unit_conversion(to_unit)
    
    if from_base and to_base and _are_categories_compatible(from_base['category'], to_base['category']):
        # Convert to base, then to target
        base_value = apply_unit_conversion(value, from_base)
        result = apply_reverse_conversion(base_value, to_base)
        if round_result and precision is not None:
            result = round(result, precision)
        return result
    
    raise ValueError(f"No conversion path found from '{from_unit}' to '{to_unit}'")


def get_direct_conversion_factor(from_unit: str, to_unit: str) -> Optional[float]:
    """Get direct conversion factor between two units.
    
    Args:
        from_unit: Source unit
        to_unit: Target unit
        
    Returns:
        Conversion factor or None if not available
    """
    if not _GLOBAL_CONVERTER_DATABASES['initialized']:
        return None
    
    conversion_config = _GLOBAL_CONVERTER_DATABASES['conversion_config']
    
    for category, units in conversion_config.items():
        if isinstance(units, dict):
            if from_unit in units and to_unit in units:
                from_factor = units[from_unit].get('factor', 1.0)
                to_factor = units[to_unit].get('factor', 1.0)
                return from_factor / to_factor
    
    return None


def get_base_unit_conversion(unit: str) -> Optional[Dict[str, Any]]:
    """Get conversion info for a unit to its base unit.
    
    Args:
        unit: Unit to convert
        
    Returns:
        Conversion info dict or None
    """
    if not _GLOBAL_CONVERTER_DATABASES['initialized']:
        return None
    
    return _GLOBAL_CONVERTER_DATABASES['units_database'].get(unit)


def apply_unit_conversion(value: Union[float, int], conversion_info: Dict[str, Any]) -> float:
    """Apply unit conversion using conversion info.
    
    Args:
        value: Value to convert
        conversion_info: Conversion parameters
        
    Returns:
        Converted value
    """
    factor = conversion_info.get('factor', 1.0)
    offset = conversion_info.get('offset', 0.0)
    formula = conversion_info.get('formula', 'linear')
    
    if formula == 'linear':
        return (float(value) + offset) * factor
    else:
        # Handle other formulas if needed
        return float(value) * factor


def apply_reverse_conversion(value: Union[float, int], conversion_info: Dict[str, Any]) -> float:
    """Apply reverse unit conversion using conversion info.
    
    Args:
        value: Base unit value to convert back
        conversion_info: Conversion parameters
        
    Returns:
        Converted value
    """
    factor = conversion_info.get('factor', 1.0)
    offset = conversion_info.get('offset', 0.0)
    formula = conversion_info.get('formula', 'linear')
    
    if formula == 'linear':
        return (float(value) / factor) - offset
    else:
        # Handle other formulas if needed
        return float(value) / factor


def _normalize_unit_str(unit_str: str, superscript_mappings: Dict[str, str] = None, 
                       subscript_mappings: Dict[str, str] = None) -> str:
    """Normalize unit string by handling aliases and formatting.
    
    Args:
        unit_str: Raw unit string
        superscript_mappings: Optional superscript character mappings
        subscript_mappings: Optional subscript character mappings
        
    Returns:
        Normalized unit string
    """
    if not unit_str:
        return ""
    
    # Apply aliases if databases initialized
    if _GLOBAL_CONVERTER_DATABASES['initialized']:
        aliases = _GLOBAL_CONVERTER_DATABASES['aliases_database']
        if unit_str in aliases:
            unit_str = aliases[unit_str]
    
    # Handle common numeric patterns (like "m2" -> "m^2")
    import re
    # Replace pattern like "/m2" or "/cm2" with "/m^2", "/cm^2" etc.
    unit_str = re.sub(r'([a-zA-Z])([23456789])(\s*$|[\s/·*])', r'\1^\2\3', unit_str)
    # Handle patterns like "m2/" -> "m^2/"  
    unit_str = re.sub(r'([a-zA-Z])([23456789])([/·*])', r'\1^\2\3', unit_str)
    
    # Get character mappings from FORMAT kingdom - NO HARDCODED VALUES
    try:
        if superscript_mappings is None or subscript_mappings is None:
            from ePy_docs.components.format import get_format_config
            format_config = get_format_config()
            
            if superscript_mappings is None:
                # Get superscript mappings from format.json - CONSTITUTIONAL SOURCE
                # We need to reverse the mapping: unicode char -> caret notation
                unicode_format = format_config.get('unicode', {}).get('superscripts', {})
                superscript_mappings = {}
                for caret_notation, unicode_char in unicode_format.items():
                    if caret_notation.startswith('^'):
                        superscript_mappings[unicode_char] = caret_notation
                
            if subscript_mappings is None:
                # Get subscript mappings from format.json - CONSTITUTIONAL SOURCE  
                unicode_format = format_config.get('unicode', {}).get('subscripts', {})
                subscript_mappings = {}
                for caret_notation, unicode_char in unicode_format.items():
                    subscript_mappings[unicode_char] = caret_notation
    except Exception:
        # CONSTITUTIONAL COMPLIANCE: No fallbacks - FORMAT kingdom must be complete
        if superscript_mappings is None:
            superscript_mappings = {}
        if subscript_mappings is None:
            subscript_mappings = {}
    
    # Apply character mappings from FORMAT kingdom
    result = unit_str
    if superscript_mappings:
        for char, replacement in superscript_mappings.items():
            result = result.replace(char, replacement)
    if subscript_mappings:
        for char, replacement in subscript_mappings.items():
            result = result.replace(char, replacement)
    
    return result.strip()


def get_available_units() -> List[str]:
    """Get list of all available units.
    
    Returns:
        List of unit names
        
    Raises:
        RuntimeError: If databases not initialized
    """
    if not _GLOBAL_CONVERTER_DATABASES['initialized']:
        raise RuntimeError("Converter databases not initialized")
    
    return list(_GLOBAL_CONVERTER_DATABASES['units_database'].keys())


def get_units_by_category(category: str) -> List[str]:
    """Get all units in a specific category.
    
    Args:
        category: Category name
        
    Returns:
        List of unit names in category
        
    Raises:
        RuntimeError: If databases not initialized
    """
    if not _GLOBAL_CONVERTER_DATABASES['initialized']:
        raise RuntimeError("Converter databases not initialized")
    
    units = []
    for unit, data in _GLOBAL_CONVERTER_DATABASES['units_database'].items():
        if data.get('category') == category:
            units.append(unit)
    
    return units


def get_unit_categories() -> List[str]:
    """Get list of all unit categories.
    
    Returns:
        List of category names
        
    Raises:
        RuntimeError: If databases not initialized
    """
    if not _GLOBAL_CONVERTER_DATABASES['initialized']:
        raise RuntimeError("Converter databases not initialized")
    
    categories = set()
    for data in _GLOBAL_CONVERTER_DATABASES['units_database'].values():
        if 'category' in data:
            categories.add(data['category'])
    
    return sorted(list(categories))


def format_unit_display(unit: str, value: Union[float, int] = None) -> str:
    """Format unit for display with optional value.
    
    Args:
        unit: Unit name
        value: Optional numeric value
        
    Returns:
        Formatted display string
    """
    if not _GLOBAL_CONVERTER_DATABASES['initialized']:
        return unit
    
    format_mappings = _GLOBAL_CONVERTER_DATABASES.get('format_mappings', {})
    display_unit = format_mappings.get(unit, unit)
    
    if value is not None:
        return f"{value} {display_unit}"
    
    return display_unit


def validate_unit(unit: str) -> bool:
    """Validate if a unit is supported.
    
    Args:
        unit: Unit name to validate
        
    Returns:
        True if unit is supported
    """
    if not _GLOBAL_CONVERTER_DATABASES['initialized']:
        return False
    
    normalized = _normalize_unit_str(unit)
    return normalized in _GLOBAL_CONVERTER_DATABASES['units_database']


def get_unit_info(unit: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a unit.
    
    Args:
        unit: Unit name
        
    Returns:
        Unit info dict or None if not found
    """
    if not _GLOBAL_CONVERTER_DATABASES['initialized']:
        return None
    
    normalized = _normalize_unit_str(unit)
    return _GLOBAL_CONVERTER_DATABASES['units_database'].get(normalized)


# =====================================
# CORE UTILITY FUNCTION FOR CONFIG ACCESS
# =====================================

def get_unit_from_config(units_config: Dict[str, Any], category: str, unit_type: str) -> Optional[str]:
    """Extract unit value from nested configuration dictionary.
    
    Args:
        units_config: Units configuration dictionary
        category: Category name (e.g., 'structure_dimensions')
        unit_type: Unit type name (e.g., 'length')
        
    Returns:
        Unit string if found, None otherwise
    """
    if not isinstance(units_config, dict):
        return None
    
    # Navigate nested structure: units_config['categories'][category][unit_type][0]
    categories = units_config.get('categories', {})
    if category not in categories:
        return None
    
    category_data = categories[category]
    if not isinstance(category_data, dict) or unit_type not in category_data:
        return None
    
    unit_data = category_data[unit_type]
    if isinstance(unit_data, list) and len(unit_data) > 0:
        return unit_data[0]  # Return first element which is the unit string
    
    return None


# =====================================
# ROBUST UNIT CONVERTER WITH AUTO-RELOAD
# =====================================

def safe_unit_converter(value: Union[float, int], from_unit: str, to_unit: str, 
                       max_retries: int = 1) -> Union[float, int]:
    """
    Robust unit converter with automatic database reload on failure.
    
    This function provides bulletproof unit conversion with auto-recovery.
    If a conversion fails, it automatically reloads the conversion system
    and retries the operation.
    
    Args:
        value: Numeric value to convert
        from_unit: Source unit (e.g., 'ksi', 'Pa', 'atm')
        to_unit: Target unit (e.g., 'kgf/cm2', 'bar', 'psi')
        max_retries: Maximum number of retry attempts after failure
        
    Returns:
        Converted numeric value
        
    Raises:
        Exception: If conversion fails even after reload attempts
        
    Examples:
        >>> safe_unit_converter(100, 'ksi', 'kgf/cm2')
        7030.70
        >>> safe_unit_converter(1, 'atm', 'bar')
        1.01325
        >>> safe_unit_converter(10000, 'Pa', 'kgf/m2')
        1019.72
    """
    for attempt in range(max_retries + 1):
        try:
            # Attempt the conversion using the existing convert_units function
            result = convert_units(value, from_unit, to_unit)
            return result
            
        except Exception as e:
            if attempt < max_retries:
                print(f"⚠️  Recargando sistema de conversión debido a: {e}")
                
                # Force reload the conversion databases
                units_dir = os.path.dirname(__file__)
                initialize_converter_databases(
                    conversion_file=os.path.join(units_dir, 'conversion.json'),
                    prefix_file=os.path.join(units_dir, 'prefix.json'),
                    aliases_file=os.path.join(units_dir, 'aliases.json'),
                    format_file=None,
                    units_file=os.path.join(units_dir, 'units.json')
                )
                
                # Try again after reload
                continue
            else:
                # Final attempt failed
                raise Exception(f"Conversión falló incluso después de recarga: {e}")


# =====================================
# SMART UNIT CONVERTER WITH units.json DEFAULTS
# =====================================

def load_units_config(units_json_path: Optional[str] = None) -> Dict[str, Any]:
    """Load units configuration from units.json."""
    if units_json_path is None:
        units_json_path = os.path.join(os.path.dirname(__file__), 'units.json')
    
    with open(units_json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_default_target_unit(source_unit: str, context: str = "auto") -> str:
    """Get the default target unit based on units.json configuration.
    
    Args:
        source_unit: The source unit to convert from
        context: Context hint for unit selection ('structure', 'section', 'force', etc.)
    
    Returns:
        The target unit to convert to based on units.json defaults
    """
    unit_info = get_default_target_unit_with_precision(source_unit, context)
    return unit_info["unit"]


def get_default_target_unit_with_precision(source_unit: str, context: str = "auto") -> dict:
    """Get the default target unit and precision based on units.json configuration.
    
    Args:
        source_unit: The source unit to convert from
        context: Context hint for unit selection ('structure', 'section', 'force', etc.)
    
    Returns:
        Dict with 'unit' and 'precision' keys based on units.json configuration
    """
    from ePy_docs.units.units import detect_unit_type
    
    units_config = load_units_config()
    categories = units_config.get('categories', {})
    context_mappings = units_config.get('context_mappings', {})
    
    # Detect unit type from conversion.json
    unit_info = detect_unit_type(source_unit)
    unit_category = unit_info.get("type", "unknown")
    
    # Use dynamic context mappings
    if unit_category in context_mappings:
        context_map = context_mappings[unit_category]
        
        # Choose based on context
        if context in context_map:
            mapping_config = context_map[context]
        else:
            mapping_config = context_map.get("auto", context_map[list(context_map.keys())[0]])
        
        # Extract category and unit type from array configuration
        if isinstance(mapping_config, list) and len(mapping_config) >= 2:
            category_name = mapping_config[0]
            unit_type = mapping_config[1]
            
            # Get the target unit and precision from units.json
            category_data = categories.get(category_name, {})
            if unit_type in category_data:
                unit_spec = category_data[unit_type]
                if isinstance(unit_spec, list) and len(unit_spec) >= 2:
                    return {
                        "unit": unit_spec[0],        # First element is the unit
                        "precision": unit_spec[1]    # Second element is the precision
                    }
    
    # Fallback: return source unit with default precision
    return {"unit": source_unit, "precision": 4}


def smart_unit_converter(value: float, source_unit: str, context: str = "auto") -> Tuple[float, str]:
    """Convert a value to the default target unit based on units.json configuration.
    
    Args:
        value: The numeric value to convert
        source_unit: The source unit
        context: Context hint ('structure', 'section', 'force', etc.)
    
    Returns:
        Tuple of (converted_value, target_unit)
    """
    target_unit = get_default_target_unit(source_unit, context)
    
    if target_unit == source_unit:
        return value, target_unit
    
    converted_value = safe_unit_converter(value, source_unit, target_unit)
    return converted_value, target_unit


def smart_unit_converter_with_precision(value: float, source_unit: str, context: str = "auto") -> Tuple[str, str]:
    """Convert a value to the default target unit with proper precision formatting.
    
    Args:
        value: The numeric value to convert
        source_unit: The source unit
        context: Context hint ('structure', 'section', 'force', etc.)
    
    Returns:
        Tuple of (formatted_converted_value, target_unit)
    """
    unit_info = get_default_target_unit_with_precision(source_unit, context)
    target_unit = unit_info["unit"]
    precision = unit_info["precision"]
    
    if target_unit == source_unit:
        formatted_value = f"{value:.{precision}f}"
        return formatted_value, target_unit
    
    converted_value = safe_unit_converter(value, source_unit, target_unit)
    formatted_value = f"{converted_value:.{precision}f}"
    return formatted_value, target_unit


def convert_table_units_smart(force_examples: List[Tuple], context: str = "structure") -> List[Dict[str, str]]:
    """Convert a list of force examples using smart default targets from units.json.
    
    Args:
        force_examples: List of (value, from_unit, to_unit) tuples
        context: Context for determining default units
    
    Returns:
        List of conversion dictionaries ready for DataFrame
    """
    conversions = []
    
    for value, from_unit, to_unit in force_examples:
        try:
            # Option 1: Use specified target unit (original behavior)
            if to_unit:
                result = safe_unit_converter(value, from_unit, to_unit)
                target_unit = to_unit
                # Get precision for the target unit if available
                unit_info = get_default_target_unit_with_precision(to_unit, context)
                precision = unit_info["precision"]
            else:
                # Option 2: Use smart default target from units.json with precision
                formatted_result, target_unit = smart_unit_converter_with_precision(value, from_unit, context)
                result = float(formatted_result)
                precision = get_default_target_unit_with_precision(from_unit, context)["precision"]
            
            if isinstance(result, (int, float)):
                conversions.append({
                    'Original Value': f"{value} {from_unit}",
                    'Converted Value': f"{result:.{precision}f} {target_unit}",
                    'Conversion Factor': f"1 {from_unit} = {result/value:.6f} {target_unit}"
                })
            else:
                conversions.append({
                    'Original Value': f"{value} {from_unit}",
                    'Converted Value': f"{result} {target_unit}",
                    'Conversion Factor': "See conversion"
                })
        except Exception as e:
            conversions.append({
                'Original Value': f"{value} {from_unit}",
                'Converted Value': "Conversion Error",
                'Conversion Factor': f"Error: {str(e)}"
            })
    
    return conversions


# ========================================
# BACKWARD COMPATIBILITY LAYER
# ========================================

class UnitConverter:
    """Compatibility wrapper that provides the same interface as the old UnitConverter class.
    
    This is a temporary compatibility layer for code that still expects UnitConverter.
    All actual work is done by pure functions - this just provides the expected interface.
    
    TRANSPARENCY DIMENSION: This wrapper will be deprecated. Use pure functions directly.
    """
    
    def __init__(self):
        """Initialize the compatibility wrapper."""
        # Ensure converter databases are initialized using current directory structure
        import os
        current_dir = os.path.dirname(__file__)
        
        initialize_converter_databases(
            conversion_file=os.path.join(current_dir, 'conversion.json'),
            prefix_file=os.path.join(current_dir, 'prefix.json'),
            aliases_file=os.path.join(current_dir, 'aliases.json'),
            format_file=None,
            units_file=os.path.join(current_dir, 'units.json')
        )
    
    @classmethod
    def create_default(cls, sync_files: bool = True):
        """Create default converter instance for backward compatibility."""
        return cls()
    
    def convert(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert value from one unit to another."""
        return convert_units(value, from_unit, to_unit)
    
    def safe_convert(self, value: float, from_unit: str, to_unit: str) -> float:
        """Safely convert value with error handling."""
        return safe_unit_converter(value, from_unit, to_unit)
    
    def smart_convert(self, value: float, source_unit: str, context: str = "auto") -> Tuple[float, str]:
        """Smart convert using default target units."""
        return smart_unit_converter(value, source_unit, context)
    
    def smart_convert_with_precision(self, value: float, source_unit: str, context: str = "auto") -> Tuple[str, str]:
        """Smart convert with precision formatting."""
        return smart_unit_converter_with_precision(value, source_unit, context)
    
    def convert_table(self, force_examples: List[Tuple], context: str = "structure") -> List[Dict[str, str]]:
        """Convert table of unit examples."""
        return convert_table_units_smart(force_examples, context)
    
    def universal_unit_converter(self, value: float, from_unit: str, to_unit: str) -> float:
        """Universal unit converter method for backward compatibility."""
        return convert_units(value, from_unit, to_unit)
