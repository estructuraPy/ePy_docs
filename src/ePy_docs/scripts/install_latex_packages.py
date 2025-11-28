#!/usr/bin/env python
"""
Script para instalar paquetes LaTeX requeridos por ePy_docs.
Instala automáticamente los paquetes faltantes usando tlmgr (TinyTeX).
"""

import subprocess
import sys
import shutil
from tqdm import tqdm


def check_tlmgr():
    """Verifica si tlmgr está disponible."""
    return shutil.which("tlmgr") is not None


def install_latex_package(package_name):
    """Instala un paquete LaTeX usando tlmgr."""
    try:
        subprocess.run(
            ["tlmgr", "install", package_name],
            check=True,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    """Instala todos los paquetes LaTeX requeridos."""
    print("=" * 60)
    print("ePy_docs - Instalación de paquetes LaTeX")
    print("=" * 60)
    
    if not check_tlmgr():
        print("❌ tlmgr no encontrado")
        print("   Instala TinyTeX primero: quarto install tinytex")
        print("   O ejecuta: epy-docs-install")
        sys.exit(1)
    
    # Lista de paquetes LaTeX requeridos
    required_packages = [
        "fancyhdr",        # Headers y footers personalizados
        "titlesec",        # Formato de títulos
        "tcolorbox",       # Cajas de colores (callouts)
        "environ",         # Entornos personalizados
        "pgf",             # Gráficos
        "listings",        # Bloques de código
        "fancyvrb",        # Verbatim mejorado (highlighting)
        "framed",          # Marcos para código
        "caption",         # Subtítulos personalizados
        "float",           # Control de flotantes
        "hyperref",        # Enlaces e hipervínculos
        "bookmark",        # Marcadores PDF
        "xurl",            # URLs con saltos de línea
        "csquotes",        # Citas contextuales
        "biblatex",        # Bibliografía
        "biber",           # Motor bibliográfico
    ]
    
    print(f"\n📋 Instalando {len(required_packages)} paquetes LaTeX...\n")
    
    failed = []
    
    # Barra de progreso
    with tqdm(total=len(required_packages), desc="Instalando", unit="pkg") as pbar:
        for package in required_packages:
            pbar.set_description(f"Instalando {package[:15]:<15}")
            if install_latex_package(package):
                pbar.set_postfix_str(f"✓ {package}")
            else:
                pbar.set_postfix_str(f"✗ {package}")
                failed.append(package)
            pbar.update(1)
    
    print("\n" + "=" * 60)
    if not failed:
        print("✅ Todos los paquetes LaTeX instalados correctamente")
        print("   ePy_docs está listo para generar PDFs")
    else:
        print(f"⚠️  {len(failed)} paquete(s) fallaron:")
        for pkg in failed:
            print(f"   - {pkg}")
        print("\n   Intenta instalarlos manualmente:")
        print(f"   tlmgr install {' '.join(failed)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
