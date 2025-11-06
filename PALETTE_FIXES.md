# Fix: Palette Application in Plots and Minimal Tables

## Problems Fixed

### 1. Palettes Not Being Applied to Matplotlib Plots

**Problem**: When users specified `palette_name` in `add_plot()`, the palette colors were not being applied to the plot. Matplotlib continued using its default color cycle.

**Example Usage**:
```python
writer.add_plot(
    fig,
    title="Gráfico con paleta 'blues'",
    palette_name='blues'  # ❌ Not working
)
```

**Root Cause**: In `src/ePy_docs/core/_images.py` line ~469, `setup_matplotlib_palette()` called `self.load_cached_files()` which doesn't exist:
```python
def setup_matplotlib_palette(self, palette_name: Optional[str] = None):
    ...
    # Get colors configuration
    colors_config = self.load_cached_files()  # ❌ Method doesn't exist
```

**Solution**: Changed to use existing `get_config_section('colors')`:
```python
def setup_matplotlib_palette(self, palette_name: Optional[str] = None):
    ...
    # Get colors configuration
    from ePy_docs.core._config import get_config_section
    colors_config = get_config_section('colors')  # ✅ Correct method
```

### 2. Minimal Layout Tables Showing Gray Colors

**Problem**: Minimal layout is supposed to use only pure black and white colors, but tables were showing gray colors in:
- Alternating rows
- Borders
- Headers

**Root Cause**: `src/ePy_docs/config/layouts/minimal.epyson` was using `default_palette: "neutrals"` for tables. The `neutrals` palette contains grays:
- `quaternary`: [150, 151, 153] ← Gray!
- `quinary`: [50, 50, 51] ← Dark gray!

**Solution**: Changed minimal layout to use `default_palette: "minimal"`. The `minimal` palette contains only pure black and white:
- `primary`: [255, 255, 255] ← White
- `secondary`: [255, 255, 255] ← White
- `tertiary`: [255, 255, 255] ← White
- `quaternary`: [0, 0, 0] ← Black
- `quinary`: [0, 0, 0] ← Black
- `senary`: [0, 0, 0] ← Black

### 3. Minimal Table Headers Had Black Background (Hiding Text)

**Problem**: After changing to `minimal` palette, table headers had black background with black text, making text invisible.

**Root Cause**: Headers were using `tone: "quaternary"` which is black [0,0,0] in the minimal palette, resulting in black background.

**Solution**: Changed header tone from `quaternary` (black) to `primary` (white):
```json
"header": {
  "default": {
    "palette": "minimal",
    "tone": "primary"  // ✅ White background instead of black
  }
}
```

## File Changes

### src/ePy_docs/core/_images.py (lines ~451-495)

**Before**:
```python
def setup_matplotlib_palette(self, palette_name: Optional[str] = None) -> List[List[float]]:
    """Configure matplotlib color cycle with colors from a specific palette."""
    if palette_name is None:
        return []
    
    try:
        import matplotlib.pyplot as plt
        from cycler import cycler
        
        # Get colors configuration
        colors_config = self.load_cached_files()  # ❌ Doesn't exist
        
        if 'palettes' not in colors_config or palette_name not in colors_config['palettes']:
            return []
        
        palette = colors_config['palettes'][palette_name]
        ...
```

**After**:
```python
def setup_matplotlib_palette(self, palette_name: Optional[str] = None) -> List[List[float]]:
    """Configure matplotlib color cycle with colors from a specific palette."""
    if palette_name is None:
        return []
    
    try:
        import matplotlib.pyplot as plt
        from cycler import cycler
        
        # Get colors configuration
        from ePy_docs.core._config import get_config_section
        colors_config = get_config_section('colors')  # ✅ Correct
        
        if 'palettes' not in colors_config or palette_name not in colors_config['palettes']:
            return []
        
        palette = colors_config['palettes'][palette_name]
        ...
```

### src/ePy_docs/config/layouts/minimal.epyson (lines ~120-170)

