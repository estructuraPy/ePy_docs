"""
Project Metadata Generation Module

Handles generation of project-related markdown tables:
- Project information
- Client information
- Team information
- Consultants information
- Authors information
- Copyright footers
- Document integrity legends
"""

from typing import Dict, Any
from datetime import datetime


# =============================================================================
# TRANSLATION UTILITIES
# =============================================================================

def get_translation(key: str, language: str = 'en') -> str:
    """Get translation for a key in the specified language."""
    from ._config import get_config_section
    
    try:
        translations_config = get_config_section('translations')
        languages = translations_config.get('languages', {})
        return languages.get(language, languages.get('en', {})).get(key, key.title())
    except:
        return key.title()


def detect_language_from_config() -> str:
    """Detect language from layout configuration."""
    try:
        from ._config import ModularConfigLoader
        
        config_loader = ModularConfigLoader()
        config = config_loader.load_project()
        
        language = config.get('language', 'en')
        if isinstance(language, dict):
            language = language.get('default', 'en')
            
        return language if language in ['en', 'es'] else 'en'
    except:
        return 'en'


# =============================================================================
# AUTHOR FORMATTING
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
    
    roles = author_data.get('role', [])
    if isinstance(roles, str):
        roles = [roles]
    
    affiliations = author_data.get('affiliation', [])
    if isinstance(affiliations, str):
        affiliations = [affiliations]
    
    contacts = author_data.get('contact', [])
    if isinstance(contacts, str):
        contacts = [contacts]
    
    parts = [name]
    
    if roles:
        roles_str = ', '.join(roles)
        parts.append(f"({roles_str})")
    
    if affiliations:
        affiliation_parts = []
        for i, affiliation in enumerate(affiliations):
            if i < len(contacts) and contacts[i]:
                affiliation_parts.append(f"{affiliation} ({contacts[i]})")
            else:
                affiliation_parts.append(affiliation)
        
        affiliations_str = ' & '.join(affiliation_parts)
        parts.append(f"- {affiliations_str}")
    elif contacts:
        contacts_str = ', '.join(contacts)
        parts.append(f"({contacts_str})")
    
    return ' '.join(parts)


# =============================================================================
# TABLE GENERATION FUNCTIONS
# =============================================================================


def generate_project_info_table(language: str = None) -> str:
    """Generate project information table from project configuration."""
    try:
        from ._config import ModularConfigLoader
        
        if language is None:
            language = detect_language_from_config()
        
        config_loader = ModularConfigLoader()
        config = config_loader.load_project()
        project_info = config.get('project', {})
        
        if not project_info:
            return f"\n<!-- No {get_translation('project_information', language).lower()} available -->\n"
        
        table = f"\n## {get_translation('project_information', language)}\n\n"
        table += f"| {get_translation('field', language)} | {get_translation('information', language)} |\n"
        table += "|:----------------------|:-------------------------------------|\n"
        
        field_translation_keys = {
            'code': 'project_code', 'name': 'project_name', 'type': 'project_type',
            'status': 'status', 'description': 'description', 'created_date': 'created_date'
        }
        
        for field, value in project_info.items():
            if field not in ['location', 'client', 'team', 'consultants'] and value and value != "":
                translation_key = field_translation_keys.get(field, field)
                readable_name = get_translation(translation_key, language)
                table += f"| {readable_name} | {value} |\n"
        
        location = project_info.get('location', {})
        if location:
            location_parts = []
            for key in ['address', 'city', 'region', 'country']:
                val = location.get(key, '')
                if val and val != "":
                    location_parts.append(val)
            
            if location_parts:
                location_str = ', '.join(location_parts)
                table += f"| {get_translation('location', language)} | {location_str} |\n"
            
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
    """Generate client information table from project configuration."""
    try:
        from ._config import ModularConfigLoader
        
        if language is None:
            language = detect_language_from_config()
        
        config_loader = ModularConfigLoader()
        config = config_loader.load_project()
        project_info = config.get('project', {})
        client_info = project_info.get('client', {})
        
        if not client_info:
            return f"\n<!-- No {get_translation('client_information', language).lower()} available -->\n"
        
        table = f"\n## {get_translation('client_information', language)}\n\n"
        table += f"| {get_translation('field', language)} | {get_translation('information', language)} |\n"
        table += "|:----------------------|:-------------------------------------|\n"
        
        field_names = {
            'name': 'Client Name', 'company': 'Company', 'contact': 'Email',
            'phone': 'Phone', 'address': 'Address'
        }
        
        for field, value in client_info.items():
            if value and value != "":
                readable_name = field_names.get(field, field.title())
                table += f"| {readable_name} | {value} |\n"
        
        table += "\n"
        return table
    except Exception as e:
        return f"\n<!-- Error generating client table: {e} -->\n"


