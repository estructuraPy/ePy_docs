"""Directory and Path Configuration Manager

This module provides a centralized configuration system for managing
project directories and file paths in the rigid block foundation analysis.
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Optional, Any, List, Union
from dataclasses import dataclass
from pydantic import BaseModel, Field, validator
from ePy_docs.files.data import _load_cached_json

try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    tk = None
    filedialog = None

try:
    from IPython import get_ipython
except ImportError:
    get_ipython = None

_CONFIG_CACHE = {}


def _load_setup_config(sync_json: bool = True) -> Dict[str, Any]:
    """Load configuration from setup.json file with sync support.
    
    Args:
        sync_json: Whether to synchronize from source before loading.
        
    Returns:
        Dictionary containing setup configuration data.
        
    Raises:
        FileNotFoundError: If setup configuration file not found.
    """
    setup_path = Path(__file__).parent / "setup.json"
    if not setup_path.exists():
        raise FileNotFoundError(f"Setup configuration file not found: {setup_path}")
    
    # If sync_json is True, we should reload from disk
    cache_key = f"setup_config_{sync_json}"
    
    if not sync_json and cache_key in _CONFIG_CACHE:
        return _CONFIG_CACHE[cache_key]
    
    with open(setup_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    _CONFIG_CACHE[cache_key] = config
    return config


@dataclass
class ProjectFolders:
    """Data class for project folder paths."""
    config: str
    data: str
    results: str
    brand: str
    templates: str
    exports: str

@dataclass
class ProjectConfigPaths:
    """Data class for project configuration file paths."""
    project_json: str

@dataclass
class UnitsConfigPaths:
    """Data class for units configuration file paths."""
    units_json: str
    aliases_json: str
    conversion_json: str
    prefix_json: str

@dataclass
class FoundationsConfigPaths:
    """Data class for foundations configuration file paths."""
    soil_json: str
    foundations_json: str
    design_codes_json: str

@dataclass
class AnalysisConfigPaths:
    """Data class for analysis configuration file paths."""
    rebar_json: str
    mapper_json: str
    combos_cscr2014_json: str
    combos_cscr2025_json: str

@dataclass
class StylingConfigPaths:
    """Data class for styling configuration file paths."""
    colors_json: str
    styles_json: str

@dataclass
class WriterConfigPaths:
    """Data class for writer configuration file paths."""
    tables_json: str
    quarto_json: str
    categories_json: str

@dataclass
class ConfigurationPaths:
    """Data class for all configuration file paths organized by theme."""
    project: ProjectConfigPaths
    units: UnitsConfigPaths
    foundations: FoundationsConfigPaths
    analysis: AnalysisConfigPaths
    styling: StylingConfigPaths
    writer: WriterConfigPaths
    
    # Backward compatibility properties
    @property
    def soil_json(self) -> str:
        return self.foundations.soil_json
    
    @property
    def units_json(self) -> str:
        return self.units.units_json
    
    @property
    def project_json(self) -> str:
        return self.project.project_json
    
    @property
    def foundations_json(self) -> str:
        return self.foundations.foundations_json
    
    @property
    def design_codes_json(self) -> str:
        return self.foundations.design_codes_json
    
    @property
    def colors_json(self) -> str:
        return self.styling.colors_json
    
    @property
    def styles_json(self) -> str:
        return self.styling.styles_json
    
    @property
    def aliases_json(self) -> str:
        return self.units.aliases_json
    
    @property
    def conversion_json(self) -> str:
        return self.units.conversion_json
    
    @property
    def prefix_json(self) -> str:
        return self.units.prefix_json
    
    @property
    def rebar_json(self) -> str:
        return self.analysis.rebar_json
    
    @property
    def mapper_json(self) -> str:
        return self.analysis.mapper_json
    
    @property
    def combos_cscr2014_json(self) -> str:
        return self.analysis.combos_cscr2014_json
    
    @property
    def combos_cscr2025_json(self) -> str:
        return self.analysis.combos_cscr2025_json
    
    @property
    def tables_json(self) -> str:
        return self.writer.tables_json
    
    @property
    def quarto_json(self) -> str:
        return self.writer.quarto_json

@dataclass
class StructuralDataPaths:
    """Data class for structural input data file paths."""
    blocks_csv: str
    nodes_csv: str

@dataclass
class AnalysisDataPaths:
    """Data class for analysis input data file paths."""
    reactions_csv: str
    combinations_csv: str

@dataclass
class DataPaths:
    """Data class for all input data file paths organized by theme."""
    structural: StructuralDataPaths
    analysis: AnalysisDataPaths
    
    # Backward compatibility properties
    @property
    def blocks_csv(self) -> str:
        return self.structural.blocks_csv
    
    @property
    def nodes_csv(self) -> str:
        return self.structural.nodes_csv
    
    @property
    def reactions_csv(self) -> str:
        return self.analysis.reactions_csv
    
    @property
    def combinations_csv(self) -> str:
        return self.analysis.combinations_csv

@dataclass
class ReportOutputPaths:
    """Data class for report output file paths."""
    report_md: str

@dataclass
class GraphicsOutputPaths:
    """Data class for graphics output file paths."""
    watermark_png: str

@dataclass
class OutputPaths:
    """Data class for all output file paths organized by theme."""
    reports: ReportOutputPaths
    graphics: GraphicsOutputPaths
    
    # Backward compatibility properties
    @property
    def report_md(self) -> str:
        return self.reports.report_md
    
    @property
    def watermark_png(self) -> str:
        return self.graphics.watermark_png

@dataclass
class ProjectPaths:
    """Combined data class for all project file paths."""
    configuration: ConfigurationPaths
    data: DataPaths
    output: OutputPaths
    
    # Backward compatibility properties
    @property
    def soil_json(self) -> str:
        return self.configuration.soil_json
    
    @property
    def units_json(self) -> str:
        return self.configuration.units_json
    
    @property
    def project_json(self) -> str:
        return self.configuration.project_json
    
    @property
    def foundations_json(self) -> str:
        return self.configuration.foundations_json
    
    @property
    def design_codes_json(self) -> str:
        return self.configuration.design_codes_json
    
    @property
    def blocks_csv(self) -> str:
        return self.data.blocks_csv
    
    @property
    def nodes_csv(self) -> str:
        return self.data.nodes_csv
    
    @property
    def reactions_csv(self) -> str:
        return self.data.reactions_csv
    
    @property
    def combinations_csv(self) -> str:
        return self.data.combinations_csv
    
    @property
    def report_md(self) -> str:
        return self.output.report_md
    
    @property
    def watermark_png(self) -> str:
        return self.output.watermark_png

class DirectoryManager(BaseModel):
    """Class to manage directory operations.
    
    Assumptions:
        Base directory is properly configured for all operations
        File system permissions allow directory creation and file access
    """

    base_directory: Optional[str] = Field(None, description="Base directory for operations")

    def get_current_directory(self) -> str:
        """Get the current working directory.
        
        Returns:
            Current working directory path
            
        Assumptions:
            Operating system provides valid current directory information
        """
        return os.getcwd()

    def is_jupyter_notebook(self) -> bool:
        """Check if the code is running in a Jupyter notebook.
        
        Returns:
            True if running in Jupyter notebook, False otherwise
            
        Assumptions:
            IPython kernel detection is sufficient for notebook identification
        """
        try:
            if get_ipython is not None:
                ipython = get_ipython()
                if ipython is not None and "IPKernelApp" in ipython.config:
                    return True
            return False
        except ImportError:
            return False

    def get_notebook_directory(self) -> str:
        """Get the directory of the current Jupyter notebook.
        
        Returns:
            Directory path of the current notebook or current working directory
            
        Assumptions:
            Notebook files have .ipynb extension
            IPython kernel provides accessible information
        """
        if self.is_jupyter_notebook():
            try:
                if get_ipython is not None:
                    ipython = get_ipython()
                    if hasattr(ipython, 'user_ns') and 'get_ipython' in ipython.user_ns:
                        kernel_info = ipython.kernel.info
                    if 'argv' in kernel_info and len(kernel_info['argv']) > 0:
                        notebook_path = kernel_info['argv'][0]
                        if os.path.isfile(notebook_path):
                            return os.path.dirname(os.path.abspath(notebook_path))
                
                cwd = os.getcwd()
                if any(f.endswith('.ipynb') for f in os.listdir(cwd)):
                    return cwd
            except Exception:
                pass
        return self.get_current_directory()

    def request_directory_dialog(self) -> str:
        """Open a dialog for the user to select a directory.
        
        Returns:
            Selected directory path or current directory if cancelled
            
        Assumptions:
            GUI environment is available for dialog display
            User interaction is possible
        """
        if tk is None or filedialog is None:
            raise ImportError("tkinter is not available for directory selection")
        
        root = tk.Tk()
        root.withdraw()
        directory = filedialog.askdirectory(title="Select Directory")
        root.destroy()
        return directory if directory else self.get_current_directory()

    def ensure_directory_exists(self, directory: Optional[str] = None) -> str:
        """Ensure that a directory exists, creating it if necessary.
        
        Args:
            directory: Directory path to ensure exists, uses base_directory if None
            
        Returns:
            Path to the ensured directory
            
        Assumptions:
            File system permissions allow directory creation
            Parent directories can be created if needed
        """
        target_dir = directory or self.base_directory or self.get_current_directory()
        os.makedirs(target_dir, exist_ok=True)
        return target_dir

    def list_directory_contents(self, directory: Optional[str] = None) -> List[str]:
        """List the contents of a directory.
        
        Args:
            directory: Directory to list, uses base_directory if None
            
        Returns:
            List of file and directory names in the target directory
            
        Assumptions:
            Directory exists and is accessible
            Directory permissions allow listing contents
        """
        target_dir = directory or self.base_directory or self.get_current_directory()
        if os.path.isdir(target_dir):
            return os.listdir(target_dir)
        return []

    def get_absolute_path(self, relative_path: str) -> str:
        """Convert a relative path to an absolute path.
        
        Args:
            relative_path: Relative path to convert
            
        Returns:
            Absolute path string
            
        Assumptions:
            Input path is properly formatted for the operating system
        """
        return os.path.abspath(relative_path)
    
    def join_path(self, base_path: Optional[str] = None, *subpaths) -> str:
        """Join a base path with one or more subpaths.
        
        Args:
            base_path: Base path, uses base_directory if None
            *subpaths: Variable number of subpath components
            
        Returns:
            Joined path string
            
        Assumptions:
            All path components are valid for the operating system
        """
        base = base_path or self.base_directory or self.get_current_directory()
        return os.path.join(base, *subpaths)
    
    def create_file_path(self, filename: str, directory: Optional[str] = None) -> str:
        """Create a complete file path by combining a directory and filename.
        
        Args:
            filename: Name of the file
            directory: Directory path, uses base_directory if None
            
        Returns:
            Complete file path
            
        Assumptions:
            Filename is valid for the target file system
        """
        target_dir = directory or self.base_directory or self.get_current_directory()
        return os.path.join(target_dir, filename)

    def write_file(self, filename: str, content: Union[str, dict, List[List[Any]]], 
                  directory: Optional[str] = None, **kwargs) -> str:
        """Write content to a file using WriteFiles class.
        
        Args:
            filename: Name of the file to create
            content: Content to write (string, dict, or list of lists)
            directory: Target directory, uses base_directory if None
            **kwargs: Additional arguments for file writing
            
        Returns:
            Path to the created file
            
        Assumptions:
            WriteFiles class is available and functional
            File format is determined by filename extension
        """
        from ePy_docs.core.base import WriteFiles
    
        file_path = self.create_file_path(filename, directory)
        writer = WriteFiles(file_path=file_path)
    
        return writer.write_content(content, **kwargs)

class DirectoryConfigSettings(BaseModel):
    """Configuration settings for DirectoryConfig initialization."""
    
    base_dir: Optional[str] = Field(None, description="Base directory for the project")
    json_templates: bool = Field(False, description="Whether to sync JSON configuration files from library")
    auto_create_dirs: bool = Field(False, description="Whether to automatically create project directories")
    validate_on_init: bool = Field(False, description="Whether to validate file structure on initialization")
    
    class Config:
        extra = "forbid"
        
    @validator('base_dir')
    def validate_base_dir(cls, v):
        """Validate base directory path."""
        if v is not None:
            if not isinstance(v, str):
                raise ValueError("base_dir must be a string")
            v = os.path.abspath(v)
        return v
    
    @validator('json_templates', 'auto_create_dirs', 'validate_on_init')
    def validate_booleans(cls, v):
        """Validate boolean fields."""
        if not isinstance(v, bool):
            raise ValueError("Must be a boolean value")
        return v

class DirectoryConfig(BaseModel):
    """Centralized configuration manager for project directories and paths."""
    
    base_dir: str = Field(..., description="Base directory for the project")
    folders: ProjectFolders = Field(default_factory=ProjectFolders, description="Project folder paths")
    files: ProjectPaths = Field(default_factory=ProjectPaths, description="Project file paths")
    settings: DirectoryConfigSettings = Field(default_factory=DirectoryConfigSettings, description="Configuration settings")
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, settings: Optional[DirectoryConfigSettings] = None, **data):
        """Initialize the directory configuration.
        
        Args:
            settings: DirectoryConfigSettings instance with all configuration
            **data: Additional data for Pydantic initialization
        """
        if settings is None:
            settings = DirectoryConfigSettings()
        
        final_base_dir = settings.base_dir or self._detect_base_directory()
        
        data.update({
            'base_dir': final_base_dir,
            'folders': self._create_project_folders(),
            'files': self._create_project_paths(),
            'settings': settings
        })
        
        super().__init__(**data)
        
        self._setup_directories(settings.json_templates)
        self._setup_file_paths(settings.json_templates)
        
        # Auto-create directories if requested
        if settings.auto_create_dirs:
            self.create_directories()
        
        # Only sync JSON templates if explicitly requested
        if settings.json_templates:
            self.sync_templates_from_library()
        
        # Validate structure if requested
        if settings.validate_on_init:
            validation = self.validate_structure()
            if not all(validation.values()):
                missing = [k for k, v in validation.items() if not v]
                raise RuntimeError(f"Missing directories: {missing}")

    @classmethod
    def from_settings(cls, settings: DirectoryConfigSettings) -> 'DirectoryConfig':
        """Create DirectoryConfig from DirectoryConfigSettings.
        
        Args:
            settings: Configuration settings
            
        Returns:
            Configured DirectoryConfig instance
        """
        return cls(settings=settings)
    
    @classmethod
    def with_json_sync(cls, base_dir: Optional[str] = None) -> 'DirectoryConfig':
        """Create DirectoryConfig with JSON synchronization enabled.
        
        Args:
            base_dir: Base directory path
            
        Returns:
            DirectoryConfig with JSON sync enabled
        """
        settings = DirectoryConfigSettings(
            base_dir=base_dir,
            json_templates=True
        )
        config = cls.from_settings(settings)
        # Set this config as the current project config
        set_current_project_config(config)
        return config
    
    @classmethod
    def minimal(cls, base_dir: Optional[str] = None) -> 'DirectoryConfig':
        """Create minimal DirectoryConfig without any synchronization.
        
        Args:
            base_dir: Base directory path
            
        Returns:
            Minimal DirectoryConfig instance
        """
        settings = DirectoryConfigSettings(
            base_dir=base_dir,
            json_templates=False,
            auto_create_dirs=False
        )
        return cls.from_settings(settings)

    @classmethod
    def full_setup(cls, base_dir: Optional[str] = None) -> 'DirectoryConfig':
        """Create DirectoryConfig with full setup (JSON sync + auto-create dirs).
        
        Args:
            base_dir: Base directory path
            
        Returns:
            Fully configured DirectoryConfig instance
        """
        settings = DirectoryConfigSettings(
            base_dir=base_dir,
            json_templates=True,
            auto_create_dirs=True,
            validate_on_init=True
        )
        return cls.from_settings(settings)

    @staticmethod
    def _detect_base_directory() -> str:
        """Detect the base directory based on execution context.
        
        Returns:
            Base directory path
            
        Assumptions:
            Current working directory is appropriate for project setup
        """
        return os.getcwd()
    
    @staticmethod
    def _create_project_folders() -> ProjectFolders:
        """Create ProjectFolders instance with proper initialization.
        
        Returns:
            Configured ProjectFolders instance
            
        Assumptions:
            Base directory is properly set before calling this method
        """
        return ProjectFolders(
            config="",
            data="",
            results="",
            brand="",
            templates="",
            exports=""
        )
    
    @staticmethod
    def _create_project_paths() -> ProjectPaths:
        """Create ProjectPaths instance with proper initialization.
        
        Returns:
            Configured ProjectPaths instance
            
        Assumptions:
            Folder structure will be configured before file paths are set
        """
        # Create empty project configuration paths
        project_config = ProjectConfigPaths(project_json="")
        
        # Create empty units configuration paths
        units_config = UnitsConfigPaths(
            units_json="",
            aliases_json="",
            conversion_json="",
            prefix_json=""
        )
        
        # Create empty foundations configuration paths
        foundations_config = FoundationsConfigPaths(
            soil_json="",
            foundations_json="",
            design_codes_json=""
        )
        
        # Create empty analysis configuration paths
        analysis_config = AnalysisConfigPaths(
            rebar_json="",
            mapper_json="",
            combos_cscr2014_json="",
            combos_cscr2025_json=""
        )
        
        # Create empty styling configuration paths
        styling_config = StylingConfigPaths(
            colors_json="",
            styles_json=""
        )
        
        # Create empty writer configuration paths
        writer_config = WriterConfigPaths(
            tables_json="",
            quarto_json="",
            categories_json=""
        )
        
        # Create empty configuration paths
        config_paths = ConfigurationPaths(
            project=project_config,
            units=units_config,
            foundations=foundations_config,
            analysis=analysis_config,
            styling=styling_config,
            writer=writer_config
        )
        
        # Create empty structural data paths
        structural_data = StructuralDataPaths(
            blocks_csv="",
            nodes_csv=""
        )
        
        # Create empty analysis data paths
        analysis_data = AnalysisDataPaths(
            reactions_csv="",
            combinations_csv=""
        )
        
        # Create empty data paths
        data_paths = DataPaths(
            structural=structural_data,
            analysis=analysis_data
        )
        
        # Create empty report output paths
        report_output = ReportOutputPaths(report_md="")
        
        # Create empty graphics output paths
        graphics_output = GraphicsOutputPaths(watermark_png="")
        
        # Create empty output paths
        output_paths = OutputPaths(
            reports=report_output,
            graphics=graphics_output
        )
        
        return ProjectPaths(
            configuration=config_paths,
            data=data_paths,
            output=output_paths
        )
    
    def _setup_directories(self, sync_json: bool = True) -> None:
        """Setup all project directories using setup.json configuration."""
        config = _load_setup_config(sync_json)
        directories = config['directories']
        
        self.folders.config = os.path.join(self.base_dir, directories['config'])
        self.folders.data = os.path.join(self.base_dir, directories['data'])
        self.folders.results = os.path.join(self.base_dir, directories['results'])
        self.folders.brand = os.path.join(self.base_dir, directories['brand'])
        self.folders.templates = os.path.join(self.base_dir, directories['templates'])
        self.folders.exports = os.path.join(self.base_dir, directories['exports'])

    def _setup_file_paths(self, sync_json: bool = True) -> None:
        """Setup all project file paths using setup.json configuration."""
        config = _load_setup_config(sync_json)
        files_config = config['files']
        
        # Configuration files
        if self.settings.json_templates:
            # Use local configuration directory
            config_base = self.folders.config
        else:
            # Use package directory
            config_base = self._get_library_templates_path()
        
        # Project configuration files
        project_config = files_config['configuration']['project']
        for key, value in project_config.items():
            setattr(self.files.configuration.project, key, os.path.join(config_base, value))
        
        # Units configuration files
        units_config = files_config['configuration']['units']
        for key, value in units_config.items():
            setattr(self.files.configuration.units, key, os.path.join(config_base, value))
        
        # Foundations configuration files (dynamic)
        if 'foundations' in files_config['configuration']:
            foundations_config = files_config['configuration']['foundations']
            for key, value in foundations_config.items():
                setattr(self.files.configuration.foundations, key, os.path.join(config_base, value))
        
        # Analysis configuration files (dynamic)
        if 'analysis' in files_config['configuration']:
            analysis_config = files_config['configuration']['analysis']
            for key, value in analysis_config.items():
                setattr(self.files.configuration.analysis, key, os.path.join(config_base, value))
        
        # Styling configuration files
        styling_config = files_config['configuration']['styling']
        for key, value in styling_config.items():
            setattr(self.files.configuration.styling, key, os.path.join(config_base, value))
        
        # Writer configuration files (dynamic)
        if 'writer' in files_config['configuration']:
            writer_config = files_config['configuration']['writer']
            for key, value in writer_config.items():
                setattr(self.files.configuration.writer, key, os.path.join(config_base, value))
        
        # Data files - always in data directory
        input_data_config = files_config['input_data']
        
        # Process each category of input data dynamically
        for category, files_dict in input_data_config.items():
            category_obj = getattr(self.files.data, category)
            for key, value in files_dict.items():
                setattr(category_obj, key, os.path.join(self.folders.data, value))
        
        # Output files
        output_files_config = files_config['output_files']
        
        # Process each category of output files dynamically
        for category, files_dict in output_files_config.items():
            if category == 'reports':
                target_folder = self.folders.results
                category_obj = self.files.output.reports
            elif category == 'graphics':
                target_folder = self.folders.brand
                category_obj = self.files.output.graphics
            else:
                continue
                
            for key, value in files_dict.items():
                setattr(category_obj, key, os.path.join(target_folder, value))

    def create_directories(self) -> None:
        """Create all project directories if they don't exist.
        
        Assumptions:
            File system permissions allow directory creation
        """
        # Only create essential directories
        essential_folders = [
            self.folders.data, 
            self.folders.results
        ]
        
        for folder in essential_folders:
            os.makedirs(folder, exist_ok=True)
        
        # Create configuration directory only if JSON sync is active
        if self.settings.json_templates:
            os.makedirs(self.folders.config, exist_ok=True)
    
    def get_folders_dict(self) -> Dict[str, str]:
        """Get all folders as a dictionary.
        
        Returns:
            Dictionary mapping folder names to their paths
            
        Assumptions:
            Folder structure has been properly initialized
        """
        folders_dict = {
            'data': self.folders.data,
            'results': self.folders.results,
            'exports': self.folders.exports,
            'brand': self.folders.brand
        }
        
        # Only include configuration folder if JSON sync is active
        if self.settings.json_templates:
            folders_dict['configuration'] = self.folders.config
        
        # Keep templates for backward compatibility but don't create it
        folders_dict['templates'] = self.folders.templates
        
        return folders_dict

    def get_files_dict(self) -> Dict[str, str]:
        """Get all file paths as a dictionary organized by category.
        
        Returns:
            Dictionary mapping file keys to their paths organized by category
        """
        return {
            'configuration': {
                'project': {
                    'project_json': self.files.configuration.project_json
                },
                'units': {
                    'units_json': self.files.configuration.units_json,
                    'aliases_json': self.files.configuration.aliases_json,
                    'conversion_json': self.files.configuration.conversion_json,
                    'prefix_json': self.files.configuration.prefix_json
                },
                'foundations': {
                    'soil_json': self.files.configuration.soil_json,
                    'foundations_json': self.files.configuration.foundations_json,
                    'design_codes_json': self.files.configuration.design_codes_json
                },
                'analysis': {
                    'rebar_json': self.files.configuration.rebar_json,
                    'mapper_json': self.files.configuration.mapper_json,
                    'combos_cscr2014_json': self.files.configuration.combos_cscr2014_json,
                    'combos_cscr2025_json': self.files.configuration.combos_cscr2025_json
                },
                'styling': {
                    'colors_json': self.files.configuration.colors_json,
                    'styles_json': self.files.configuration.styles_json
                },
                'writer': {
                    'tables_json': self.files.configuration.tables_json,
                    'quarto_json': self.files.configuration.quarto_json
                }
            },
            'input_data': {
                'structural': {
                    'blocks_csv': self.files.data.blocks_csv,
                    'nodes_csv': self.files.data.nodes_csv
                },
                'analysis': {
                    'reactions_csv': self.files.data.reactions_csv,
                    'combinations_csv': self.files.data.combinations_csv
                }
            },
            'output_files': {
                'reports': {
                    'report_md': self.files.output.report_md
                },
                'graphics': {
                    'watermark_png': self.files.output.watermark_png
                }
            }
        }
    
    def _get_library_templates_path(self) -> str:
        """Get the path to the library's templates folder."""
        try:
            # Direct package import approach
            import ePy_docs
            package_path = os.path.dirname(ePy_docs.__file__)
            return package_path  # Templates are directly in the package
                
        except Exception as e:
            raise RuntimeError(f"Error finding package path: {e}")

    def sync_templates_from_library(self) -> None:
        """Synchronize ALL JSON templates from the library package to user's configuration folder."""
        package_source_dir = self._get_library_templates_path()
        
        if not os.path.exists(package_source_dir):
            raise FileNotFoundError(f"Package source directory not found: {package_source_dir}")
        
        # Create configuration directory since we're syncing
        base_config_dir = self.folders.config
        os.makedirs(base_config_dir, exist_ok=True)
        copied_files = []
        updated_files = []
        
        # Discover ALL JSON files in the package
        discovered_files = self._discover_all_json_files(package_source_dir)
        
        for source_path, relative_path in discovered_files.items():
            target_file = os.path.join(base_config_dir, relative_path)
            
            # Create target directory if it doesn't exist
            target_dir = os.path.dirname(target_file)
            os.makedirs(target_dir, exist_ok=True)
            
            # Copy or update file
            try:
                import shutil
                
                if not os.path.exists(target_file):
                    # File doesn't exist, copy it
                    shutil.copy2(source_path, target_file)
                    copied_files.append(relative_path)
                elif os.path.getmtime(source_path) > os.path.getmtime(target_file):
                    # Source is newer, update it
                    shutil.copy2(source_path, target_file)
                    updated_files.append(relative_path)
                    
            except Exception as e:
                raise RuntimeError(f"Error processing {relative_path}: {e}")
        
        # Return summary without printing
        return {
            'copied_files': copied_files,
            'updated_files': updated_files,
            'total_processed': len(copied_files) + len(updated_files)
        }
    
    def _discover_all_json_files(self, source_dir: str) -> Dict[str, str]:
        """Discover all JSON files in the source directory.
        
        Args:
            source_dir: Directory to search for JSON files
            
        Returns:
            Dictionary mapping absolute source paths to relative target paths
        """
        discovered = {}
        source_path = Path(source_dir)
        
        # Find all JSON files
        for json_file in source_path.rglob("*.json"):
            # Skip files in configuration directories to avoid circular copying
            if "configuration" in str(json_file):
                continue
                
            # Get relative path from the library's ePy_docs directory
            try:
                # Find the last occurrence of ePy_docs (the library directory, not project directory)
                parts = json_file.parts
                epy_docs_index = None
                
                # Look for src/ePy_docs pattern specifically
                for i in range(len(parts) - 1):
                    if parts[i] == "src" and parts[i + 1] == "ePy_docs":
                        epy_docs_index = i + 1  # Point to ePy_docs after src
                        break
                
                if epy_docs_index is not None:
                    # Get path relative to the library's ePy_docs directory
                    # Skip the ePy_docs part to get the clean relative path
                    relative_parts = parts[epy_docs_index + 1:]
                    if relative_parts:  # Only process if there are parts after ePy_docs
                        relative_path = str(Path(*relative_parts))
                        discovered[str(json_file)] = relative_path
                    
            except Exception as e:
                continue
        
        return discovered

    def validate_required_files(self, required_files: Optional[Dict[str, str]] = None) -> Dict[str, bool]:
        """Validate that specified files exist.
        
        Args:
            required_files: Dictionary mapping file keys to file paths.
                          If None, validates both configuration and data files.
        
        Returns:
            Dictionary with validation results for required files.
            
        Raises:
            FileNotFoundError: If any required file is missing
            
        Assumptions:
            File system access is available for existence checks
        """
        validation = {}
        
        if required_files:
            for file_key, file_path in required_files.items():
                validation[f"required_{file_key}"] = os.path.exists(file_path)
        
        # Dynamically validate configuration files based on what's actually configured
        config_sections = {
            'project': self.files.configuration.project,
            'units': self.files.configuration.units,
            'foundations': self.files.configuration.foundations,
            'analysis': self.files.configuration.analysis,
            'styling': self.files.configuration.styling,
            'writer': self.files.configuration.writer
        }
        
        for section_name, section_obj in config_sections.items():
            for attr_name in dir(section_obj):
                if not attr_name.startswith('_') and hasattr(section_obj, attr_name):
                    file_path = getattr(section_obj, attr_name)
                    if isinstance(file_path, str) and file_path.endswith('.json'):
                        validation[f"config_{attr_name}"] = os.path.exists(file_path)
        
        # Dynamically validate data files based on what's actually configured
        data_sections = {
            'structural': self.files.data.structural,
            'analysis': self.files.data.analysis
        }
        
        for section_name, section_obj in data_sections.items():
            for attr_name in dir(section_obj):
                if not attr_name.startswith('_') and hasattr(section_obj, attr_name):
                    file_path = getattr(section_obj, attr_name)
                    if isinstance(file_path, str):
                        validation[f"data_{attr_name}"] = os.path.exists(file_path)
        
        return validation
    
    def create_default_configs(self, force_sync: bool = False) -> None:
        """Ensure default configuration files exist by syncing from library templates."""
        if force_sync or not self.settings.json_templates:
            self.settings.json_templates = True
            self._setup_file_paths(self.settings.json_templates)
            self.sync_templates_from_library()
        else:
            # Check if any configuration files exist dynamically
            config_files = []
            
            # Collect all configuration file paths dynamically
            for section_name, section_obj in [
                ('project', self.files.configuration.project),
                ('units', self.files.configuration.units),
                ('styling', self.files.configuration.styling),
                ('writer', self.files.configuration.writer)
            ]:
                for attr_name in dir(section_obj):
                    if not attr_name.startswith('_') and hasattr(section_obj, attr_name):
                        file_path = getattr(section_obj, attr_name)
                        if isinstance(file_path, str) and file_path.endswith('.json'):
                            config_files.append(file_path)
            
            missing_configs = [f for f in config_files if not os.path.exists(f)]
            
            if missing_configs:
                self.sync_templates_from_library()

    def setup_project(self, sync_json: Optional[bool] = None, auto_sync_missing: bool = False) -> Dict[str, Any]:
        """Complete project setup: create directories, optionally sync templates, and validate."""
        final_sync_json = sync_json if sync_json is not None else self.settings.json_templates
        
        # If sync_json=True is explicitly requested, enable json_templates automatically
        if sync_json is True:
            self.settings.json_templates = True
            # Reconfigure file paths to use local config directory
            self._setup_file_paths(self.settings.json_templates)
        
        # Set this config as the current project config
        set_current_project_config(self)
        
        # Always create basic directories
        self.create_directories()
        
        # Only sync if explicitly requested or if it's True in settings
        if final_sync_json:
            self.sync_templates_from_library()
        
        validation = self.validate_required_files()
        folder_validation = self.validate_structure()
        
        missing_configs = [
            key.replace('config_', '') 
            for key, exists in validation.items() 
            if key.startswith('config_') and not exists
        ]
        
        setup_result = {
            'directories_created': True,
            'json_synced': final_sync_json,
            'configuration_directory_created': self.settings.json_templates,
            'missing_config_files': missing_configs,
            'validation': validation,
            'folder_validation': folder_validation,
            'settings': self.settings.dict()
        }
        
        if missing_configs:
            if not final_sync_json:
                raise RuntimeError(f"Missing configuration files: {', '.join(missing_configs)}. Set sync_json=True to create them.")
            else:
                raise FileNotFoundError(f"Missing configuration files after sync: {', '.join(missing_configs)}")
        
        return setup_result

    @classmethod
    def smart_setup(cls, base_dir: Optional[str] = None, auto_sync: bool = True) -> 'DirectoryConfig':
        """Create DirectoryConfig with intelligent setup that auto-detects missing files."""
        # Start with JSON sync enabled for smart setup
        settings = DirectoryConfigSettings(
            base_dir=base_dir,
            json_templates=True,  # Enable sync for smart setup
            auto_create_dirs=True,
            validate_on_init=False
        )
        
        config = cls.from_settings(settings)
        
        if auto_sync:
            config.sync_templates_from_library()
        
        return config
    
    @classmethod
    def with_json_sync(cls, base_dir: Optional[str] = None) -> 'DirectoryConfig':
        """Create DirectoryConfig with JSON synchronization enabled."""
        settings = DirectoryConfigSettings(
            base_dir=base_dir,
            json_templates=True,
            auto_create_dirs=True  # Also create directories
        )
        config = cls.from_settings(settings)
        # Set this config as the current project config
        set_current_project_config(config)
        return config

    def enable_json_sync(self) -> None:
        """Enable JSON synchronization and update file paths."""
        self.settings.json_templates = True
        self._setup_file_paths(self.settings.json_templates)
        self.sync_templates_from_library()

    def force_sync_now(self) -> Dict[str, Any]:
        """Force synchronization of JSON templates regardless of current settings."""
        # Temporarily enable sync
        original_setting = self.settings.json_templates
        self.settings.json_templates = True
        self._setup_file_paths(self.settings.json_templates)
        
        # Create configuration directory and sync
        os.makedirs(self.folders.config, exist_ok=True)
        self.sync_templates_from_library()
        
        # Validate results
        validation = self.validate_required_files()
        missing_configs = [
            key.replace('config_', '') 
            for key, exists in validation.items() 
            if key.startswith('config_') and not exists
        ]
        
        result = {
            'sync_forced': True,
            'json_templates_enabled': self.settings.json_templates,
            'missing_files': missing_configs,
            'success': len(missing_configs) == 0
        }
        
        if not result['success']:
            raise FileNotFoundError(f"Missing configuration files after sync: {missing_configs}")
        
        return result

    def validate_structure(self) -> Dict[str, bool]:
        """Validate that all directories exist.
        
        Returns:
            Dictionary with validation results for each component
            
        Assumptions:
            Directory structure has been properly configured
        """
        validation = {}
        
        # Always validate essential folders
        essential_folders = {
            'data': self.folders.data,
            'results': self.folders.results
        }
        
        for name, path in essential_folders.items():
            validation[f"folder_{name}"] = os.path.exists(path)
        
        # Only validate configuration folder if JSON sync is active
        if self.settings.json_templates:
            validation[f"folder_configuration"] = os.path.exists(self.folders.config)
        
        return validation

    def __str__(self) -> str:
        """String representation of the configuration.
        
        Returns:
            String representation showing base directory.
        """
        return f"DirectoryConfig(base_dir='{self.base_dir}')"
    
    def __repr__(self) -> str:
        """Detailed representation of the configuration.
        
        Returns:
            Detailed string representation with folder and file counts.
        """
        return (f"DirectoryConfig(base_dir='{self.base_dir}', "
                f"folders={len(self.get_folders_dict())}, "
                f"files={len(self.get_files_dict())})")
    
    def load_config_file(self, config_type: str) -> Dict[str, Any]:
        """Load configuration file using the project configuration system.
        
        Args:
            config_type: Type of configuration to load
            
        Returns:
            Dictionary containing configuration data
            
        Raises:
            ValueError: If config type is unknown
            FileNotFoundError: If configuration file doesn't exist
            RuntimeError: If file cannot be loaded
        """
        # Import here to avoid circular dependency
        from ePy_docs.files.reader import ReadFiles
        
        # Dynamically build config paths from configuration sections
        config_paths = {}
        
        # Check all configuration sections for JSON files
        for section_name, section_obj in [
            ('project', self.files.configuration.project),
            ('units', self.files.configuration.units),
            ('analysis', self.files.configuration.analysis),
            ('styling', self.files.configuration.styling),
            ('writer', self.files.configuration.writer)
        ]:
            for attr_name in dir(section_obj):
                if not attr_name.startswith('_') and hasattr(section_obj, attr_name):
                    file_path = getattr(section_obj, attr_name)
                    if isinstance(file_path, str) and file_path.endswith('.json'):
                        # Create config type name from attribute (remove _json suffix)
                        config_type_name = attr_name.replace('_json', '')
                        config_paths[config_type_name] = file_path
        
        file_path = config_paths.get(config_type)
        if not file_path:
            available_types = list(config_paths.keys())
            raise ValueError(f"No path configured for config type: {config_type}. Available types: {available_types}")
        
        # Check if the configured file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {config_type} at {file_path}")
        
        try:
            # Use cached loading for JSON files
            if file_path.endswith('.json'):
                config_data = _load_cached_json(file_path)
                if config_data is None:
                    raise ValueError(f"Empty JSON configuration: {config_type}")
            else:
                # Fallback to ReadFiles for non-JSON files
                reader = ReadFiles(file_path=file_path)
                
                if file_path.endswith('.csv'):
                    config_df = reader.load_csv()
                    if config_df is None or config_df.empty:
                        raise ValueError(f"Empty CSV configuration: {config_type}")
                    config_data = config_df.to_dict('records')
                else:
                    config_data = reader.load_json()
                    if config_data is None:
                        raise ValueError(f"Empty configuration: {config_type}")
            
            return config_data or {}
            
        except Exception as e:
            raise RuntimeError(f"Error loading {config_type} configuration from {file_path}: {e}")

    def load_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load all available configuration files dynamically.
        
        Returns:
            Dictionary containing all configuration data organized by type.
            
        Raises:
            FileNotFoundError: If any configuration file is missing
            RuntimeError: If any configuration file cannot be loaded
            
        Assumptions:
            Configuration files follow expected format and structure.
        """
        configs = {}
        
        # Dynamically discover all available configuration types
        available_config_types = []
        
        # Check all configuration sections for JSON files
        for section_name, section_obj in [
            ('project', self.files.configuration.project),
            ('units', self.files.configuration.units),
            ('analysis', self.files.configuration.analysis),
            ('styling', self.files.configuration.styling),
            ('writer', self.files.configuration.writer)
        ]:
            for attr_name in dir(section_obj):
                if not attr_name.startswith('_') and hasattr(section_obj, attr_name):
                    file_path = getattr(section_obj, attr_name)
                    if isinstance(file_path, str) and file_path.endswith('.json'):
                        # Create config type name from attribute (remove _json suffix)
                        config_type_name = attr_name.replace('_json', '')
                        available_config_types.append(config_type_name)
        
        # Load all available configurations
        for config_type in available_config_types:
            try:
                configs[config_type] = self.load_config_file(config_type)
            except (FileNotFoundError, ValueError) as e:
                # Skip configurations that don't exist or can't be loaded
                print(f"Warning: Could not load config '{config_type}': {e}")
                continue
        
        return configs

    def load_data_file(self, data_type: str, return_format: str = 'dataframe') -> Union[pd.DataFrame, List[List[Any]]]:
        """Load data file (CSV) using ReadFiles with proper error handling.
        
        Args:
            data_type: Type of data ('blocks', 'nodes', 'reactions', 'combinations').
            return_format: 'dataframe' or 'list' - format to return the data in.
            
        Returns:
            DataFrame or list of lists containing the data.
            
        Raises:
            ValueError: If data type is unknown or file is invalid.
            FileNotFoundError: If data file cannot be found.
            
        Assumptions:
            ReadFiles class can handle CSV file loading.
            Data files follow expected CSV format.
        """
        # Import here to avoid circular dependency
        from ePy_docs.files.reader import ReadFiles
        
        data_paths = {
            'blocks': self.files.blocks_csv,
            'nodes': self.files.nodes_csv,
            'reactions': self.files.reactions_csv,
            'combinations': self.files.combinations_csv
        }
        
        file_path = data_paths.get(data_type)
        if not file_path:
            raise ValueError(f"Unknown data type: {data_type}")
            
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found: {data_type} at {file_path}")
        
        reader = ReadFiles(file_path=file_path)
        df = reader.load_csv()
        
        if df is None:
            raise ValueError(f"ReadFiles returned None for {data_type}")
            
        if df.empty:
            raise ValueError(f"Data file is empty: {data_type}")
            
        if return_format == 'list':
            headers = df.columns.tolist()
            data_rows = df.values.tolist()
            result = [headers] + data_rows
            return result
        else:
            return df

# Public API functions for JSON synchronization
def sync_all_json_configs(base_dir: Optional[str] = None, force_update: bool = False) -> bool:
    """Synchronize all JSON configuration files from library to project.
    
    Args:
        base_dir: Base directory for the project. If None, auto-detects.
        force_update: If True, updates existing files even if they're newer.
        
    Returns:
        True if synchronization was successful, False otherwise.
    
    """
    try:
        settings = DirectoryConfigSettings(
            base_dir=base_dir,
            json_templates=True,
            auto_create_dirs=True
        )
        
        config = DirectoryConfig.from_settings(settings)
        config.sync_templates_from_library()
        
        return True
        
    except Exception as e:
        raise RuntimeError(f"Error during JSON synchronization: {e}")


def discover_available_json_configs() -> Dict[str, str]:
    """Discover all available JSON configuration files in the library.
    
    Returns:
        Dictionary mapping relative paths to absolute source paths.
        
    Raises:
        RuntimeError: If discovery fails
        
    """
    try:
        config = DirectoryConfig()
        package_source_dir = config._get_library_templates_path()
        
        if not os.path.exists(package_source_dir):
            raise FileNotFoundError(f"Library source directory not found: {package_source_dir}")
        
        discovered = config._discover_all_json_files(package_source_dir)
        
        return {v: k for k, v in discovered.items()}  # Reverse mapping
        
    except Exception as e:
        raise RuntimeError(f"Error discovering JSON configurations: {e}")


def force_sync_json_configs(base_dir: Optional[str] = None) -> bool:
    """Force synchronization of all JSON files, updating existing ones.
    
    Args:
        base_dir: Base directory for the project. If None, auto-detects.
        
    Returns:
        True if synchronization was successful, False otherwise.
        
    """
    try:
        # First discover what's available
        configs = discover_available_json_configs()
        
        if not configs:
            raise FileNotFoundError("No configurations found to sync")
        
        # Then sync them
        return sync_all_json_configs(base_dir, force_update=True)
        
    except Exception as e:
        raise RuntimeError(f"Error during force sync: {e}")

def load_setup_config(sync_json: bool = True) -> Dict[str, Any]:
    """Load configuration from setup.json file with sync support and fallback locations.
    
    Public interface to load setup configuration with synchronization control.
    Includes robust fallback logic to find setup.json in multiple locations.
    
    Args:
        sync_json: Whether to synchronize from source before loading.
        
    Returns:
        Dictionary containing setup configuration data.
        
    Raises:
        FileNotFoundError: If setup configuration file not found.
        RuntimeError: If configuration cannot be loaded.
    """
    try:
        # Try the primary location first
        return _load_setup_config(sync_json)
    except FileNotFoundError as e:
        # Fallback to manual loading with multiple location search
        from pathlib import Path
        import json
        
        # Try multiple possible locations for setup.json
        possible_paths = [
            # Primary location: src/ePy_docs/project/setup.json
            Path(__file__).parent / "setup.json",
            # Alternative location: configuration/project/setup.json (from project root)
            Path(__file__).parent.parent.parent.parent / "configuration" / "project" / "setup.json",
        ]
        
        # Try to load reader config for legacy path construction
        try:
            reader_config_path = Path(__file__).parent.parent / "files" / "reader_config.json"
            if reader_config_path.exists():
                with open(reader_config_path, 'r', encoding='utf-8') as f:
                    reader_config = json.load(f)
                    
                # Try the legacy path construction as fallback
                setup_path_parts = reader_config["file_paths"]["setup_path_relative"]
                legacy_path = Path(__file__).parent.parent.parent
                for part in setup_path_parts:
                    legacy_path = legacy_path / part
                possible_paths.append(legacy_path)
                
                default_encoding = reader_config["encoding"]["default"]
            else:
                default_encoding = 'utf-8'
        except Exception:
            default_encoding = 'utf-8'
        
        for setup_path in possible_paths:
            if setup_path.exists():
                try:
                    with open(setup_path, 'r', encoding=default_encoding) as f:
                        config = json.load(f)
                        
                    # Cache the result if sync_json is False
                    if not sync_json:
                        cache_key = f"setup_config_{sync_json}"
                        _CONFIG_CACHE[cache_key] = config
                        
                    return config
                except Exception:
                    continue  # Try next path if this one fails to load
        
        # If no path worked, raise detailed error
        paths_tried = [str(p) for p in possible_paths]
        raise RuntimeError(
            f"Setup configuration file not found in any of the expected locations: {paths_tried}. Original error: {e}"
        )


def get_current_project_config() -> Optional['DirectoryConfig']:
    """Get the current project configuration.
    
    Returns:
        Current DirectoryConfig instance if set, None otherwise
    """
    global _CURRENT_PROJECT_CONFIG
    return _CURRENT_PROJECT_CONFIG

def set_current_project_config(config: 'DirectoryConfig') -> None:
    """Set the current project configuration.
    
    Args:
        config: DirectoryConfig instance to set as current
    """
    global _CURRENT_PROJECT_CONFIG
    _CURRENT_PROJECT_CONFIG = config

def clear_current_project_config() -> None:
    """Clear the current project configuration."""
    global _CURRENT_PROJECT_CONFIG
    _CURRENT_PROJECT_CONFIG = None
