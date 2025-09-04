"""Test 007: Final verification of Dimension Setup compliance.

Verify that both violations have been corrected:
1. sync_files=False compliance maintained
2. Only get_colors_config() exists (get_color() eliminated)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_get_color_elimination():
    """Test that get_color() function has been eliminated."""
    
    print("=== TESTING get_color() ELIMINATION ===")
    
    try:
        from ePy_docs.components.colors import get_color
        print("❌ VIOLATION: get_color() still exists!")
        return False
    except ImportError:
        print("✅ get_color() successfully eliminated")
        return True


def test_colors_module_purity():
    """Test that colors module only has get_colors_config()."""
    
    print("\n=== TESTING COLORS MODULE PURITY ===")
    
    try:
        import ePy_docs.components.colors as colors_module
        
        # Get all public functions (not starting with _)
        public_functions = [name for name in dir(colors_module) 
                          if not name.startswith('_') and callable(getattr(colors_module, name))]
        
        print(f"Public functions found: {public_functions}")
        
        expected_functions = ['get_colors_config']
        
        if public_functions == expected_functions:
            print("✅ Colors module is pure - only get_colors_config() exists")
            return True
        else:
            extra_functions = set(public_functions) - set(expected_functions)
            missing_functions = set(expected_functions) - set(public_functions)
            
            if extra_functions:
                print(f"❌ VIOLATION: Extra functions found: {extra_functions}")
            if missing_functions:
                print(f"❌ ERROR: Missing functions: {missing_functions}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_basic_functionality():
    """Test that basic color functionality still works."""
    
    print("\n=== TESTING BASIC FUNCTIONALITY ===")
    
    try:
        from ePy_docs.components.colors import get_colors_config
        
        # Test sync_files=False
        colors = get_colors_config(sync_files=False)
        print("✅ get_colors_config(sync_files=False) works")
        
        # Test access to palettes
        if 'palettes' in colors and 'brand' in colors['palettes']:
            print("✅ Palette access works")
        else:
            print("❌ ERROR: Palette access broken")
            return False
        
        # Test access to layout_styles
        if 'layout_styles' in colors and 'creative' in colors['layout_styles']:
            print("✅ Layout styles access works")
        else:
            print("❌ ERROR: Layout styles access broken")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_no_automatic_sync():
    """Test that nothing syncs automatically."""
    
    print("\n=== TESTING NO AUTOMATIC SYNC ===")
    
    try:
        # Clean any configuration folders
        import shutil
        from pathlib import Path
        
        test_dir = Path(__file__).parent
        config_dirs = [
            test_dir / "data" / "configuration",
            test_dir.parent / "data" / "configuration"
        ]
        
        for config_dir in config_dirs:
            if config_dir.exists():
                shutil.rmtree(config_dir)
        
        # Import and use colors without explicit sync_files
        from ePy_docs.components.colors import get_colors_config
        colors = get_colors_config()  # Uses default sync_files=False
        
        # Check no directories were created
        for config_dir in config_dirs:
            if config_dir.exists():
                print(f"❌ VIOLATION: Directory created automatically: {config_dir}")
                return False
        
        print("✅ No automatic synchronization occurred")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_import_structure():
    """Test that imports work correctly after changes."""
    
    print("\n=== TESTING IMPORT STRUCTURE ===")
    
    try:
        # Test main import
        from ePy_docs.components.colors import get_colors_config
        print("✅ Direct import works")
        
        # Test that old get_color imports fail gracefully
        try:
            from ePy_docs.components.colors import get_color
            print("❌ VIOLATION: get_color still importable")
            return False
        except ImportError:
            print("✅ get_color import correctly blocked")
        
        # Test package-level imports
        import ePy_docs
        if hasattr(ePy_docs, 'get_colors_config'):
            print("✅ Package-level import available")
        else:
            print("⚠️  Package-level import not available (may be okay)")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    print("🔍 FINAL DIMENSION SETUP COMPLIANCE VERIFICATION\n")
    
    test_results = [
        test_get_color_elimination(),
        test_colors_module_purity(), 
        test_basic_functionality(),
        test_no_automatic_sync(),
        test_import_structure()
    ]
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - DIMENSION SETUP COMPLIANCE ACHIEVED!")
        print("✅ get_color() eliminated")  
        print("✅ Only get_colors_config() exists")
        print("✅ sync_files=False compliance maintained")
    else:
        print("🚨 VIOLATIONS REMAIN - Additional fixes needed")
    
    print(f"\nOverall result: {'PASS' if passed == total else 'FAIL'}")
