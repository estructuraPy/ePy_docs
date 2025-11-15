"""
Shared Validation Module for ePy_docs.

Provides unified ValidationEngine and specialized validators used across
all modules to enforce configuration-driven behavior, consistent input
validation, and error handling.

Consolidated from: _quarto.py, _pdf.py, _notes.py, _markdown.py, _format.py,
_data.py, _config.py, _images.py, _document.py

Version: 3.0.0 - Zero hardcoding, fail-fast validation
"""
from typing import Dict, List, Any, Optional, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    import pandas as pd
else:
    try:
        import pandas as pd
    except ImportError:
        pd = None


def _get_quarto_config_from_documents() -> Dict[str, Any]:
    """Get Quarto configuration from documents.epyson configuration system.
    
    Returns:
        Quarto configuration dictionary
        
    Raises:
        ValueError: If quarto_config not found in documents configuration
    """
    from ePy_docs.core._config import get_config_section
    documents_config = get_config_section('documents')
    
    if 'quarto_config' not in documents_config:
        raise ValueError(
            "quarto_config not found in documents configuration. "
            "Expected 'quarto_config' key in documents.epyson."
        )
    
    return documents_config['quarto_config']


class ValidationEngine:
    """Handles input validation and error checking with comprehensive rules."""

    def __init__(self, config_provider=None):
        """Initialize validation engine with optional config provider."""
        self._config_provider = config_provider

    def _get_base_config_structure(self) -> Dict[str, Any]:
        """Get base configuration structure from documents.epyson."""
        try:
            from ePy_docs.core._config import get_config_section
            documents_config = get_config_section('documents')
            if 'quarto_config' in documents_config:
                return documents_config['quarto_config']
        except (ImportError, KeyError):
            pass

        # No fallback - configuration must be available
        raise ValueError(
            "Failed to load base configuration from documents.epyson - configuration system is required"
        )

    def validate_title(self, title: str) -> str:
        """Validate and sanitize document title."""
        if not title or not isinstance(title, str):
            raise ValueError("Title must be a non-empty string")
        return title.strip()

    def validate_layout_name(self, layout_name: str) -> str:
        """Validate layout name."""
        if not layout_name or not isinstance(layout_name, str):
            raise ValueError("Layout name must be a non-empty string")
        return layout_name.strip()

    def validate_document_type(self, document_type: str) -> str:
        """Validate document type against available types in configuration.
        
        Args:
            document_type: Document type to validate
            
        Returns:
            Validated document type
            
        Raises:
            ValueError: If document_types not found or document_type invalid
        """
        from ePy_docs.core._config import get_config_section
        documents_config = get_config_section('documents')
        
        if 'document_types' not in documents_config:
            raise ValueError(
                "document_types not found in documents configuration. "
                "Expected 'document_types' key in documents.epyson."
            )
        
        available_types = documents_config['document_types'].keys()

        if document_type not in available_types:
            valid_types = list(available_types)
            raise ValueError(f"Document type must be one of: {valid_types}")

        # Return the document type as-is since Quarto handles these natively
        return document_type

    def validate_output_formats(self, output_formats: List[str], document_type: str = None) -> List[str]:
        """Validate output formats list against global and document-specific supported formats."""
        if not output_formats or not isinstance(output_formats, list):
            raise ValueError("Output formats must be a non-empty list")

        # Get all supported formats from documents configuration
        supported_formats = self._get_supported_formats(document_type)

        for fmt in output_formats:
            if fmt not in supported_formats:
                raise ValueError(f"Unsupported format '{fmt}'. Supported: {supported_formats}")

        return output_formats

    def _get_supported_formats(self, document_type: str = None) -> List[str]:
        """Get supported formats globally or for specific document type.
        
        Args:
            document_type: Optional document type to get specific formats
            
        Returns:
            List of supported format strings
            
        Raises:
            ValueError: If document_types or output_formats not found
        """
        try:
            from ePy_docs.core._config import get_config_section
            documents_config = get_config_section('documents')
            
            if 'document_types' not in documents_config:
                raise ValueError(
                    "document_types not found in documents configuration. "
                    "Expected 'document_types' key in documents.epyson."
                )

            if document_type and document_type in documents_config['document_types']:
                # Return formats for specific document type
                doc_config = documents_config['document_types'][document_type]
                if 'output_formats' not in doc_config:
                    raise ValueError(
                        f"output_formats not found for document type '{document_type}'. "
                        "Expected 'output_formats' key in document type configuration."
                    )
                return doc_config['output_formats']

            # Return all supported formats across all document types
            all_formats = set()
            for doc_name, doc_config in documents_config['document_types'].items():
                if 'output_formats' not in doc_config:
                    raise ValueError(
                        f"output_formats not found for document type '{doc_name}'. "
                        "Expected 'output_formats' key in document type configuration."
                    )
                all_formats.update(doc_config['output_formats'])

            if not all_formats:
                raise ValueError("No output formats configured in any document type in documents.epyson")
            return list(all_formats)

        except (ImportError, KeyError) as e:
            raise ValueError(f"Failed to load document types configuration from documents.epyson: {e}")

    def validate_language(self, language: str) -> str:
        """Validate document language."""
        config = self._get_config()
        supported = config['metadata']['supported_languages']

        if language not in supported:
            raise ValueError(f"Unsupported language '{language}'. Supported: {supported}")

        return language

    def validate_path(self, path: Path, must_exist: bool = False) -> Path:
        """Validate file path."""
        if not isinstance(path, Path):
            path = Path(path)

        if must_exist and not path.exists():
            raise ValueError(f"Path does not exist: {path}")

        return path

    def _get_config(self) -> Dict[str, Any]:
        """Get configuration with fallback to defaults."""
        return self._load_quarto_config()

    def _load_quarto_config(self) -> Dict[str, Any]:
        """Load Quarto configuration from config system with intelligent fallback."""
        try:
            # Try to load from modular config system
            if self._config_provider:
                config = self._config_provider('quarto')
                if isinstance(config, dict) and 'metadata' in config:
                    return config

            # Try to load documents config and extract quarto section
            from ePy_docs.core._config import get_config_section
            documents_config = get_config_section('documents')
            if 'quarto_config' in documents_config:
                quarto_section = documents_config['quarto_config']
                # Merge with fallback for missing sections
                return self._merge_with_fallback(quarto_section)

        except (ImportError, KeyError, AttributeError):
            pass

        return _get_quarto_config_from_documents()

    def _merge_with_fallback(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with fallback values."""
        merged = _get_quarto_config_from_documents().copy()

        # Add supported formats and languages if available from documents config
        try:
            from ePy_docs.core._config import get_config_section
            documents_config = get_config_section('documents')

            # Extract supported formats from document types
            all_formats = set()
            for doc_name, doc_config in documents_config['document_types'].items():
                if 'output_formats' not in doc_config:
                    raise ValueError(
                        f"output_formats not found for document type '{doc_name}'. "
                        "All document types must have 'output_formats' configured."
                    )
                all_formats.update(doc_config['output_formats'])

            if 'metadata' not in merged:
                merged['metadata'] = {}
            merged['metadata']['supported_formats'] = list(all_formats)

            # Get supported languages from documents config
            supported_languages = documents_config.get('supported_languages')
            if not supported_languages:
                raise ValueError("No supported languages configured in documents.epyson")
            merged['metadata']['supported_languages'] = supported_languages

        except (ImportError, KeyError):
            pass

        # Deep merge with loaded config
        for key, value in config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key].update(value)
            else:
                merged[key] = value

        return merged


# ============================================================================
# SPECIALIZED VALIDATORS
# ============================================================================

class PdfValidator:
    """PDF-specific validation (from _pdf.py)."""
    
    def __init__(self):
        self._config = None
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get PDF configuration with caching."""
        if self._config is None:
            try:
                from ePy_docs.core._config import get_config_section
                self._config = get_config_section('pdf')
            except Exception:
                self._config = {}
        return self._config
    
    def validate_engine(self, engine: str) -> str:
        """Validate PDF engine selection.
        
        Args:
            engine: PDF engine name to validate
            
        Returns:
            Validated engine name
            
        Raises:
            ValueError: If engine invalid or supported_engines not configured
        """
        if not engine or not isinstance(engine, str):
            raise ValueError("Engine must be a non-empty string")
        
        supported_engines = self.config.get('supported_engines')
        if not supported_engines:
            raise ValueError("supported_engines not found in PDF configuration")
        
        if engine not in supported_engines:
            raise ValueError(
                f"Unsupported PDF engine '{engine}'. "
                f"Supported engines: {', '.join(supported_engines)}"
            )
        return engine
    
    def validate_document_class(self, document_class: str) -> str:
        """Validate LaTeX document class."""
        valid_classes = self.config.get('valid_document_classes')
        if not valid_classes:
            raise ValueError("valid_document_classes not found in PDF configuration")
        
        if document_class not in valid_classes:
            raise ValueError(
                f"Invalid document class '{document_class}'. "
                f"Valid classes: {', '.join(valid_classes)}"
            )
        return document_class
    
    def validate_layout_name(self, layout_name: str) -> str:
        """Validate layout name."""
        if not layout_name or not isinstance(layout_name, str):
            return 'classic'
        return layout_name.strip()


class NotesValidator:
    """Notes and callouts validation (from _notes.py)."""
    
    def __init__(self):
        self._config = None
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get notes configuration with caching."""
        if self._config is None:
            try:
                from ePy_docs.core._config import get_config_section
                self._config = get_config_section('notes')
            except Exception:
                self._config = {}
        return self._config
    
    def validate_content(self, content: str) -> str:
        """Validate and sanitize note content."""
        if not content or not isinstance(content, str):
            return ""
        return content.strip()
    
    def validate_note_type(self, note_type: str) -> str:
        """Validate and normalize note type.
        
        Args:
            note_type: Note type to validate
            
        Returns:
            Validated and normalized note type
            
        Raises:
            ValueError: If note_type invalid or type_mapping not configured
        """
        if not note_type or not isinstance(note_type, str):
            raise ValueError("Note type must be a non-empty string")
        
        normalized_type = note_type.lower().strip()
        
        if 'type_mapping' not in self.config:
            raise ValueError(
                "type_mapping not found in notes configuration. "
                "Expected 'type_mapping' key in notes.epyson."
            )
        
        type_mapping = self.config['type_mapping']
        
        if normalized_type not in type_mapping:
            raise ValueError(
                f"Invalid note type '{note_type}'. "
                f"Valid types: {', '.join(type_mapping.keys())}"
            )
        
        return type_mapping[normalized_type]
    
    def validate_title(self, title: Optional[str]) -> Optional[str]:
        """Validate and sanitize note title."""
        if not title or not isinstance(title, str):
            return None
        
        sanitized = title.strip()
        return sanitized if sanitized else None


class MarkdownValidator:
    """Markdown file validation (from _markdown.py)."""
    
    def __init__(self):
        self._config = None
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get markdown configuration with caching."""
        if self._config is None:
            try:
                from ePy_docs.core._config import get_config_section
                self._config = get_config_section('markdown')
            except Exception:
                self._config = {}
        return self._config
    
    def validate_file_path(self, file_path: Path) -> None:
        """Validate markdown file path and extension.
        
        Args:
            file_path: Path to markdown file
            
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If file extension invalid or valid_extensions not configured
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Markdown file not found: {file_path}")
        
        if 'valid_extensions' not in self.config:
            raise ValueError(
                "valid_extensions not found in markdown configuration. "
                "Expected 'valid_extensions' array in configuration."
            )
        
        valid_extensions = self.config['valid_extensions']
        
        if file_path.suffix.lower() not in valid_extensions:
            raise ValueError(
                f"Not a markdown file: {file_path}\n"
                f"Valid extensions: {', '.join(valid_extensions)}"
            )
    
    def sanitize_content(self, content: str) -> str:
        """Sanitize markdown content."""
        if not isinstance(content, str):
            content = str(content)
        return content.strip()


class FormatValidator:
    """Text formatting validation (from _format.py)."""
    
    @staticmethod
    def sanitize_text(text: Any) -> str:
        """Convert input to string and sanitize."""
        if pd and (text is None or pd.isna(text)):
            return ""
        
        if text is None:
            return ""
        
        # Handle pandas Series
        if hasattr(text, 'iloc'):
            text = text.iloc[0] if len(text) > 0 else ""
        
        return str(text).strip()
    
    @staticmethod
    def is_missing_value(text: str, missing_indicators: List[str]) -> bool:
        """Check if text represents a missing value."""
        text_lower = text.lower()
        return text_lower in missing_indicators
    
    @staticmethod
    def validate_dataframe(df: 'pd.DataFrame') -> None:
        """Validate DataFrame input."""
        if pd is None:
            raise ImportError("pandas is required for DataFrame validation")
        
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(df).__name__}")
        
        if df.empty:
            raise ValueError("DataFrame cannot be empty")


class ImageValidator:
    """Image file validation (from _images.py)."""
    
    def __init__(self):
        self._config = None
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get images configuration with caching."""
        if self._config is None:
            try:
                from ePy_docs.core._config import get_config_section
                self._config = get_config_section('images')
            except Exception:
                self._config = {}
        return self._config
    
    def validate_image_path(self, image_path: Path) -> Path:
        """Validate image file path and format.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Validated Path object
            
        Raises:
            TypeError: If image_path is None or not a string/Path
            FileNotFoundError: If image file does not exist
            ValueError: If image format unsupported or supported_formats not configured
        """
        # Validate type first
        if image_path is None:
            raise TypeError(f"Image path cannot be None (expected str, bytes or os.PathLike object, not NoneType)")
        
        if not isinstance(image_path, (str, Path)):
            raise TypeError(f"Image path must be str or Path, got {type(image_path).__name__}")
        
        if not isinstance(image_path, Path):
            image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Try to get supported_formats from shared_defaults or root level
        supported_formats = self.config.get('supported_formats')
        if not supported_formats and 'shared_defaults' in self.config:
            supported_formats = self.config['shared_defaults'].get('supported_formats')
        
        if not supported_formats:
            raise ValueError(
                "supported_formats not found in images configuration. "
                "Expected 'supported_formats' in images.epyson (root or shared_defaults)."
            )
        
        valid_formats = supported_formats
        
        if image_path.suffix.lower() not in valid_formats:
            raise ValueError(
                f"Unsupported image format: {image_path.suffix}\n"
                f"Supported formats: {', '.join(valid_formats)}"
            )
        
        return image_path
    
    def validate_dimensions(self, width: Optional[float], height: Optional[float]) -> tuple:
        """Validate image dimensions."""
        if width is not None and width <= 0:
            raise ValueError(f"Width must be positive, got {width}")
        if height is not None and height <= 0:
            raise ValueError(f"Height must be positive, got {height}")
        return width, height


class DocumentValidator:
    """Document structure validation (from _document.py)."""
    
    def validate_columns(self, columns: int) -> int:
        """Validate column count."""
        if not isinstance(columns, int):
            raise TypeError(f"Columns must be an integer, got {type(columns).__name__}")
        
        if columns < 1:
            raise ValueError(f"Columns must be at least 1, got {columns}")
        
        if columns > 4:
            raise ValueError(f"Columns must be at most 4 for layout purposes, got {columns}")
        
        return columns
    
    def validate_input_file(self, file_path: Path) -> bool:
        """Validate input file exists and is readable."""
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        return True


class DataValidator:
    """Data structure validation (from _data.py)."""
    
    @staticmethod
    def validate_dict_structure(data: Dict, required_keys: List[str]) -> None:
        """Validate dictionary has required keys."""
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data).__name__}")
        
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            raise ValueError(f"Missing required keys: {', '.join(missing_keys)}")
    
    @staticmethod
    def validate_list_not_empty(data: List, name: str = "list") -> None:
        """Validate list is not empty."""
        if not isinstance(data, list):
            raise TypeError(f"{name} must be a list, got {type(data).__name__}")
        
        if not data:
            raise ValueError(f"{name} cannot be empty")


