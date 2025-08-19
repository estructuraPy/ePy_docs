"""Quarto Document Generation and Styling for ePy_docs.

This module handles document generation using Quarto, including PDF and HTML
output formats. It provides functions to create Quarto YAML configurations,
generate CSS styles, and set up complete Quarto projects for document compilation.
"""
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import os
import yaml
import shutil
import subprocess
import json

# Import from the page configuration module
from ePy_docs.components.page import (
    get_color, get_project_config, get_config_value, _ConfigManager,
    get_layout_config, get_default_citation_style, get_header_style, validate_csl_style,
    sync_ref, create_css_styles
)
from ePy_docs.components.colors import rgb_to_latex_str, _load_cached_colors


def _load_config_file(config_type: str = "page") -> Dict[str, Any]:
    """Load configuration file generically using ConfigManager with sync_json.
    
    Args:
        config_type: Type of configuration to load (currently only 'page' supported)
        
    Returns:
        Dict containing the configuration
        
    Raises:
        ValueError: If configuration file is not found or invalid type
    """
    valid_types = ["page"]
    if config_type not in valid_types:
        raise ValueError(f"Invalid config_type '{config_type}'. Must be one of: {valid_types}")
    
    from ePy_docs.components.page import _ConfigManager
    
    config_manager = _ConfigManager()
    config = config_manager.get_config_by_path(f'components/{config_type}.json', sync_json=True)
    
    if not config:
        raise ValueError(f"Configuration file not found: components/{config_type}.json")
        
    return config


