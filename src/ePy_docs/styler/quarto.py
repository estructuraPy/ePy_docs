"""Quarto styling module for ePy_suite.

This module handles the styling configuration for Quarto documents, including
PDF and HTML formats, by accessing styling information from JSON configuration files.
It provides functions to create Quarto configurations, generate CSS styles,
and set up reference files for document compilation.
"""
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import os
import yaml
import shutil

from ePy_docs.styler.setup import get_color, get_project_config, get_config_value


def _rgb_to_str(rgb_list: List[int]) -> str:
    """Convert RGB list to string format for LaTeX color definitions.
    
    Args:
        rgb_list: RGB color as [r, g, b] list where each value is an integer 0-255.
        
    Returns:
        str: String in the format "r, g, b" for LaTeX color definitions.
    """
    return f"{rgb_list[0]}, {rgb_list[1]}, {rgb_list[2]}"




def generate_quarto_config(sync_json: bool = True, citation_style: Optional[str] = None) -> Dict[str, Any]:
    """Generate Quarto YAML configuration from project settings.
    
    This function reads the project configuration and styling information
    from JSON files and creates a complete Quarto configuration dictionary
    for the document's appearance. The configuration includes document metadata,
    formatting options for PDF and HTML outputs, and styling based on the
    project's color scheme.
    
    Args:
        sync_json: Whether to synchronize JSON files before reading. Defaults to True.
        
    Returns:
        Dict[str, Any]: Complete Quarto YAML configuration dictionary ready for
            rendering with Quarto.
            
    Assumes:
        The required JSON configuration files exist and contain valid color and
        project information.
    """
    # Load project configuration
    project_config = get_project_config(sync_json=sync_json)
    
    # Extract relevant project information
    project_info = project_config.get('project', {})
    copyright_info = project_config.get('copyright', {})
    
    # Get document information - no fallbacks, all from JSON
    title = project_info['name']
    subtitle = project_info.get('description', '')
    author_date = project_info['created_date']
    
    # Determine CSL style to use - must be provided
    if not citation_style:
        raise ValueError("citation_style parameter is required")
    csl_file = validate_csl_style(citation_style)
    
    # Get references paths from DirectoryConfig
    from ePy_docs.project.setup import DirectoryConfig
    
    try:
        # Try to get directory configuration
        dir_config = DirectoryConfig()
        config_dir = Path(dir_config.folders.config)
        references_dir = config_dir / "references"
        
        # Use absolute paths with proper forward slashes for Quarto/Pandoc
        bib_path = str(references_dir / "references.bib").replace("\\", "/")
        csl_path = str(references_dir / f"{csl_file}").replace("\\", "/")
    except:
        # Fallback to relative path if DirectoryConfig fails
        bib_path = "configuration/references/references.bib"
        csl_path = f"configuration/references/{csl_file}"
    
    # Create base configuration - load from setup.json instead of hardcoded values
    quarto_config = get_config_value('formats_quarto', 'quarto', {}, sync_json)
    project_type = quarto_config.get('project_type', 'book')
    language = quarto_config.get('language', 'es')
    
    # Get crossref configuration from setup.json
    crossref_config = get_config_value('formats_quarto', 'crossref', {}, sync_json)
    
    config = {
        'project': {
            'type': project_type
        },
        'lang': language,
        'book': {
            'title': title,
            'subtitle': subtitle,
            'author': author_date,
        },
        'bibliography': bib_path,
        'csl': csl_path,
        'execute': {
            'echo': crossref_config.get('execute_echo', False)
        },
        'crossref': {
            'chapters': crossref_config.get('chapters', False),
            'eq-prefix': crossref_config.get('eq_prefix', 'Ec.'),
            'eq-labels': crossref_config.get('eq_labels', 'arabic'),
            'fig-prefix': crossref_config.get('fig_prefix', 'Figura'),
            'fig-labels': crossref_config.get('fig_labels', 'arabic'),
            'tbl-prefix': crossref_config.get('tbl_prefix', 'Tabla'),
            'tbl-labels': crossref_config.get('tbl_labels', 'arabic')
        }
    }
    
    # Get colors for styling
    primary_blue = get_color('brand.primary_blue', format_type="hex", sync_json=sync_json)
    accent_red = get_color('brand.accent_red', format_type="hex", sync_json=sync_json)
    secondary_gray = get_color('brand.secondary_gray', format_type="hex", sync_json=sync_json)
    
    # Gray scales - all from config, no hardcoded values
    gray_1 = get_color('general.light_gray', format_type="hex", sync_json=sync_json)
    gray_2 = get_color('general.medium_gray', format_type="hex", sync_json=sync_json)
    # No more hardcoded values
    gray_4 = get_color('general.dark_gray', format_type="hex", sync_json=sync_json)
    
    # Create PDF format configuration with LaTeX header
    pdf_config = {
        'number-sections': False,
        'include-in-header': {
            'text': f'''
\\usepackage[utf8]{{inputenc}}
\\usepackage{{fancyhdr}}
\\pagestyle{{fancy}}

\\clearpage
\\setcounter{{page}}{{0}}
\\pagenumbering{{arabic}}
\\lhead{{{project_config['client']['name']}}}
\\chead{{}}        
\\rhead{{{copyright_info['name']}}}
\\lfoot{{}}
\\cfoot{{\\thepage}}
\\rfoot{{}}

\\usepackage{{graphicx}}

\\usepackage {{xcolor}}
% All colors from configuration - no hardcoded values
\\definecolor{{redANM}}{{RGB}}{{{_rgb_to_str(get_color('brand.accent_red', format_type="rgb", sync_json=sync_json))}}}
\\definecolor{{blueANM}}{{RGB}}{{{_rgb_to_str(get_color('brand.primary_blue', format_type="rgb", sync_json=sync_json))}}}
\\definecolor{{Gray_1}}{{RGB}}{{{_rgb_to_str(get_color('general.light_gray', format_type="rgb", sync_json=sync_json))}}}
\\definecolor{{Gray_2}}{{RGB}}{{{_rgb_to_str(get_color('general.medium_gray', format_type="rgb", sync_json=sync_json))}}}
\\definecolor{{Gray_4}}{{RGB}}{{{_rgb_to_str(get_color('general.dark_gray', format_type="rgb", sync_json=sync_json))}}}

% Equation numbering configuration
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{amsfonts}}
% Remove section-based numbering - equations will be numbered consecutively

\\usepackage{{sectsty}}
\\chapterfont{{\\color{{blueANM}}}}  % sets colour of chapters
\\sectionfont{{\\color{{Gray_4}}}}  % sets colour of sections

% Custom content-block styling to keep content together
\\newenvironment{{contentblock}}
  {{\\begin{{minipage}}{{\\textwidth}}}}
  {{\\end{{minipage}}\\par\\vspace{{\\baselineskip}}}}

% Map Quarto div class content-block to our contentblock environment
\\newenvironment{{content-block}}{{\\begin{{contentblock}}}}{{\\end{{contentblock}}}}

\\makeatletter
\\def\\thickhrulefill{{\\leavevmode \\leaders \\hrule height 1pt\\hfill \\kern \\z@}}
\\renewcommand{{\\maketitle}}{{\\begin{{titlepage}}%
  \\let\\footnotesize\\small
  \\let\\footnoterule\\relax
  \\parindent \\z@
  \\reset@font
  \\null
  \\vskip 10\\p@
  \\hbox{{\\mbox{{\\hspace{{3em}}}}%
    \\vrule depth 0.6\\textheight %
    \\mbox{{\\hspace{{2em}}}}
    \\vbox{{
      \\vskip 40\\p@
      \\begin{{flushleft}}
        \\Large \\@author \\par
      \\end{{flushleft}}
      \\vskip 80\\p@
      \\begin{{flushleft}}
        \\huge \\bfseries \\@title \\par
      \\end{{flushleft}}
      \\vfill
      }}}}
    \\null
  \\end{{titlepage}}%
  \\setcounter{{footnote}}{{0}}%
}} 
\\makeatother
'''
        },
        'documentclass': 'report',
        'fontsize': '11pt',
        'papersize': 'letter',
        'margin-left': '25mm',
        'margin-right': '25mm',
        'margin-top': '25mm',
        'margin-bottom': '25mm',
        'linestretch': 1.25,
        'toc-depth': 2,
        'toc': True,
        'lof': True,
        'lot': True
    }
    
    # Create HTML format configuration - use JSON config values
    quarto_config = get_config_value('formats_quarto', 'format.html', {}, sync_json)
    html_config = {
        'theme': quarto_config.get('theme', 'default'),
        'toc': quarto_config.get('toc', True),
        'toc-depth': quarto_config.get('toc-depth', 2),
        'number-sections': quarto_config.get('number-sections', False),
        'html-math-method': 'mathjax',
        'self-contained': quarto_config.get('self-contained', True),
        'embed-resources': quarto_config.get('embed-resources', True),
        'fig-width': quarto_config.get('fig-width', 5.0),
        'fig-height': quarto_config.get('fig-height', 3.8),
        'fig-align': quarto_config.get('fig-align', 'center'),
        'fig-responsive': quarto_config.get('fig-responsive', True),
        'fig-cap-location': quarto_config.get('fig-cap-location', 'bottom'),
        'tbl-cap-location': quarto_config.get('tbl-cap-location', 'top'),
        'fig-dpi': quarto_config.get('fig-dpi', 150),
        'code-fold': quarto_config.get('code-fold', False),
        'code-tools': quarto_config.get('code-tools', False)
    }
    
    # Add format configurations to main config
    config['format'] = {
        'pdf': pdf_config,
        'html': html_config
    }
    
    return config


