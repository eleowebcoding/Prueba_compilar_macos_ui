"""
Comando para eliminar completamente un proyecto Cronux-CRX
"""
from pathlib import Path
import shutil
from funcion_verficar import verificarCronux, obtener_ruta_cronux, obtener_ruta_proyecto_json
import json

def eliminar_proyecto_cli():
    """Elimina completamente el proyecto Cronux-CRX"""
    
    # Verificar que estamos en un proyecto
    if not verificarCronux():
        print("ERROR: No estás en un proyecto Cronux-CRX")
        return False
    
    # Obtener información del proyecto
    archivo_proyecto = obtener_ruta_proyecto_json()
    nombre_proyecto = "Desconocido"
    
    if archivo_proyecto.exists():
        try:
            with open(archivo_proyecto, "r") as f:
                datos = json.load(f)
                nombre_proyecto = datos.get('nombre', 'Desconocido')
        except Exception:
            pass
    
    # Contar versiones
    carpeta_cronux = obtener_ruta_cronux()
    carpeta_versiones = carpeta_cronux / "versiones"
    num_versiones = 0
    
    if carpeta_versiones.exists():
        num_versiones = len(list(carpeta_versiones.glob("version_*")))
    
    # Mostrar información
    print("=" * 50)
    print("[!] ELIMINAR PROYECTO CRONUX-CRX")
    print("=" * 50)
    print(f"Proyecto: {nombre_proyecto}")
    print(f"Ubicación: {Path.cwd()}")
    print(f"Versiones guardadas: {num_versiones}")
    print()
    print("ADVERTENCIA: Esta acción eliminará:")
    print("  * Todas las versiones guardadas")
    print("  * Todo el historial del proyecto")
    print("  * La carpeta .cronux completa")
    print()
    print("Los archivos actuales del proyecto NO se eliminarán.")
    print("=" * 50)
    
    # Primera confirmación
    respuesta1 = input("\n¿Estás seguro de eliminar este proyecto? (escribe 'SI' para confirmar): ")
    
    if respuesta1.strip() != "SI":
        print("Operación cancelada")
        return False
    
    # Segunda confirmación
    print()
    respuesta2 = input(f"Escribe el nombre del proyecto '{nombre_proyecto}' para confirmar: ")
    
    if respuesta2.strip() != nombre_proyecto:
        print("El nombre no coincide. Operación cancelada")
        return False
    
    # Eliminar carpeta .cronux
    try:
        print()
        print("Eliminando proyecto Cronux-CRX...")
        shutil.rmtree(carpeta_cronux)
        
        print()
        print("[OK] Proyecto Cronux-CRX eliminado exitosamente")
        print(f"[OK] Se eliminaron {num_versiones} versiones")
        print()
        print("Los archivos de tu proyecto siguen intactos.")
        print("Puedes crear un nuevo proyecto con: crx new <nombre>")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Error al eliminar el proyecto: {e}")
        return False