def generate_team_table(language: str = None) -> str:
    """Generate team information table from project configuration."""
    try:
        from ._config import ModularConfigLoader
        
        if language is None:
            language = detect_language_from_config()
        
        config_loader = ModularConfigLoader()
        config = config_loader.load_project()
        project_info = config.get('project', {})
        team_info = project_info.get('team', {})
        
        if not team_info:
            return f"\n<!-- No {get_translation('project_team', language).lower()} available -->\n"
        
        table = f"\n## {get_translation('project_team', language)}\n\n"
        table += f"| {get_translation('name', language)} | {get_translation('role', language)} | {get_translation('email', language)} |\n"
        table += "|:-----------------|:-------------------------|:---------------------------|\n"
        
        for role_key in ['lead_engineer', 'project_manager']:
            if role_key in team_info:
                member = team_info[role_key]
                name = member.get('name', '')
                role = member.get('role', '')
                email = member.get('email', '')
                if name and name != "":
                    table += f"| {name} | {role or 'N/A'} | {email or 'N/A'} |\n"
        
        for group_key in ['designers', 'engineers']:
            if group_key in team_info:
                for member in team_info[group_key]:
                    name = member.get('name', '')
                    role = member.get('role', '')
                    email = member.get('email', '')
                    if name and name != "":
                        table += f"| {name} | {role or 'N/A'} | {email or 'N/A'} |\n"
        
        table += "\n"
        return table
    except Exception as e:
        return f"\n<!-- Error generating team table: {e} -->\n"


def generate_consultants_table(language: str = None) -> str:
    """Generate consultants information table from project configuration."""
    try:
        from ._config import ModularConfigLoader
        
        if language is None:
            language = detect_language_from_config()
        
        config_loader = ModularConfigLoader()
        config = config_loader.load_project()
        project_info = config.get('project', {})
        consultants_info = project_info.get('consultants', {})
        
        if not consultants_info:
            return f"\n<!-- No {get_translation('project_consultants', language).lower()} available -->\n"
        
        table = f"\n## {get_translation('project_consultants', language)}\n\n"
        table += f"| {get_translation('specialty', language)} | {get_translation('consultant', language)} | {get_translation('company', language)} | {get_translation('contact', language)} |\n"
        table += "|:-------------|:------------------|:----------------|:---------------------------|\n"
        
        specialty_names = {
            'architectural': 'Architectural', 'geotechnical': 'Geotechnical',
            'mep': 'MEP', 'structural': 'Structural'
        }
        
        for consultant_type, consultant_data in consultants_info.items():
            name = consultant_data.get('name', '')
            company = consultant_data.get('company', '')
            contact = consultant_data.get('contact', '')
            
            if name and name != "":
                specialty = specialty_names.get(consultant_type, consultant_type.title())
                table += f"| {specialty} | {name} | {company or 'N/A'} | {contact or 'N/A'} |\n"
        
        table += "\n"
        return table
    except Exception as e:
        return f"\n<!-- Error generating consultants table: {e} -->\n"


def generate_authors_table(document_type: str = "report", language: str = None) -> str:
    """Generate authors information table from project configuration."""
    try:
        from ._config import ModularConfigLoader
        
        if language is None:
            language = detect_language_from_config()
        
        config_loader = ModularConfigLoader()
        full_config = config_loader.load_project()
        authors = full_config.get('authors', [])
        
        if not authors:
            return f"\n<!-- No {get_translation('authors', language).lower()} available -->\n"
        
        table = f"\n## {get_translation('authors', language)}\n\n"
        table += ':::{.table-responsive}\n\n'
        table += f"| {get_translation('name', language)} | {get_translation('role', language)} | {get_translation('affiliation', language)} | {get_translation('contact', language)} |\n"
        table += "|:-------------|:------------------|:----------------------|:------------------------|\n"
        
        def format_cell_content(content, max_length=25):
            if len(content) > max_length:
                return content[:max_length-3] + '...'
            return content
        
        for author in authors:
            name = author.get('name', '')
            roles = ', '.join(author.get('role', [])) if author.get('role') else ''
            affiliations = ', '.join(author.get('affiliation', [])) if author.get('affiliation') else ''
            contacts = ', '.join(author.get('contact', [])) if author.get('contact') else ''
            
            if name and name != "":
                formatted_name = format_cell_content(name, 20)
                formatted_roles = format_cell_content(roles, 35) if roles else 'N/A'
                formatted_affiliations = format_cell_content(affiliations, 30) if affiliations else 'N/A'
                formatted_contacts = contacts if contacts else 'N/A'
                
                table += f"| {formatted_name} | {formatted_roles} | {formatted_affiliations} | {formatted_contacts} |\n"
        
        table += '\n:::\n\n'
        return table
    except Exception as e:
        return f"\n<!-- Error generating authors table: {e} -->\n"