**Before** (had grays and black header backgrounds):
```json
"colors": {
  "layout_config": {
    "default_palette": "neutrals",  // ❌ Has grays
    "tables": {
      "alt_row": {
        "palette": "neutrals",  // ❌ Gray alternating rows
        "tone": "secondary"
      },
      "border": {
        "palette": "neutrals",  // ❌ Gray borders
        "tone": "quaternary"
      },
      "header": {
        "default": {
          "palette": "neutrals",  // ❌ Gray headers
          "tone": "quaternary"
        },
        "engineering": {
          "palette": "neutrals",
          "tone": "quaternary"
        },
        ...
      }
    }
  }
}
```

**After** (pure B&W with white header backgrounds):
```json
"colors": {
  "layout_config": {
    "default_palette": "minimal",  // ✅ Pure B&W
    "tables": {
      "alt_row": {
        "palette": "minimal",  // ✅ White alternating rows
        "tone": "secondary"
      },
      "border": {
        "palette": "minimal",  // ✅ Black borders
        "tone": "quaternary"
      },
      "header": {
        "default": {
          "palette": "minimal",  // ✅ Uses minimal palette
          "tone": "primary"      // ✅ White background (not black!)
        },
        "engineering": {
          "palette": "minimal",
          "tone": "primary"      // ✅ White background
        },
        ...
      }
    }
  }
}
```

## Palette Definitions

### Minimal Palette (Pure Black & White)
```json
"minimal": {
  "description": "Paleta monocromática pura: solo blanco y negro para minimal",
  "page_background": [255, 255, 255],
  "primary": [255, 255, 255],      // White
  "secondary": [255, 255, 255],    // White
  "tertiary": [255, 255, 255],     // White
  "quaternary": [0, 0, 0],         // Black
  "quinary": [0, 0, 0],            // Black
  "senary": [0, 0, 0]              // Black
}
```

### Neutrals Palette (Has Grays)
```json
"neutrals": {
  "description": "Paleta base neutra universal: blancos, negros y grises básicos",
  "page_background": [255, 255, 255],
  "primary": [255, 255, 255],      // White
  "secondary": [253, 253, 248],    // Off-white
  "tertiary": [250, 250, 250],     // Light gray
  "quaternary": [150, 151, 153],   // ❌ Gray!
  "quinary": [50, 50, 51],         // ❌ Dark gray!
  "senary": [0, 0, 0]              // Black
}
```

## Usage Examples

### Plots with Specific Palettes

**Blues Palette**:
```python
fig, ax = plt.subplots()
for i in range(4):
    ax.plot(x, y[i], label=f'Series {i+1}')

writer.add_plot(
    fig,
    title="Gráfico con paleta 'blues'",
    palette_name='blues'  # ✅ Now works! Uses only blue tones
)
```

**Minimal Palette** (Black & White only):
```python
fig, ax = plt.subplots()
for i in range(3):
    ax.plot(x, y[i], label=f'Case {i+1}', linewidth=2)

writer.add_plot(
    fig,
    title="Gráfico minimal - solo blanco y negro",
    palette_name='minimal'  # ✅ Uses only black/white
)
```

**Without Palette** (Matplotlib default):
```python
fig, ax = plt.subplots()
ax.scatter(x, y)

writer.add_plot(
    fig,
    title="Sin paleta específica"
    # No palette_name: Uses matplotlib's default colors
)
```

### Tables with Minimal Layout

**Before Fix** (with grays):
```python
writer = DocumentWriter("report", "minimal")
writer.add_colored_table(df, title="Tabla con grises")  # ❌ Showed grays
```

**After Fix** (pure B&W):
```python
writer = DocumentWriter("report", "minimal")
writer.add_colored_table(df, title="Tabla B&W")  # ✅ Only black/white
```

## Testing

### Test File: `test_palette_fixes.py`

