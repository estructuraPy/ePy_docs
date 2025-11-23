"""
Quarto Integration Module

Handles:
- Quarto YAML generation
- QMD file creation
- Quarto rendering (qmd -> pdf/html)
- Format coordination
"""

from typing import Dict, List, Optional, Tuple, Union, TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd
from pathlib import Path
import subprocess
import yaml
import inspect


# =============================================================================
# INTERNATIONALIZATION SUPPORT
# =============================================================================

TRANSLATIONS = {
    'en': {
        'project_information': 'Project Information',
        'client_information': 'Client Information', 
        'project_team': 'Project Team',
        'project_consultants': 'Project Consultants',
        'authors': 'Authors',
        'field': 'Field',
        'information': 'Information',
        'name': 'Name',
        'role': 'Role',
        'email': 'Email',
        'affiliation': 'Affiliation',
        'contact': 'Contact',
        'specialty': 'Specialty',
        'consultant': 'Consultant',
        'company': 'Company',
        'project_code': 'Project Code',
        'project_name': 'Project Name',
        'project_type': 'Project Type',
        'status': 'Status',
        'description': 'Description',
        'created_date': 'Created Date',
        'location': 'Location',
        'client_name': 'Client Name',
        'phone': 'Phone',
        'address': 'Address',
        'architectural': 'Architectural',
        'geotechnical': 'Geotechnical',
        'structural': 'Structural',
        'coordinates': 'Coordinates'
    },
    'es': {
        'project_information': 'Información del Proyecto',
        'client_information': 'Información del Cliente',
        'project_team': 'Equipo del Proyecto', 
        'project_consultants': 'Consultores del Proyecto',
        'authors': 'Autores',
        'field': 'Campo',
        'information': 'Información',
        'name': 'Nombre',
        'role': 'Rol',
        'email': 'Correo',
        'affiliation': 'Afiliación',
        'contact': 'Contacto',
        'specialty': 'Especialidad',
        'consultant': 'Consultor',
        'company': 'Empresa',
        'project_code': 'Código del Proyecto',
        'project_name': 'Nombre del Proyecto',
        'project_type': 'Tipo de Proyecto',
        'status': 'Estado',
        'description': 'Descripción',
        'created_date': 'Fecha de Creación',
        'location': 'Ubicación',
        'client_name': 'Nombre del Cliente',
        'phone': 'Teléfono',
        'address': 'Dirección',
        'architectural': 'Arquitectónico',
        'geotechnical': 'Geotécnico',
        'structural': 'Estructural',
        'coordinates': 'Coordenadas'
    }
}

def get_translation(key: str, language: str = 'en') -> str:
    """Get translation for a key in the specified language."""
    return TRANSLATIONS.get(language, TRANSLATIONS['en']).get(key, key.title())

def detect_language_from_config() -> str:
    """Detect language from layout configuration."""
    try:
        from ._config import ModularConfigLoader
        
        # Try to get language from config
        config_loader = ModularConfigLoader()
        config = config_loader.load_project()
        
        # Check various places for language setting
        language = config.get('language', 'en')
        if isinstance(language, dict):
            language = language.get('default', 'en')
            
        return language if language in ['en', 'es'] else 'en'
    except:
        return 'en'


# =============================================================================
# PROJECT METADATA EXTRACTION
# =============================================================================

def format_author_info(author_data: Dict[str, Any]) -> str:
    """
    Format author information with multiple roles, affiliations, and contacts.
    
    Args:
        author_data: Dictionary with author information
        
    Returns:
        Formatted author string with contacts included
    """
    name = author_data.get('name', 'Unknown Author')
    
    # Handle roles (can be string or list)
    roles = author_data.get('role', [])
    if isinstance(roles, str):
        roles = [roles]
    
    # Handle affiliations (can be string or list)  
    affiliations = author_data.get('affiliation', [])
    if isinstance(affiliations, str):
        affiliations = [affiliations]
    
    # Handle contacts (can be string or list)
    contacts = author_data.get('contact', [])
    if isinstance(contacts, str):
        contacts = [contacts]
    
    # Create formatted string with roles, affiliations and contacts
    parts = [name]
    
    if roles:
        roles_str = ', '.join(roles)
        parts.append(f"({roles_str})")
    
    if affiliations:
        # Combine affiliations with contacts if available
        affiliation_parts = []
        for i, affiliation in enumerate(affiliations):
            if i < len(contacts) and contacts[i]:
                affiliation_parts.append(f"{affiliation} ({contacts[i]})")
            else:
                affiliation_parts.append(affiliation)
        
        affiliations_str = ' & '.join(affiliation_parts)
        parts.append(f"- {affiliations_str}")
    elif contacts:
        # If no affiliations but have contacts
        contacts_str = ', '.join(contacts)
        parts.append(f"({contacts_str})")
    
    return ' '.join(parts)


def generate_project_info_table(language: str = None) -> str:
    """
    Generate project information table from project configuration.
    
    Args:
        language: Language code ('en', 'es'). If None, auto-detects from config.
        
    Returns:
        Markdown table with project information
    """
    try:
        from ._config import ModularConfigLoader
        
        # Detect language if not provided
        if language is None:
            language = detect_language_from_config()
        
        # Create config loader directly
        config_loader = ModularConfigLoader()
        config = config_loader.load_project()
        
        project_info = config.get('project', {})
        
        if not project_info:
            return f"\n<!-- No {get_translation('project_information', language).lower()} available -->\n"
        
        table = f"\n## {get_translation('project_information', language)}\n\n"
        table += f"| {get_translation('field', language)} | {get_translation('information', language)} |\n"
        table += "|:----------------------|:-------------------------------------|\n"
        
        # Map fields to translation keys
        field_translation_keys = {
            'code': 'project_code',
            'name': 'project_name',
            'type': 'project_type',
            'status': 'status',
            'description': 'description',
            'created_date': 'created_date'
        }
        
        # Add basic project fields (excluding nested objects)
        for field, value in project_info.items():
            if field not in ['location', 'client', 'team', 'consultants'] and value and value != "":
                translation_key = field_translation_keys.get(field, field)
                readable_name = get_translation(translation_key, language)
                table += f"| {readable_name} | {value} |\n"
        
        # Add location information if available
        location = project_info.get('location', {})
        if location:
            location_parts = []
            
            address = location.get('address', '')
            city = location.get('city', '')
            region = location.get('region', '')
            country = location.get('country', '')
            
            if address and address != "":
                location_parts.append(address)
            if city and city != "":
                location_parts.append(city)
            if region and region != "":
                location_parts.append(region)
            if country and country != "":
                location_parts.append(country)
            
            if location_parts:
                location_str = ', '.join(location_parts)
                table += f"| {get_translation('location', language)} | {location_str} |\n"
            
            # Add coordinates if available
            coordinates = location.get('coordinates', {})
            if coordinates:
                lat = coordinates.get('latitude')
                lng = coordinates.get('longitude')
                if lat is not None and lng is not None and (lat != 0.0 or lng != 0.0):
                    table += f"| {get_translation('coordinates', language)} | {lat}, {lng} |\n"
        
        table += "\n"
        return table
        
    except Exception as e:
        return f"\n<!-- Error generating project info table: {e} -->\n"


def generate_client_table(language: str = None) -> str:
    """
    Generate client information table from project configuration.
    
    Args:
        language: Language code ('en', 'es'). If None, auto-detects from config.
        
    Returns:
        Markdown table with client information
    """
    try:
        from ._config import ModularConfigLoader
        
        # Detect language if not provided
        if language is None:
            language = detect_language_from_config()
        
        # Create config loader directly
        config_loader = ModularConfigLoader()
        config = config_loader.load_project()
        
        project_info = config.get('project', {})
        client_info = project_info.get('client', {})
        
        if not client_info:
            return f"\n<!-- No {get_translation('client_information', language).lower()} available -->\n"
        
        table = f"\n## {get_translation('client_information', language)}\n\n"
        table += f"| {get_translation('field', language)} | {get_translation('information', language)} |\n"
        table += "|:----------------------|:-------------------------------------|\\n"
        
        # Map fields to readable names
        field_names = {
            'name': 'Client Name',
            'company': 'Company',
            'contact': 'Email',
            'phone': 'Phone',
            'address': 'Address'
        }
        
        for field, value in client_info.items():
            if value and value != "":  # Only include non-empty values
                readable_name = field_names.get(field, field.title())
                table += f"| {readable_name} | {value} |\n"
        
        table += "\n"
        return table
        
    except Exception as e:
        return f"\n<!-- Error generating client table: {e} -->\n"