def create_quarto_yml(output_dir: str, chapters: Optional[List[str]] = None, sync_json: bool = True, citation_style: str = 'apa') -> str:
    """Create _quarto.yml file from project configuration.
    
    This function generates a _quarto.yml file and supporting styles.css file in 
    the specified directory, based on the project configuration from JSON files.
    
    Args:
        output_dir: Directory where the _quarto.yml file will be created.
        chapters: Optional list of chapter paths to include in the configuration.
            If provided, these will be set as the book chapters in order.
        sync_json: Whether to synchronize JSON files before reading. Defaults to True.
        citation_style: Citation style to use. Defaults to 'apa'.
        
    Returns:
        str: Absolute path to the created _quarto.yml file.
        
    Assumes:
        The output directory is writable, and the required JSON configuration 
        files exist.
    """
    # Generate the Quarto configuration
    config = generate_quarto_config(sync_json=sync_json, citation_style=citation_style)
    
    # Add chapters if provided
    if chapters:
        # Keep other 'book' settings but update 'chapters'
        config['book']['chapters'] = chapters
    
    # Create the output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Write the configuration to _quarto.yml
    config_file = output_path / "_quarto.yml"
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    # Create CSS file for HTML output
    css_file = output_path / "styles.css"
    css_content = create_css_styles(sync_json=sync_json)
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    return str(config_file)


