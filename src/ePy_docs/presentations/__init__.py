"""Presentation module for ePy_suite.

Provides specialized functionality for creating presentations with slides,
themes, animations, and interactive content optimized for presentation formats.
"""

from .formatter import PresentationFormatter
from .slides import SlideType, SlideRenderer
from .themes import PresentationTheme
from .animations import AnimationRenderer

__all__ = ['PresentationFormatter', 'SlideType', 'SlideRenderer', 'PresentationTheme', 'AnimationRenderer']
