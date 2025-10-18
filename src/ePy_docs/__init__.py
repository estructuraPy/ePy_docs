"""ePy_docs - Engineering document generation library.

Public API:
- DocumentWriter: Main class for document generation (unified API)

Internal structure (not exposed):
- writers.py: Core API implementation (pure delegation)
- config/: Configuration loaders
- internals/: Implementation logic (styling, generation, data processing, formatting)
- utils/: Internal utilities (validation)
- resources/: Configuration files (.epyson)
"""

__version__ = "0.2.0"

# External libraries validation
try:
    from ePy_units.converter import UnitConverter
except ImportError:
    raise ImportError("ePy_units library is required. Install with: pip install ePy_units")

# Public API - unified DocumentWriter
from ePy_docs.writers import DocumentWriter

__all__ = [
    'DocumentWriter',
    'UnitConverter',
]

