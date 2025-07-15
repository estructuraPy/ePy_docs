"""Content processor for ePy_docs report generation.

Handles formatting, styling, and content optimization for markdown and PDF outputs.
Moved from writer/process.py to provide shared content processing capabilities.
"""

import re
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

from ePy_docs.files.data import _load_cached_json
from ePy_docs.files.reader import ReadFiles
from ePy_docs.project.setup import DirectoryConfig
from ePy_docs.core.text import TextFormatter


def _load_cached_config(config_type: str) -> Dict[str, Any]:
    """Load configuration with caching to avoid redundant file operations.

    Args:
        config_type: Type of configuration to load ('colors', 'reports', etc.).

    Returns:
        Dictionary containing configuration data.

    Assumptions:
        ReadFiles and DirectoryConfig are available for loading configuration.
        Configuration files follow expected JSON structure.
    """
    try:
        config = DirectoryConfig()

        if config_type == "colors":
            colors_path = os.path.join(config.folders.templates, "colors.json")
            if os.path.exists(colors_path):
                return _load_cached_json(colors_path)
            else:
                return {}
        else:
            return {}

    except Exception as e:
        print(f"Warning: Could not load {config_type} configuration: {e}")
        return {}


class ContentProcessor:
    """Enhanced content processor for better report formatting.

    Provides content transformation methods for markdown to HTML conversion,
    text cleaning, and formatting optimization for different output formats.

    Assumptions:
        Input content follows standard markdown conventions
        HTML output is compatible with target rendering systems
        Configuration files are available for styling and formatting
    """

    @staticmethod
    def clean_html_for_reportlab(content: str) -> str:
        """Clean HTML content to be compatible with ReportLab.

        Args:
            content: HTML content to clean for ReportLab compatibility

        Returns:
            Cleaned HTML content with simplified tags and attributes

        Assumptions:
            Input content contains valid HTML markup
            ReportLab has specific requirements for supported HTML elements
        """
        if not isinstance(content, str):
            return str(content)

        pattern = r'<img[^>]*src="([^"]*)"[^>]*/>'
        replacement = r'<img src="\1"/>'
        content = re.sub(pattern, replacement, content)

        # Preserve styles related to page breaks and alignment but clean other unused styles
        # First, save important styles in a new attribute
        content = re.sub(
            r'style="([^"]*?(page-break|break-inside|align)[^"]*?)"', 
            r'data-keep-style="\1"', 
            content
        )
        
        # Remove all regular styles
        content = re.sub(r'\s*style="[^"]*"', '', content)
        
        # Restore the important styles we saved
        content = re.sub(r'data-keep-style="([^"]*)"', r' style="\1"', content)
        
        # Remove other unnecessary attributes
        content = re.sub(r'\s*class="[^"]*"', '', content)
        content = re.sub(r'\s*id="[^"]*"', '', content)

        return content.strip()

    @staticmethod
    def enhance_unit_display(content: str) -> str:
        """Enhance the display of units with emojis and better formatting.
        
        Args:
            content: Content with unit information
            
        Returns:
            Content with enhanced unit display including emojis
        """
        # Define unit emojis mapping
        unit_emojis = {
            "Length unit:": "📏 Length unit:",
            "Area unit:": "📐 Area unit:",
            "Volume unit:": "📦 Volume unit:", 
            "Force unit:": "🏋️ Force unit:",
            "Moment unit:": "⚖️ Moment unit:",
            # Add more unit types as needed
            "Pressure unit:": "🔄 Pressure unit:",
            "Mass unit:": "⚖️ Mass unit:",
            "Time unit:": "⏱️ Time unit:",
            "Temperature unit:": "🌡️ Temperature unit:",
            "Energy unit:": "⚡ Energy unit:",
            "Power unit:": "💪 Power unit:",
            "Velocity unit:": "🏃 Velocity unit:",
            "Acceleration unit:": "🚀 Acceleration unit:",
            "Angle unit:": "📐 Angle unit:",
            "Density unit:": "🧱 Density unit:"
        }
        
        # Fix line breaks in unit specifications that appear as 'n '
        # This pattern specifically targets the units section format
        content = re.sub(r'n ([A-Z][a-z]+ unit:)', r'\n\1', content)
        
        # Add proper spacing to ensure each unit appears on its own line
        for unit_key in unit_emojis.keys():
            # Replace any instances where units don't have proper spacing
            content = re.sub(f'([.\\w])({unit_key})', r'\1\n\n\2', content)
        
        # Fix superscripts for common unit notations
        # Convert basic number superscripts
        content = re.sub(r'([a-zA-Z])2\b', r'\1²', content)  # m2 -> m²
        content = re.sub(r'([a-zA-Z])3\b', r'\1³', content)  # m3 -> m³
        
        # Convert caret notation (like m^2) to proper superscripts
        superscript_map = {
            '^1': '¹', '^2': '²', '^3': '³', '^4': '⁴', '^5': '⁵',
            '^6': '⁶', '^7': '⁷', '^8': '⁸', '^9': '⁹', '^0': '⁰',
            '^-1': '⁻¹', '^-2': '⁻²', '^-3': '⁻³'
        }
        for caret, sup in superscript_map.items():
            content = content.replace(caret, sup)
        
        # Replace unit labels with emoji versions
        for unit_text, emoji_text in unit_emojis.items():
            content = content.replace(unit_text, emoji_text)
        
        # Add proper indentation for units in lists
        content = re.sub(r'\n([📏📐📦🏋️⚖️🔄⏱️🌡️⚡💪🚀])', r'\n    \1', content)
        
        return content

    @staticmethod
    def markdown_to_html_for_pdf(content: str) -> str:
        """Convert Markdown to HTML for PDF generation, preserving formatting combinations.

        This method handles cases where bullet points, bold text and notes coexist.
        It protects callouts from header processing to avoid promoting callout headers to document level.

        Args:
            content: Markdown content to convert to HTML.

        Returns:
            HTML content optimized for PDF generation.

        Assumptions:
            Input content follows standard markdown syntax.
            Target PDF system supports basic HTML elements.
        """
        if not isinstance(content, str):
            return str(content)
            
        # First protect callouts from header processing
        protected_content, callout_replacements = ContentProcessor.protect_callouts_from_header_processing(content)
        
        # Then enhance unit display with emojis and better formatting
        protected_content = ContentProcessor.enhance_unit_display(protected_content)
        
        # Preserve meaningful line breaks (double newlines) in HTML
        # This keeps paragraph breaks while avoiding too many <br/> tags
        protected_content = re.sub(r'\n\n', '<br/><br/>\n\n', protected_content)
        
        # For unit lists specifically, ensure they are preserved with proper spacing
        protected_content = re.sub(r'\n    (📏|📐|📦|🏋️|⚖️|🔄|⏱️|🌡️|⚡|💪|🚀)', r'<br/>\n    \1', protected_content)

        protected_content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', protected_content)
        protected_content = re.sub(r'(?<!\*)\*([^\*]+?)\*(?!\*)', r'<i>\1</i>', protected_content)
        protected_content = re.sub(r'`(.*?)`', r'<code>\1</code>', protected_content)

        lines = protected_content.split('\n')
        processed_lines = []
        in_list = False
        in_numbered_list = False

        for line in lines:
            # Handle headers - preserve them as-is for later processing
            # Note: Headers inside callouts are now protected by placeholders
            if line.strip().startswith(('#', '##', '###')):
                if in_list:
                    processed_lines.append('</ul>')
                    in_list = False
                if in_numbered_list:
                    processed_lines.append('</ol>')
                    in_numbered_list = False
                processed_lines.append(line)
            # Handle bullet lists
            elif line.strip().startswith('- '):
                if in_numbered_list:
                    processed_lines.append('</ol>')
                    in_numbered_list = False
                if not in_list:
                    processed_lines.append('<ul>')
                    in_list = True
                item_text = line.strip()[2:]
                processed_lines.append(f'<li>{item_text}</li>')
            # Handle numbered lists
            elif re.match(r'^\s*\d+\.\s+', line):
                if in_list:
                    processed_lines.append('</ul>')
                    in_list = False
                if not in_numbered_list:
                    processed_lines.append('<ol>')
                    in_numbered_list = True
                item_text = re.sub(r'^\s*\d+\.\s+', '', line)
                processed_lines.append(f'<li>{item_text}</li>')
            else:
                if in_list:
                    processed_lines.append('</ul>')
                    in_list = False
                if in_numbered_list:
                    processed_lines.append('</ol>')
                    in_numbered_list = False
                processed_lines.append(line)

        if in_list:
            processed_lines.append('</ul>')
        if in_numbered_list:
            processed_lines.append('</ol>')

        content = '\n'.join(processed_lines)

        content = re.sub(r'(?m)^>\s*\*\*(Note|Warning|Error|Success|Tip):\*\*\s*(.*?)\s*$',
                        r'<div class="note-\1"><b>\1:</b> \2</div>',
                        content)

        # Finally, restore the callouts with their original content
        content = ContentProcessor.restore_callouts_after_processing(content, callout_replacements)

        return content

    @staticmethod
    def smart_content_formatter(content: str) -> str:
        """Enhanced formatting for content with better markdown preservation for notes.

        Args:
            content: Raw content to format.

        Returns:
            Formatted content with enhanced markdown preservation and cleanup.

        Assumptions:
            TextFormatter methods are available and functional.
            Content follows standard text formatting conventions.
        """
        if not isinstance(content, str):
            return str(content)

        if not content or len(content.strip()) < 10:
            return content.strip()

        # Apply basic markdown formatting first
        content = TextFormatter.format_markdown_text(content)
        
        # Process superscripts for better display
        content = TextFormatter.process_superscripts_for_text(content)
        
        # Enhanced handling for bullet points and lists with better markdown preservation
        if TextFormatter.has_bullet_points(content):
            lines = content.split('\n')
            formatted_lines = []
            for line in lines:
                stripped = line.strip()
                # Preserve bullet formatting but clean up spacing
                if stripped.startswith(('• ', '* ', '- ')):
                    # Normalize bullet symbols to markdown dash for compatibility
                    item_text = stripped[2:].strip()
                    formatted_lines.append(f"- {item_text}")
                elif re.match(r'^\d+\.\s+', stripped):
                    # PRESERVE numbered lists exactly as they are
                    formatted_lines.append(stripped)
                elif stripped:  # Non-empty line without bullet
                    formatted_lines.append(stripped)
                else:  # Empty line - preserve for paragraph breaks
                    formatted_lines.append('')
            content = '\n'.join(formatted_lines)
        
        # Preserve markdown headers for note processing
        # Clean up excessive whitespace but preserve meaningful line breaks
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # Max 2 consecutive newlines
        content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces to single space
        
        return content.strip()

    @staticmethod
    def load_report_colors() -> Optional[Dict[str, Any]]:
        """Load colors configuration for reports using cached loading.

        Returns:
            Dictionary containing color configuration for reports or None if not found.

        Assumptions:
            Color configuration files follow expected JSON structure.
        """
        colors_config = _load_cached_config('colors')
        
        if colors_config:
            return colors_config

        print("Warning: No color configuration loaded")
        return None

    @staticmethod
    def get_note_config(note_type: str) -> Optional[Dict[str, str]]:
        """Get configuration for note formatting.

        Args:
            note_type: Type of note formatting to retrieve

        Returns:
            Dictionary containing color and icon configuration for the note type or None if not found

        Assumptions:
            Note types follow standard categorization (note, warning, error, success)
            Color and icon values are properly formatted for target output system
        """
        try:
            colors_config = _load_cached_config('colors')
            if colors_config and 'notes' in colors_config:
                note_config = colors_config['notes'].get(note_type)
                if note_config:
                    return note_config
        except Exception:
            pass
            
        print(f"Warning: No note configuration found for {note_type}")
        return None

    @staticmethod
    def format_content(content: str) -> str:
        """Formatear contenido para salida Quarto.
        
        Args:
            content: Contenido sin procesar
            
        Returns:
            Contenido formateado listo para Quarto
        """
        if not isinstance(content, str):
            return str(content)

        # Primero proteger los callouts
        protected_content = content

        # Ajustar títulos y referencias de tablas
        protected_content = re.sub(
            r'(!\[\]\([^)]+\)\{#(?:tbl|fig)-[^}]+\})\s*:\s*([^\n]+)',
            r'\1\n\n: \2\n',
            protected_content
        )

        # Ajustar ecuaciones
        protected_content = re.sub(
            r'\$\$([\s\S]*?)\$\$\s*(\{#[^}]+\})',
            r'$$\n\1\n$$ \2',
            protected_content
        )

        # Remover líneas en blanco excesivas pero preservar espaciado entre bloques
        protected_content = re.sub(r'\n{3,}', '\n\n', protected_content)
        
        # Asegurarse de que los títulos tengan espacio adecuado
        protected_content = re.sub(r'\n(#+ .*)\n([^\n])', r'\n\1\n\n\2', protected_content)

        return protected_content.strip()

    @staticmethod
    def protect_callouts_from_header_processing(content: str) -> tuple[str, dict]:
        """Proteger los callouts de Quarto durante el procesamiento.
        
        Args:
            content: Contenido que puede contener callouts
            
        Returns:
            Tupla de (contenido_protegido, reemplazos_callouts)
        """
        if not isinstance(content, str):
            return str(content), {}
            
        callout_replacements = {}
        protected_content = content
        
        # Patrón para identificar callouts de Quarto
        # Busca bloques que empiecen con ::: {.callout-tipo} y terminen con :::
        callout_pattern = r':::\s*\{[^}]+\}.*?:::'
        
        callout_matches = re.finditer(callout_pattern, content, re.DOTALL)
        
        replacement_counter = 0
        for match in callout_matches:
            replacement_counter += 1
            callout_content = match.group(0)
            placeholder = f"__CALLOUT_{replacement_counter}__"
            callout_replacements[placeholder] = callout_content
            protected_content = protected_content.replace(callout_content, placeholder, 1)
        
        return protected_content, callout_replacements

    @staticmethod
    def restore_callouts_after_processing(content: str, callout_replacements: dict) -> str:
        """Restaurar los callouts después del procesamiento.
        
        Args:
            content: Contenido con placeholders de callouts
            callout_replacements: Diccionario con los reemplazos originales
            
        Returns:
            Contenido con los callouts restaurados
        """
        if not isinstance(content, str) or not callout_replacements:
            return content
            
        restored_content = content
        for placeholder, original_content in callout_replacements.items():
            restored_content = restored_content.replace(placeholder, original_content)
            
        return restored_content

    def generate(self) -> str:
        """Generar contenido final procesado.
        
        Returns:
            Contenido final procesado y formateado
        """
        # Proteger los callouts antes del procesamiento 
        protected_content = self.protect_callouts_from_header_processing(self.raw_content)

        # Aplicar formateo de contenido
        formatted_content = self.format_content(protected_content)

        # Restaurar los callouts después del procesamiento
        final_content = self.restore_callouts_after_processing(formatted_content)

        # Asegurarse de que hay una línea en blanco al final
        if not final_content.endswith('\n'):
            final_content += '\n'
            
        return final_content
