"""Slide management and rendering for presentations.

Provides different slide types and rendering capabilities optimized
for various presentation formats and content types.
"""

from enum import Enum
from typing import Dict, Any, List, Optional


class SlideType(Enum):
    """Types of slides available for presentations."""
    TITLE = "title"
    SECTION = "section"
    CONTENT = "content"
    TWO_COLUMN = "two_column"
    IMAGE = "image"
    TABLE = "table"
    QUOTE = "quote"
    CONCLUSION = "conclusion"


class SlideRenderer:
    """Renderer for different types of slides."""
    
    def __init__(self, presentation_format: str = "revealjs"):
        self.presentation_format = presentation_format
        self.slide_templates = self._load_slide_templates()
    
    def _load_slide_templates(self) -> Dict[SlideType, str]:
        """Load slide templates for different slide types."""
        templates = {
            SlideType.TITLE: """
# {title}
{subtitle_block}
{author_block}
{date_block}
""",
            SlideType.SECTION: """
# {title}
{subtitle_block}
""",
            SlideType.CONTENT: """
## {title}

{content}
{bullet_points}
""",
            SlideType.TWO_COLUMN: """
## {title}

:::: {{.columns}}

::: {{.column width="50%"}}
{left_content}
:::

::: {{.column width="50%"}}
{right_content}
:::

::::
""",
            SlideType.IMAGE: """
## {title}

![{alt_text}]({image_path})

{caption_block}
""",
            SlideType.QUOTE: """
## {title}

> {quote_text}
>
> --- {attribution}
""",
        }
        
        return templates
    
    def render_slide(self, slide_type: SlideType, **kwargs) -> str:
        """Render a slide of the specified type with given parameters."""
        template = self.slide_templates.get(slide_type, "")
        
        # Process template variables
        rendered_content = self._process_template_variables(template, **kwargs)
        
        return rendered_content
    
    def _process_template_variables(self, template: str, **kwargs) -> str:
        """Process template variables and conditional blocks."""
        # Handle conditional blocks
        if 'subtitle' in kwargs and kwargs['subtitle']:
            subtitle_block = f"## {kwargs['subtitle']}"
        else:
            subtitle_block = ""
        
        if 'author' in kwargs and kwargs['author']:
            author_block = f"**{kwargs['author']}**"
        else:
            author_block = ""
        
        if 'date' in kwargs and kwargs['date']:
            date_block = kwargs['date']
        else:
            date_block = ""
        
        if 'caption' in kwargs and kwargs['caption']:
            caption_block = f"*{kwargs['caption']}*"
        else:
            caption_block = ""
        
        # Handle bullet points
        bullet_points = ""
        if 'bullet_points' in kwargs and kwargs['bullet_points']:
            bullet_points = "\n".join([f"- {point}" for point in kwargs['bullet_points']])
        
        # Update kwargs with processed blocks
        template_vars = {
            **kwargs,
            'subtitle_block': subtitle_block,
            'author_block': author_block,
            'date_block': date_block,
            'caption_block': caption_block,
            'bullet_points': bullet_points,
        }
        
        # Format template
        try:
            return template.format(**template_vars)
        except KeyError as e:
            # Handle missing variables gracefully
            return template
    
    def get_slide_break(self) -> str:
        """Get slide break syntax for the presentation format."""
        if self.presentation_format == "revealjs":
            return "\n---\n\n"
        elif self.presentation_format == "beamer":
            return "\n\\framebreak\n\n"
        else:
            return "\n\n"
