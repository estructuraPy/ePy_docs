"""Document processing and column width calculation utilities for ePy_docs.

Unified module providing:
- Document type detection, conversion routing, and batch processing
- Column width calculations for multi-column layouts
- Table and figure width optimization
- Support for various input formats (QMD, Markdown, Word) to multiple outputs
"""

import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class ColumnWidthCalculator:
    """Optimized column width calculator for multi-column document layouts.
    
    Handles width calculations for tables and figures based on document type,
    layout columns, and requested column span with intelligent caching.
    """
    
    def __init__(self):
        """Initialize calculator with configuration caching."""
        self._config_cache = None
    
    def _get_config(self) -> Dict[str, Any]:
        """Load document types configuration from documents.epyson with strict validation.
        
        Returns:
            Complete document configuration dictionary from documents.epyson
            
        Raises:
            ValueError: If documents.epyson cannot be loaded or is missing required sections
        """
        if self._config_cache is None:
            from ePy_docs.core._config import ModularConfigLoader
            
            config_loader = ModularConfigLoader()
            documents_config = config_loader.get_config_section("documents")
            
            if not documents_config:
                raise ValueError(
                    "Failed to load documents configuration from documents.epyson. "
                    "Ensure documents.epyson exists in config directory."
                )
            
            if "document_types" not in documents_config:
                raise ValueError(
                    "Missing 'document_types' section in documents.epyson. "
                    "Configuration must define document_types section."
                )
            
            if "column_widths" not in documents_config:
                raise ValueError(
                    "Missing 'column_widths' section in documents.epyson. "
                    "Configuration must define column_widths section."
                )
            
            self._config_cache = documents_config
                
        return self._config_cache
    
    def get_document_type_info(self, document_type: str) -> Dict[str, Any]:
        """Get configuration for specific document type with validation.
        
        Args:
            document_type: Document type ('paper', 'report', 'book', 'presentations')
            
        Returns:
            Complete document type configuration dictionary
            
        Raises:
            ValueError: If document_type is invalid
        """
        config = self._get_config()
        
        if 'document_types' not in config:
            raise ValueError("Missing 'document_types' section in documents.epyson")
        
        doc_types = config['document_types']
        
        if document_type not in doc_types:
            valid_types = list(doc_types.keys())
            raise ValueError(
                f"Invalid document_type '{document_type}'. Valid types: {valid_types}"
            )
        
        return doc_types[document_type]
    
    def get_width_config(self, document_type: str) -> Dict[str, Any]:
        """Get width configuration optimized for document type margins.
        
        Args:
            document_type: Document type identifier
            
        Returns:
            Column width configuration dictionary with margin mappings
            
        Raises:
            ValueError: If column_widths configuration is missing or config_key not found
        """
        config = self._get_config()
        
        if 'column_widths' not in config:
            raise ValueError("Missing 'column_widths' section in documents.epyson")
        
        width_configs = config['column_widths']
        
        # Use document type mapping based on documents.epyson structure
        # book uses letter_book_margins, others use letter_1in_margins
        config_key = 'letter_book_margins' if document_type == 'book' else 'letter_1in_margins'
        
        if config_key not in width_configs:
            available_keys = list(width_configs.keys())
            raise ValueError(
                f"Missing width configuration key '{config_key}' in documents.epyson. "
                f"Available keys: {available_keys}"
            )
        
        return width_configs[config_key]
    
    def calculate_width(self, 
                       document_type: str,
                       layout_columns: int,
                       requested_columns: Union[float, List[float], None] = None) -> float:
        """Calculate optimized width in inches for tables/figures.
        
        Implements intelligent width calculation with fractional column support
        and performance optimization for common cases.
        
        Args:
            document_type: Document type ('paper', 'report', 'book', 'presentations')
            layout_columns: Number of columns in document layout (1-3)
            requested_columns: Width specification:
                - None: Single column width (default)
                - float: Column span (e.g., 1.0, 1.5, 2.0)
                - List[float]: Custom widths in inches
                
        Returns:
            Calculated width in inches
            
        Examples:
            >>> calc = ColumnWidthCalculator()
            >>> calc.calculate_width('paper', 2, 1.0)  # Single column in 2-col layout
            3.1
            >>> calc.calculate_width('paper', 2, 2.0)  # Full width in 2-col layout
            6.5
            >>> calc.calculate_width('paper', 2, 1.5)  # 1.5 columns in 2-col layout
            4.75
        """
        width_config = self.get_width_config(document_type)
        
        # Handle custom width lists (for split tables)
        if isinstance(requested_columns, list):
            if not requested_columns:
                raise ValueError("Custom width list cannot be empty")
            return requested_columns[0]
        
        # Default to single column
        requested_columns = requested_columns or 1.0
        
        # Get column configuration (documents.epyson uses '1_column', '2_columns', etc.)
        col_key = f"{layout_columns}_column" + ("s" if layout_columns > 1 else "")
        
        if col_key not in width_config:
            available_keys = list(width_config.keys())
            raise ValueError(
                f"Missing column configuration key '{col_key}' for {layout_columns} columns in documents.epyson. "
                f"Available keys: {available_keys}"
            )
        
        col_config = width_config[col_key]
        
        if 'single' not in col_config:
            raise ValueError(
                f"Missing 'single' width in column configuration '{col_key}' for document_type '{document_type}'"
            )
        
        single_width = col_config['single']
        
        # Get gap configuration (required for multi-column layouts)
        if layout_columns > 1:
            if 'gap' not in col_config:
                raise ValueError(
                    f"Missing 'gap' width in column configuration '{col_key}' for multi-column layout"
                )
            gap = col_config['gap']
        else:
            gap = 0.0
        
        # Optimized calculation for common cases
        if requested_columns == 1.0:
            return single_width
        elif requested_columns == 2.0 and 'double' in col_config:
            # Use pre-calculated double width if available
            return col_config['double']
        elif requested_columns == 3.0 and 'triple' in col_config:
            # Use pre-calculated triple width if available
            return col_config['triple']
        elif requested_columns == int(requested_columns):
            # Integer columns - calculate from single width
            cols = int(requested_columns)
            return cols * single_width + (cols - 1) * gap
        else:
            # Fractional columns with optimized calculation
            full_columns = int(requested_columns)
            fraction = requested_columns - full_columns
            base_width = full_columns * single_width + (full_columns - 1) * gap
            return base_width + fraction * (single_width + gap)
            base_width = full_columns * single_width + (full_columns - 1) * gap
            return base_width + fraction * (single_width + gap)
    
    def get_width_string(self, width_inches: float) -> str:
        """Convert width to optimized markdown string format.
        
        Args:
            width_inches: Width in inches
            
        Returns:
            Formatted string like "6.5in" or "3.1in" (optimized format)
        """
        # Optimized formatting: strip unnecessary trailing zeros
        formatted = f"{width_inches:.2f}".rstrip('0').rstrip('.')
        return f"{formatted}in"
    
    def validate_columns(self, 
                        document_type: str,
                        layout_columns: int,
                        requested_columns: Union[float, List[float], None]) -> None:
        """Validate column span parameters with comprehensive error handling.
        
        Args:
            document_type: Document type identifier
            layout_columns: Number of columns in layout
            requested_columns: Requested column span
            
        Raises:
            ValueError: If validation fails with descriptive message
        """
        if requested_columns is None or isinstance(requested_columns, list):
            return  # None or custom widths are always valid
        
        if requested_columns > layout_columns:
            raise ValueError(
                f"Requested {requested_columns} columns exceeds layout capacity "
                f"of {layout_columns} columns for document_type '{document_type}'"
            )


