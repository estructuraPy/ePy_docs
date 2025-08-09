"""Directory and Path Configuration Manager

This module provides a centralized configuration system for managing
project directories and file paths in the rigid block foundation analysis.
"""

import os
import sys
import json
import shutil
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

# Global variable to store current project configuration
_CURRENT_PROJECT_CONFIG = None


# Configuration utilities removed - using dynamic discovery instead


@dataclass
class ProjectFolders:
    """Data class for project folder paths."""
    config: str
    data: str
    results: str
    brand: str
    templates: str
    exports: str


class DynamicConfigPaths:
    """Dynamic configuration paths based on setup.json."""
    
    def __init__(self, base_path: str = ""):
        self._base_path = base_path
        self._paths = {}
        self._dynamic_attrs = {}
    
    def __getattr__(self, name: str):
        if name.startswith('_'):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        # Return path if it's a file attribute (ends with _json, _csv, etc.)
        if '_' in name and name.split('_')[-1] in ['json', 'csv', 'py']:
            return self._paths.get(name, "")
        
        # Otherwise, create and return a new DynamicConfigPaths object
        if name not in self._dynamic_attrs:
            self._dynamic_attrs[name] = DynamicConfigPaths()
        return self._dynamic_attrs[name]
    
    def __setattr__(self, name: str, value) -> None:
        if name.startswith('_'):
            super().__setattr__(name, value)
        else:
            if not hasattr(self, '_paths'):
                # Initialize _paths if it doesn't exist yet
                super().__setattr__('_paths', {})
            self._paths[name] = value
    
    def __dir__(self):
        return list(self._paths.keys()) if hasattr(self, '_paths') else []


class DynamicDataPaths:
    """Dynamic data paths based on setup.json."""
    
    def __init__(self):
        # Initialize internal storage for dynamic attributes
        self._dynamic_attrs = {}
    
    def __getattr__(self, name: str):
        # Return empty object if attribute doesn't exist
        if name not in self._dynamic_attrs:
            self._dynamic_attrs[name] = DynamicConfigPaths()
        return self._dynamic_attrs[name]
    
    def __setattr__(self, name: str, value) -> None:
        if name == '_dynamic_attrs':
            super().__setattr__(name, value)
        else:
            if not hasattr(self, '_dynamic_attrs'):
                self._dynamic_attrs = {}
            self._dynamic_attrs[name] = value
    
    def __dir__(self):
        return list(self._dynamic_attrs.keys()) if hasattr(self, '_dynamic_attrs') else []