class ConfigValidator:
    """Configuration validation (from _config.py)."""
    
    @staticmethod
    def validate_config_file(config_path: Path) -> None:
        """Validate configuration file exists and is readable."""
        if not isinstance(config_path, Path):
            config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        if not config_path.is_file():
            raise ValueError(f"Path is not a file: {config_path}")
        
        valid_extensions = ['.json', '.epyson', '.yaml', '.yml']
        if config_path.suffix.lower() not in valid_extensions:
            raise ValueError(
                f"Unsupported configuration format: {config_path.suffix}\n"
                f"Supported formats: {', '.join(valid_extensions)}"
            )
    
    @staticmethod
    def validate_section_exists(config: Dict, section_name: str) -> None:
        """Validate configuration section exists."""
        if not isinstance(config, dict):
            raise TypeError(f"Config must be a dict, got {type(config).__name__}")
        
        if section_name not in config:
            raise ValueError(f"Configuration section '{section_name}' not found")


# ============================================================================
# VALIDATION FACTORY
# ============================================================================

class ValidationFactory:
    """Factory for creating specialized validators."""
    
    _instances = {}
    
    @classmethod
    def get_base_validator(cls, config_provider=None) -> ValidationEngine:
        """Get base ValidationEngine instance."""
        key = 'base'
        if key not in cls._instances:
            cls._instances[key] = ValidationEngine(config_provider)
        return cls._instances[key]
    
    @classmethod
    def get_pdf_validator(cls) -> PdfValidator:
        """Get PdfValidator instance."""
        key = 'pdf'
        if key not in cls._instances:
            cls._instances[key] = PdfValidator()
        return cls._instances[key]
    
    @classmethod
    def get_notes_validator(cls) -> NotesValidator:
        """Get NotesValidator instance."""
        key = 'notes'
        if key not in cls._instances:
            cls._instances[key] = NotesValidator()
        return cls._instances[key]
    
    @classmethod
    def get_markdown_validator(cls) -> MarkdownValidator:
        """Get MarkdownValidator instance."""
        key = 'markdown'
        if key not in cls._instances:
            cls._instances[key] = MarkdownValidator()
        return cls._instances[key]
    
    @classmethod
    def get_image_validator(cls) -> ImageValidator:
        """Get ImageValidator instance."""
        key = 'image'
        if key not in cls._instances:
            cls._instances[key] = ImageValidator()
        return cls._instances[key]
    
    @classmethod
    def get_document_validator(cls) -> DocumentValidator:
        """Get DocumentValidator instance."""
        key = 'document'
        if key not in cls._instances:
            cls._instances[key] = DocumentValidator()
        return cls._instances[key]
    
    @classmethod
    def clear_cache(cls):
        """Clear all cached validator instances."""
        cls._instances.clear()