**Test Results**:
```
======================================================================
TEST 1: Palette Application in Matplotlib Plots
======================================================================
✓ Available palettes: 20
✓ Minimal palette colors:
  primary     : RGB[255, 255, 255]
  quaternary  : RGB[0, 0, 0]
  senary      : RGB[0, 0, 0]
✓ Minimal palette is pure black and white

✓ Blues palette loaded: 6 colors
✓ Minimal palette in matplotlib: 6 colors
  Color 1: [1.0, 1.0, 1.0] → WHITE
  Color 4: [0.0, 0.0, 0.0] → BLACK
✓ All minimal colors are pure black or white (no grays)

======================================================================
TEST 2: Minimal Layout Table Configuration
======================================================================
✓ Minimal default_palette: 'minimal'
✓ Tables alt_row palette: 'minimal'
✓ Tables border palette: 'minimal'
✓ Default header palette: 'minimal'

======================================================================
TEST 3: Create Minimal Document and Verify Palette Usage
======================================================================
✓ Created DocumentWriter with 'minimal' layout
✓ Writer layout: 'minimal'

======================================================================
✓ ALL TESTS PASSED!
======================================================================
```

## Matplotlib Color Cycle Application

When `palette_name` is specified:

1. **Load palette**: Get RGB colors from `colors.palettes[palette_name]`
2. **Extract tones**: Get colors in order (primary → senary)
3. **Convert to matplotlib format**: RGB [0-255] → [0.0-1.0]
4. **Set color cycle**: `plt.rcParams['axes.prop_cycle'] = cycler(color=color_list)`

Example for `blues` palette:
```python
# Extracted colors (in matplotlib format [0-1]):
[
  [0.89, 0.95, 0.99],  # Light blue (primary)
  [0.70, 0.84, 0.96],  # Sky blue (secondary)
  [0.39, 0.71, 0.96],  # Medium blue (tertiary)
  [0.10, 0.46, 0.82],  # Blue (quaternary)
  [0.05, 0.28, 0.63],  # Dark blue (quinary)
  [0.00, 0.13, 0.52]   # Navy (senary)
]
```

## Impact

### Before Fixes
- ❌ `palette_name` parameter in `add_plot()` didn't work
- ❌ Plots always used matplotlib default colors regardless of palette
- ❌ Minimal tables had gray colors (not pure B&W)
- ❌ Minimal table headers had black background hiding black text
- ❌ Inconsistent with minimal's design philosophy

### After Fixes
- ✅ `palette_name` correctly applies palette colors to plots
- ✅ Blues plots use only blue tones
- ✅ Reds plots use only red tones
- ✅ Minimal plots use only black and white
- ✅ Minimal tables use pure black and white (no grays)
- ✅ Minimal table headers have white background with black text (visible!)
- ✅ All layouts apply their palettes consistently

## Available Palettes

### Colored Palettes
- `blues` - Light blue → navy
- `reds` - Light pink → deep red
- `greens` - Light green → dark green
- `oranges` - Light orange → deep orange
- `purples` - Lavender → deep purple
- `creative` - Cyan/turquoise gradient
- `scientific` - Cyan/aquamarine
- `technical` - Turquoise/teal
- `corporate` - Navy/crimson/gold
- `handwritten` - Earth tones

### Monochrome Palettes
- `minimal` - **Pure black and white only**
- `monochrome` - Gray slate tones (light → dark)
- `neutrals` - Grays (white → black with gray tones)
- `classic` - Grayscale (light → dark grays)

### Status Palettes
- `status_positive` - Green success tones
- `status_negative` - Red error tones
- `status_warning` - Orange/amber warning tones
- `status_info` - Blue information tones

## Related Files

- `src/ePy_docs/core/_images.py` - Image and plot processing
- `src/ePy_docs/config/layouts/minimal.epyson` - Minimal layout definition
- `src/ePy_docs/config/assets.epyson` - Palette definitions
- `test_palette_fixes.py` - Validation tests

## Notes

- **Typography Colors Unchanged**: Headers, body text, etc. in minimal still use `neutrals` palette for black text (senary tone)
- **Only Table Colors Changed**: The fix specifically targets table visualization colors
- **Other Layouts Unaffected**: Classic, professional, etc. continue using their configured palettes
- **Backward Compatible**: Existing code works without changes; `palette_name` is optional

---

**Status**: ✅ Fixed and Validated  
**Tests**: `test_palette_fixes.py` all passing  
**Date**: November 5, 2025
