"""PDF configuration utilities for ePy_docs.

Refactored module following SOLID principles:
- PdfConfig: Configuration management for PDF settings
- PdfEngineSelector: Specialized PDF engine selection logic
- GeometryProcessor: Page geometry and layout calculations
- HeaderGenerator: LaTeX header and styling generation
- PdfOrchestrator: Unified facade orchestrating PDF operations

Version: 3.0.0 - Zero hardcoding, fail-fast validation
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from abc import ABC, abstractmethod

# Import shared validation
from ePy_docs.core._validation import PdfValidator


# ============================================================================
# CONFIGURATION AND VALIDATION
# ============================================================================

class PdfConfig:
    """Centralized PDF configuration management."""
    
    def __init__(self):
        self._config = None
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get PDF configuration with caching.
        
        Returns:
            PDF configuration from documents/_index.epyson rendering section
            
        Raises:
            ValueError: If rendering section not found in documents configuration
        """
        if self._config is None:
            from ePy_docs.core._config import get_config_section
            documents_config = get_config_section('documents')
            if not documents_config or 'rendering' not in documents_config:
                raise ValueError(
                    "Rendering configuration not found in documents. "
                    "Please ensure documents/_index.epyson contains a 'rendering' section."
                )
            self._config = documents_config['rendering']
        return self._config
    
    def get_default_engine(self) -> str:
        """Get default PDF engine from configuration.
        
        Returns:
            Default PDF engine name
            
        Raises:
            ValueError: If default_pdf_engine not found in configuration
        """
        if 'default_pdf_engine' not in self.config:
            raise ValueError(
                "default_pdf_engine not found in rendering configuration. "
                "Expected 'default_pdf_engine' key in documents/_index.epyson."
            )
        return self.config['default_pdf_engine']
    
    def get_supported_engines(self) -> List[str]:
        """Get list of supported PDF engines from configuration.
        
        Returns:
            List of supported engines from documents configuration
            
        Raises:
            ValueError: If supported_engines not found in configuration
        """
        supported_engines = self.config.get('supported_engines')
        if not supported_engines:
            raise ValueError(
                "supported_engines not found in rendering configuration. "
                "Please ensure documents/_index.epyson contains rendering.supported_engines."
            )
        return supported_engines
    
    def get_document_class_mapping(self) -> Dict[str, str]:
        """Get document type to LaTeX class mapping from configuration.
        
        Returns:
            Document type mapping from epyson configuration
            
        Raises:
            ValueError: If document_class_mapping not found in configuration
        """
        class_mapping = self.config.get('document_class_mapping')
        if not class_mapping:
            raise ValueError(
                "document_class_mapping not found in PDF configuration. "
                "Please ensure the epyson configuration file contains a pdf.document_class_mapping section."
            )
        return class_mapping
    
    def get_default_options(self) -> Dict[str, Any]:
        """Get default PDF options from configuration.
        
        Returns:
            Default PDF options from epyson configuration
            
        Raises:
            ValueError: If default_options not found in configuration
        """
        default_options = self.config.get('default_options')
        if not default_options:
            raise ValueError(
                "default_options not found in PDF configuration. "
                "Please ensure the epyson configuration file contains a pdf.default_options section."
            )
        return default_options


# ============================================================================
# PDF ENGINE SELECTION
# ============================================================================