def generate_team_table(language: str = None) -> str:
    """
    Generate team information table from project configuration.
    
    Args:
        language: Language code ('en', 'es'). If None, auto-detects from config.
        
    Returns:
        Markdown table with team information
    """
    try:
        from ._config import ModularConfigLoader
        
        # Detect language if not provided
        if language is None:
            language = detect_language_from_config()
        
        # Create config loader directly
        config_loader = ModularConfigLoader()
        config = config_loader.load_project()
        
        project_info = config.get('project', {})
        team_info = project_info.get('team', {})
        
        if not team_info:
            return f"\n<!-- No {get_translation('project_team', language).lower()} available -->\n"
        
        table = f"\n## {get_translation('project_team', language)}\n\n"
        table += f"| {get_translation('name', language)} | {get_translation('role', language)} | {get_translation('email', language)} |\n"
        table += "|:-----------------|:-------------------------|:---------------------------|\n"
        
        # Add lead engineer
        if 'lead_engineer' in team_info:
            lead = team_info['lead_engineer']
            name = lead.get('name', '')
            role = lead.get('role', '')
            email = lead.get('email', '')
            if name and name != "":  # Only add if name is not empty
                table += f"| {name} | {role or 'N/A'} | {email or 'N/A'} |\n"
        
        # Add project manager
        if 'project_manager' in team_info:
            pm = team_info['project_manager']
            name = pm.get('name', '')
            role = pm.get('role', '')
            email = pm.get('email', '')
            if name and name != "":  # Only add if name is not empty
                table += f"| {name} | {role or 'N/A'} | {email or 'N/A'} |\n"
        
        # Add designers
        if 'designers' in team_info:
            for designer in team_info['designers']:
                name = designer.get('name', '')
                role = designer.get('role', '')
                email = designer.get('email', '')
                if name and name != "":  # Only add if name is not empty
                    table += f"| {name} | {role or 'N/A'} | {email or 'N/A'} |\n"
        
        # Add engineers (if different from designers)
        if 'engineers' in team_info:
            for engineer in team_info['engineers']:
                name = engineer.get('name', '')
                role = engineer.get('role', '')
                email = engineer.get('email', '')
                if name and name != "":  # Only add if name is not empty
                    table += f"| {name} | {role or 'N/A'} | {email or 'N/A'} |\n"
        
        table += "\n"
        return table
        
    except Exception as e:
        return f"\n<!-- Error generating team table: {e} -->\n"


def generate_consultants_table(language: str = None) -> str:
    """
    Generate consultants information table from project configuration.
    
    Args:
        language: Language code ('en', 'es'). If None, auto-detects from config.
        
    Returns:
        Markdown table with consultants information
    """
    try:
        from ._config import ModularConfigLoader
        
        # Detect language if not provided
        if language is None:
            language = detect_language_from_config()
        
        # Create config loader directly
        config_loader = ModularConfigLoader()
        config = config_loader.load_project()
        
        project_info = config.get('project', {})
        consultants_info = project_info.get('consultants', {})
        
        if not consultants_info:
            return f"\n<!-- No {get_translation('project_consultants', language).lower()} available -->\n"
        
        table = f"\n## {get_translation('project_consultants', language)}\n\n"
        table += f"| {get_translation('specialty', language)} | {get_translation('consultant', language)} | {get_translation('company', language)} | {get_translation('contact', language)} |\n"
        table += "|:-------------|:------------------|:----------------|:---------------------------|\n"
        
        # Map consultant types to readable names
        specialty_names = {
            'architectural': 'Architectural',
            'geotechnical': 'Geotechnical',
            'mep': 'MEP',
            'structural': 'Structural'
        }
        
        for consultant_type, consultant_data in consultants_info.items():
            name = consultant_data.get('name', '')
            company = consultant_data.get('company', '')
            contact = consultant_data.get('contact', '')
            
            # Only add row if at least name is not empty
            if name and name != "":
                specialty = specialty_names.get(consultant_type, consultant_type.title())
                table += f"| {specialty} | {name} | {company or 'N/A'} | {contact or 'N/A'} |\n"
        
        table += "\n"
        return table
        
    except Exception as e:
        return f"\n<!-- Error generating consultants table: {e} -->\n"


def generate_authors_table(document_type: str = "report", language: str = None) -> str:
    """
    Generate authors information table from project configuration.
    
    Args:
        document_type: Type of document to determine author source
        language: Language code ('en', 'es'). If None, auto-detects from config.
        
    Returns:
        Formatted markdown table with authors information
    """
    try:
        from ._config import ModularConfigLoader
        from pathlib import Path
        
        # Detect language if not provided
        if language is None:
            language = detect_language_from_config()
        
        # Load authors directly from the top-level config
        config_loader = ModularConfigLoader()
        full_config = config_loader.load_project()
        
        authors = full_config.get('authors', [])
        
        if not authors:
            return f"\n<!-- No {get_translation('authors', language).lower()} available -->\n"
        
        table = f"\n## {get_translation('authors', language)}\n\n"
        
        # Add responsive table wrapper
        table += ':::{.table-responsive}\n\n'
        table += f"| {get_translation('name', language)} | {get_translation('role', language)} | {get_translation('affiliation', language)} | {get_translation('contact', language)} |\n"
        table += "|:-------------|:------------------|:----------------------|:------------------------|\n"
        
        for author in authors:
            name = author.get('name', '')
            roles = ', '.join(author.get('role', [])) if author.get('role') else ''
            affiliations = ', '.join(author.get('affiliation', [])) if author.get('affiliation') else ''
            contacts = ', '.join(author.get('contact', [])) if author.get('contact') else ''
            
            # Handle long content by using appropriate lengths for each column
            def format_cell_content(content, max_length=25):
                if len(content) > max_length:
                    return content[:max_length-3] + '...'
                return content
            
            if name and name != "":  # Only add row if name exists
                formatted_name = format_cell_content(name, 20)  # Allow more space for names
                formatted_roles = format_cell_content(roles, 35) if roles else 'N/A'  # More space for roles
                formatted_affiliations = format_cell_content(affiliations, 30) if affiliations else 'N/A'  # Adequate for affiliations
                formatted_contacts = contacts if contacts else 'N/A'  # Don't truncate emails
                
                table += f"| {formatted_name} | {formatted_roles} | {formatted_affiliations} | {formatted_contacts} |\n"
        
        table += '\n:::\n'
        
        table += "\n"
        return table
        
    except Exception as e:
        return f"\n<!-- Error generating authors table: {e} -->\n"


def generate_project_info(info_type: str = "project", document_type: str = "report", language: str = None) -> str:
    """
    Generate project information table based on type.
    
    Args:
        info_type: Type of information (project, client, team, consultants, authors)
        document_type: Document type for author routing
        language: Language code ('en', 'es'). If None, auto-detects from config.
        
    Returns:
        Formatted markdown table
    """
    if info_type == "project":
        return generate_project_info_table(language)
    elif info_type == "client":
        return generate_client_table(language)
    elif info_type == "team":
        return generate_team_table(language)
    elif info_type == "consultants":
        return generate_consultants_table(language)
    elif info_type == "authors":
        return generate_authors_table(document_type, language)
    else:
        return f"\n<!-- Unknown info_type: {info_type}. Valid options: project, client, team, consultants, authors -->\n"