def generate_single_document_config(sync_json: bool = True, citation_style: Optional[str] = None) -> Dict[str, Any]:
    """Generate Quarto YAML configuration for single documents (not books).
    
    This function creates a configuration suitable for rendering individual
    Quarto documents with equation numbering and cross-referencing. It's
    optimized for standalone documents rather than multi-chapter books.
    
    Args:
        sync_json: Whether to synchronize JSON files before reading. Defaults to True.
        
    Returns:
        Dict[str, Any]: Quarto YAML configuration dictionary for single documents
            including PDF and HTML output formats.
            
    Assumes:
        The required JSON configuration files exist and contain valid color and
        project information.
    """
    # Load project configuration
    project_config = get_project_config(sync_json=sync_json)
    
    # Extract relevant project information
    project_info = project_config.get('project', {})
    copyright_info = project_config.get('copyright', {})
    
    # Get document information - no fallbacks, all from JSON
    title = project_info['name']
    subtitle = project_info.get('description', '')
    author_date = project_info.get('updated_date') or project_info['created_date']
    
    # Determine CSL style to use - must be provided
    if not citation_style:
        raise ValueError("citation_style parameter is required")
    csl_file = validate_csl_style(citation_style)
    
    # Create base configuration for single document - load from setup.json instead of hardcoded values
    quarto_config = get_config_value('formats_quarto', 'quarto', {}, sync_json)
    project_type = quarto_config.get('single_document_project_type', 'default')
    language = quarto_config.get('language', 'es')
    
    # Get crossref configuration from setup.json
    crossref_config = get_config_value('formats_quarto', 'crossref', {}, sync_json)
    
    config = {
        'project': {
            'type': project_type
        },
        'lang': language,
        'title': title,
        'subtitle': subtitle,
        'author': author_date,
        'date': 'today',
        'bibliography': 'references/references.bib',
        'csl': f'references/{csl_file}',
        'execute': {
            'echo': crossref_config.get('execute_echo', False)
        },
        'crossref': {
            'chapters': crossref_config.get('chapters', False),
            'eq-prefix': crossref_config.get('eq_prefix', 'Ec.'),
            'eq-labels': crossref_config.get('eq_labels', 'arabic'),
            'fig-prefix': crossref_config.get('fig_prefix', 'Figura'),
            'fig-labels': crossref_config.get('fig_labels', 'arabic'),
            'tbl-prefix': crossref_config.get('tbl_prefix', 'Tabla'),
            'tbl-labels': crossref_config.get('tbl_labels', 'arabic')
        }
    }
    
    # Get colors for styling
    primary_blue = get_color('brand.primary_blue', format_type="hex", sync_json=sync_json)
    accent_red = get_color('brand.accent_red', format_type="hex", sync_json=sync_json)
    secondary_gray = get_color('brand.secondary_gray', format_type="hex", sync_json=sync_json)
    
    # Gray scales from config
    gray_1 = get_color('general.light_gray', format_type="hex", sync_json=sync_json)
    gray_2 = get_color('general.medium_gray', format_type="hex", sync_json=sync_json)
    gray_4 = get_color('general.dark_gray', format_type="hex", sync_json=sync_json)
    
    # Create PDF format configuration
    pdf_config = {
        'number-sections': False,
        'include-in-header': {
            'text': f'''
\\usepackage[utf8]{{inputenc}}
\\usepackage{{fancyhdr}}
\\pagestyle{{fancy}}

\\clearpage
\\setcounter{{page}}{{0}}
\\pagenumbering{{arabic}}
\\lhead{{{project_config['client']['name']}}}
\\chead{{}}        
\\rhead{{{copyright_info['name']}}}
\\lfoot{{}}
\\cfoot{{\\thepage}}
\\rfoot{{}}

\\usepackage{{graphicx}}

\\usepackage{{xcolor}}
\\definecolor{{redANM}}{{RGB}}{{{_rgb_to_str(get_color('brand.accent_red', format_type="rgb", sync_json=sync_json))}}}
\\definecolor{{blueANM}}{{RGB}}{{{_rgb_to_str(get_color('brand.primary_blue', format_type="rgb", sync_json=sync_json))}}}
\\definecolor{{Gray_1}}{{RGB}}{{{_rgb_to_str(get_color('general.light_gray', format_type="rgb", sync_json=sync_json))}}}
\\definecolor{{Gray_2}}{{RGB}}{{{_rgb_to_str(get_color('general.medium_gray', format_type="rgb", sync_json=sync_json))}}}
\\definecolor{{Gray_4}}{{RGB}}{{{_rgb_to_str(get_color('general.dark_gray', format_type="rgb", sync_json=sync_json))}}}

% Equation numbering configuration
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{amsfonts}}
% Remove section-based numbering - equations will be numbered consecutively

\\usepackage{{sectsty}}
\\usepackage{{sectsty}}
\\sectionfont{{\\color{{blueANM}}}}
\\subsectionfont{{\\color{{Gray_4}}}}
'''
        },
        'documentclass': 'article',
        'fontsize': '11pt',
        'papersize': 'letter',
        'margin-left': '25mm',
        'margin-right': '25mm',
        'margin-top': '25mm',
        'margin-bottom': '25mm',
        'linestretch': 1.25,
        'toc-depth': 2,
        'toc': True
    }
    
    # Create HTML format configuration - use JSON config values
    quarto_config = get_config_value('formats_quarto', 'format.html', {}, sync_json)
    html_config = {
        'theme': quarto_config.get('theme', 'default'),
        'toc': quarto_config.get('toc', True),
        'toc-depth': quarto_config.get('toc-depth', 2),
        'number-sections': quarto_config.get('number-sections', False),
        'html-math-method': 'mathjax',
        'self-contained': quarto_config.get('self-contained', True),
        'embed-resources': quarto_config.get('embed-resources', True),
        'fig-width': quarto_config.get('fig-width', 5.0),
        'fig-height': quarto_config.get('fig-height', 3.8),
        'fig-align': quarto_config.get('fig-align', 'center'),
        'fig-responsive': quarto_config.get('fig-responsive', True),
        'fig-cap-location': quarto_config.get('fig-cap-location', 'bottom'),
        'tbl-cap-location': quarto_config.get('tbl-cap-location', 'top'),
        'fig-dpi': quarto_config.get('fig-dpi', 150),
        'code-fold': quarto_config.get('code-fold', False),
        'code-tools': quarto_config.get('code-tools', False)
    }
    
    # Add format configurations
    config['format'] = {
        'pdf': pdf_config,
        'html': html_config
    }
    
    return config


