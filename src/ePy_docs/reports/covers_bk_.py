# """Front matter generator for ePy_docs reports.

# This module provides functionality to generate professional front matter for reports,
# including project information, professional credentials, and contact details sourced
# from project.json configuration.
# """

# from typing import Dict, Any, Optional, List
# import datetime
# import json
# import os
# from pathlib import Path


# def _get_month_translations() -> Dict[str, str]:
#     """Get month name translations from English to Spanish.
    
#     Returns:
#         Dict[str, str]: Dictionary mapping English month names to Spanish equivalents.
#     """
#     # Try to load from project/aliases.json (preferred location)
#     try:
#         aliases_path = Path(__file__).parent.parent.parent / "project" / "aliases.json"
        
#         if aliases_path.exists():
#             with open(aliases_path, 'r', encoding='utf-8') as f:
#                 aliases_data = json.load(f)
#                 if "month_translations" in aliases_data:
#                     return aliases_data["month_translations"]
#     except Exception:
#         pass  # Silently fail and try next option
    
#     # Try to get translations from project configuration as fallback
#     try:
#         project_config = get_project_config(sync_json=True)
#         if "month_translations" in project_config:
#             return project_config["month_translations"]
#     except Exception:
#         pass  # Silently fail and use defaults
    
#     # Fallback to hardcoded translations if file not found or error
#     return {
#         "January": "enero", "February": "febrero", "March": "marzo",
#         "April": "abril", "May": "mayo", "June": "junio",
#         "July": "julio", "August": "agosto", "September": "septiembre",
#         "October": "octubre", "November": "noviembre", "December": "diciembre"
#     }


# def add_responsability_page(writer: Any, report_config: Optional[Dict[str, Any]] = None, sync_json: bool = True) -> None:
#     """Add a professional responsibility page with all available consultants.
    
#     Creates a professional responsibility section with project details and information
#     about all consultants involved in the project. All content is dynamically populated
#     from project.json configuration.
    
#     Args:
#         writer: The writer object that provides add_h1 and add_content methods
#         report_config: Optional report configuration dictionary with customization options
#         sync_json: Whether to synchronize JSON files before reading. Defaults to True.
        
#     Returns:
#         None: Content is added directly to the writer object
        
#     Assumes:
#         The writer object has add_h1 and add_content methods.
#         Project configuration exists and contains valid project and consultants information.
#     """
#     # Get project configuration
#     project_config = get_project_config(sync_json=sync_json)
    
#     # Extract relevant project information
#     project_info = project_config.get('project', {})
#     client_info = project_config.get('client', {})
#     location_info = project_config.get('location', {})
#     consultants_list = project_config.get('consultants', [])
    
#     # Get report configuration defaults
#     report_config = report_config or {}
    
#     # Get title from configuration or use default
#     title = report_config.get('professional_responsibility_title', 'Responsabilidad Profesional')
    
#     # Format project information
#     project_name = project_info.get('name', '[Nombre del Proyecto]')
#     project_version = project_info.get('version', '[Versión del Documento]')
#     project_code = project_info.get('code', '[Código del Proyecto]')
    
#     # Get location details
#     location_address = location_info.get('address', '')
#     location_city = location_info.get('city', '')
#     location_state = location_info.get('state', '')
#     location_country = location_info.get('country', '')
    
#     # Combine location elements that exist
#     location_parts = []
#     if location_address:
#         location_parts.append(location_address)
#     if location_city:
#         location_parts.append(location_city)
#     if location_state and location_state != location_city:
#         location_parts.append(location_state)
#     if location_country:
#         location_parts.append(location_country)
    
#     location_str = ', '.join(location_parts) if location_parts else '[Ubicación del Proyecto]'
    
#     # Get client name
#     client_name = client_info.get('name', '[Nombre del Cliente]')
    
#     # Get date information
#     date_str = project_info.get('updated_date', '')
#     if not date_str:
#         date_str = project_info.get('created_date', '')
#     if not date_str:
#         # Use current date if no date is provided
#         date_str = datetime.datetime.now().strftime("%d de %B de %Y")
#         # Try to convert month to Spanish
#         month_translations = _get_month_translations()
#         for eng, esp in month_translations.items():
#             date_str = date_str.replace(eng, esp)
    
#     # Generate the project information content
#     content = f"""

# **Proyecto:** {project_name}  
# **Ubicación:** {location_str}  
# **Cliente:** {client_name}  

# ## {title}

# """
    
#     # If no consultants in list, fallback to single consultant
#     if not consultants_list and project_config.get('consultant'):
#         consultants_list = [project_config.get('consultant')]
    
#     # If still no consultants, add placeholder
#     if not consultants_list:
#         consultants_list = [{
#             "name": "[Nombre del Consultor]",
#             "license": "[Número de Carné]",
#             "title": "[Título del Consultor]",
#             "education": [],
#             "company": {
#                 "name": "[Nombre de la Empresa]",
#                 "address": "[Dirección]",
#                 "phone": "[Teléfono]",
#                 "email": "[Email]"
#             }
#         }]
    
#     # Add each consultant's information
#     for i, consultant in enumerate(consultants_list):
#         # Get consultant details
#         consultant_name = consultant.get('name', '[Nombre del Consultor]')
#         consultant_license = consultant.get('license', '[Número de Carné]')
#         consultant_title = consultant.get('title', '')
#         consultant_role = consultant.get('role', '')
        
