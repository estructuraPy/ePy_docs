"""Image processing utilities for ePy_docs.

Provides unified image handling, plot generation, and markdown creation
with centralized configuration management and intelligent caching.
"""

from typing import Tuple, List, Optional, Dict, Any, Union
from pathlib import Path
import shutil
from ePy_docs.core._data import TableDimensionCalculator


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
        show_figure: bool = False,
        document_columns: int = 1,
        label: str = None,
        **kwargs
    ) -> Tuple[str, int, List]:
        """Generate image markdown with standardized naming.
        
        Args:
            document_columns: Total number of columns in document (for span calculation)
        """
        # If width not explicitly provided, use 100%
        if width is None:
            final_width = "100%"
        else:
            # Use explicitly provided width
            final_width = width
        
        # Process image file
        dest_path = self._process_image_file(path, figure_counter, output_dir, document_type)
        
        # Display in notebook if requested
        if show_figure:
            self._display_in_notebook(dest_path)
        
        # Generate markdown
        markdown = self._build_image_markdown(
            dest_path, caption, final_width, alt_text, figure_counter, document_columns, label
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
        show_figure: bool = False,
        layout_style: str = None,
        palette_name: Optional[str] = None,
        document_columns: int = 1,
        label: str = None,
        **kwargs
    ) -> Tuple[str, int]:
        """Generate plot markdown with standardized naming.
        
        Args:
            palette_name: Name of color palette to use for plot colors (e.g., 'blues', 'reds').
                         If specified, matplotlib will use only colors from this palette.
                         If None, matplotlib uses its default color cycle.
            document_columns: Total number of columns in document (for span calculation)
            label: Custom label for cross-referencing (e.g., 'myplot'). Will be formatted as 'fig-{label}'.
                  If None, uses figure_counter (e.g., 'fig-1')
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
        
        # Use 100% width for single-column documents
        plot_width = "100%"
        
        # Generate markdown
        markdown = self._build_plot_markdown(
            final_path, title, caption, figure_counter, plot_width, document_columns, label
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
            # Ensure source file exists
            if not source.exists():
                print(f"WARNING: Source image not found: {source_path}")
                return Path(source_path)
            
            # Ensure destination directory exists
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            shutil.copy2(source, dest_path)
            return dest_path
        except Exception as e:
            # More detailed error reporting
            print(f"ERROR: Failed to copy image {source_path} to {dest_path}: {e}")
            # Return original path if copy fails, but this should be rare now
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
        
        # Resolve facecolor if it's a reference
        facecolor = plot_config.get('facecolor', 'white')
        if isinstance(facecolor, str) and facecolor == 'layout_background':
            # Get background color from layout
            try:
                from ePy_docs.core._config import load_layout
                if layout_style:
                    layout = load_layout(layout_style, resolve_refs=False)
                    if 'palette' in layout and 'page' in layout['palette']:
                        bg = layout['palette']['page'].get('background', [255, 255, 255])
                        # Convert RGB [R, G, B] to normalized tuple (r, g, b)
                        facecolor = tuple(v / 255.0 for v in bg)
            except:
                facecolor = 'white'  # Fallback
        
        fig.savefig(
            output_path,
            dpi=plot_config.get('dpi', 300),
            bbox_inches=plot_config.get('bbox_inches', 'tight'),
            facecolor=facecolor
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

    def _escape_latex(self, text: str) -> str:
        """Escape LaTeX special characters in text.
        
        Args:
            text: Text to escape
            
        Returns:
            Text with LaTeX special characters escaped
        """
        if not text:
            return text
            
        # Escape special LaTeX characters
        replacements = {
            '\\': '\\textbackslash{}',
            '{': '\\{',
            '}': '\\}',
            '$': '\\$',
            '&': '\\&',
            '%': '\\%',
            '#': '\\#',
            '_': '\\_',
            '^': '\\textasciicircum{}',
            '~': '\\textasciitilde{}',
        }
        
        result = text
        # Handle backslash first to avoid escaping our escape sequences
        if '\\' in result:
            result = result.replace('\\', replacements['\\'])
        
        # Then handle other characters
        for char, replacement in replacements.items():
            if char != '\\' and char in result:
                result = result.replace(char, replacement)
        
        return result
    
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
                             counter: int, document_columns: int = 1, label: str = None) -> str:
        """Build markdown for image content.
        
        Args:
            label: Optional custom label for Quarto cross-referencing (e.g., 'fig-myimage').
                  If provided, uses this instead of auto-generated 'fig-N' ID.
        """
        parts = []
        
        # Convert to relative path - use only directory name (figures, tables, etc)
        img_path_str = str(img_path)
        img_path_obj = Path(img_path_str)
        
        # For LaTeX compatibility, use relative path from output directory
        # If path contains 'figures', 'tables', or 'images', extract that portion
        # Also check if path points to a results directory to extract the correct relative path
        if img_path_obj.is_absolute():
            # Extract the relevant part: figures/filename or tables/filename or images/filename
            parts_list = img_path_obj.parts
            
            # Check if this is in a results output directory (e.g., results/paper/figures/...)
            if 'results' in parts_list:
                # Find the document type (paper, report, book, etc) after 'results'
                try:
                    results_idx = parts_list.index('results')
                    if results_idx + 1 < len(parts_list):
                        # Get everything after the document type (e.g., after 'paper')
                        doc_type_idx = results_idx + 1
                        if doc_type_idx + 1 < len(parts_list):
                            # This gives us figures/filename or tables/filename or images/filename
                            img_path_normalized = '/'.join(parts_list[doc_type_idx + 1:])
                        else:
                            img_path_normalized = img_path_obj.name
                    else:
                        img_path_normalized = img_path_obj.name
                except (ValueError, IndexError):
                    # Fallback if results is not in parts or indexing fails
                    if 'figures' in parts_list:
                        idx = parts_list.index('figures')
                        img_path_normalized = '/'.join(parts_list[idx:])
                    elif 'tables' in parts_list:
                        idx = parts_list.index('tables')
                        img_path_normalized = '/'.join(parts_list[idx:])
                    elif 'images' in parts_list:
                        idx = parts_list.index('images')
                        img_path_normalized = '/'.join(parts_list[idx:])
                    else:
                        img_path_normalized = img_path_obj.name
            elif 'figures' in parts_list:
                idx = parts_list.index('figures')
                img_path_normalized = '/'.join(parts_list[idx:])
            elif 'tables' in parts_list:
                idx = parts_list.index('tables')
                img_path_normalized = '/'.join(parts_list[idx:])
            elif 'images' in parts_list:
                idx = parts_list.index('images')
                img_path_normalized = '/'.join(parts_list[idx:])
            else:
                # Fallback: just use filename
                img_path_normalized = img_path_obj.name
        else:
            img_path_normalized = img_path_str.replace('\\', '/')
        
        # Prepare alt text
        alt = alt_text if alt_text else caption if caption else self._get_default_alt_text()
        parts.append(f"![{alt}]({img_path_normalized})")
        
        # Build attributes: width + id + caption
        fig_width = self.parse_image_width(width) if width else "100%"
        # Use custom label if provided, otherwise auto-generate
        fig_id = f"#{label}" if label else f"#{self._get_figure_id(counter)}"
        attrs = [f"width={fig_width}", fig_id]
        # Don't add fig-cap if label is provided (metadata already has it)
        if caption and not label:
            # Escape quotes in caption
            caption_escaped = caption.replace('"', '\\"')
            attrs.append(f'fig-cap="{caption_escaped}"')
        parts.append("{" + " ".join(attrs) + "}")
        parts.append("\n\n")
        
        return ''.join(parts)
    
    def _build_plot_markdown(self, img_path: str, title: str, caption: str, counter: int, 
                            width: str = None, document_columns: int = 1, label: str = None) -> str:
        """Build markdown for plot content.
        
        Args:
            label: Custom label for cross-referencing. If None, uses counter.
        """
        parts = []
        
        # Add title if provided
        if title:
            parts.append(f"### {title}\n\n")
        
        # Convert to relative path - use only directory name (figures, tables, etc)
        img_path_str = str(img_path)
        img_path_obj = Path(img_path_str)
        
        # For LaTeX compatibility, use relative path from output directory
        # If path contains 'figures', 'tables', or 'images', extract that portion
        # Also check if path points to a results directory to extract the correct relative path
        if img_path_obj.is_absolute():
            # Extract the relevant part: figures/filename or tables/filename or images/filename
            parts_list = img_path_obj.parts
            
            # Check if this is in a results output directory (e.g., results/paper/figures/...)
            if 'results' in parts_list:
                # Find the document type (paper, report, book, etc) after 'results'
                try:
                    results_idx = parts_list.index('results')
                    if results_idx + 1 < len(parts_list):
                        # Get everything after the document type (e.g., after 'paper')
                        doc_type_idx = results_idx + 1
                        if doc_type_idx + 1 < len(parts_list):
                            # This gives us figures/filename or tables/filename or images/filename
                            img_path_normalized = '/'.join(parts_list[doc_type_idx + 1:])
                        else:
                            img_path_normalized = img_path_obj.name
                    else:
                        img_path_normalized = img_path_obj.name
                except (ValueError, IndexError):
                    # Fallback if results is not in parts or indexing fails
                    if 'figures' in parts_list:
                        idx = parts_list.index('figures')
                        img_path_normalized = '/'.join(parts_list[idx:])
                    elif 'tables' in parts_list:
                        idx = parts_list.index('tables')
                        img_path_normalized = '/'.join(parts_list[idx:])
                    elif 'images' in parts_list:
                        idx = parts_list.index('images')
                        img_path_normalized = '/'.join(parts_list[idx:])
                    else:
                        img_path_normalized = img_path_obj.name
            elif 'figures' in parts_list:
                idx = parts_list.index('figures')
                img_path_normalized = '/'.join(parts_list[idx:])
            elif 'tables' in parts_list:
                idx = parts_list.index('tables')
                img_path_normalized = '/'.join(parts_list[idx:])
            elif 'images' in parts_list:
                idx = parts_list.index('images')
                img_path_normalized = '/'.join(parts_list[idx:])
            else:
                # Fallback: just use filename
                img_path_normalized = img_path_obj.name
        else:
            img_path_normalized = img_path_str.replace('\\', '/')
        
        # Use title as alt text if available
        alt_text = title if title else ""
        
        # Build attributes with width, id, and optional caption
        plot_width = width if width is not None else "100%"
        # Use custom label if provided, otherwise use counter
        figure_id = f"#fig-{label}" if label else f"#{self._get_figure_id(counter)}"
        attrs = [f"width={plot_width}", figure_id]
        if caption:
            # Escape quotes in caption
            caption_escaped = caption.replace('"', '\\"')
            attrs.append(f'fig-cap="{caption_escaped}"')
        
        parts.append(f"![{alt_text}]({img_path_normalized})" + "{" + " ".join(attrs) + "}\n\n")
        
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
        """Get image/figure configuration with caching (now unified under 'figures')."""
        if 'image' not in self._config_cache:
            from ePy_docs.core._config import get_config_section
            self._config_cache['image'] = get_config_section('figures')
        return self._config_cache['image']
    
    def _get_plot_config(self) -> Dict[str, Any]:
        """Get plot configuration from layout.figures.plot_settings."""
        # Try to get from layout.figures.plot_settings first
        try:
            from ePy_docs.core._config import load_layout
            if hasattr(self, 'layout_style') and self.layout_style:
                layout = load_layout(self.layout_style, resolve_refs=False)
                if 'figures' in layout and 'plot_settings' in layout['figures']:
                    return layout['figures']['plot_settings']
        except:
            pass
        
        # Fallback to images config if layout doesn't have plot_settings
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
        """Get default image width from layout.figures.defaults."""
        # Try to get from layout.figures.defaults first
        try:
            from ePy_docs.core._config import load_layout
            if hasattr(self, 'layout_style') and self.layout_style:
                layout = load_layout(self.layout_style, resolve_refs=False)
                if 'figures' in layout and 'defaults' in layout['figures'] and 'width' in layout['figures']['defaults']:
                    return layout['figures']['defaults']['width']
        except:
            pass
        
        # Fallback to images config
        return self._get_image_config().get('default_width', '100%')
    
    def _get_default_alt_text(self) -> str:
        """Get default alt text from layout.figures.defaults."""
        # Try to get from layout.figures.defaults first
        try:
            from ePy_docs.core._config import load_layout
            if hasattr(self, 'layout_style') and self.layout_style:
                layout = load_layout(self.layout_style, resolve_refs=False)
                if 'figures' in layout and 'defaults' in layout['figures'] and 'alt_text' in layout['figures']['defaults']:
                    return layout['figures']['defaults']['alt_text']
        except:
            pass
        
        # Fallback to images config
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
        
        # Filter out metadata keys
        metadata_keys = {'description', 'version', 'last_updated'}
        palettes = {k: v for k, v in colors_config.items() if k not in metadata_keys}
        
        if palette_name in palettes:
            palette = palettes[palette_name]
            if tone in palette:
                return self.convert_rgb_to_matplotlib(palette[tone])
        
        # Fallback to neutrals palette
        if 'neutrals' in palettes:
            neutrals = palettes['neutrals']
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
            
            # Approach 1: From resolved 'text' field (most common after resolve_refs=True)
            if 'text' in layout_data and isinstance(layout_data['text'], dict):
                font_info = layout_data['text']
                if 'primary' in font_info:
                    primary_font = font_info['primary']
                    font_list.append(primary_font)
                    self._register_font_if_exists(primary_font)
                if 'fallback' in font_info:
                    fallback_fonts = font_info['fallback']
                    if isinstance(fallback_fonts, str):
                        font_list.extend([f.strip() for f in fallback_fonts.split(',')])
                    elif isinstance(fallback_fonts, list):
                        font_list.extend(fallback_fonts)
            
            # Approach 2: Direct from layout font_family (if it's a dict)
            if not font_list and 'font_family' in layout_data:
                font_info = layout_data['font_family']
                if isinstance(font_info, dict):
                    if 'primary' in font_info:
                        primary_font = font_info['primary']
                        font_list.append(primary_font)
                        self._register_font_if_exists(primary_font)
                    if 'fallback' in font_info:
                        font_list.append(font_info['fallback'])
                elif isinstance(font_info, str):
                    # It's a reference, try to resolve it from layout's font_families
                    if 'font_families' in layout_data and font_info in layout_data['font_families']:
                        font_config = layout_data['font_families'][font_info]
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
                if 'font_families' in layout_data and font_family_ref in layout_data['font_families']:
                    font_config = layout_data['font_families'][font_family_ref]
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
            
            # Approach 3: Get font from layout's embedded font_families using layout_style name
            if not font_list and 'font_families' in layout_data:
                # Try to get font using layout_style as key (e.g., 'technical', 'classic')
                if layout_style in layout_data['font_families']:
                    font_config = layout_data['font_families'][layout_style]
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
            
            # Filter out metadata keys
            metadata_keys = {'description', 'version', 'last_updated'}
            palettes = {k: v for k, v in colors_config.items() if k not in metadata_keys}
            
            if palette_name not in palettes:
                # If palette not found, don't modify matplotlib defaults
                return []
            
            palette = palettes[palette_name]
            
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
            # Use default font file template (fonts.epyson no longer exists)
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
            return 'technical'


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
    show_figure: bool = False,
    label: str = None,
    **kwargs
) -> Tuple[str, int, List]:
    return _processor.add_image_content(
        path, caption, width, alt_text, responsive, document_type,
        figure_counter, output_dir, show_figure, label=label, **kwargs
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
    show_figure: bool = False,
    palette_name: Optional[str] = None,
    label: str = None,
    **kwargs
) -> Tuple[str, int, str]:
    return _processor.add_plot_content(
        img_path, fig, title, caption, figure_counter,
        output_dir, document_type, show_figure, 
        palette_name=palette_name, label=label, **kwargs
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
