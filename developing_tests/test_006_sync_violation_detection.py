"""Test 006: Precise sync_files violation detection.

Detect EXACTLY when and where sync_files=False is being violated
by monitoring all file system operations and synchronization attempts.
"""
import sys
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import traceback

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class SyncViolationDetector:
    """Track all synchronization violations."""
    
    def __init__(self):
        self.violations = []
        self.file_operations = []
        self.sync_calls = []
    
    def track_copy(self, src, dst, *args, **kwargs):
        """Track file copy operations."""
        self.violations.append(f"🚨 FILE COPY: {src} → {dst}")
        self.file_operations.append(('copy', src, dst))
        print(f"🚨 VIOLATION: File copy detected: {src} → {dst}")
        
        # Get stack trace to see who called this
        stack = traceback.format_stack()
        print(f"   Called from: {stack[-3].strip()}")
        
        # Call original function
        return shutil.copy2.__wrapped__(src, dst, *args, **kwargs)
    
    def track_makedirs(self, path, mode=0o777, exist_ok=False):
        """Track directory creation."""
        if 'configuration' in str(path):
            self.violations.append(f"🚨 MKDIR: {path}")
            print(f"🚨 VIOLATION: Configuration directory created: {path}")
            
            # Get stack trace
            stack = traceback.format_stack()
            print(f"   Called from: {stack[-3].strip()}")
        
        return os.makedirs.__wrapped__(path, mode, exist_ok)
    
    def track_mkdir(self, mode=0o777, parents=False, exist_ok=False):
        """Track Path.mkdir calls."""
        if 'configuration' in str(self):
            self.violations.append(f"🚨 PATH.MKDIR: {self}")
            print(f"🚨 VIOLATION: Configuration path mkdir: {self}")
            
            # Get stack trace  
            stack = traceback.format_stack()
            print(f"   Called from: {stack[-3].strip()}")
        
        return Path.mkdir.__wrapped__(self, mode, parents, exist_ok)


def test_sync_violation_detection():
    """Detect sync_files=False violations with precise tracking."""
    
    print("=== PRECISE SYNC VIOLATION DETECTION ===\n")
    
    # Clean configuration directories
    test_dir = Path(__file__).parent
    config_dirs = [
        test_dir / "data" / "configuration",
        test_dir.parent / "data" / "configuration",
        Path.cwd() / "data" / "configuration"
    ]
    
    for config_dir in config_dirs:
        if config_dir.exists():
            shutil.rmtree(config_dir)
            print(f"Cleaned: {config_dir}")
    
    detector = SyncViolationDetector()
    
    # Patch all file system operations
    original_copy2 = shutil.copy2
    original_makedirs = os.makedirs
    original_mkdir = Path.mkdir
    
    with patch('shutil.copy2', side_effect=detector.track_copy):
        with patch('os.makedirs', side_effect=detector.track_makedirs):  
            with patch('pathlib.Path.mkdir', detector.track_mkdir):
                
                print("1. Testing get_colors_config(sync_files=False)...")
                try:
                    from ePy_docs.components.colors import get_colors_config
                    colors = get_colors_config(sync_files=False)
                    print("   ✅ Colors loaded")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                print("\n2. Testing direct _load_cached_files with sync_files=False...")
                try:
                    from ePy_docs.components.setup import _load_cached_files, _resolve_config_path
                    path = _resolve_config_path('colors', sync_files=False)
                    print(f"   Resolved path: {path}")
                    config = _load_cached_files(path, sync_files=False)
                    print("   ✅ Direct load successful")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                print("\n3. Testing get_absolute_output_directories...")
                try:
                    from ePy_docs.components.setup import get_absolute_output_directories
                    dirs = get_absolute_output_directories()
                    print(f"   ✅ Output directories: {list(dirs.keys())}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                print("\n4. Testing any automatic initialization...")
                try:
                    # This might trigger automatic setup
                    import ePy_docs.components.colors
                    import ePy_docs.components.setup
                    import ePy_docs.components.pages
                    print("   ✅ Modules imported")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
    
    print(f"\n=== VIOLATION SUMMARY ===")
    if detector.violations:
        print(f"❌ {len(detector.violations)} VIOLATIONS DETECTED:")
        for violation in detector.violations:
            print(f"  {violation}")
        return False
    else:
        print("✅ NO VIOLATIONS DETECTED")
        return True


def test_find_actual_sync_trigger():
    """Find what actually triggers synchronization."""
    
    print(f"\n=== FINDING SYNC TRIGGER ===")
    
    # Search for functions that might be calling sync operations
    patterns_to_check = [
        "sync_files=True",
        "sync_files = True", 
        "sync_files:.*True",
        "def.*sync.*True",
        "makedirs.*configuration",
        "copy.*configuration"
    ]
    
    from pathlib import Path
    src_dir = Path(__file__).parent.parent / "src" / "ePy_docs"
    
    print("Searching for potential sync triggers...")
    
    for py_file in src_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            
            for pattern in patterns_to_check:
                import re
                if re.search(pattern, content, re.IGNORECASE):
                    print(f"🔍 Found '{pattern}' in: {py_file.relative_to(src_dir)}")
                    
                    # Show the specific lines
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if re.search(pattern, line, re.IGNORECASE):
                            print(f"   Line {i+1}: {line.strip()}")
                    
        except Exception:
            continue
    
    return True


if __name__ == "__main__":
    print("🚨 INVESTIGATING sync_files=False VIOLATIONS")
    
    result1 = test_sync_violation_detection()
    result2 = test_find_actual_sync_trigger() 
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Violation detection: {'PASS' if result1 else 'FAIL'}")
    print(f"Trigger analysis: {'COMPLETE' if result2 else 'INCOMPLETE'}")
    
    if not result1:
        print("🚨 DIMENSION SETUP VIOLATED - Synchronization occurring with sync_files=False")
    else:
        print("✅ sync_files=False compliance verified")
