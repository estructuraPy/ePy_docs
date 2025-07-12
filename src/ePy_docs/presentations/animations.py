"""Animation and transition effects for presentations.

Provides animation capabilities and transition effects for engaging
presentation content including slide transitions and content animations.
"""

from enum import Enum
from typing import Dict, Any, List


class TransitionType(Enum):
    """Available transition types for slides."""
    NONE = "none"
    FADE = "fade"
    SLIDE = "slide"
    CONVEX = "convex"
    CONCAVE = "concave"
    ZOOM = "zoom"


class AnimationType(Enum):
    """Available animation types for content."""
    FADE_IN = "fade-in"
    FADE_UP = "fade-up"
    FADE_DOWN = "fade-down"
    FADE_LEFT = "fade-left"
    FADE_RIGHT = "fade-right"
    ZOOM_IN = "zoom-in"
    ZOOM_OUT = "zoom-out"
    SLIDE_UP = "slide-up"
    SLIDE_DOWN = "slide-down"


class AnimationRenderer:
    """Renderer for animations and transitions in presentations."""
    
    def __init__(self, presentation_format: str = "revealjs"):
        self.presentation_format = presentation_format
    
    def add_slide_transition(self, transition: TransitionType, 
                           background_transition: TransitionType = None) -> str:
        """Add transition effect to a slide."""
        if self.presentation_format == "revealjs":
            bg_trans = background_transition.value if background_transition else transition.value
            return f'<!-- .slide: data-transition="{transition.value}" data-background-transition="{bg_trans}" -->\n\n'
        return ""
    
    def add_content_animation(self, content: str, animation: AnimationType,
                            delay: int = 0) -> str:
        """Add animation to content element."""
        if self.presentation_format == "revealjs":
            delay_attr = f' data-fragment-delay="{delay}"' if delay > 0 else ''
            return f'<div class="fragment {animation.value}"{delay_attr}>\n{content}\n</div>\n'
        return content
    
    def add_fragment_list(self, items: List[str], animation: AnimationType = AnimationType.FADE_IN) -> str:
        """Create an animated list where items appear one by one."""
        if self.presentation_format == "revealjs":
            fragment_list = ""
            for i, item in enumerate(items):
                delay = i * 200  # 200ms delay between items
                fragment_list += f'- <span class="fragment {animation.value}" data-fragment-delay="{delay}">{item}</span>\n'
            return fragment_list
        else:
            # Fallback to regular list
            return "\n".join([f"- {item}" for item in items])
    
    def add_step_by_step_reveal(self, sections: List[Dict[str, str]],
                               animation: AnimationType = AnimationType.FADE_UP) -> str:
        """Create step-by-step content reveal."""
        if self.presentation_format == "revealjs":
            reveal_content = ""
            for i, section in enumerate(sections):
                delay = i * 500  # 500ms delay between sections
                title = section.get('title', '')
                content = section.get('content', '')
                
                reveal_content += f'<div class="fragment {animation.value}" data-fragment-delay="{delay}">\n'
                if title:
                    reveal_content += f'### {title}\n\n'
                reveal_content += f'{content}\n'
                reveal_content += '</div>\n\n'
            
            return reveal_content
        else:
            # Fallback to regular content
            regular_content = ""
            for section in sections:
                title = section.get('title', '')
                content = section.get('content', '')
                if title:
                    regular_content += f'### {title}\n\n'
                regular_content += f'{content}\n\n'
            return regular_content
    
    def add_highlight_animation(self, text: str, highlight_color: str = "#ffeb3b") -> str:
        """Add highlight animation to text."""
        if self.presentation_format == "revealjs":
            return f'<mark class="fragment highlight-current-red">{text}</mark>'
        return f'**{text}**'
    
    def add_auto_animate_slide(self) -> str:
        """Add auto-animate attribute to slide."""
        if self.presentation_format == "revealjs":
            return '<!-- .slide: data-auto-animate -->\n\n'
        return ""
    
    def create_progress_bar(self, current: int, total: int, 
                          color: str = "#2E86AB") -> str:
        """Create an animated progress bar."""
        if self.presentation_format == "revealjs":
            percentage = (current / total) * 100
            return f'''
<div style="width: 100%; background-color: #e0e0e0; border-radius: 10px; margin: 20px 0;">
    <div class="fragment" data-fragment-index="1" 
         style="width: {percentage}%; height: 20px; background-color: {color}; 
                border-radius: 10px; transition: width 2s ease-in-out;">
    </div>
</div>
<p class="fragment" data-fragment-index="2">
    Progress: {current}/{total} ({percentage:.1f}%)
</p>
'''
        else:
            return f"Progress: {current}/{total} ({(current/total)*100:.1f}%)"
    
    def add_countdown_timer(self, seconds: int) -> str:
        """Add countdown timer animation."""
        if self.presentation_format == "revealjs":
            return f'''
<div id="countdown" style="font-size: 3em; color: #e74c3c; text-align: center;">
    <span class="fragment" data-fragment-index="1">{seconds}</span>
</div>

<script>
let timeLeft = {seconds};
const countdownElement = document.getElementById('countdown').querySelector('span');
const timer = setInterval(() => {{
    timeLeft--;
    countdownElement.textContent = timeLeft;
    if (timeLeft <= 0) {{
        clearInterval(timer);
        countdownElement.textContent = "Time's up!";
    }}
}}, 1000);
</script>
'''
        else:
            return f"Timer: {seconds} seconds"