def generate_quarto_config(sync_json: bool = True, layout_name: str = None) -> Dict[str, Any]:
    """Generate Quarto YAML configuration from project settings.
    
    This function reads the project configuration and styling information
    from JSON files and creates a complete Quarto configuration dictionary
    for the document's appearance. The configuration includes document metadata,
    formatting options for PDF and HTML outputs, and styling based on the
    project's color scheme.
    
    Citation style is automatically determined from the layout in configuration files.
    
    Args:
        sync_json: Whether to synchronize JSON files before reading. Defaults to True.
        layout_name: Layout name to use. If None, uses default_layout from page.json.
        
    Returns:
        Dict[str, Any]: Complete Quarto YAML configuration dictionary ready for
            rendering with Quarto.
            
    Assumes:
        The required JSON configuration files exist and contain valid color and
        project information.
    """
    # Load configuration from page.json - NO FALLBACKS
    page_config = _load_config_file("page")
    
    # Get layout configuration  
    if layout_name is None:
        if 'default_layout' not in page_config['format']:
            raise ValueError("Missing 'default_layout' in page.json format section")
        layout_name = page_config['format']['default_layout']
    
    # Load project configuration
    project_config = get_project_config(sync_json=sync_json)
    
    # Extract relevant project information - NO FALLBACKS
    project_info = project_config['project']
    copyright_info = project_config['copyright']
    
    # Get document information - all from JSON, fail if missing
    title = project_info['name']
    subtitle = project_info['description']
    author_date = project_info['created_date']
    
    # Get header style from layout
    header_style_from_layout = get_header_style()
    
    # Determine CSL style from layout
    citation_style = get_default_citation_style()
    csl_file = validate_csl_style(citation_style)
    
    # Get references paths from DirectoryConfig - NO FALLBACKS
    from ePy_docs.project.setup import DirectoryConfig
    dir_config = DirectoryConfig()
    config_dir = Path(dir_config.folders.config)
    references_dir = config_dir / "references"
    
    # Use absolute paths with proper forward slashes for Quarto/Pandoc
    bib_path = str(references_dir / "references.bib").replace("\\", "/")
    csl_path = str(references_dir / f"{csl_file}").replace("\\", "/")
    
    # Use page_config as styler_config for compatibility
    styler_config = page_config
    
    # Get crossref configuration from component JSON files, NO FALLBACKS
    from ePy_docs.components.page import _ConfigManager
    config_manager = _ConfigManager()
    
    # Load configuration for images (for display settings, not crossref)
    images_config = config_manager.get_config_by_path('components/images.json')
    
    if not images_config:
        raise ValueError("Missing images configuration in components/images.json")
    
    # Load font configuration from text.json using ConfigManager - NO FALLBACKS
    text_config = config_manager.get_config_by_path('components/text.json', sync_json=sync_json)
    if not text_config:
        raise ValueError("Missing text configuration from components/text.json")
    
    if 'text' not in text_config or 'normal' not in text_config['text']:
        raise ValueError("Missing text.normal configuration in text.json")
    
    normal_text = text_config['text']['normal']
    if 'fontSize' not in normal_text:
        raise ValueError("Missing fontSize in text.normal configuration")
    if 'lineSpacing' not in normal_text:
        raise ValueError("Missing lineSpacing in text.normal configuration")
    
    font_size = normal_text['fontSize']
    line_spacing = normal_text['lineSpacing']
    
    # Get margins from current layout instead of hardcoded pdf_settings
    if layout_name not in page_config['layouts']:
        raise ValueError(f"Layout '{layout_name}' not found in page.json")
    
    current_layout = page_config['layouts'][layout_name]
    layout_margins = current_layout['margins']
    
    # Convert inches to mm for LaTeX (1 inch = 25.4 mm)
    margin_top_mm = f"{layout_margins['top'] * 25.4:.0f}mm"
    margin_bottom_mm = f"{layout_margins['bottom'] * 25.4:.0f}mm"
    margin_left_mm = f"{layout_margins['left'] * 25.4:.0f}mm"
    margin_right_mm = f"{layout_margins['right'] * 25.4:.0f}mm"
    
    config = {
        'project': {
            'type': page_config['project']['type']
        },
        'lang': page_config['project']['lang'],
        'book': {
            'title': title,
            'subtitle': subtitle,
            'author': author_date,
        },
        'bibliography': bib_path,
        'csl': csl_path,
        'execute': {
            'echo': page_config['execute']['echo']
        },
        'crossref': {
            'chapters': page_config['crossref']['chapters'],
            'eq-labels': page_config['crossref']['eq-labels'],
            'fig-labels': page_config['crossref']['fig-labels'],
            'tbl-labels': page_config['crossref']['tbl-labels']
        }
    }
    
    # Get colors for styling based on header_style from layout
    # Get header colors based on the layout's header_style
    h1_color_rgb = get_color(f'reports.header_styles.{header_style_from_layout}.h1', format_type="rgb", sync_json=sync_json)
    h2_color_rgb = get_color(f'reports.header_styles.{header_style_from_layout}.h2', format_type="rgb", sync_json=sync_json)
    h3_color_rgb = get_color(f'reports.header_styles.{header_style_from_layout}.h3', format_type="rgb", sync_json=sync_json)
    
    # Also get brand colors for other elements
    primary_blue = get_color('brand.brand_secondary', format_type="hex", sync_json=sync_json)
    accent_red = get_color('brand.brand_primary', format_type="hex", sync_json=sync_json)
    secondary_gray = get_color('brand.brand_tertiary', format_type="hex", sync_json=sync_json)
    
    # Gray scales - all from config
    gray_1 = get_color('general.light_gray', format_type="hex", sync_json=sync_json)
    gray_2 = get_color('general.medium_gray', format_type="hex", sync_json=sync_json)
    gray_4 = get_color('general.dark_gray', format_type="hex", sync_json=sync_json)
    
    # Create PDF format configuration with LaTeX header
    # Combine common settings with PDF-specific settings
    if 'common' not in styler_config['format']:
        raise ValueError("Missing 'common' section in format configuration")
    if 'pdf' not in styler_config['format']:
        raise ValueError("Missing 'pdf' section in format configuration")
        
    common_config = styler_config['format']['common']
    pdf_format_config = styler_config['format']['pdf']
    
    # Merge common and PDF-specific configurations
    merged_pdf_config = {**common_config, **pdf_format_config}
    
    pdf_config = {
        'number-sections': merged_pdf_config['number-sections'],
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
\definecolor{{brandSecondary}}{{RGB}}{{{rgb_to_latex_str(get_color('brand.brand_secondary', format_type="rgb", sync_json=sync_json))}}}
\definecolor{{Gray_1}}{{RGB}}{{{rgb_to_latex_str(get_color('general.light_gray', format_type="rgb", sync_json=sync_json))}}}
\definecolor{{Gray_2}}{{RGB}}{{{rgb_to_latex_str(get_color('general.medium_gray', format_type="rgb", sync_json=sync_json))}}}
\definecolor{{Gray_4}}{{RGB}}{{{rgb_to_latex_str(get_color('general.dark_gray', format_type="rgb", sync_json=sync_json))}}}

% Header colors based on layout header_style: {header_style_from_layout}
\definecolor{{h1color}}{{RGB}}{{{rgb_to_latex_str(h1_color_rgb)}}}
\definecolor{{h2color}}{{RGB}}{{{rgb_to_latex_str(h2_color_rgb)}}}
\definecolor{{h3color}}{{RGB}}{{{rgb_to_latex_str(h3_color_rgb)}}}

\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{amsfonts}}

