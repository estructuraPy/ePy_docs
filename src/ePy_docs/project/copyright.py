"""Copyright and authorship information generator for ePy_suite reports.

Handles copyright notices, company information, and authorship details
for professional reports and documentation.
"""

from typing import Dict, Any

from ePy_docs.project.setup import load_setup_config
from ePy_docs.components.text import TextFormatter


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
