"""Equation processing module for ePy_docs.

Handles LaTeX equation formatting, numbering, and Quarto-compatible output.
Provides specialized functionality for mathematical content in technical documents.
"""

import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class EquationProcessor(BaseModel):
    """Processor for LaTeX equations with Quarto compatibility."""
    
    equation_counter: int = Field(default=0, description="Counter for equation numbering")
    
    def increment_counter(self) -> int:
        """Increment and return the equation counter."""
        self.equation_counter += 1
        return self.equation_counter
    
    def format_equation(self, latex_code: str, label: str = None, caption: str = None) -> Dict[str, str]:
        """Format a single equation for Quarto rendering.
        
        Args:
            latex_code: Raw LaTeX equation code
            label: Optional label for cross-referencing
            caption: Optional caption for the equation
            
        Returns:
            Dictionary with formatted equation parts
        """
        # Clean and normalize the LaTeX code
        clean_latex = self._clean_latex_code(latex_code)
        
        # Generate label if not provided
        if label is None:
            counter = self.increment_counter()
            label = f"eq-{counter:03d}"
        
        # Format for Quarto
        equation_text = f"$$\n{clean_latex}\n$$ {{#{label}}}"
        
        result = {
            'equation': equation_text,
            'label': label,
            'counter': self.equation_counter
        }
        
        if caption:
            result['caption'] = caption
            
        return result
    
    def format_equation_block(self, equations: List[str], label: str = None, 
                            caption: str = None, align: bool = True) -> Dict[str, str]:
        """Format multiple equations as a block.
        
        Args:
            equations: List of LaTeX equation strings
            label: Optional label for cross-referencing
            caption: Optional caption for the equation block
            align: Whether to align the equations
            
        Returns:
            Dictionary with formatted equation block
        """
        if not equations:
            raise ValueError("Equations list cannot be empty")
        
        # Generate label if not provided
        if label is None:
            counter = self.increment_counter()
            label = f"eq-{counter:03d}"
        
        # Clean all equations
        clean_equations = [self._clean_latex_code(eq) for eq in equations]
        
        if align and len(clean_equations) > 1:
            # Use align environment for multiple equations
            equation_content = "\\begin{align}\n"
            for i, eq in enumerate(clean_equations):
                if i < len(clean_equations) - 1:
                    equation_content += f"{eq} \\\\\n"
                else:
                    equation_content += f"{eq}\n"
            equation_content += "\\end{align}"
        else:
            # Single equation or unaligned block
            equation_content = "\n".join(clean_equations)
        
        # Format for Quarto
        equation_text = f"$$\n{equation_content}\n$$ {{#{label}}}"
        
        result = {
            'equation': equation_text,
            'label': label,
            'counter': self.equation_counter,
            'is_block': True
        }
        
        if caption:
            result['caption'] = caption
            
        return result
    
    def format_inline_equation(self, latex_code: str) -> str:
        """Format an inline equation (not numbered).
        
        Args:
            latex_code: Raw LaTeX equation code
            
        Returns:
            Formatted inline equation string
        """
        clean_latex = self._clean_latex_code(latex_code)
        
        # Use single $ for inline math (not numbered)
        if clean_latex.startswith('$') and clean_latex.endswith('$'):
            return clean_latex
        else:
            return f"${clean_latex}$"
    
    def _clean_latex_code(self, latex_code: str) -> str:
        """Clean and normalize LaTeX code.
        
        Args:
            latex_code: Raw LaTeX code
            
        Returns:
            Cleaned LaTeX code
        """
        if not latex_code:
            raise ValueError("LaTeX code cannot be empty")
        
        # Normalize line endings
        clean_code = latex_code.replace('\r\n', '\n').strip()
        
        # Check if it's a multiline equation
        lines = clean_code.split('\n')
        if len(lines) > 1:
            # If multiline, check if first and last lines are $$ markers
            if lines[0].strip() == '$$' and lines[-2].strip().startswith('$$'):
                # Extract label if present in last line
                last_line = lines[-2].strip()
                label_part = ''
                if '{#' in last_line:
                    label_part = last_line[last_line.index('$$') + 2:].strip()
                # Join the content lines, preserving internal formatting
                content_lines = [line.rstrip() for line in lines[1:-1]]
                # Remove empty lines at start and end but preserve internal empty lines
                while content_lines and not content_lines[0].strip():
                    content_lines.pop(0)
                while content_lines and not content_lines[-1].strip():
                    content_lines.pop()
                return ' '.join(line.strip() for line in content_lines if line.strip())
        
        # Handle single line cases
        if clean_code.startswith('$$') and clean_code.endswith('$$'):
            clean_code = clean_code[2:-2].strip()
        elif clean_code.startswith('$') and clean_code.endswith('$'):
            clean_code = clean_code[1:-1].strip()
        
        return clean_code
    
    def create_equation_reference(self, ref_id: str, custom_text: str = None) -> str:
        """Create a cross-reference to an equation.
        
        Args:
            ref_id: Reference ID of the equation
            custom_text: Optional custom text for the reference
            
        Returns:
            Formatted cross-reference string
        """
        if custom_text:
            return f"[{custom_text}](#{ref_id})"
        else:
            return f"@{ref_id}"
    
    def get_equation_markdown(self, formatted_equation: Dict[str, str]) -> str:
        """Convert formatted equation dictionary to markdown string.
        
        Args:
            formatted_equation: Dictionary from format_equation or format_equation_block
            
        Returns:
            Complete markdown string for the equation
        """
        equation_text = formatted_equation['equation']
        caption = formatted_equation.get('caption')
        
        if caption:
            return f"\n\n{equation_text}\n\n: {caption}\n\n"
        else:
            return f"\n\n{equation_text}\n\n"


# Convenience functions for direct use
def create_equation(latex_code: str, label: str = None, caption: str = None, 
                   processor: EquationProcessor = None) -> str:
    """Create a formatted equation string.
    
    Args:
        latex_code: LaTeX equation code
        label: Optional label for cross-referencing
        caption: Optional caption
        processor: Optional processor instance (creates new if None)
        
    Returns:
        Complete markdown string for the equation
    """
    if processor is None:
        processor = EquationProcessor()
    
    formatted = processor.format_equation(latex_code, label, caption)
    return processor.get_equation_markdown(formatted)


def create_equation_block(equations: List[str], label: str = None, caption: str = None,
                         align: bool = True, processor: EquationProcessor = None) -> str:
    """Create a formatted equation block string.
    
    Args:
        equations: List of LaTeX equation strings
        label: Optional label for cross-referencing
        caption: Optional caption
        align: Whether to align equations
        processor: Optional processor instance (creates new if None)
        
    Returns:
        Complete markdown string for the equation block
    """
    if processor is None:
        processor = EquationProcessor()
    
    formatted = processor.format_equation_block(equations, label, caption, align)
    return processor.get_equation_markdown(formatted)


def create_inline_equation(latex_code: str, processor: EquationProcessor = None) -> str:
    """Create an inline equation string.
    
    Args:
        latex_code: LaTeX equation code
        processor: Optional processor instance (creates new if None)
        
    Returns:
        Formatted inline equation string
    """
    if processor is None:
        processor = EquationProcessor()
    
    return processor.format_inline_equation(latex_code)


def create_equation_reference(ref_id: str, custom_text: str = None) -> str:
    """Create a cross-reference to an equation.
    
    Args:
        ref_id: Reference ID of the equation
        custom_text: Optional custom text for the reference
        
    Returns:
        Formatted cross-reference string
    """
    processor = EquationProcessor()
    return processor.create_equation_reference(ref_id, custom_text)