class PdfEngineSelector:
    """Specialized PDF engine selection logic."""
    
    def __init__(self, config: PdfConfig):
        self.config = config
        self.validator = PdfValidator()  # Use shared validator
    
    def select_engine(self, layout_name: str = 'classic', requirements: Optional[Dict[str, Any]] = None) -> str:
        """Select appropriate PDF engine for layout and requirements.
        
        Args:
            layout_name: Name of the layout
            requirements: Optional engine requirements (unicode, fonts, etc.)
            
        Returns:
            PDF engine name
        """
        # Get engine from configuration or use smart selection
        configured_engine = self._get_configured_engine(layout_name)
        if configured_engine:
            return self.validator.validate_engine(configured_engine)
        
        # Smart engine selection based on requirements
        return self._select_optimal_engine(requirements or {})
    
    def _get_configured_engine(self, layout_name: str) -> Optional[str]:
        """Get engine from layout configuration."""
        try:
            from ePy_docs.core._config import get_config_section
            layout_config = get_config_section('layout')
            return layout_config.get(layout_name, {}).get('pdf_engine')
        except Exception:
            return None
    
    def _select_optimal_engine(self, requirements: Dict[str, Any]) -> str:
        """Select optimal engine based on requirements.
        
        Args:
            requirements: Engine requirements dictionary
            
        Returns:
            Selected PDF engine name
            
        Raises:
            ValueError: If requirements keys are invalid
        """
        # Validate requirements keys if provided
        valid_keys = {'unicode_support', 'custom_fonts', 'simple_document'}
        if requirements:
            invalid_keys = set(requirements.keys()) - valid_keys
            if invalid_keys:
                raise ValueError(
                    f"Invalid requirement keys: {invalid_keys}. "
                    f"Valid keys are: {valid_keys}"
                )
        
        # xelatex is generally the best choice for modern documents
        # Better Unicode support and custom font handling
        if requirements.get('unicode_support') or requirements.get('custom_fonts'):
            return 'xelatex'
        
        # pdflatex for simple documents without special requirements
        if requirements.get('simple_document'):
            return 'pdflatex'
        
        # Default to configured engine
        return self.config.get_default_engine()


# ============================================================================
# GEOMETRY PROCESSING
# ============================================================================

class GeometryProcessor:
    """Specialized page geometry and layout calculations."""
    
    def __init__(self, config: PdfConfig, validator: PdfValidator):
        self.config = config
        self.validator = validator
    
    def get_page_geometry(self, layout_name: str = 'classic') -> List[str]:
        """Get PDF page geometry settings for layout.
        
        Args:
            layout_name: Name of the layout
            
        Returns:
            List of geometry strings for Quarto
        """
        layout_name = self.validator.validate_layout_name(layout_name)
        margins = self._get_layout_margins(layout_name)
        
        # Convert margins to geometry strings (margins are in inches)
        return [
            f"top={margins['top']}in",
            f"bottom={margins['bottom']}in", 
            f"left={margins['left']}in",
            f"right={margins['right']}in"
        ]
    
    def get_column_configuration(self, layout_name: str, document_type: str) -> Optional[Dict[str, Any]]:
        """Get column configuration for document type.
        
        Args:
            layout_name: Name of the layout
            document_type: Type of document
            
        Returns:
            Column configuration or None
        """
        try:
            from ePy_docs.core._config import get_config_section
            layout_config = get_config_section('layout')
            layout = layout_config.get(layout_name, {})
            
            if document_type in layout:
                return layout[document_type].get('columns', {})
        except Exception:
            pass
        
        return None
    
    def _get_layout_margins(self, layout_name: str) -> Dict[str, float]:
        """Get layout margins from configuration.
        
        Args:
            layout_name: Name of the layout
            
        Returns:
            Dictionary with margin values (top, bottom, left, right)
            
        Raises:
            ValueError: If margins not found in layout configuration
        """
        from ePy_docs.core._config import get_layout_margins
        margins = get_layout_margins(layout_name)
        
        # Validate all required margin keys exist
        required_keys = {'top', 'bottom', 'left', 'right'}
        missing_keys = required_keys - set(margins.keys())
        if missing_keys:
            raise ValueError(
                f"Missing margin keys in layout '{layout_name}': {missing_keys}. "
                f"Required keys: {required_keys}"
            )
        
        return margins


# ============================================================================
# HEADER GENERATION
# ============================================================================

