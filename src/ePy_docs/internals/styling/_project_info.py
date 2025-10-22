"""Project information management for ePy_docs reports.

Handles project data, professional responsibility, copyright information, and authorship details
for professional reports and documentation. Consolidates functionality from multiple modules
into a single, cohesive project information system.

Strict JSON-only configuration - no hardcoded values, no fallbacks.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from ePy_docs.internals.styling._pages import get_project_config
from ePy_docs.internals.data_processing._data import load_cached_files
from ePy_docs.config.setup import _resolve_config_path

def _load_component_config(config_name: str) -> Dict[str, Any]:
    """Helper function to load component configuration using the correct pattern."""
    # Handle redundant configs that are now in master.epyson
    if config_name in ['setup', 'project_info']:
        from ePy_docs.config.config_manager import ConfigManager
        cm = ConfigManager()
        if config_name == 'setup':
            return cm.get_config()
        elif config_name == 'project_info':
            return cm.get_config('general')['common']
    
    # Use centralized config system for all other configs
    from ePy_docs.config.setup import get_config_section
    return get_config_section(config_name)

# UPDATED IMPORTS - Using new kingdom architecture
# from ePy_docs.internals.formatting._text import TextFormatter  # LEGACY - not available in purified TEXT kingdom
from ePy_docs.internals.formatting._text import get_text_config
from ePy_files import import_to_dict

# TEMPORARY TextFormatter replacement for compatibility
class TextFormatter:
    """Temporary TextFormatter replacement for legacy compatibility."""
    
    @staticmethod
    def format_field(label, value):
        """Simple text field formatter replacement."""
        if value is None:
            value = ""
        return f"**{label}:** {value}\n"


# Data classes for project structure (DEPRECATED - Not actively used)
@dataclass
class ProjectPaths:
    """Data class to hold all project file paths.
    
    Note: This dataclass is deprecated and not actively used in the codebase.
          Unit configuration is now handled by ePy_units library.
    
    Assumptions:
        All file paths are configured through proper initialization
        No default values are provided to prevent result bias
    """
    soil_json: str
    units_json: str  # DEPRECATED - Units now handled by user
    project_json: str
    foundations_json: str
    design_codes_json: str
    report: str
    watermark_png: str
    blocks_csv: str
    nodes_csv: str
    reactions_csv: str
    combinations_csv: str


@dataclass
class ProjectFolders:
    """Data class to hold all project folder paths.
    
    Note: This dataclass is deprecated and not actively used in the codebase.
          Unit configuration is now handled by ePy_units library.
    
    Assumptions:
        All folder paths are configured through proper initialization
        No default values are provided to prevent configuration bias
    """
    templates: str
    config: str
    brand: str
    data: str
    results: str
    exports: str
    soil_config: str
    reports_config: str
    units_config: str  # DEPRECATED - Units now handled by user
    design_codes: str
    structure_config: str


# components project information functions
def load_setup_config() -> Dict[str, Any]:
    """Load setup configuration from components/setup.json.
        
    Returns:
        Dictionary containing setup configuration data
        
    Raises:
        RuntimeError: If setup configuration cannot be loaded
    """
    try:
        # Load from new location in components/ usando ePy_files directamente
        from ePy_files import import_to_dict
        
        # Try to load from components/setup.json
        import os
        from pathlib import Path
        
        # Get package root
        package_root = Path(__file__).parent.parent
        setup_path = package_root / "components" / "setup.json"
        
        if setup_path.exists():
            return import_to_dict(setup_path)
        else:
            # Fallback to legacy location if needed during transition
            legacy_path = package_root / "project" / "setup.json"
            if legacy_path.exists():
                return import_to_dict(legacy_path)
            else:
                raise FileNotFoundError("setup.json not found in components/ or project/ directories")
        
    except Exception as e:
        raise RuntimeError(f"Failed to load setup configuration: {e}")


def get_project_config_data() -> Dict[str, Any]:
    """Load project configuration from project_info.json.
        
    Returns:
        Dictionary containing project configuration data
    """
    try:
        return _load_component_config('project_info')
    except Exception:
        # Fallback during transition
        try:
            return _load_component_config('project')
        except Exception as e:
            raise RuntimeError(f"Failed to load project configuration: {e}")


def get_constitutional_project_info(document_type: str = "report") -> Dict[str, Any]:
    """Extract constitutional project information based on document type.
    
    Args:
        document_type: Type of document ("report" or "paper")
        
    Returns:
        Merged dictionary with common info and document-specific overrides
    """
    from ePy_docs.config.config_manager import ConfigManager
    cm = ConfigManager()
    full_config = cm.get_config()
    
    # Extract common information from general.common
    common_info = full_config.get('general', {}).get('common', {})
    
    # Extract document-specific information from general[document_type]
    document_info = full_config.get('general', {}).get(document_type, {})
    
    # Deep merge: Start with common, then override nested keys from document_info
    merged_info = common_info.copy()
    
    # For each key in document_info, do a nested merge if both are dicts
    for key, value in document_info.items():
        if key in merged_info and isinstance(merged_info[key], dict) and isinstance(value, dict):
            # Nested dict: merge the nested dict
            merged_info[key] = {**merged_info[key], **value}
        else:
            # Not both dicts: simple override
            merged_info[key] = value
    
    return merged_info


def get_legacy_project_structure(document_type: str = "report") -> Dict[str, Any]:
    """Provide legacy project structure for backward compatibility.
    
    Args:
        document_type: Type of document ("report" or "paper")
        
    Returns:
        Dictionary with 'project' key containing merged configuration
    """
    constitutional_info = get_constitutional_project_info(document_type)
    return {'project': constitutional_info}


# Project information generation functions
def create_project_info_text(project_config: Dict[str, Any], writer) -> None:
    """Generate formatted text for project information with page break."""
    
    # Get report configuration from setup.json
    setup_config = load_setup_config()
    report_config = setup_config["report_config"]
    project = project_config["project"]
    labels = report_config["project_labels"]
    
    # Validate required project fields
    required_fields = ['name', 'description', 'code', 'version']
    for field in required_fields:
        if field not in project:
            raise ValueError(f"Required project field '{field}' missing from project configuration")
    
    # Add project title and section
    # Initialize writer with minimal content to fix H1 issue
    writer.add_content("\\clearpage\n\n")  # Page break to start fresh

    writer.add_h1(report_config["responsibilities_title"])
    
    writer.add_h2(report_config["project_section_title"])
    
    # Start content block for project information section using Quarto div syntax
    writer.add_content("::: {.content-block}\n")
    
    # Add project name as subtitle (similar to consultant names)
    writer.add_h3(project['name'])
    
    # Add project information with consistent formatting
    writer.add_content(f"**{labels['code']}:** {project['code']}\n\n")
    writer.add_content(f"**{labels['description']}:** {project['description']}\n\n")

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
        writer.add_content(f"**{labels['location']}:** {location_string}\n\n")
    
    writer.add_content(f"**{labels['version']}:** {project['version']}\n\n")
    
    # End content block for project information
    writer.add_content(":::\n\n")
    
    # Client Information Section
    if "client" in project_config:
        client = project_config["client"]
        client_labels = report_config["client_labels"]

        writer.add_h2(client_labels["client"])
        
        # Start content block for client information using Quarto div syntax
        writer.add_content("::: {.content-block}\n")
        
        # Add client name as subtitle (similar to consultant names)
        writer.add_h3(client['name'])
        writer.add_content(f"**{client_labels['email']}:** {client['email']}\n\n")
        writer.add_content(f"**{client_labels['phone']}:** {client['phone']}\n\n")
        
        # Add address if available
        if 'address' in client:
            writer.add_content(f"**Dirección:** {client['address']}\n\n")
        
        # End content block for client information
        writer.add_content(":::\n\n")


def create_consultant_info_text(project_config: Dict[str, Any], writer) -> None:
    """Generate formatted text for all consultants with consistent styling."""
    
    # Get report configuration from setup.json
    setup_config = load_setup_config()
    report_config = setup_config["report_config"]
    consultant_labels = report_config["consultant_labels"]
    
    if "authors" not in project_config:
        raise ValueError("authors configuration missing from project configuration")
    
    authors = project_config["authors"]
    
    if not authors or len(authors) == 0:
        raise ValueError("At least one author must be configured")
    
    # Add consultants section
    writer.add_h2(consultant_labels["label"])
    
    # Process each author
    for author in authors:
        # Validate required author fields
        required_fields = ['name', 'specialty', 'license']
        for field in required_fields:
            if field not in author:
                raise ValueError(f"Required author field '{field}' missing from author configuration")
        
        # Start content block for each author using Quarto div syntax
        writer.add_content("::: {.content-block}\n")
        
        # Add author name as subtitle (H3)
        writer.add_h3(author['name'])
        
        # Add author information with consistent formatting
        writer.add_content(f"**{consultant_labels['specialty']}:** {author['specialty']}\n\n")
        writer.add_content(f"**{consultant_labels['license']}:** {author['license']}\n\n")
        
        # Add optional fields if available
        if 'orcid' in author:
            writer.add_content(f"**{consultant_labels['orcid_label']}:** {author['orcid']}\n\n")
        
        if 'linkedin' in author:
            writer.add_content(f"**{consultant_labels['linkedin']}:** {author['linkedin']}\n\n")
        
        if 'education' in author:
            writer.add_content(f"**{consultant_labels['education']}:** {author['education']}\n\n")
        
        # End content block for this author
        writer.add_content(":::\n\n")


# Copyright and authorship functions
def create_copyright_page(project_config: Dict[str, Any], writer) -> None:
    """Generate copyright and disclaimer footer as a standalone section.
    
    Creates a new page with copyright information and disclaimer centered at the bottom.
    This can be used independently or as part of other report sections.
    
    Args:
        project_config: Dictionary containing project configuration with copyright information
        writer: ReportWriter instance for adding content
    
    Raises:
        ValueError: If copyright configuration is missing or invalid
    """
    if "copyright" not in project_config:
        raise ValueError("copyright configuration missing from project configuration")
    
    copyright_info = project_config["copyright"]
    
    # Validate required copyright fields
    required_fields = ['reserved', 'disclaimer']
    for field in required_fields:
        if field not in copyright_info:
            raise ValueError(f"Required copyright field '{field}' missing from copyright configuration")
    
    # Add copyright and disclaimer at bottom of page
    writer.add_content("\\newpage\n\n")
    writer.add_content("\\null\n")  # Empty content
    writer.add_content("\\vfill\n")  # Fill vertical space
    writer.add_content("\\begin{center}\n")
    writer.add_content("\\small\\textit{" + copyright_info['reserved'] + "}\\\\\n")
    writer.add_content("\\vspace{0.5cm}\n")
    writer.add_content("\\small\\textit{" + copyright_info['disclaimer'] + "}\n")
    writer.add_content("\\end{center}\n")
    writer.add_content("\\vfill\n")  # Fill remaining space


def create_authorship_text(project_config: Dict[str, Any], writer) -> None:
    """Generate formatted text for copyright and company information.
    
    Args:
        project_config: Dictionary containing project configuration with copyright information
        writer: ReportWriter instance for adding content
    
    Raises:
        ValueError: If required configuration is missing
    """
    # Get report configuration from setup.json
    setup_config = load_setup_config()
    report_config = setup_config["report_config"]
    company_labels = report_config["company_labels"]
    copyright_info = project_config["copyright"]
    
    # Add company information section
    writer.add_h2(company_labels["section_title"])
    
    # Add company name as subtitle (similar to consultant names)
    writer.add_h3(copyright_info['name'])
    
    # Company information fields in order with proper labels (excluding name since it's now the subtitle)
    company_fields = [
        (company_labels["legal_name"], copyright_info['legal_name']),
        (company_labels["address"], copyright_info['address']),
        (company_labels["phone"], copyright_info['phone']),
        (company_labels["email"], copyright_info['email']),
        (company_labels["website"], copyright_info['website'])
    ]
    
    # Add registration if available
    if 'registration' in copyright_info:
        company_fields.append((company_labels.get("registration", "Registro"), copyright_info['registration']))
    
    # Add company information with consistent formatting
    for label, value in company_fields:
        writer.add_content(TextFormatter.format_field(label, value))
    
    writer.add_content("\n")


def create_company_info(project_config: Dict[str, Any], writer) -> None:
    """Generate only company information without copyright footer.
    
    Useful when you need company info but want to handle copyright separately.
    
    Args:
        project_config: Dictionary containing project configuration with copyright information
        writer: ReportWriter instance for adding content
        sync_files: Whether to use synchronized configuration files
    
    Raises:
        ValueError: If required configuration is missing
    """
    # Get report configuration from setup.json
    setup_config = load_setup_config()
    report_config = setup_config["report_config"]
    company_labels = report_config["company_labels"]
    copyright_info = project_config["copyright"]
    
    # Add company information section
    writer.add_h2(company_labels["section_title"])
    
    # Company information fields in order with proper labels
    company_fields = [
        (company_labels["company"], copyright_info['name']),
        (company_labels["legal_name"], copyright_info['legal_name']),
        (company_labels["address"], copyright_info['address']),
        (company_labels["phone"], copyright_info['phone']),
        (company_labels["email"], copyright_info['email']),
        (company_labels["website"], copyright_info['website']),
        (company_labels["registration"], copyright_info['registration'])
    ]
    
    # Add company information with consistent formatting
    for label, value in company_fields:
        writer.add_content(TextFormatter.format_field(label, value))
    
    writer.add_content("\n")


# Main responsibility page function
def add_responsibility_text(writer) -> None:
    """Generate complete responsibility section with project info, consultants, and company/copyright.
    
    Args:
        writer: ReportWriter instance for adding content
    
    Raises:
        ValueError: If any required configuration is missing
    """
    # Get project configuration
    project_config = get_project_config()
    
    if not project_config:
        raise ValueError("Project configuration not found or empty")
    
    # Get report configuration from setup.json
    setup_config = load_setup_config()
    report_config = setup_config["report_config"]
    
    # Add the responsibilities section title
    # writer.add_h1(report_config["responsibilities_title"])
    
    # Add all sections using writer
    create_project_info_text(project_config, writer)
    create_authorship_text(project_config, writer)
    create_consultant_info_text(project_config, writer)
    create_copyright_page(project_config, writer)


# Utility functions
def get_consultant_names(project_config: Optional[Dict[str, Any]] = None) -> List[str]:
    """Get list of author names from project configuration.
    
    Args:
        project_config: Optional project configuration dictionary. If None, loads from file.
        
    Returns:
        List of author names
        
    Raises:
        ValueError: If author configuration is missing or invalid
    """
    if project_config is None:
        project_config = get_project_config()
    
    if not project_config:
        raise ValueError("Project configuration not found or empty")
    
    if "authors" not in project_config:
        raise ValueError("authors configuration missing from project configuration")
    
    authors = project_config["authors"]
    
    if not authors:
        raise ValueError("No authors configured in project configuration")
    
    names = []
    for author in authors:
        if 'name' not in author:
            raise ValueError("Author name missing from author configuration")
        names.append(author['name'])
    
    return names


def get_author_for_section(section_name: str, project_config: Optional[Dict[str, Any]] = None) -> str:
    """Get appropriate author name for a report section.
    
    Args:
        section_name: Name of the report section
        project_config: Optional project configuration dictionary
        sync_files: Whether to sync configuration files
        
    Returns:
        Author name for the section
    """
    consultant_names = get_consultant_names(project_config)
    
    # For now, return the first consultant as the main author
    # This could be expanded with section-specific author mapping
    return consultant_names[0] if consultant_names else "Unknown Author"
