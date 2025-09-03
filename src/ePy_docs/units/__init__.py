"""Units subpackage for ePy_docs.units.

This module provides unit conversion and detection functionality.
"""

from ePy_docs.units.units import auto_detect_and_convert_units, convert_units_generic, detect_unit_type
from ePy_docs.units.converter import (
    UnitConverter,
    load_units_config,
    get_available_unit_categories,
    get_aliases_for_category,
    get_unit_from_config,
    format_unit_display,
    format_unit_for_output,
    create_compound_unit,
    create_composite_unit,
    create_moment_unit,
    get_dimensional_units,
    get_structural_units,
    get_foundation_units,
    get_decimal_config_from_format_json,
    get_decimal_places_for_conversion_factors,
    get_format_string_for_conversion_factors,
    get_engineering_decimal_config,
    get_format_for_conversion_factors,
    get_conversion_format,
    format_conversion_factor
)

__all__ = [
    'auto_detect_and_convert_units',
    'convert_units_generic',
    'detect_unit_type',
    'UnitConverter',
    'load_units_config',
    'get_available_unit_categories',
    'get_aliases_for_category',
    'get_unit_from_config',
    'format_unit_display',
    'format_unit_for_output',
    'create_compound_unit',
    'create_composite_unit',
    'create_moment_unit',
    'get_dimensional_units',
    'get_structural_units',
    'get_foundation_units',
    'get_decimal_config_from_format_json',
    'get_decimal_places_for_conversion_factors',
    'get_format_string_for_conversion_factors',
    'get_engineering_decimal_config',
    'get_engineering_decimal_config',
    'get_format_for_conversion_factors',
    'get_conversion_format',
    'format_conversion_factor'
]