def generate_copyright_footer() -> str:
    """
    Generate copyright footer from project configuration.
    
    Returns:
        Copyright footer text
    """
    try:
        from ._config import ModularConfigLoader
        from pathlib import Path
        
        # Create config loader directly
        config_loader = ModularConfigLoader()
        config = config_loader.load_project()
        
        copyright_info = config.get('copyright', {})
        
        if not copyright_info:
            return "\n---\n\n*Este documento tiene validez únicamente en su forma íntegra y original; no se permite la reproducción parcial sin autorización previa.*\n"
        
        name = copyright_info.get('name', 'N/A')
        year = copyright_info.get('year', 2025)
        text = copyright_info.get('text', 'All rights reserved.')
        
        footer = "\n---\n\n"
        footer += f"Este documento tiene validez únicamente en su forma íntegra y original; "
        footer += f"no se permite la reproducción parcial sin la autorización previa de "
        footer += f"**{name}** © {year}. {text}\n"
        
        return footer
        
    except Exception as e:
        return f"\n---\n\n*Error generating copyright footer: {e}*\n"


def get_project_metadata(document_type: str = 'paper') -> Dict[str, Any]:
    """
    Extract metadata from project configuration.
    
    Args:
        document_type (str): Type of document ('paper', 'book', 'report', 'notebook')
                            - paper/book: uses authors (supports multiple roles/affiliations)
                            - report: uses consultants 
                            - notebook: uses team
    
    Returns:
        Dict with project metadata (title, author, subtitle, date, etc.)
    """
    try:
        # Get the full project file content, not just the 'project' section
        from ePy_docs.core._config import ModularConfigLoader
        from pathlib import Path
        
        # Try to get the config loader that was set during initialization
        try:
            from ePy_docs.core._config import get_config_loader
            config_loader = get_config_loader()
            if config_loader:
                full_config = config_loader.load_project()
            else:
                # Fallback: load empty config
                config_loader = ModularConfigLoader()
                full_config = config_loader.load_project()
        except:
            # Final fallback
            config_loader = ModularConfigLoader()
            full_config = config_loader.load_project()
        
        metadata = {}
        
        # Title from project name or document name
        if 'project' in full_config and 'name' in full_config['project']:
            metadata['title'] = full_config['project']['name']
        elif 'metadata' in full_config and 'document_name' in full_config['metadata']:
            metadata['title'] = full_config['metadata']['document_name'].replace('_', ' ')
        
        # Subtitle from project description
        if 'project' in full_config and 'description' in full_config['project']:
            metadata['subtitle'] = full_config['project']['description']
        
        # Author selection based on document type
        author_list = []
        
        if document_type in ['paper', 'book']:
            # For papers and books: use authors with flexible structure
            if 'authors' in full_config and full_config['authors']:
                authors = full_config['authors']
                for author in authors:
                    if 'name' in author:
                        # Use rich format if roles/affiliations available, otherwise just name
                        if author.get('role') or author.get('affiliation'):
                            formatted_author = format_author_info(author)
                            author_list.append(formatted_author)
                        else:
                            author_list.append(author['name'])
        
        elif document_type == 'report':
            # For reports: use consultants
            if 'project' in full_config and 'consultants' in full_config['project']:
                consultants = full_config['project']['consultants']
                for consultant_type, consultant_info in consultants.items():
                    if 'name' in consultant_info:
                        author_list.append(consultant_info['name'])
        
        elif document_type == 'notebook':
            # For notebooks: use team
            if 'project' in full_config and 'team' in full_config['project']:
                team = full_config['project']['team']
                
                # Add lead engineer and project manager
                if 'lead_engineer' in team and 'name' in team['lead_engineer']:
                    author_list.append(team['lead_engineer']['name'])
                if 'project_manager' in team and 'name' in team['project_manager']:
                    author_list.append(team['project_manager']['name'])
                
                # Add designers
                if 'designers' in team:
                    for member in team['designers']:
                        if 'name' in member:
                            author_list.append(member['name'])
        
        # Set author metadata
        if author_list:
            if len(author_list) == 1:
                metadata['author'] = author_list[0]
            else:
                metadata['author'] = author_list
        
        # Date from project creation date or current date
        if 'project' in full_config and 'created_date' in full_config['project']:
            metadata['date'] = full_config['project']['created_date']
        else:
            from datetime import datetime
            metadata['date'] = datetime.now().strftime("%Y-%m-%d")
        
        # Additional metadata
        if 'metadata' in full_config:
            meta = full_config['metadata']
            if 'document_version' in meta:
                metadata['version'] = meta['document_version']
            if 'revision' in meta:
                metadata['revision'] = meta['revision']
            if 'confidentiality' in meta:
                metadata['confidentiality'] = meta['confidentiality']
        
        return metadata
        
    except Exception as e:
        # Fallback to empty metadata if project config is not available
        print(f"Warning: Could not load project metadata: {e}")
        return {}


# =============================================================================
# QUARTO YAML GENERATION
# =============================================================================

def _get_authors_for_yaml() -> Optional[Union[str, List[Dict[str, str]]]]:
    """
    Get authors from DocumentWriter instance in call stack for YAML metadata.
    
    Returns:
        - String with single author name if only one author
        - List of author dictionaries for multiple authors
        - None if no authors found
    """
    # Look for DocumentWriter instance in call stack
    for frame_info in inspect.stack():
        frame_locals = frame_info.frame.f_locals
        for name, obj in frame_locals.items():
            if hasattr(obj, '_authors') and obj._authors:
                authors = obj._authors
                
                if len(authors) == 1:
                    # Single author - return just the name as string
                    return authors[0].get('name', 'Anonymous')
                else:
                    # Multiple authors - return list of dictionaries
                    author_list = []
                    for author in authors:
                        author_dict = {'name': author.get('name', 'Anonymous')}
                        
                        # Add affiliation if available
                        if author.get('affiliation'):
                            affiliations = author['affiliation']
                            if isinstance(affiliations, list) and affiliations:
                                author_dict['affiliation'] = affiliations[0]  # Use first affiliation
                            elif isinstance(affiliations, str):
                                author_dict['affiliation'] = affiliations
                        
                        # Add email if available
                        if author.get('contact'):
                            contacts = author['contact']
                            if isinstance(contacts, list) and contacts:
                                # Look for email in contacts
                                for contact in contacts:
                                    if '@' in str(contact):
                                        author_dict['email'] = contact
                                        break
                            elif isinstance(contacts, str) and '@' in contacts:
                                author_dict['email'] = contacts
                        
                        author_list.append(author_dict)
                    
                    return author_list
    
    return None