class DynamicProjectPaths:
    """Combined dynamic paths for all project files."""
    
    def __init__(self):
        self.configuration = DynamicConfigPaths()
        self.data = DynamicDataPaths()
        # For output, we can keep it simple
        from types import SimpleNamespace
        self.output = SimpleNamespace()
        self.output.reports = SimpleNamespace()
        self.output.reports.report = ""
        self.output.graphics = SimpleNamespace()
        self.output.graphics.watermark_png = ""

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
    files: DynamicProjectPaths = Field(default_factory=DynamicProjectPaths, description="Project file paths")
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
    def _create_project_paths() -> DynamicProjectPaths:
        """Create DynamicProjectPaths instance with dynamic structure.
        
        Returns:
            Configured DynamicProjectPaths instance
        """
        return DynamicProjectPaths()
    
    def _setup_directories(self, sync_json: bool = True) -> None:
        """Setup all project directories using standard folder names."""
        # Use standard folder names without hardcoded configuration
        self.folders.config = os.path.join(self.base_dir, 'configuration')
        self.folders.data = os.path.join(self.base_dir, 'data')
        self.folders.results = os.path.join(self.base_dir, 'results')
        self.folders.brand = os.path.join(self.base_dir, 'brand')
        self.folders.templates = os.path.join(self.base_dir, 'templates')
        self.folders.exports = os.path.join(self.base_dir, 'exports')

    def _setup_file_paths(self, sync_json: bool = True) -> None:
        """Setup all project file paths by scanning actual JSON files."""
        
        # Configuration files base path
        if self.settings.json_templates:
            config_base = self.folders.config
        else:
            config_base = self._get_library_templates_path()
        
        # Dynamically discover and map all JSON files
        discovered_files = self._discover_all_json_files(config_base)
        
        # Organize files by their directory structure
        for source_path, relative_path in discovered_files.items():
            parts = Path(relative_path).parts
            if len(parts) >= 2:
                category = parts[0]  # e.g., 'components', 'core', 'project'
                filename = parts[-1]  # e.g., 'colors.json'
                
                # Get or create category object using dynamic system
                category_obj = getattr(self.files.configuration, category)
                
                # Set the file path
                file_attr = filename.replace('.json', '_json')
                file_path = os.path.join(config_base, relative_path)
                setattr(category_obj, file_attr, file_path)
        
        # Data files - scan data directory for CSV files
        if os.path.exists(self.folders.data):
            for root, dirs, files in os.walk(self.folders.data):
                for file in files:
                    if file.endswith('.csv'):
                        rel_root = os.path.relpath(root, self.folders.data)
                        if rel_root == '.':
                            category = 'structural'
                        else:
                            category = rel_root.replace(os.sep, '_')
                        
                        # Get category object using dynamic system
                        category_obj = getattr(self.files.data, category)
                        
                        # Set the file path
                        file_attr = file.replace('.csv', '_csv')
                        file_path = os.path.join(root, file)
                        setattr(category_obj, file_attr, file_path)

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
        
        This method dynamically builds the file dictionary based on actual
        discovered files, without relying on setup.json configuration.
        
        Returns:
            Dictionary mapping file keys to their paths organized by category
        """
        files_dict = {
            'configuration': {},
            'input_data': {}
        }
        
        # Process configuration files dynamically
        for attr_name in dir(self.files.configuration):
            if not attr_name.startswith('_'):
                category_obj = getattr(self.files.configuration, attr_name)
                if hasattr(category_obj, '_paths') or hasattr(category_obj, '_dynamic_attrs'):
                    files_dict['configuration'][attr_name] = {}
                    
                    # Get all file paths from this category
                    if hasattr(category_obj, '_paths'):
                        for file_key, file_path in category_obj._paths.items():
                            if file_path:  # Only include non-empty paths
                                files_dict['configuration'][attr_name][file_key] = file_path
        
        # Process input data files dynamically
        for attr_name in dir(self.files.data):
            if not attr_name.startswith('_'):
                category_obj = getattr(self.files.data, attr_name)
                if hasattr(category_obj, '_paths') or hasattr(category_obj, '_dynamic_attrs'):
                    files_dict['input_data'][attr_name] = {}
                    
                    # Get all file paths from this category
                    if hasattr(category_obj, '_paths'):
                        for file_key, file_path in category_obj._paths.items():
                            if file_path:  # Only include non-empty paths
                                files_dict['input_data'][attr_name][file_key] = file_path
        
        return files_dict
    
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
                parts = json_file.parts
                epy_docs_index = None
                
                # Look for src/ePy_docs pattern specifically
                for i in range(len(parts) - 1):
                    if parts[i] == "src" and parts[i + 1] == "ePy_docs":
                        epy_docs_index = i + 1
                        break
                
                if epy_docs_index is not None:
                    # Get path relative to the library's ePy_docs directory
                    relative_parts = parts[epy_docs_index + 1:]
                    if relative_parts:
                        relative_path = str(Path(*relative_parts))
                        discovered[str(json_file)] = relative_path
                    
            except Exception:
                continue
        
        return discovered

    def validate_required_files(self, required_files: Optional[Dict[str, str]] = None) -> Dict[str, bool]:
        """Validate that specified files exist.
        
        Args:
            required_files: Dictionary mapping file keys to file paths.
                          If None, validates both configuration and data files.
        
        Returns:
            Dictionary with validation results organized by category like setup.json
            
        Raises:
            FileNotFoundError: If any required file is missing
            
        Assumptions:
            File system access is available for existence checks
        """
        validation = {
            'configuration': {},
            'input_data': {}
        }
        
        if required_files:
            validation['required'] = {}
            for file_key, file_path in required_files.items():
                validation['required'][file_key] = os.path.exists(file_path)
        
        # Dynamically validate configuration files organized by category
        for attr_name in dir(self.files.configuration):
            if not attr_name.startswith('_') and hasattr(self.files.configuration, attr_name):
                section_obj = getattr(self.files.configuration, attr_name)
                
                # Skip methods and built-in attributes, only process configuration sections
                if hasattr(section_obj, '_paths') or hasattr(section_obj, '__dict__'):
                    validation['configuration'][attr_name] = {}
                    
                    # Get all file attributes from this section
                    for file_attr_name in dir(section_obj):
                        if not file_attr_name.startswith('_') and hasattr(section_obj, file_attr_name):
                            file_path = getattr(section_obj, file_attr_name)
                            if isinstance(file_path, str) and file_path.endswith('.json'):
                                # Remove _json suffix for cleaner display
                                clean_name = file_attr_name.replace('_json', '')
                                validation['configuration'][attr_name][clean_name] = os.path.exists(file_path)
        
        # Dynamically validate data files organized by category
        # Get all attributes of self.files.data that don't start with underscore
        for attr_name in dir(self.files.data):
            if not attr_name.startswith('_') and hasattr(self.files.data, attr_name):
                section_obj = getattr(self.files.data, attr_name)
                
                # Skip methods and properties, only process actual data sections
                if hasattr(section_obj, '__dict__') or hasattr(section_obj, '__slots__'):
                    validation['input_data'][attr_name] = {}
                    
                    # Get all file attributes from this section
                    for file_attr_name in dir(section_obj):
                        if not file_attr_name.startswith('_') and hasattr(section_obj, file_attr_name):
                            file_path = getattr(section_obj, file_attr_name)
                            if isinstance(file_path, str):
                                # Remove _csv suffix for cleaner display
                                clean_name = file_attr_name.replace('_csv', '')
                                validation['input_data'][attr_name][clean_name] = os.path.exists(file_path)
        
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
        
        # Extract missing config files from the new organized structure
        missing_configs = []
        if 'configuration' in validation:
            for category, files in validation['configuration'].items():
                for file_name, exists in files.items():
                    if not exists:
                        missing_configs.append(f"{category}_{file_name}")
        
        setup_result = {
            'directories_created': True,
            'json_synced': final_sync_json,
            'configuration_directory_created': self.settings.json_templates,
            'missing_config_files': missing_configs,
            'file_validation': validation,
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
        
        # Extract missing config files from the new organized structure
        missing_configs = []
        if 'configuration' in validation:
            for category, files in validation['configuration'].items():
                for file_name, exists in files.items():
                    if not exists:
                        missing_configs.append(f"{category}_{file_name}")
        
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
    
    def load_config_file(self, config_type: str, sync_json: bool = True) -> Dict[str, Any]:
        """Load configuration file using the project configuration system.
        
        Args:
            config_type: Type of configuration to load
            sync_json: Whether to synchronize from source before loading
            
        Returns:
            Dictionary containing configuration data
            
        Raises:
            ValueError: If config type is unknown
            FileNotFoundError: If configuration file doesn't exist
            RuntimeError: If file cannot be loaded
        """
        # Import here to avoid circular dependency
        from ePy_docs.files.reader import ReadFiles
        
        # Dynamically build config paths from ALL configuration sections
        config_paths = {}
        
        # Get section names from _dynamic_attrs if available
        if hasattr(self.files.configuration, '_dynamic_attrs'):
            section_names = list(self.files.configuration._dynamic_attrs.keys())
        else:
            # Fallback to known section names
            section_names = ['components', 'core', 'project', 'units', 'formats', 'files', 'references', 'reports']
        
        # Scan ALL configuration sections dynamically
        for section_name in section_names:
            section_obj = getattr(self.files.configuration, section_name)
            # Force accessing the section to trigger dynamic creation
            if hasattr(section_obj, '_paths'):
                for attr_name, file_path in section_obj._paths.items():
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
                config_data = _load_cached_json(file_path, sync_json=sync_json)
                if config_data is None:
                    raise ValueError(f"Empty JSON configuration: {config_type}")
            else:
                # Fallback to ReadFiles for non-JSON files
                reader = ReadFiles(file_path=file_path, sync_json=sync_json)
                
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

    def load_all_configs(self, sync_json: bool = True) -> Dict[str, Dict[str, Any]]:
        """Load all available configuration files dynamically.
        
        Args:
            sync_json: Whether to synchronize from source before loading.
        
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
        
        # Get section names from _dynamic_attrs if available
        if hasattr(self.files.configuration, '_dynamic_attrs'):
            section_names = list(self.files.configuration._dynamic_attrs.keys())
        else:
            # Fallback to known section names
            section_names = ['components', 'core', 'project', 'units', 'formats', 'files', 'references', 'reports']
        
        # Scan ALL configuration sections dynamically
        for section_name in section_names:
            section_obj = getattr(self.files.configuration, section_name)
            # Force accessing the section to trigger dynamic creation
            if hasattr(section_obj, '_paths'):
                for attr_name, file_path in section_obj._paths.items():
                    if isinstance(file_path, str) and file_path.endswith('.json'):
                        # Create config type name from attribute (remove _json suffix)
                        config_type_name = attr_name.replace('_json', '')
                        available_config_types.append(config_type_name)
        
        # Load all available configurations
        for config_type in available_config_types:
            try:
                configs[config_type] = self.load_config_file(config_type, sync_json=sync_json)
            except (FileNotFoundError, ValueError) as e:
                # Skip configurations that don't exist or can't be loaded
                print(f"Warning: Could not load config '{config_type}': {e}")
                continue
        
        # Add output configuration for backward compatibility with notebooks
        if 'project' in configs:
            # Add the output section that notebooks expect
            if 'output' not in configs['project']:
                configs['project']['output'] = {}
            
            # Add report filename to the output section using the sync_json parameter
            report_filename = self.get_report_filename('pdf', sync_json=sync_json)
            configs['project']['output']['report_filename'] = report_filename
            configs['project']['output']['auto_print'] = True  # Default value
        
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
    
    # Convenience properties for direct access to common file paths
    @property
    def report(self) -> str:
        """Get the report file path.
        
        Returns:
            Full path to the report file
        """
        return self.files.report
    
    def get_report_filename(self, extension: str = "pdf", sync_json: bool = True) -> str:
        """Get the report filename with extension.
        
        Args:
            extension: File extension (default: pdf)
            sync_json: Whether to synchronize from source before loading
            
        Returns:
            Report filename with extension, taken from project.json 'report' field
        """
        if sync_json:
            # Load configuration directly from project.json to get current name
            try:
                # Import here to avoid circular dependency
                from ePy_docs.files.reader import ReadFiles
                
                # Load project.json to get the report name
                project_json_path = self.files.configuration.project.project_json
                
                reader = ReadFiles(file_path=project_json_path, sync_json=True)
                project_config = reader.load_json()
                
                report_name = project_config.get('project', {}).get('report', 'report')
            except (FileNotFoundError, ValueError, KeyError, AttributeError):
                # Fallback to configured path if loading fails
                report_name = os.path.basename(self.files.report)
        else:
            # Use the configured path from initialization
            report_name = os.path.basename(self.files.report)
        
        return f"{report_name}.{extension}"
    
    def get_report_path(self, extension: str = "pdf", sync_json: bool = True) -> str:
        """Get the full report path with extension.
        
        Args:
            extension: File extension (default: pdf)
            sync_json: Whether to synchronize from source before loading
            
        Returns:
            Full path to report file with extension
        """
        return os.path.join(self.folders.results, self.get_report_filename(extension, sync_json=sync_json))

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

