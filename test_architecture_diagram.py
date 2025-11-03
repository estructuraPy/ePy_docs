#!/usr/bin/env python3
"""
Gráfico del flujo arquitectural del sistema de fuentes
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
from pathlib import Path

def create_architecture_flow_diagram():
    """Crea un diagrama del flujo arquitectural"""
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Colores
    config_color = '#E8F4FD'  # Azul claro
    code_color = '#FFF2CC'    # Amarillo claro
    output_color = '#E1D5E7'  # Púrpura claro
    process_color = '#D5E8D4' # Verde claro
    
    # Título
    ax.text(5, 9.5, 'Flujo Arquitectural del Sistema de Fuentes ePy_docs', 
            fontsize=16, fontweight='bold', ha='center')
    
    # 1. Configuración (assets.epyson)
    config_box = FancyBboxPatch((0.5, 7.5), 2, 1.2, 
                               boxstyle="round,pad=0.1", 
                               facecolor=config_color, 
                               edgecolor='black', linewidth=1)
    ax.add_patch(config_box)
    ax.text(1.5, 8.1, 'assets.epyson', fontweight='bold', ha='center', fontsize=10)
    ax.text(1.5, 7.8, 'font_families:', ha='center', fontsize=8)
    ax.text(1.5, 7.6, 'handwritten_personal', ha='center', fontsize=8, style='italic')
    
    # 2. Layout específico (handwritten.epyson)  
    layout_box = FancyBboxPatch((3.5, 7.5), 2, 1.2,
                               boxstyle="round,pad=0.1",
                               facecolor=config_color,
                               edgecolor='black', linewidth=1)
    ax.add_patch(layout_box)
    ax.text(4.5, 8.1, 'handwritten.epyson', fontweight='bold', ha='center', fontsize=10)
    ax.text(4.5, 7.8, 'font_family:', ha='center', fontsize=8)
    ax.text(4.5, 7.6, 'handwritten_personal', ha='center', fontsize=8, style='italic')
    
    # 3. Template de archivo
    template_box = FancyBboxPatch((6.5, 7.5), 2.5, 1.2,
                                 boxstyle="round,pad=0.1",
                                 facecolor=config_color,
                                 edgecolor='black', linewidth=1)
    ax.add_patch(template_box)
    ax.text(7.75, 8.1, 'font_file_template:', fontweight='bold', ha='center', fontsize=10)
    ax.text(7.75, 7.8, '"{font_name}_regular.otf"', ha='center', fontsize=8, style='italic')
    ax.text(7.75, 7.6, '(configuración dinámica)', ha='center', fontsize=7)
    
    # 4. Procesador de imágenes
    processor_box = FancyBboxPatch((1, 5.5), 3, 1.2,
                                  boxstyle="round,pad=0.1",
                                  facecolor=process_color,
                                  edgecolor='black', linewidth=1)
    ax.add_patch(processor_box)
    ax.text(2.5, 6.1, 'ImageProcessor', fontweight='bold', ha='center', fontsize=11)
    ax.text(2.5, 5.8, 'setup_matplotlib_fonts()', ha='center', fontsize=9)
    ax.text(2.5, 5.6, '(genérico, sin hardcoding)', ha='center', fontsize=8, style='italic')
    
    # 5. Registro de fuentes
    register_box = FancyBboxPatch((5.5, 5.5), 3, 1.2,
                                 boxstyle="round,pad=0.1",
                                 facecolor=code_color,
                                 edgecolor='black', linewidth=1)
    ax.add_patch(register_box)
    ax.text(7, 6.1, '_register_font_if_exists()', fontweight='bold', ha='center', fontsize=11)
    ax.text(7, 5.8, 'Usa font_file_template', ha='center', fontsize=9)
    ax.text(7, 5.6, 'No más "_regular" hardcoded', ha='center', fontsize=8, style='italic')
    
    # 6. Archivo de fuente
    font_file_box = FancyBboxPatch((0.5, 3.5), 3.5, 1.2,
                                  boxstyle="round,pad=0.1",
                                  facecolor='#FFE6CC',  # Naranja claro
                                  edgecolor='black', linewidth=1)
    ax.add_patch(font_file_box)
    ax.text(2.25, 4.1, 'C2024_anm_font_regular.otf', fontweight='bold', ha='center', fontsize=10)
    ax.text(2.25, 3.8, 'Archivo físico de fuente', ha='center', fontsize=9)
    ax.text(2.25, 3.6, '(src/ePy_docs/config/assets/fonts/)', ha='center', fontsize=8, style='italic')
    
    # 7. Matplotlib
    matplotlib_box = FancyBboxPatch((5, 3.5), 3.5, 1.2,
                                   boxstyle="round,pad=0.1",
                                   facecolor=output_color,
                                   edgecolor='black', linewidth=1)
    ax.add_patch(matplotlib_box)
    ax.text(6.75, 4.1, 'Matplotlib FontManager', fontweight='bold', ha='center', fontsize=10)
    ax.text(6.75, 3.8, 'Fuente registrada y disponible', ha='center', fontsize=9)
    ax.text(6.75, 3.6, 'para gráficos', ha='center', fontsize=8, style='italic')
    
    # 8. Resultado final
    result_box = FancyBboxPatch((2.5, 1.5), 4, 1.2,
                               boxstyle="round,pad=0.1",
                               facecolor='#D4EDDA',  # Verde claro
                               edgecolor='black', linewidth=2)
    ax.add_patch(result_box)
    ax.text(4.5, 2.1, 'Gráficos con Fuente Personalizada', fontweight='bold', ha='center', fontsize=12)
    ax.text(4.5, 1.8, '✅ Sistema completamente genérico', ha='center', fontsize=10)
    ax.text(4.5, 1.6, '✅ Configuración externalizada', ha='center', fontsize=10)
    
    # Flechas del flujo
    arrows = [
        # Config a processor
        ((1.5, 7.5), (2.5, 6.7)),
        ((4.5, 7.5), (2.5, 6.7)),
        ((7.75, 7.5), (7, 6.7)),
        
        # Processor a registro
        ((4, 6.1), (5.5, 6.1)),
        
        # Registro a archivo y matplotlib
        ((7, 5.5), (2.25, 4.7)),
        ((7, 5.5), (6.75, 4.7)),
        
        # A resultado final
        ((2.25, 3.5), (4.5, 2.7)),
        ((6.75, 3.5), (4.5, 2.7))
    ]
    
    for start, end in arrows:
        arrow = ConnectionPatch(start, end, "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5,
                              mutation_scale=20, fc="black", lw=1.5)
        ax.add_patch(arrow)
    
    # Leyenda
    legend_elements = [
        mpatches.Patch(color=config_color, label='Configuración (.epyson)'),
        mpatches.Patch(color=process_color, label='Procesamiento'),
        mpatches.Patch(color=code_color, label='Código Python'),
        mpatches.Patch(color='#FFE6CC', label='Recursos'),
        mpatches.Patch(color=output_color, label='Sistema externo'),
        mpatches.Patch(color='#D4EDDA', label='Resultado')
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.98, 0.98))
    
    # Texto explicativo
    ax.text(0.5, 0.8, 'FLUJO ARQUITECTURAL:', fontweight='bold', fontsize=10)
    ax.text(0.5, 0.5, '1. Configuración define familias de fuentes y templates de archivos', fontsize=8)
    ax.text(0.5, 0.3, '2. Código genérico lee configuración (sin hardcoding)', fontsize=8)
    ax.text(0.5, 0.1, '3. Archivos de fuente se localizan dinámicamente usando templates', fontsize=8)
    
    plt.tight_layout()
    
    # Guardar
    output_file = Path(__file__).parent / 'results' / 'font_architecture_flow.png'
    output_file.parent.mkdir(exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Diagrama de flujo guardado en: {output_file}")
    
    plt.show()

def create_before_after_comparison():
    """Crea comparación antes/después del refactor"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # ANTES
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    ax1.set_title('ANTES: Sistema con Hardcoding', fontsize=14, fontweight='bold', color='red')
    
    # Código hardcodeado
    hardcode_box = FancyBboxPatch((2, 6), 6, 2,
                                 boxstyle="round,pad=0.2",
                                 facecolor='#FFCCCB',  # Rojo claro
                                 edgecolor='red', linewidth=2)
    ax1.add_patch(hardcode_box)
    ax1.text(5, 7.2, 'Código Python', fontweight='bold', ha='center', fontsize=12)
    ax1.text(5, 6.7, 'font_file = f"{font_name}_regular.otf"', ha='center', fontsize=10, 
            family='monospace', bbox=dict(boxstyle="round,pad=0.3", facecolor="white"))
    ax1.text(5, 6.3, '❌ Sufijo hardcodeado', ha='center', fontsize=10, color='red')
    
    # Problema
    problem_box = FancyBboxPatch((1, 3), 8, 1.5,
                                boxstyle="round,pad=0.2",
                                facecolor='#FFE4E1',
                                edgecolor='darkred', linewidth=1)
    ax1.add_patch(problem_box)
    ax1.text(5, 3.8, 'PROBLEMAS:', fontweight='bold', ha='center', fontsize=11, color='darkred')
    ax1.text(5, 3.4, '• Cada fuente necesita el sufijo "_regular"', ha='center', fontsize=9)
    ax1.text(5, 3.1, '• No es genérico para otras convenciones de nombres', ha='center', fontsize=9)
    
    # DESPUÉS  
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    ax2.set_title('DESPUÉS: Sistema Genérico', fontsize=14, fontweight='bold', color='green')
    
    # Configuración
    config_box = FancyBboxPatch((1, 7.5), 8, 1.5,
                               boxstyle="round,pad=0.2",
                               facecolor='#E8F4FD',
                               edgecolor='blue', linewidth=2)
    ax2.add_patch(config_box)
    ax2.text(5, 8.4, 'assets.epyson', fontweight='bold', ha='center', fontsize=12)
    ax2.text(5, 8, '"font_file_template": "{font_name}_regular.otf"', ha='center', fontsize=10,
            family='monospace', bbox=dict(boxstyle="round,pad=0.3", facecolor="white"))
    
    # Código genérico
    generic_box = FancyBboxPatch((1, 5), 8, 1.5,
                                boxstyle="round,pad=0.2",
                                facecolor='#D5E8D4',  # Verde claro
                                edgecolor='green', linewidth=2)
    ax2.add_patch(generic_box)
    ax2.text(5, 5.9, 'Código Python', fontweight='bold', ha='center', fontsize=12)
    ax2.text(5, 5.5, 'font_file_template.format(font_name=font_name)', ha='center', fontsize=10,
            family='monospace', bbox=dict(boxstyle="round,pad=0.3", facecolor="white"))
    ax2.text(5, 5.1, '✅ Usa configuración dinámica', ha='center', fontsize=10, color='green')
    
    # Beneficios
    benefits_box = FancyBboxPatch((1, 2), 8, 2,
                                 boxstyle="round,pad=0.2",
                                 facecolor='#D4EDDA',
                                 edgecolor='darkgreen', linewidth=1)
    ax2.add_patch(benefits_box)
    ax2.text(5, 3.5, 'BENEFICIOS:', fontweight='bold', ha='center', fontsize=11, color='darkgreen')
    ax2.text(5, 3.1, '✅ Completamente configurable', ha='center', fontsize=9)
    ax2.text(5, 2.8, '✅ Soporte para cualquier convención de nombres', ha='center', fontsize=9)
    ax2.text(5, 2.5, '✅ Sin hardcoding en el código', ha='center', fontsize=9)
    ax2.text(5, 2.2, '✅ Fácil mantenimiento y extensión', ha='center', fontsize=9)
    
    # Flecha de transformación
    arrow = ConnectionPatch((8.5, 5), (1.5, 5), "data", "data",
                          axesA=ax1, axesB=ax2, color="purple", 
                          arrowstyle="->", shrinkA=5, shrinkB=5,
                          mutation_scale=30, lw=3)
    fig.add_artist(arrow)
    
    plt.tight_layout()
    
    # Guardar
    output_file = Path(__file__).parent / 'results' / 'font_refactor_comparison.png'
    output_file.parent.mkdir(exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Comparación antes/después guardada en: {output_file}")
    
    plt.show()

if __name__ == "__main__":
    print("Generando diagramas arquitecturales...")
    create_architecture_flow_diagram()
    create_before_after_comparison()
    print("✅ Diagramas completados")