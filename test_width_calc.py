#!/usr/bin/env python3
"""Test width calculation directly."""

def test_width_calculation():
    """Test width calculation logic."""
    print("🔍 Testing width calculation...")
    
    # Test the width calculation logic
    columns = 2
    img_config = {'height': '4cm'}
    
    # Calculate width as in the function
    if columns == 1:
        calculated_width = '6.5in'
    elif columns == 2:
        calculated_width = '3.2in'
    elif columns == 3:
        calculated_width = '2.1in'
    else:
        calculated_width = f'{6.5/columns:.1f}in'
    
    print(f"📐 Columns: {columns}")
    print(f"📐 Calculated width: {calculated_width}")
    
    # Apply config logic
    if 'width' in img_config:
        width = img_config['width']
    elif 'height' in img_config:
        height = img_config['height']
        if height.endswith('cm'):
            height_cm = float(height[:-2])
            width = calculated_width
        else:
            width = calculated_width
    else:
        width = calculated_width
    
    print(f"📐 Final width: {width}")

if __name__ == "__main__":
    test_width_calculation()