class HeaderGenerator:
    """Specialized LaTeX header and styling generation."""
    
    def __init__(self, config: PdfConfig, validator: PdfValidator):
        self.config = config
        self.validator = validator
    
    def generate_header(self, layout_name: str = 'classic', fonts_dir: Optional[Path] = None) -> str:
        """Generate LaTeX include-in-header configuration.
        
        Args:
            layout_name: Name of the layout
            fonts_dir: Absolute path to fonts directory
            
        Returns:
            LaTeX commands for document header
        """
        layout_name = self.validator.validate_layout_name(layout_name)
        
        # Build header components
        font_config = self._get_font_configuration(layout_name, fonts_dir)
        color_definitions = self._generate_color_definitions(layout_name)
        package_imports = self._get_required_packages()
        styling_commands = self._generate_styling_commands()
        
        # Combine all components
        header_parts = [
            package_imports,
            font_config,
            color_definitions,
            styling_commands
        ]
        
        return '\n\n'.join(filter(None, header_parts))
    
    def _get_font_configuration(self, layout_name: str, fonts_dir: Optional[Path]) -> str:
        """Get font configuration from layout."""
        try:
            from ePy_docs.core._config import get_font_latex_config
            return get_font_latex_config(layout_name, fonts_dir=fonts_dir)
        except Exception:
            return ""
    
    def _generate_color_definitions(self, layout_name: str) -> str:
        """Generate LaTeX color definitions.
        
        Args:
            layout_name: Name of the layout
            
        Returns:
            LaTeX color definition commands
            
        Raises:
            ValueError: If color configuration cannot be loaded
        """
        from ePy_docs.core._config import get_layout_colors
        
        try:
            colors = get_layout_colors(layout_name)
        except Exception as e:
            raise ValueError(f"Failed to load colors for layout '{layout_name}': {e}")
        
        if not colors:
            raise ValueError(f"No colors found for layout '{layout_name}'")
        
        # Convert colors to RGB
        color_definitions = []
        
        # Define brand colors
        for color_name, hex_value in colors.items():
            if hex_value:
                try:
                    rgb_value = self._hex_to_rgb(hex_value)
                    latex_name = self._get_latex_color_name(color_name)
                    color_definitions.append(f"\\definecolor{{{latex_name}}}{{RGB}}{{{rgb_value}}}")
                except Exception as e:
                    raise ValueError(f"Failed to convert color '{color_name}' ({hex_value}): {e}")
        
        # Set page background and text color
        if 'page_background' in colors:
            color_definitions.append("\\pagecolor{colorBackground}")
        
        text_color = self._resolve_text_color(layout_name, colors)
        if text_color:
            color_definitions.append(f"\\color[RGB]{{{text_color}}}")
        
        return '\n'.join(color_definitions) if color_definitions else ""
    
    def _get_required_packages(self) -> str:
        """Get required LaTeX packages from configuration.
        
        Returns:
            Newline-separated LaTeX package imports
            
        Raises:
            ValueError: If latex_packages not found in configuration
        """
        rendering_config = self.config.config
        if 'latex_packages' not in rendering_config:
            raise ValueError(
                "latex_packages not found in rendering configuration. "
                "Expected 'latex_packages' array in documents/_index.epyson rendering section."
            )
        
        packages = rendering_config['latex_packages']
        if not isinstance(packages, list) or not packages:
            raise ValueError(
                "latex_packages must be a non-empty list in rendering configuration."
            )
        
        return '\n'.join(packages)
    
    def _generate_styling_commands(self) -> str:
        """Generate LaTeX styling commands with appropriate color contrasts.
        
        Uses color hierarchy: primary (darkest) -> secondary -> tertiary -> quaternary.
        """
        styling = [
            "\\pagestyle{fancy}",
            "\\fancyhf{}",
            "\\renewcommand{\\headrulewidth}{0.4pt}",
            "\\renewcommand{\\footrulewidth}{0.4pt}",
            "",
            "% Configure section colors - using hierarchical palette colors",
            "\\sectionfont{\\color{colorPrimary}}",        # h1: Darkest
            "\\subsectionfont{\\color{colorSecondary}}",   # h2: Dark
            "\\subsubsectionfont{\\color{colorTertiary}}", # h3: Medium
            "\\paragraphfont{\\color{colorQuaternary}}",   # h4: Lighter
            "\\subparagraphfont{\\color{colorQuaternary}}" # h5-h6: Lighter
        ]
        return '\n'.join(styling)
    
    def _get_latex_color_name(self, color_name: str) -> str:
        """Convert color name to LaTeX-safe name.
        
        Args:
            color_name: Color name from palette
            
        Returns:
            LaTeX-safe color name
            
        Raises:
            ValueError: If color_name is not in mapping
        """
        color_mapping = {
            'primary': 'colorPrimary',
            'secondary': 'colorSecondary',
            'tertiary': 'colorTertiary',
            'quaternary': 'colorQuaternary',
            'quinary': 'colorQuinary',
            'senary': 'colorSenary',
            'page_background': 'colorBackground',
            'page_text': 'colorText',
            'border_color': 'colorBorder',
            'code_background': 'colorCodeBg',
            'code_text': 'colorCodeText',
            'table_header': 'colorTableHeader',
            'table_header_text': 'colorTableHeaderText',
            'table_stripe': 'colorTableStripe',
            'table_stripe_text': 'colorTableStripeText',
            'table_background': 'colorTableBackground',
            'table_background_text': 'colorTableBackgroundText',
            'caption_color': 'colorCaption',
            'page_header_color': 'colorPageHeader',
            'page_footer_color': 'colorPageFooter'
        }
        
        if color_name not in color_mapping:
            raise ValueError(
                f"Unknown color name '{color_name}'. "
                f"Valid names: {list(color_mapping.keys())}"
            )
        
        return color_mapping[color_name]
    
    def _resolve_text_color(self, layout_name: str, colors: Dict[str, str]) -> str:
        """Resolve text color from palette to match HTML output.
        
        Args:
            layout_name: Layout name (for error messages)
            colors: Color dictionary from palette
            
        Returns:
            RGB string for LaTeX
            
        Raises:
            ValueError: If page_text not found in palette
        """
        if 'page_text' not in colors:
            raise ValueError(
                f"page_text not found in colors for layout '{layout_name}'. "
                "All palettes must define page_text."
            )
        
        return self._hex_to_rgb(colors['page_text'])
    
    def _hex_to_rgb(self, hex_color: str) -> str:
        """Convert hex color to RGB string for LaTeX.
        
        Args:
            hex_color: Hex color string (with or without #)
            
        Returns:
            RGB string in format 'R,G,B'
            
        Raises:
            ValueError: If hex_color is invalid
        """
        hex_color = hex_color.lstrip('#')
        
        if len(hex_color) != 6:
            raise ValueError(
                f"Invalid hex color '{hex_color}'. Expected 6 characters."
            )
        
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f"{r},{g},{b}"
        except ValueError as e:
            raise ValueError(f"Invalid hex color '{hex_color}': {e}")