def create_single_document_config(output_dir: str, sync_json: bool = True, citation_style: Optional[str] = None) -> str:
    """Create _quarto.yml file for single documents.
    
    This function generates a _quarto.yml file and supporting styles.css file
    in the specified directory, optimized for single-document Quarto projects
    rather than books.
    
    Args:
        output_dir: Directory where the _quarto.yml file will be created.
        sync_json: Whether to synchronize JSON files before reading. Defaults to True.
        
    Returns:
        str: Absolute path to the created _quarto.yml file.
        
    Assumes:
        The output directory is writable, and the required JSON configuration 
        files exist.
    """
    # Generate the Quarto configuration for single documents
    config = generate_single_document_config(sync_json=sync_json, citation_style=citation_style)
    
    # Create the output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Write the configuration to _quarto.yml
    config_file = output_path / "_quarto.yml"
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    # Create CSS file for HTML output
    css_file = output_path / "styles.css"
    css_content = create_css_styles(sync_json=sync_json)
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    return str(config_file)


def create_latex_header_includes(sync_json: bool = True) -> List[str]:
    """Create LaTeX header includes for PDF styling.
    
    Generates a list of LaTeX commands for inclusion in the header of PDF documents,
    including color definitions based on the project's color scheme from JSON
    configuration files.
    
    Args:
        sync_json: Whether to synchronize JSON files before reading. Defaults to True.
        
    Returns:
        List[str]: List of LaTeX commands for inclusion in document headers,
            including color definitions and styling directives.
            
    Assumes:
        The required JSON configuration files exist with valid color definitions.
    """
    # Get colors for styling from JSON configuration directly as RGB
    blue_rgb = get_color('brand.primary_blue', format_type="rgb", sync_json=sync_json)
    red_rgb = get_color('brand.accent_red', format_type="rgb", sync_json=sync_json)
    gray_rgb = get_color('brand.secondary_gray', format_type="rgb", sync_json=sync_json)
    
    # Create LaTeX header includes
    includes = [
        "\\usepackage{xcolor}",
        "\\usepackage{sectsty}",
        "\\usepackage{titlesec}",
        f"\\definecolor{{primaryblue}}{{RGB}}{{{blue_rgb[0]}, {blue_rgb[1]}, {blue_rgb[2]}}}",
        f"\\definecolor{{accentred}}{{RGB}}{{{red_rgb[0]}, {red_rgb[1]}, {red_rgb[2]}}}",
        f"\\definecolor{{secondarygray}}{{RGB}}{{{gray_rgb[0]}, {gray_rgb[1]}, {gray_rgb[2]}}}",
        "\\sectionfont{\\color{primaryblue}}",
        "\\subsectionfont{\\color{secondarygray}}",
        "\\subsubsectionfont{\\color{secondarygray}}",
    ]
    
    return includes


