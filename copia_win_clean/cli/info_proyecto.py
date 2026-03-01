import json
from pathlib import Path
from funcion_verficar import verificarCronux, obtener_ruta_proyecto_json, obtener_ruta_cronux

def calcular_tamaño_directorio(directorio):
    """Calcula el tamaño total de un directorio en bytes"""
    tamaño_total = 0
    try:
        for item in directorio.rglob('*'):
            if item.is_file() and not str(item.relative_to(directorio)).startswith('.cronux'):
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

def info_proyecto():
    """Muestra información del proyecto Cronux"""
    # 1. Verificar si existe proyecto Cronux
    if not verificarCronux():
        print("No estamos en un proyecto Cronux")
        print("Usa 'cronux new <nombre>' para crear uno")
        return
    
    # 2. Leer el JSON
    archivo_proyecto = obtener_ruta_proyecto_json()

    if archivo_proyecto.exists():
        with open(archivo_proyecto, "r") as f:
            datos = json.load(f)

        # 3. Mostrar información del proyecto
        print("INFORMACION DEL PROYECTO CRONUX")
        print("=" * 40)
        print(f"Nombre: {datos.get('nombre', 'Sin nombre')}")
        print(f"Fecha de creación: {datos.get('fecha_creacion', 'Desconocida')}")
        print(f"Autor: {datos.get('autor', 'Desconocido')}")
        print(f"Ubicación: {Path.cwd()}")
        
        # Calcular y mostrar tamaño del proyecto actual
        tamaño_actual = calcular_tamaño_directorio(Path.cwd())
        tamaño_formateado = formatear_tamaño(tamaño_actual)
        print(f"Tamaño actual del proyecto: {tamaño_formateado}")
        
        # 4. Información de versiones
        carpeta_versiones = obtener_ruta_cronux() / "versiones"
        if carpeta_versiones.exists():
            versiones = list(carpeta_versiones.glob("version_*"))
            print(f"Versiones guardadas: {len(versiones)}")
            
            if versiones:
                # Mostrar última versión
                versiones_ordenadas = []
                for version_dir in versiones:
                    try:
                        numero = version_dir.name.replace("version_", "")
                        if "." in numero:
                            mayor, menor = numero.split(".")
                            versiones_ordenadas.append((int(mayor), int(menor), numero))
                        else:
                            versiones_ordenadas.append((int(numero), 0, numero))
                    except ValueError:
                        continue
                
                if versiones_ordenadas:
                    versiones_ordenadas.sort()
                    ultima_version = versiones_ordenadas[-1][2]
                    print(f"Ultima version: {ultima_version}")
        else:
            print("Versiones guardadas: 0")
        
        print("\nComandos disponibles:")
        print("  crx save -m 'mensaje'  # Guardar nueva versión")
        print("  crx log                # Ver historial")
        print("  crx restore <version>  # Restaurar versión")
        print("  crx fin                # Eliminar proyecto")
        
    else:
        print("ERROR: No se pudo leer la información del proyecto")
        print("El archivo proyecto.json no existe o está corrupto")