def generate_quarto_yaml(
    title: str,
    layout_name: str = 'classic',
    document_type: str = 'article',
    output_formats: List[str] = None,
    fonts_dir: Path = None,
    language: str = 'en',
    author: str = None,
    subtitle: str = None,
    date: str = None,
    bibliography_path: str = None,
    csl_path: str = None,
    crossref_chapters: bool = None,
    crossref_fig_labels: str = 'arabic',
    crossref_tbl_labels: str = 'arabic',
    crossref_eq_labels: str = 'arabic',
    echo: bool = False,
    warning: bool = False,
    message: bool = False
) -> Dict[str, Any]:
    """
    Generate complete Quarto YAML frontmatter.
    
    Args:
        title: Document title
        layout_name: Layout name ('classic', 'modern', 'handwritten', etc.)
        document_type: Document type ('article', 'report', 'book')
        output_formats: List of output formats ('pdf', 'html', 'tex', 'docx')
        fonts_dir: Absolute path to fonts directory (for PDF font loading)
        language: Document language ('en', 'es', 'fr', etc.)
        author: Document author
        subtitle: Document subtitle
        date: Document date
        bibliography_path: Path to bibliography file (.bib)
        csl_path: Path to CSL style file (.csl)
        crossref_chapters: Enable chapter numbering (None = auto-detect from document_type)
        crossref_fig_labels: Figure label format
        crossref_tbl_labels: Table label format
        crossref_eq_labels: Equation label format
        echo: Show code in output
        warning: Show warnings in output
        message: Show messages in output
        
    Returns:
        Dictionary with Quarto YAML configuration
    """
    if output_formats is None:
        output_formats = ['pdf', 'html']
        
    from ePy_docs.core._pdf import get_pdf_config
    from ePy_docs.core._html import get_html_config
    from ePy_docs.core._config import get_document_type_config
    
    # Load document type configuration
    try:
        doc_type_config = get_document_type_config(document_type)
    except ValueError:
        doc_type_config = {}
    
    # Base metadata
    yaml_config = {
        'title': title,
        'author': _get_authors_for_yaml() or author or 'Anonymous',
        'lang': language,
    }
    
    # Optional metadata
    if subtitle:
        yaml_config['subtitle'] = subtitle
    if date:
        yaml_config['date'] = date
    
    # Format configuration (build formats first, then apply document_type overrides)
    format_config = {}
    
    # PDF configuration
    if 'pdf' in output_formats:
        pdf_config = get_pdf_config(
            layout_name=layout_name,
            document_type=document_type,
            fonts_dir=fonts_dir
        )
        
        # PRIORITY ORDER: PDF Config (from get_pdf_config) < Layout Common < Document Type PDF
        # Include common settings from quarto.epyson for PDF
        from ePy_docs.core._config import get_config_section
        quarto_config = get_config_section('quarto')
        if layout_name in quarto_config:
            layout_quarto = quarto_config[layout_name]
            if 'common' in layout_quarto:
                # Include all common settings for PDF format
                for key, value in layout_quarto['common'].items():
                    quarto_key = key.replace('_', '-')
                    pdf_config[quarto_key] = value
        
        # Apply quarto_common from document_type to PDF (before quarto_pdf specifics)
        if 'quarto_common' in doc_type_config:
            for key, value in doc_type_config['quarto_common'].items():
                quarto_key = key.replace('_', '-')
                pdf_config[quarto_key] = value
        
        # OVERRIDE with quarto_pdf from document_type (HIGHEST PRIORITY)
        # This ensures document-specific settings like fontsize are respected
        if 'quarto_pdf' in doc_type_config:
            for key, value in doc_type_config['quarto_pdf'].items():
                quarto_key = key.replace('_', '-')
                pdf_config[quarto_key] = value
        
        # Add title page configuration
        documentclass = doc_type_config.get('documentclass', 'article')
        if doc_type_config.get('title_page', False):
            # For book/report: use native titlepage
            if documentclass in ['book', 'report']:
                pdf_config['titlepage'] = True
            # For article with title page (notebook): add titling package and newpage after title
            elif documentclass == 'article':
                # Add titling package to header for better title page formatting
                if 'include-in-header' in pdf_config and 'text' in pdf_config['include-in-header']:
                    pdf_config['include-in-header']['text'] += '\n\n\\usepackage{titling}\n\\pretitle{\\begin{center}\\LARGE}\n\\posttitle{\\par\\end{center}\\vskip 0.5em}\n\\preauthor{\\begin{center}\\large \\lineskip 0.5em\\begin{tabular}[t]{c}}\n\\postauthor{\\end{tabular}\\par\\end{center}}\n\\predate{\\begin{center}\\large}\n\\postdate{\\par\\end{center}}'
                # Quarto already generates title page from YAML metadata, just add newpage after it
                pdf_config['include-before-body'] = {'text': '\\newpage'}
        else:
            # For paper (no separate title page)
            pdf_config['titlepage'] = False
        
        format_config['pdf'] = pdf_config
    
    if 'html' in output_formats:
        html_config = get_html_config(
            layout_name=layout_name,
            document_type=document_type
        )
        
        # PRIORITY ORDER: Base < Layout Common < Document Type HTML
        # Step 1: Include common settings from quarto.epyson (layout) as baseline
        from ePy_docs.core._config import get_config_section
        quarto_config = get_config_section('quarto')
        if layout_name in quarto_config:
            layout_quarto = quarto_config[layout_name]
            if 'common' in layout_quarto:
                # Include all common settings for HTML format
                for key, value in layout_quarto['common'].items():
                    quarto_key = key.replace('_', '-')
                    html_config[quarto_key] = value
        
        # Step 2: Apply quarto_common from document_type to HTML
        if 'quarto_common' in doc_type_config:
            for key, value in doc_type_config['quarto_common'].items():
                quarto_key = key.replace('_', '-')
                html_config[quarto_key] = value
        
        # Step 3: OVERRIDE with quarto_html from document_type (HIGHEST PRIORITY)
        # This ensures document-specific settings like page-layout, title-block-banner
        # take precedence over layout defaults
        if 'quarto_html' in doc_type_config:
            for key, value in doc_type_config['quarto_html'].items():
                quarto_key = key.replace('_', '-')
                html_config[quarto_key] = value
        format_config['html'] = html_config
    
    if 'docx' in output_formats:
        from ePy_docs.core._config import get_config_section
        from pathlib import Path
        
        # Get the DOCX configuration from quarto.epyson
        quarto_config = get_config_section('quarto')
        docx_config = {}
        
        # PRIORITY ORDER: Layout Common (safe keys) < Layout DOCX Reference < Document Type DOCX
        # Include safe common settings (structural, non-visual)
        safe_common_keys = {
            'fig-cap-location', 'tbl-cap-location',  # Caption positions (structural)
            'fig-width', 'fig-height',  # Figure dimensions
            # Exclude: number-sections, fig-align, colorlinks (should come from template or document_type)
        }
        
        if layout_name in quarto_config:
            layout_quarto = quarto_config[layout_name]
            
            # Get only safe common settings from layout
            if 'common' in layout_quarto:
                for key, value in layout_quarto['common'].items():
                    if key in safe_common_keys:
                        docx_config[key] = value
            
            # Get DOCX-specific settings (mainly reference-doc)
            if 'docx_reference' in layout_quarto:
                # Get reference template path
                relative_template = layout_quarto['docx_reference']
                
                # Resolve template path to absolute BEFORE adding to config
                import ePy_docs
                package_dir = Path(ePy_docs.__file__).parent
                docx_config['reference-doc'] = str(package_dir / 'config' / relative_template)
        
        # OVERRIDE with quarto_docx from document_type (HIGHEST PRIORITY)
        if 'quarto_docx' in doc_type_config:
            for key, value in doc_type_config['quarto_docx'].items():
                quarto_key = key.replace('_', '-')
                docx_config[quarto_key] = value
        
        # Apply quarto_common from document_type to DOCX
        if 'quarto_common' in doc_type_config:
            for key, value in doc_type_config['quarto_common'].items():
                quarto_key = key.replace('_', '-')
                docx_config[quarto_key] = value
        
        format_config['docx'] = docx_config
    
    yaml_config['format'] = format_config
    
    # No need to convert backslashes since they're just filenames now
    if bibliography_path:
        yaml_config['bibliography'] = bibliography_path
    if csl_path:
        yaml_config['csl'] = csl_path
    
    # Crossref configuration
    # Use crossref from document_type config if available, otherwise use defaults
    if 'crossref' in doc_type_config:
        yaml_config['crossref'] = doc_type_config['crossref'].copy()
        # Allow parameter overrides
        if crossref_chapters is not None:
            yaml_config['crossref']['chapters'] = crossref_chapters
        if crossref_fig_labels:
            yaml_config['crossref']['fig-labels'] = crossref_fig_labels
        if crossref_tbl_labels:
            yaml_config['crossref']['tbl-labels'] = crossref_tbl_labels
        if crossref_eq_labels:
            yaml_config['crossref']['eq-labels'] = crossref_eq_labels
    else:
        # Fallback to old behavior
        if crossref_chapters is None:
            chapters_enabled = True if document_type != 'report' else False
        else:
            chapters_enabled = crossref_chapters
        
        yaml_config['crossref'] = {
            'chapters': chapters_enabled,
            'fig-labels': crossref_fig_labels,
            'tbl-labels': crossref_tbl_labels,
            'eq-labels': crossref_eq_labels,
        }
    
    # Code execution settings
    # Use execution from document_type config if available (has priority)
    if 'execution' in doc_type_config:
        yaml_config['execute'] = doc_type_config['execution'].copy()
        # Note: doc_type_config values take precedence over function parameters
        # This ensures document-specific settings (like notebook's echo=true) are respected
    else:
        # Fallback to parameters only if doc_type has no execution config
        yaml_config['execute'] = {
            'echo': echo,
            'warning': warning,
            'message': message,
        }
    
    return yaml_config


# =============================================================================
# QMD FILE CREATION
# =============================================================================

