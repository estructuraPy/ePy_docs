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

from ePy_docs.core.quarto import (
    generate_quarto_config,
    create_quarto_yml
)
from ePy_docs.components.page import get_config_value


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


def cleanup_quarto_files_directories(base_filename: str, file_path: str = None) -> None:
    """Clean up any Quarto-generated _files directories.
    
    Args:
        base_filename: Base filename (without extension) used for the report
        file_path: Optional original file path for additional cleanup patterns
    """
    try:
        # Check for various possible _files directories
        directory = os.path.dirname(base_filename) if os.path.dirname(base_filename) else "."
        basename_only = os.path.basename(base_filename)
        
        # Possible patterns for _files directories
        files_patterns = [
            f"{basename_only}_files"
        ]
        
        # Add additional pattern if file_path is provided
        if file_path:
            files_patterns.append(f"{os.path.basename(file_path).split('.')[0]}_files")
        
        for pattern in files_patterns:
            files_dir = os.path.join(directory, pattern)
            if os.path.exists(files_dir) and os.path.isdir(files_dir):
                shutil.rmtree(files_dir)
    except Exception:
        # Silent cleanup - don't fail if we can't clean up
        pass


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
    
    # Create _quarto.yml
    create_quarto_yml(output_dir, chapter_files, sync_json, citation_style='apa')
    
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
        from ePy_docs.components.page import get_references_config
        reference_config = get_references_config()
        reference_settings = reference_config['reference_settings']
        
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
    
    def _cleanup_quarto_files_directory(self, qmd_path: str) -> None:
        """Clean up Quarto-generated _files directory.
        
        Args:
            qmd_path: Path to the QMD file that was rendered
        """
        try:
            qmd_dir = os.path.dirname(qmd_path)
            qmd_basename = os.path.splitext(os.path.basename(qmd_path))[0]
            files_dir = os.path.join(qmd_dir, f"{qmd_basename}_files")
            
            if os.path.exists(files_dir) and os.path.isdir(files_dir):
                shutil.rmtree(files_dir)
        except Exception:
            # Silent cleanup - don't fail if we can't clean up
            pass
    
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
        
        # Only use the exact name specified in JSON - no alternatives with hyphens
        generated_pdf = None
        # Use the original basename for the final PDF name (preserving spaces as specified in JSON)
        final_pdf = os.path.join(output_dir, f"{qmd_basename}.pdf")
        
        # Buscar únicamente el archivo con el nombre exacto especificado
        expected_pdf = os.path.join(os.path.dirname(qmd_path), f"{qmd_basename}.pdf")
        if os.path.exists(expected_pdf):
            generated_pdf = expected_pdf
        
        try:
            # Run quarto render command with explicit PDF format and output filename
            # Force Quarto to use the exact filename we want
            result = subprocess.run(
                ['quarto', 'render', qmd_path, '--to', 'pdf', '--output', f"{qmd_basename}.pdf"],
                cwd=os.path.dirname(qmd_path),
                capture_output=True,
                text=True,
                check=True
            )
            
            # Verificar que el PDF se generó con el nombre correcto
            generated_pdf = os.path.join(os.path.dirname(qmd_path), f"{qmd_basename}.pdf")
            
            # Move PDF to desired output directory if different
            if output_dir != os.path.dirname(qmd_path) and os.path.exists(generated_pdf):
                shutil.move(generated_pdf, final_pdf)
            elif os.path.exists(generated_pdf):
                final_pdf = generated_pdf
            else:
                # Si no se encontró el PDF con el nombre exacto, reportar error
                raise FileNotFoundError(f"PDF not generated with expected name: {generated_pdf}")
            
            if not os.path.exists(final_pdf):
                # Enhanced error message with more diagnostic information
                error_details = []
                error_details.append(f"Generated PDF path: {generated_pdf}")
                error_details.append(f"Final PDF path: {final_pdf}")
                error_details.append(f"QMD file: {qmd_path}")
                error_details.append(f"Output directory: {output_dir}")
                
                # Check if Quarto generated any output
                if result.stdout:
                    error_details.append(f"Quarto stdout: {result.stdout}")
                if result.stderr:
                    error_details.append(f"Quarto stderr: {result.stderr}")
                
                # List files in the QMD directory to see what was generated
                qmd_dir = os.path.dirname(qmd_path)
                if os.path.exists(qmd_dir):
                    files_in_dir = os.listdir(qmd_dir)
                    error_details.append(f"Files in QMD directory: {files_in_dir}")
                
                error_msg = "PDF was not generated successfully. Details:\n" + "\n".join(error_details)
                raise RuntimeError(error_msg)
            
            # Clean up Quarto-generated _files directory
            self._cleanup_quarto_files_directory(qmd_path)
            
            return final_pdf
            
        except subprocess.CalledProcessError as e:
            # Enhanced error reporting for subprocess failures
            error_details = []
            error_details.append(f"Command: {' '.join(e.cmd)}")
            error_details.append(f"Return code: {e.returncode}")
            if e.stdout:
                error_details.append(f"Stdout: {e.stdout}")
            if e.stderr:
                error_details.append(f"Stderr: {e.stderr}")
            
            # Check if Quarto is available
            try:
                version_result = subprocess.run(['quarto', '--version'], capture_output=True, text=True)
                error_details.append(f"Quarto version: {version_result.stdout.strip()}")
            except FileNotFoundError:
                error_details.append("Quarto command not found - please install Quarto")
            
            error_msg = "Quarto render failed. Details:\n" + "\n".join(error_details)
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
            
            # Clean up Quarto-generated _files directory
            self._cleanup_quarto_files_directory(qmd_path)
            
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
                    # Also clean up any associated _files directory
                    try:
                        self._cleanup_quarto_files_directory(temp_qmd)
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
                    # Also clean up any associated _files directory
                    try:
                        self._cleanup_quarto_files_directory(temp_qmd)
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
        
        This method should make minimal changes to preserve user-written
        Quarto-compatible markdown exactly as intended.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Processed content ready for Quarto
        """
        # Import ContentProcessor to use callout protection
        from ePy_docs.core.content import ContentProcessor
        
        # Normalize line endings only
        content = content.replace('\r\n', '\n')
        
        # Protect callouts before applying any processing
        protected_content, callout_replacements = ContentProcessor.protect_callouts_from_header_processing(content)
        
        # Apply only minimal, necessary fixes for edge cases
        # Only fix severely malformed equations with excessive spaces
        protected_content = re.sub(r'\$ {2,}([^$]+?) {2,}\$', r'$\1$', protected_content)
        
        # Restore callouts after processing
        protected_content = ContentProcessor.restore_callouts_after_processing(protected_content, callout_replacements)
        
        return protected_content