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
    Modo silencioso para instalación automática con pip.
    """
    # Detectar si estamos en instalación automática (sin terminal interactivo)
    is_interactive = sys.stdin.isatty() and sys.stdout.isatty()
    
    print("\n" + "="*60)
    print("🚀 ePy_docs - Post-instalación")
    print("="*60 + "\n")
    
    # Importar los módulos de instalación
    try:
        from ePy_docs.scripts.install_deps import check_quarto_installed, check_tinytex_installed
        from ePy_docs.scripts.install_latex_packages import check_latex_packages
    except ImportError as e:
        print(f"⚠️  Error al importar scripts de instalación: {e}")
        print("\n💡 Para configurar manualmente, ejecute después:")
        print("   epy-docs-setup")
        return
    
    # Verificar qué falta instalar
    needs_quarto = not check_quarto_installed()
    needs_tinytex = not check_tinytex_installed()
    needs_latex = not check_latex_packages()
    
    if not (needs_quarto or needs_tinytex or needs_latex):
        print("✅ Todas las dependencias ya están instaladas.")
        print("\n📚 ePy_docs está listo para usar!")
        return
    
    print("📦 Dependencias detectadas:")
    if needs_quarto:
        print("   ❌ Quarto (requerido para generación de documentos)")
    else:
        print("   ✅ Quarto instalado")
    
    if needs_tinytex:
        print("   ❌ TinyTeX (distribución LaTeX)")
    else:
        print("   ✅ TinyTeX instalado")
    
    if needs_latex:
        print("   ❌ Paquetes LaTeX (17 paquetes necesarios)")
    else:
        print("   ✅ Paquetes LaTeX instalados")
    
    print()
    
    # En modo no interactivo, solo informar
    if not is_interactive:
        print("⚠️  Instalación detectada en modo no interactivo.")
        print("📋 Para completar la configuración, ejecute:")
        print()
        if needs_quarto or needs_tinytex:
            print("   epy-docs-install   # Instalar Quarto y TinyTeX")
        if needs_latex:
            print("   epy-docs-latex     # Instalar paquetes LaTeX")
        print()
        print("   O use el asistente completo:")
        print("   epy-docs-setup")
        return
    
    # En modo interactivo, preguntar
    try:
        print("🔧 ¿Desea instalar las dependencias faltantes ahora?")
        response = input("   [S/n]: ").strip().lower()
        if response == 'n' or response == 'no':
            print("\n⏭️  Instalación omitida.")
            print("\n💡 Para instalar más tarde, ejecute:")
            if needs_quarto or needs_tinytex:
                print("   epy-docs-install")
            if needs_latex:
                print("   epy-docs-latex")
            return
    except (KeyboardInterrupt, EOFError):
        print("\n\n⏭️  Instalación cancelada.")
        print("\n💡 Para instalar más tarde, ejecute: epy-docs-setup")
        return
    
    # Ejecutar instalaciones
    from ePy_docs.scripts.install_deps import main as install_deps
    from ePy_docs.scripts.install_latex_packages import main as install_latex
    
    if needs_quarto or needs_tinytex:
        print("\n" + "-"*60)
        print("📥 Instalando Quarto y TinyTeX...")
        print("-"*60 + "\n")
        try:
            install_deps()
        except Exception as e:
            print(f"\n⚠️  Error: {e}")
            print("💡 Intente manualmente: epy-docs-install")
    
    if needs_latex:
        print("\n" + "-"*60)
        print("📥 Instalando paquetes LaTeX...")
        print("-"*60 + "\n")
        try:
            install_latex()
        except Exception as e:
            print(f"\n⚠️  Error: {e}")
            print("💡 Intente manualmente: epy-docs-latex")
    
    print("\n" + "="*60)
    print("✅ Configuración completada")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
