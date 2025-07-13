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

from ePy_docs.styler.setup import get_color, get_project_config


def _rgb_to_str(rgb_list: List[int]) -> str:
    """Convert RGB list to string format for LaTeX color definitions.
    
    Args:
        rgb_list: RGB color as [r, g, b] list where each value is an integer 0-255.
        
    Returns:
        str: String in the format "r, g, b" for LaTeX color definitions.
    """
    return f"{rgb_list[0]}, {rgb_list[1]}, {rgb_list[2]}"




def generate_quarto_config(sync_json: bool = True) -> Dict[str, Any]:
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
    
    # Get document information
    title = project_info.get('name', 'Memoria descriptiva de cálculo estructural')
    subtitle = project_info.get('description', '')
    author_date = project_info.get('updated_date', '') or project_info.get('created_date', '')
    
    # Create base configuration
    config = {
        'project': {
            'type': 'book'
        },
        'lang': 'es',
        'book': {
            'title': title,
            'subtitle': subtitle,
            'author': author_date,
        },
        'bibliography': 'references/references.bib',
        'csl': 'references/ieee.csl',
        'execute': {
            'echo': False
        },
        'crossref': {
            'chapters': False,
            'eq-prefix': 'Ec.',
            'eq-labels': 'arabic',
            'fig-prefix': 'Figura',
            'fig-labels': 'arabic',
            'tbl-prefix': 'Tabla',
            'tbl-labels': 'arabic'
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
\\lhead{{{project_config.get('client', {}).get('name', 'Cliente')}}}
\\chead{{}}        
\\rhead{{{copyright_info.get('name', 'Consultor')}}}
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
    
    # Create HTML format configuration
    html_config = {
        'theme': 'cosmo',
        'css': 'styles.css',
        'toc': True,
        'toc-depth': 2,
        'number-sections': False,
        'html-math-method': 'mathjax'
    }
    
    # Add format configurations to main config
    config['format'] = {
        'pdf': pdf_config,
        'html': html_config
    }
    
    return config


def create_quarto_yml(output_dir: str, chapters: Optional[List[str]] = None, sync_json: bool = True) -> str:
    """Create _quarto.yml file from project configuration.
    
    This function generates a _quarto.yml file and supporting styles.css file in 
    the specified directory, based on the project configuration from JSON files.
    
    Args:
        output_dir: Directory where the _quarto.yml file will be created.
        chapters: Optional list of chapter paths to include in the configuration.
            If provided, these will be set as the book chapters in order.
        sync_json: Whether to synchronize JSON files before reading. Defaults to True.
        
    Returns:
        str: Absolute path to the created _quarto.yml file.
        
    Assumes:
        The output directory is writable, and the required JSON configuration 
        files exist.
    """
    # Generate the Quarto configuration
    config = generate_quarto_config(sync_json=sync_json)
    
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


def generate_single_document_config(sync_json: bool = True) -> Dict[str, Any]:
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
    
    # Get document information
    title = project_info.get('name', 'Documento de Cálculo Estructural')
    subtitle = project_info.get('description', '')
    author_date = project_info.get('updated_date', '') or project_info.get('created_date', '')
    
    # Create base configuration for single document
    config = {
        'project': {
            'type': 'default'
        },
        'lang': 'es',
        'title': title,
        'subtitle': subtitle,
        'author': author_date,
        'date': 'today',
        'bibliography': 'references/references.bib',
        'csl': 'references/ieee.csl',
        'execute': {
            'echo': False
        },
        'crossref': {
            'chapters': False,
            'eq-prefix': 'Ec.',
            'eq-labels': 'arabic',
            'fig-prefix': 'Figura',
            'fig-labels': 'arabic',
            'tbl-prefix': 'Tabla',
            'tbl-labels': 'arabic'
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
\\lhead{{{project_config.get('client', {}).get('name', 'Cliente')}}}
\\chead{{}}        
\\rhead{{{copyright_info.get('name', 'Consultor')}}}
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
    
    # Create HTML format configuration
    html_config = {
        'theme': 'cosmo',
        'css': 'styles.css',
        'toc': True,
        'toc-depth': 2,
        'number-sections': False,
        'html-math-method': 'mathjax'
    }
    
    # Add format configurations
    config['format'] = {
        'pdf': pdf_config,
        'html': html_config
    }
    
    return config


def create_single_document_config(output_dir: str, sync_json: bool = True) -> str:
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
    config = generate_single_document_config(sync_json=sync_json)
    
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


def copy_or_create_references(references_dir: str, user_csl: Optional[str] = None) -> None:
    """Copy or create necessary reference files for Quarto.
    
    This function ensures that the necessary reference files (ieee.csl and references.bib)
    exist in the specified references directory. It will copy them from the package's
    reference files if available, or create minimal versions if not.
    
    Args:
        references_dir: Path to references directory where files should be created.
        user_csl: Optional path to a user-provided CSL file. If provided and the file
            exists, it will be used instead of the default ieee.csl.
            
    Returns:
        None
        
    Assumes:
        The references_dir is writable. If user_csl is provided, it should be a valid
        path to an existing CSL file.
    """
    # Create references directory if it doesn't exist
    os.makedirs(references_dir, exist_ok=True)
    
    # Path to source reference files in package
    src_references_dir = Path(__file__).parent.parent / "references"
    
    # Copy or create references.bib
    bib_file = os.path.join(references_dir, "references.bib")
    src_bib_file = src_references_dir / "references.bib"
    
    if src_bib_file.exists():
        # Copy from source if available
        shutil.copy2(src_bib_file, bib_file)
    else:
        # Create a minimal references.bib
        with open(bib_file, 'w', encoding='utf-8') as f:
            f.write("% References file for Quarto project\n")
    
    # Copy or create ieee.csl
    csl_file = os.path.join(references_dir, "ieee.csl")
    
    # If user provided a CSL file, use it
    if user_csl and os.path.exists(user_csl):
        shutil.copy2(user_csl, csl_file)
    else:
        # Otherwise use the default from the package
        src_csl_file = src_references_dir / "ieee.csl"
        
        if src_csl_file.exists():
            # Copy from source if available
            shutil.copy2(src_csl_file, csl_file)
        else:
            # Create a minimal IEEE CSL file
            with open(csl_file, 'w', encoding='utf-8') as f:
                f.write("""<?xml version="1.0" encoding="utf-8"?>
<style xmlns="http://purl.org/net/xbiblio/csl" class="in-text" version="1.0" demote-non-dropping-particle="sort-only">
  <info>
    <title>IEEE</title>
    <id>http://www.zotero.org/styles/ieee</id>
    <link href="http://www.zotero.org/styles/ieee" rel="self"/>
    <link href="http://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE_Reference_Guide.pdf" rel="documentation"/>
    <link href="https://journals.ieeeauthorcenter.ieee.org/your-role-in-article-production/ieee-editorial-style-manual/" rel="documentation"/>
    <category citation-format="numeric"/>
    <category field="engineering"/>
    <category field="generic-base"/>
    <updated>2024-01-11T00:52:46+10:00</updated>
  </info>
  <!-- Simplified IEEE CSL for Quarto -->
  <citation>
    <sort>
      <key variable="citation-number"/>
    </sort>
    <layout delimiter=", ">
      <group prefix="[" suffix="]" delimiter=", ">
        <text variable="citation-number"/>
      </group>
    </layout>
  </citation>
  <bibliography entry-spacing="0" second-field-align="flush">
    <layout>
      <text variable="citation-number" prefix="[" suffix="]"/>
      <text macro="author" suffix=", "/>
      <choose>
        <if type="article-journal">
          <group delimiter=", ">
            <text variable="title" quotes="true"/>
            <text variable="container-title" font-style="italic"/>
            <text variable="volume" prefix="vol. "/>
            <text variable="issue" prefix="no. "/>
            <text variable="page" prefix="pp. "/>
            <date variable="issued">
              <date-part name="year"/>
            </date>
          </group>
        </if>
        <else>
          <group delimiter=", ">
            <text variable="title" font-style="italic"/>
            <text variable="publisher"/>
            <date variable="issued">
              <date-part name="year"/>
            </date>
          </group>
        </else>
      </choose>
    </layout>
  </bibliography>
</style>
""")


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
