"""Content management utilities for ePy_docs.

Clean configuration loading from setup.json without fallbacks.
"""

import re
from typing import Tuple, Dict
from ePy_docs.core.setup import _load_cached_config


class ContentProcessor:
    """Content processing utilities for protecting special content during transformations."""
    
    @staticmethod
    def protect_callouts_from_header_processing(content: str) -> Tuple[str, Dict[str, str]]:
        """Protect Quarto callouts from being processed as headers.
        
        Args:
            content: The markdown content to process
            
        Returns:
            Tuple of (protected_content, callout_replacements)
        """
        if not content:
            return content, {}
            
        # Pattern to match Quarto callouts like ::: {.callout-note} or ::: {.content-block}
        callout_pattern = r'(:::?\s*\{[^}]*\}.*?:::?)'
        
        callout_replacements = {}
        counter = 0
        
        def replace_callout(match):
            nonlocal counter
            placeholder = f"__CALLOUT_PLACEHOLDER_{counter}__"
            callout_replacements[placeholder] = match.group(1)
            counter += 1
            return placeholder
            
        # Replace callouts with placeholders
        protected_content = re.sub(callout_pattern, replace_callout, content, flags=re.DOTALL)
        
        return protected_content, callout_replacements
    
    @staticmethod
    def restore_callouts_after_processing(content: str, callout_replacements: Dict[str, str]) -> str:
        """Restore callouts after processing is complete.
        
        Args:
            content: The processed content with placeholders
            callout_replacements: Dictionary mapping placeholders to original callouts
            
        Returns:
            Content with callouts restored
        """
        if not callout_replacements:
            return content
            
        restored_content = content
        for placeholder, original_callout in callout_replacements.items():
            restored_content = restored_content.replace(placeholder, original_callout)
            
        return restored_content


__all__ = [
    '_load_cached_config',
    'ContentProcessor'
]