def create_css_styles(sync_json: bool = True) -> str:
    """Create CSS styles for HTML output.
    
    Generates CSS styling for HTML output based on the project's color scheme
    from JSON configuration files. The styles include heading colors, figure and
    table captions, equation styling, and cross-reference link colors.
    
    Args:
        sync_json: Whether to synchronize JSON files before reading. Defaults to True.
        
    Returns:
        str: Complete CSS styles as a string, ready to be written to a styles.css file.
        
    Assumes:
        The required JSON configuration files exist with valid color definitions.
    """
    # Get colors for styling from JSON configuration
    primary_blue = get_color('brand.primary_blue', format_type="hex", sync_json=sync_json)
    accent_red = get_color('brand.accent_red', format_type="hex", sync_json=sync_json)
    secondary_gray = get_color('brand.secondary_gray', format_type="hex", sync_json=sync_json)
    
    css = f"""
    /* Custom ePy_suite heading styles with high specificity */
    .quarto-title-block h1,
    h1.title,
    h1 {{ 
        color: {primary_blue} !important; 
    }}
    
    .quarto-title-block h2,
    h2.subtitle,
    h2 {{ 
        color: {secondary_gray} !important; 
    }}
    
    .quarto-title-block h3,
    h3 {{ 
        color: {secondary_gray} !important; 
    }}
    
    .quarto-title-block h4,
    h4 {{ 
        color: {secondary_gray} !important; 
    }}
    
    .quarto-title-block h5,
    h5 {{ 
        color: {secondary_gray} !important; 
    }}
    
    .quarto-title-block h6,
    h6 {{ 
        color: {secondary_gray} !important; 
    }}
    
    /* Override any theme colors that might interfere */
    .content h1, .content h2, .content h3, .content h4, .content h5, .content h6 {{
        color: inherit !important;
    }}
    
    /* Ensure table of contents uses the same colors */
    #TOC a[href*="#"] {{
        color: inherit !important;
    }}
    
    /* Figure and table captions */
    .figure-caption, .table-caption {{
        font-size: 10pt;
        color: {secondary_gray};
        font-style: italic;
    }}
    
    .table-caption {{
        caption-side: top;
        margin-bottom: 0.5em;
    }}
    
    .figure-caption {{
        margin-top: 0.5em;
    }}
    
    /* Equation styling */
    .mjx-chtml {{
        font-size: 1.1em !important;
    }}
    
    .mjx-math {{
        color: #333 !important;
    }}
    
    /* Equation numbering */
    .mjx-mrow .mjx-texatom {{
        margin-right: 0.2em;
    }}
    
    /* Cross-reference links */
    a[href^="#eq-"] {{
        color: {primary_blue} !important;
        text-decoration: none;
    }}
    
    a[href^="#eq-"]:hover {{
        text-decoration: underline;
    }}
    """
    
    return css


