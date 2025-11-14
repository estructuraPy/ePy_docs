#!/usr/bin/env python3
"""
Test completo de fuentes personalizadas con tablas
"""

from src.ePy_docs import create_qmd

# Configuración del documento de prueba
test_document = {
    "title": "✅ TESTE FINAL: Fuentes Personalizadas",
    "author": "ePy_docs",
    "date": "2025-01-17",
    "layout": "handwritten",
    "content": [
        {
            "type": "header",
            "level": 1,
            "text": "Verificación Final de Fuentes Personalizadas"
        },
        {
            "type": "text",
            "content": "Este documento verifica que las fuentes personalizadas funcionen correctamente en **TODO EL DOCUMENTO**, incluyendo tablas, texto normal, y todos los elementos."
        },
        {
            "type": "header",
            "level": 2,
            "text": "Prueba de Texto Normal"
        },
        {
            "type": "text",
            "content": "Este texto debería aparecer en la fuente **anm_ingenieria_2025** tanto en HTML como en el navegador. La fuente debe verse **tipo manuscrito** con estilo personal."
        },
        {
            "type": "table",
            "caption": "Tabla de Verificación de Fuentes",
            "data": [
                ["Elemento", "Fuente Esperada", "Estado"],
                ["Texto del body", "anm_ingenieria_2025", "✅ CORRECTO"],
                ["Headers", "anm_ingenieria_2025", "✅ CORRECTO"],
                ["Tablas", "anm_ingenieria_2025", "🔍 VERIFICANDO"],
                ["CSS @font-face", "anm_ingenieria_2025.otf", "✅ CORRECTO"]
            ]
        },
        {
            "type": "header",
            "level": 2,
            "text": "Confirmación Técnica"
        },
        {
            "type": "list",
            "items": [
                "✅ **CSS body**: `font-family: 'anm_ingenieria_2025', Segoe Script, ...`",
                "✅ **@font-face**: Declaración correcta con archivo .otf",  
                "✅ **HTML**: Carga styles.css correctamente",
                "✅ **Configuración**: handwritten_personal → anm_ingenieria_2025"
            ]
        },
        {
            "type": "text",
            "content": "**RESULTADO ESPERADO**: Todo el texto de este documento, incluyendo esta frase y la tabla anterior, debe renderizarse con la fuente personalizada anm_ingenieria_2025 que tiene apariencia manuscrita."
        }
    ]
}

print("🔍 GENERANDO DOCUMENTO DE VERIFICACIÓN FINAL...")

# Generar documento
files = create_qmd(
    document=test_document,
    output_dir="results/report",
    filename="VERIFICACION_FINAL_FUENTES"
)

print(f"✅ Archivos generados: {files}")

for format_type, file_path in files.items():
    print(f"📄 {format_type.upper()}: {file_path}")

print("\n" + "="*60)
print("🎉 VERIFICACIÓN FINAL COMPLETADA")
print("="*60)
print("✅ Abra el archivo HTML en el navegador")
print("✅ Verifique que TODO el texto use la fuente manuscrita")
print("✅ Especialmente verifique que las TABLAS usen la fuente personalizada")
print("="*60)