"""Units subpackage for ePy_docs.units.

This module provides unit conversion and detection functionality.
"""

from ePy_docs.units.units import auto_detect_and_convert_units, convert_units_generic, detect_unit_type
from ePy_docs.units.converter import (
    UnitConverter,
    get_unit_from_config,
    load_units_config,
    get_available_unit_categories,
    get_aliases_for_category,
    format_unit_display,
    create_compound_unit,
    create_composite_unit,
    create_moment_unit,
    get_dimensional_units,
    get_structural_units,
    get_foundation_units
)

__all__ = [
    'auto_detect_and_convert_units',
    'convert_units_generic',
    'detect_unit_type',
    'UnitConverter',
    'get_unit_from_config',
    'load_units_config',
    'get_available_unit_categories',
    'get_aliases_for_category',
    'format_unit_display',
    'create_compound_unit',
    'create_composite_unit',
    'create_moment_unit',
    'get_dimensional_units',
    'get_structural_units',
    'get_foundation_units'
]
