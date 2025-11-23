"""Test para verificar que add_project_info genera listas en lugar de tablas."""

from pathlib import Path
from ePy_docs import DocumentWriter

def test_project_info_lists():
    """Prueba básica de información de proyecto como listas."""
    
    # Crear writer
    writer = DocumentWriter(
        layout_style="professional",
        document_type="report",
        language="es"
    )
    
    # Configurar información del proyecto
    writer.set_project_info(
        code="PROJ-2024-001",
        name="Análisis Estructural de Puente",
        project_type="Ingeniería Civil",
        status="En Progreso",
        description="Análisis de capacidad de carga y estabilidad estructural",
        created_date="21 de noviembre de 2024",
        location="Ciudad de México"
    )
    
    # Configurar autores
    writer.set_author(
        name="Ing. Juan Pérez",
        role="Ingeniero Principal",
        affiliation="Universidad Nacional",
        contact="juan.perez@example.com"
    )
    
    # Configurar cliente
    writer.set_client_info(
        name="María García",
        company="Constructora ABC S.A.",
        contact="+52 55 1234 5678",
        address="Av. Principal 123, Ciudad de México"
    )
    
    # Agregar información del proyecto como listas
    writer.add_h1("Información del Proyecto")
    writer.add_project_info("project")
    
    writer.add_h1("Autores del Documento")
    writer.add_project_info("authors")
    
    writer.add_h1("Información del Cliente")
    writer.add_project_info("client")
    
    # Agregar contenido adicional
    writer.add_h1("Introducción")
    writer.add_text(
        "Este documento presenta el análisis estructural realizado para el puente. "
        "La información del proyecto se presenta en formato de lista para mejor legibilidad."
    )
    
    # Generar solo HTML para verificación rápida
    output_dir = Path(__file__).parent / "results" / "test_project_lists"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    result = writer.generate(
        output_path=output_dir / "test_project_info_lists.qmd",
        output_formats=["html"]
    )
    
    print("✅ Documento generado exitosamente:")
    for fmt, path in result.items():
        print(f"  - {fmt}: {path}")
    
    return result

if __name__ == "__main__":
    test_project_info_lists()