#         # Get education details
#         education = consultant.get('education', [])
#         education_str = '\n'.join([f"{degree}  " for degree in education]) if education else ''
        
#         # Get company details
#         company_info = consultant.get('company', {})
#         company_name = company_info.get('name', '[Nombre de la Empresa]')
#         company_address = company_info.get('address', '[Dirección]')
#         company_phone = company_info.get('phone', '[Teléfono]')
#         company_email = company_info.get('email', '[Email]')
        
#         # Add separator if not the first consultant
#         if i > 0:
#             content += "\n\n---\n\n"
        
#         # Add consultant details
#         content += f"**Elaborado por:**  \n"
#         content += f"{consultant_name}  \n"
        
#         if consultant_role:
#             content += f"{consultant_role}  \n"
        
#         content += f"Carné CFIA: {consultant_license}  \n"
        
#         if consultant_title:
#             content += f"{consultant_title}  \n"
        
#         if education_str:
#             content += f"{education_str}\n"
        
#         # Add company info
#         content += f"\n**{company_name}**  \n"
#         content += f"{company_address}  \n"
#         content += f"Tel. {company_phone}  \n"
#         content += f"email: {company_email}  \n"
    
#     # Add document information at the end
#     content += f"\n\n**Fecha:** {date_str}  \n"
#     content += f"**Versión:** {project_version}  \n"
#     content += f"**Código de Proyecto:** {project_code}  \n"
    
#     # Add the content to the report
#     writer.add_content(content)


# def add_project_cover(writer: Any, report_config: Optional[Dict[str, Any]] = None, sync_json: bool = True) -> None:
#     """Add a complete project cover page to the report.
    
#     Creates a comprehensive cover page with project details, client information,
#     consultant credentials, and all relevant metadata. All content is dynamically
#     populated from project.json configuration. This function uses the primary consultant
#     from the consultants list or falls back to the single consultant entry.
    
#     Args:
#         writer: The writer object that provides methods to add content to the document
#         report_config: Optional report configuration dictionary with customization options
#         sync_json: Whether to synchronize JSON files before reading. Defaults to True.
        
#     Returns:
#         None: Content is added directly to the writer object
        
#     Assumes:
#         The writer object has methods to add content and formatting.
#         Project configuration exists and contains valid information.
#     """
#     # Get project configuration
#     project_config = get_project_config(sync_json=sync_json)
    
#     # Extract relevant project information
#     project_info = project_config.get('project', {})
#     client_info = project_config.get('client', {})
#     location_info = project_config.get('location', {})
    
#     # Try to get primary consultant from consultants list, fall back to single consultant
#     consultants_list = project_config.get('consultants', [])
#     primary_consultant = consultants_list[0] if consultants_list else project_config.get('consultant', {})
#     company_info = primary_consultant.get('company', {})
    
#     # Get project name and description
#     project_name = project_info.get('name', 'Proyecto de Ingeniería')
#     project_description = project_info.get('description', '')
    
#     # Format the cover page content
#     writer.add_cover_title(project_name)
    
#     if project_description:
#         writer.add_cover_subtitle(project_description)
    
#     # Add client information
#     client_name = client_info.get('name', '')
#     if client_name:
#         writer.add_cover_section('Cliente')
#         writer.add_cover_content(client_name)
        
#         # Add client contact if available
#         client_contact = client_info.get('contact_person', '')
#         if client_contact:
#             writer.add_cover_content(f"Contacto: {client_contact}")
    
#     # Add location information
#     location_parts = []
#     for key in ['address', 'city', 'state', 'country']:
#         if location_info.get(key):
#             location_parts.append(location_info[key])
    
#     if location_parts:
#         writer.add_cover_section('Ubicación')
#         writer.add_cover_content(', '.join(location_parts))
    
#     # Add consultant information
#     consultant_name = primary_consultant.get('name', '')
#     if consultant_name:
#         writer.add_cover_section('Consultor')
#         writer.add_cover_content(consultant_name)
        
#         # Add license and role if available
#         consultant_license = primary_consultant.get('license', '')
#         if consultant_license:
#             writer.add_cover_content(f"CFIA: {consultant_license}")
            
#         consultant_role = primary_consultant.get('role', '')
#         if consultant_role:
#             writer.add_cover_content(f"Rol: {consultant_role}")
    
#     # Add company information
#     company_name = company_info.get('name', '')
#     if company_name:
#         writer.add_cover_section('Empresa Consultora')
#         writer.add_cover_content(company_name)
        
#         # Add company contact if available
#         if company_info.get('phone'):
#             writer.add_cover_content(f"Tel: {company_info['phone']}")
#         if company_info.get('email'):
#             writer.add_cover_content(f"Email: {company_info['email']}")
#         if company_info.get('website'):
#             writer.add_cover_content(f"Web: {company_info['website']}")
    
#     # Add project metadata - fail if required dates not provided
#     date_str = project_info.get('updated_date') or project_info.get('created_date')
#     if not date_str:
#         raise ValueError("Project must have either 'updated_date' or 'created_date'")
    
#     version = project_info.get('version')
#     code = project_info.get('code')
    
#     if any([date_str, version, code]):
#         writer.add_cover_section('Información del Documento')
#         if date_str:
#             writer.add_cover_content(f"Fecha: {date_str}")
#         if version:
#             writer.add_cover_content(f"Versión: {version}")
#         if code:
#             writer.add_cover_content(f"Código: {code}")
