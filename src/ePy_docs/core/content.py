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
        config_type: Type of configuration to load ('colors', 'reports', 'units').

    Returns:
        Dictionary containing configuration data.

    Raises:
        ValueError: Si no se puede cargar la configuración requerida
    """
    config = DirectoryConfig()
    
    config_paths = {
        "colors": config.files.configuration.styling.colors_json,
        "units": os.path.join(config.folders.config, "units", "units.json"),
        "styles": config.files.configuration.styling.styles_json,
        "notes": os.path.join(config.folders.config, "components", "notes.json")
    }
    
    if config_type not in config_paths:
        raise ValueError(f"Unsupported configuration type: {config_type}")
    
    config_path = config_paths[config_type]
    
    if not os.path.exists(config_path):
        raise ValueError(f"Configuration file not found: {config_path}")
    
    return _load_cached_json(config_path)


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
            
        Raises:
            ValueError: Si no se puede cargar la configuración de unidades
        """
        units_config = _load_cached_config('units')
        
        if 'display' not in units_config:
            raise ValueError("Display configuration not found in units.json")
            
        display_config = units_config['display']
        unit_emojis = display_config['unit_emojis']
        superscripts = display_config['superscripts']
        formatting = display_config['formatting']
        
        # Fix line breaks in unit specifications that appear as 'n '
        content = re.sub(r'n ([A-Z][a-z]+ unit:)', r'\n\1', content)
        
        # Add proper spacing to ensure each unit appears on its own line
        for unit_key in unit_emojis.keys():
            content = re.sub(f'([.\\w])({re.escape(unit_key)})', r'\1\n\n\2', content)
        
        # Fix superscripts for common unit notations
        content = re.sub(r'([a-zA-Z])2\b', r'\1²', content)
        content = re.sub(r'([a-zA-Z])3\b', r'\1³', content)
        
        # Convert caret notation using configuration
        for caret, sup in superscripts.items():
            content = content.replace(caret, sup)
        
        # Replace unit labels with emoji versions
        for unit_text, emoji_text in unit_emojis.items():
            content = content.replace(unit_text, emoji_text)
        
        # Add proper indentation for units in lists using configuration
        emoji_patterns = '|'.join(re.escape(emoji) for emoji in formatting['unit_emoji_patterns'])
        if emoji_patterns:
            indentation = " " * formatting['indentation_spaces']
            content = re.sub(f'\\n({emoji_patterns})', f'\\n{indentation}\\1', content)
        
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

        Raises:
            ValueError: Si no se puede cargar la configuración necesaria
        """
        if not isinstance(content, str):
            return str(content)
            
        units_config = _load_cached_config('units')
        
        if 'display' not in units_config:
            raise ValueError("Display configuration not found in units.json")
            
        formatting = units_config['display']['formatting']
        emoji_patterns = formatting['unit_emoji_patterns']
        indentation_spaces = formatting['indentation_spaces']
            
        # First protect callouts from header processing
        protected_content, callout_replacements = ContentProcessor.protect_callouts_from_header_processing(content)
        
        # Then enhance unit display with emojis and better formatting
        protected_content = ContentProcessor.enhance_unit_display(protected_content)
        
        # Preserve meaningful line breaks (double newlines) in HTML
        # This keeps paragraph breaks while avoiding too many <br/> tags
        protected_content = re.sub(r'\n\n', '<br/><br/>\n\n', protected_content)
        
        # For unit lists specifically, ensure they are preserved with proper spacing using configuration
        if emoji_patterns:
            emoji_pattern = '|'.join(re.escape(emoji) for emoji in emoji_patterns)
            indentation = " " * indentation_spaces
            protected_content = re.sub(
                f'\\n{re.escape(indentation)}({emoji_pattern})', 
                f'<br/>\\n{indentation}\\1', 
                protected_content
            )

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

        Raises:
            ValueError: Si no se puede cargar la configuración necesaria o el contenido es inválido
        """
        if not isinstance(content, str):
            return str(content)

        if not content or len(content.strip()) < 1:
            return content.strip()

        units_config = _load_cached_config('units')
        
        if 'display' not in units_config:
            raise ValueError("Display configuration not found in units.json")
            
        formatting = units_config['display']['formatting']
        max_newlines = formatting['max_consecutive_newlines']

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
        
        # Clean up excessive whitespace but preserve meaningful line breaks using configuration
        if max_newlines > 0:
            pattern = f'\\n\\s*\\n\\s*\\n{{{max_newlines - 1},}}'
            replacement = '\n' * max_newlines
            content = re.sub(pattern, replacement, content)
            
        content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces to single space
        
        return content.strip()

    @staticmethod
    def load_report_colors() -> Dict[str, Any]:
        """Load colors configuration for reports using cached loading.

        Returns:
            Dictionary containing color configuration for reports.

        Raises:
            ValueError: Si no se puede cargar la configuración de colores
        """
        return _load_cached_config('colors')

    @staticmethod
    def get_note_config(note_type: str) -> Dict[str, str]:
        """Get configuration for note formatting.

        Args:
            note_type: Type of note formatting to retrieve

        Returns:
            Dictionary containing color and icon configuration for the note type

        Raises:
            ValueError: Si no se encuentra la configuración para el tipo de nota especificado
        """
        colors_config = _load_cached_config('colors')
        
        if 'reports' not in colors_config or 'notes' not in colors_config['reports']:
            raise ValueError("Notes configuration section not found in colors configuration")
        
        if note_type not in colors_config['reports']['notes']:
            raise ValueError(f"No note configuration found for type: {note_type}")
            
        return colors_config['reports']['notes'][note_type]

    @staticmethod
    def format_content(content: str) -> str:
        """Formatear contenido para salida Quarto.
        
        Args:
            content: Contenido sin procesar
            
        Returns:
            Contenido formateado listo para Quarto
            
        Raises:
            ValueError: Si no se puede cargar la configuración necesaria
        """
        if not isinstance(content, str):
            return str(content)

        units_config = _load_cached_config('units')
        
        if 'display' not in units_config:
            raise ValueError("Display configuration not found in units.json")
            
        formatting = units_config['display']['formatting']
        emoji_patterns = formatting['unit_emoji_patterns']
        max_newlines = formatting['max_consecutive_newlines']

        protected_content = content

        # Procesar tablas con sus títulos (van arriba)
        protected_content = re.sub(
            r'!\[\]\(([^)]+)\)(\{#tbl-([^}]+)\})\s*:\s*([^\n]+)?',
            lambda m: (
                f"\n{{{{< pagebreak >}}}}\n\n"
                f"::: {{.table-responsive}}\n"
                f"![{m.group(4) if m.group(4) else ''}]({m.group(1).replace(chr(92)+chr(92), '/').replace('//', '/')}){{#tbl-{m.group(3)} width=100%}}\n"
                f":::\n"
            ),
            protected_content
        )

        # Procesar figuras con sus títulos (van abajo) 
        protected_content = re.sub(
            r'!\[\]\(([^)]+)\)(\{#fig-([^}]+)\})\s*:\s*([^\n]+)?',
            lambda m: (
                f"![]({m.group(1).replace(chr(92)+chr(92), '/').replace('//', '/')})\n\n"
                f": Figura: {m.group(4) if m.group(4) else ''} {{#fig-{m.group(3)}}}\n"
            ),
            protected_content
        )

        # Asegurar que las tablas sin título mantienen el formato correcto
        protected_content = re.sub(
            r'!\[\]\(([^)]+)\)(\{#tbl-([^}]+)\})\s*$',
            lambda m: (
                f"\n{{{{< pagebreak >}}}}\n\n"
                f"::: {{.table-responsive}}\n"
                f"![Tabla]({m.group(1).replace(chr(92)+chr(92), '/').replace('//', '/')}){{#tbl-{m.group(3)} width=100%}}\n"
                f":::\n"
            ),
            protected_content
        )

        # Asegurar que las figuras sin título mantienen el formato correcto
        protected_content = re.sub(
            r'!\[\]\(([^)]+)\)(\{#fig-([^}]+)\})\s*$',
            lambda m: (
                f"![]({m.group(1).replace(chr(92)+chr(92), '/').replace('//', '/')})\n\n"
                f": Figura {{#fig-{m.group(3)}}}\n"
            ),
            protected_content
        )

        # Ajustar ecuaciones
        protected_content = re.sub(
            r'\$\$([\s\S]*?)\$\$\s*(\{#[^}]+\})',
            r'$$\n\1\n$$ \2',
            protected_content
        )

        # Asegurar que hay espacio entre emojis y expresiones LaTeX y normalizarlas
        protected_content = re.sub(
            r'([^\s])\$\$',
            r'\1 $$',
            protected_content
        )
        
        # Asegurar que los bloques de unidades con emojis estén bien formateados
        if emoji_patterns:
            emoji_pattern = '|'.join(re.escape(emoji) for emoji in emoji_patterns)
            protected_content = re.sub(
                f'(\\s*)({emoji_pattern})(.*?)\\$\\$(.*?)\\$\\$',
                r'\1\2\3 $$\4$$\n',
                protected_content,
                flags=re.MULTILINE
            )

        # Remover líneas en blanco excesivas usando configuración
        if max_newlines > 0:
            pattern = f'\\n{{{max_newlines + 1},}}'
            replacement = '\n' * max_newlines
            protected_content = re.sub(pattern, replacement, protected_content)
        
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

    @staticmethod
    def wrap_title_text(text: str, max_width_chars: Optional[int] = None) -> str:
        """Envolver texto de título con ancho máximo especificado.
        
        Args:
            text: Texto a envolver
            max_width_chars: Ancho máximo en caracteres. Si es None, se carga de configuración.
            
        Returns:
            Texto envuelto con saltos de línea apropiados
            
        Raises:
            ValueError: Si no se puede cargar la configuración cuando max_width_chars es None
        """
        if not isinstance(text, str):
            return str(text)
        
        if max_width_chars is None:
            units_config = _load_cached_config('units')
            
            if 'display' not in units_config:
                raise ValueError("Display configuration not found in units.json")
                
            formatting = units_config['display']['formatting']
            max_width_chars = formatting['max_title_width_chars']
            
        if len(text) <= max_width_chars:
            return text
            
        # Envolver el texto preservando palabras completas
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + len(current_line) <= max_width_chars:
                current_line.append(word)
                current_length += len(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
            
        return '\n'.join(lines)

    def __init__(self, raw_content: str = ""):
        """Inicializar el procesador de contenido.
        
        Args:
            raw_content: Contenido sin procesar
        """
        self.raw_content = raw_content

    def generate(self) -> str:
        """Generar contenido final procesado.
        
        Returns:
            Contenido final procesado y formateado
        """
        # Proteger los callouts antes del procesamiento 
        protected_content, callout_replacements = ContentProcessor.protect_callouts_from_header_processing(self.raw_content)

        # Aplicar formateo de contenido
        formatted_content = ContentProcessor.format_content(protected_content)

        # Restaurar los callouts después del procesamiento
        final_content = ContentProcessor.restore_callouts_after_processing(formatted_content, callout_replacements)

        # Asegurarse de que hay una línea en blanco al final
        if not final_content.endswith('\n'):
            final_content += '\n'
            
        return final_content
