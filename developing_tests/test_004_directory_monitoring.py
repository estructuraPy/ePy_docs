"""Test 004: Directory creation monitoring.

Monitor exactly when and where configuration directories are created
to identify violations of sync_files=False rules.
"""
import sys
import os
from pathlib import Path
import shutil
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def monitor_directory_creation():
    """Monitor and log all directory creation attempts."""
    original_makedirs = os.makedirs
    original_mkdir = Path.mkdir
    
    created_dirs = []
    
    def tracked_makedirs(name, mode=0o777, exist_ok=False):
        created_dirs.append(f"os.makedirs: {name}")
        print(f"🚨 DIRECTORY CREATED: os.makedirs({name})")
        return original_makedirs(name, mode, exist_ok)
    
    def tracked_mkdir(self, mode=0o777, parents=False, exist_ok=False):
        created_dirs.append(f"Path.mkdir: {self}")
        print(f"🚨 DIRECTORY CREATED: {self}.mkdir()")
        return original_mkdir(self, mode, parents, exist_ok)
    
    return created_dirs, tracked_makedirs, tracked_mkdir


def test_directory_monitoring():
    """Test which operations create directories inappropriately."""
    
    print("=== MONITORING DIRECTORY CREATION ===")
    
    # Clean any existing configuration folders
    test_dir = Path(__file__).parent
    config_dirs = [
        test_dir / "data" / "configuration",
        test_dir.parent / "data" / "configuration"
    ]
    
    for config_dir in config_dirs:
        if config_dir.exists():
            shutil.rmtree(config_dir)
            print(f"Cleaned: {config_dir}")
    
    created_dirs, tracked_makedirs, tracked_mkdir = monitor_directory_creation()
    
    # Patch directory creation methods
    with patch('os.makedirs', side_effect=tracked_makedirs):
        with patch('pathlib.Path.mkdir', tracked_mkdir):
            
            print("\n--- Testing basic color loading with sync_files=False ---")
            try:
                from ePy_docs.components.colors import get_colors_config
                colors = get_colors_config(sync_files=False)
                print("✅ Colors loaded without directory creation")
            except Exception as e:
                print(f"❌ Error loading colors: {e}")
            
            print("\n--- Testing table creation with sync_files=False ---")
            try:
                from ePy_docs.components.tables import get_tables_config
                tables = get_tables_config(sync_files=False)
                print("✅ Tables loaded without directory creation")
            except Exception as e:
                print(f"❌ Error loading tables: {e}")
            
            print("\n--- Testing setup with sync_files=False ---")
            try:
                from ePy_docs.components.setup import get_absolute_output_directories
                dirs = get_absolute_output_directories()
                print(f"✅ Output directories retrieved: {list(dirs.keys())}")
            except Exception as e:
                print(f"❌ Error getting directories: {e}")
            
            print("\n--- Testing project setup simulation ---")
            try:
                from ePy_docs.api.quick_setup import setup_report_api
                setup_data = setup_report_api(
                    layout='creative',
                    project_name="Test Monitor",
                    author="Test System", 
                    base_path=Path(__file__).parent
                )
                print("✅ Setup API completed")
            except Exception as e:
                print(f"❌ Error in setup API: {e}")
    
    print(f"\n=== DIRECTORY CREATION SUMMARY ===")
    if created_dirs:
        print(f"❌ {len(created_dirs)} DIRECTORIES WERE CREATED:")
        for dir_creation in created_dirs:
            print(f"  - {dir_creation}")
        return False
    else:
        print("✅ NO DIRECTORIES WERE CREATED")
        return True


if __name__ == "__main__":
    result = test_directory_monitoring()
    print(f"\nTest result: {'PASS' if result else 'FAIL'}")
    print("🔍 Check if this reveals the source of unwanted directory creation")
