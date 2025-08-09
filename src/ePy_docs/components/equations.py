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
            latex_code: Raw LaTeX equation code (can be multiline, preserves format)
            label: Optional label for cross-referencing
            caption: Optional caption for the equation
            
        Returns:
            Dictionary with formatted equation parts
        """
        # Clean and normalize the LaTeX code, but preserve multiline format
        clean_latex = self._clean_latex_code(latex_code)
        
        # Generate label automatically only if user didn't provide one
        if label is None:
            label = f"eq-{self.increment_counter()}"
        
        # Check if already properly formatted (single line with label)
        if (clean_latex.startswith('$$') and 
            clean_latex.endswith(f'$$ {{#{label}}}') and
            '\n' not in clean_latex):
            # Already in single line format - preserve as is
            equation_text = clean_latex
        else:
            # Format for Quarto - use compact multiline format that works
            if clean_latex.startswith('$$') and clean_latex.endswith('$$'):
                # Extract content between $$
                content = clean_latex[2:-2].strip()
                # Remove any existing label
                if '{#' in content and '}' in content:
                    content = re.sub(r'\s*\{#[^}]+\}', '', content).strip()
            else:
                content = clean_latex
            
            # Format for Quarto with compact spacing (this works)
            # Using the format: $$           \nF = ma         \n$$ {#eq-newton}
            equation_text = f"$$           \n{content}         \n$$ {{#{label}}}"
        
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
        
        # Generate label automatically only if user didn't provide one
        if label is None:
            label = f"eq-{self.increment_counter()}"
        
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
        
        # Format for Quarto with compact spacing
        equation_text = f"$$           \n{equation_content}         \n$$ {{#{label}}}"
        
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
        """Clean and normalize LaTeX code while preserving multiline structure.
        
        Args:
            latex_code: Raw LaTeX code
            
        Returns:
            Cleaned LaTeX code with preserved structure
        """
        if not latex_code:
            raise ValueError("LaTeX code cannot be empty")
        
        # Normalize line endings only
        clean_code = latex_code.replace('\r\n', '\n').strip()
        
        # Remove any existing inline labels from single line equations
        if '\n' not in clean_code and '{#' in clean_code:
            # Remove the label part for reprocessing
            clean_code = re.sub(r'\s*\{#[^}]+\}', '', clean_code).strip()
        
        # For multiline equations, preserve the structure completely
        if '\n' in clean_code:
            return clean_code
        
        # For single line equations, handle basic cleanup
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