#!/usr/bin/env python3
"""
Debug paso a paso de load_complete_config.
"""

from src.ePy_docs.core._config import ModularConfigLoader

def debug_complete_config_steps():
    """Debug cada paso de load_complete_config."""
    print("🔍 Debuggeando load_complete_config paso a paso...")
    
    loader = ModularConfigLoader()
    layout_name = 'handwritten'
    
    # Step by step like load_complete_config
    master = loader.load_master()
    project = loader.load_project()
    layout = loader.load_layout(layout_name)
    
    complete_config = {}
    
    print("\n1. Después de _merge_master_config:")
    complete_config.update(loader._merge_master_config(master))
    layout_text = complete_config.get('layout', {}).get('text', {})
    print(f"   layout.text: {layout_text}")
    
    print("\n2. Después de _merge_project_config:")
    complete_config.update(loader._merge_project_config(project))
    layout_text = complete_config.get('layout', {}).get('text', {})
    print(f"   layout.text: {layout_text}")
    
    print("\n3. Después de _merge_layout_config:")
    layout_merged = loader._merge_layout_config(layout, layout_name, master)
    print(f"   layout_merged text: {layout_merged.get('text', {})}")
    complete_config.update(layout_merged)
    layout_text = complete_config.get('layout', {}).get('text', {})
    complete_text = complete_config.get('text', {})
    print(f"   complete_config layout.text: {layout_text}")
    print(f"   complete_config text: {complete_text}")
    
    print("\n4. Después de _merge_external_configs:")
    loader._merge_external_configs(master, complete_config)
    layout_text = complete_config.get('layout', {}).get('text', {})
    complete_text = complete_config.get('text', {})
    print(f"   complete_config layout.text: {layout_text}")
    print(f"   complete_config text: {complete_text}")

if __name__ == "__main__":
    print("=" * 60)
    print("DEBUG: load_complete_config paso a paso")
    print("=" * 60)
    
    debug_complete_config_steps()