def _fix_image_paths_to_absolute(content: str, base_dir: Path) -> str:
    """
    Convert relative image paths to absolute paths for LaTeX compilation.
    
    LuaLaTeX runs from a temporary directory, so relative paths don't work.
    This function converts all relative image paths to absolute paths.
    
    Args:
        content: Markdown content with image references
        base_dir: Base directory to resolve relative paths from
        
    Returns:
        Content with absolute image paths
    """
    import re
    from pathlib import Path
    
    # Pattern to match markdown images: ![alt](path)
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    
    def replace_path(match):
        alt_text = match.group(1)
        img_path = match.group(2)
        
        # Skip URLs
        if img_path.startswith(('http://', 'https://')):
            return match.group(0)
        
        # Skip data URLs or other special formats (but not Windows paths)
        if ':' in img_path:
            # Check if it's a Windows path (drive letter followed by colon)
            if not (len(img_path) > 1 and img_path[1] == ':'):
                return match.group(0)
        
        # If path is already absolute (Windows or Unix), just fix slashes
        if img_path.startswith('/') or (len(img_path) > 1 and img_path[1] == ':'):
            # Convert backslashes to forward slashes for LaTeX
            abs_path_str = img_path.replace('\\', '/')
            return f'![{alt_text}]({abs_path_str})'
        
        # Convert relative path to absolute
        candidate_path = (base_dir / img_path).resolve()
        
        # If the path doesn't exist, try going up directories to find the root
        if not candidate_path.exists():
            parent_candidate = (base_dir.parent / img_path).resolve()
            if parent_candidate.exists():
                candidate_path = parent_candidate
            else:
                grandparent_candidate = (base_dir.parent.parent / img_path).resolve()
                if grandparent_candidate.exists():
                    candidate_path = grandparent_candidate
                else:
                    candidate_path = (base_dir / img_path).resolve()
        
        # Convert to forward slashes for LaTeX compatibility
        abs_path_str = str(candidate_path).replace('\\', '/')
        
        return f'![{alt_text}]({abs_path_str})'
    
    # Replace all image paths
    fixed_content = re.sub(image_pattern, replace_path, content)
    
    return fixed_content


def create_qmd_file(
    output_path: Path,
    content: str,
    yaml_config: Dict[str, Any],
    fix_image_paths: bool = False,
    layout_name: str = 'classic',
    document_type: str = 'article'
) -> Path:
    """
    Create QMD file with YAML frontmatter and content.
    
    Also generates the styles.css file for HTML rendering with the correct layout.
    
    Args:
        output_path: Path to save QMD file
        content: Markdown content body
        yaml_config: YAML frontmatter configuration
        fix_image_paths: Convert relative image paths to absolute (default: True)
        layout_name: Layout name for CSS generation
        document_type: Document type (report, paper, book, etc.)
        
    Returns:
        Path to created QMD file
    """
    import shutil
    
    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Copy custom fonts to output directory if needed for PDF
    # Returns absolute path to fonts directory
    fonts_dir = _copy_layout_fonts_to_output(layout_name, output_path.parent)
    
    # Update PDF config with fonts directory path if needed
    if 'format' in yaml_config and 'pdf' in yaml_config['format']:
        if fonts_dir and 'include-in-header' in yaml_config['format']['pdf']:
            # The fonts directory path is already embedded in the header during generation
            # No need to regenerate the entire config
            pass
    
    # Fix image paths to absolute if requested
    if fix_image_paths:
        # Use the directory where the QMD will be saved as base
        base_dir = output_path.parent
        content = _fix_image_paths_to_absolute(content, base_dir)
    
    # Generate and save CSS file for HTML rendering
    from ePy_docs.core._html import generate_css
    css_content = generate_css(layout_name=layout_name)
    css_path = output_path.parent / 'styles.css'
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    # Generate YAML frontmatter
    yaml_str = yaml.dump(yaml_config, default_flow_style=False, sort_keys=False)
    
    # Combine YAML and content
    qmd_content = f'''---
{yaml_str}---

{content}
'''
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(qmd_content)
    
    return output_path


def _copy_layout_fonts_to_output(layout_name: str, output_dir: Path) -> Path:
    """Copy custom fonts required by layout to output directory for PDF rendering.
    
    Returns:
        Path to fonts directory (absolute path)
    """
    import shutil
    from ePy_docs.core._config import get_loader
    
    fonts_dir = output_dir / 'fonts'
    
    try:
        loader = get_loader()
        layout = loader.load_layout(layout_name)
        font_family = layout.get('font_family')
        
        if not font_family:
            return fonts_dir
        
        # Get fonts config from embedded font_families
        font_families = layout.get('font_families', {})
        fonts_font_config = font_families.get(font_family, {})
        
        primary_font = fonts_font_config.get('primary', '')
        # Use default font file template since text.epyson is deprecated
        font_file_template = '{font_name}.otf'
        
        if primary_font:
            # Find source font file
            font_filename = font_file_template.format(font_name=primary_font)
            package_root = Path(__file__).parent.parent
            source_font = package_root / 'config' / 'assets' / 'fonts' / font_filename
            
            if source_font.exists():
                # Create fonts subdirectory in output
                fonts_dir.mkdir(exist_ok=True)
                
                # Copy font file
                dest_font = fonts_dir / font_filename
                shutil.copy2(source_font, dest_font)
                
    except Exception:
        # Don't fail if font copy fails
        pass
    
    return fonts_dir


def _copy_bibliography_files_to_output(
    bibliography_path: Optional[str],
    csl_path: Optional[str],
    output_dir: Path
) -> Tuple[Optional[str], Optional[str]]:
    """Copy bibliography and CSL files to output directory for Quarto rendering.
    
    Quarto expects these files to be in the same directory as the .qmd file or
    in a relative path accessible from that directory. This function copies the
    files and returns the relative paths to use in the YAML configuration.
    
    Args:
        bibliography_path: Path to bibliography file (.bib) - can be absolute or None
        csl_path: Path to CSL style file (.csl) - can be absolute or None
        output_dir: Output directory where .qmd file will be saved
        
    Returns:
        Tuple of (bibliography_relative_path, csl_relative_path)
        Returns None for paths that weren't provided or couldn't be copied
    """
    import shutil
    from pathlib import Path
    
    bib_relative = None
    csl_relative = None
    
    # Copy bibliography file if provided
    if bibliography_path:
        try:
            source_bib = Path(bibliography_path)
            if source_bib.exists():
                # Copy to output directory with same filename
                dest_bib = output_dir / source_bib.name
                shutil.copy2(source_bib, dest_bib)
                # Return just the filename (relative to .qmd location)
                bib_relative = source_bib.name
        except Exception as e:
            print(f"Warning: Failed to copy bibliography file: {e}")
    
    # Copy CSL file if provided
    if csl_path:
        try:
            source_csl = Path(csl_path)
            if source_csl.exists():
                # Copy to output directory with same filename
                dest_csl = output_dir / source_csl.name
                shutil.copy2(source_csl, dest_csl)
                # Return just the filename (relative to .qmd location)
                csl_relative = source_csl.name
        except Exception as e:
            print(f"Warning: Failed to copy CSL file: {e}")
    
    return bib_relative, csl_relative


# =============================================================================
# QUARTO RENDERING
# =============================================================================

def render_qmd(
    qmd_path: Path,
    output_format: Optional[str] = None,
    output_dir: Optional[Path] = None
) -> Path:
    """
    Render QMD file using Quarto.
    
    Args:
        qmd_path: Path to QMD file
        output_format: Specific format to render ('pdf', 'html', or None for all)
        output_dir: Output directory (optional)
        
    Returns:
        Path to output file
        
    Raises:
        RuntimeError: If Quarto rendering fails
    """
    if not qmd_path.exists():
        raise FileNotFoundError(f"QMD file not found: {qmd_path}")
    
    # Build Quarto command
    cmd = ['quarto', 'render', str(qmd_path)]
    
    if output_format:
        cmd.extend(['--to', output_format])
        
        # For HTML, specify output filename to match the QMD base name
        if output_format == 'html':
            html_filename = qmd_path.with_suffix('.html').name
            cmd.extend(['--output', html_filename])
    
    if output_dir:
        cmd.extend(['--output-dir', str(output_dir)])
    
    # Execute Quarto
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=qmd_path.parent
        )
        
        # Determine output file path
        if output_format == 'pdf':
            output_file = qmd_path.with_suffix('.pdf')
        elif output_format == 'html':
            output_file = qmd_path.with_suffix('.html')
        elif output_format == 'docx':
            output_file = qmd_path.with_suffix('.docx')
        else:
            output_file = qmd_path.parent
        
        return output_file
        
    except subprocess.CalledProcessError as e:
        error_msg = f"Quarto rendering failed:\n{e.stderr}"
        raise RuntimeError(error_msg) from e


