"""Image processing utilities for ePy_docs.

Provides unified image handling, plot generation, and markdown creation
with centralized configuration management and intelligent caching.
"""

from typing import Tuple, List, Optional, Dict, Any, Union
from pathlib import Path
import shutil


class ImageProcessor:
    """Unified image processing engine with cached configuration."""
    
    _matplotlib_configured = False  # Class variable to track if matplotlib is configured
    
    def __init__(self):
        self._config_cache = {}
        self._path_cache = {}
        # Initialize logger
        import logging
        self.logger = logging.getLogger(__name__)
        
        # Configure matplotlib fonts ONCE at first initialization
        if not ImageProcessor._matplotlib_configured:
            self._early_matplotlib_setup()
            ImageProcessor._matplotlib_configured = True
    
    def _early_matplotlib_setup(self):
        """Configure matplotlib BEFORE any plotting to avoid font warnings."""
        try:
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            from matplotlib import rcParams
            
            # Minimal setup - fonts will be configured later from layout
            rcParams['font.family'] = 'sans-serif'
            rcParams['font.size'] = 10
            rcParams['axes.unicode_minus'] = False
            
            # Register Arial Narrow if available
            try:
                from pathlib import Path
                import matplotlib.font_manager as fm
                package_root = Path(__file__).parent.parent
                arial_narrow_path = package_root / 'config' / 'assets' / 'fonts' / 'arial_narrow.TTF'
                if arial_narrow_path.exists():
                    fm.fontManager.addfont(str(arial_narrow_path))
            except Exception as e:
                self.logger.debug(f"Could not register Arial Narrow: {e}")
                
        except Exception as e:
            self.logger.debug(f"Early matplotlib setup failed: {e}")
    
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
        column_span: Optional[int] = None,
        document_columns: int = 1,
        **kwargs
    ) -> Tuple[str, int, List]:
        """Generate image markdown with standardized naming.
        
        Args:
            column_span: Number of columns the image should span (None=1, 2, 3, etc.)
            document_columns: Total number of columns in document (for span calculation)
        """
        # Use provided width or default
        final_width = width
        
        # Process image file
        dest_path = self._process_image_file(path, figure_counter, output_dir, document_type)
        
        # Display in notebook if requested
        if show_figure:
            self._display_in_notebook(dest_path)
        
        # Generate markdown with column class
        markdown = self._build_image_markdown(
            dest_path, caption, final_width, alt_text, figure_counter, column_span, document_columns
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
        column_span: Optional[int] = None,
        document_columns: int = 1,
        **kwargs
    ) -> Tuple[str, int]:
        """Generate plot markdown with standardized naming.
        
        Args:
            palette_name: Name of color palette to use for plot colors (e.g., 'blues', 'reds').
                         If specified, matplotlib will use only colors from this palette.
                         If None, matplotlib uses its default color cycle.
            column_span: Number of columns the plot should span (None=1, 2, 3, etc.)
            document_columns: Total number of columns in document (for span calculation)
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
        
        # Generate markdown with column class
        markdown = self._build_plot_markdown(
            final_path, title, caption, figure_counter, plot_width, column_span, document_columns
        )
        
        return markdown, figure_counter, final_path
    
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
        
        # Clean up matplotlib thoroughly
        try:
            import matplotlib.pyplot as plt
            plt.close(fig)
            # Force garbage collection for better memory management
            import gc
            gc.collect()
        except Exception:
            pass  # Ignore cleanup errors
        
        # Clean up any temporary matplotlib files in the same directory
        image_config = self._get_image_config()
        if image_config.get('output_settings', {}).get('cleanup_temporary_files', True):
            self._cleanup_matplotlib_temps(target_dir)
        
        return str(output_path)

    def _cleanup_matplotlib_temps(self, directory: Path) -> None:
        """Clean up temporary matplotlib files in directory.
        
        Args:
            directory: Directory to clean up
        """
        if not directory.exists():
            return
            
        # Common matplotlib temporary file patterns
        temp_patterns = [
            'tmp*.png',
            'tmp*.jpg', 
            'matplotlib_*.png',
            'figure_*.tmp',
            'temp_*.png'
        ]
        
        import glob
        for pattern in temp_patterns:
            temp_files = directory.glob(pattern)
            for temp_file in temp_files:
                try:
                    if temp_file.exists() and temp_file.is_file():
                        temp_file.unlink()
                except (OSError, PermissionError):
                    # Ignore cleanup errors
                    pass

    def _get_column_class(self, column_span: Optional[int], document_columns: int) -> str:
        """Get Quarto column class based on span and document columns.
        
        Args:
            column_span: Number of columns element should span (None = 1)
            document_columns: Total columns in document
            
        Returns:
            Quarto column class: 'column-body', 'column-body-outset-right', or 'column-page'
        """
        if column_span is None or column_span == 1:
            return "column-body"
        elif column_span >= document_columns:
            return "column-page"
        else:
            # Use -right variant to avoid left overflow in multi-column layouts
            return "column-body-outset-right"
    
    def _get_output_directory(self, output_dir: Optional[str], document_type: str) -> Path:
        """Get standardized output directory for figures."""
        if output_dir is not None:
            return Path(output_dir)
        
        # Use caching for repeated calls
        cache_key = f"output_dir_{document_type}"
        if cache_key not in self._path_cache:
            from ePy_docs.core._config import get_absolute_output_directories
            output_dirs = get_absolute_output_directories(document_type=document_type)
            figures_dir = Path(output_dirs['figures'])
            self._path_cache[cache_key] = figures_dir
        
        return self._path_cache[cache_key]
    
    def _build_image_markdown(self, img_path: Path, caption: str, width: str, alt_text: str, 
                             counter: int, column_span: Optional[int] = None, 
                             document_columns: int = 1) -> str:
        """Build markdown for image content with column span support."""
        parts = []
        
        if caption:
            parts.append(f"**{self._get_figure_label(counter)}:** {caption}\n\n")
        
        alt = alt_text or caption or self._get_default_alt_text()
        parts.append(f"![{alt}]({img_path})")
        
        # Build attributes: width + id + column class
        fig_width = self.parse_image_width(width)
        column_class = self._get_column_class(column_span, document_columns)
        parts.append(f"{{width={fig_width} #{self._get_figure_id(counter)} .{column_class}}}")
        parts.append("\n\n")
        return ''.join(parts)
    
    def _build_plot_markdown(self, img_path: str, title: str, caption: str, counter: int, 
                            width: str = None, column_span: Optional[int] = None,
                            document_columns: int = 1) -> str:
        """Build markdown for plot content with column span support."""
        parts = []
        
        if title:
            parts.append(f"### {title}\n\n")
        if caption:
            parts.append(f"**{self._get_figure_label(counter)}:** {caption}\n\n")
        
        # Use provided width or default width to ensure consistent sizing with tables
        plot_width = width if width is not None else self._get_default_width()
        
        # Use title as alt text if available
        alt_text = title if title else ""
        column_class = self._get_column_class(column_span, document_columns)
        parts.append(f"![{alt_text}]({img_path}){{width={plot_width} #{self._get_figure_id(counter)} .{column_class}}}\n\n")
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
        """Configure matplotlib fonts from epyson configuration - RESPECTS USER CONFIG."""
        import matplotlib.pyplot as plt
        from matplotlib import rcParams
        
        # Get configured fonts from epyson - THIS IS WHAT THE USER CONFIGURED
        font_list = self._get_font_list_from_config(layout_style)
        
        self.logger.debug(f"Configuring matplotlib with fonts from epyson: {font_list}")
        
        # Configure matplotlib with configuration-only fonts
        rcParams.update({
            'font.sans-serif': font_list,
            'font.family': 'sans-serif', 
            'font.size': 10,
            'axes.unicode_minus': False
        })
        # Note: serif and monospace fonts should come from configuration if needed
        
        # Clear matplotlib font cache to force reload
        try:
            import matplotlib.font_manager as fm
            if hasattr(fm, 'get_fontconfig_fonts'):
                fm.fontManager = fm.FontManager()  # Force rebuild
            self.logger.debug("Rebuilt matplotlib font manager")
        except Exception as e:
            self.logger.debug(f"Could not rebuild font manager: {e}")
        
        self.logger.debug(f"Configured matplotlib fonts: {font_list[:3]}...")
        return font_list
    

    
    def _get_font_list_from_config(self, layout_style: str) -> List[str]:
        """Extract font list from epyson configuration."""
        from ePy_docs.core._config import get_layout, get_config_section
        
        try:
            # Get layout configuration
            layout_data = get_layout(layout_style)
            self.logger.debug(f"Layout data for {layout_style}: {layout_data}")
            
            # Try different approaches to get font configuration
            font_list = []
            
            # Approach 1: Direct from layout font_family
            if 'font_family' in layout_data:
                font_info = layout_data['font_family']
                if isinstance(font_info, dict):
                    if 'primary' in font_info:
                        primary_font = font_info['primary']
                        font_list.append(primary_font)
                        self._register_font_if_exists(primary_font)
                    if 'fallback' in font_info:
                        font_list.append(font_info['fallback'])
                elif isinstance(font_info, str):
                    # It's a reference, try to resolve it
                    format_config = get_config_section('format')
                    if format_config and 'font_families' in format_config:
                        font_families = format_config['font_families']
                        if font_info in font_families:
                            font_config = font_families[font_info]
                            if 'primary' in font_config:
                                primary_font = font_config['primary']
                                font_list.append(primary_font)
                                self._register_font_if_exists(primary_font)
                            if 'fallback' in font_config:
                                fallback_fonts = font_config['fallback']
                                if isinstance(fallback_fonts, str):
                                    font_list.extend([f.strip() for f in fallback_fonts.split(',')])
                                elif isinstance(fallback_fonts, list):
                                    font_list.extend(fallback_fonts)
            
            # Approach 2: From font_family_ref
            if not font_list and 'font_family_ref' in layout_data:
                font_family_ref = layout_data['font_family_ref']
                format_config = get_config_section('format')
                if format_config and 'font_families' in format_config:
                    font_families = format_config['font_families']
                    if font_family_ref in font_families:
                        font_config = font_families[font_family_ref]
                        if 'primary' in font_config:
                            primary_font = font_config['primary']
                            font_list.append(primary_font)
                            self._register_font_if_exists(primary_font)
                        if 'fallback' in font_config:
                            fallback_fonts = font_config['fallback']
                            if isinstance(fallback_fonts, str):
                                font_list.extend([f.strip() for f in fallback_fonts.split(',')])
                            elif isinstance(fallback_fonts, list):
                                font_list.extend(fallback_fonts)
            
            # Approach 3: Legacy method
            if not font_list:
                format_config = get_config_section('format')
                if format_config and 'font_families' in format_config:
                    font_family = self._extract_font_family_from_layout(layout_data)
                    font_families = format_config['font_families']
                    
                    if font_family in font_families:
                        font_config = font_families[font_family]
                        if 'primary' in font_config:
                            primary_font = font_config['primary']
                            font_list.append(primary_font)
                            self._register_font_if_exists(primary_font)
                        if 'fallback' in font_config:
                            fallback_fonts = font_config['fallback']  
                            if isinstance(fallback_fonts, str):
                                font_list.extend([f.strip() for f in fallback_fonts.split(',')])
                            elif isinstance(fallback_fonts, list):
                                font_list.extend(fallback_fonts)
            
            # Ensure Arial Narrow is preserved and properly processed
            processed_fonts = []
            for font in font_list:
                # Keep Arial Narrow as is - it's a valid font
                processed_fonts.append(font)
            
            # Use only fonts from configuration - NO hardcoded fallbacks
            final_list = processed_fonts if processed_fonts else []
            
            if not final_list:
                raise ValueError(f"No fonts configured for layout '{layout_style}'. Check layout configuration.")
            self.logger.debug(f"Final font list for {layout_style}: {final_list}")
            return final_list
            
        except Exception as e:
            self.logger.error(f"Error extracting fonts for {layout_style}: {e}")
            raise ValueError(f"Font configuration error for layout '{layout_style}': {e}")
            
        except Exception as e:
            self.logger.debug(f"Error in _get_font_list_from_config: {e}")
            raise ValueError(f"Font configuration failed for layout '{layout_style}': {e}")
    
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
        import os
        
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
            
            # First try package fonts folder
            package_root = Path(__file__).parent.parent
            font_filename = font_file_template.format(font_name=font_name)
            font_file = package_root / 'config' / 'assets' / 'fonts' / font_filename
            
            if font_file.exists():
                # Register font with matplotlib
                fm.fontManager.addfont(str(font_file))
                self._rebuild_font_cache(fm)
                return True
            
            # If not found in package, try system fonts (Windows)
            if os.name == 'nt':  # Windows
                windows_fonts_dir = Path(os.environ.get('WINDIR', 'C:\\Windows')) / 'Fonts'
                
                # Try common font filename patterns for Arial Narrow
                font_patterns = [
                    'ARIALN.TTF',  # Arial Narrow
                    'ARIALNB.TTF',  # Arial Narrow Bold
                    f'{font_name.replace(" ", "")}.ttf',
                    f'{font_name.replace(" ", "_")}.ttf',
                    f'{font_name.replace(" ", "")}.TTF',
                    f'{font_name.replace(" ", "_")}.TTF',
                ]
                
                for pattern in font_patterns:
                    font_path = windows_fonts_dir / pattern
                    if font_path.exists():
                        try:
                            fm.fontManager.addfont(str(font_path))
                            self._rebuild_font_cache(fm)
                            
                            # Verify registration
                            font_registered = any(f.name == font_name for f in fm.fontManager.ttflist)
                            if font_registered:
                                self.logger.debug(f"✅ Fuente {font_name} registrada desde sistema: {font_path}")
                                return True
                        except Exception as e:
                            self.logger.debug(f"Failed to register {font_path}: {e}")
                            continue
            
            return False
                
        except Exception as e:
            self.logger.debug(f"Error registering font {font_name}: {e}")
            return False
    
    def _rebuild_font_cache(self, fm):
        """Force matplotlib to rebuild font cache."""
        try:
            fm.fontManager._init()
        except AttributeError:
            try:
                fm._rebuild()
            except AttributeError:
                # Clear and rebuild font cache manually
                fm.fontManager.ttflist = []
                fm.fontManager.afmlist = []
                try:
                    fm.fontManager._load_fonts()
                except AttributeError:
                    pass
    
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
) -> Tuple[str, int, str]:
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
