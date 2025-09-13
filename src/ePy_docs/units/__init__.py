"""Units subpackage for ePy_docs.units.

This module provides unit conversion and detection functionality.
"""

from ePy_docs.units.units import auto_detect_and_convert_units, convert_units_generic, detect_unit_type
from ePy_docs.units.converter import (
    UnitConverter,
    load_units_config,
    get_unit_categories,
    get_units_by_category,
    get_unit_from_config,
    format_unit_display
)

__all__ = [
    'auto_detect_and_convert_units',
    'convert_units_generic',
    'detect_unit_type',
    'UnitConverter',
    'load_units_config',
    'get_unit_categories',
    'get_units_by_category',
    'get_unit_from_config',
    'format_unit_display'
]
