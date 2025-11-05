"""Document processing utilities for ePy_docs.

Provides document type detection, conversion routing, and batch processing
for various input formats (QMD, Markdown, Word) to multiple output formats.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Unified document processing engine."""
    
    def __init__(self):
        self._supported_types = self._get_supported_types()
    
    def _get_supported_types(self) -> Dict[str, str]:
        """Get supported file types from configuration."""
        from ePy_docs.core._config import get_config_section
        config = get_config_section('reader')
        extensions = config.get('file_extensions', {})
        return {
            ext: doc_type 
            for doc_type, exts in extensions.items() 
            for ext in exts
        }
    
    def detect_document_type(self, file_path: Path) -> str:
        """Detect document type from file extension."""
        extension = file_path.suffix.lower()
        return self._supported_types.get(extension, 'unknown')
    
    def validate_input_file(self, file_path: Path) -> bool:
        """Validate input file exists and is supported."""
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        doc_type = self.detect_document_type(file_path)
        if doc_type == 'unknown':
            supported = ', '.join(self._supported_types.keys())
            raise ValueError(f"Unsupported file type: {file_path.suffix}. Supported: {supported}")
        
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
        """Process Markdown file."""
        from ePy_docs.core._markdown import read_markdown_file, extract_frontmatter, convert_markdown_to_qmd
        from ePy_docs.core._quarto import generate_quarto_yaml
        
        content = read_markdown_file(input_path)
        frontmatter, body = extract_frontmatter(content)
        title = frontmatter.get('title', input_path.stem) if frontmatter else input_path.stem
        
        yaml_config = generate_quarto_yaml(
            title=title, layout_name=layout_name, document_type=document_type,
            output_formats=output_formats, language=kwargs.get('language', 'en'), **kwargs
        )
        
        convert_markdown_to_qmd(input_path, qmd_path, add_yaml=True, yaml_config=yaml_config)
        with open(qmd_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _process_word(self, input_path: Path, qmd_path: Path,
                     layout_name: str, document_type: str, output_formats: List[str], **kwargs) -> str:
        """Process Word file."""
        from ePy_docs.core._word import convert_docx_to_qmd
        from ePy_docs.core._quarto import generate_quarto_yaml
        
        title = kwargs.get('title', input_path.stem.replace('_', ' ').title())
        yaml_config = generate_quarto_yaml(
            title=title, layout_name=layout_name, document_type=document_type,
            output_formats=output_formats, language=kwargs.get('language', 'en'), **kwargs
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
        from ePy_docs.core._quarto import create_and_render
        
        output_formats = output_formats or ['pdf', 'html']
        return create_and_render(
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


# Global processor instance
_processor = DocumentProcessor()

# Public API functions (for backward compatibility)
def detect_document_type(file_path: Path) -> str:
    """Detect document type from file extension."""
    return _processor.detect_document_type(file_path)

def process_document(input_path: Path, output_dir: Path, 
                    layout_name: str = 'classic', document_type: str = 'article',
                    output_formats: List[str] = None, **kwargs) -> Dict[str, Path]:
    """Process document to specified formats."""
    return _processor.process_document(input_path, output_dir, layout_name, 
                                     document_type, output_formats, **kwargs)

def create_document_from_content(content: str, output_path: Path, title: str,
                               layout_name: str = 'classic', document_type: str = 'article',
                               output_formats: List[str] = None, **kwargs) -> Dict[str, Path]:
    """Create document from content string."""
    return _processor.create_from_content(content, output_path, title, layout_name, 
                                        document_type, output_formats, **kwargs)

def process_multiple_documents(input_dir: Path, output_dir: Path, 
                             pattern: str = '*.md', **kwargs) -> Dict[str, Dict[str, Path]]:
    """Process multiple documents in directory."""
    return _processor.process_batch(input_dir, output_dir, pattern, **kwargs)

def validate_input_file(file_path: Path) -> bool:
    """Validate input file exists and is supported."""
    return _processor.validate_input_file(file_path)
