"""Test 003: Sync files compliance verification.

Tests whether sync_files=False is being respected across the system.
No configuration folder synchronization should occur.
"""
import sys
import os
from pathlib import Path
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def clean_configuration_folders():
    """Remove any existing configuration folders."""
    test_dir = Path(__file__).parent
    config_dirs = [
        test_dir / "data" / "configuration",
        test_dir.parent / "data" / "configuration"
    ]
    
    for config_dir in config_dirs:
        if config_dir.exists():
            shutil.rmtree(config_dir)
            print(f"Cleaned: {config_dir}")


def test_sync_files_false_compliance():
    """Test that sync_files=False prevents any synchronization."""
    from ePy_docs.components.setup import _resolve_config_path, _load_cached_files
    
    print("=== TESTING sync_files=False COMPLIANCE ===")
    
    # Clean any existing configuration folders
    clean_configuration_folders()
    
    test_configs = [
        'colors',
        'tables', 
        'components/pages',
        'components/setup',
        'units/format'
    ]
    
    violations = []
    
    for config_name in test_configs:
        try:
            print(f"\nTesting: {config_name}")
            
            # Test path resolution with sync_files=False
            resolved_path = _resolve_config_path(config_name, sync_files=False)
            print(f"Resolved path: {resolved_path}")
            
            # Verify it's pointing to package directory, not configuration folder
            if "configuration" in resolved_path:
                violations.append(f"Path resolution violation: {config_name} -> {resolved_path}")
                print(f"❌ VIOLATION: Path points to configuration folder!")
                continue
            
            # Test loading with sync_files=False  
            try:
                config = _load_cached_files(resolved_path, sync_files=False)
                print(f"✅ Loaded successfully from package")
                
                # Check if any configuration folders were created
                test_dir = Path(__file__).parent
                config_dirs = [
                    test_dir / "data" / "configuration",
                    test_dir.parent / "data" / "configuration"
                ]
                
                for config_dir in config_dirs:
                    if config_dir.exists():
                        violations.append(f"Folder creation violation: {config_dir} was created during sync_files=False")
                        print(f"❌ VIOLATION: Configuration folder was created!")
                        
            except FileNotFoundError:
                print(f"✅ File not found (expected when sync_files=False)")
            except Exception as e:
                violations.append(f"Loading error for {config_name}: {e}")
                print(f"❌ ERROR: {e}")
                
        except Exception as e:
            violations.append(f"General error for {config_name}: {e}")
            print(f"❌ ERROR: {e}")
    
    print(f"\n=== RESULTS ===")
    if violations:
        print(f"❌ {len(violations)} VIOLATIONS DETECTED:")
        for violation in violations:
            print(f"  - {violation}")
        return False
    else:
        print("✅ ALL TESTS PASSED - sync_files=False compliance verified")
        return True


def test_sync_files_true_functionality():
    """Test that sync_files=True works correctly."""
    from ePy_docs.components.setup import _resolve_config_path, _load_cached_files
    
    print("\n=== TESTING sync_files=True FUNCTIONALITY ===")
    
    # Clean any existing configuration folders
    clean_configuration_folders()
    
    try:
        config_name = 'colors'
        print(f"Testing synchronization for: {config_name}")
        
        # Test path resolution with sync_files=True
        resolved_path = _resolve_config_path(config_name, sync_files=True)
        print(f"Resolved path: {resolved_path}")
        
        # This should create configuration folder and sync file
        config = _load_cached_files(resolved_path, sync_files=True)
        print(f"✅ Configuration loaded with sync_files=True")
        
        # Verify configuration folder was created
        test_dir = Path(__file__).parent
        config_dir = test_dir.parent / "data" / "configuration"
        
        if config_dir.exists():
            print(f"✅ Configuration folder created as expected")
            return True
        else:
            print(f"❌ Configuration folder was NOT created")
            return False
            
    except Exception as e:
        print(f"❌ ERROR in sync_files=True test: {e}")
        return False


if __name__ == "__main__":
    test1 = test_sync_files_false_compliance()
    test2 = test_sync_files_true_functionality()
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"sync_files=False compliance: {'PASS' if test1 else 'FAIL'}")
    print(f"sync_files=True functionality: {'PASS' if test2 else 'FAIL'}")
    
    if test1 and test2:
        print("🎉 ALL TESTS PASSED - Dimensión Setup compliance verified")
    else:
        print("🚨 VIOLATIONS DETECTED - Dimensión Setup rules broken")