class DocumentProcessor:
    """Unified document processing engine."""
    
    def __init__(self):
        self._supported_types = self._get_supported_types()
    
    def _get_supported_types(self) -> Dict[str, str]:
        """Get supported file types from configuration with strict validation.
        
        Returns:
            Dictionary mapping file extensions to document types
            
        Raises:
            ValueError: If reader configuration is missing or invalid
        """
        from ePy_docs.core._config import get_config_section
        config = get_config_section('reader')
        
        if not config:
            raise ValueError(
                "Failed to load reader configuration. Ensure reader.epyson exists in config directory."
            )
        
        if 'file_extensions' not in config:
            raise ValueError(
                "Missing 'file_extensions' section in reader configuration"
            )
        
        extensions = config['file_extensions']
        
        return {
            ext: doc_type 
            for doc_type, exts in extensions.items() 
            for ext in exts
        }
    
    def detect_document_type(self, file_path: Path) -> str:
        """Detect document type from file extension with strict validation.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Document type string
            
        Raises:
            ValueError: If file extension is not supported
        """
        extension = file_path.suffix.lower()
        
        if extension not in self._supported_types:
            supported = ', '.join(sorted(self._supported_types.keys()))
            raise ValueError(
                f"Unsupported file extension '{extension}' for file '{file_path.name}'. "
                f"Supported extensions: {supported}"
            )
        
        return self._supported_types[extension]
    
    def validate_input_file(self, file_path: Path) -> bool:
        """Validate input file exists and is supported.
        
        Args:
            file_path: Path to validate
            
        Returns:
            True if valid
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file type is unsupported
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        # detect_document_type will raise ValueError if unsupported
        self.detect_document_type(file_path)
        
        return True
    
    def process_document(self, input_path: Path, output_dir: Path, 
                        layout_name: str = 'classic', document_type: str = 'article',
                        output_formats: List[str] = None, **kwargs) -> Dict[str, Path]:
        """Process document to specified formats."""
        output_formats = output_formats or ['pdf', 'html']
        
        # Validate input
        self.validate_input_file(input_path)
        
        # Prepare output
        output_dir.mkdir(parents=True, exist_ok=True)
        qmd_path = output_dir / f"{input_path.stem}.qmd"
        
        # Convert to QMD based on input type
        doc_type = self.detect_document_type(input_path)
        converter = self._get_converter(doc_type)
        qmd_content = converter(input_path, qmd_path, layout_name, document_type, output_formats, **kwargs)
        
        # Render to output formats
        return self._render_formats(qmd_path, output_formats)
    
    def _get_converter(self, doc_type: str):
        """Get appropriate converter function."""
        converters = {
            'qmd': self._process_qmd,
            'markdown': self._process_markdown,
            'word': self._process_word
        }
        return converters[doc_type]
    
    def _process_qmd(self, input_path: Path, qmd_path: Path, *args, **kwargs) -> str:
        """Process QMD file (copy)."""
        import shutil
        shutil.copy2(input_path, qmd_path)
        with open(qmd_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _process_markdown(self, input_path: Path, qmd_path: Path, 
                         layout_name: str, document_type: str, output_formats: List[str], **kwargs) -> str:
        """Process Markdown file.
        
        Args:
            input_path: Path to markdown file
            qmd_path: Output QMD path
            layout_name: Layout name
            document_type: Document type
            output_formats: Output format list
            **kwargs: Additional parameters (must include 'language')
            
        Raises:
            ValueError: If required parameters are missing
        """
        from ePy_docs.core._markdown import read_markdown_file, extract_frontmatter, convert_markdown_to_qmd
        from ePy_docs.core._quarto import quarto_orchestrator
        
        if 'language' not in kwargs:
            raise ValueError("Missing required parameter 'language' for markdown processing")
        
        content = read_markdown_file(input_path)
        frontmatter, body = extract_frontmatter(content)
        
        # Extract title with strict validation
        if frontmatter and 'title' in frontmatter:
            title = frontmatter['title']
        else:
            title = input_path.stem
        
        yaml_config = quarto_orchestrator.generate_yaml_config(
            title=title, layout_name=layout_name, document_type=document_type,
            output_formats=output_formats, language=kwargs['language'], **kwargs
        )
        
        convert_markdown_to_qmd(input_path, qmd_path, add_yaml=True, yaml_config=yaml_config)
        with open(qmd_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _process_word(self, input_path: Path, qmd_path: Path,
                     layout_name: str, document_type: str, output_formats: List[str], **kwargs) -> str:
        """Process Word file.
        
        Args:
            input_path: Path to Word file
            qmd_path: Output QMD path
            layout_name: Layout name
            document_type: Document type
            output_formats: Output format list
            **kwargs: Additional parameters (must include 'language', optional 'title')
            
        Raises:
            ValueError: If required parameters are missing
        """
        from ePy_docs.core._word import convert_docx_to_qmd
        from ePy_docs.core._quarto import quarto_orchestrator
        
        if 'language' not in kwargs:
            raise ValueError("Missing required parameter 'language' for Word processing")
        
        # Extract title with validation
        if 'title' in kwargs:
            title = kwargs['title']
        else:
            title = input_path.stem.replace('_', ' ').title()
        
        yaml_config = quarto_orchestrator.generate_yaml_config(
            title=title, layout_name=layout_name, document_type=document_type,
            output_formats=output_formats, language=kwargs['language'], **kwargs
        )
        
        convert_docx_to_qmd(input_path, qmd_path, yaml_config=yaml_config)
        with open(qmd_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _render_formats(self, qmd_path: Path, output_formats: List[str]) -> Dict[str, Path]:
        """Render QMD to specified formats."""
        from ePy_docs.core._quarto import render_qmd
        
        results = {'qmd': qmd_path}
        for fmt in output_formats:
            try:
                results[fmt] = render_qmd(qmd_path, output_format=fmt)
            except Exception as e:
                logger.warning(f"Failed to render {fmt}: {e}")
                results[fmt] = None
        
        return results
    
    def create_from_content(self, content: str, output_path: Path, title: str,
                          layout_name: str = 'classic', document_type: str = 'article',
                          output_formats: List[str] = None, **kwargs) -> Dict[str, Path]:
        """Create document from content string."""
        from ePy_docs.core._quarto import quarto_orchestrator
        
        output_formats = output_formats or ['pdf', 'html']
        return quarto_orchestrator.create_and_render(
            output_path=output_path, content=content, title=title,
            layout_name=layout_name, document_type=document_type,
            output_formats=output_formats, **kwargs
        )
    
    def process_batch(self, input_dir: Path, output_dir: Path, 
                     pattern: str = '*.md', **kwargs) -> Dict[str, Dict[str, Path]]:
        """Process multiple documents in directory."""
        results = {}
        for file_path in input_dir.glob(pattern):
            if file_path.is_file():
                try:
                    results[file_path.name] = self.process_document(
                        input_path=file_path,
                        output_dir=output_dir / file_path.stem,
                        **kwargs
                    )
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    results[file_path.name] = {'error': str(e)}
        
        return results


# Global internal instances for other modules to access
_processor = DocumentProcessor()
_width_calculator = ColumnWidthCalculator()
