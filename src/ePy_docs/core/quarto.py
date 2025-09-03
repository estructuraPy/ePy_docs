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

from ePy_docs.core.styler import (
    generate_quarto_config,
    create_quarto_yml
)
from ePy_docs.components.pages import get_config_value


def load_quarto_config() -> Dict[str, Any]:
    """Load quarto configuration from pages.json - respects sync_files from DirectoryConfigSettings.
    
    The sync_files setting is automatically read from the current project configuration:
    - sync_files=True: Reads from configuration/components/pages.json (synced files)  
    - sync_files=False: Reads from src/ePy_docs/components/pages.json (installation directory)
                  
    Returns:
        Dict containing the page configuration
        
    Raises:
        ValueError: If configuration file is not found or invalid
    """
    from ePy_docs.core.setup import get_current_project_config
    # Load configuration using centralized cache system as lord supremo commands
    from ePy_docs.core.setup import get_current_project_config, _load_cached_files, get_filepath
    
    # Get project configuration to determine sync_files setting
    current_config = get_current_project_config()
    
    # Get sync_files setting from DirectoryConfigSettings
    if current_config is not None:
        sync_files = current_config.settings.sync_files
    else:
        sync_files = False  # Default to False if no project configured (use installation files)
    
    try:
        return _load_cached_files(get_filepath('files.configuration.styling.page_json'), sync_files)
    except Exception as e:
        raise ValueError(f"pages.json not found via centralized system: {e}")


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
                          markdown_content: Dict[str, str]) -> str:
    """Create a complete Quarto project structure.
    
    The sync_files setting is automatically read from DirectoryConfigSettings.
    
    Args:
        output_dir: Path to output directory
        markdown_content: Dictionary of relative paths to markdown content
        
    Returns:
        Path to created project directory
    
    Raises:
        ValueError: If markdown_content is empty or None
    """
    if not markdown_content:
        raise ValueError("markdown_content is required and cannot be empty")
    
    # Get sync_files setting from DirectoryConfigSettings
    from ePy_docs.core.setup import get_current_project_config
    current_config = get_current_project_config()
    sync_files = current_config.settings.sync_files if current_config else False
    
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
    create_quarto_yml(output_dir, chapters=chapter_files)
    
    return str(output_path)


