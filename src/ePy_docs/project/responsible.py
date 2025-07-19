"""Professional responsibility page generator for ePy_docs .

Creates formatted text sections for project and consultant information from JSON configuration.
Strict JSON-only configuration - no hardcoded values, no fallbacks.
"""

from typing import Dict, Any, Optional, List
import json
import os
from pathlib import Path

from ePy_docs.styler.setup import get_project_config
from ePy_docs.project.setup import _load_setup_config
from ePy_docs.reports.covers import _get_month_translations
from ePy_docs.core.text import TextFormatter
from ePy_docs.project.copyright import create_authorship_text, create_copyright_page


def create_project_info_text(project_config: Dict[str, Any], writer) -> None:
    """Generate formatted text for project information with page break."""
    
    # Get report configuration from setup.json
    setup_config = _load_setup_config()
    report_config = setup_config["report_config"]
    project = project_config["project"]
    labels = report_config["project_labels"]
    
    # Validate required project fields
    required_fields = ['name', 'description', 'code', 'version', 'created_date']
    for field in required_fields:
        if field not in project:
            raise ValueError(f"Required project field '{field}' missing from project configuration")
    
    # Add project title and section
    writer.add_h1(report_config["project_title"])
    writer.add_h2(report_config["project_section_title"])
    
    # Add project information with consistent formatting
    writer.add_content(TextFormatter.format_field(labels['project'], project['name']))
    writer.add_content(TextFormatter.format_field(labels['code'], project['code']))
    writer.add_content(TextFormatter.format_field(labels['description'], project['description']))

    # Add location information if available
    if "location" in project_config:
        location = project_config["location"]
        
        # Validate required location fields
        required_location_fields = ['city', 'state', 'country']
        for field in required_location_fields:
            if field not in location:
                raise ValueError(f"Required location field '{field}' missing from location configuration")
        
        # Build location string: country, state, city, zip, (lat, lon)
        location_parts = [location['country'], location['state'], location['city']]
        
        # Add optional fields
        if 'zip' in location:
            location_parts.append(location['zip'])
        
        if 'latitude' in location and 'longitude' in location:
            location_parts.append(f"({location['latitude']}, {location['longitude']})")
        
        location_string = ", ".join(location_parts)
        writer.add_content(TextFormatter.format_field(labels['location'], location_string))

    writer.add_content(TextFormatter.format_field(labels['date'], project['created_date']))
    
    # Add optional updated date
    if "updated_date" in project:
        writer.add_content(TextFormatter.format_field(labels['updated_date_label'], project['updated_date']))
    
    writer.add_content(TextFormatter.format_field(labels['version'], project['version']))
    

    
    writer.add_content("\n")
    

    # Client Information Section
    if "client" in project_config:
        client = project_config["client"]
        client_labels = report_config["client_labels"]

        writer.add_h2(client_labels["client"])
        writer.add_content(TextFormatter.format_field(client_labels['client_name_label'], client['name']))
        writer.add_content(TextFormatter.format_field(client_labels['email'], client['email']))
        writer.add_content(TextFormatter.format_field(client_labels['phone'], client['phone']))
        writer.add_content("\n")
        

def create_consultant_info_text(project_config: Dict[str, Any], writer) -> None:
    """Generate formatted text for all consultants with consistent styling."""
    
    # Get report configuration from setup.json
    setup_config = _load_setup_config()
    report_config = setup_config["report_config"]
    consultants = project_config["consultants"]
    labels = report_config["consultant_labels"]
    
    # Add consultants section title
    writer.add_h2(labels["label"]) 
    
    for i, consultant in enumerate(consultants):
        # Build consultant information content
        consultant_info = []
        
        # Add personal information with bold formatting
        consultant_info.append(f"**{labels['specialty']}:** {consultant['specialty']}\n")
        consultant_info.append(f"**{labels['license']}:** {consultant['license']}\n")
        
        # Add optional fields if present
        if "orcid_label" in consultant:
            consultant_info.append(f"**ORCID:** {consultant['orcid_label']}\n")
        
        if "linkedin" in consultant:
            consultant_info.append(f"**LinkedIn:** {consultant['linkedin']}\n")
        
        # Education Section - same level as other fields
        if "education" in consultant:
            education_items = ", ".join(consultant["education"])
            consultant_info.append(f"**{labels['education']}:** {education_items}\n")
        
        # Combine all consultant information into a single note with gray brand format
        consultant_content = "\n".join(consultant_info)
        writer.add_consultant(consultant_content, title=consultant["name"])
    

def add_responsibility_text(writer) -> None:
    """Generate complete responsibility section with project info, consultants, and company/copyright.
    
    Args:
        writer: ReportFormatter instance for adding content
    
    Raises:
        ValueError: If any required configuration is missing
    """
    # Get project configuration
    project_config = get_project_config(sync_json=True)
    
    if not project_config:
        raise ValueError("Project configuration not found or empty")
    
    # Add all sections using writer
    create_project_info_text(project_config, writer)
    create_authorship_text(project_config, writer)
    create_consultant_info_text(project_config, writer)
    create_copyright_page(project_config, writer)


def get_consultant_names(project_config: Optional[Dict[str, Any]] = None) -> List[str]:
    """Get list of consultant names from project configuration.
    
    Args:
        project_config: Optional project configuration dict. If None, loads from file.
    
    Returns:
        List[str]: List of consultant names
    
    Raises:
        ValueError: If consultants configuration is missing or invalid
    """
    if project_config is None:
        project_config = get_project_config(sync_json=True)
    
    if not project_config:
        raise ValueError("Project configuration not found or empty")
    
    if "consultants" not in project_config:
        raise ValueError("consultants configuration missing from project configuration")
    
    consultants = project_config["consultants"]
    
    if not consultants:
        raise ValueError("consultants list is empty in project configuration")
    
    names = []
    for i, consultant in enumerate(consultants):
        if "name" not in consultant:
            raise ValueError(f"Required field 'name' missing from consultant {i+1} configuration")
        names.append(consultant["name"])
    
    return names


def get_author_for_section(section_name: str, project_config: Optional[Dict[str, Any]] = None) -> str:
    """Get the author name for a specific section. 
    
    Since the current project.json structure doesn't have authorship roles,
    this function returns the first consultant as the default author.
    
    Args:
        section_name: Name of the section (kept for compatibility)
        project_config: Optional project configuration dict. If None, loads from file.
    
    Returns:
        str: Author name (first consultant from the consultants list)
    
    Raises:
        ValueError: If consultants configuration is missing
    """

    if project_config is None:
        project_config = get_project_config(sync_json=True)
    
    if not project_config:
        raise ValueError("Project configuration not found or empty")
    
    if "consultants" not in project_config:
        raise ValueError("consultants configuration missing from project configuration")
    
    consultants = project_config["consultants"]
    
    if not consultants:
        raise ValueError("consultants list is empty in project configuration")
    
    # Return the first consultant as the default author
    if "name" not in consultants[0]:
        raise ValueError("Required field 'name' missing from first consultant configuration")
    
    return consultants[0]["name"]