def debug_config_loading(create_new: bool = True) -> Dict[str, Any]:
    """Debug configuration loading issues.
    
    Args:
        create_new: Whether to create a new DirectoryConfig instance
        
    Returns:
        Dictionary with debugging information
    """
    debug_info = {
        'global_config_exists': _CURRENT_PROJECT_CONFIG is not None,
        'steps': []
    }
    
    if create_new:
        debug_info['steps'].append("Creating new DirectoryConfig...")
        config = DirectoryConfig()
    else:
        config = get_current_project_config()
        if config is None:
            debug_info['steps'].append("No global config found, creating new...")
            config = DirectoryConfig()
        else:
            debug_info['steps'].append("Using existing global config...")
    
    # Check configuration sections
    debug_info['steps'].append("Checking configuration sections...")
    sections = ['components', 'core', 'project', 'units', 'formats', 'files', 'references', 'reports']
    available_sections = []
    
    for section in sections:
        try:
            section_obj = getattr(config.files.configuration, section)
            if hasattr(section_obj, '_dynamic_attrs'):
                available_sections.append(f"{section} (dynamic)")
            else:
                available_sections.append(f"{section} (static)")
        except Exception as e:
            debug_info['steps'].append(f"Error accessing {section}: {e}")
    
    debug_info['available_sections'] = available_sections
    debug_info['steps'].append(f"Found sections: {available_sections}")
    
    # Try loading all configs
    try:
        debug_info['steps'].append("Loading all configurations...")
        configs = config.load_all_configs()
        debug_info['loaded_configs'] = list(configs.keys())
        debug_info['units_available'] = 'units' in configs
        debug_info['success'] = True
        
        if 'units' in configs:
            debug_info['units_sample'] = {k: str(v)[:50] + "..." if len(str(v)) > 50 else v 
                                        for k, v in list(configs['units'].items())[:3]}
        
    except Exception as e:
        debug_info['error'] = str(e)
        debug_info['success'] = False
        debug_info['steps'].append(f"Error loading configs: {e}")
    
    # Set as current config if successful
    if debug_info.get('success', False) and create_new:
        set_current_project_config(config)
        debug_info['steps'].append("Set as current global config")
    
    return debug_info

def force_refresh_config() -> 'DirectoryConfig':
    """Force refresh the configuration system.
    
    Returns:
        New DirectoryConfig instance with all configurations loaded
    """
    # Clear any cached config
    clear_current_project_config()
    
    # Create fresh instance
    config = DirectoryConfig()
    
    # Force access to all known sections to trigger dynamic creation
    known_sections = ['components', 'core', 'project', 'units', 'formats', 'files', 'references', 'reports']
    for section in known_sections:
        getattr(config.files.configuration, section)
    
    # Set as current config
    set_current_project_config(config)
    
    return config

def load_setup_config(sync_json: bool = True) -> Dict[str, Any]:
    """Load setup configuration using the current project configuration.
    
    Args:
        sync_json: Whether to synchronize from source before loading
        
    Returns:
        Dictionary containing setup configuration data
        
    Raises:
        RuntimeError: If setup configuration cannot be loaded
    """
    try:
        # Get current project config or create new one
        config = get_current_project_config()
        if config is None:
            config = DirectoryConfig()
            set_current_project_config(config)
        
        # Load setup configuration
        setup_config = config.load_config_file('setup', sync_json=sync_json)
        return setup_config
        
    except Exception as e:
        raise RuntimeError(f"Error loading setup configuration: {e}")