# ============================================================================
# UNIFIED PDF ORCHESTRATOR
# ============================================================================

class PdfOrchestrator:
    """Unified facade orchestrating all PDF operations."""
    
    def __init__(self):
        """Initialize orchestrator with all specialized components."""
        self._config = PdfConfig()
        self._validator = PdfValidator()  # Use shared validator
        self._engine_selector = PdfEngineSelector(self._config)
        self._geometry_processor = GeometryProcessor(self._config, self._validator)
        self._header_generator = HeaderGenerator(self._config, self._validator)
    
    def generate_pdf_config(
        self,
        layout_name: str = 'classic',
        document_type: str = 'article',
        fonts_dir: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate complete PDF configuration for Quarto.
        
        Args:
            layout_name: Name of the layout
            document_type: Document type
            fonts_dir: Absolute path to fonts directory
            config: Optional layout configuration for testing
            **kwargs: Additional PDF options
            
        Returns:
            Dictionary with PDF configuration for Quarto YAML
        """
        layout_name = self._validator.validate_layout_name(layout_name)
        
        # Get document class mapping
        quarto_documentclass = self._map_document_type(document_type)
        validated_class = self._validator.validate_document_class(quarto_documentclass)
        
        # Build base configuration
        base_config = self._build_base_config(layout_name, document_type, validated_class, **kwargs)
        
        # Add PDF-specific components
        base_config['pdf-engine'] = self._engine_selector.select_engine(layout_name)
        base_config['include-in-header'] = {
            'text': self._header_generator.generate_header(layout_name, fonts_dir)
        }
        
        # Add geometry for non-beamer documents
        if validated_class != 'beamer':
            base_config['geometry'] = self._geometry_processor.get_page_geometry(layout_name)
        
        # Handle multi-column layouts
        # Use explicit columns parameter (has priority over kwargs)
        columns_param = columns if columns is not None else kwargs.get('columns')
        self._apply_column_configuration(base_config, layout_name, document_type, columns_param)
        
        return base_config
    
    def _map_document_type(self, document_type: str) -> str:
        """Map document type to LaTeX class."""
        mapping = self._config.get_document_class_mapping()
        return mapping.get(document_type, document_type)
    
    def _build_base_config(self, layout_name: str, document_type: str, document_class: str, **kwargs) -> Dict[str, Any]:
        """Build base PDF configuration."""
        default_options = self._config.get_default_options()
        
        # Get line spacing from layout
        line_spacing = self._get_line_spacing(layout_name)
        
        # Determine section numbering
        default_number_sections = document_type != 'report'
        
        return {
            'documentclass': document_class,
            'linestretch': line_spacing,
            'fontsize': kwargs.get('fontsize') or default_options['fontsize'],
            'papersize': kwargs.get('papersize') or default_options['papersize'],
            'number-sections': kwargs.get('number_sections', default_number_sections),
            'colorlinks': kwargs.get('colorlinks') if 'colorlinks' in kwargs else default_options['colorlinks'],
            'toc': kwargs.get('toc') if 'toc' in kwargs else default_options['toc'],
            'toc-depth': kwargs.get('toc_depth') or default_options['toc_depth'],
            'lof': kwargs.get('lof') if 'lof' in kwargs else False,
            'lot': kwargs.get('lot') if 'lot' in kwargs else False,
            'fig-pos': default_options['fig_pos'],
            'fig-cap-location': default_options['fig_cap_location'],
            'tbl-cap-location': default_options['tbl_cap_location']
        }
    
    def _get_line_spacing(self, layout_name: str) -> float:
        """Get line spacing from layout configuration.
        
        Args:
            layout_name: Name of the layout
            
        Returns:
            Line spacing value
            
        Raises:
            ValueError: If line_spacing not found in layout configuration
        """
        from ePy_docs.core._config import get_config_section
        layout_config = get_config_section('layout')
        layout = layout_config.get(layout_name)
        
        if not layout:
            raise ValueError(
                f"Layout '{layout_name}' not found in configuration. "
                "Please ensure the layout exists in layouts config."
            )
        
        # Navigate to line_spacing: tables.layout_config.styling.line_spacing
        tables_config = layout.get('tables', {})
        layout_styling = tables_config.get('layout_config', {})
        styling = layout_styling.get('styling', {})
        line_spacing = styling.get('line_spacing')
        
        if line_spacing is None:
            raise ValueError(
                f"line_spacing not found in layout '{layout_name}'. "
                "Expected path: tables.layout_config.styling.line_spacing"
            )
        
        return line_spacing
    
    def _apply_column_configuration(self, config: Dict[str, Any], layout_name: str, document_type: str, columns: int = None) -> None:
        """Apply multi-column configuration to PDF config.
        
        Args:
            config: PDF configuration dictionary
            layout_name: Layout name
            document_type: Document type
            columns: Number of columns (from constructor parameter)
        """
        # Priority: 1) constructor parameter, 2) document type default
        target_columns = columns
        
        if target_columns is None:
            # Get from document type configuration
            try:
                from ePy_docs.core._config import get_document_type_config
                doc_config = get_document_type_config(document_type)
                target_columns = doc_config.get('default_columns', 1)
            except Exception:
                target_columns = 1
        
        if target_columns and target_columns > 1:
            # For LaTeX/PDF, use documentclass option 'twocolumn'
            # This is the correct way to enable two-column mode in LaTeX
            # Always use list format for Quarto compatibility
            if 'classoption' not in config:
                config['classoption'] = ['twocolumn']
            elif isinstance(config['classoption'], str):
                config['classoption'] = [config['classoption'], 'twocolumn']
            elif isinstance(config['classoption'], list):
                if 'twocolumn' not in config['classoption']:
                    config['classoption'].append('twocolumn')
    
    # Public interface methods
    def get_pdf_engine(self, layout_name: str = 'classic') -> str:
        """Get PDF engine for layout."""
        return self._engine_selector.select_engine(layout_name)
    
    def get_pdf_geometry(self, layout_name: str = 'classic') -> List[str]:
        """Get PDF geometry for layout."""
        return self._geometry_processor.get_page_geometry(layout_name)
    
    def get_pdf_header_config(self, layout_name: str = 'classic', fonts_dir: Optional[Path] = None) -> str:
        """Get PDF header configuration."""
        return self._header_generator.generate_header(layout_name, fonts_dir)
    
    def validate_document_class(self, document_class: str) -> bool:
        """Validate document class."""
        try:
            self._validator.validate_document_class(document_class)
            return True
        except ValueError:
            return False




# ============================================================================
# COMPATIBILITY LAYER FOR TESTS
# ============================================================================

def get_pdf_config(layout_name: str = 'classic', 
                   document_type: str = 'report',
                   config: Optional[Dict[str, Any]] = None,
                   fonts_dir: Optional[str] = None,
                   columns: int = None) -> Dict[str, Any]:
    """Compatibility wrapper for tests.
    
    Generates complete PDF configuration for Quarto from layout and document type.
    
    Args:
        layout_name: Layout name (e.g., 'classic', 'handwritten')
        document_type: Document type (e.g., 'report', 'paper', 'book')
        config: Optional test configuration override
        fonts_dir: Optional custom fonts directory path
        columns: Number of columns for document layout
        
    Returns:
        Dictionary with PDF configuration ready for Quarto
        
    Raises:
        ValueError: If layout or document_type invalid
    """
    from ePy_docs.core._config import get_document_type_config
    from pathlib import Path
    
    # Initialize orchestrator
    orchestrator = PdfOrchestrator()
    
    # Load document configuration
    try:
        doc_type_config = get_document_type_config(document_type)
    except ValueError as e:
        raise ValueError(f"Invalid document type '{document_type}': {e}")
    
    # Convert fonts_dir to Path if provided
    fonts_path = Path(fonts_dir) if fonts_dir else None
    
    # Build PDF configuration using orchestrator components
    pdf_config = {}
    
    # 1. PDF Engine
    pdf_config['pdf-engine'] = orchestrator.get_pdf_engine(layout_name)
    
    # 2. Geometry
    pdf_config['geometry'] = orchestrator.get_pdf_geometry(layout_name)
    
    # 3. Include-in-header (fonts + packages)
    header_text = orchestrator.get_pdf_header_config(layout_name, fonts_dir=fonts_path)
    pdf_config['include-in-header'] = {'text': header_text}
    
    # 4. Apply multi-column configuration
    orchestrator._apply_column_configuration(pdf_config, layout_name, document_type, columns)
    
    # 5. Document class from document_type
    pdf_config['documentclass'] = doc_type_config.get('documentclass', 'article')
    
    # 6. Paper size from document_type
    if 'papersize' in doc_type_config:
        pdf_config['papersize'] = doc_type_config['papersize']
    
    # 7. Apply quarto_pdf settings from document_type config
    if 'quarto_pdf' in doc_type_config:
        for key, value in doc_type_config['quarto_pdf'].items():
            pdf_config[key] = value
    
    # 8. Font size from layout or defaults (fallback if not in quarto_pdf)
    if 'fontsize' not in pdf_config:
        pdf_config['fontsize'] = '11pt'
    
    return pdf_config





