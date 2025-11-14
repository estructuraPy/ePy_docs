"""Image processing utilities for ePy_docs.

Provides unified image handling, plot generation, and markdown creation
with centralized configuration management and intelligent caching.
"""

from typing import Tuple, List, Optional, Dict, Any, Union
from pathlib import Path
import shutil


class ImageProcessor:
    """Unified image processing engine with cached configuration."""
    
    def __init__(self):
        self._config_cache = {}
        self._path_cache = {}
    
    def parse_image_width(self, width: str = None) -> str:
        """Parse and validate image width specification."""
        if width is None:
            return self._get_default_width()
        
        if isinstance(width, str):
            # Check for negative values
            if width.startswith('-'):
                raise ValueError(f"Image width must be positive, got: {width}")
            
            valid_units = self._get_image_config().get('valid_units', ['%', 'px', 'em'])
            if any(width.endswith(unit) for unit in valid_units):
                return width
        
        return str(width) if width else self._get_default_width()
    
    def add_image_content(
        self,
        path: str,
        caption: str = None,
        width: str = None,
        alt_text: str = None,
        responsive: bool = True,
        document_type: str = 'report',
        figure_counter: int = 1,
        output_dir: Optional[str] = None,
        show_figure: bool = True,
        **kwargs
    ) -> Tuple[str, int, List]:
        """Generate image markdown with standardized naming."""
        # Use provided width or default
        final_width = width
        
        # Process image file
        dest_path = self._process_image_file(path, figure_counter, output_dir, document_type)
        
        # Display in notebook if requested
        if show_figure:
            self._display_in_notebook(dest_path)
        
        # Generate markdown
        markdown = self._build_image_markdown(
            dest_path, caption, final_width, alt_text, figure_counter
        )
        
        return markdown, figure_counter, [str(dest_path)]
    
    def add_plot_content(
        self,
        img_path: str = None,
        fig=None,
        title: str = None,
        caption: str = None,
        figure_counter: int = 1,
        output_dir: Optional[str] = None,
        document_type: str = 'report',
        show_figure: bool = True,
        layout_style: str = None,
        palette_name: Optional[str] = None,
        **kwargs
    ) -> Tuple[str, int]:
        """Generate plot markdown with standardized naming.
        
        Args:
            palette_name: Name of color palette to use for plot colors (e.g., 'blues', 'reds').
                         If specified, matplotlib will use only colors from this palette.
                         If None, matplotlib uses its default color cycle.
        """
        # Configure color palette if specified
        if palette_name:
            self.setup_matplotlib_palette(palette_name)
        
        # Apply fonts before displaying or saving (works for all layouts)
        if fig is not None and layout_style:
            font_list = self.setup_matplotlib_fonts(layout_style)
            self.apply_fonts_to_figure(fig, font_list)
            try:
                fig.canvas.draw()
            except:
                pass
        
        # Display figure in notebook
        if show_figure and fig is not None:
            self._display_figure_in_notebook(fig)
        
        # Process figure or image
        if fig is not None:
            final_path = self._save_plot_to_output(fig, figure_counter, output_dir, document_type, layout_style)
        elif img_path is not None:
            final_path = self._process_image_file(img_path, figure_counter, output_dir, document_type)
        else:
            raise ValueError(self._get_error_message('missing_input'))
        
        # Use provided width or None for default
        plot_width = None
        
        # Generate markdown
        markdown = self._build_plot_markdown(final_path, title, caption, figure_counter, plot_width)
        
        return markdown, figure_counter
    
    def _process_image_file(self, source_path: str, counter: int, output_dir: Optional[str], document_type: str) -> Path:
        """Process and copy image file to standardized location."""
        # Get output directory
        target_dir = self._get_output_directory(output_dir, document_type)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate standardized filename
        source = Path(source_path)
        extension = source.suffix or '.png'
        filename = f"{self._get_figure_prefix()}{counter}{extension}"
        dest_path = target_dir / filename
        
        # Copy file with error handling
        try:
            shutil.copy2(source, dest_path)
            return dest_path
        except (FileNotFoundError, PermissionError):
            # Return original path if copy fails
            return Path(source_path)
    
    def _save_plot_to_output(self, fig, counter: int, output_dir: Optional[str], document_type: str, layout_style: str = None) -> str:
        """Save matplotlib figure to output directory."""
        target_dir = self._get_output_directory(output_dir, document_type)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename and save
        filename = f"{self._get_figure_prefix()}{counter}.png"
        output_path = target_dir / filename
        
        # Get plot configuration
        plot_config = self._get_plot_config()
        fig.savefig(
            output_path,
            dpi=plot_config.get('dpi', 300),
            bbox_inches=plot_config.get('bbox_inches', 'tight'),
            facecolor=plot_config.get('facecolor', 'white')
        )
        
        # Clean up matplotlib
        import matplotlib.pyplot as plt
        plt.close(fig)
        
        return str(output_path)
    
    def _get_output_directory(self, output_dir: Optional[str], document_type: str) -> Path:
        """Get standardized output directory for figures."""
        if output_dir is not None:
            return Path(output_dir)
        
        # Use caching for repeated calls
        cache_key = f"output_dir_{document_type}"
        if cache_key not in self._path_cache:
            from ePy_docs.core._config import get_absolute_output_directories
            output_dirs = get_absolute_output_directories(document_type=document_type)
            figures_dir = Path(output_dirs[document_type]) / 'figures'
            self._path_cache[cache_key] = figures_dir
        
        return self._path_cache[cache_key]
    
    def _build_image_markdown(self, img_path: Path, caption: str, width: str, alt_text: str, counter: int) -> str:
        """Build markdown for image content."""
        parts = []
        
        if caption:
            parts.append(f"**{self._get_figure_label(counter)}:** {caption}\n\n")
        
        alt = alt_text or caption or self._get_default_alt_text()
        parts.append(f"![{alt}]({img_path})")
        
        # Always include width specification to ensure consistent sizing with tables
        fig_width = self.parse_image_width(width)
        parts.append(f"{{width={fig_width} #{self._get_figure_id(counter)}}}")
        parts.append("\n\n")
        return ''.join(parts)
    
    def _build_plot_markdown(self, img_path: str, title: str, caption: str, counter: int, width: str = None) -> str:
        """Build markdown for plot content."""
        parts = []
        
        if title:
            parts.append(f"### {title}\n\n")
        if caption:
            parts.append(f"**{self._get_figure_label(counter)}:** {caption}\n\n")
        
        # Use provided width or default width to ensure consistent sizing with tables
        plot_width = width if width is not None else self._get_default_width()
        
        # Use title as alt text if available
        alt_text = title if title else ""
        parts.append(f"![{alt_text}]({img_path}){{width={plot_width} #{self._get_figure_id(counter)}}}\n\n")
        return ''.join(parts)
    
    def _display_in_notebook(self, img_path: Path):
        """Display image in Jupyter notebook if available."""
        try:
            from IPython.display import Image, display
            display(Image(filename=str(img_path)))
        except (ImportError, NameError):
            pass
    
    def _display_figure_in_notebook(self, fig):
        """Display matplotlib figure in Jupyter notebook if available."""
        try:
            from IPython.display import display
            display(fig)
        except (ImportError, NameError):
            pass
    
    def _get_image_config(self) -> Dict[str, Any]:
        """Get image configuration with caching."""
        if 'image' not in self._config_cache:
            from ePy_docs.core._config import get_config_section
            self._config_cache['image'] = get_config_section('images')
        return self._config_cache['image']
    
    def _get_plot_config(self) -> Dict[str, Any]:
        """Get plot configuration."""
        return self._get_image_config().get('plot_settings', {})
    
    def _get_figure_label(self, counter: int) -> str:
        """Get localized figure label."""
        template = self._get_image_config().get('figure_label_template', 'Figure {counter}')
        return template.format(counter=counter)
    
    def _get_figure_id(self, counter: int) -> str:
        """Get figure ID for cross-references."""
        prefix = self._get_image_config().get('figure_id_prefix', 'fig')
        return f"{prefix}-{counter}"
    
    def _get_figure_prefix(self) -> str:
        """Get filename prefix for figures."""
        return self._get_image_config().get('filename_prefix', 'figure_')
    
    def _get_default_width(self) -> str:
        """Get default image width."""
        return self._get_image_config().get('default_width', '100%')
    
    def _get_default_alt_text(self) -> str:
        """Get default alt text."""
        return self._get_image_config().get('default_alt_text', 'Image')
    
    def _get_error_message(self, error_type: str) -> str:
        """Get localized error message."""
        messages = self._get_image_config().get('error_messages', {})
        return messages.get(error_type, f"Error: {error_type}")
    
    # Matplotlib and Color Utilities (moved from _tables.py)
    def convert_rgb_to_matplotlib(self, rgb_list) -> Union[str, List[float]]:
        """Convert RGB list [0-255] to matplotlib format [0-1]."""
        if isinstance(rgb_list, str):
            if rgb_list.startswith('#'):
                return rgb_list
            if ',' in rgb_list:
                rgb_list = [x.strip() for x in rgb_list.split(',')]
        
        numeric_rgb = []
        for x in rgb_list:
            if isinstance(x, str):
                try:
                    numeric_rgb.append(float(x))
                except ValueError:
                    numeric_rgb.append(0.0)
            else:
                numeric_rgb.append(float(x))
        
        return [x/255.0 for x in numeric_rgb]
    
    def get_palette_color_by_tone(self, palette_name: str, tone: str) -> List[float]:
        """Get RGB color from palette and tone according to Colors configuration."""
        from ePy_docs.core._config import get_config_section
        colors_config = get_config_section('colors')
        
        if 'palettes' in colors_config and palette_name in colors_config['palettes']:
            palette = colors_config['palettes'][palette_name]
            if tone in palette:
                return self.convert_rgb_to_matplotlib(palette[tone])
        
        # Fallback to neutrals palette
        if 'palettes' in colors_config and 'neutrals' in colors_config['palettes']:
            neutrals = colors_config['palettes']['neutrals']
            if tone in neutrals:
                return self.convert_rgb_to_matplotlib(neutrals[tone])
            return self.convert_rgb_to_matplotlib(neutrals.get('secondary', [250, 250, 250]))
        
        # Ultimate fallback: light gray
        return self.convert_rgb_to_matplotlib([250, 250, 250])
    
    def setup_matplotlib_fonts(self, layout_style: str) -> List[str]:
        """Configure matplotlib fonts for all layouts."""
        import logging
        import warnings
        import matplotlib.font_manager as fm
        import matplotlib.pyplot as plt
        
        # Suppress matplotlib font warnings
        matplotlib_logger = logging.getLogger('matplotlib.font_manager')
        matplotlib_logger.setLevel(logging.ERROR)
        
        # Suppress glyph missing warnings
        warnings.filterwarnings('ignore', message='Glyph .* missing from font.*')
        
        from ePy_docs.core._config import get_layout, get_config_section
        
        # Get layout configuration
        try:
            layout_data = get_layout(layout_style)
        except ValueError:
            layout_data = get_layout('classic')
        
        # Get text configuration for font families
        text_config = get_config_section('text')
        if text_config and 'shared_defaults' in text_config:
            font_families = text_config['shared_defaults'].get('font_families', {})
        else:
            font_families = {}
            
        font_family = self._extract_font_family_from_layout(layout_data)
        
        # Build font list with fallbacks
        font_list = []
        
        if font_family in font_families:
            font_config = font_families[font_family]
            primary_font = font_config['primary']
            
            # Register custom font if exists
            self._register_font_if_exists(primary_font)
            
            # Get matplotlib-specific fallback or use general fallback
            fallback_policy = font_config.get('fallback_policy', {})
            context_specific = fallback_policy.get('context_specific', {})
            
            if 'images_matplotlib' in context_specific:
                matplotlib_fonts = context_specific['images_matplotlib']
                font_list.extend([f.strip() for f in matplotlib_fonts.split(',')])
            else:
                font_list.append(primary_font)
                if 'fallback' in font_config:
                    fallback_fonts = font_config['fallback']
                    font_list.extend([f.strip() for f in fallback_fonts.split(',')])
        elif font_family:
            font_list.append(font_family)
        
        # Add system fallbacks
        system_fallbacks = ['DejaVu Sans', 'Arial', 'sans-serif']
        for fallback in system_fallbacks:
            if fallback not in font_list:
                font_list.append(fallback)
        
        # Configure matplotlib
        plt.rcParams['font.sans-serif'] = font_list
        plt.rcParams['font.family'] = 'sans-serif'
        
        return font_list
    
    def setup_matplotlib_palette(self, palette_name: Optional[str] = None) -> List[List[float]]:
        """Configure matplotlib color cycle with colors from a specific palette.
        
        Args:
            palette_name: Name of the palette to use (e.g., 'blues', 'reds', 'minimal').
                         If None, matplotlib will use its default colors.
        
        Returns:
            List of RGB colors in matplotlib format [0-1].
        """
        if palette_name is None:
            return []
        
        try:
            import matplotlib.pyplot as plt
            from cycler import cycler
            
            # Get colors configuration
            from ePy_docs.core._config import get_config_section
            colors_config = get_config_section('colors')
            
            if 'palettes' not in colors_config or palette_name not in colors_config['palettes']:
                # If palette not found, don't modify matplotlib defaults
                return []
            
            palette = colors_config['palettes'][palette_name]
            
            # Extract all tones in order: primary through senary
            color_list = []
            for tone in ['primary', 'secondary', 'tertiary', 'quaternary', 'quinary', 'senary']:
                if tone in palette:
                    rgb_mpl = self.convert_rgb_to_matplotlib(palette[tone])
                    if isinstance(rgb_mpl, list):
                        color_list.append(rgb_mpl)
            
            if not color_list:
                return []
            
            # Set matplotlib color cycle
            plt.rcParams['axes.prop_cycle'] = cycler(color=color_list)
            
            return color_list
            
        except Exception as e:
            # If anything fails, silently skip and use matplotlib defaults
            return []
    
    def apply_fonts_to_plot(self, ax, font_list: List[str]):
        """Apply font list to all text elements in a plot axis."""
        if ax.title:
            ax.title.set_fontfamily(font_list)
        
        ax.xaxis.label.set_fontfamily(font_list)
        ax.yaxis.label.set_fontfamily(font_list)
        
        for label in ax.get_xticklabels():
            label.set_fontfamily(font_list)
        
        for label in ax.get_yticklabels():
            label.set_fontfamily(font_list)
        
        legend = ax.get_legend()
        if legend:
            for text in legend.get_texts():
                text.set_fontfamily(font_list)
    
    def apply_fonts_to_figure(self, fig, font_list: List[str]):
        """Apply font list to all text elements in a figure."""
        if hasattr(fig, '_suptitle') and fig._suptitle:
            fig._suptitle.set_fontfamily(font_list)
        
        for ax in fig.get_axes():
            self.apply_fonts_to_plot(ax, font_list)
    
    def _register_font_if_exists(self, font_name: str):
        """Register custom font file with matplotlib if it exists."""
        import matplotlib.font_manager as fm
        from pathlib import Path
        
        try:
            from ePy_docs.core._config import get_config_section
            text_config = get_config_section('text')
            
            # Get font families from shared_defaults
            if text_config and 'shared_defaults' in text_config:
                font_families = text_config['shared_defaults'].get('font_families', {})
            else:
                font_families = {}
            
            # Find font file template
            font_file_template = None
            for family_name, family_config in font_families.items():
                if family_config.get('primary') == font_name:
                    font_file_template = family_config.get('font_file_template')
                    break
            
            if not font_file_template:
                font_file_template = "{font_name}.otf"
            
            # Build font file path
            package_root = Path(__file__).parent.parent
            font_filename = font_file_template.format(font_name=font_name)
            font_file = package_root / 'config' / 'assets' / 'fonts' / font_filename
            
            if font_file.exists():
                fm.fontManager.addfont(str(font_file))
                try:
                    fm.fontManager._init()
                except AttributeError:
                    try:
                        fm._rebuild()
                    except AttributeError:
                        pass
                return True
            return False
                
        except Exception:
            return False
    
    def _extract_font_family_from_layout(self, layout_data: Dict[str, Any]) -> str:
        """Extract font family from layout configuration."""
        if 'font_family_ref' in layout_data:
            return layout_data['font_family_ref']
        elif 'font_family' in layout_data:
            return layout_data['font_family']
        elif 'tables' in layout_data and 'content_font' in layout_data['tables']:
            return layout_data['tables']['content_font']['family']
        elif 'typography' in layout_data and 'normal' in layout_data['typography']:
            return layout_data['typography']['normal']['family']
        elif 'colors' in layout_data and 'layout_config' in layout_data['colors'] and 'typography' in layout_data['colors']['layout_config'] and 'normal' in layout_data['colors']['layout_config']['typography']:
            return layout_data['colors']['layout_config']['typography']['normal']['family']
        else:
            return 'sans_technical'