# =============================================================================
# STANDALONE VALIDATION FUNCTIONS FOR EASY IMPORT
# =============================================================================

def validate_dataframe(df: 'pd.DataFrame', name: str = "DataFrame") -> None:
    """Validate DataFrame input."""
    FormatValidator.validate_dataframe(df)


def validate_string(text: str, name: str = "string", allow_empty: bool = True, allow_none: bool = False) -> None:
    """Validate string input."""
    if text is None:
        if not allow_none:
            raise TypeError(f"{name} cannot be None")
        return
    
    if not isinstance(text, str):
        raise TypeError(f"{name} must be a string, got {type(text).__name__}")
    
    if not allow_empty and not text.strip():
        raise ValueError(f"{name} cannot be empty")


def validate_list(items: List, name: str = "list", allow_empty: bool = True, validate_items: bool = True) -> None:
    """Validate list input."""
    if not isinstance(items, list):
        raise TypeError(f"{name} must be a list, got {type(items).__name__}")
    
    if not allow_empty and len(items) == 0:
        raise ValueError(f"{name} cannot be empty")
    
    if validate_items:
        for i, item in enumerate(items):
            if item is None:
                raise TypeError(f"{name} item at position {i} cannot be None")
            if not isinstance(item, str):
                raise TypeError(f"{name} item at position {i} must be str, got {type(item).__name__}")


