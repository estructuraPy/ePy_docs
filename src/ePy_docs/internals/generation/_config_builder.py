"""Quarto Configuration Builder - Unified metadata construction.

This module centralizes ALL Quarto metadata construction for both HTML and PDF.
It eliminates the fragmentation between generate_quarto_config() and PDFRenderer.generate_metadata().

Constitutional Principle: ONE source of truth for Quarto configuration.
"""

from typing import Dict, Any, List, Optional
import os


class QuartoConfigBuilder:
    """Builds complete Quarto metadata from layout configuration.
    
    Responsibilities:
    1. Load base configuration from JSON files (via generate_quarto_config)
    2. Add HTML-specific metadata (CSS)
    3. Add PDF-specific metadata (LaTeX fonts, header-includes)
    4. Merge all configs into single metadata dict
    """
    
    def __init__(self, document_type: str = "report", layout_name: str = None):
        """Initialize config builder.
        
        Args:
            document_type: Type of document ("report" or "paper")
            layout_name: Layout name. If None, uses current layout.
        """
        self.document_type = document_type
        self.layout_name = layout_name or self._get_current_layout()
    
    def _get_current_layout(self) -> str:
        """Get current layout name."""
        from ePy_docs.internals.styling._pages import get_current_layout
        return get_current_layout()
    
    def build_complete_metadata(self, title: str, author: str) -> Dict[str, Any]:
        """Build complete Quarto metadata with ALL configurations.
        
        Args:
            title: Document title
            author: Document author
            
        Returns:
            Complete metadata dict ready for QMD YAML header
        """
        # 1. Get base configuration from existing function
        base_config = self._get_base_config()
        
        # 2. Update title and author
        if 'book' in base_config:
            base_config['book']['title'] = title
            base_config['book']['author'] = author
        else:
            base_config['title'] = title
            base_config['author'] = author
        
        # 3. Add HTML-specific metadata (CSS)
        html_metadata = self._build_html_metadata()
        if 'format' not in base_config:
            base_config['format'] = {}
        if 'html' not in base_config['format']:
            base_config['format']['html'] = {}
        base_config['format']['html'].update(html_metadata)
        
        # 4. Add PDF-specific metadata (LaTeX fonts)
        pdf_metadata = self._build_pdf_metadata()
        if 'pdf' not in base_config['format']:
            base_config['format']['pdf'] = {}
        
        # Update PDF config (this replaces header-includes with fonts)
        base_config['format']['pdf'].update(pdf_metadata)
        
        # Remove include-in-header if we have header-includes (header-includes takes precedence)
        if 'header-includes' in base_config['format']['pdf'] and 'include-in-header' in base_config['format']['pdf']:
            del base_config['format']['pdf']['include-in-header']
        
        return base_config
    
    def _get_base_config(self) -> Dict[str, Any]:
        """Get base configuration from generate_quarto_config."""
        from ePy_docs.internals.styling._styler import generate_quarto_config
        return generate_quarto_config(
            layout_name=self.layout_name,
            document_type=self.document_type
        )
    
    def _build_html_metadata(self) -> Dict[str, Any]:
        """Build HTML-specific metadata.
        
        Returns:
            Dict with HTML config (css reference, etc.)
        """
        # HTML already has css: styles.css in base config
        # Just ensure it's set correctly
        return {
            'css': 'styles.css'
        }
    
    def _build_pdf_metadata(self) -> Dict[str, Any]:
        """Build PDF-specific metadata from base config.
        
        Returns:
            Dict with PDF config (uses original include-in-header from styler)
        """
        # Get base config that already has all PDF styling configured
        from ePy_docs.internals.styling._styler import generate_quarto_config
        base_config = generate_quarto_config(layout_name=self.layout_name, document_type=self.document_type)
        
        # Extract and return PDF section as-is (no modifications)
        # This preserves the original include-in-header with font config
        pdf_base = base_config.get('format', {}).get('pdf', {})
        
        return pdf_base

    
    def _get_latex_font_config(self) -> str:
        """Get LaTeX font configuration from _latex_builder.
        
        Returns:
            LaTeX fontspec configuration string
        """
        from ePy_docs.internals.styling._latex_builder import _get_font_latex_config
        from ePy_docs.internals.styling._layout import LayoutCoordinator
        
        # Load layout configuration to get font family
        coordinator = LayoutCoordinator()
        layout_config = coordinator.coordinate_layout_style(self.layout_name)
        
        # Get font family from layout typography
        typography_data = layout_config.typography.get('typography', {})
        normal_font_config = typography_data.get('normal', {})
        h1_font_config = typography_data.get('h1', {})
        font_family = normal_font_config.get('family', h1_font_config.get('family', 'sans_modern'))
        
        # Generate LaTeX font configuration
        return _get_font_latex_config(font_family)
    
    def _get_pdf_style_metadata(self) -> Dict[str, Any]:
        """Get PDF styling metadata (colors, spacing, etc.) from PDFRenderer logic.
        
        This extracts the non-font parts of PDFRenderer.generate_metadata().
        """
        from ePy_docs.internals.styling._pages import get_pages_config, _load_component_config
        
        page_config = get_pages_config()
        if not page_config:
            return {}
        
        # Load report/paper configuration
        if self.document_type == "paper":
            realm_config = _load_component_config('paper')
        else:
            realm_config = _load_component_config('report')
        
        if not realm_config:
            return {}
        
        # Get layout margins
        default_margins = {'top': 1.0, 'bottom': 1.0, 'left': 1.0, 'right': 1.0}
        layouts = realm_config.get('layouts', {})
        current_layout = layouts.get(self.layout_name, {'margins': default_margins})
        layout_margins = current_layout.get('margins', default_margins)
        
        # Get styles
        layout_data = page_config.get('layouts', {}).get(self.layout_name, {})
        styles = layout_data.get('styles', {})
        
        if not styles:
            return {}
        
        heading1 = styles.get('heading1', {})
        heading2 = styles.get('heading2', {})
        heading3 = styles.get('heading3', {})
        normal = styles.get('normal', {})
        
        # Convert RGB colors to hex
        def rgb_to_hex(rgb_list):
            return f"#{rgb_list[0]:02x}{rgb_list[1]:02x}{rgb_list[2]:02x}"
        
        h1_color = rgb_to_hex(heading1.get('textColor', [0, 0, 0]))
        h2_color = rgb_to_hex(heading2.get('textColor', [0, 0, 0]))
        h3_color = rgb_to_hex(heading3.get('textColor', [0, 0, 0]))
        
        # Create LaTeX header for styling
        latex_header = [
            "\\usepackage{xcolor}",
            "\\usepackage{float}",
            "\\usepackage{caption}",
            "\\usepackage{subcaption}",
            f"\\definecolor{{heading1color}}{{HTML}}{{{h1_color[1:]}}}",
            f"\\definecolor{{heading2color}}{{HTML}}{{{h2_color[1:]}}}",
            f"\\definecolor{{heading3color}}{{HTML}}{{{h3_color[1:]}}}",
            "\\makeatletter",
            f"\\renewcommand{{\\section}}{{\\@startsection{{section}}{{1}}{{\\z@}}{{{heading1.get('spaceBefore', 12)}pt}}{{{heading1.get('spaceAfter', 6)}pt}}{{\\normalfont\\fontsize{{{heading1.get('fontSize', 16)}}}{{{heading1.get('leading', 20)}}}\\selectfont\\bfseries\\color{{heading1color}}}}}}",
            f"\\renewcommand{{\\subsection}}{{\\@startsection{{subsection}}{{2}}{{\\z@}}{{{heading2.get('spaceBefore', 10)}pt}}{{{heading2.get('spaceAfter', 5)}pt}}{{\\normalfont\\fontsize{{{heading2.get('fontSize', 14)}}}{{{heading2.get('leading', 18)}}}\\selectfont\\bfseries\\color{{heading2color}}}}}}",
            f"\\renewcommand{{\\subsubsection}}{{\\@startsection{{subsubsection}}{{3}}{{\\z@}}{{{heading3.get('spaceBefore', 8)}pt}}{{{heading3.get('spaceAfter', 4)}pt}}{{\\normalfont\\fontsize{{{heading3.get('fontSize', 12)}}}{{{heading3.get('leading', 16)}}}\\selectfont\\bfseries\\color{{heading3color}}}}}}",
            "\\makeatother",
            "\\captionsetup[figure]{position=bottom,labelfont=bf,textfont=normal}",
            "\\floatplacement{figure}{H}"
        ]
        
        # Get page size and documentclass
        format_config = page_config.get('format', {})
        common_config = format_config.get('common', {})
        pdf_config = format_config.get('pdf', {})
        merged_config = {**common_config, **pdf_config}
        
        return {
            'documentclass': merged_config.get('documentclass', 'article'),
            'geometry': [
                f'top={layout_margins["top"]}in',
                f'bottom={layout_margins["bottom"]}in',
                f'left={layout_margins["left"]}in',
                f'right={layout_margins["right"]}in'
            ],
            'papersize': merged_config.get('papersize', 'letter'),
            'toc': merged_config.get('toc', True),
            'toc-depth': merged_config.get('toc-depth', 3),
            'number-sections': merged_config.get('number-sections', True),
            'colorlinks': merged_config.get('colorlinks', True),
            'fontsize': f"{normal.get('fontSize', 12)}pt",
            'header-includes': latex_header,
            'fig-cap-location': merged_config.get('fig-cap-location', 'bottom'),
            'fig-pos': merged_config.get('fig-pos', 'H')
        }
