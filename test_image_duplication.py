#!/usr/bin/env python3
"""
Test detallado para rastrear duplicación de imágenes.
"""

import matplotlib.pyplot as plt
import pandas as pd
import shutil
from pathlib import Path
import os
import sys

# Add src to path
sys.path.insert(0, 'src')

# Monkey patch savefig to track all saves
original_savefig = plt.Figure.savefig
save_calls = []

def tracked_savefig(self, *args, **kwargs):
    """Wrapper para rastrear todas las llamadas a savefig."""
    import traceback
    
    # Capturar información del save
    call_info = {
        'args': args,
        'kwargs': kwargs,
        'stack': traceback.format_stack()
    }
    save_calls.append(call_info)
    
    print(f"📸 SAVEFIG LLAMADA:")
    if args:
        print(f"   Archivo: {args[0]}")
    if 'fname' in kwargs:
        print(f"   Archivo (kwargs): {kwargs['fname']}")
    
    # Llamar al método original
    return original_savefig(self, *args, **kwargs)

# Aplicar el monkey patch
plt.Figure.savefig = tracked_savefig

from ePy_docs import DocumentWriter

def test_image_duplication():
    """Test detallado para rastrear duplicación de imágenes."""
    
    global save_calls
    save_calls = []
    
    # Clear any existing test results
    test_dir = Path('results/report')
    if test_dir.exists():
        # Solo borrar archivos de figura para no afectar otros tests
        for fig_file in test_dir.glob('figure_*.png'):
            fig_file.unlink()
        for fig_file in test_dir.glob('figure_*.jpg'):
            fig_file.unlink()
    
    print("🧪 Iniciando test de duplicación...")
    
    # Create a writer
    writer = DocumentWriter(
        layout_style='creative', 
        document_type="report"
    )
    
    # Create ONE test plot
    print("📊 Creando figura de prueba...")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot([1, 2, 3], [1, 4, 2])
    ax.set_title('Una sola figura de prueba')
    
    print("➕ Agregando plot al writer...")
    writer.add_plot(fig, title="Test Plot", caption="Should only be saved ONCE")
    
    print(f"💾 Llamadas a savefig hasta ahora: {len(save_calls)}")
    
    print("🔧 Generando documento...")
    paths = writer.generate(output_filename="test_duplication", html=True, pdf=False)
    
    print(f"✅ Generación completa. Total de llamadas a savefig: {len(save_calls)}")
    
    # Analizar las llamadas
    print("\n📋 ANÁLISIS DE LLAMADAS A SAVEFIG:")
    for i, call in enumerate(save_calls, 1):
        print(f"\n--- Llamada {i} ---")
        if call['args']:
            print(f"Archivo: {call['args'][0]}")
        if 'fname' in call['kwargs']:
            print(f"Archivo (kwargs): {call['kwargs']['fname']}")
        
        # Mostrar las últimas 3 líneas del stack trace para identificar de dónde viene
        stack_lines = call['stack'][-3:]
        print("Stack trace (últimas 3 líneas):")
        for line in stack_lines:
            line = line.strip()
            if 'File' in line:
                print(f"  {line}")
    
    # Check files created
    figures_dir = Path('results/report/figures')
    if figures_dir.exists():
        figure_files = list(figures_dir.glob('figure_*.png'))
        jpg_files = list(figures_dir.glob('figure_*.jpg'))
        
        print(f"\n📁 ARCHIVOS CREADOS:")
        print(f"   PNG files: {len(figure_files)}")
        for f in figure_files:
            print(f"     ✓ {f.name}")
        
        if jpg_files:
            print(f"   JPG files: {len(jpg_files)}")
            for f in jpg_files:
                print(f"     ⚠️  {f.name}")
        
        expected_files = 1
        actual_files = len(figure_files) + len(jpg_files)
        
        if actual_files == expected_files:
            print(f"\n✅ CORRECTO: Se creó exactamente {expected_files} archivo como se esperaba")
        else:
            print(f"\n❌ ERROR: Se esperaba {expected_files} archivo, pero se crearon {actual_files}")
    
    # Close figure
    plt.close(fig)

if __name__ == "__main__":
    test_image_duplication()