def copy_setup_files(setup_dir: str, sync_json: bool = True) -> None:
    """Copy setup files including Word templates and other assets for Quarto.
    
    This function ensures that necessary setup files (Word templates, logos, etc.)
    exist in the specified setup directory. It will copy them from the package's
    setup files if available.
    
    Args:
        setup_dir: Path to setup directory where files should be copied to.
        sync_json: Whether to sync JSON files before looking for setup files.
            Defaults to True.
            
    Returns:
        None
        
    Assumes:
        The setup_dir is writable. If the source setup directory doesn't exist
        in the package, no files will be copied.
    """
    # Create setup directory if it doesn't exist
    os.makedirs(setup_dir, exist_ok=True)
    
    # Path to source setup files in package
    src_setup_dir = Path(__file__).parent.parent / "setup"
    
    # Only try to copy files if the source directory exists
    if not src_setup_dir.exists():
        # No setup files available to copy
        return
    
    # Copy Word template if available
    template_file = os.path.join(setup_dir, "Template.docx")
    src_template_file = src_setup_dir / "Template.docx"
    
    if src_template_file.exists():
        shutil.copy2(src_template_file, template_file)
    
    # Copy logo files if available
    logo_file = os.path.join(setup_dir, "logo.png")
    src_logo_file = src_setup_dir / "logo.png"
    
    if src_logo_file.exists():
        shutil.copy2(src_logo_file, logo_file)
    
    # Copy any other setup files
    for file_path in src_setup_dir.iterdir():
        if file_path.is_file() and file_path.name not in ["Template.docx", "logo.png"]:
            dest_file = os.path.join(setup_dir, file_path.name)
            try:
                shutil.copy2(file_path, dest_file)
            except Exception:
                # Skip files that can't be copied
                pass


