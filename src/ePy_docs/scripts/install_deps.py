#!/usr/bin/env python
"""
Script de instalación automática de dependencias externas para ePy_docs.
Instala Quarto y TinyTeX si no están disponibles.
"""

import subprocess
import sys
import platform
import shutil
from pathlib import Path
from tqdm import tqdm
import time


def check_command(command):
    """Verifica si un comando está disponible en el sistema."""
    return shutil.which(command) is not None


def install_quarto():
    """Instala Quarto según el sistema operativo."""
    system = platform.system()
    
    print("📦 Instalando Quarto...")
    
    if system == "Windows":
        print("⚠️  Para Windows, descarga Quarto desde: https://quarto.org/docs/get-started/")
        print("    O instala con winget: winget install --id Posit.Quarto")
        return False
    
    elif system == "Darwin":  # macOS
        try:
            subprocess.run(["brew", "install", "quarto"], check=True)
            print("✅ Quarto instalado correctamente")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error instalando Quarto con Homebrew")
            print("   Instala manualmente desde: https://quarto.org/docs/get-started/")
            return False
        except FileNotFoundError:
            print("❌ Homebrew no encontrado")
            print("   Instala Quarto manualmente desde: https://quarto.org/docs/get-started/")
            return False
    
    elif system == "Linux":
        print("⚠️  Para Linux, descarga Quarto desde: https://quarto.org/docs/get-started/")
        print("    O usa el gestor de paquetes de tu distribución")
        return False
    
    return False


def install_tinytex():
    """Instala TinyTeX usando Quarto."""
    if not check_command("quarto"):
        print("❌ Quarto no está instalado. Instálalo primero.")
        return False
    
    print("📦 Instalando TinyTeX (esto puede tomar varios minutos)...")
    
    try:
        # Crear una barra de progreso falsa ya que no podemos capturar progreso real
        with tqdm(total=100, desc="TinyTeX", bar_format='{l_bar}{bar}| {elapsed}') as pbar:
            process = subprocess.Popen(
                ["quarto", "install", "tinytex"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Simular progreso mientras el proceso corre
            while process.poll() is None:
                time.sleep(0.5)
                if pbar.n < 90:
                    pbar.update(2)
            
            pbar.n = 100
            pbar.refresh()
        
        if process.returncode == 0:
            print("✅ TinyTeX instalado correctamente")
            return True
        else:
            print("❌ Error instalando TinyTeX")
            return False
            
    except Exception as e:
        print(f"❌ Error instalando TinyTeX: {e}")
        print("   Intenta manualmente: quarto install tinytex")
        return False


def check_installations():
    """Verifica qué dependencias están instaladas."""
    quarto_installed = check_command("quarto")
    
    # Verificar TinyTeX (buscar pdflatex)
    tinytex_installed = check_command("pdflatex") or check_command("xelatex")
    
    return {
        "quarto": quarto_installed,
        "tinytex": tinytex_installed
    }


def main():
    """Función principal del script de instalación."""
    print("=" * 60)
    print("ePy_docs - Instalación de dependencias externas")
    print("=" * 60)
    
    # Verificar instalaciones actuales
    status = check_installations()
    
    print("\n📋 Estado actual:")
    print(f"  Quarto:  {'✅ Instalado' if status['quarto'] else '❌ No instalado'}")
    print(f"  TinyTeX: {'✅ Instalado' if status['tinytex'] else '❌ No instalado'}")
    
    # Instalar Quarto si no está
    if not status["quarto"]:
        print("\n🔧 Quarto no encontrado")
        install_quarto()
        # Revalidar
        status = check_installations()
    
    # Instalar TinyTeX si no está
    if not status["tinytex"]:
        print("\n🔧 TinyTeX no encontrado")
        if status["quarto"]:
            response = input("¿Deseas instalar TinyTeX ahora? (s/n): ")
            if response.lower() in ['s', 'y', 'si', 'yes']:
                install_tinytex()
        else:
            print("⚠️  Quarto debe estar instalado antes de instalar TinyTeX")
    
    # Estado final
    print("\n" + "=" * 60)
    final_status = check_installations()
    
    if final_status["quarto"] and final_status["tinytex"]:
        print("✅ Todas las dependencias están instaladas correctamente")
        print("   Puedes generar documentos PDF con ePy_docs")
    else:
        print("⚠️  Algunas dependencias no están instaladas:")
        if not final_status["quarto"]:
            print("   - Quarto: https://quarto.org/docs/get-started/")
        if not final_status["tinytex"]:
            print("   - TinyTeX: Ejecuta 'quarto install tinytex' después de instalar Quarto")
        print("\n   Sin estas dependencias, solo podrás generar HTML y DOCX")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
