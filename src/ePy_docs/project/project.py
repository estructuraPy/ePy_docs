from dataclasses import dataclass

@dataclass
class ProjectPaths:
    """Data class to hold all project file paths.
    
    Assumptions:
        All file paths are configured through proper initialization
        No default values are provided to prevent result bias
    """
    soil_json: str
    units_json: str
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
    units_config: str
    design_codes: str
    structure_config: str
