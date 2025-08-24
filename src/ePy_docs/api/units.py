"""
Units module for ePy_docs API.
Provides clean and simple unit conversion functionality and unit management.
"""

import builtins


def setup_units():
    """
    Initialize units system and make conversion functions available globally.
    
    Requires: Library must be initialized with quick_setup() first
    
    Returns:
        Dict with unit system summary
        
    Raises:
        RuntimeError: If library not initialized or setup fails
    """
    # Check if library is initialized
    if not hasattr(builtins, 'configs'):
        raise RuntimeError("Library not initialized. Call quick_setup() first.")
    
    try:
        from ePy_docs.units.converter import initialize_units_system
        
        # Get units configuration and initialize system
        units_config = builtins.configs['units']
        units_data = initialize_units_system(units_config, sync_files=True)
        
        # Make everything available globally
        builtins.units = units_data['all_units']
        builtins.converter = units_data['converter']
        
        # Backward compatibility units as direct globals
        compatibility = units_data['compatibility_units']
        for unit_name, unit_value in compatibility.items():
            if unit_value:  # Only set if value exists
                setattr(builtins, unit_name, unit_value)
        
        # Create convenient conversion functions
        def convert(value, from_unit, to_unit):
            """Convert between any two units."""
            return builtins.converter.universal_unit_converter(value, from_unit, to_unit)
        
        def convert_to_default_length(value, from_unit):
            """Convert to default length unit."""
            length_unit = getattr(builtins, 'length_unit', None)
            if not length_unit:
                raise ValueError("No default length unit configured")
            return builtins.converter.universal_unit_converter(value, from_unit, length_unit)
        
        def convert_to_default_force(value, from_unit):
            """Convert to default force unit."""
            force_unit = getattr(builtins, 'force_unit', None)
            if not force_unit:
                raise ValueError("No default force unit configured")
            return builtins.converter.universal_unit_converter(value, from_unit, force_unit)
        
        # Make conversion functions available globally
        builtins.convert = convert
        builtins.convert_to_default_length = convert_to_default_length
        builtins.convert_to_default_force = convert_to_default_force
        
        # Print summary
        print(f"🔧 Units system initialized with {len(units_data['categories'])} categories:")
        for category, units in builtins.units.items():
            print(f"   📋 {category}: {len(units)} unit types")
        
        # Show backward compatibility defaults
        for unit_name, unit_value in compatibility.items():
            if unit_value:
                display_name = unit_name.replace('_', ' ').title()
                print(f"   📏 Default {display_name}: {unit_value}")
            
        print(f"💡 Global functions: convert(), convert_to_default_length(), convert_to_default_force()")
        print(f"💡 Access units: builtins.units[category][unit_type]")
        
        return {
            'categories': units_data['categories'],
            'total_units': units_data['total_units'],
            'compatibility_units': compatibility
        }
        
    except Exception as e:
        raise RuntimeError(f"Units system setup failed: {e}")


def get_unit_info():
    """Get current unit configuration summary."""
    if not hasattr(builtins, 'units'):
        raise RuntimeError("Units system not initialized. Call setup_units() first.")
    
    return {
        'categories': list(builtins.units.keys()),
        'total_categories': len(builtins.units),
        'total_units': sum(len(units) for units in builtins.units.values()),
        'sample_units': {cat: list(units.keys())[:3] for cat, units in list(builtins.units.items())[:3]}
    }


def convert_units(value, from_unit, to_unit):
    """Convert between units using the global converter."""
    if not hasattr(builtins, 'converter'):
        raise RuntimeError("Units system not initialized. Call setup_units() first.")
    return builtins.converter.universal_unit_converter(value, from_unit, to_unit)


def get_units_by_category(category: str):
    """Get all units in a specific category."""
    if not hasattr(builtins, 'units'):
        raise RuntimeError("Units system not initialized. Call setup_units() first.")
    return builtins.units.get(category, {})


def get_all_categories():
    """Get list of all available unit categories."""
    if not hasattr(builtins, 'units'):
        raise RuntimeError("Units system not initialized. Call setup_units() first.")
    return list(builtins.units.keys())


def get_unit_by_type(category: str, unit_type: str):
    """Get a specific unit by category and type."""
    if not hasattr(builtins, 'units'):
        raise RuntimeError("Units system not initialized. Call setup_units() first.")
    return builtins.units.get(category, {}).get(unit_type, None)


def list_all_available_units():
    """Print a formatted list of all available units organized by category."""
    if not hasattr(builtins, 'units'):
        raise RuntimeError("Units system not initialized. Call setup_units() first.")
    
    print("📋 All Available Units:")
    print("=" * 50)
    
    for category, units in builtins.units.items():
        print(f"\n🔧 {category.replace('_', ' ').title()}:")
        for unit_type, unit_value in units.items():
            print(f"   {unit_type}: {unit_value}")
    
    print("\n" + "=" * 50)
    print(f"Total: {len(builtins.units)} categories, {sum(len(units) for units in builtins.units.values())} unit types")
