"""
Units module for ePy_docs API.
Provides unit conversion functionality and unit management.
"""

import builtins


def setup_units():
    """
    Initialize units system and make conversion functions available globally.
    
    Requires: Library must be initialized with quick_setup() first
    
    Returns:
        Dict with unit system components
        
    Raises:
        RuntimeError: If library not initialized
    """
    
    # Check if library is initialized
    if not hasattr(builtins, 'configs'):
        raise RuntimeError("Library not initialized. Call quick_setup() first.")
    
    try:
        from ePy_docs.units.converter import UnitConverter, get_unit_from_config
        
        # Get units configuration
        units_config = builtins.configs['units']
        
        # Get default units from configuration
        length_unit = get_unit_from_config(units_config, 'structure_dimensions', 'length')
        area_unit = get_unit_from_config(units_config, 'structure_dimensions', 'structure_area')
        volume_unit = get_unit_from_config(units_config, 'section_dimensions', 'length3')
        force_unit = get_unit_from_config(units_config, 'forces', 'force')
        moment_unit = get_unit_from_config(units_config, 'forces', 'moment')
        
        # Create unit converter
        converter = UnitConverter.create_default()
        
        # Make units and converter available globally
        builtins.length_unit = length_unit
        builtins.area_unit = area_unit
        builtins.volume_unit = volume_unit
        builtins.force_unit = force_unit
        builtins.moment_unit = moment_unit
        builtins.converter = converter
        
        # Create convenient conversion functions
        def convert(value, from_unit, to_unit):
            """Convenient conversion function."""
            return converter.universal_unit_converter(value, from_unit, to_unit)
        
        def convert_to_default_length(value, from_unit):
            """Convert to default length unit."""
            return converter.universal_unit_converter(value, from_unit, length_unit)
        
        def convert_to_default_force(value, from_unit):
            """Convert to default force unit."""
            return converter.universal_unit_converter(value, from_unit, force_unit)
        
        # Make conversion functions available globally
        builtins.convert = convert
        builtins.convert_to_default_length = convert_to_default_length
        builtins.convert_to_default_force = convert_to_default_force
        
        units_info = {
            'length_unit': length_unit,
            'area_unit': area_unit, 
            'volume_unit': volume_unit,
            'force_unit': force_unit,
            'moment_unit': moment_unit,
            'converter': converter
        }
        
        print(f"🔧 Units system initialized:")
        print(f"   📏 Length: {length_unit}")
        print(f"   📐 Area: {area_unit}")
        print(f"   📦 Volume: {volume_unit}")
        print(f"   🏋️ Force: {force_unit}")
        print(f"   ⚖️ Moment: {moment_unit}")
        print(f"💡 Available functions: convert(), convert_to_default_length(), convert_to_default_force()")
        
        return units_info
        
    except Exception as e:
        raise RuntimeError(f"Units system setup failed: {e}")


def get_unit_info():
    """
    Get current unit configuration.
    
    Returns:
        Dict with current units
    """
    if not hasattr(builtins, 'length_unit'):
        raise RuntimeError("Units system not initialized. Call setup_units() first.")
    
    return {
        'length_unit': builtins.length_unit,
        'area_unit': builtins.area_unit,
        'volume_unit': builtins.volume_unit,
        'force_unit': builtins.force_unit,
        'moment_unit': builtins.moment_unit
    }


def convert_units(value, from_unit, to_unit):
    """
    Convert between units using the global converter.
    
    Args:
        value: Value to convert
        from_unit: Source unit
        to_unit: Target unit
        
    Returns:
        Converted value
    """
    if not hasattr(builtins, 'converter'):
        raise RuntimeError("Units system not initialized. Call setup_units() first.")
    
    return builtins.converter.universal_unit_converter(value, from_unit, to_unit)