def get_available_csl_styles() -> Dict[str, str]:
    """Get available CSL citation styles from the references directory.
    
    Returns:
        Dict[str, str]: Dictionary mapping style names to CSL file names
        
    Example:
        {
            'ieee': 'ieee.csl',
            'apa': 'apa.csl', 
            'chicago': 'chicago.csl'
        }
    """
    references_dir = Path(__file__).parent.parent / "references"
    available_styles = {}
    
    if references_dir.exists():
        for csl_file in references_dir.glob("*.csl"):
            style_name = csl_file.stem.lower()
            available_styles[style_name] = csl_file.name
    
    return available_styles


def validate_csl_style(style_name: str) -> str:
    """Validate and get the CSL file name for a given style.
    
    Args:
        style_name: Name of the citation style (e.g., 'ieee', 'apa', 'chicago')
        
    Returns:
        str: CSL file name (e.g., 'ieee.csl')
        
    Raises:
        ValueError: If the style is not available in references directory
    """
    if not style_name:
        raise ValueError("Citation style name is required")
    
    available_styles = get_available_csl_styles()
    
    if not available_styles:
        raise ValueError("No CSL files found in references directory")
    
    # Normalize style name
    style_name = style_name.lower().strip()
    
    if style_name in available_styles:
        return available_styles[style_name]
    
    # If not found, check if it's already a .csl filename
    if style_name.endswith('.csl'):
        base_name = style_name[:-4]
        if base_name in available_styles:
            return style_name
    
    # If style not found, raise error
    available_list = ', '.join(available_styles.keys())
    raise ValueError(f"Citation style '{style_name}' not found. Available styles: {available_list}")


def get_csl_style_for_layout(layout_name: str) -> str:
    """Get citation style from layout configuration.
    
    Args:
        layout_name: Name of the layout from layouts.json
        
    Returns:
        str: Citation style name from layout configuration
        
    Raises:
        ValueError: If layout is not found in layouts.json
    """
    import json
    from pathlib import Path
    
    # Load layouts configuration
    layouts_file = Path(__file__).parent.parent / "reports" / "layouts.json"
    
    if not layouts_file.exists():
        raise ValueError(f"Layouts configuration file not found: {layouts_file}")
    
    with open(layouts_file, 'r', encoding='utf-8') as f:
        layouts_config = json.load(f)
    
    if layout_name not in layouts_config:
        available_layouts = ', '.join(layouts_config.keys())
        raise ValueError(f"Layout '{layout_name}' not found. Available layouts: {available_layouts}")
    
    layout = layouts_config[layout_name]
    
    if 'citation_style' not in layout:
        raise ValueError(f"Layout '{layout_name}' does not specify citation_style")
    
    return layout['citation_style']
