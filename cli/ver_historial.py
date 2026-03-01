from pathlib import Path
import json
from funcion_verficar import *

def calcular_tamaño_directorio(directorio):
    """Calcula el tamaño total de un directorio en bytes"""
    tamaño_total = 0
    try:
        for item in directorio.rglob('*'):
            if item.is_file():
                tamaño_total += item.stat().st_size
    except Exception:
        pass
    return tamaño_total

def formatear_tamaño(bytes_size):
    """Convierte bytes a formato legible (KB, MB, GB)"""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / (1024 * 1024):.1f} MB"
    else:
        return f"{bytes_size / (1024 * 1024 * 1024):.1f} GB"

def ver_historial_cli():
    """Versión CLI para mostrar historial"""
    if not verificarCronux():
        print("ERROR: No estas en un proyecto Cronux")
        return False
    
    carpeta_versiones = obtener_ruta_cronux() / "versiones"

    if not carpeta_versiones.exists():
        print("INFO: No hay versiones guardadas")
        return False
    
    versiones = list(carpeta_versiones.glob("version_*"))
    
    if not versiones:
        print("INFO: No hay versiones guardadas")
        return False

    print("HISTORIAL DE VERSIONES:")
    print("=" * 50)
    
    # Ordenar versiones
    versiones_ordenadas = []
    for version_dir in versiones:
        try:
            numero = version_dir.name.replace("version_", "")
            if "." in numero:
                mayor, menor = numero.split(".")
                versiones_ordenadas.append((int(mayor), int(menor), version_dir))
            else:
                versiones_ordenadas.append((int(numero), 0, version_dir))
        except ValueError:
            continue
    
    versiones_ordenadas.sort(reverse=True)
    
    for mayor, menor, version_dir in versiones_ordenadas:
        metadatos_file = version_dir / "metadatos.json"
        
        if metadatos_file.exists():
            try:
                with open(metadatos_file, "r") as f:
                    metadatos = json.load(f)
                
                print(f"Version: {metadatos['version']}")
                print(f"Fecha: {metadatos['fecha']}")
                print(f"Mensaje: {metadatos['mensaje']}")
                print(f"Archivos: {metadatos.get('archivos_guardados', 'N/A')}")
                
                # Mostrar tamaño si está disponible
                if 'tamaño_formateado' in metadatos:
                    print(f"Tamaño: {metadatos['tamaño_formateado']}")
                elif 'tamaño_bytes' in metadatos:
                    # Formatear tamaño si solo tenemos bytes
                    tamaño_formateado = formatear_tamaño(metadatos['tamaño_bytes'])
                    print(f"Tamaño: {tamaño_formateado}")
                else:
                    # Calcular tamaño si no está en metadatos (versiones antiguas)
                    try:
                        tamaño_bytes = calcular_tamaño_directorio(version_dir)
                        tamaño_formateado = formatear_tamaño(tamaño_bytes)
                        print(f"Tamaño: {tamaño_formateado}")
                    except:
                        print("Tamaño: N/A")
                
                print("-" * 30)
                
            except Exception as e:
                print(f"Error leyendo metadatos de {version_dir.name}: {e}")
        else:
            print(f"Version: {version_dir.name.replace('version_', '')}")
            print("Metadatos no disponibles")
            # Intentar calcular tamaño aunque no haya metadatos
            try:
                tamaño_bytes = calcular_tamaño_directorio(version_dir)
                tamaño_formateado = formatear_tamaño(tamaño_bytes)
                print(f"Tamaño: {tamaño_formateado}")
            except:
                print("Tamaño: N/A")
            print("-" * 30)
    
    return True