# Global processor instance
_processor = ImageProcessor()


# API Functions - Backward compatibility
def parse_image_width(width: str = None) -> str:
    return _processor.parse_image_width(width)


def add_image_content(
    path: str,
    caption: str = None,
    width: str = None,
    alt_text: str = None,
    responsive: bool = True,
    document_type: str = 'report',
    figure_counter: int = 1,
    output_dir: Optional[str] = None,
    show_figure: bool = True,
    **kwargs
) -> Tuple[str, int, List]:
    return _processor.add_image_content(
        path, caption, width, alt_text, responsive, document_type,
        figure_counter, output_dir, show_figure, **kwargs
    )


def save_plot_to_output(fig, figure_counter: int, output_dir: Optional[str] = None, 
                        document_type: str = 'report') -> str:
    return _processor._save_plot_to_output(fig, figure_counter, output_dir, document_type)


def add_plot_content(
    img_path: str = None,
    fig=None,
    title: str = None,
    caption: str = None,
    figure_counter: int = 1,
    output_dir: Optional[str] = None,
    document_type: str = 'report',
    show_figure: bool = True,
    palette_name: Optional[str] = None,
    **kwargs
) -> Tuple[str, int]:
    return _processor.add_plot_content(
        img_path, fig, title, caption, figure_counter,
        output_dir, document_type, show_figure, 
        palette_name=palette_name, **kwargs
    )


def convert_rgb_to_matplotlib(rgb_list) -> Union[str, List[float]]:
    return _processor.convert_rgb_to_matplotlib(rgb_list)


def get_palette_color_by_tone(palette_name: str, tone: str) -> List[float]:
    return _processor.get_palette_color_by_tone(palette_name, tone)


def setup_matplotlib_fonts(layout_style: str) -> List[str]:
    return _processor.setup_matplotlib_fonts(layout_style)


def setup_matplotlib_palette(palette_name: Optional[str] = None) -> List[List[float]]:
    """Configure matplotlib to use colors from a specific palette.
    
    Args:
        palette_name: Name of palette to use (e.g., 'blues', 'reds', 'minimal').
                     If None, matplotlib uses default colors.
    
    Returns:
        List of RGB colors in matplotlib format [0-1].
    """
    return _processor.setup_matplotlib_palette(palette_name)


def apply_fonts_to_plot(ax, font_list: List[str]):
    return _processor.apply_fonts_to_plot(ax, font_list)


def apply_fonts_to_figure(fig, font_list: List[str]):
    return _processor.apply_fonts_to_figure(fig, font_list)
    return _processor.apply_fonts_to_figure(fig, font_list)
