"""
Quarto document writer for ePy_docs.

This module provides functionality to create and render Quarto documents
with all parameters sourced from JSON configuration files.
"""

import os
import shutil
import subprocess
import tempfile
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, Union, List

from ePy_docs.styler.quarto import (
    generate_quarto_config,
    copy_or_create_references,
    create_quarto_yml
)
from ePy_docs.styler.setup import get_config_value


def load_quarto_config() -> Dict[str, Any]:
    """Load quarto configuration from quarto.json"""
    config_path = os.path.join(os.path.dirname(__file__), 'quarto.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ValueError(f"quarto.json not found at {config_path}. Please ensure configuration file exists.")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in quarto.json: {e}")


def create_quarto_project(output_dir: str, 
                          markdown_content: Dict[str, str],
                          sync_json: bool = True) -> str:
    """Create a complete Quarto project structure.
    
    Args:
        output_dir: Path to output directory
        markdown_content: Dictionary of relative paths to markdown content
        sync_json: Whether to sync JSON files before reading configuration
        
    Returns:
        Path to created project directory
    
    Raises:
        ValueError: If markdown_content is empty or None
    """
    if not markdown_content:
        raise ValueError("markdown_content is required and cannot be empty")
    
    # Create the output directory structure
    output_path = Path(output_dir)
    chapters_dir = output_path / "chapters"
    references_dir = output_path / "references"
    
    # Create directories
    output_path.mkdir(parents=True, exist_ok=True)
    chapters_dir.mkdir(exist_ok=True)
    references_dir.mkdir(exist_ok=True)
    
    # Write provided content
    chapter_files = []
    for rel_path, content in markdown_content.items():
        file_path = output_path / rel_path
        file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Add to chapter files list for _quarto.yml if it's a qmd file
        if rel_path.endswith('.qmd'):
            chapter_files.append(rel_path)
    
    # Use centralized function to copy or create references
    copy_or_create_references(str(references_dir))
    
    # Create _quarto.yml
    create_quarto_yml(output_dir, chapter_files, sync_json)
    
    return str(output_path)


class QuartoConverter:
    """Coordinates Markdown conversion to PDF and HTML using Quarto."""
    
    def __init__(self):
        """Initialize the Quarto converter."""
        pass
        
    def _validate_markdown_content(self, markdown_content: Union[str, Path]) -> str:
        """Validate and prepare markdown content.
        
        Args:
            markdown_content: Markdown content as string or path to .md file
            
        Returns:
            Validated markdown content as string
        """
        if isinstance(markdown_content, (str, Path)) and os.path.isfile(markdown_content):
            with open(markdown_content, 'r', encoding='utf-8') as f:
                content = f.read()
        elif isinstance(markdown_content, str):
            content = markdown_content
        else:
            raise ValueError("markdown_content must be a string or path to a file")
            
        # Pre-process the content for Quarto
        return self._preprocess_markdown(content)
    
    def _create_qmd_content(self, 
                           markdown_content: str, 
                           yaml_config: Dict[str, Any],
                           sync_json: bool = True,
                           citation_style: Optional[str] = None) -> str:
        """Create complete QMD content with YAML header and markdown.
        
        Args:
            markdown_content: Markdown content
            yaml_config: YAML configuration dictionary
            sync_json: Whether to sync JSON files before reading configuration
            
        Returns:
            Complete QMD content as string
        """
        import yaml
        
        # If yaml_config is not provided, use project-based config
        if not yaml_config:
            yaml_config = generate_quarto_config(sync_json=sync_json, citation_style=citation_style)
        
        # Create YAML header
        yaml_header = "---\n"
        yaml_header += yaml.dump(yaml_config, default_flow_style=False, allow_unicode=True)
        yaml_header += "---\n\n"
        
        # Add references subtitle if configured
        from ePy_docs.styler.setup import get_styles_config
        styles_config = get_styles_config()
        reference_settings = styles_config['pdf_settings']['reference_settings']
        
        processed_content = markdown_content
        if reference_settings['add_subtitle'] and '@' in markdown_content:
            # Add references subtitle at the end
            processed_content += f"\n\n{reference_settings['title']}\n"
        
        # Combine with markdown content
        return yaml_header + processed_content
    
    def _check_quarto_installation(self) -> None:
        """Check if Quarto is installed and accessible."""
        try:
            result = subprocess.run(['quarto', '--version'], 
                                  capture_output=True, text=True, check=True)
            if not result.stdout.strip():
                raise FileNotFoundError
        except (FileNotFoundError, subprocess.CalledProcessError):
            raise RuntimeError(
                "Quarto is not installed or not accessible. "
                "Please install Quarto from https://quarto.org/docs/get-started/"
            )
    
    def markdown_to_qmd(self, 
                       markdown_content: Union[str, Path], 
                       title: str,
                       author: str,
                       output_file: Optional[str] = None,
                       sync_json: bool = True,
                       citation_style: Optional[str] = None) -> str:
        """Convert Markdown content to Quarto (.qmd) format.
        
        Args:
            markdown_content: Markdown content as string or path to .md file
            title: Document title (required)
            author: Document author (required)
            output_file: Optional output file path. If None, creates temporary file
            sync_json: Whether to sync JSON files before reading configuration
            
        Returns:
            Path to the created .qmd file
        """
        if not title:
            raise ValueError("title is required")
        if not author:
            raise ValueError("author is required")
        
        # Validate and get markdown content
        content = self._validate_markdown_content(markdown_content)
        
        # Get configuration
        yaml_config = generate_quarto_config(sync_json=sync_json, citation_style=citation_style)
        
        # Update title and author in config
        if 'book' in yaml_config:
            yaml_config['book']['title'] = title
            yaml_config['book']['author'] = author
        else:
            yaml_config['title'] = title
            yaml_config['author'] = author
        
        # Create complete QMD content
        qmd_content = self._create_qmd_content(content, yaml_config, sync_json=sync_json)
        
        # Determine output file path
        if output_file is None:
            temp_dir = tempfile.mkdtemp()
            output_file = os.path.join(temp_dir, f"{title.replace(' ', '_')}.qmd")
        else:
            output_file = os.path.abspath(output_file)
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write QMD file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(qmd_content)
            
        # Create references directory and copy necessary files
        output_dir = os.path.dirname(output_file)
        references_dir = os.path.join(output_dir, "references")
        os.makedirs(references_dir, exist_ok=True)
        
        # Copy or create references
        copy_or_create_references(references_dir)
        
        return output_file
    
    def render_to_pdf(self, qmd_file: str, output_dir: Optional[str] = None) -> str:
        """Render Quarto document to PDF.
        
        Args:
            qmd_file: Path to the .qmd file
            output_dir: Optional output directory. If None, uses same directory as qmd_file
            
        Returns:
            Path to the generated PDF file
        """
        self._check_quarto_installation()
        
        qmd_path = os.path.abspath(qmd_file)
        if not os.path.exists(qmd_path):
            raise FileNotFoundError(f"QMD file not found: {qmd_path}")
        
        # Determine output directory
        if output_dir is None:
            output_dir = os.path.dirname(qmd_path)
        else:
            output_dir = os.path.abspath(output_dir)
            os.makedirs(output_dir, exist_ok=True)
        
        # Get expected PDF output path
        qmd_basename = os.path.splitext(os.path.basename(qmd_path))[0]
        expected_pdf = os.path.join(os.path.dirname(qmd_path), f"{qmd_basename}.pdf")
        final_pdf = os.path.join(output_dir, f"{qmd_basename}.pdf")
        
        try:
            # Run quarto render command with explicit PDF format
            result = subprocess.run(
                ['quarto', 'render', qmd_path, '--to', 'pdf'],
                cwd=os.path.dirname(qmd_path),
                capture_output=True,
                text=True,
                check=True
            )
            
            # Move PDF to desired output directory if different
            if output_dir != os.path.dirname(qmd_path) and os.path.exists(expected_pdf):
                shutil.move(expected_pdf, final_pdf)
            elif os.path.exists(expected_pdf):
                final_pdf = expected_pdf
            
            if not os.path.exists(final_pdf):
                raise RuntimeError("PDF was not generated successfully")
            
            return final_pdf
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Quarto render failed: {e.stderr.strip() if e.stderr else 'Unknown error'}"
            raise RuntimeError(error_msg)
        except Exception as e:
            raise RuntimeError(f"Error during PDF rendering: {str(e)}")
    
    def render_to_html(self, qmd_file: str, output_dir: Optional[str] = None) -> str:
        """Render a Quarto document to HTML.
        
        Args:
            qmd_file: Path to the .qmd file to render
            output_dir: Optional output directory (defaults to same directory as QMD file)
            
        Returns:
            Path to the generated HTML file
        """
        self._check_quarto_installation()
        
        qmd_path = os.path.abspath(qmd_file)
        if not os.path.exists(qmd_path):
            raise FileNotFoundError(f"QMD file not found: {qmd_path}")
        
        # Determine output directory
        if output_dir is None:
            output_dir = os.path.dirname(qmd_path)
        else:
            output_dir = os.path.abspath(output_dir)
            os.makedirs(output_dir, exist_ok=True)
        
        # Get expected HTML output path
        qmd_basename = os.path.splitext(os.path.basename(qmd_path))[0]
        expected_html = os.path.join(os.path.dirname(qmd_path), f"{qmd_basename}.html")
        final_html = os.path.join(output_dir, f"{qmd_basename}.html")
        
        try:
            # Run quarto render command for HTML
            result = subprocess.run(
                ['quarto', 'render', qmd_path, '--to', 'html'],
                cwd=os.path.dirname(qmd_path),
                capture_output=True,
                text=True,
                check=True
            )
            
            # Move HTML to desired output directory if different
            if output_dir != os.path.dirname(qmd_path) and os.path.exists(expected_html):
                shutil.move(expected_html, final_html)
            elif os.path.exists(expected_html):
                final_html = expected_html
            
            if not os.path.exists(final_html):
                raise RuntimeError("HTML was not generated successfully")
            
            return final_html
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Quarto HTML render failed: {e.stderr.strip() if e.stderr else 'Unknown error'}"
            raise RuntimeError(error_msg)
        except Exception as e:
            raise RuntimeError(f"Error during HTML rendering: {str(e)}")
    
    def convert_markdown_to_pdf(self, 
                              markdown_content: Union[str, Path],
                              title: str,
                              author: str,
                              output_file: Optional[str] = None,
                              clean_temp: bool = True,
                              sync_json: bool = True,
                              citation_style: Optional[str] = None) -> str:
        """Complete conversion from Markdown to PDF using Quarto.
        
        Args:
            markdown_content: Markdown content as string or path to .md file
            title: Document title (required)
            author: Document author (required)
            output_file: Optional output PDF file path
            clean_temp: Whether to clean temporary files after conversion
            sync_json: Whether to sync JSON files before reading configuration
            
        Returns:
            Path to the generated PDF file
        """
        if not title:
            raise ValueError("title is required")
        if not author:
            raise ValueError("author is required")
        
        temp_qmd = None
        temp_dir = None
        
        try:
            # Create QMD file
            if output_file:
                # If output file is specified, create QMD in same directory
                pdf_path = os.path.abspath(output_file)
                qmd_dir = os.path.dirname(pdf_path)
                os.makedirs(qmd_dir, exist_ok=True)
                
                base_name = os.path.splitext(os.path.basename(pdf_path))[0]
                temp_qmd = os.path.join(qmd_dir, f"{base_name}.qmd")
            else:
                # Create temporary QMD file
                temp_dir = tempfile.mkdtemp()
                temp_qmd = os.path.join(temp_dir, f"{title.replace(' ', '_')}.qmd")
            
            # Convert to QMD
            qmd_file = self.markdown_to_qmd(
                markdown_content=markdown_content,
                title=title,
                author=author,
                output_file=temp_qmd,
                sync_json=sync_json,
                citation_style=citation_style
            )
            
            # Render to PDF
            if output_file:
                output_dir = os.path.dirname(os.path.abspath(output_file))
                pdf_path = self.render_to_pdf(qmd_file, output_dir)
                
                # Rename to desired output file name if different
                desired_pdf = os.path.abspath(output_file)
                if pdf_path != desired_pdf:
                    shutil.move(pdf_path, desired_pdf)
                    pdf_path = desired_pdf
            else:
                pdf_path = self.render_to_pdf(qmd_file)
            
            return pdf_path
            
        finally:
            # Clean up temporary files if requested
            if clean_temp:
                if temp_qmd and os.path.exists(temp_qmd):
                    try:
                        os.remove(temp_qmd)
                    except:
                        pass
                if temp_dir and os.path.exists(temp_dir):
                    try:
                        shutil.rmtree(temp_dir)
                    except:
                        pass

    def convert_markdown_to_html(self, 
                               markdown_content: Union[str, Path],
                               title: str,
                               author: str,
                               output_file: Optional[str] = None,
                               clean_temp: bool = True,
                               sync_json: bool = True,
                               citation_style: Optional[str] = None) -> str:
        """Complete conversion from Markdown to HTML using Quarto.
        
        Args:
            markdown_content: Markdown content as string or path to .md file
            title: Document title (required)
            author: Document author (required)
            output_file: Optional output HTML file path
            clean_temp: Whether to clean temporary files after conversion
            sync_json: Whether to sync JSON files before reading configuration
            
        Returns:
            Path to the generated HTML file
        """
        if not title:
            raise ValueError("title is required")
        if not author:
            raise ValueError("author is required")
        
        temp_qmd = None
        temp_dir = None
        
        try:
            # Create QMD file
            if output_file:
                # If output file is specified, create QMD in same directory
                html_path = os.path.abspath(output_file)
                qmd_dir = os.path.dirname(html_path)
                os.makedirs(qmd_dir, exist_ok=True)
                
                base_name = os.path.splitext(os.path.basename(html_path))[0]
                temp_qmd = os.path.join(qmd_dir, f"{base_name}.qmd")
            else:
                # Create temporary QMD file
                temp_dir = tempfile.mkdtemp()
                temp_qmd = os.path.join(temp_dir, f"{title.replace(' ', '_')}.qmd")
            
            # Convert to QMD
            qmd_file = self.markdown_to_qmd(
                markdown_content=markdown_content,
                title=title,
                author=author,
                output_file=temp_qmd,
                sync_json=sync_json,
                citation_style=citation_style
            )
            
            # Render to HTML
            if output_file:
                output_dir = os.path.dirname(os.path.abspath(output_file))
                html_path = self.render_to_html(qmd_file, output_dir)
                
                # Rename to desired output file name if different
                desired_html = os.path.abspath(output_file)
                if html_path != desired_html:
                    shutil.move(html_path, desired_html)
                    html_path = desired_html
            else:
                html_path = self.render_to_html(qmd_file)
            
            return html_path
            
        finally:
            # Clean up temporary files if requested
            if clean_temp:
                if temp_qmd and os.path.exists(temp_qmd):
                    try:
                        os.remove(temp_qmd)
                    except:
                        pass
                if temp_dir and os.path.exists(temp_dir):
                    try:
                        shutil.rmtree(temp_dir)
                    except:
                        pass

    def import_and_render_qmd(self, 
                             qmd_file: str,
                             output_format: str = "pdf",
                             output_dir: Optional[str] = None,
                             sync_json: bool = True) -> str:
        """Import and render an existing Quarto (.qmd) file.
        
        Args:
            qmd_file: Path to existing .qmd file
            output_format: Output format ("pdf" or "html")
            output_dir: Optional output directory (defaults to same directory as QMD file)
            sync_json: Whether to sync JSON files before reading configuration
            
        Returns:
            Path to the generated output file
            
        Raises:
            FileNotFoundError: If QMD file doesn't exist
            ValueError: If output format is not supported
        """
        qmd_path = os.path.abspath(qmd_file)
        if not os.path.exists(qmd_path):
            raise FileNotFoundError(f"QMD file not found: {qmd_path}")
        
        if not qmd_path.endswith('.qmd'):
            raise ValueError(f"File must have .qmd extension: {qmd_path}")
        
        if output_format.lower() not in ["pdf", "html"]:
            raise ValueError(f"Unsupported output format: {output_format}. Use 'pdf' or 'html'")
        
        # Ensure references are available in the QMD directory
        qmd_dir = os.path.dirname(qmd_path)
        references_dir = os.path.join(qmd_dir, "references")
        
        os.makedirs(references_dir, exist_ok=True)
        
        # Copy or create references
        copy_or_create_references(references_dir)
        
        # Render based on format
        if output_format.lower() == "pdf":
            output_path = self.render_to_pdf(qmd_path, output_dir)
        else:  # html
            output_path = self.render_to_html(qmd_path, output_dir)
        
        print(f"✅ Rendered {qmd_file} to {output_format.upper()}: {output_path}")
        return output_path

    def scan_and_render_directory(self, 
                                 directory: str,
                                 output_format: str = "pdf",
                                 output_dir: Optional[str] = None,
                                 recursive: bool = False,
                                 sync_json: bool = True,
                                 ignore_patterns: Optional[List[str]] = None) -> Dict[str, str]:
        """Scan directory for .qmd files and render them all.
        
        Args:
            directory: Directory path to scan for .qmd files
            output_format: Output format ("pdf" or "html")
            output_dir: Optional output directory (defaults to same directory as each QMD file)
            recursive: Whether to scan subdirectories recursively
            sync_json: Whether to sync JSON files before reading configuration
            ignore_patterns: Optional list of filename patterns to ignore (e.g., ['temp_*', '_*'])
            
        Returns:
            Dictionary mapping QMD file paths to output file paths
            
        Raises:
            FileNotFoundError: If directory doesn't exist
            ValueError: If output format is not supported
        """
        directory_path = os.path.abspath(directory)
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        if not os.path.isdir(directory_path):
            raise ValueError(f"Path is not a directory: {directory_path}")
        
        if output_format.lower() not in ["pdf", "html"]:
            raise ValueError(f"Unsupported output format: {output_format}. Use 'pdf' or 'html'")
        
        # Set ignore patterns from config or fail
        if ignore_patterns is None:
            ignore_patterns = get_config_value('files/formats/quarto.json', 'ignore_patterns', sync_json=sync_json)
            if not ignore_patterns:
                raise ValueError("ignore_patterns not found in configuration and not provided")
        
        # Find all .qmd files
        qmd_files = []
        
        if recursive:
            # Recursive search
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    if file.endswith('.qmd'):
                        # Check ignore patterns
                        should_ignore = False
                        for pattern in ignore_patterns:
                            if pattern.startswith('*'):
                                if file.endswith(pattern[1:]):
                                    should_ignore = True
                                    break
                            elif pattern.endswith('*'):
                                if file.startswith(pattern[:-1]):
                                    should_ignore = True
                                    break
                            elif pattern in file:
                                should_ignore = True
                                break
                        
                        if not should_ignore:
                            qmd_files.append(os.path.join(root, file))
        else:
            # Non-recursive search
            for file in os.listdir(directory_path):
                if file.endswith('.qmd'):
                    # Check ignore patterns
                    should_ignore = False
                    for pattern in ignore_patterns:
                        if pattern.startswith('*'):
                            if file.endswith(pattern[1:]):
                                should_ignore = True
                                break
                        elif pattern.endswith('*'):
                            if file.startswith(pattern[:-1]):
                                should_ignore = True
                                break
                        elif pattern in file:
                            should_ignore = True
                            break
                    
                    if not should_ignore:
                        qmd_files.append(os.path.join(directory_path, file))
        
        if not qmd_files:
            print(f"⚠️  No .qmd files found in {directory_path}")
            return {}
        
        print(f"📄 Found {len(qmd_files)} .qmd file(s) to render:")
        for qmd_file in qmd_files:
            print(f"  - {os.path.relpath(qmd_file, directory_path)}")
        
        # Render all files
        results = {}
        successful_renders = 0
        failed_renders = 0
        
        for qmd_file in qmd_files:
            try:
                # Determine output directory for this file
                if output_dir:
                    file_output_dir = output_dir
                else:
                    file_output_dir = os.path.dirname(qmd_file)
                
                output_path = self.import_and_render_qmd(
                    qmd_file=qmd_file,
                    output_format=output_format,
                    output_dir=file_output_dir,
                    sync_json=sync_json
                )
                
                results[qmd_file] = output_path
                successful_renders += 1
                
            except Exception as e:
                print(f"❌ Failed to render {qmd_file}: {e}")
                failed_renders += 1
        
        return results

    def _preprocess_markdown(self, content: str) -> str:
        """Pre-process markdown content before conversion to QMD.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Processed content ready for Quarto
        """
        # Import ContentProcessor to use callout protection
        from ePy_docs.core.content import ContentProcessor
        
        # Normalize line endings
        content = content.replace('\r\n', '\n')
        
        # Protect callouts before applying regex processing
        protected_content, callout_replacements = ContentProcessor.protect_callouts_from_header_processing(content)
        
        # Fix spacing around table and figure references
        protected_content = re.sub(
            r'(!\[\]\([^)]+\)\{#(?:tbl|fig)-[^}]+\})\s*\n+\s*:\s*([^\n]+)',
            r'\1\n\n: \2\n\n',
            protected_content
        )
        
        # Fix spacing around equation references
        protected_content = re.sub(
            r'(\$\$[^\$]+\$\$)\s*(\{#eq-[^}]+\})\s*\n+\s*:\s*([^\n]+)',
            r'\1 \2\n\n: \3\n\n',
            protected_content
        )
        
        # Fix spacing around inline equations
        protected_content = re.sub(r'\$\s+([^$]+)\s+\$', r'$\1$', protected_content)
        
        # Restore callouts after processing
        protected_content = ContentProcessor.restore_callouts_after_processing(protected_content, callout_replacements)
        
        # Preserve all blank lines to keep user-defined spacing intact
        # (remove aggressive blank-line collapsing and strip)
        # content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Return content as-is without stripping to maintain line breaks
        return protected_content