def render_to_pdf(qmd_path: Path) -> Path:
    """Render QMD to PDF."""
    return render_qmd(qmd_path, output_format='pdf')


def render_to_html(qmd_path: Path) -> Path:
    """Render QMD to HTML."""
    return render_qmd(qmd_path, output_format='html')


# =============================================================================
# COMPLETE WORKFLOW
# =============================================================================

def create_and_render(
    output_path: Path,
    content: str,
    title: str,
    layout_name: str = 'classic',
    document_type: str = 'article',
    output_formats: List[str] = None,
    language: str = 'en',
    bibliography_path: str = None,
    csl_path: str = None
) -> Dict[str, Path]:
    """
    Complete workflow: create QMD and render to specified formats.
    
    Args:
        output_path: Path to save QMD file
        content: Markdown content
        title: Document title
        layout_name: Layout name
        document_type: Document type
        output_formats: List of formats to generate ('pdf', 'html', 'tex', 'docx', 'markdown')
        language: Document language
        bibliography_path: Path to bibliography file (.bib) - will be copied to output directory
        csl_path: Path to CSL style file (.csl) - will be copied to output directory
        
    Returns:
        Dictionary mapping format names to output file paths
    """
    if output_formats is None:
        output_formats = ['pdf', 'html']
    
    # If no bibliography/CSL paths provided, use default assets
    if bibliography_path is None or csl_path is None:
        package_root = Path(__file__).parent.parent  # ePy_docs root directory
        assets_bib_dir = package_root / 'config' / 'assets' / 'bibliography'
        
        # Use default bibliography if not provided
        if bibliography_path is None:
            default_bib = assets_bib_dir / 'references.bib'
            if default_bib.exists():
                bibliography_path = str(default_bib)
        
        # Use default CSL (APA style) if not provided  
        if csl_path is None:
            default_csl = assets_bib_dir / 'ieee.csl'
            if default_csl.exists():
                csl_path = str(default_csl)
    
    # Copy bibliography and CSL files to output directory (same location as .qmd)
    # This ensures Quarto can find them during rendering
    output_dir = output_path.parent
    bib_relative, csl_relative = _copy_bibliography_files_to_output(
        bibliography_path, csl_path, output_dir
    )
    
    # Get project metadata based on document type
    project_metadata = get_project_metadata(document_type)
    
    # Use project metadata if available, otherwise use provided title
    final_title = project_metadata.get('title', title)
    final_author = project_metadata.get('author')
    final_subtitle = project_metadata.get('subtitle')
    final_date = project_metadata.get('date')
    
    # Generate YAML configuration with project metadata and relative paths
    yaml_config = generate_quarto_yaml(
        title=final_title,
        author=final_author,
        subtitle=final_subtitle,
        date=final_date,
        layout_name=layout_name,
        document_type=document_type,
        output_formats=output_formats,
        language=language,
        bibliography_path=bib_relative,  # Use relative path (just filename)
        csl_path=csl_relative           # Use relative path (just filename)
    )
    
    # Create QMD file with CSS generation
    # Don't fix image paths since our tables already generate correct relative paths
    qmd_path = create_qmd_file(output_path, content, yaml_config, fix_image_paths=False, 
                               layout_name=layout_name, document_type=document_type)
    
    # Render to each format with progress bar
    results = {'qmd': qmd_path}
    
    # Generate formats without progress bar
    format_iterator = output_formats
    print(f"Generando {len(output_formats)} formato(s)...")
    
    for i, fmt in enumerate(format_iterator):
        print(f"  [{i+1}/{len(output_formats)}] Generando {fmt.upper()}...")
        
        try:
            output_file = render_qmd(qmd_path, output_format=fmt)
            results[fmt] = output_file
            print(f"      ✅ {fmt.upper()} generado")
        except Exception as e:
            error_msg = str(e)
            
            # Check if error is just Chrome warnings but file was actually created
            expected_output = qmd_path.with_suffix(f'.{fmt}')
            if expected_output.exists():
                # File was created successfully despite warnings
                results[fmt] = expected_output
                print(f"      ✅ {fmt.upper()} generado (con advertencias)")
            else:
                # Actual failure
                print(f"      ❌ Error generando {fmt.upper()}")
                if fmt in ['pdf', 'docx']:
                    print(f"         Detalles: {error_msg[:100]}...")
                    if 'chromium' in error_msg.lower() or 'chrome' in error_msg.lower():
                        print("         💡 Puede requerir Chromium: quarto install tool chromium")
                results[fmt] = None
    
    # Generation completed
    
    return results


# =============================================================================
# UTILITIES
# =============================================================================

