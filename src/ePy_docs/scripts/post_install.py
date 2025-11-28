"""
Script de post-instalación para ePy_docs.
Se ejecuta automáticamente después de instalar el paquete con pip.
"""
import sys
import subprocess
import os


def main():
    """
    Ejecuta los scripts de instalación de dependencias automáticamente.
    """
    print("\n" + "="*60)
    print("🚀 Configurando ePy_docs...")
    print("="*60 + "\n")
    
    # Importar los módulos de instalación
    try:
        from ePy_docs.scripts.install_deps import main as install_deps
        from ePy_docs.scripts.install_latex_packages import main as install_latex
    except ImportError as e:
        print(f"⚠️  Error al importar scripts de instalación: {e}")
        return
    
    # Preguntar al usuario si desea instalar las dependencias
    print("📦 ePy_docs requiere las siguientes dependencias externas:")
    print("   - Quarto (para generación de documentos)")
    print("   - TinyTeX (distribución LaTeX)")
    print("   - Paquetes LaTeX (17 paquetes necesarios)")
    print()
    
    # En instalación automática, intentar instalar sin preguntar
    # El usuario puede cancelar con Ctrl+C si lo desea
    try:
        response = input("¿Desea instalar estas dependencias ahora? [S/n]: ").strip().lower()
        if response == 'n' or response == 'no':
            print("\n⏭️  Instalación de dependencias omitida.")
            print("💡 Ejecute manualmente cuando lo necesite:")
            print("   epy-docs-install   # Para Quarto y TinyTeX")
            print("   epy-docs-latex     # Para paquetes LaTeX")
            return
    except (KeyboardInterrupt, EOFError):
        print("\n\n⏭️  Instalación de dependencias cancelada.")
        print("💡 Ejecute manualmente cuando lo necesite:")
        print("   epy-docs-install   # Para Quarto y TinyTeX")
        print("   epy-docs-latex     # Para paquetes LaTeX")
        return
    
    print("\n" + "-"*60)
    print("📥 Instalando Quarto y TinyTeX...")
    print("-"*60 + "\n")
    
    try:
        install_deps()
    except Exception as e:
        print(f"\n⚠️  Error durante la instalación de Quarto/TinyTeX: {e}")
        print("💡 Puede intentar instalar manualmente con: epy-docs-install")
    
    print("\n" + "-"*60)
    print("📥 Instalando paquetes LaTeX...")
    print("-"*60 + "\n")
    
    try:
        install_latex()
    except Exception as e:
        print(f"\n⚠️  Error durante la instalación de paquetes LaTeX: {e}")
        print("💡 Puede intentar instalar manualmente con: epy-docs-latex")
    
    print("\n" + "="*60)
    print("✅ Configuración de ePy_docs completada")
    print("="*60 + "\n")
    print("💡 Si hubo algún error, puede ejecutar manualmente:")
    print("   epy-docs-install   # Para Quarto y TinyTeX")
    print("   epy-docs-latex     # Para paquetes LaTeX")
    print()


if __name__ == "__main__":
    main()
