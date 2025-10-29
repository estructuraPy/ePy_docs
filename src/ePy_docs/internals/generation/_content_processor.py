"""Content processing utilities for Quarto document generation.

Handles callout protection and text manipulation during document processing.
"""


class ContentProcessor:
    """Content processing utilities for callout protection and text manipulation."""
    
    @staticmethod
    def protect_callouts_from_header_processing(content: str):
        """Protect Quarto callouts from header processing.
        
        Args:
            content: Raw content string
            
        Returns:
            Tuple of (protected_content, callout_replacements)
        """
        import re
        
        # Find all callout blocks
        callout_pattern = r':::\{([^}]*)\}\s*\n(.*?)\n:::'
        callouts = re.findall(callout_pattern, content, re.DOTALL)
        
        # Create replacement tokens
        replacements = {}
        protected_content = content
        
        for i, (callout_type, callout_content) in enumerate(callouts):
            token = f"__CALLOUT_PROTECTED_{i}__"
            original_callout = f":::{{{callout_type}}}\n{callout_content}\n:::"
            replacements[token] = original_callout
            protected_content = protected_content.replace(original_callout, token, 1)
        
        return protected_content, replacements
    
    @staticmethod
    def restore_callouts_after_processing(content: str, callout_replacements: dict):
        """Restore protected callouts after processing.
        
        Args:
            content: Content with protected callout tokens
            callout_replacements: Dictionary mapping tokens to original callouts
            
        Returns:
            Content with callouts restored
        """
        restored_content = content
        
        for token, original_callout in callout_replacements.items():
            restored_content = restored_content.replace(token, original_callout)
        
        return restored_content