def validate_image_path(image_path) -> Path:
    """Validate image file path and format."""
    validator = ImageValidator()
    return validator.validate_image_path(image_path)


def validate_image_width(width: str) -> str:
    """Validate image width specification."""
    if not isinstance(width, str):
        raise TypeError(f"Width must be a string, got {type(width).__name__}")
    
    # Accept percentage or absolute units
    if width.endswith('%') or width.endswith('in') or width.endswith('cm') or width.endswith('px'):
        return width
    
    raise ValueError(f"Width must end with %, in, cm, or px. Got: {width}")


def validate_callout_type(callout_type: str) -> str:
    """Validate callout type."""
    if not isinstance(callout_type, str):
        raise TypeError(f"Callout type must be a string, got {type(callout_type).__name__}")
    
    valid_types = ['note', 'tip', 'warning', 'caution', 'important', 'error', 'success', 'information', 'risk']
    
    if callout_type.lower() not in valid_types:
        raise ValueError(f"Callout type must be one of: {valid_types}. Got: {callout_type}")
    
    return callout_type.lower()


def validate_reference_key(ref_key: str) -> str:
    """Validate reference key format."""
    if not isinstance(ref_key, str):
        raise TypeError(f"Reference key must be a string, got {type(ref_key).__name__}")
    
    if not ref_key.strip():
        raise ValueError("Reference key cannot be empty")
    
    # Allow alphanumeric, hyphens, and underscores
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', ref_key):
        raise ValueError(f"Reference key can only contain letters, numbers, hyphens, and underscores. Got: {ref_key}")
    
    return ref_key.strip()
