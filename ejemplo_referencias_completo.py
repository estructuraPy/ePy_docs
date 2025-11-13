#!/usr/bin/env python3
"""
Ejemplo completo del sistema de referencias bibliográficas de ePy_docs.
Demuestra cómo configurar y usar referencias de forma automática.
"""

import sys
from pathlib import Path
import pandas as pd

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from ePy_docs import DocumentWriter


def ejemplo_completo_referencias():
    """Ejemplo completo con referencias bibliográficas."""
    
    print("=== EJEMPLO COMPLETO: SISTEMA DE REFERENCIAS ===")
    
    # Crear writer con configuración corporativa
    writer = DocumentWriter(
        document_type='report',
        layout_style='classic'
    )
    
    # Configurar referencias IEEE - Los archivos se copian automáticamente
    writer.configure_references(
        csl_style='ieee',
        bibliography_file=None  # Usa bibliografía por defecto
    )
    
    # Agregar contenido del documento
    writer.add_h1("Informe Técnico con Referencias")
    
    writer.add_text("Este documento demuestra el uso del sistema de referencias bibliográficas de ePy_docs. ")
    writer.add_text("Las referencias se configuran automáticamente y los archivos necesarios se copian al directorio de salida.")
    
    # Sección con múltiples citas
    writer.add_h2("Marco Teórico")
    
    writer.add_text("Los fundamentos de la física moderna fueron establecidos por varios científicos destacados. ")
    writer.add_text("Einstein desarrolló la teoría de la relatividad ")
    writer.add_citation("Einstein1905")
    writer.add_text(", mientras que Newton había previamente formulado las leyes del movimiento ")
    writer.add_citation("Newton1687", page="142")
    writer.add_text(".")
    
    writer.add_text("En el campo del electromagnetismo, Maxwell contribuyó significativamente ")
    writer.add_citation("Maxwell1865")
    writer.add_text(", y los métodos matemáticos de Gauss ")
    writer.add_citation("Gauss1809")
    writer.add_text(" siguen siendo fundamentales en la física teórica.")
    
    # Agregar una tabla con datos
    writer.add_h2("Datos Experimentales")
    
    data = {
        'Experimento': ['Exp-001', 'Exp-002', 'Exp-003'],
        'Valor Medido': [1.234, 2.567, 3.890],
        'Error (±)': [0.005, 0.008, 0.012],
        'Referencia': ['[@Einstein1905]', '[@Newton1687]', '[@Maxwell1865]']
    }
    
    df = pd.DataFrame(data)
    writer.add_table(df, title="Resultados experimentales con referencias")
    
    # Sección de metodología
    writer.add_h2("Metodología")
    
    writer.add_text("La metodología utilizada se basa en los principios establecidos por ")
    writer.add_citation("Gauss1809", page="15-18")
    writer.add_text(" y las técnicas modernas descritas en ")
    writer.add_citation("Einstein1905")
    writer.add_text(".")
    
    # Lista con referencias integradas
    writer.add_h3("Pasos del Proceso")
    
    pasos = [
        "Aplicar principios de Newton [@Newton1687, p. 25]",
        "Utilizar ecuaciones de Maxwell [@Maxwell1865]", 
        "Verificar con teoría de Einstein [@Einstein1905, p. 891]",
        "Analizar con métodos de Gauss [@Gauss1809, p. 42-45]"
    ]
    
    writer.add_numbered_list(pasos)
    
    # Sección de conclusiones
    writer.add_h2("Conclusiones")
    
    writer.add_text("Los resultados obtenidos confirman las predicciones teóricas establecidas en la literatura ")
    writer.add_citation("Einstein1905")
    writer.add_text(", ")
    writer.add_citation("Newton1687")
    writer.add_text(", ")
    writer.add_citation("Maxwell1865")
    writer.add_text(".")
    
    # Nota sobre referencias automáticas
    writer.add_note(
        "Las referencias bibliográficas se manejan automáticamente. " +
        "ePy_docs copia los archivos CSL y de bibliografía al directorio de salida " +
        "y configura Quarto para usarlos correctamente.",
        title="Sistema de Referencias Automático"
    )
    
    # Generar documentos
    print("\nGenerando documentos con referencias...")
    
    try:
        result = writer.generate(
            html=True,
            pdf=True,  # Incluir PDF para demostración completa
            qmd=True,
            output_filename="ejemplo_referencias_completo"
        )
        
        print("✅ Documentos generados exitosamente!")
        
        for format_name, file_path in result.items():
            if file_path:
                print(f"   {format_name.upper()}: {file_path}")
        
        # Verificar archivos copiados
        output_dir = Path(result['qmd']).parent
        print(f"\n📁 Archivos en directorio de salida ({output_dir}):")
        
        for pattern in ["*.csl", "*.bib"]:
            files = list(output_dir.glob(pattern))
            for file in files:
                print(f"   ✅ {file.name}")
        
        # Contar citas en el archivo QMD
        qmd_path = Path(result['qmd'])
        if qmd_path.exists():
            content = qmd_path.read_text(encoding='utf-8')
            citation_count = content.count('[@')
            print(f"\n📚 Citas encontradas en el documento: {citation_count}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error durante la generación: {e}")
        import traceback
        traceback.print_exc()
        return False


def ejemplo_diferentes_estilos():
    """Ejemplo con diferentes estilos de citas."""
    
    print("\n=== EJEMPLO: DIFERENTES ESTILOS DE CITAS ===")
    
    estilos = {
        'ieee': 'IEEE (numérico)',
        'apa': 'APA 7ª Edición',
        'chicago': 'Chicago Manual of Style'
    }
    
    for estilo, descripcion in estilos.items():
        print(f"\nGenerando documento con estilo {descripcion}...")
        
        writer = DocumentWriter(document_type='report')
        writer.configure_references(csl_style=estilo)
        
        writer.add_h1(f"Documento con Estilo {descripcion}")
        writer.add_text("Este documento utiliza el estilo de citas ")
        writer.add_text(f"{descripcion}. ")
        writer.add_text("Ejemplo de cita: ")
        writer.add_citation("Einstein1905")
        writer.add_text(".")
        
        writer.add_h2("Múltiples Referencias")
        writer.add_text("Varios autores han contribuido al tema ")
        writer.add_citation("Newton1687")
        writer.add_text(", ")
        writer.add_citation("Maxwell1865")
        writer.add_text(", y ")
        writer.add_citation("Gauss1809")
        writer.add_text(".")
        
        try:
            result = writer.generate(
                html=True,
                pdf=False,  # Solo HTML para rapidez
                qmd=True,
                output_filename=f"ejemplo_estilo_{estilo}"
            )
            
            print(f"   ✅ Generado: {result['html']}")
            
        except Exception as e:
            print(f"   ❌ Error con estilo {estilo}: {e}")


if __name__ == "__main__":
    success = ejemplo_completo_referencias()
    ejemplo_diferentes_estilos()
    
    if success:
        print("\n🎉 ¡Ejemplos completados exitosamente!")
        print("📖 Los archivos HTML generados muestran las referencias formateadas correctamente.")
        print("📁 Los archivos CSL y de bibliografía se copiaron automáticamente.")
    else:
        print("\n❌ Error en los ejemplos.")