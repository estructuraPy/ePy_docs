"""
Project Information Tables Module

Handles generation of structured project information tables as DataFrames
that can be processed through the standard add_table() pipeline for consistent formatting.
"""

import pandas as pd
from typing import Dict, List, Optional, Any
import inspect


def _get_project_config_from_stack() -> Dict[str, Any]:
    """Get project configuration from DocumentWriter instance in call stack."""
    for frame_info in inspect.stack():
        frame_locals = frame_info.frame.f_locals
        for name, obj in frame_locals.items():
            if hasattr(obj, '_project_info') or hasattr(obj, '_authors') or hasattr(obj, '_client_info'):
                config = {}
                if hasattr(obj, '_project_info') and obj._project_info:
                    config['project'] = obj._project_info
                if hasattr(obj, '_authors') and obj._authors:
                    config['authors'] = obj._authors
                if hasattr(obj, '_client_info') and obj._client_info:
                    config['client'] = obj._client_info
                return config
    return {}


def get_project_table_data(language: str = 'en') -> Optional[pd.DataFrame]:
    """
    Generate project information as DataFrame.
    
    Args:
        language: Language code ('en', 'es')
        
    Returns:
        DataFrame with project information or None if no data available
    """
    config = _get_project_config_from_stack()
    project_info = config.get('project', {})
    
    if not project_info:
        return None
    
    # Translation mappings
    field_translations = {
        'en': {
            'code': 'Project Code',
            'name': 'Project Name',
            'type': 'Project Type',
            'status': 'Status',
            'description': 'Description',
            'created_date': 'Created Date',
            'location': 'Location'
        },
        'es': {
            'code': 'Código del Proyecto',
            'name': 'Nombre del Proyecto',
            'type': 'Tipo de Proyecto',
            'status': 'Estado',
            'description': 'Descripción',
            'created_date': 'Fecha de Creación',
            'location': 'Ubicación'
        }
    }
    
    translations = field_translations.get(language, field_translations['en'])
    
    # Build data rows
    data = []
    
    # Add basic project fields
    field_order = ['code', 'name', 'type', 'status', 'description', 'created_date']
    for field in field_order:
        value = project_info.get(field)
        if value and str(value).strip():
            data.append({
                'Field': translations.get(field, field.title()),
                'Information': str(value)
            })
    
    # Handle location specially
    location = project_info.get('location', {})
    if location:
        if isinstance(location, dict):
            location_parts = []
            for key in ['address', 'city', 'region', 'country']:
                if location.get(key):
                    location_parts.append(location[key])
            if location_parts:
                data.append({
                    'Field': translations.get('location', 'Location'),
                    'Information': ', '.join(location_parts)
                })
        elif isinstance(location, str) and location.strip():
            data.append({
                'Field': translations.get('location', 'Location'),
                'Information': location
            })
    
    if not data:
        return None
    
    return pd.DataFrame(data)


def get_authors_table_data(language: str = 'en') -> Optional[pd.DataFrame]:
    """
    Generate authors information as DataFrame.
    
    Args:
        language: Language code ('en', 'es')
        
    Returns:
        DataFrame with authors information or None if no data available
    """
    config = _get_project_config_from_stack()
    authors = config.get('authors', [])
    
    if not authors:
        return None
    
    # Translation mappings
    column_translations = {
        'en': {
            'name': 'Name',
            'role': 'Role',
            'affiliation': 'Affiliation',
            'contact': 'Contact'
        },
        'es': {
            'name': 'Nombre',
            'role': 'Rol',
            'affiliation': 'Afiliación',
            'contact': 'Contacto'
        }
    }
    
    translations = column_translations.get(language, column_translations['en'])
    
    # Build data rows
    data = []
    for author in authors:
        name = author.get('name', '')
        if not name.strip():
            continue
            
        # Handle roles (can be list or string)
        roles = author.get('role', [])
        if isinstance(roles, list):
            role_str = ', '.join(roles) if roles else 'N/A'
        else:
            role_str = str(roles) if roles else 'N/A'
        
        # Handle affiliations (can be list or string)
        affiliations = author.get('affiliation', [])
        if isinstance(affiliations, list):
            affiliation_str = ', '.join(affiliations) if affiliations else 'N/A'
        else:
            affiliation_str = str(affiliations) if affiliations else 'N/A'
        
        # Handle contacts (can be list or string)
        contacts = author.get('contact', [])
        if isinstance(contacts, list):
            contact_str = ', '.join(contacts) if contacts else 'N/A'
        else:
            contact_str = str(contacts) if contacts else 'N/A'
        
        data.append({
            translations['name']: name,
            translations['role']: role_str,
            translations['affiliation']: affiliation_str,
            translations['contact']: contact_str
        })
    
    if not data:
        return None
        
    return pd.DataFrame(data)


def get_client_table_data(language: str = 'en') -> Optional[pd.DataFrame]:
    """
    Generate client information as DataFrame.
    
    Args:
        language: Language code ('en', 'es')
        
    Returns:
        DataFrame with client information or None if no data available
    """
    config = _get_project_config_from_stack()
    client_info = config.get('client', {})
    
    if not client_info:
        return None
    
    # Translation mappings
    field_translations = {
        'en': {
            'name': 'Client Name',
            'company': 'Company',
            'contact': 'Contact',
            'address': 'Address'
        },
        'es': {
            'name': 'Nombre del Cliente',
            'company': 'Empresa',
            'contact': 'Contacto',
            'address': 'Dirección'
        }
    }
    
    translations = field_translations.get(language, field_translations['en'])
    
    # Build data rows
    data = []
    field_order = ['name', 'company', 'contact', 'address']
    for field in field_order:
        value = client_info.get(field)
        if value and str(value).strip():
            data.append({
                'Field': translations.get(field, field.title()),
                'Information': str(value)
            })
    
    if not data:
        return None
        
    return pd.DataFrame(data)


def get_project_info_dataframe(info_type: str, language: str = 'en') -> Optional[pd.DataFrame]:
    """
    Get project information as DataFrame for the specified type.
    
    Args:
        info_type: Type of information ('project', 'authors', 'client')
        language: Language code ('en', 'es')
        
    Returns:
        DataFrame with the requested information or None if not available
    """
    if info_type == 'project':
        return get_project_table_data(language)
    elif info_type == 'authors':
        return get_authors_table_data(language)
    elif info_type == 'client':
        return get_client_table_data(language)
    else:
        return None


def get_project_info_title(info_type: str, language: str = 'en') -> str:
    """
    Get the appropriate title for a project information table.
    
    Args:
        info_type: Type of information ('project', 'authors', 'client')
        language: Language code ('en', 'es')
        
    Returns:
        Localized title for the table
    """
    title_translations = {
        'en': {
            'project': 'Project Information',
            'authors': 'Authors',
            'client': 'Client Information'
        },
        'es': {
            'project': 'Información del Proyecto',
            'authors': 'Autores',
            'client': 'Información del Cliente'
        }
    }
    
    translations = title_translations.get(language, title_translations['en'])
    return translations.get(info_type, info_type.title())