def generate_project_info(info_type: str = "project", document_type: str = "report", language: str = None) -> str:
    """
    Generate project information table based on type.
    
    Args:
        info_type: Type of information (project, client, team, consultants, authors)
        document_type: Document type for author routing
        language: Language code ('en', 'es')
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
    """Generate copyright footer from project configuration."""
    try:
        from ._config import ModularConfigLoader
        
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


def generate_integrity_legend() -> str:
    """
    Generate document integrity legend that appears after references.
    Uses Quarto's raw LaTeX to ensure placement after bibliography.
    """
    legend_content = f"""

```{{=latex}}
\\newpage
\\vspace{{2cm}}
\\begin{{center}}
\\rule{{0.8\\textwidth}}{{0.4pt}}
\\end{{center}}
\\vspace{{0.5cm}}

\\begin{{center}}
\\textbf{{\\large Nota Legal y de Integridad del Documento}}
\\end{{center}}

\\vspace{{0.5cm}}

\\begin{{center}}
Este documento tiene validez únicamente en su forma íntegra y original; \\\\
no se permite la reproducción parcial sin autorización previa.
\\end{{center}}

\\vspace{{1cm}}

\\begin{{center}}
\\textit{{Documento generado el {datetime.now().strftime('%d de %B de %Y')} a las {datetime.now().strftime('%H:%M')} mediante ePy\\_docs}}
\\end{{center}}

\\begin{{center}}
\\rule{{0.8\\textwidth}}{{0.4pt}}
\\end{{center}}
```

"""
    return legend_content


def get_project_metadata(document_type: str = 'paper') -> Dict[str, Any]:
    """
    Extract metadata from project configuration.
    
    Args:
        document_type: Type of document ('paper', 'book', 'report', 'notebook')
    """
    try:
        from ePy_docs.core._config import ModularConfigLoader
        
        try:
            from ePy_docs.core._config import get_config_loader
            config_loader = get_config_loader()
            if config_loader:
                full_config = config_loader.load_project()
            else:
                config_loader = ModularConfigLoader()
                full_config = config_loader.load_project()
        except:
            config_loader = ModularConfigLoader()
            full_config = config_loader.load_project()
        
        metadata = {}
        
        if 'project' in full_config and 'name' in full_config['project']:
            metadata['title'] = full_config['project']['name']
        elif 'metadata' in full_config and 'document_name' in full_config['metadata']:
            metadata['title'] = full_config['metadata']['document_name'].replace('_', ' ')
        
        if 'project' in full_config and 'description' in full_config['project']:
            metadata['subtitle'] = full_config['project']['description']
        
        author_list = []
        
        if document_type in ['paper', 'book']:
            if 'authors' in full_config and full_config['authors']:
                for author in full_config['authors']:
                    if 'name' in author:
                        if author.get('role') or author.get('affiliation'):
                            formatted_author = format_author_info(author)
                            author_list.append(formatted_author)
                        else:
                            author_list.append(author['name'])
        
        elif document_type == 'report':
            if 'project' in full_config and 'consultants' in full_config['project']:
                consultants = full_config['project']['consultants']
                for consultant_type, consultant_info in consultants.items():
                    if 'name' in consultant_info:
                        author_list.append(consultant_info['name'])
        
        elif document_type == 'notebook':
            if 'project' in full_config and 'team' in full_config['project']:
                team = full_config['project']['team']
                
                if 'lead_engineer' in team and 'name' in team['lead_engineer']:
                    author_list.append(team['lead_engineer']['name'])
                if 'project_manager' in team and 'name' in team['project_manager']:
                    author_list.append(team['project_manager']['name'])
                
                if 'designers' in team:
                    for member in team['designers']:
                        if 'name' in member:
                            author_list.append(member['name'])
        
        if author_list:
            if len(author_list) == 1:
                metadata['author'] = author_list[0]
            else:
                metadata['author'] = author_list
        
        if 'project' in full_config and 'created_date' in full_config['project']:
            date_str = full_config['project']['created_date']
            
            try:
                import re
                
                if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
                    metadata['date'] = date_str
                elif ' de ' in date_str.lower():
                    meses = {
                        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
                    }
                    parts = date_str.lower().split(' de ')
                    if len(parts) == 3:
                        day = int(parts[0].strip())
                        month = meses.get(parts[1].strip())
                        year = int(parts[2].strip())
                        if month:
                            metadata['date'] = f"{year:04d}-{month:02d}-{day:02d}"
                        else:
                            metadata['date'] = date_str
                    else:
                        metadata['date'] = date_str
                else:
                    metadata['date'] = date_str
            except Exception:
                metadata['date'] = date_str
        else:
            metadata['date'] = datetime.now().strftime("%Y-%m-%d")
        
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
        print(f"Warning: Could not load project metadata: {e}")
        return {}
