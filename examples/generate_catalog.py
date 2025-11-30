import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from ePy_docs.writers import DocumentWriter

# Ensure output directory exists
output_dir = "results/catalog"
os.makedirs(output_dir, exist_ok=True)

def visualize_palette(colors_dict, title, figsize=(14, 2)):
    """Visualiza una paleta de colores en formato horizontal."""
    fig, ax = plt.subplots(figsize=figsize)
    n_colors = len(colors_dict)
    for i, (name, color) in enumerate(colors_dict.items()):
        rect = mpatches.Rectangle((i, 0), 1, 1, facecolor=color, edgecolor='black', linewidth=1.5)
        ax.add_patch(rect)
        ax.text(i + 0.5, 0.5, name.upper(), ha='center', va='center', fontsize=10, fontweight='bold', color='white' if is_dark_color(color) else 'black')
        ax.text(i + 0.5, -0.15, color, ha='center', va='top', fontsize=8, color='black')
    ax.set_xlim(0, n_colors)
    ax.set_ylim(-0.3, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    return fig

def is_dark_color(hex_color):
    """Determina si un color es oscuro basado en su luminancia."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return luminance < 0.5

def generate_layout_samples(language="es"):
    """Genera un documento de muestra para cada layout disponible."""
    layouts = DocumentWriter.get_available_layouts()
    lang_suffix = f"_{language}"
    print(f"📚 Generando muestras para {len(layouts)} layouts (Idioma: {language})...")

    for layout in layouts:
        print(f"  Generating sample for '{layout}'...")
        writer = DocumentWriter(document_type="report", layout_style=layout, language=language)
        
        if language == "es":
            writer.set_project_info(name=f"Muestra de Layout: {layout.title()}", code="CAT-2024", created_date="2024-11-29")
            writer.add_h1(f"Estilo Visual: {layout.title()}")
            writer.add_text(f"Este documento es una muestra del layout **{layout}**. El diseño incluye tipografía, colores y espaciado específicos.")
            writer.add_h2("Elementos de Muestra")
            writer.add_note("Este es un ejemplo de nota (callout) con el estilo del layout.", title="Nota de Estilo")
            df = pd.DataFrame({'Concepto': ['A', 'B', 'C'], 'Valor': [10, 20, 30], 'Estado': ['Bajo', 'Medio', 'Alto']})
            writer.add_table(df, title="Tabla de Ejemplo")
        else:
            writer.set_project_info(name=f"Layout Sample: {layout.title()}", code="CAT-2024", created_date="2024-11-29")
            writer.add_h1(f"Visual Style: {layout.title()}")
            writer.add_text(f"This document is a sample of the **{layout}** layout. The design includes specific typography, colors, and spacing.")
            writer.add_h2("Sample Elements")
            writer.add_note("This is a sample note (callout) with the layout style.", title="Style Note")
            df = pd.DataFrame({'Concept': ['A', 'B', 'C'], 'Value': [10, 20, 30], 'Status': ['Low', 'Medium', 'High']})
            writer.add_table(df, title="Sample Table")
        
        writer.generate(pdf=True, html=True, output_filename=f"{output_dir}/layout_sample_{layout}{lang_suffix}")

def generate_color_catalog(language="es"):
    """Genera un catálogo maestro de todas las paletas de colores."""
    lang_suffix = f"_{language}"
    print(f"\n🎨 Generando catálogo maestro de colores (Idioma: {language})...")
    
    writer = DocumentWriter(document_type="report", layout_style="professional", language=language)
    
    if language == "es":
        writer.set_project_info(name="Catálogo de Colores ePy_docs", code="COLOR-2024", created_date="2024-11-29")
        writer.add_h1("Catálogo de Paletas de Colores")
        writer.add_text("Este documento muestra todas las paletas de colores disponibles para tablas y elementos visuales.")
    else:
        writer.set_project_info(name="ePy_docs Color Catalog", code="COLOR-2024", created_date="2024-11-29")
        writer.add_h1("Color Palette Catalog")
        writer.add_text("This document shows all available color palettes for tables and visual elements.")

    # Table Palettes
    table_palettes = {
        'amber': {'Color 1': '#FFA000', 'Color 2': '#FFB300', 'Color 3': '#FFC107', 'Color 4': '#FFE082', 'Color 5': '#FFF8E1', 'Color 6': '#FF6F00'},
        'blues': {'Color 1': '#464A85', 'Color 2': '#636295', 'Color 3': '#827EA8', 'Color 4': '#A4A1C1', 'Color 5': '#CFDEE9', 'Color 6': '#00217E'},
        'brown': {'Color 1': '#5D4037', 'Color 2': '#795548', 'Color 3': '#A1887F', 'Color 4': '#BCAAA4', 'Color 5': '#EFEBE9', 'Color 6': '#3E2723'},
        'burgundy': {'Color 1': '#880E4F', 'Color 2': '#AD1457', 'Color 3': '#C2185B', 'Color 4': '#E91E63', 'Color 5': '#F8BBD0', 'Color 6': '#4A148C'},
        'coral': {'Color 1': '#FF5722', 'Color 2': '#FF7043', 'Color 3': '#FF8A65', 'Color 4': '#FFCCBC', 'Color 5': '#FFF3EE', 'Color 6': '#EF5350'},
        'crimson': {'Color 1': '#B71C1C', 'Color 2': '#D32F2F', 'Color 3': '#E57373', 'Color 4': '#EF9A9A', 'Color 5': '#FFEBEE', 'Color 6': '#880E4F'},
        'cyan': {'Color 1': '#00ACC1', 'Color 2': '#00BCD4', 'Color 3': '#26C6DA', 'Color 4': '#80DEEA', 'Color 5': '#E0F7FA', 'Color 6': '#006064'},
        'demand_capacity': {'Color 1': '#DC2626', 'Color 2': '#F44336', 'Color 3': '#FFC107', 'Color 4': '#8BC34A', 'Color 5': '#4CAF50', 'Color 6': '#1B5E20'},
        'emerald': {'Color 1': '#009688', 'Color 2': '#26A69A', 'Color 3': '#4DB6AC', 'Color 4': '#80CBC4', 'Color 5': '#E0F2F1', 'Color 6': '#00695C'},
        'engineering': {'Color 1': '#1E60A9', 'Color 2': '#428ED4', 'Color 3': '#81BAEF', 'Color 4': '#BBDEFB', 'Color 5': '#ECF5FF', 'Color 6': '#0D3C6C'},
        'forest': {'Color 1': '#388E3C', 'Color 2': '#689F38', 'Color 3': '#8BC34A', 'Color 4': '#AED581', 'Color 5': '#DCEDC8', 'Color 6': '#1B5E20'},
        'grays': {'Color 1': '#636466', 'Color 2': '#808285', 'Color 3': '#9D9FA2', 'Color 4': '#AFB1B3', 'Color 5': '#BCBEC0', 'Color 6': '#010101'},
        'greens': {'Color 1': '#1B5E20', 'Color 2': '#4C8449', 'Color 3': '#4CAF50', 'Color 4': '#C8E6C9', 'Color 5': '#E8F5E9', 'Color 6': '#00796B'},
        'indigo': {'Color 1': '#303F9F', 'Color 2': '#3F51B5', 'Color 3': '#5C6BC0', 'Color 4': '#9FA8DA', 'Color 5': '#E8EAF6', 'Color 6': '#1A237E'},
        'info': {'Color 1': '#1D4ED8', 'Color 2': '#2563EB', 'Color 3': '#3B82F6', 'Color 4': '#BFDBFE', 'Color 5': '#EFF6FF', 'Color 6': '#1E3A8A'},
        'lavender': {'Color 1': '#7E57C2', 'Color 2': '#9575CD', 'Color 3': '#B39DDB', 'Color 4': '#D1C4E9', 'Color 5': '#F3EFF8', 'Color 6': '#5E35B1'},
        'lime': {'Color 1': '#9E9D24', 'Color 2': '#C0CA33', 'Color 3': '#CDDC39', 'Color 4': '#E6EE9C', 'Color 5': '#F9FBE7', 'Color 6': '#827717'},
        'mint': {'Color 1': '#26A69A', 'Color 2': '#4DB6AC', 'Color 3': '#80CBC4', 'Color 4': '#B2DFDB', 'Color 5': '#E0F2F1', 'Color 6': '#00796B'},
        'monochrome': {'Color 1': '#475569', 'Color 2': '#64748B', 'Color 3': '#94A3B8', 'Color 4': '#E2E8F0', 'Color 5': '#F8FAFC', 'Color 6': '#1E293B'},
        'navy': {'Color 1': '#0D47A1', 'Color 2': '#1976D2', 'Color 3': '#42A5F5', 'Color 4': '#90CAF9', 'Color 5': '#E3F2FD', 'Color 6': '#01579B'},
        'neutrals': {'Color 1': '#737373', 'Color 2': '#A3A3A3', 'Color 3': '#D4D4D4', 'Color 4': '#F5F5F5', 'Color 5': '#FAFAFA', 'Color 6': '#404040'},
        'ocean': {'Color 1': '#004D40', 'Color 2': '#00695C', 'Color 3': '#009688', 'Color 4': '#4DB6AC', 'Color 5': '#B2DFDB', 'Color 6': '#003333'},
        'oranges': {'Color 1': '#FF5722', 'Color 2': '#CA9A24', 'Color 3': '#FF9800', 'Color 4': '#FFCC80', 'Color 5': '#FFF3E0', 'Color 6': '#E65100'},
        'peach': {'Color 1': '#FF8A65', 'Color 2': '#FFAB91', 'Color 3': '#FFCCBC', 'Color 4': '#FFE0B2', 'Color 5': '#FFF8F0', 'Color 6': '#FF5722'},
        'purples': {'Color 1': '#4A148C', 'Color 2': '#653972', 'Color 3': '#9C27B0', 'Color 4': '#E1BEE7', 'Color 5': '#F8F5FA', 'Color 6': '#311B92'},
        'reds': {'Color 1': '#CD4E3F', 'Color 2': '#D36F6A', 'Color 3': '#DE8F87', 'Color 4': '#E8B2AA', 'Color 5': '#FFEBEE', 'Color 6': '#C6123C'},
        'rose': {'Color 1': '#C2185B', 'Color 2': '#E91E63', 'Color 3': '#F06292', 'Color 4': '#F8BBD0', 'Color 5': '#FCE4EC', 'Color 6': '#880E4F'},
        'slate': {'Color 1': '#37474F', 'Color 2': '#455A64', 'Color 3': '#607D8B', 'Color 4': '#B0BEC5', 'Color 5': '#ECEFF1', 'Color 6': '#263238'},
        'sunset': {'Color 1': '#FF7043', 'Color 2': '#EF5350', 'Color 3': '#AB47BC', 'Color 4': '#FFB74D', 'Color 5': '#FFEEDD', 'Color 6': '#880E4F'},
        'teal': {'Color 1': '#00796B', 'Color 2': '#00897B', 'Color 3': '#26A69A', 'Color 4': '#80CBC4', 'Color 5': '#E0F2F1', 'Color 6': '#004D40'},
        'yellows': {'Color 1': '#D5A02F', 'Color 2': '#E0A73A', 'Color 3': '#E8B346', 'Color 4': '#F0C355', 'Color 5': '#F8D369', 'Color 6': '#CA9A24'},
    }

    for name, colors in table_palettes.items():
        if language == "es":
            writer.add_h2(f"Paleta: {name.title()}")
            fig = visualize_palette(colors, f"Gradiente: {name}")
            writer.add_plot(fig, caption=f"Visualización de paleta {name}")
            plt.close(fig)
            
            df = pd.DataFrame({
                'Categoría': ['Nivel 1', 'Nivel 2', 'Nivel 3', 'Nivel 4', 'Nivel 5', 'Nivel 6'],
                'Valor': [100, 200, 300, 400, 500, 600],
                'Descripción': ['Detalle A', 'Detalle B', 'Detalle C', 'Detalle D', 'Detalle E', 'Detalle F']
            })
            writer.add_colored_table(df, title=f"Tabla de Ejemplo - {name.title()}", palette_name=name)
        else:
            writer.add_h2(f"Palette: {name.title()}")
            fig = visualize_palette(colors, f"Gradient: {name}")
            writer.add_plot(fig, caption=f"Palette visualization {name}")
            plt.close(fig)
            
            df = pd.DataFrame({
                'Category': ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5', 'Level 6'],
                'Value': [100, 200, 300, 400, 500, 600],
                'Description': ['Detail A', 'Detail B', 'Detail C', 'Detail D', 'Detail E', 'Detail F']
            })
            writer.add_colored_table(df, title=f"Sample Table - {name.title()}", palette_name=name)

    writer.generate(pdf=True, html=True, output_filename=f"{output_dir}/color_palette_catalog{lang_suffix}")

if __name__ == "__main__":
    # Generate Spanish versions
    generate_layout_samples("es")
    generate_color_catalog("es")
    
    # Generate English versions
    generate_layout_samples("en")
    generate_color_catalog("en")

    print(f"\n✅ Catálogo bilingüe generado exitosamente en: {os.path.abspath(output_dir)}")
