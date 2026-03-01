"""
Script para crear ejecutable con PyInstaller
Optimizado para tamaño mínimo
"""

import subprocess
import sys
import os

def main():
    print("=" * 60)
    print("  CRONUX-CRX - CREAR EJECUTABLE CON PYINSTALLER")
    print("=" * 60)
    print()
    
    # Instalar PyInstaller
    print("[1/3] Instalando PyInstaller...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "customtkinter", "Pillow", "--quiet"])
    print("✓ PyInstaller instalado")
    
    # Verificar archivos necesarios
    print("\n[1.5/3] Verificando archivos...")
    required_files = [
        "cli/cronux_cli.py",
        "cli/utilidades.py", 
        "cli/eliminar_proyecto.py",
        "assets/cronux_cli.png"
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"[WARNING] Archivo no encontrado: {file}")
    
    print("✓ Verificación completa")
    
    # Crear ejecutable
    print("\n[2/3] Compilando ejecutable...")
    print("Esto puede tardar 2-3 minutos...\n")
    
    cmd = [
        "pyinstaller",
        "--onefile",                    # Un solo archivo
        "--windowed",                   # Sin consola (GUI)
        "--noupx",                      # Sin compresión UPX (evita antivirus)
        "--name=Cronux-CRX-Installer",  # Nombre del ejecutable
        "--add-data=cli;cli",           # Incluir carpeta cli
        "--add-data=assets;assets",     # Incluir carpeta assets
        "--icon=assets/cronux_cli.png", # Icono (si existe)
        "--clean",                      # Limpiar cache
        "--noconfirm",                  # No pedir confirmación
        "installer_gui.py"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print("\n❌ ERROR: Compilacion fallida")
        input("Presiona Enter para salir...")
        sys.exit(1)
    
    print("\n✓ Compilacion exitosa")
    
    # Limpiar
    print("\n[3/3] Limpiando archivos temporales...")
    import shutil
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("Cronux-CRX-Installer.spec"):
        os.remove("Cronux-CRX-Installer.spec")
    print("✓ Limpieza completa")
    
    # Resultado
    print("\n" + "=" * 60)
    print("  ✓ EXITO!")
    print("=" * 60)
    print("\nEjecutable creado en:")
    print("  dist\\Cronux-CRX-Installer.exe")
    print("\nCaracterísticas:")
    print("  • Un solo archivo ejecutable")
    print("  • Solicita permisos de administrador")
    print("  • Muestra mensaje explicando por qué")
    print("  • Interfaz gráfica profesional")
    print("  • Incluye todas las mejoras v0.1.0 Beta:")
    print("    - Compresión automática")
    print("    - Sistema .cronuxignore")
    print("    - Backups automáticos")
    print("    - Comando 'crx fin'")
    print("\nPruébalo:")
    print("  1. Ejecuta dist\\Cronux-CRX-Installer.exe")
    print("  2. Acepta permisos de administrador")
    print("  3. Click en 'Instalar'")
    print("\nPara distribuir:")
    print("  • Sube solo: Cronux-CRX-Installer.exe")
    print("  • Tamaño: ~25-30 MB")
    print("\nEnviar a Microsoft (evitar alertas):")
    print("  https://www.microsoft.com/en-us/wdsi/filesubmission")
    print("\n" + "=" * 60)
    
    input("\nPresiona Enter para salir...")

if __name__ == "__main__":
    main()