\\usepackage{{sectsty}}
\\chapterfont{{\\color{{h1color}}}}  % Chapter uses h1 color from header_style  
\\sectionfont{{\\color{{h2color}}}}  % Section (#) uses h2 color from header_style
\\subsectionfont{{\\color{{h3color}}}}  % Subsection (##) uses h3 color from header_style
\\subsubsectionfont{{\\color{{h3color}}}}  % Subsubsection (###) uses h3 color from header_style

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
        'documentclass': merged_pdf_config['documentclass'],
        'fontsize': f'{font_size}pt',
        'papersize': merged_pdf_config['papersize'],
        'margin-left': margin_left_mm,
        'margin-right': margin_right_mm,
        'margin-top': margin_top_mm,
        'margin-bottom': margin_bottom_mm,
        'linestretch': line_spacing,
        'toc-depth': merged_pdf_config['toc-depth'],
        'toc': merged_pdf_config['toc'],
        'lof': merged_pdf_config['lof'],
        'lot': merged_pdf_config['lot'],
        # Figure configurations from images.json
        'fig-width': images_config['display']['max_width_inches'],
        'fig-height': images_config['display']['max_width_inches'] * 0.65,  # Maintain aspect ratio
        'fig-pos': merged_pdf_config['fig-pos'],
        'fig-cap-location': merged_pdf_config['fig-cap-location'],
        'colorlinks': merged_pdf_config.get('colorlinks', False)
    }
    
    # Create HTML format configuration - NO FALLBACKS, read from component configs
    if 'html' not in styler_config['format']:
        raise ValueError("Missing 'html' section in format configuration")
    
    html_format_config = styler_config['format']['html']
    
    # Merge common and HTML-specific configurations
    merged_html_config = {**common_config, **html_format_config}
    
    html_config = {
        'theme': merged_html_config['theme'],
        'toc': merged_html_config['toc'],
        'toc-depth': merged_html_config['toc-depth'],
        'number-sections': merged_html_config['number-sections'],
        'html-math-method': 'mathjax',
        'self-contained': merged_html_config['self-contained'],
        'embed-resources': merged_html_config['embed-resources'],
        # Figure configurations from images.json
        'fig-width': images_config['display']['max_width_inches_html'],
        'fig-height': images_config['display']['max_width_inches_html'] * 0.6,  # Maintain aspect ratio
        'fig-align': images_config['styling']['alignment'].lower(),
        'fig-responsive': images_config['display']['html_responsive'],
        'fig-cap-location': merged_html_config['fig-cap-location'],
        'tbl-cap-location': merged_html_config['tbl-cap-location'],
        'fig-dpi': images_config['display']['dpi'] // 2,  # Half DPI for HTML
        'code-fold': merged_html_config['code-fold'],
        'code-tools': merged_html_config['code-tools']
    }
    
    # Add format configurations to main config
    config['format'] = {
        'pdf': pdf_config,
        'html': html_config
    }
    
    return config


def create_quarto_yml(output_dir: str, chapters: Optional[List[str]] = None, header_style: str = "formal", sync_json: bool = True) -> str:
    """Create _quarto.yml file from project configuration.
    
    This function generates a _quarto.yml file and supporting styles.css file in 
    the specified directory, based on the project configuration from JSON files.
    
    Args:
        output_dir: Directory where the _quarto.yml file will be created.
        chapters: Optional list of chapter paths to include in the configuration.
            If provided, these will be set as the book chapters in order.
        header_style: Header style to use ('formal', 'modern', 'branded', 'clean'). Defaults to 'formal'.
        sync_json: Whether to synchronize JSON files before reading. Defaults to True.
        
    Returns:
        str: Absolute path to the created _quarto.yml file.
        
    Assumes:
        The output directory is writable, and the required JSON configuration 
        files exist.
    """
    # Generate the Quarto configuration - citation style determined automatically from layout
    config = generate_quarto_config(sync_json=sync_json)
    
    # Get header style from the layout
    header_style = get_header_style()
    
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
    css_content = create_css_styles(header_style=header_style, sync_json=sync_json)
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    return str(config_file)




def create_quarto_project(output_dir: str, 
                         chapters: Optional[List[str]] = None, 
                         sync_json: bool = True,
                         create_index: bool = True) -> Dict[str, str]:
    """Create a complete Quarto project directory with all necessary files.
    
    This function creates a ready-to-compile Quarto book project with:
    - _quarto.yml configuration file
    - styles.css for HTML output styling  
    
    Citation style is automatically determined from the layout in page.json.  
    - index.qmd (optional) as the main entry point
    - All necessary configuration based on project JSON files
    
    Args:
        output_dir: Directory where the Quarto project will be created.
        citation_style: Citation style to use. If not provided, uses layout default.
        chapters: Optional list of chapter paths to include. If provided,
            these will be set as the book chapters in order.
        sync_json: Whether to synchronize JSON files before reading. Defaults to True.
        create_index: Whether to create an index.qmd file. Defaults to True.
        layout_name: Layout to use for default settings. Defaults to 'technical'.
        
    Returns:
        Dict[str, str]: Dictionary with paths to created files:
            - 'quarto_yml': Path to _quarto.yml
            - 'styles_css': Path to styles.css  
            - 'index_qmd': Path to index.qmd (if created)
            - 'project_dir': Path to the project directory
        
    Raises:
        ValueError: If citation_style is not supported.
        OSError: If output_dir cannot be created or is not writable.
        
    Example:
        >>> files = create_quarto_project("/path/to/my_book", 
        ...                              chapters=["intro.qmd", "chapter1.qmd"])
        >>> print(f"Project created at: {files['project_dir']}")
    """
    # Validation will be handled by generate_quarto_config() when citation_style is used
    
    # Create the output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    created_files = {}
    created_files['project_dir'] = str(output_path.absolute())
    
    # 1. Create _quarto.yml configuration - citation style determined automatically
    quarto_yml_path = create_quarto_yml(
        output_dir=output_dir,
        chapters=chapters,
        sync_json=sync_json
    )
    created_files['quarto_yml'] = quarto_yml_path
    
    # 2. CSS file is already created by create_quarto_yml
    css_path = output_path / "styles.css"
    created_files['styles_css'] = str(css_path.absolute())
    
    # 3. Create index.qmd if requested
    if create_index:
        index_content = create_index_qmd(sync_json=sync_json)
        index_path = output_path / "index.qmd"
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        created_files['index_qmd'] = str(index_path.absolute())
    
    return created_files


def create_index_qmd(sync_json: bool = True) -> str:
    """Create content for an index.qmd file based on project configuration.
    
    Args:
        sync_json: Whether to synchronize JSON files before reading.
        
    Returns:
        str: Complete content for index.qmd file.
        
    Raises:
        FileNotFoundError: If project.json file doesn't exist.
        KeyError: If required keys are missing from configuration.
        JSONDecodeError: If JSON file is malformed.
    """
    from ePy_docs.components.page import _ConfigManager
    
    # Read project configuration using ConfigManager with sync_json
    config_manager = _ConfigManager()
    project_data = config_manager.get_config_by_path('project/project.json', sync_json=sync_json)
    
    if not project_data:
        raise ValueError("Missing project configuration from project/project.json")
    
    # Extract project information - fail if missing
    project_info = project_data['project']
    title = project_info['name']
    description = project_info['description']
    version = project_info['version']
    code = project_info['code']
    created_date = project_info['created_date']
    
    # Extract consultant information - fail if missing
    consultants = project_data['consultants']
    author = consultants[0]['name']
    author_specialty = consultants[0]['specialty']
    author_license = consultants[0]['license']
    
    # Extract client information - fail if missing  
    client_info = project_data['client']
    client_name = client_info['name']
    
    # Extract location information - fail if missing
    location_info = project_data['location']
    location = f"{location_info['city']}, {location_info['country']}"
    
    # Build author description
    author_description = author
    author_details = []
    if author_license:
        author_details.append(f"Carné CFIA: {author_license}")
    if author_specialty:
        author_details.append(author_specialty)
    if author_details:
        author_description += f"  \n{' | '.join(author_details)}"
    
    index_content = f'''# Prefacio {{.unnumbered}}

Este documento presenta el proyecto "{title}".

**Descripción:** {description}

**Cliente:** {client_name}

**Ubicación:** {location}

## Información del Proyecto {{.unnumbered}}

- **Código:** {code}
- **Versión:** {version}
- **Fecha de creación:** {created_date}

## Acerca de este documento {{.unnumbered}}

Esta documentación ha sido generada utilizando ePy_docs, un sistema de documentación 
técnica que integra código, análisis y reportes de ingeniería estructural.

## Responsabilidad Profesional {{.unnumbered}}

**{author_description}**

---

*Generado con ePy_docs - Sistema de documentación técnica para ingeniería*
'''
    
    return index_content


# def copy_setup_files(setup_dir: str, sync_json: bool = True) -> None:
#     """Copy setup files including Word templates and other assets for Quarto.
    
#     This function ensures that necessary setup files (Word templates, logos, etc.)
#     exist in the specified setup directory. It will copy them from the package's
#     setup files if available.
    
#     Args:
#         setup_dir: Path to setup directory where files should be copied to.
#         sync_json: Whether to sync JSON files before looking for setup files.
#             Defaults to True.
            
#     Returns:
#         None
        
#     Assumes:
#         The setup_dir is writable. If the source setup directory doesn't exist
#         in the package, no files will be copied.
#     """
#     # Create setup directory if it doesn't exist
#     os.makedirs(setup_dir, exist_ok=True)
    
#     # Path to source setup files in package
#     src_setup_dir = Path(__file__).parent.parent / "setup"
    
#     # Only try to copy files if the source directory exists
#     if not src_setup_dir.exists():
#         # No setup files available to copy
#         return
    
#     # Copy Word template if available
#     template_file = os.path.join(setup_dir, "Template.docx")
#     src_template_file = src_setup_dir / "Template.docx"
    
#     if src_template_file.exists():
#         shutil.copy2(src_template_file, template_file)
    
#     # Copy logo files if available
#     logo_file = os.path.join(setup_dir, "logo.png")
#     src_logo_file = src_setup_dir / "logo.png"
    
#     if src_logo_file.exists():
#         shutil.copy2(src_logo_file, logo_file)
    
#     # Copy any other setup files
#     for file_path in src_setup_dir.iterdir():
#         if file_path.is_file() and file_path.name not in ["Template.docx", "logo.png"]:
#             dest_file = os.path.join(setup_dir, file_path.name)
#             try:
#                 shutil.copy2(file_path, dest_file)
#             except Exception:
#                 # Skip files that can't be copied
#                 pass



class PDFRenderer:
    """Handles PDF rendering using Quarto with configuration from page.json."""
    
    def __init__(self):
        """Initialize PDF renderer with styling configuration."""
        config_manager = _ConfigManager()
        self.styles_config = config_manager.get_styles_config()
        
        # Require styles_config - NO fallbacks
        if not self.styles_config:
            raise ValueError("Missing styles configuration from components/page.json")
        
        # Load PDF settings from components/page.json using ConfigManager with sync_json
        page_config = config_manager.get_config_by_path('components/page.json', sync_json=True)
        if not page_config:
            raise ValueError("Missing page configuration from components/page.json")
        
        try:
            # Get layout configuration for dynamic margins
            if 'default_layout' not in page_config['format']:
                raise ValueError("Missing 'default_layout' in page.json format section")
            layout_name = page_config['format']['default_layout']
            if layout_name not in page_config['layouts']:
                raise ValueError(f"Layout '{layout_name}' not found in page.json")
            
            current_layout = page_config['layouts'][layout_name]
            layout_margins = current_layout['margins']
            
            # Convert inches to points for ReportLab (1 inch = 72 points)
            margin_top_pts = layout_margins['top'] * 72
            margin_bottom_pts = layout_margins['bottom'] * 72
            margin_left_pts = layout_margins['left'] * 72
            margin_right_pts = layout_margins['right'] * 72
            
            # Extract PDF-related settings from page config
            if 'toc' not in page_config:
                raise ValueError("Missing 'toc' in page.json")
            if 'toc-depth' not in page_config:
                raise ValueError("Missing 'toc-depth' in page.json")
            if 'number-sections' not in page_config:
                raise ValueError("Missing 'number-sections' in page.json")
            
            # Get settings from format configuration
            if 'format' not in page_config:
                raise ValueError("Missing 'format' section in page.json")
            if 'common' not in page_config['format']:
                raise ValueError("Missing 'common' section in format configuration")
            if 'pdf' not in page_config['format']:
                raise ValueError("Missing 'pdf' section in format configuration")
                
            common_config = page_config['format']['common']
            pdf_config = page_config['format']['pdf']
            
            # Merge common and PDF-specific configurations
            merged_config = {**common_config, **pdf_config}
            
            self.pdf_settings = {
                "documentclass": merged_config['documentclass'],
                "pagesize": merged_config['papersize'],
                "toc": merged_config['toc'],
                "toc_depth": merged_config['toc-depth'],
                "number_sections": merged_config['number-sections'],
                "colorlinks": merged_config['colorlinks'],
                "fig_cap_location": merged_config['fig-cap-location'],
                "fig_pos": merged_config['fig-pos'],
                "margins": {
                    "top": margin_top_pts,
                    "bottom": margin_bottom_pts,
                    "left": margin_left_pts,
                    "right": margin_right_pts
                }
            }
        except Exception as e:
            raise ValueError(f"Error loading page configuration: {e}")
    
    def _load_crossref_config(self) -> Dict[str, Any]:
        """Load crossref configuration from component JSON files."""
        config_manager = _ConfigManager()
        crossref_config = {}
        
        # Load images crossref (figures) - REQUIRED
        images_config = config_manager.get_config_by_path('components/images.json')
        if not images_config or 'crossref' not in images_config:
            raise ValueError("Missing 'crossref' configuration in components/images.json")
        crossref_config.update(images_config['crossref'])
        
        # Load tables crossref - REQUIRED
        tables_config = config_manager.get_config_by_path('components/tables.json')
        if not tables_config or 'crossref' not in tables_config:
            raise ValueError("Missing 'crossref' configuration in components/tables.json")
        crossref_config.update(tables_config['crossref'])
        
        # Load equations crossref - REQUIRED
        equations_config = config_manager.get_config_by_path('components/equations.json')
        if not equations_config or 'crossref' not in equations_config:
            raise ValueError("Missing 'crossref' configuration in components/equations.json")
        crossref_config.update(equations_config['crossref'])
        
        return crossref_config
    
    def _load_typography_config(self, header_style: str = "formal") -> Dict[str, Any]:
        """Load typography configuration from JSON files - NO FALLBACKS.
        
        Args:
            header_style: The header style to use ('formal', 'modern', 'branded', 'clean').
        """
        config_manager = _ConfigManager()
        
        # Load text configuration - REQUIRED
        text_config = config_manager.get_config_by_path('components/text.json')
        if not text_config:
            raise ValueError("Missing text configuration from components/text.json")
        
        # Load colors configuration - REQUIRED  
        colors_config = config_manager.get_colors_config()
        if not colors_config:
            raise ValueError("Missing colors configuration from colors.json")
        
        # Extract required sections
        if 'headers' not in text_config:
            raise ValueError("Missing 'headers' section in components/text.json")
        headers_config = text_config['headers']
        if not headers_config:
            raise ValueError("Empty 'headers' section in components/text.json")
        
        if 'text' not in text_config:
            raise ValueError("Missing 'text' section in components/text.json")
        text_section_config = text_config['text']
        if not text_section_config:
            raise ValueError("Empty 'text' section in components/text.json")
        
        if 'reports' not in colors_config:
            raise ValueError("Missing 'reports' section in colors configuration")
        if 'header_styles' not in colors_config['reports']:
            raise ValueError("Missing 'header_styles' section in colors configuration")
        header_styles = colors_config['reports']['header_styles']
        if not header_styles:
            raise ValueError("Missing 'header_styles' section in colors configuration")
        if header_style not in header_styles:
            raise ValueError(f"Header style '{header_style}' not found in colors configuration")
        
        text_colors = header_styles[header_style]
        
        # Process styles - NO DEFAULTS
        combined_styles = {}
        
        # Process headers (h1, h2, h3) - REQUIRED
        header_mapping = {'h1': 'heading1', 'h2': 'heading2', 'h3': 'heading3'}
        for header_key, latex_key in header_mapping.items():
            if header_key not in headers_config:
                raise ValueError(f"Missing '{header_key}' configuration in components/text.json headers")
            
            combined_styles[latex_key] = headers_config[header_key].copy()
            
            if header_key not in text_colors:
                raise ValueError(f"Missing '{header_key}' color configuration in colors.json")
            combined_styles[latex_key]['textColor'] = text_colors[header_key]
        
        # Process text styles (normal, caption) - REQUIRED
        for style_name in ['normal', 'caption']:
            if style_name not in text_section_config:
                raise ValueError(f"Missing '{style_name}' configuration in components/text.json text section")
                
            combined_styles[style_name] = text_section_config[style_name].copy()
            
            if style_name not in text_colors:
                raise ValueError(f"Missing '{style_name}' color configuration in colors.json")
            combined_styles[style_name]['textColor'] = text_colors[style_name]
        
        return combined_styles
    
    def create_pdf_yaml_config(self, title: str, author: str, header_style: str = "formal") -> Dict[str, Any]:
        """Create PDF-specific YAML configuration using styles.json.
        
        Args:
            title: Document title
            author: Document author
            header_style: The header style to use ('formal', 'modern', 'branded', 'clean').
            
        Returns:
            PDF configuration dictionary
        """
        margins = self.pdf_settings['margins']
        pagesize = self.pdf_settings['pagesize']
        
        # Load typography configuration
        styles = self._load_typography_config(header_style=header_style)
        
        # Convert margins from points to inches
        margin_top = margins['top'] / 72
        margin_bottom = margins['bottom'] / 72
        margin_left = margins['left'] / 72
        margin_right = margins['right'] / 72
        
        heading1 = styles['heading1']
        heading2 = styles['heading2'] 
        heading3 = styles['heading3']
        normal = styles['normal']
        
        # Convert RGB colors to hex format
        def rgb_to_hex(rgb_list):
            return f"#{rgb_list[0]:02x}{rgb_list[1]:02x}{rgb_list[2]:02x}"
        
        h1_color = rgb_to_hex(heading1['textColor'])
        h2_color = rgb_to_hex(heading2['textColor'])
        h3_color = rgb_to_hex(heading3['textColor'])
        
        # Create LaTeX header for custom styling and figure handling as a list
        latex_header = [
            "\\usepackage{xcolor}",
            "\\usepackage{float}",
            "\\usepackage{caption}",
            "\\usepackage{subcaption}",
            f"\\definecolor{{heading1color}}{{HTML}}{{{h1_color[1:]}}}",
            f"\\definecolor{{heading2color}}{{HTML}}{{{h2_color[1:]}}}",
            f"\\definecolor{{heading3color}}{{HTML}}{{{h3_color[1:]}}}",
            "\\makeatletter",
            f"\\renewcommand{{\\section}}{{\\@startsection{{section}}{{1}}{{\\z@}}{{{heading1['spaceBefore']}pt}}{{{heading1['spaceAfter']}pt}}{{\\normalfont\\fontsize{{{heading1['fontSize']}}}{{{heading1['leading']}}}\\selectfont\\bfseries\\color{{heading1color}}}}}}",
            f"\\renewcommand{{\\subsection}}{{\\@startsection{{subsection}}{{2}}{{\\z@}}{{{heading2['spaceBefore']}pt}}{{{heading2['spaceAfter']}pt}}{{\\normalfont\\fontsize{{{heading2['fontSize']}}}{{{heading2['leading']}}}\\selectfont\\bfseries\\color{{heading2color}}}}}}",
            f"\\renewcommand{{\\subsubsection}}{{\\@startsection{{subsubsection}}{{3}}{{\\z@}}{{{heading3['spaceBefore']}pt}}{{{heading3['spaceAfter']}pt}}{{\\normalfont\\fontsize{{{heading3['fontSize']}}}{{{heading3['leading']}}}\\selectfont\\bfseries\\color{{heading3color}}}}}}",
            "\\makeatother",
            "\\captionsetup[figure]{position=bottom,labelfont=bf,textfont=normal}",
            "\\floatplacement{figure}{H}"
        ]
        
        # Load crossref configuration from component files
        crossref_config = self._load_crossref_config()
        
        return {
            'title': title,
            'author': author,
            'format': {
                'pdf': {
                    'documentclass': self.pdf_settings['documentclass'],
                    'geometry': [
                        f'top={margin_top}in',
                        f'bottom={margin_bottom}in',
                        f'left={margin_left}in',
                        f'right={margin_right}in'
                    ],
                    'papersize': pagesize,
                    'toc': self.pdf_settings['toc'],
                    'toc-depth': self.pdf_settings['toc_depth'],
                    'number-sections': self.pdf_settings['number_sections'],
                    'colorlinks': self.pdf_settings['colorlinks'],
                    # Add link colors automatically from brand_primary if available
                    **{k: v for k, v in self.pdf_settings.items() if k in ['linkcolor', 'urlcolor', 'citecolor', 'anchorcolor']},
                    'fontsize': f"{normal['fontSize']}pt",
                    'header-includes': latex_header,
                    'fig-cap-location': self.pdf_settings['fig_cap_location'],
                    'fig-pos': self.pdf_settings['fig_pos'],
                    'crossref': crossref_config
                }
            },
            'crossref': crossref_config
        }
    
    def render_pdf(self, qmd_file: str, output_dir: Optional[str] = None) -> str:
        """Render QMD file to PDF.
        
        Args:
            qmd_file: Path to the .qmd file
            output_dir: Optional output directory
            
        Returns:
            Path to the generated PDF file
        """
        qmd_path = os.path.abspath(qmd_file)
        if not os.path.exists(qmd_path):
            raise FileNotFoundError(f"QMD file not found: {qmd_path}")
        
        if output_dir is None:
            output_dir = os.path.dirname(qmd_path)
        else:
            output_dir = os.path.abspath(output_dir)
            os.makedirs(output_dir, exist_ok=True)
        
        qmd_basename = os.path.splitext(os.path.basename(qmd_path))[0]
        expected_pdf = os.path.join(os.path.dirname(qmd_path), f"{qmd_basename}.pdf")
        final_pdf = os.path.join(output_dir, f"{qmd_basename}.pdf")
        
        result = subprocess.run(
            ['quarto', 'render', qmd_path, '--to', 'pdf'],
            cwd=os.path.dirname(qmd_path),
            capture_output=True,
            text=True,
            check=True
        )
        
        if output_dir != os.path.dirname(qmd_path) and os.path.exists(expected_pdf):
            shutil.move(expected_pdf, final_pdf)
        elif os.path.exists(expected_pdf):
            final_pdf = expected_pdf
        
        if not os.path.exists(final_pdf):
            raise RuntimeError("PDF was not generated")
        
        return final_pdf
    
    def get_pdf_settings(self) -> Dict[str, Any]:
        """Get PDF-specific settings from configuration.
        
        Returns:
            PDF settings dictionary
        """
        return self.pdf_settings.copy()