class QuartoConverter:
    """Coordinates Markdown conversion to PDF and HTML using Quarto."""
    
    def __init__(self):
        """Initialize the Quarto converter."""
        pass
        
    def _validate_markdown_content(self, markdown_content: Union[str, Path], format_type: str = 'pdf') -> str:
        """Validate and prepare markdown content.
        
        Args:
            markdown_content: Markdown content as string or path to .md file
            format_type: Output format ('html', 'pdf', 'latex') - affects Unicode handling
            
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
        return self._preprocess_markdown(content, format_type)
    
    def _create_qmd_content(self, 
                           markdown_content: str, 
                           yaml_config: Dict[str, Any]) -> str:
        """Create complete QMD content with YAML header and markdown.
        
        The sync_files setting is automatically read from DirectoryConfigSettings.
        
        Args:
            markdown_content: Markdown content
            yaml_config: YAML configuration dictionary
            
        Returns:
            Complete QMD content as string
        """
        import yaml
        
        # Get sync_files setting from DirectoryConfigSettings
        from ePy_docs.core.setup import get_current_project_config
        current_config = get_current_project_config()
        sync_files = current_config.settings.sync_files if current_config else False
        
        # If yaml_config is not provided, use project-based config
        if not yaml_config:
            yaml_config = generate_quarto_config(sync_files=sync_files)
        
        # Create YAML header
        yaml_header = "---\n"
        yaml_header += yaml.dump(yaml_config, default_flow_style=False, allow_unicode=True)
        yaml_header += "---\n\n"
        
        # Add references subtitle if configured
        from ePy_docs.components.pages import get_references_config
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
                       output_file: Optional[str] = None) -> str:
        """Convert Markdown content to Quarto (.qmd) format.
        
        Citation style is automatically determined from the layout in pages.json.
        The sync_files setting is automatically read from DirectoryConfigSettings.
        
        Args:
            markdown_content: Markdown content as string or path to .md file
            title: Document title (required)
            author: Document author (required)
            output_file: Optional output file path. If None, creates temporary file
            
        Returns:
            Path to the created .qmd file
        """
        if not title:
            raise ValueError("title is required")
        if not author:
            raise ValueError("author is required")
        
        # Get sync_files setting from DirectoryConfigSettings
        from ePy_docs.core.setup import get_current_project_config
        current_config = get_current_project_config()
        sync_files = current_config.settings.sync_files if current_config else False
        
        # Validate and get markdown content - specify PDF format for LaTeX safety
        content = self._validate_markdown_content(markdown_content, format_type='pdf')
        
        # Get configuration - now reads layout from pages.json automatically
        yaml_config = generate_quarto_config(sync_files=sync_files)
        
        # Update title and author in config
        if 'book' in yaml_config:
            yaml_config['book']['title'] = title
            yaml_config['book']['author'] = author
        else:
            yaml_config['title'] = title
            yaml_config['author'] = author
        
        # Create complete QMD content
        qmd_content = self._create_qmd_content(content, yaml_config)
        
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

    def markdown_to_qmd_html(self, 
                           markdown_content: Union[str, Path], 
                           title: str,
                           author: str,
                           output_file: Optional[str] = None) -> str:
        """Convert Markdown content to Quarto (.qmd) format optimized for HTML output.
        
        This method processes superscripts/subscripts as Unicode for HTML rendering.
        
        Args:
            markdown_content: Markdown content as string or path to .md file
            title: Document title (required)
            author: Document author (required)
            output_file: Optional output file path. If None, creates temporary file
            
        Returns:
            Path to the created .qmd file
        """
        if not title:
            raise ValueError("title is required")
        if not author:
            raise ValueError("author is required")
        
        # Get sync_files setting from DirectoryConfigSettings
        from ePy_docs.core.setup import get_current_project_config
        current_config = get_current_project_config()
        sync_files = current_config.settings.sync_files if current_config else False
        
        # Validate and get markdown content - specify HTML format for Unicode
        content = self._validate_markdown_content(markdown_content, format_type='html')
        
        # Get configuration - now reads layout from pages.json automatically
        yaml_config = generate_quarto_config(sync_files=sync_files)
        
        # Update title and author in config
        if 'book' in yaml_config:
            yaml_config['book']['title'] = title
            yaml_config['book']['author'] = author
        else:
            yaml_config['title'] = title
            yaml_config['author'] = author
        
        # Create complete QMD content
        qmd_content = self._create_qmd_content(content, yaml_config)
        
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
            # First, check if any processes might be locking the PDF file
            import time
            
            # Clean up any existing PDF files that might conflict with the target name
            # Focus on the exact final PDF name we want
            if os.path.exists(final_pdf):
                try:
                    # Try to rename to check if file is locked
                    temp_name = final_pdf + ".tmp"
                    os.rename(final_pdf, temp_name)
                    os.rename(temp_name, final_pdf)
                    # If successful, we can safely remove it
                    os.remove(final_pdf)
                    print(f"✅ Removed existing PDF: {os.path.basename(final_pdf)}")
                except (OSError, PermissionError):
                    # File is locked by a PDF reader
                    print(f"⚠️  Warning: Existing PDF {os.path.basename(final_pdf)} is locked (probably open in PDF reader)")
                    print("    The new PDF might be generated with a different name or timestamp")
                    
            # Also clean up any Quarto-generated variants that might interfere
            potential_variants = [
                os.path.join(os.path.dirname(qmd_path), f"{qmd_basename.replace(' ', '-')}.pdf"),
                os.path.join(os.path.dirname(qmd_path), f"{qmd_basename.replace(' ', '_')}.pdf")
            ]
            
            for pdf_path in potential_variants:
                if os.path.exists(pdf_path) and pdf_path != final_pdf:
                    try:
                        os.remove(pdf_path)
                        print(f"✅ Cleaned up variant PDF: {os.path.basename(pdf_path)}")
                    except (OSError, PermissionError):
                        # Skip if locked
                        pass
            
            # Run quarto render command with explicit PDF format 
            # Let Quarto decide the filename internally to avoid permission conflicts
            result = subprocess.run(
                ['quarto', 'render', qmd_path, '--to', 'pdf'],
                cwd=os.path.dirname(qmd_path),
                capture_output=True,
                text=True,
                check=True
            )
            
            # After rendering, find the generated PDF file
            # Quarto might generate with a different name due to space handling
            qmd_dir = os.path.dirname(qmd_path)
            possible_names = [
                f"{qmd_basename}.pdf",
                f"{qmd_basename.replace(' ', '-')}.pdf",
                f"{qmd_basename.replace(' ', '_')}.pdf"
            ]
            
            generated_pdf = None
            for name in possible_names:
                candidate = os.path.join(qmd_dir, name)
                if os.path.exists(candidate):
                    generated_pdf = candidate
                    break
            
            if not generated_pdf:
                # Look for any PDF file generated in the directory
                pdf_files = [f for f in os.listdir(qmd_dir) if f.endswith('.pdf')]
                if pdf_files:
                    # Use the most recently created PDF file
                    pdf_files_with_time = [(f, os.path.getctime(os.path.join(qmd_dir, f))) 
                                          for f in pdf_files]
                    pdf_files_with_time.sort(key=lambda x: x[1], reverse=True)
                    generated_pdf = os.path.join(qmd_dir, pdf_files_with_time[0][0])
            
            # Ensure PDF is generated in the correct location from the start
            if generated_pdf:
                if output_dir != os.path.dirname(qmd_path):
                    # Move PDF to desired output directory
                    shutil.move(generated_pdf, final_pdf)
                    final_pdf = os.path.abspath(final_pdf)
                else:
                    # If different name in same directory, try to rename
                    if generated_pdf != final_pdf:
                        try:
                            # If target file exists, try to remove it first
                            if os.path.exists(final_pdf):
                                try:
                                    os.remove(final_pdf)
                                except (OSError, PermissionError):
                                    # File might be locked by PDF reader
                                    print(f"⚠️  Warning: Could not remove existing PDF {final_pdf}")
                                    print("    This might be because the PDF is open in a PDF reader.")
                                    print("    The new PDF will be saved with a different name.")
                                    # Generate a unique name to avoid conflict
                                    import time
                                    timestamp = int(time.time())
                                    base_name = os.path.splitext(os.path.basename(final_pdf))[0]
                                    final_pdf = os.path.join(output_dir, f"{base_name}-{timestamp}.pdf")
                            
                            shutil.move(generated_pdf, final_pdf)
                        except (OSError, PermissionError) as e:
                            # If we still can't rename, use the generated name but warn user
                            print(f"⚠️  Warning: Could not rename PDF to desired name due to: {e}")
                            print(f"    Using generated name: {os.path.basename(generated_pdf)}")
                            final_pdf = generated_pdf
                    else:
                        final_pdf = generated_pdf
            
            if not os.path.exists(final_pdf):
                # Enhanced error message with more diagnostic information
                error_details = []
                error_details.append(f"Expected final PDF path: {final_pdf}")
                error_details.append(f"QMD file: {qmd_path}")
                error_details.append(f"Output directory: {output_dir}")
                
                # List files in the QMD directory to see what was generated
                qmd_dir = os.path.dirname(qmd_path)
                if os.path.exists(qmd_dir):
                    files_in_dir = [f for f in os.listdir(qmd_dir) if f.endswith(('.pdf', '.tex', '.log'))]
                    error_details.append(f"Relevant files in QMD directory: {files_in_dir}")
                
                # Check if Quarto generated any output
                if result.stdout:
                    error_details.append(f"Quarto stdout: {result.stdout}")
                if result.stderr:
                    error_details.append(f"Quarto stderr: {result.stderr}")
                
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
            
            # Check for permission-related errors
            if e.stderr and ("PermissionDenied" in e.stderr or "Acceso denegado" in e.stderr):
                error_details.append("")
                error_details.append("PERMISSION ERROR DETECTED:")
                error_details.append("This error commonly occurs when:")
                error_details.append("1. A PDF reader (like Foxit, Adobe, etc.) has the PDF file open")
                error_details.append("2. The PDF file is locked by another process")
                error_details.append("3. Insufficient file system permissions")
                error_details.append("")
                error_details.append("Solutions:")
                error_details.append("- Close any PDF readers that might have the file open")
                error_details.append("- Try running with administrator privileges")
                error_details.append("- Use a different output filename")
                
                # Check for running PDF readers
                try:
                    import subprocess as sp
                    result = sp.run(['powershell', '-Command', 
                                   'Get-Process | Where-Object {$_.ProcessName -match "PDF|Acrobat|Foxit|Adobe"} | Select-Object ProcessName'], 
                                   capture_output=True, text=True)
                    if result.stdout.strip():
                        error_details.append(f"Running PDF-related processes: {result.stdout}")
                except:
                    pass
            
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
            
            # Generate and write CSS styles after HTML creation
            try:
                from pathlib import Path
                from ePy_docs.components.pages import create_css_styles
                from ePy_docs.components.pages import get_current_layout
                from ePy_docs.api.file_management import write_text
                
                # Get current layout and generate CSS
                current_layout = get_current_layout()
                css_content = create_css_styles(layout_name=current_layout)
                
                # Write CSS file to same directory as HTML
                html_dir = Path(final_html).parent
                css_file = html_dir / "styles.css"
                write_text(css_content, css_file)
                
            except Exception as e:
                # Don't fail HTML generation if CSS fails, just log warning
                print(f"Warning: CSS generation failed: {e}")
            
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
                              clean_temp: bool = True) -> str:
        """Complete conversion from Markdown to PDF using Quarto.
        
        The sync_files setting is automatically read from DirectoryConfigSettings.
        
        Args:
            markdown_content: Markdown content as string or path to .md file
            title: Document title (required)
            author: Document author (required)
            output_file: Optional output PDF file path
            clean_temp: Whether to clean temporary files after conversion
            
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
                # If output file is specified, create QMD in the user's configured report directory
                # This ensures Quarto runs from the same directory structure as the images
                from ePy_docs.core.setup import get_absolute_output_directories
                try:
                    output_dirs = get_absolute_output_directories()
                    abs_report_dir = output_dirs['report']
                    os.makedirs(abs_report_dir, exist_ok=True)
                    
                    # Place QMD file in the report directory where images are configured to be relative from
                    base_name = os.path.splitext(os.path.basename(output_file))[0] if output_file else title.replace(' ', '_')
                    temp_qmd = os.path.join(abs_report_dir, f"{base_name}.qmd")
                    
                except Exception as e:
                    # Fallback to original behavior if setup.json can't be read
                    print(f"Warning: Could not read directory configuration: {e}")
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
                output_file=temp_qmd
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
                               clean_temp: bool = True) -> str:
        """Complete conversion from Markdown to HTML using Quarto.
        
        The sync_files setting is automatically read from DirectoryConfigSettings.
        
        Args:
            markdown_content: Markdown content as string or path to .md file
            title: Document title (required)
            author: Document author (required)
            output_file: Optional output HTML file path
            clean_temp: Whether to clean temporary files after conversion
            
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
            
            # Convert to QMD with HTML format for Unicode support
            qmd_file = self.markdown_to_qmd_html(
                markdown_content=markdown_content,
                title=title,
                author=author,
                output_file=temp_qmd
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
                             sync_files: bool = True) -> str:
        """Import and render an existing Quarto (.qmd) file.
        
        Args:
            qmd_file: Path to existing .qmd file
            output_format: Output format ("pdf" or "html")
            output_dir: Optional output directory (defaults to same directory as QMD file)
            sync_files: Whether to sync JSON files before reading configuration
            
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
                                 sync_files: bool = True,
                                 ignore_patterns: Optional[List[str]] = None) -> Dict[str, str]:
        """Scan directory for .qmd files and render them all.
        
        Args:
            directory: Directory path to scan for .qmd files
            output_format: Output format ("pdf" or "html")
            output_dir: Optional output directory (defaults to same directory as each QMD file)
            recursive: Whether to scan subdirectories recursively
            sync_files: Whether to sync JSON files before reading configuration
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
            ignore_patterns = get_config_value('components/pages.json', 'ignore_patterns', sync_files=sync_files)
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
                    sync_files=sync_files
                )
                
                results[qmd_file] = output_path
                successful_renders += 1
                
            except Exception as e:
                print(f"❌ Failed to render {qmd_file}: {e}")
                failed_renders += 1
        
        return results

    def _preprocess_markdown(self, content: str, format_type: str = 'pdf') -> str:
        """Pre-process markdown content before conversion to QMD.
        
        This method should make minimal changes to preserve user-written
        Quarto-compatible markdown exactly as intended.
        
        Args:
            content: Raw markdown content
            format_type: Output format ('html', 'pdf', 'latex') - affects Unicode handling
            
        Returns:
            Processed content ready for Quarto
        """
        # Import ContentProcessor to use callout protection
        from ePy_docs.core.setup import ContentProcessor
        
        # Normalize line endings only
        content = content.replace('\r\n', '\n')
        
        # Protect callouts before applying any processing
        protected_content, callout_replacements = ContentProcessor.protect_callouts_from_header_processing(content)
        
        # Apply mathematical text processing with format-specific handling
        try:
            # Get current layout for mathematical processing
            from ePy_docs.components.pages import get_current_layout
            from ePy_docs.core.setup import get_current_project_config
            
            current_layout = get_current_layout()
            current_config = get_current_project_config()
            sync_files = current_config.settings.sync_files if current_config else False
            
            # Process mathematical text with appropriate format
            protected_content = process_mathematical_text(protected_content, current_layout, sync_files, format_type)
            
        except Exception:
            # If mathematical processing fails, continue without it
            pass
        
        # Apply only minimal, necessary fixes for edge cases
        # Only fix severely malformed equations with excessive spaces
        protected_content = re.sub(r'\$ {2,}([^$]+?) {2,}\$', r'$\1$', protected_content)
        
        # CRITICAL: For PDF output, aggressively remove all problematic Unicode characters
        if format_type in ['pdf', 'latex']:
            protected_content = self._sanitize_for_latex(protected_content)
        
        # Restore callouts after processing
        protected_content = ContentProcessor.restore_callouts_after_processing(protected_content, callout_replacements)
        
        return protected_content
    
    def _sanitize_for_latex(self, content: str) -> str:
        """Aggressively sanitize content for LaTeX compilation.
        
        This removes all Unicode characters that could cause LaTeX compilation errors.
        
        Args:
            content: Content to sanitize
            
        Returns:
            LaTeX-safe content
        """
        import re
        
        # Define problematic Unicode characters and their LaTeX replacements
        unicode_replacements = {
            # Mathematical superscripts
            '²': '^{2}',
            '³': '^{3}',
            '⁴': '^{4}',
            '⁵': '^{5}',
            '⁶': '^{6}',
            '⁷': '^{7}',
            '⁸': '^{8}',
            '⁹': '^{9}',
            '¹': '^{1}',
            '⁰': '^{0}',
            
            # Mathematical subscripts  
            '₀': '_{0}',
            '₁': '_{1}',
            '₂': '_{2}',
            '₃': '_{3}',
            '₄': '_{4}',
            '₅': '_{5}',
            '₆': '_{6}',
            '₇': '_{7}',
            '₈': '_{8}',
            '₉': '_{9}',
            'ᵢ': '_{i}',
            'ₓ': '_{x}',
            'ₐ': '_{a}',
            'ₑ': '_{e}',
            'ₒ': '_{o}',
            'ᵤ': '_{u}',
            'ₕ': '_{h}',
            'ₖ': '_{k}',
            'ₗ': '_{l}',
            'ₘ': '_{m}',
            'ₙ': '_{n}',
            'ₚ': '_{p}',
            'ᵣ': '_{r}',
            'ₛ': '_{s}',
            'ₜ': '_{t}',
            'ᵥ': '_{v}',
            
            # Greek letters and other mathematical symbols
            'α': r'\alpha',
            'β': r'\beta', 
            'γ': r'\gamma',
            'δ': r'\delta',
            'ε': r'\varepsilon',
            'ζ': r'\zeta',
            'η': r'\eta',
            'θ': r'\theta',
            'ι': r'\iota',
            'κ': r'\kappa',
            'λ': r'\lambda',
            'μ': r'\mu',
            'ν': r'\nu',
            'ξ': r'\xi',
            'π': r'\pi',
            'ρ': r'\rho',
            'σ': r'\sigma',
            'τ': r'\tau',
            'υ': r'\upsilon',
            'φ': r'\phi',
            'χ': r'\chi',
            'ψ': r'\psi',
            'ω': r'\omega',
            
            # Uppercase Greek letters
            'Α': 'A', 'Β': 'B', 'Γ': r'\Gamma', 'Δ': r'\Delta',
            'Ε': 'E', 'Ζ': 'Z', 'Η': 'H', 'Θ': r'\Theta',
            'Ι': 'I', 'Κ': 'K', 'Λ': r'\Lambda', 'Μ': 'M',
            'Ν': 'N', 'Ξ': r'\Xi', 'Ο': 'O', 'Π': r'\Pi',
            'Ρ': 'P', 'Σ': r'\Sigma', 'Τ': 'T', 'Υ': r'\Upsilon',
            'Φ': r'\Phi', 'Χ': 'X', 'Ψ': r'\Psi', 'Ω': r'\Omega',
            
            # Mathematical operators and symbols
            '×': r'\times',
            '÷': r'\div', 
            '±': r'\pm',
            '∓': r'\mp',
            '≤': r'\leq',
            '≥': r'\geq',
            '≠': r'\neq',
            '≈': r'\approx',
            '∞': r'\infty',
            '∫': r'\int',
            '∑': r'\sum',
            '∏': r'\prod',
            '√': r'\sqrt',
            '∂': r'\partial',
            '∇': r'\nabla',
            '°': r'^\circ',
            
            # Arrows
            '→': r'\rightarrow',
            '←': r'\leftarrow',
            '↑': r'\uparrow',
            '↓': r'\downarrow',
            '↔': r'\leftrightarrow',
            '⇒': r'\Rightarrow',
            '⇐': r'\Leftarrow',
            '⇔': r'\Leftrightarrow',
            
            # Other problematic characters
            '–': '--',  # en dash
            '—': '---',  # em dash
            ''': "'",    # left single quote
            ''': "'",    # right single quote
            '"': '"',    # left double quote
            '"': '"',    # right double quote
            '…': '...',  # ellipsis
            '¼': '1/4',
            '½': '1/2', 
            '¾': '3/4',
            '℃': r'^\circ C',
            '℉': r'^\circ F',
            '©': r'\copyright',
            '®': r'\textregistered',
            '™': r'\texttrademark'
        }
        
        # Apply all Unicode replacements
        for unicode_char, latex_replacement in unicode_replacements.items():
            content = content.replace(unicode_char, latex_replacement)
        
        # Additional aggressive cleaning for any remaining problematic characters
        # Remove or replace any high Unicode characters that could cause issues
        # Keep only ASCII characters, basic LaTeX commands, and essential Unicode ranges
        
        # Pattern to match problematic Unicode ranges
        # This is aggressive but necessary for LaTeX compilation success
        def is_safe_char(char):
            code = ord(char)
            # Allow basic ASCII
            if 32 <= code <= 126:
                return True
            # Allow essential characters
            if char in '\n\r\t':
                return True
            # Allow basic Latin extended (accented characters)
            if 128 <= code <= 255:
                return True
            # Everything else is potentially problematic for XeLaTeX
            return False
        
        # Filter out problematic characters, replacing with safe equivalents when possible
        safe_content = []
        for char in content:
            if is_safe_char(char):
                safe_content.append(char)
            else:
                # Log the problematic character for debugging
                print(f"⚠️  Removing problematic Unicode character: '{char}' (U+{ord(char):04X})")
                # Replace with a space to maintain text flow
                safe_content.append(' ')
        
        result = ''.join(safe_content)
        
        # Clean up any multiple spaces created by character removal
        result = re.sub(r' {2,}', ' ', result)
        
        return result


class QuartoConfigManager:
    """Manager for Quarto-specific configuration operations."""
    
    @staticmethod
    def merge_crossref_config() -> Dict[str, Any]:
        """Merge crossref configuration from multiple component files."""
        from ePy_docs.components.pages import get_config_value
        
        crossref_config = {}
        
        # Load from images.json - must exist
        images_config = get_config_value('components/images.json', 'crossref')
        if images_config:
            crossref_config.update(images_config)
        
        # Load from tables.json - must exist
        tables_config = get_config_value('components/tables.json', 'crossref')
        if tables_config:
            crossref_config.update(tables_config)
        
        # Load from equations.json - must exist
        equations_config = get_config_value('components/equations.json', 'crossref')
        if equations_config:
            crossref_config.update(equations_config)
        
        return crossref_config


# ============================================================================
# MATHEMATICAL PROCESSING - ANNEXED FROM MATH KINGDOM
# Optimized integration with Quarto processing pipeline
# ============================================================================
# MATH KINGDOM CONFIGURATION - AUTONOMOUS AND EFFICIENT
# ============================================================================

# DEFAULT MATH CONFIGURATION - Lord's decree: NO external files needed
DEFAULT_MATH_CONFIG = {
    "mathematical_processing": {
        "supported_formats": ["latex", "mathml", "ascii"],
        "default_renderer": "latex",
        "equation_numbering": True,
        "inline_math_delimiters": ["$", "$"],
        "display_math_delimiters": ["$$", "$$"],
        "processing_settings": {
            "auto_convert": True,
            "preserve_spacing": True,
            "error_handling": "strict"
        }
    }
}

def _load_math_config(sync_files: bool = False) -> Dict[str, Any]:
    """Load mathematical configuration - now autonomous with default values."""
    # Lord's decree: NO external files, use DEFAULT_MATH_CONFIG
    return DEFAULT_MATH_CONFIG.copy()

def load_math_config(sync_files: bool = False) -> Dict[str, Any]:
    """Public function to load math configuration - used by other components."""
    return _load_math_config(sync_files)

def process_mathematical_text(text: str, layout_name: str, sync_files: bool, format_type: str = 'html') -> str:
    """Process text containing mathematical content - delegated from text.py.
    
    Optimized for Quarto pipeline integration with superscript/subscript conversion.
    
    Args:
        text: Text to process
        layout_name: Layout name
        sync_files: Sync files setting
        format_type: Output format ('html', 'pdf', 'latex') - affects Unicode handling
    """
    config = _load_math_config(sync_files)
    
    # Load units format config for superscript/subscript conversion
    try:
        from ePy_docs.core.setup import _load_cached_files, get_filepath
        units_config = _load_cached_files(get_filepath('files.configuration.units.format_json'), sync_files)
        
        if 'math_formatting' in units_config:
            math_formatting = units_config['math_formatting']
            
            # For PDF/LaTeX output, use LaTeX commands instead of Unicode
            if format_type in ['pdf', 'latex']:
                # Process superscripts with LaTeX syntax for PDF
                if math_formatting.get('enable_superscript', False):
                    pattern = math_formatting.get('superscript_pattern', r'\^(\{[^}]+\}|\w)')
                    
                    import re
                    def replace_superscript_latex(match):
                        content = match.group(1)
                        # Remove braces if present
                        if content.startswith('{') and content.endswith('}'):
                            content = content[1:-1]
                        # Use LaTeX syntax for superscript
                        return f'^{{{content}}}'
                    
                    text = re.sub(pattern, replace_superscript_latex, text)
                
                # Process subscripts with LaTeX syntax for PDF
                if math_formatting.get('enable_subscript', False):
                    pattern = math_formatting.get('subscript_pattern', r'_(\{[^}]+\}|\w)')
                    
                    import re
                    def replace_subscript_latex(match):
                        content = match.group(1)
                        # Remove braces if present
                        if content.startswith('{') and content.endswith('}'):
                            content = content[1:-1]
                        # Use LaTeX syntax for subscript
                        return f'_{{{content}}}'
                    
                    text = re.sub(pattern, replace_subscript_latex, text)
            
            else:
                # For HTML output, use Unicode characters as before
                # Process superscripts if enabled
                if math_formatting.get('enable_superscript', False):
                    superscript_map = math_formatting.get('superscript_map', {})
                    pattern = math_formatting.get('superscript_pattern', r'\^(\{[^}]+\}|\w)')
                    
                    import re
                    def replace_superscript(match):
                        content = match.group(1)
                        # Remove braces if present
                        if content.startswith('{') and content.endswith('}'):
                            content = content[1:-1]
                        
                        # Convert each character to superscript
                        result = ''
                        for char in content:
                            result += superscript_map.get(char, char)
                        return result
                    
                    text = re.sub(pattern, replace_superscript, text)
                
                # Process subscripts if enabled
                if math_formatting.get('enable_subscript', False):
                    subscript_map = math_formatting.get('subscript_map', {})
                    pattern = math_formatting.get('subscript_pattern', r'_(\{[^}]+\}|\w)')
                    
                    import re
                    def replace_subscript(match):
                        content = match.group(1)
                        # Remove braces if present
                        if content.startswith('{') and content.endswith('}'):
                            content = content[1:-1]
                        
                        # Convert each character to subscript
                        result = ''
                        for char in content:
                            result += subscript_map.get(char, char)
                        return result
                    
                    text = re.sub(pattern, replace_subscript, text)
    
    except Exception:
        # If units config fails, continue without superscript/subscript conversion
        pass
    
    return text

class MathProcessor:
    """Mathematical content processor - optimized for Quarto integration."""
    
    def __init__(self, layout_name: str = 'academic', sync_files: bool = False, format_type: str = 'html'):
        self.layout_name = layout_name
        self.sync_files = sync_files
        self.format_type = format_type
        self.config = _load_math_config(sync_files)
    
    def process_equation(self, equation: str) -> str:
        """Process mathematical equation."""
        return process_mathematical_text(equation, self.layout_name, self.sync_files, self.format_type)
    
    def format_formula(self, formula: str) -> str:
        """Format mathematical formula.""" 
        return process_mathematical_text(formula, self.layout_name, self.sync_files, self.format_type)
