"""PDF styling utilities for report generation.

Provides PDF style configuration, color management, and layout settings
for consistent document formatting using ReportLab with JSON-based configuration.
"""

import os
from typing import Dict, Any, Optional, Tuple, Union, List
from dataclasses import dataclass
from enum import Enum
from pydantic import BaseModel

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus.tables import TableStyle

from ePy_docs.styler.setup import get_styles_config, get_style_value, ConfigurationError
from ePy_docs.styler.colors import get_color, convert_to_reportlab_color

# Backward compatibility import - _load_cached_json should be imported from ePy_docs.files.data
from ePy_docs.files.data import _load_cached_json


class WatermarkConfig(BaseModel):
    """Configuration for watermark settings for PDF documents."""
    watermark_path: Optional[str] = None
    opacity: float = 0.3
    position: str = "center"
    scale: float = 1.0
    enabled: bool = False
    
    @classmethod
    def from_config(cls, sync_json: bool = True) -> 'WatermarkConfig':
        """Create watermark config from styles configuration."""
        try:
            config_data = get_style_value('pdf.watermark', {}, sync_json)
            return cls(**config_data)
        except (ConfigurationError, TypeError):
            return cls()
    
    def get_watermark_path(self) -> Optional[str]:
        """Gets the actual watermark path, checking if file exists."""
        if not self.enabled:
            return None
            
        # Try configured path first
        if self.watermark_path and os.path.exists(self.watermark_path):
            return self.watermark_path
        
        # Try default paths
        default_paths = [
            os.path.join(os.getcwd(), "brand", "watermark.png"),
            os.path.join(os.getcwd(), "brand", "logo.png"),
            os.path.join(os.getcwd(), "assets", "brand", "watermark.png"),
            os.path.join(os.getcwd(), "assets", "watermark.png"),
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                return path
        
        return None


class PageSize(Enum):
    """Enumeration for standard page sizes."""
    LETTER = "letter"
    A4 = "a4"


class TextAlignment(Enum):
    """Text alignment options for PDF content."""
    LEFT = TA_LEFT
    CENTER = TA_CENTER
    RIGHT = TA_RIGHT
    JUSTIFY = TA_JUSTIFY


@dataclass
class PDFMargins:
    """PDF page margins configuration."""
    top: float
    bottom: float
    left: float
    right: float
    
    @classmethod
    def from_config(cls, sync_json: bool = True) -> 'PDFMargins':
        """Create PDFMargins from styles configuration."""
        try:
            margins_config = get_style_value('pdf.margins', {}, sync_json)
            return cls(
                top=margins_config.get('top', 72),
                bottom=margins_config.get('bottom', 72),
                left=margins_config.get('left', 72),
                right=margins_config.get('right', 72)
            )
        except ConfigurationError:
            # Default margins (1 inch)
            return cls(top=72, bottom=72, left=72, right=72)


@dataclass
class PDFStyleConfig:
    """Configuration for PDF text styles."""
    fontSize: int
    leading: Optional[int]
    textColor: str
    alignment: TextAlignment
    spaceAfter: int
    spaceBefore: int
    leftIndent: int
    rightIndent: int
    
    @classmethod
    def from_config(cls, style_name: str, sync_json: bool = True) -> 'PDFStyleConfig':
        """Create style config from JSON configuration."""
        style_config = get_style_value(f'pdf_settings.styles.{style_name}', None, sync_json)
        
        if style_config is None:
            raise ConfigurationError(f"Style '{style_name}' not found in configuration. Please configure this style in styles.json")
        
        # Validate required fields
        if 'fontSize' not in style_config:
            raise ConfigurationError(f"fontSize not found for style '{style_name}' in configuration")
        if 'textColor' not in style_config:
            raise ConfigurationError(f"textColor not found for style '{style_name}' in configuration")
        
        return cls(
            fontSize=style_config['fontSize'],
            leading=style_config.get('leading'),
            textColor=style_config['textColor'],
            alignment=TextAlignment(style_config.get('alignment', TA_LEFT)),
            spaceAfter=style_config.get('spaceAfter', 6),
            spaceBefore=style_config.get('spaceBefore', 0),
            leftIndent=style_config.get('leftIndent', 0),
            rightIndent=style_config.get('rightIndent', 0)
        )


@dataclass
class TableStyleConfig:
    """Configuration for table styling."""
    font_size: int
    header_font_size: int
    title_font_size: int
    padding: int
    max_rows_per_table: int
    max_words_per_line: int
    
    @classmethod
    def from_config(cls, sync_json: bool = True) -> 'TableStyleConfig':
        """Create table style config from JSON configuration."""
        try:
            table_config = get_style_value('pdf_settings.table_style', {}, sync_json)
            
            return cls(
                font_size=table_config.get('font_size', 10),
                header_font_size=table_config.get('header_font_size', 11),
                title_font_size=table_config.get('title_font_size', 12),
                padding=table_config.get('padding', 8),
                max_rows_per_table=table_config.get('max_rows_per_table', 20),
                max_words_per_line=table_config.get('max_words_per_line', 6)
            )
        except ConfigurationError:
            # Return sensible defaults
            return cls(
                font_size=10,
                header_font_size=11,
                title_font_size=12,
                padding=8,
                max_rows_per_table=20,
                max_words_per_line=6
            )


@dataclass
class ImageSettings:
    """Configuration for image handling in PDFs."""
    max_width_inches: float
    default_width_inches: float
    max_height_inches: float
    quality: int
    
    @classmethod
    def from_config(cls, sync_json: bool = True) -> 'ImageSettings':
        """Create image settings from JSON configuration."""
        try:
            image_config = get_style_value('pdf.images', {}, sync_json)
            
            return cls(
                max_width_inches=image_config.get('max_width_inches', 7.0),
                default_width_inches=image_config.get('default_width_inches', 5.0),
                max_height_inches=image_config.get('max_height_inches', 8.0),
                quality=image_config.get('quality', 300)
            )
        except ConfigurationError:
            return cls(
                max_width_inches=7.0,
                default_width_inches=5.0,
                max_height_inches=8.0,
                quality=300
            )


class PDFStyleManager:
    """Manages PDF styling configuration and provides style creation utilities."""
    
    def __init__(self, sync_json: bool = True):
        """Initialize with configuration from JSON files."""
        self._sync_json = sync_json
        self._load_configuration()
    
    def _load_configuration(self):
        """Load all style configurations from JSON."""
        self.margins = PDFMargins.from_config(self._sync_json)
        self.watermark = WatermarkConfig.from_config(self._sync_json)
        self.table_config = TableStyleConfig.from_config(self._sync_json)
        self.image_settings = ImageSettings.from_config(self._sync_json)
        
        # Load page size
        try:
            page_size_name = get_style_value('pdf.page_size', 'letter', self._sync_json)
            self.page_size = letter if page_size_name.lower() == 'letter' else A4
        except ConfigurationError:
            self.page_size = letter
    
    def get_table_style_config(self) -> TableStyleConfig:
        """Get table style configuration."""
        return self.table_config
    
    def create_paragraph_style(self, style_name: str, base_style_name: str = 'Normal') -> ParagraphStyle:
        """Create a ReportLab ParagraphStyle from JSON configuration.
        
        Args:
            style_name: Name of the style in the JSON config
            base_style_name: Base style to inherit from
            
        Returns:
            Configured ParagraphStyle
        """
        config = PDFStyleConfig.from_config(style_name, self._sync_json)
        base_styles = getSampleStyleSheet()
        base_style = base_styles.get(base_style_name, base_styles['Normal'])
        
        return ParagraphStyle(
            name=style_name,
            parent=base_style,
            fontSize=config.fontSize,
            leading=config.leading or config.fontSize * 1.2,
            textColor=self._get_safe_color(config.textColor),
            alignment=config.alignment.value,
            spaceAfter=config.spaceAfter,
            spaceBefore=config.spaceBefore,
            leftIndent=config.leftIndent,
            rightIndent=config.rightIndent
        )
    
    def _get_safe_color(self, color_input, fallback: str = '#000000'):
        """Get safe ReportLab color from color input (string or RGB list)."""
        try:
            if isinstance(color_input, list) and len(color_input) == 3:
                # Convert RGB list [r, g, b] to ReportLab color
                r, g, b = color_input
                return colors.Color(r/255.0, g/255.0, b/255.0)
            elif isinstance(color_input, str):
                return convert_to_reportlab_color(color_input)
            else:
                raise ValueError(f"Invalid color format: {color_input}")
        except Exception:
            raise ValueError(f"Failed to convert color: {color_input}. Colors must be either hex strings (e.g., '#FF0000') or RGB lists (e.g., [255, 0, 0])")
    
    def get_safe_color(self, color_input, fallback: str = '#000000'):
        """Public method to get safe ReportLab color."""
        return self._get_safe_color(color_input, fallback)


def create_pdf_styles(sync_json: bool = True) -> Dict[str, Any]:
    """Create complete PDF styling configuration.
    
    Args:
        sync_json: Whether to reload configuration from disk
        
    Returns:
        Dictionary containing all styling configuration
    """
    style_manager = PDFStyleManager(sync_json)
    
    # Create paragraph styles - NO FALLBACKS
    paragraph_styles = {}
    required_styles = ['heading1', 'heading2', 'heading3', 'normal', 'caption']
    
    for style_name in required_styles:
        if style_name == 'heading1':
            base = 'Heading1'
        elif style_name == 'heading2':
            base = 'Heading2'
        elif style_name == 'heading3':
            base = 'Heading3'
        else:
            base = 'Normal'
        
        paragraph_styles[style_name] = style_manager.create_paragraph_style(style_name, base)
    
    return {
        'manager': style_manager,
        'page_size': style_manager.page_size,
        'margins': style_manager.margins,
        'paragraph_styles': paragraph_styles,
        'table_config': style_manager.table_config,
        'image_settings': style_manager.image_settings,
        'watermark': style_manager.watermark
    }