def check_quarto_installed() -> bool:
    """
    Check if Quarto is installed and available.
    
    Returns:
        True if Quarto is installed, False otherwise
    """
    try:
        result = subprocess.run(
            ['quarto', '--version'],
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def get_quarto_version() -> str:
    """
    Get installed Quarto version.
    
    Returns:
        Version string, or 'Not installed' if Quarto not found
    """
    try:
        result = subprocess.run(
            ['quarto', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "Not installed"


def check_pdf_rendering_capability() -> Dict[str, bool]:
    """
    Check what PDF rendering tools are available.
    
    Returns:
        Dictionary with availability status for different PDF engines
    """
    capabilities = {
        'chromium': False,
        'tinytex': False,
        'system_latex': False
    }
    
    try:
        # Check for Chromium (used by Quarto for HTML->PDF)
        result = subprocess.run(
            ['quarto', 'check', 'tools'],
            capture_output=True,
            text=True,
            check=False
        )
        output = result.stdout.lower()
        capabilities['chromium'] = 'chromium' in output and 'ok' in output
        capabilities['tinytex'] = 'tinytex' in output and 'ok' in output
        
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    
    # Check for system LaTeX
    try:
        result = subprocess.run(['pdflatex', '--version'], capture_output=True, check=False)
        capabilities['system_latex'] = result.returncode == 0
    except FileNotFoundError:
        try:
            result = subprocess.run(['lualatex', '--version'], capture_output=True, check=False)
            capabilities['system_latex'] = result.returncode == 0
        except FileNotFoundError:
            pass
    
    return capabilities


def diagnose_pdf_issues() -> str:
    """
    Diagnose PDF rendering issues and provide solutions.
    
    Returns:
        Diagnostic message with recommended solutions
    """
    if not check_quarto_installed():
        return ("❌ Quarto not installed.\n"
                "💡 Install from: https://quarto.org/docs/get-started/")
    
    capabilities = check_pdf_rendering_capability()
    
    issues = []
    solutions = []
    
    if not capabilities['chromium']:
        issues.append("❌ Chromium not available for HTML->PDF conversion")
        solutions.append("   • Install Chromium: quarto install tool chromium")
    
    if not capabilities['tinytex'] and not capabilities['system_latex']:
        issues.append("❌ No LaTeX distribution found")
        solutions.append("   • Install TinyTeX: quarto install tool tinytex")
        solutions.append("   • Or install full LaTeX: MiKTeX (Windows) or TeX Live")
    
    if not issues:
        return "✅ PDF rendering tools appear to be configured correctly."
    
    diagnostic = "🔍 PDF Rendering Issues Detected:\n"
    diagnostic += "\n".join(issues)
    diagnostic += "\n\n💡 Recommended Solutions:\n"
    diagnostic += "\n".join(solutions)
    diagnostic += "\n\n🔗 More help: https://quarto.org/docs/output-formats/pdf.html"
    
    return diagnostic


# =============================================================================
# QUARTO FILE PROCESSING FOR WRITER
# =============================================================================
def _is_table_start(line: str, lines: list, index: int) -> bool:
    """Check if current line starts a markdown table.
    
    Skip if within 5 lines there's a Quarto directive (#|) as these are
    table metadata blocks that should be associated with the table.
    """
    # Check if there's a #| block within the previous 5 lines
    # If so, this could be a new table with metadata
    for lookback in range(1, min(6, index + 1)):
        if lines[index - lookback].strip().startswith('#|'):
            # Found metadata block - this IS a table start
            return ('|' in line and 
                    index + 1 < len(lines) and 
                    '|' in lines[index + 1])
    
    # No metadata block nearby, use normal detection
    return ('|' in line and 
            index + 1 < len(lines) and 
            '|' in lines[index + 1])


def _extract_table_content(lines: list, start_index: int) -> Tuple[List[str], Optional[str], int]:
    """Extract table lines and caption from markdown.
    
    Returns:
        Tuple of (table_lines, caption, next_index)
    """
    table_lines = [lines[start_index]]
    i = start_index + 1
    table_caption = None
    
    # Check for Quarto metadata block BEFORE the table
    caption_index = start_index - 1
    while caption_index >= 0 and caption_index >= start_index - 5:
        prev_line = lines[caption_index].strip()
        if prev_line.startswith('#| tbl-cap:'):
            # Extract caption from Quarto metadata
            table_caption = prev_line.replace('#| tbl-cap:', '').strip().strip('"')
            break
        elif prev_line.startswith('#|'):
            # Continue looking for caption in metadata block
            caption_index -= 1
        else:
            # Not in metadata block anymore
            break
    
    while i < len(lines):
        current_line = lines[i].strip()
        
        # Stop if we hit a new Quarto metadata block (start of next table)
        if current_line.startswith('#|'):
            break
        
        if '|' in lines[i]:
            table_lines.append(lines[i])
            i += 1
        elif current_line == '':
            # Empty line - check if table continues after it
            # If next non-empty line is not a table row, stop here
            peek_index = i + 1
            while peek_index < len(lines) and lines[peek_index].strip() == '':
                peek_index += 1
            
            if peek_index < len(lines):
                next_line = lines[peek_index].strip()
                # Stop if next content is metadata or not a table row
                if next_line.startswith('#|') or ('|' not in next_line):
                    break
            i += 1
        elif current_line.startswith(':') and table_caption is None:
            # Markdown table caption
            table_caption = current_line[1:].strip()
            i += 1  # Move past caption line
            break
        else:
            # End of table reached
            break
    
    return table_lines, table_caption, i


def _process_image_line(line: str, file_path: str, core, show_figure: bool = False) -> str:
    """Process a markdown image line, copy image to figures/ and update path.
    
    Args:
        line: Line containing image markdown
        file_path: Path to source file
        core: Writer instance
        show_figure: Whether to display image in Jupyter
        
    Returns:
        Updated markdown line with new image path in figures/ directory
    """
    import re
    import os
    import shutil
    from pathlib import Path
    
    # Match markdown image syntax: ![alt](path){#fig-id}
    # Capture alt text, path, and optional Quarto attributes
    match = re.match(r'!\[(.*?)\]\((.*?)\)(\{.*?\})?', line.strip())
    if not match:
        return line  # Not an image line, return unchanged
        
    alt_text = match.group(1)
    image_path = match.group(2)
    quarto_attrs = match.group(3) or ''  # Preserve {#fig-id} etc.
    
    # Skip HTTP/HTTPS URLs and absolute paths
    if image_path.startswith('http') or os.path.isabs(image_path):
        return line
    
    # Resolve relative path from source file location
    base_dir = Path(file_path).parent
    source_image = (base_dir / image_path).resolve()
    
    # Check if image exists
    if not source_image.exists():
        return line  # Image not found, return unchanged
    
    # Determine output directory (results/{document_type}/figures/)
    output_dir = Path(core.output_dir) / 'figures'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy image to figures/ with original filename
    dest_image = output_dir / source_image.name
    shutil.copy2(source_image, dest_image)
    
    # Update markdown line with new path
    new_path = f'figures/{source_image.name}'
    updated_line = f'![{alt_text}]({new_path}){quarto_attrs}'
    
    return updated_line


def _parse_markdown_table(table_lines: list) -> 'pd.DataFrame':
    """Parse markdown table lines into a pandas DataFrame.
    
    Args:
        table_lines: List of markdown table lines
        
    Returns:
        DataFrame if parsing succeeds, None otherwise
    """
    try:
        import pandas as pd
        
        # Filter out alignment rows and empty lines
        valid_rows = []
        for line in table_lines:
            line = line.strip()
            if not line:
                continue
            # Skip alignment rows (contain only |, -, :, spaces)  
            cleaned = line.replace('|', '').replace(' ', '').replace('\t', '')
            if cleaned and not all(c in '-:' for c in cleaned):
                valid_rows.append(line)
        
        if len(valid_rows) < 2:  # Need at least header + 1 data row
            return None
            
        # Parse rows into cells
        parsed_rows = []
        for row in valid_rows[:20]:  # Limit rows to prevent performance issues
            cells = [cell.strip() for cell in row.split('|')[1:-1]]
            if cells:
                parsed_rows.append(cells)
        
        if len(parsed_rows) < 2:
            return None
            
        # Create DataFrame
        header = parsed_rows[0]
        data_rows = parsed_rows[1:]
        
        # Normalize row lengths
        max_cols = len(header)
        for row in data_rows:
            # Pad short rows
            while len(row) < max_cols:
                row.append('')
            # Truncate long rows
            if len(row) > max_cols:
                row[:] = row[:max_cols]
        
        return pd.DataFrame(data_rows, columns=header)
        
    except Exception:
        return None


def process_quarto_file(
    file_path: str,
    include_yaml: bool = False,
    fix_image_paths: bool = True,
    convert_tables: bool = True,
    output_dir: str = None,
    figure_counter: int = 1,
    document_type: str = 'report',
    writer_instance = None,
    execute_code_blocks: bool = True,
    show_figure: bool = False
) -> None:
    """
    Process Quarto file and add to writer.
    
    Automatically processes:
    - Markdown tables: Converts to styled image tables
    - Images: Extracts caption from markdown and adds as figure
    - Text content: Preserves as-is
    - YAML frontmatter: Optionally included or stripped
    - Code blocks: Optionally executed if execute_code_blocks=True
    
    Args:
        file_path: Path to Quarto file
        include_yaml: Whether to include YAML frontmatter
        fix_image_paths: Whether to fix image paths
        convert_tables: Whether to convert tables to styled images
        output_dir: Output directory
        figure_counter: Current figure counter
        document_type: Document type
        writer_instance: DocumentWriter instance
        execute_code_blocks: Whether to execute code blocks (default True)
    """
    import re
    import os
    from pathlib import Path
    
    # Read file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip YAML if requested
    if not include_yaml and content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    
    if not writer_instance:
        return
    
    # NOTE: Preserve Quarto cross-references for proper rendering
    # Do NOT remove @fig-xxx, @tbl-xxx, @eq-xxx as they are essential for Quarto's cross-referencing
    # Quarto will handle these references and convert them to proper figure/table/equation numbers
    import re
    
    # NOTE: Preserve figure blocks with layout (e.g., ::: {#fig-xxx layout-ncol="2"} for subfigures)
    # These blocks are needed for Quarto to render multiple figures together
    # The images inside will be processed individually by _process_image_line
    # content = re.sub(r'::: \{[^}]*#fig-[^}]*\}.*?:::', '', content, flags=re.DOTALL)  # DISABLED
    
    # NOTE: Preserve Quarto attributes on images - they will be handled by _process_image_line
    # Do NOT remove {#fig-id} attributes from images as they're needed for cross-referencing
    # content = re.sub(r'!\[([^\]]*)\]\(([^)]*)\)\{#[\w-]+[^}]*\}', r'![\1](\2)', content)  # DISABLED
    content = re.sub(r'^\s*\{#[\w-]+[^}]*\}\s*$', '', content, flags=re.MULTILINE)  # Standalone ID lines
    
    # Detect if writer_instance is the wrapper or the core
    # If it has _core attribute, it's the wrapper; otherwise it's the core itself
    core = writer_instance._core if hasattr(writer_instance, '_core') else writer_instance
    
    # Add spacer before imported content
    core.content_buffer.append("\n\n")
    
    # Process content if conversion is enabled
    if convert_tables or fix_image_paths:
        # Split content into blocks (tables, images, text)
        lines = content.split('\n')
        i = 0
        current_block = []
        
        # Processing file
        print(f"Procesando {Path(file_path).name} ({len(lines)} líneas)...")
        
        while i < len(lines):
            line = lines[i]
            old_i = i  # Track starting position
            
            # Detect Quarto metadata block followed by table or image
            # This indicates start of a new element with metadata
            if line.strip().startswith('#|'):
                # Collect metadata lines
                metadata_lines = []
                metadata_start = i
                while i < len(lines) and lines[i].strip().startswith('#|'):
                    current_meta = lines[i].strip()
                    
                    # Handle inline metadata (multiple #| on same line)
                    # e.g., "#| label: tbl-x #| tbl-cap: 'caption'"
                    # Split into separate lines for Quarto compatibility
                    if current_meta.count('#|') > 1:
                        # Split by #| and process each part
                        parts = current_meta.split('#|')
                        for part in parts:
                            part = part.strip()
                            if part:  # Skip empty parts
                                metadata_lines.append('#| ' + part)
                    else:
                        metadata_lines.append(lines[i])
                    
                    i += 1
                
                # Skip empty lines after metadata
                empty_after_metadata = 0
                while i < len(lines) and lines[i].strip() == '':
                    empty_after_metadata += 1
                    i += 1
                
                # Now check if we're at a table
                if i < len(lines) and convert_tables and _is_table_start(lines[i], lines, i):
                    # Save any accumulated text
                    if current_block:
                        core.content_buffer.append('\n'.join(current_block) + '\n\n')
                        current_block = []
                    
                    # Extract caption and label from metadata
                    table_label = None
                    table_caption_from_meta = None
                    
                    for meta_line in metadata_lines:
                        if 'label:' in meta_line:
                            # Extract label: tbl-xxx
                            match = re.search(r'label:\s*(tbl-[\w-]+)', meta_line)
                            if match:
                                table_label = match.group(1)
                        if 'tbl-cap:' in meta_line:
                            # Extract caption from tbl-cap: "caption text"
                            match = re.search(r'tbl-cap:\s*["\']([^"\']*)["\']', meta_line)
                            if match:
                                table_caption_from_meta = match.group(1)
                    
                    # DON'T add metadata - we'll put caption in alt text instead
                    # This removes the metadata blocks completely
                    
                    # Extract table (will look back for caption in metadata)
                    table_lines, table_caption, i = _extract_table_content(lines, i)
                    
                    # Convert markdown table to DataFrame
                    df = _parse_markdown_table(table_lines)
                    if df is not None:
                        # Use caption from metadata if available, otherwise from table
                        final_caption = table_caption_from_meta or table_caption
                        core.add_table(df, title=final_caption, show_figure=show_figure)
                        
                        # If there's a Quarto label, update the table markdown ID
                        if table_label and core.content_buffer:
                            last_entry = core.content_buffer[-1]
                            # Replace #tbl-N with the Quarto label
                            updated_entry = re.sub(
                                r'\{[^}]*#tbl-\d+[^}]*\}',
                                lambda m: m.group(0).replace(re.search(r'#tbl-\d+', m.group(0)).group(0), f'#{table_label}'),
                                last_entry
                            )
                            core.content_buffer[-1] = updated_entry
                    else:
                        # Failed to parse - add as raw markdown WITH metadata (already added above)
                        current_block.extend(table_lines)
                    
                    # Update progress bar for all lines processed
                    
                    # Skip any trailing empty lines after table
                    while i < len(lines) and lines[i].strip() == '':
                        i += 1
                    
                    continue
                else:
                    # Metadata but no table following (or convert_tables=False)
                    # Preserve metadata for Quarto to process (could be for images, tables, etc.)
                    current_block.extend(metadata_lines)
                    # Add back the empty lines we consumed
                    current_block.extend([''] * empty_after_metadata)
                    continue
            
            # Detect Quarto div blocks (e.g., ::: {#fig-xxx layout-ncol="2"})
            # These are used for complex figure layouts with subfigures
            if line.strip().startswith(':::') and '{#' in line:
                # Find the closing :::
                block_lines = [line]
                i += 1
                
                while i < len(lines):
                    block_lines.append(lines[i])
                    if lines[i].strip() == ':::':
                        # Found closing tag
                        i += 1
                        break
                    i += 1
                
                # Process images within the block if fix_image_paths is enabled
                if fix_image_paths:
                    processed_block = []
                    for block_line in block_lines:
                        if block_line.strip().startswith('!['):
                            # Process image path
                            updated_line = _process_image_line(block_line, file_path, core, show_figure)
                            processed_block.append(updated_line)
                        else:
                            processed_block.append(block_line)
                    current_block.extend(processed_block)
                else:
                    current_block.extend(block_lines)
                
                continue
            
            # Detect markdown table (without metadata)
            if convert_tables and _is_table_start(line, lines, i):
                # Save any accumulated text
                if current_block:
                    core.content_buffer.append('\n'.join(current_block) + '\n\n')
                    current_block = []
                
                # Extract table content and caption
                table_lines, table_caption, i = _extract_table_content(lines, i)
                
                # Convert markdown table to DataFrame
                df = _parse_markdown_table(table_lines)
                if df is not None:
                    # Add table with proper caption
                    core.add_table(df, title=table_caption, show_figure=show_figure)
                    
                    # Update progress bar for all lines processed
                    continue
                else:
                    # Failed to parse - add as raw markdown
                    core.content_buffer.append('\n'.join(table_lines) + '\n\n')
                    
                    # Update progress bar for all lines processed
                    continue
            
            # Detect markdown image: ![alt](path)
            elif fix_image_paths and line.strip().startswith('!['):
                # Process image - update path and add to current block
                updated_line = _process_image_line(line, file_path, core, show_figure)
                current_block.append(updated_line)
            
            else:
                current_block.append(line)
            
            i += 1
            
            # Update progress bar (only if we didn't already update in a continue branch)
        
        # Ensure progress bar reaches 100%
        else:
            print(f"✓ Procesamiento completado")
        
        # Add remaining text
        if current_block:
            core.content_buffer.append('\n'.join(current_block))
    else:
        # No conversion, add raw content
        core.content_buffer.append(content)
    
    # Add trailing spacer for next content
    core.content_buffer.append("\n\n")


def prepare_generation(writer_instance, output_filename: str = None):
    """
    Prepare content for generation.
    
    Args:
        writer_instance: DocumentWriter instance
        output_filename: Optional output filename
        
    Returns:
        Tuple of (content, title)
        
    Raises:
        ValueError: If buffer is empty
    """
    # Get content from buffer (writers.py provides content_buffer directly)
    content = ''.join(writer_instance.content_buffer)
    
    # Validate content is not empty
    if not content or content.strip() == '':
        raise ValueError("Cannot generate document: buffer is empty. Add some content first.")
    
    # Add copyright footer automatically
    try:
        copyright_footer = generate_copyright_footer()
        content += copyright_footer
    except Exception as e:
        # If copyright footer fails, continue without it
        pass
    
    # Get title from config or use default
    title = output_filename or "Document"
    if title.endswith('.qmd'):
        title = title[:-4]
    
    return content, title

# ============================================================================
# COMPATIBILITY LAYER FOR TESTS
# ============================================================================

class QuartoOrchestrator:
    """Compatibility wrapper for tests that expect quarto_orchestrator singleton."""
    
    def generate_yaml_config(self, 
                            title: str,
                            layout_name: str = 'classic',
                            document_type: str = 'article',
                            output_formats = None,
                            language: str = 'en',
                            **kwargs):
        """Generate Quarto YAML configuration."""
        return generate_quarto_yaml(
            title=title,
            layout_name=layout_name,
            document_type=document_type,
            output_formats=output_formats,
            language=language,
            **kwargs
        )


# Singleton instance for tests
quarto_orchestrator = QuartoOrchestrator()
