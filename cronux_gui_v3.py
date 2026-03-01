#!/usr/bin/env python3
"""
Cronux-CRX GUI v3 - Interfaz gráfica con diseño personalizado
Sistema de control de versiones local
"""

import flet as ft
import json
import os
from pathlib import Path
from datetime import datetime
import shutil
import sys
import subprocess
import zipfile
import tempfile
import platform

# Agregar el directorio cli al path
sys.path.insert(0, str(Path(__file__).parent / "cli"))

from funcion_verficar import verificarCronux, obtener_ruta_cronux, determinar_numero_version


# Función auxiliar para selector de archivos/carpetas multiplataforma
def seleccionar_carpeta(titulo="Seleccionar carpeta"):
    """Abre un selector de carpetas nativo según el sistema operativo"""
    sistema = platform.system()
    
    try:
        if sistema == "Darwin":  # macOS
            script = f'''
            tell application "System Events"
                activate
                set folderPath to choose folder with prompt "{titulo}"
                return POSIX path of folderPath
            end tell
            '''
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        elif sistema == "Windows":
            script = f'''
            Add-Type -AssemblyName System.Windows.Forms
            $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
            $dialog.Description = "{titulo}"
            $result = $dialog.ShowDialog()
            if ($result -eq [System.Windows.Forms.DialogResult]::OK) {{
                Write-Output $dialog.SelectedPath
            }}
            '''
            result = subprocess.run(['powershell', '-Command', script], capture_output=True, text=True)
        else:  # Linux
            result = subprocess.run(
                ['zenity', '--file-selection', '--directory', f'--title={titulo}', '--modal'],
                capture_output=True, text=True
            )
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as ex:
        print(f"Error al seleccionar carpeta: {ex}")
    
    return None


def seleccionar_archivo(titulo="Seleccionar archivo", filtros=None, guardar=False, nombre_default=""):
    """Abre un selector de archivos nativo según el sistema operativo"""
    sistema = platform.system()
    
    try:
        if sistema == "Darwin":  # macOS
            if guardar:
                script = f'''
                tell application "System Events"
                    activate
                    set filePath to choose file name with prompt "{titulo}" default name "{nombre_default}"
                    return POSIX path of filePath
                end tell
                '''
            else:
                script = f'''
                tell application "System Events"
                    activate
                    set filePath to choose file with prompt "{titulo}"
                    return POSIX path of filePath
                end tell
                '''
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        elif sistema == "Windows":
            if guardar:
                script = f'''
                Add-Type -AssemblyName System.Windows.Forms
                $dialog = New-Object System.Windows.Forms.SaveFileDialog
                $dialog.Title = "{titulo}"
                $dialog.FileName = "{nombre_default}"
                $result = $dialog.ShowDialog()
                if ($result -eq [System.Windows.Forms.DialogResult]::OK) {{
                    Write-Output $dialog.FileName
                }}
                '''
            else:
                script = f'''
                Add-Type -AssemblyName System.Windows.Forms
                $dialog = New-Object System.Windows.Forms.OpenFileDialog
                $dialog.Title = "{titulo}"
                $result = $dialog.ShowDialog()
                if ($result -eq [System.Windows.Forms.DialogResult]::OK) {{
                    Write-Output $dialog.FileName
                }}
                '''
            result = subprocess.run(['powershell', '-Command', script], capture_output=True, text=True)
        else:  # Linux
            cmd = ['zenity', '--file-selection', f'--title={titulo}', '--modal']
            if guardar:
                cmd.append('--save')
                if nombre_default:
                    cmd.append(f'--filename={nombre_default}')
            if filtros:
                cmd.append(f'--file-filter={filtros}')
            result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as ex:
        print(f"Error al seleccionar archivo: {ex}")
    
    return None


# Paleta de colores - Diseño Minimalista con soporte para modo claro y oscuro
class Colors:
    _theme_mode = ft.ThemeMode.LIGHT  # Default
    
    @classmethod
    def set_theme(cls, theme_mode):
        """Establece el tema actual"""
        cls._theme_mode = theme_mode
    
    @classmethod
    def _get_colors(cls):
        """Retorna los colores según el tema actual"""
        is_dark = cls._theme_mode == ft.ThemeMode.DARK
        
        if is_dark:
            return {
                # Fondos oscuros
                "BG_PRIMARY": "#1a1a1a",
                "BG_SECONDARY": "#242424",
                "BG_TERTIARY": "#2d2d2d",
                "BG_HOVER": "#363636",
                
                # Bordes oscuros
                "BORDER_DEFAULT": "#3a3a3a",
                "BORDER_LIGHT": "#2d2d2d",
                "BORDER_DARK": "#4a4a4a",
                
                # Textos para modo oscuro
                "TEXT_PRIMARY": "#e8e8e8",
                "TEXT_SECONDARY": "#b8b8b8",
                "TEXT_MUTED": "#888888",
                "TEXT_LIGHT": "#ffffff",
                
                # Acentos (mantener vibrantes en oscuro)
                "ACCENT_PRIMARY": "#ff4757",
                "ACCENT_SECONDARY": "#7c3aed",
                "ACCENT_SUCCESS": "#10b981",
                "ACCENT_DANGER": "#ef4444",
                "ACCENT_WARNING": "#f59e0b",
                "ACCENT_INFO": "#3b82f6",
                
                # Estados con transparencias oscuras
                "ACCENT_PRIMARY_LIGHT": "#3d1f23",
                "ACCENT_SECONDARY_LIGHT": "#2d1f3d",
                "ACCENT_SUCCESS_LIGHT": "#1f3d2d",
                "ACCENT_DANGER_LIGHT": "#3d1f23",
                "ACCENT_WARNING_LIGHT": "#3d331f",
                "ACCENT_INFO_LIGHT": "#1f2d3d",
                
                # Fondos de estado oscuros
                "SUCCESS_BG": "#1f3d2d",
                "DANGER_BG": "#3d1f23",
                "WARNING_BG": "#3d331f",
                "INFO_BG": "#1f2d3d",
                
                # Timeline oscuro
                "TIMELINE_LINE": "#3a3a3a",
                "TIMELINE_DOT": "#5a5a5a",
                "TIMELINE_DOT_ACTIVE": "#7c3aed",
            }
        else:
            return {
                # Fondos claros y suaves
                "BG_PRIMARY": "#f8f9fa",
                "BG_SECONDARY": "#ffffff",
                "BG_TERTIARY": "#e9ecef",
                "BG_HOVER": "#dee2e6",
                
                # Bordes minimalistas
                "BORDER_DEFAULT": "#dee2e6",
                "BORDER_LIGHT": "#e9ecef",
                "BORDER_DARK": "#adb5bd",
                
                # Textos - Optimizados para mejor legibilidad
                "TEXT_PRIMARY": "#1a1a1a",
                "TEXT_SECONDARY": "#4a4a4a",
                "TEXT_MUTED": "#8a8a8a",
                "TEXT_LIGHT": "#ffffff",
                
                # Acentos minimalistas - ROJO como principal
                "ACCENT_PRIMARY": "#ff4757",
                "ACCENT_SECONDARY": "#5f27cd",
                "ACCENT_SUCCESS": "#1dd1a1",
                "ACCENT_DANGER": "#ee5a6f",
                "ACCENT_WARNING": "#feca57",
                "ACCENT_INFO": "#54a0ff",
                
                # Estados con transparencias
                "ACCENT_PRIMARY_LIGHT": "#ffe5e8",
                "ACCENT_SECONDARY_LIGHT": "#e8dff5",
                "ACCENT_SUCCESS_LIGHT": "#d4f8f0",
                "ACCENT_DANGER_LIGHT": "#ffeaed",
                "ACCENT_WARNING_LIGHT": "#fff4d9",
                "ACCENT_INFO_LIGHT": "#e3f2ff",
                
                # Fondos de estado
                "SUCCESS_BG": "#d4f8f0",
                "DANGER_BG": "#ffeaed",
                "WARNING_BG": "#fff4d9",
                "INFO_BG": "#e3f2ff",
                
                # Timeline
                "TIMELINE_LINE": "#dee2e6",
                "TIMELINE_DOT": "#adb5bd",
                "TIMELINE_DOT_ACTIVE": "#5f27cd",
            }
    
    def __getattr__(self, name):
        """Permite acceder a colores como Colors.BG_PRIMARY"""
        colors = self._get_colors()
        if name in colors:
            return colors[name]
        raise AttributeError(f"Color '{name}' no encontrado")
    
    # Propiedades estáticas para acceso directo
    @property
    def BG_PRIMARY(self): return self._get_colors()["BG_PRIMARY"]
    @property
    def BG_SECONDARY(self): return self._get_colors()["BG_SECONDARY"]
    @property
    def BG_TERTIARY(self): return self._get_colors()["BG_TERTIARY"]
    @property
    def BG_HOVER(self): return self._get_colors()["BG_HOVER"]
    @property
    def BORDER_DEFAULT(self): return self._get_colors()["BORDER_DEFAULT"]
    @property
    def BORDER_LIGHT(self): return self._get_colors()["BORDER_LIGHT"]
    @property
    def BORDER_DARK(self): return self._get_colors()["BORDER_DARK"]
    @property
    def TEXT_PRIMARY(self): return self._get_colors()["TEXT_PRIMARY"]
    @property
    def TEXT_SECONDARY(self): return self._get_colors()["TEXT_SECONDARY"]
    @property
    def TEXT_MUTED(self): return self._get_colors()["TEXT_MUTED"]
    @property
    def TEXT_LIGHT(self): return self._get_colors()["TEXT_LIGHT"]
    @property
    def ACCENT_PRIMARY(self): return self._get_colors()["ACCENT_PRIMARY"]
    @property
    def ACCENT_SECONDARY(self): return self._get_colors()["ACCENT_SECONDARY"]
    @property
    def ACCENT_SUCCESS(self): return self._get_colors()["ACCENT_SUCCESS"]
    @property
    def ACCENT_DANGER(self): return self._get_colors()["ACCENT_DANGER"]
    @property
    def ACCENT_WARNING(self): return self._get_colors()["ACCENT_WARNING"]
    @property
    def ACCENT_INFO(self): return self._get_colors()["ACCENT_INFO"]
    @property
    def ACCENT_PRIMARY_LIGHT(self): return self._get_colors()["ACCENT_PRIMARY_LIGHT"]
    @property
    def ACCENT_SECONDARY_LIGHT(self): return self._get_colors()["ACCENT_SECONDARY_LIGHT"]
    @property
    def ACCENT_SUCCESS_LIGHT(self): return self._get_colors()["ACCENT_SUCCESS_LIGHT"]
    @property
    def ACCENT_DANGER_LIGHT(self): return self._get_colors()["ACCENT_DANGER_LIGHT"]
    @property
    def ACCENT_WARNING_LIGHT(self): return self._get_colors()["ACCENT_WARNING_LIGHT"]
    @property
    def ACCENT_INFO_LIGHT(self): return self._get_colors()["ACCENT_INFO_LIGHT"]
    @property
    def SUCCESS_BG(self): return self._get_colors()["SUCCESS_BG"]
    @property
    def DANGER_BG(self): return self._get_colors()["DANGER_BG"]
    @property
    def WARNING_BG(self): return self._get_colors()["WARNING_BG"]
    @property
    def INFO_BG(self): return self._get_colors()["INFO_BG"]
    @property
    def TIMELINE_LINE(self): return self._get_colors()["TIMELINE_LINE"]
    @property
    def TIMELINE_DOT(self): return self._get_colors()["TIMELINE_DOT"]
    @property
    def TIMELINE_DOT_ACTIVE(self): return self._get_colors()["TIMELINE_DOT_ACTIVE"]

# Instancia global de Colors
Colors = Colors()


class CronuxGUI:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "CRONUX-CRX"
        self.page.window.width = 1200
        self.page.window.height = 750
        self.page.window.min_width = 800
        self.page.window.min_height = 600
        self.page.window.max_width = 1920
        self.page.window.max_height = 1080
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.LIGHT
        
        # Intentar cargar el icono de la app (priorizar ICNS en macOS)
        try:
            # Priorizar ICNS en macOS para mejor calidad
            icon_icns = Path(__file__).parent / "assets" / "cronux_cli.icns"
            icon_png = Path(__file__).parent / "assets" / "cronux_cli.png"
            icon_svg = Path(__file__).parent / "assets" / "hexagon_logo.svg"
            
            if icon_icns.exists():
                self.page.window_icon = str(icon_icns)
            elif icon_png.exists():
                self.page.window_icon = str(icon_png)
            elif icon_svg.exists():
                self.page.window_icon = str(icon_svg)
        except:
            pass
        
        # Estado de navegación
        self.vista_actual = "inicio"
        
        # Archivo de configuración
        self.config_file = Path.home() / ".cronux_projects.json"
        self.proyectos = self.cargar_proyectos()
        self.proyecto_actual = None
        self.version_actual = None  # Nueva: para trackear la versión actual
        self.comparacion_actual = None  # Para la vista de comparación
        
        # Búsqueda y filtros
        self.filtro_busqueda = ""
        self.filtro_tipo = "todos"
        
        # Cache para optimización de rendimiento
        self._cache_versiones = {}
        self._cache_estadisticas = {}
        self._cache_timestamp = {}
        
        # Cargar preferencia de tema
        self.config_tema_file = Path.home() / ".cronux_theme.json"
        self.cargar_tema()
        
        # Configurar tema en Colors
        Colors.set_theme(self.page.theme_mode)
        
        # Aplicar bgcolor según tema
        self.page.bgcolor = Colors.BG_PRIMARY
        
        # Inicializar UI
        self.mostrar_pantalla_inicio()
    
    def cargar_tema(self):
        """Carga la preferencia de tema guardada"""
        try:
            if self.config_tema_file.exists():
                with open(self.config_tema_file, "r") as f:
                    config = json.load(f)
                    tema = config.get("theme_mode", "light")
                    self.page.theme_mode = ft.ThemeMode.DARK if tema == "dark" else ft.ThemeMode.LIGHT
        except:
            self.page.theme_mode = ft.ThemeMode.LIGHT
    
    def guardar_tema(self, tema):
        """Guarda la preferencia de tema"""
        try:
            with open(self.config_tema_file, "w") as f:
                json.dump({"theme_mode": tema}, f)
        except:
            pass
    
    def cambiar_tema(self):
        """Alterna entre modo claro y oscuro"""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.guardar_tema("dark")
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.guardar_tema("light")
        
        # Actualizar tema en Colors
        Colors.set_theme(self.page.theme_mode)
        
        # Actualizar bgcolor
        self.page.bgcolor = Colors.BG_PRIMARY
        self.page.update()
        
        # Recargar vista actual
        if self.vista_actual == "inicio":
            self.mostrar_pantalla_inicio()
        elif self.vista_actual == "proyecto":
            self.mostrar_vista_proyecto()
    
    def cargar_proyectos(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def guardar_proyectos(self):
        with open(self.config_file, "w") as f:
            json.dump(self.proyectos, f, indent=2)
    
    def agregar_proyecto(self, ruta, nombre, tipo="software"):
        # Intentar leer el tipo del proyecto.json si existe
        try:
            proyecto_json = Path(ruta) / ".cronux" / "proyecto.json"
            if proyecto_json.exists():
                with open(proyecto_json, "r") as f:
                    datos = json.load(f)
                    tipo = datos.get("tipo", tipo)
        except:
            pass
        
        proyecto = {
            "nombre": nombre,
            "ruta": str(ruta),
            "tipo": tipo,
            "favorito": False,  # Nuevo campo
            "fecha_agregado": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        if not any(p["ruta"] == str(ruta) for p in self.proyectos):
            self.proyectos.append(proyecto)
            self.guardar_proyectos()
    
    def eliminar_proyecto_lista(self, ruta):
        """Elimina un proyecto de la lista (no del disco)"""
        self.proyectos = [p for p in self.proyectos if p["ruta"] != ruta]
        self.guardar_proyectos()
    
    def toggle_favorito(self, ruta):
        """Alterna el estado de favorito de un proyecto"""
        for proyecto in self.proyectos:
            if proyecto["ruta"] == ruta:
                proyecto["favorito"] = not proyecto.get("favorito", False)
                self.guardar_proyectos()
                return proyecto["favorito"]
        return False
    
    def obtener_proyectos_filtrados(self):
        """Obtiene proyectos filtrados por búsqueda y tipo"""
        proyectos_filtrados = self.proyectos.copy()
        
        # Filtrar por búsqueda
        if self.filtro_busqueda:
            busqueda_lower = self.filtro_busqueda.lower()
            proyectos_filtrados = [
                p for p in proyectos_filtrados
                if busqueda_lower in p["nombre"].lower() or busqueda_lower in p["ruta"].lower()
            ]
        
        # Filtrar por tipo
        if self.filtro_tipo != "todos":
            proyectos_filtrados = [
                p for p in proyectos_filtrados
                if p.get("tipo", "software") == self.filtro_tipo
            ]
        
        # Ordenar: favoritos primero
        proyectos_filtrados.sort(key=lambda p: (not p.get("favorito", False), p["nombre"].lower()))
        
        return proyectos_filtrados
    
    def limpiar_lista_proyectos(self):
        """Limpia proyectos deprecados (sin .cronux)"""
        proyectos_validos = []
        proyectos_eliminados = 0
        
        for proyecto in self.proyectos:
            ruta_path = Path(proyecto["ruta"])
            # Solo mantener proyectos que existan y tengan .cronux
            if ruta_path.exists() and (ruta_path / ".cronux").exists():
                proyectos_validos.append(proyecto)
            else:
                proyectos_eliminados += 1
        
        self.proyectos = proyectos_validos
        self.guardar_proyectos()
        return proyectos_eliminados
    
    def mostrar_pantalla_inicio(self):
        """Pantalla de inicio minimalista con logo"""
        self.page.controls.clear()
        self.vista_actual = "inicio"
        
        # Logo hexágono SVG
        logo_svg_path = Path(__file__).parent / "assets" / "hexagon_logo.svg"
        logo = None
        if logo_svg_path.exists():
            logo = ft.Image(
                src=str(logo_svg_path),
                width=32,
                height=32,
            )
        else:
            # Fallback al rombo Unicode
            logo = ft.Container(
                content=ft.Text("◆", size=24, color=Colors.ACCENT_PRIMARY),
                width=32,
                height=32,
                alignment=ft.alignment.Alignment(0, 0),
            )
        
        # Header con logo hexágono
        header = ft.Container(
            content=ft.Row([
                # Logo y nombre
                ft.Row([
                    logo,
                    ft.Container(width=12),
                    ft.Text("CRONUX-CRX", 
                           size=18, 
                           weight=ft.FontWeight.W_600, 
                           color=Colors.TEXT_PRIMARY),
                ], spacing=0),
                ft.Container(expand=True),
                # Botones de acción
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.UPLOAD_ROUNDED, 
                                      color=Colors.TEXT_SECONDARY, 
                                      size=20),
                        on_click=lambda _: self.importar_proyecto(),
                        padding=10,
                        border_radius=10,
                        ink=True,
                        tooltip="Importar proyecto",
                        bgcolor=Colors.BG_PRIMARY,
                    ),
                    ft.Container(width=8),
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.DARK_MODE_OUTLINED if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE_OUTLINED, 
                            color=Colors.TEXT_SECONDARY, 
                            size=20
                        ),
                        on_click=lambda _: self.cambiar_tema(),
                        padding=10,
                        border_radius=10,
                        ink=True,
                        tooltip="Cambiar tema",
                        bgcolor=Colors.BG_PRIMARY,
                    ),
                    ft.Container(width=8),
                    ft.Container(
                        content=ft.Icon(ft.Icons.CLEANING_SERVICES_OUTLINED, 
                                      color=Colors.TEXT_SECONDARY, 
                                      size=20),
                        on_click=lambda _: self.confirmar_limpiar_lista(),
                        padding=10,
                        border_radius=10,
                        ink=True,
                        tooltip="Limpiar proyectos deprecados",
                        bgcolor=Colors.BG_PRIMARY,
                    ),
                ], spacing=0),
            ]),
            bgcolor=Colors.BG_SECONDARY,
            padding=ft.Padding.symmetric(horizontal=24, vertical=18),
            border=ft.Border.only(bottom=ft.BorderSide(1, Colors.BORDER_LIGHT)),
        )
        
        # Área de contenido
        if not self.proyectos:
            contenido = self.crear_pantalla_vacia()
        else:
            contenido = self.crear_lista_proyectos()
        
        # Layout principal
        self.page.add(
            ft.Column([
                header,
                contenido,
            ], spacing=0, expand=True)
        )
        self.page.update()
    
    def crear_pantalla_vacia(self):
        """Pantalla cuando no hay proyectos - diseño moderno con logo"""
        # Cargar logo hexágono SVG
        logo_svg_path = Path(__file__).parent / "assets" / "hexagon_logo.svg"
        logo = None
        if logo_svg_path.exists():
            logo = ft.Image(
                src=str(logo_svg_path),
                width=120,
                height=120,
            )
        else:
            # Fallback al rombo Unicode
            logo = ft.Container(
                content=ft.Text("◆", size=80, color=Colors.ACCENT_PRIMARY),
                width=120,
                height=120,
                alignment=ft.alignment.Alignment(0, 0),
            )
        
        return ft.Container(
            content=ft.Column([
                logo,
                ft.Container(height=24),
                ft.Text("No hay proyectos", 
                       size=26, 
                       weight=ft.FontWeight.W_500, 
                       color=Colors.TEXT_PRIMARY),
                ft.Container(height=8),
                ft.Text("Comienza creando un nuevo proyecto o abre uno existente", 
                       size=15, 
                       color=Colors.TEXT_SECONDARY,
                       weight=ft.FontWeight.W_400),
                ft.Container(height=40),
                ft.Row([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD_ROUNDED, color=ft.Colors.WHITE, size=20),
                            ft.Text("Crear proyecto", 
                                   color=Colors.TEXT_LIGHT, 
                                   size=14,
                                   weight=ft.FontWeight.W_500),
                        ], spacing=8),
                        bgcolor=Colors.ACCENT_PRIMARY,
                        padding=ft.Padding.symmetric(horizontal=28, vertical=14),
                        border_radius=25,
                        on_click=lambda _: self.dialogo_nuevo_proyecto(),
                        ink=True,
                        shadow=ft.BoxShadow(
                            spread_radius=0,
                            blur_radius=25,
                            color=ft.Colors.with_opacity(0.4, Colors.ACCENT_PRIMARY),
                            offset=ft.Offset(0, 5),
                        ),
                    ),
                    ft.Container(width=12),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.FOLDER_OPEN_OUTLINED, 
                                  color=Colors.TEXT_PRIMARY, 
                                  size=20),
                            ft.Text("Abrir proyecto", 
                                   color=Colors.TEXT_PRIMARY, 
                                   size=14,
                                   weight=ft.FontWeight.W_400),
                        ], spacing=8),
                        bgcolor=Colors.BG_SECONDARY,
                        padding=ft.Padding.symmetric(horizontal=28, vertical=14),
                        border_radius=25,
                        border=ft.Border.all(1, Colors.BORDER_DEFAULT),
                        on_click=lambda _: self.abrir_carpeta_existente(),
                        ink=True,
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.alignment.Alignment.CENTER,
            expand=True,
        )
    
    def crear_lista_proyectos(self):
        """Lista de proyectos con búsqueda y filtros"""
        
        # Referencia para la lista de proyectos (para actualización dinámica)
        lista_proyectos_ref = ft.Ref[ft.Column]()
        contador_ref = ft.Ref[ft.Container]()
        
        def actualizar_lista_local(e):
            """Actualiza solo la lista sin recargar toda la pantalla"""
            self.filtro_busqueda = e.control.value
            proyectos_filtrados = self.obtener_proyectos_filtrados()
            
            # Actualizar la lista de proyectos
            if proyectos_filtrados:
                lista_proyectos_ref.current.controls = [
                    self.crear_item_proyecto(proyecto) 
                    for proyecto in proyectos_filtrados
                ]
            else:
                lista_proyectos_ref.current.controls = [
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=48, color=Colors.TEXT_MUTED),
                            ft.Container(height=12),
                            ft.Text("No se encontraron proyectos", 
                                   size=15, 
                                   color=Colors.TEXT_SECONDARY,
                                   weight=ft.FontWeight.W_400),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=60,
                        alignment=ft.alignment.Alignment(0, 0),
                    )
                ]
            
            # Actualizar contador
            if self.filtro_busqueda or len(proyectos_filtrados) != len(self.proyectos):
                contador_ref.current.visible = True
                contador_ref.current.content.value = f"{len(proyectos_filtrados)} proyecto(s)" if proyectos_filtrados else "No se encontraron proyectos"
            else:
                contador_ref.current.visible = False
            
            lista_proyectos_ref.current.update()
            contador_ref.current.update()
        
        # Campo de búsqueda
        busqueda_field = ft.TextField(
            value=self.filtro_busqueda,
            hint_text="Buscar proyectos...",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            border_color=Colors.BORDER_DEFAULT,
            focused_border_color=Colors.ACCENT_PRIMARY,
            bgcolor=Colors.BG_SECONDARY,
            color=Colors.TEXT_PRIMARY,
            text_size=14,
            height=45,
            border_radius=10,
            content_padding=ft.Padding.symmetric(horizontal=12, vertical=10),
            on_change=actualizar_lista_local,
            expand=True,
        )
        
        # Obtener proyectos filtrados inicialmente
        proyectos_filtrados = self.obtener_proyectos_filtrados()
        
        return ft.Container(
            content=ft.Column([
                # Toolbar con búsqueda
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("Proyectos", 
                                   size=16, 
                                   weight=ft.FontWeight.W_300, 
                                   color=Colors.TEXT_SECONDARY),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.ADD_ROUNDED, color=ft.Colors.WHITE, size=16),
                                    ft.Text("Nuevo", 
                                           color=Colors.TEXT_LIGHT, 
                                           size=13,
                                           weight=ft.FontWeight.W_500),
                                ], spacing=6),
                                bgcolor=Colors.ACCENT_PRIMARY,
                                padding=ft.Padding.symmetric(horizontal=22, vertical=10),
                                border_radius=20,
                                on_click=lambda _: self.dialogo_nuevo_proyecto(),
                                ink=True,
                                shadow=ft.BoxShadow(
                                    spread_radius=0,
                                    blur_radius=15,
                                    color=ft.Colors.with_opacity(0.3, Colors.ACCENT_PRIMARY),
                                    offset=ft.Offset(0, 3),
                                ),
                            ),
                            ft.Container(width=10),
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.FOLDER_OPEN_OUTLINED, 
                                          color=Colors.TEXT_PRIMARY, 
                                          size=16),
                                    ft.Text("Abrir", 
                                           color=Colors.TEXT_PRIMARY, 
                                           size=13,
                                           weight=ft.FontWeight.W_400),
                                ], spacing=6),
                                bgcolor=Colors.BG_SECONDARY,
                                padding=ft.Padding.symmetric(horizontal=20, vertical=10),
                                border_radius=20,
                                border=ft.Border.all(1, Colors.BORDER_DEFAULT),
                                on_click=lambda _: self.abrir_carpeta_existente(),
                                ink=True,
                            ),
                        ]),
                        ft.Container(height=16),
                        # Barra de búsqueda - ocupa todo el ancho
                        ft.Row([
                            busqueda_field,
                        ], expand=True),
                    ], spacing=0),
                    padding=ft.Padding.symmetric(horizontal=24, vertical=20),
                ),
                
                # Contador de resultados
                ft.Container(
                    ref=contador_ref,
                    content=ft.Text(
                        f"{len(proyectos_filtrados)} proyecto(s)" if proyectos_filtrados else "No se encontraron proyectos",
                        size=13,
                        color=Colors.TEXT_MUTED,
                        weight=ft.FontWeight.W_400,
                    ),
                    padding=ft.Padding.only(left=24, right=24, bottom=12),
                    visible=self.filtro_busqueda or len(proyectos_filtrados) != len(self.proyectos),
                ),
                
                # Lista de proyectos filtrados
                ft.Container(
                    content=ft.Column(
                        ref=lista_proyectos_ref,
                        controls=[
                            self.crear_item_proyecto(proyecto) 
                            for proyecto in proyectos_filtrados
                        ] if proyectos_filtrados else [
                            ft.Container(
                                content=ft.Column([
                                    ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=48, color=Colors.TEXT_MUTED),
                                    ft.Container(height=12),
                                    ft.Text("No se encontraron proyectos", 
                                           size=15, 
                                           color=Colors.TEXT_SECONDARY,
                                           weight=ft.FontWeight.W_400),
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                                padding=60,
                                alignment=ft.alignment.Alignment(0, 0),
                            )
                        ],
                        spacing=12,
                    ),
                    padding=ft.Padding.symmetric(horizontal=24),
                ),
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
        )
    
    def crear_item_proyecto(self, proyecto):
        """Item de proyecto mejorado con botones de acción"""
        ruta_path = Path(proyecto["ruta"])
        existe = ruta_path.exists()
        tiene_cronux = (ruta_path / ".cronux").exists() if existe else False
        
        # Determinar estado con círculo de color
        if existe and tiene_cronux:
            color_estado = Colors.ACCENT_SUCCESS
            texto_estado = "Activo"
        elif existe:
            color_estado = Colors.ACCENT_WARNING
            texto_estado = "Sin .cronux"
        else:
            color_estado = Colors.TEXT_MUTED
            texto_estado = "No existe"
        
        # Obtener icono del tipo de proyecto
        tipo_proyecto = proyecto.get("tipo", "software")
        iconos_tipo = {
            "software": ft.Icons.CODE,
            "documentos": ft.Icons.DESCRIPTION,
            "imagenes": ft.Icons.IMAGE,
            "tareas": ft.Icons.ASSIGNMENT,
            "investigacion": ft.Icons.SCIENCE,
            "diseno": ft.Icons.PALETTE,
        }
        icono_tipo = iconos_tipo.get(tipo_proyecto, ft.Icons.FOLDER)
        
        # Función para abrir carpeta en el explorador
        def abrir_en_explorador(e):
            try:
                if existe:
                    import platform
                    sistema = platform.system()
                    
                    if sistema == "Windows":
                        os.startfile(proyecto["ruta"])
                    elif sistema == "Darwin":  # macOS
                        subprocess.run(['open', proyecto["ruta"]], check=True)
                    else:  # Linux
                        subprocess.run(['xdg-open', proyecto["ruta"]], check=True)
                else:
                    self.mostrar_snackbar("La carpeta no existe", error=True)
            except Exception as ex:
                self.mostrar_snackbar(f"Error al abrir carpeta: {str(ex)}", error=True)
        
        def eliminar_proyecto(e):
            self.confirmar_eliminar_proyecto(proyecto)
        
        def abrir_proyecto_click(e):
            if existe and tiene_cronux:
                self.abrir_proyecto(proyecto["ruta"])
        
        def toggle_favorito_click(e):
            es_favorito = self.toggle_favorito(proyecto["ruta"])
            self.mostrar_snackbar(
                f"{'Agregado a' if es_favorito else 'Eliminado de'} favoritos"
            )
            self.mostrar_pantalla_inicio()
        
        # Verificar si es favorito
        es_favorito = proyecto.get("favorito", False)
        
        return ft.Container(
            content=ft.Row([
                # Icono del tipo de proyecto
                ft.Container(
                    content=ft.Icon(icono_tipo, size=32, color=Colors.ACCENT_PRIMARY),
                    padding=12,
                    bgcolor=Colors.ACCENT_PRIMARY_LIGHT,
                    border_radius=12,
                ),
                ft.Container(width=16),
                # Información del proyecto
                ft.Column([
                    ft.Row([
                        ft.Text(proyecto["nombre"], 
                               size=17, 
                               weight=ft.FontWeight.W_600, 
                               color=Colors.TEXT_PRIMARY,
                               expand=True),
                        # Indicador de favorito
                        ft.Icon(
                            ft.Icons.STAR_ROUNDED if es_favorito else ft.Icons.STAR_BORDER_ROUNDED,
                            size=18,
                            color=Colors.ACCENT_WARNING if es_favorito else Colors.TEXT_MUTED,
                        ) if es_favorito else ft.Container(),
                    ], spacing=8),
                    ft.Container(height=4),
                    ft.Row([
                        ft.Icon(ft.Icons.FOLDER_OUTLINED, 
                               size=14, 
                               color=Colors.TEXT_MUTED),
                        ft.Container(width=6),
                        ft.Text(proyecto["ruta"], 
                               size=13, 
                               color=Colors.TEXT_MUTED,
                               weight=ft.FontWeight.W_400,
                               max_lines=1,
                               overflow=ft.TextOverflow.ELLIPSIS,
                               expand=True),
                    ], spacing=0),
                ], spacing=0, expand=True),
                # Círculo de estado
                ft.Container(
                    content=ft.Container(
                        width=10,
                        height=10,
                        bgcolor=color_estado,
                        border_radius=50,
                    ),
                    tooltip=texto_estado,
                ),
                ft.Container(width=12),
                # Botón favorito
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            ft.Icons.STAR_ROUNDED if es_favorito else ft.Icons.STAR_BORDER_ROUNDED,
                            size=18, 
                            color=Colors.ACCENT_WARNING),
                    ], spacing=0),
                    on_click=toggle_favorito_click,
                    bgcolor=Colors.WARNING_BG,
                    padding=10,
                    border_radius=10,
                    ink=True,
                    tooltip="Quitar de favoritos" if es_favorito else "Agregar a favoritos",
                ),
                ft.Container(width=8),
                # Botón abrir en explorador
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.FOLDER_OPEN_ROUNDED, 
                              size=18, 
                              color=Colors.ACCENT_INFO),
                    ], spacing=0),
                    on_click=abrir_en_explorador,
                    bgcolor=Colors.INFO_BG,
                    padding=10,
                    border_radius=10,
                    ink=True,
                    tooltip="Abrir carpeta",
                ),
                ft.Container(width=8),
                # Botón eliminar
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DELETE_OUTLINE_ROUNDED, 
                              size=18, 
                              color=Colors.ACCENT_DANGER),
                    ], spacing=0),
                    on_click=eliminar_proyecto,
                    bgcolor=Colors.DANGER_BG,
                    padding=10,
                    border_radius=10,
                    ink=True,
                    tooltip="Eliminar proyecto",
                ),
            ], spacing=0),
            bgcolor=Colors.BG_SECONDARY,
            padding=ft.Padding.all(20),
            border_radius=14,
            border=ft.Border.all(1, Colors.BORDER_LIGHT),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            on_click=abrir_proyecto_click if (existe and tiene_cronux) else None,
            # Sin ink=True para que no tenga efecto hover
        )

    
    def confirmar_eliminar_proyecto(self, proyecto):
        """Modal para confirmar eliminación de proyecto"""
        def eliminar_handler(e):
            ruta_path = Path(proyecto["ruta"])
            carpeta_cronux = ruta_path / ".cronux"
            
            # Eliminar carpeta .cronux del disco
            if carpeta_cronux.exists():
                try:
                    shutil.rmtree(carpeta_cronux)
                except Exception as ex:
                    self.mostrar_snackbar(f"Error al eliminar: {ex}", error=True)
                    modal.open = False
                    self.page.update()
                    return
            
            # Eliminar de la lista
            self.eliminar_proyecto_lista(proyecto["ruta"])
            modal.open = False
            self.page.update()
            self.mostrar_snackbar(f"Proyecto '{proyecto['nombre']}' eliminado")
            self.mostrar_pantalla_inicio()
        
        modal = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    # Header
                    ft.Text("Eliminar proyecto", 
                           size=22, 
                           weight=ft.FontWeight.W_500,
                           color=Colors.TEXT_PRIMARY),
                    
                    ft.Container(height=16),
                    
                    ft.Text(f"¿Estás seguro de eliminar '{proyecto['nombre']}'?", 
                           size=15,
                           color=Colors.TEXT_PRIMARY,
                           weight=ft.FontWeight.W_400),
                    
                    ft.Container(height=16),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.WARNING_ROUNDED, size=16, color=Colors.ACCENT_DANGER),
                                ft.Text("Se eliminará permanentemente", size=13, weight=ft.FontWeight.W_500, color=Colors.ACCENT_DANGER),
                            ], spacing=8),
                            ft.Container(height=8),
                            ft.Text("• Carpeta .cronux del disco", size=13, color=Colors.TEXT_PRIMARY),
                            ft.Text("• Todas las versiones guardadas", size=13, color=Colors.TEXT_PRIMARY),
                        ], spacing=4),
                        bgcolor=Colors.DANGER_BG,
                        padding=ft.Padding.all(14),
                        border_radius=10,
                        border=ft.Border.all(1, Colors.ACCENT_DANGER),
                    ),
                    
                    ft.Container(height=20),
                    
                    # Botones
                    ft.Row([
                        ft.Container(
                            content=ft.Text("Cancelar", 
                                           color=Colors.TEXT_PRIMARY,
                                           size=15,
                                           weight=ft.FontWeight.W_500),
                            bgcolor=Colors.BG_TERTIARY,
                            padding=ft.Padding.symmetric(horizontal=32, vertical=14),
                            border_radius=25,
                            on_click=lambda _: self.cerrar_modal(modal),
                            ink=True,
                            expand=True,
                            alignment=ft.alignment.Alignment.CENTER,
                        ),
                        ft.Container(width=12),
                        ft.Container(
                            content=ft.Text("Eliminar", 
                                           color=ft.Colors.WHITE, 
                                           weight=ft.FontWeight.W_600,
                                           size=15),
                            bgcolor=Colors.ACCENT_DANGER,
                            padding=ft.Padding.symmetric(horizontal=32, vertical=14),
                            border_radius=25,
                            on_click=eliminar_handler,
                            ink=True,
                            expand=True,
                            alignment=ft.alignment.Alignment.CENTER,
                            shadow=ft.BoxShadow(
                                spread_radius=0,
                                blur_radius=20,
                                color=ft.Colors.with_opacity(0.4, Colors.ACCENT_DANGER),
                                offset=ft.Offset(0, 4),
                            ),
                        ),
                    ], expand=True),
                ], spacing=0, tight=True),
                padding=ft.Padding.all(28),
                bgcolor=Colors.BG_SECONDARY,
                border_radius=ft.BorderRadius.only(top_left=20, top_right=20),
                height=320,
            ),
            open=True,
        )
        
        self.page.overlay.append(modal)
        self.page.update()
    
    def confirmar_limpiar_lista(self):
        """Modal para confirmar limpieza de proyectos deprecados"""
        # Contar proyectos deprecados
        deprecados = 0
        for proyecto in self.proyectos:
            ruta_path = Path(proyecto["ruta"])
            if not ruta_path.exists() or not (ruta_path / ".cronux").exists():
                deprecados += 1
        
        if deprecados == 0:
            self.mostrar_snackbar("No hay proyectos para limpiar")
            return
        
        def limpiar_handler(e):
            eliminados = self.limpiar_lista_proyectos()
            modal.open = False
            self.page.update()
            self.mostrar_snackbar(f"{eliminados} proyecto(s) eliminado(s) de la lista")
            self.mostrar_pantalla_inicio()
        
        modal = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    # Header
                    ft.Container(
                        content=ft.Row([
                            ft.Text("Limpiar lista de proyectos", 
                                   size=22, 
                                   weight=ft.FontWeight.W_500,
                                   color=Colors.TEXT_PRIMARY),
                        ]),
                        padding=ft.Padding.only(bottom=14),
                    ),
                    
                    # Contenido
                    ft.Text(f"Se encontraron {deprecados} proyecto(s) inválido(s)", 
                           size=16,
                           color=Colors.TEXT_PRIMARY,
                           weight=ft.FontWeight.W_400),
                    
                    ft.Container(height=14),
                    
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.INFO_OUTLINE, size=18, color=Colors.ACCENT_INFO),
                                ft.Text("Se eliminarán de la lista", size=15, weight=ft.FontWeight.W_600, color=Colors.ACCENT_INFO),
                            ], spacing=10),
                            ft.Container(height=12),
                            ft.Text("• Proyectos cuya carpeta ya no existe", size=14, color=Colors.TEXT_PRIMARY, weight=ft.FontWeight.W_400),
                            ft.Container(height=6),
                            ft.Text("• Proyectos sin carpeta .cronux válida", size=14, color=Colors.TEXT_PRIMARY, weight=ft.FontWeight.W_400),
                        ], spacing=0),
                        bgcolor=Colors.INFO_BG,
                        padding=ft.Padding.all(16),
                        border_radius=12,
                        border=ft.Border.all(1, Colors.ACCENT_INFO),
                    ),
                    
                    ft.Container(height=24),
                    
                    # Botones
                    ft.Row([
                        ft.Container(
                            content=ft.Text("Cancelar", 
                                           color=Colors.TEXT_PRIMARY,
                                           size=15,
                                           weight=ft.FontWeight.W_500),
                            bgcolor=Colors.BG_TERTIARY,
                            padding=ft.Padding.symmetric(horizontal=32, vertical=16),
                            border_radius=25,
                            on_click=lambda _: self.cerrar_modal(modal),
                            ink=True,
                            expand=True,
                            alignment=ft.alignment.Alignment.CENTER,
                        ),
                        ft.Container(width=12),
                        ft.Container(
                            content=ft.Text("Limpiar lista", 
                                           color=ft.Colors.WHITE, 
                                           weight=ft.FontWeight.W_600,
                                           size=15),
                            bgcolor=Colors.ACCENT_INFO,
                            padding=ft.Padding.symmetric(horizontal=32, vertical=16),
                            border_radius=25,
                            on_click=limpiar_handler,
                            ink=True,
                            expand=True,
                            alignment=ft.alignment.Alignment.CENTER,
                            shadow=ft.BoxShadow(
                                spread_radius=0,
                                blur_radius=20,
                                color=ft.Colors.with_opacity(0.4, Colors.ACCENT_INFO),
                                offset=ft.Offset(0, 4),
                            ),
                        ),
                    ], expand=True),
                ], spacing=0, tight=True),
                padding=ft.Padding.all(30),
                bgcolor=Colors.BG_SECONDARY,
                border_radius=ft.BorderRadius.only(top_left=20, top_right=20),
            ),
            open=True,
        )
        
        self.page.overlay.append(modal)
        self.page.update()
    
    def dialogo_nuevo_proyecto(self):
        """Modal wizard para crear nuevo proyecto - por pasos"""
        paso_actual = {"valor": 1}  # 1: tipo, 2: detalles
        
        # Contenedor para mostrar errores dentro del modal con diseño mejorado
        error_container = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.WARNING_ROUNDED, size=16, color=Colors.ACCENT_DANGER),
                ft.Container(width=8),
                ft.Text(
                    "",
                    size=13,
                    color=Colors.TEXT_PRIMARY,
                    weight=ft.FontWeight.W_500,
                ),
            ], spacing=0, tight=True),
            bgcolor=Colors.DANGER_BG,
            padding=ft.Padding.all(12),
            border_radius=8,
            border=ft.Border.all(1, Colors.ACCENT_DANGER),
            visible=False,
        )
        
        def mostrar_error_modal(mensaje):
            """Muestra error dentro del modal con diseño mejorado"""
            error_container.content.controls[2].value = mensaje
            error_container.visible = True
            error_container.update()
            
            # Ocultar después de 4 segundos
            import threading
            import time
            def ocultar():
                time.sleep(4)
                try:
                    error_container.visible = False
                    error_container.update()
                except:
                    pass
            threading.Thread(target=ocultar, daemon=True).start()
        
        nombre_field = ft.TextField(
            hint_text="Ej: Mi Aplicación Web",
            border_color=Colors.BORDER_DEFAULT,
            focused_border_color=Colors.ACCENT_PRIMARY,
            bgcolor=Colors.BG_PRIMARY,
            color=Colors.TEXT_PRIMARY,
            text_size=15,
            cursor_color=Colors.ACCENT_PRIMARY,
            height=56,
            border_radius=12,
            content_padding=ft.Padding.symmetric(horizontal=18, vertical=16),
            expand=True,
        )
        
        ruta_seleccionada = {"path": ""}
        tipo_seleccionado = {"tipo": "software", "icono": ft.Icons.CODE, "nombre": "Software"}
        
        # Tipos de proyecto con sus iconos
        tipos_proyecto = [
            {"nombre": "Software", "icono": ft.Icons.CODE, "key": "software"},
            {"nombre": "Documentos", "icono": ft.Icons.DESCRIPTION, "key": "documentos"},
            {"nombre": "Imágenes", "icono": ft.Icons.IMAGE, "key": "imagenes"},
            {"nombre": "Tareas", "icono": ft.Icons.ASSIGNMENT, "key": "tareas"},
            {"nombre": "Investigación", "icono": ft.Icons.SCIENCE, "key": "investigacion"},
            {"nombre": "Diseño", "icono": ft.Icons.PALETTE, "key": "diseno"},
        ]
        
        # Contenedor para las tarjetas de tipo
        tarjetas_tipo = []
        
        def seleccionar_tipo(tipo_info):
            tipo_seleccionado["tipo"] = tipo_info["key"]
            tipo_seleccionado["icono"] = tipo_info["icono"]
            tipo_seleccionado["nombre"] = tipo_info["nombre"]
            # Actualizar todas las tarjetas
            for i, tarjeta_data in enumerate(tipos_proyecto):
                es_seleccionado = tarjeta_data["key"] == tipo_info["key"]
                tarjetas_tipo[i].bgcolor = Colors.ACCENT_PRIMARY if es_seleccionado else Colors.BG_PRIMARY
                tarjetas_tipo[i].border = ft.Border.all(2 if es_seleccionado else 1, Colors.ACCENT_PRIMARY if es_seleccionado else Colors.BORDER_DEFAULT)
                # Actualizar color del icono y texto - BLANCO cuando está seleccionado
                tarjetas_tipo[i].content.controls[0].color = ft.Colors.WHITE if es_seleccionado else Colors.TEXT_SECONDARY
                tarjetas_tipo[i].content.controls[2].color = ft.Colors.WHITE if es_seleccionado else Colors.TEXT_PRIMARY
                tarjetas_tipo[i].update()
        
        # Crear tarjetas de tipo
        for tipo_info in tipos_proyecto:
            es_seleccionado = tipo_info["key"] == "software"
            tarjeta = ft.Container(
                content=ft.Column([
                    ft.Icon(tipo_info["icono"], 
                           size=40, 
                           color=ft.Colors.WHITE if es_seleccionado else Colors.TEXT_SECONDARY),
                    ft.Container(height=12),
                    ft.Text(tipo_info["nombre"], 
                           size=14, 
                           weight=ft.FontWeight.W_500,
                           color=ft.Colors.WHITE if es_seleccionado else Colors.TEXT_PRIMARY,
                           text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                bgcolor=Colors.ACCENT_PRIMARY if es_seleccionado else Colors.BG_PRIMARY,
                padding=ft.Padding.all(20),
                border_radius=12,
                border=ft.Border.all(2 if es_seleccionado else 1, Colors.ACCENT_PRIMARY if es_seleccionado else Colors.BORDER_DEFAULT),
                on_click=lambda _, t=tipo_info: seleccionar_tipo(t),
                ink=True,
                expand=True,
            )
            tarjetas_tipo.append(tarjeta)
        
        # Texto que muestra la ruta seleccionada
        ruta_texto = ft.Text(
            "No se ha seleccionado ubicación",
            size=13,
            color=Colors.TEXT_MUTED,
            weight=ft.FontWeight.W_400,
            italic=True,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        
        def seleccionar_carpeta_zenity(e):
            try:
                ruta = seleccionar_carpeta("Seleccionar carpeta")
                
                if ruta:
                    ruta_seleccionada["path"] = ruta
                    ruta_texto.value = ruta
                    ruta_texto.color = Colors.TEXT_PRIMARY
                    ruta_texto.italic = False
                    ruta_texto.update()
            except Exception as ex:
                print(f"Error: {ex}")
                self.mostrar_snackbar(f"Error al seleccionar carpeta: {str(ex)}", error=True)
        
        # Contenedores de pasos - inicializar con contenido vacío pero visible
        paso1_container = ft.Container(visible=True)
        paso2_container = ft.Container(visible=False)
        
        def actualizar_vista_paso(actualizar_ui=True):
            if paso_actual["valor"] == 1:
                # Paso 1: Seleccionar tipo
                paso1_container.content = ft.Column([
                    # Header con botones en la misma línea
                    ft.Row([
                        # Lado izquierdo: Paso y título
                        ft.Column([
                            ft.Text("Paso 1 de 2", 
                                   size=13, 
                                   color=Colors.TEXT_MUTED,
                                   weight=ft.FontWeight.W_400),
                            ft.Container(height=8),
                            ft.Text("Selecciona el tipo de proyecto", 
                                   size=24, 
                                   weight=ft.FontWeight.W_500,
                                   color=Colors.TEXT_PRIMARY),
                        ], spacing=0, expand=True),
                        
                        # Lado derecho: Botones
                        ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.CLOSE_ROUNDED, 
                                              color=Colors.TEXT_PRIMARY, 
                                              size=24),
                                bgcolor=Colors.BG_TERTIARY,
                                padding=12,
                                border_radius=25,
                                on_click=lambda _: cerrar_modal(),
                                ink=True,
                                tooltip="Cancelar",
                            ),
                            ft.Container(width=12),
                            ft.Container(
                                content=ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, 
                                              color=ft.Colors.WHITE, 
                                              size=24),
                                bgcolor=Colors.ACCENT_PRIMARY,
                                padding=12,
                                border_radius=25,
                                on_click=lambda _: ir_paso_2(),
                                ink=True,
                                tooltip="Siguiente",
                                shadow=ft.BoxShadow(
                                    spread_radius=0,
                                    blur_radius=20,
                                    color=ft.Colors.with_opacity(0.4, Colors.ACCENT_PRIMARY),
                                    offset=ft.Offset(0, 4),
                                ),
                            ),
                        ], spacing=0),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Container(height=28),
                    
                    # Tarjetas de tipo
                    ft.Row([
                        tarjetas_tipo[0],
                        ft.Container(width=12),
                        tarjetas_tipo[1],
                        ft.Container(width=12),
                        tarjetas_tipo[2],
                    ], expand=True),
                    ft.Container(height=12),
                    ft.Row([
                        tarjetas_tipo[3],
                        ft.Container(width=12),
                        tarjetas_tipo[4],
                        ft.Container(width=12),
                        tarjetas_tipo[5],
                    ], expand=True),
                ], spacing=0, tight=True)
                paso1_container.visible = True
                paso2_container.visible = False
            else:
                # Paso 2: Nombre y ubicación
                paso2_container.content = ft.Column([
                    # Header con botones en la misma línea
                    ft.Row([
                        # Lado izquierdo: Paso y título con icono
                        ft.Column([
                            ft.Text("Paso 2 de 2", 
                                   size=13, 
                                   color=Colors.TEXT_MUTED,
                                   weight=ft.FontWeight.W_400),
                            ft.Container(height=8),
                            ft.Row([
                                ft.Icon(tipo_seleccionado["icono"], size=28, color=Colors.ACCENT_PRIMARY),
                                ft.Container(width=12),
                                ft.Text(f"Proyecto de {tipo_seleccionado['nombre']}", 
                                       size=24, 
                                       weight=ft.FontWeight.W_500,
                                       color=Colors.TEXT_PRIMARY),
                            ], spacing=0),
                        ], spacing=0, expand=True),
                        
                        # Lado derecho: Botones
                        ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.ARROW_BACK_ROUNDED, 
                                              color=Colors.TEXT_PRIMARY, 
                                              size=24),
                                bgcolor=Colors.BG_TERTIARY,
                                padding=12,
                                border_radius=25,
                                on_click=lambda _: ir_paso_1(),
                                ink=True,
                                tooltip="Atrás",
                            ),
                            ft.Container(width=12),
                            ft.Container(
                                content=ft.Icon(ft.Icons.CHECK_ROUNDED, 
                                              color=ft.Colors.WHITE, 
                                              size=24),
                                bgcolor=Colors.ACCENT_PRIMARY,
                                padding=12,
                                border_radius=25,
                                on_click=lambda _: crear_proyecto_handler(),
                                ink=True,
                                tooltip="Crear proyecto",
                                shadow=ft.BoxShadow(
                                    spread_radius=0,
                                    blur_radius=20,
                                    color=ft.Colors.with_opacity(0.4, Colors.ACCENT_PRIMARY),
                                    offset=ft.Offset(0, 4),
                                ),
                            ),
                        ], spacing=0),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Container(height=28),
                    
                    # Nombre del proyecto
                    ft.Text("Nombre del proyecto", 
                           size=14, 
                           weight=ft.FontWeight.W_600, 
                           color=Colors.TEXT_PRIMARY),
                    ft.Container(height=12),
                    ft.Row([nombre_field], expand=True),
                    
                    ft.Container(height=28),
                    
                    # Botón seleccionar ubicación
                    ft.Row([
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.FOLDER_OPEN_OUTLINED, size=20, color=Colors.ACCENT_PRIMARY),
                                ft.Text("Seleccionar ubicación", 
                                       size=15, 
                                       color=Colors.ACCENT_PRIMARY, 
                                       weight=ft.FontWeight.W_600),
                            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                            bgcolor=Colors.ACCENT_PRIMARY_LIGHT,
                            padding=ft.Padding.symmetric(vertical=16),
                            border_radius=12,
                            on_click=seleccionar_carpeta_zenity,
                            ink=True,
                            expand=True,
                        ),
                    ], expand=True),
                    
                    ft.Container(height=12),
                    
                    # Texto de ruta seleccionada
                    ft.Container(
                        content=ruta_texto,
                        padding=ft.Padding.symmetric(horizontal=4),
                    ),
                    
                    ft.Container(expand=True),
                    
                    # Mensaje de error abajo
                    error_container,
                ], spacing=0, tight=True)
                paso1_container.visible = False
                paso2_container.visible = True
            
            # Solo actualizar si se solicita (después de que esté en la página)
            if actualizar_ui:
                paso1_container.update()
                paso2_container.update()
        
        def ir_paso_2():
            paso_actual["valor"] = 2
            # Actualizar el placeholder según el tipo seleccionado
            ejemplos_nombre = {
                "software": "Ej: Mi Aplicación Web",
                "documentos": "Ej: Tesis Universitaria",
                "imagenes": "Ej: Fotos Vacaciones 2024",
                "tareas": "Ej: Proyecto Final Matemáticas",
                "investigacion": "Ej: Estudio sobre IA",
                "diseno": "Ej: Rediseño Logo Empresa",
            }
            nombre_field.hint_text = ejemplos_nombre.get(tipo_seleccionado["tipo"], "Ej: Mi Proyecto")
            actualizar_vista_paso()
        
        def ir_paso_1():
            paso_actual["valor"] = 1
            actualizar_vista_paso()
        
        def cerrar_modal():
            modal.open = False
            self.page.update()
        
        def crear_proyecto_handler():
            nombre = nombre_field.value
            ruta = ruta_seleccionada["path"]
            tipo = tipo_seleccionado["tipo"]
            
            if not nombre:
                mostrar_error_modal("⚠ Debes ingresar un nombre para el proyecto")
                return
            
            if not ruta:
                mostrar_error_modal("⚠ Debes seleccionar una ubicación para el proyecto")
                return
            
            ruta_path = Path(ruta)
            os.chdir(ruta_path)
            
            if verificarCronux():
                mostrar_error_modal("⚠ Esta carpeta ya contiene un proyecto Cronux")
                return
            
            # Cerrar el modal
            modal.open = False
            self.page.update()
            
            # Mostrar pantalla de carga completa con diseño tipo Git timeline pulido y centrado
            self.page.controls.clear()
            
            # Cargar logo si existe
            logo_path = Path(__file__).parent / "assets" / "cronux_cli.png"
            logo = None
            if logo_path.exists():
                logo = ft.Image(
                    src=str(logo_path),
                    width=72,
                    height=72,
                )
            
            self.page.add(
                ft.Container(
                    content=ft.Column([
                        ft.Container(expand=True),
                        
                        # Logo con sombra sutil
                        ft.Container(
                            content=logo if logo else ft.Icon(
                                ft.Icons.ROCKET_LAUNCH_ROUNDED,
                                size=72,
                                color=Colors.ACCENT_PRIMARY,
                            ),
                            shadow=ft.BoxShadow(
                                spread_radius=0,
                                blur_radius=20,
                                color=ft.Colors.with_opacity(0.15, Colors.ACCENT_PRIMARY),
                                offset=ft.Offset(0, 4),
                            ),
                        ),
                        
                        ft.Container(height=32),
                        
                        # Título principal
                        ft.Text("Creando proyecto", 
                               size=34, 
                               weight=ft.FontWeight.W_700,
                               color=Colors.TEXT_PRIMARY,
                               text_align=ft.TextAlign.CENTER),
                        
                        ft.Container(height=10),
                        
                        # Subtítulo con icono del tipo
                        ft.Row([
                            ft.Icon(tipo_seleccionado["icono"], 
                                   size=20, 
                                   color=Colors.ACCENT_PRIMARY),
                            ft.Text(f"Proyecto de {tipo_seleccionado['nombre']}", 
                                   size=17, 
                                   weight=ft.FontWeight.W_400,
                                   color=Colors.TEXT_SECONDARY,
                                   text_align=ft.TextAlign.CENTER),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                        
                        ft.Container(height=48),
                        
                        # Timeline estilo Git - centrado
                        ft.Row([
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Column([
                                    # Paso 1: Creando estructura
                                    ft.Row([
                                        # Línea vertical y círculo
                                        ft.Container(
                                            content=ft.Column([
                                                ft.Container(
                                                    width=22,
                                                    height=22,
                                                    bgcolor=Colors.ACCENT_SUCCESS,
                                                    border_radius=50,
                                                    content=ft.Icon(
                                                        ft.Icons.CHECK_ROUNDED,
                                                        size=14,
                                                        color=ft.Colors.WHITE,
                                                    ),
                                                    alignment=ft.alignment.Alignment.CENTER,
                                                    shadow=ft.BoxShadow(
                                                        spread_radius=0,
                                                        blur_radius=8,
                                                        color=ft.Colors.with_opacity(0.3, Colors.ACCENT_SUCCESS),
                                                        offset=ft.Offset(0, 2),
                                                    ),
                                                ),
                                                ft.Container(
                                                    width=3,
                                                    height=45,
                                                    bgcolor=Colors.ACCENT_SUCCESS,
                                                ),
                                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                                            width=35,
                                        ),
                                        ft.Container(width=18),
                                        # Texto
                                        ft.Column([
                                            ft.Text("Creando estructura", 
                                                   size=17, 
                                                   weight=ft.FontWeight.W_600,
                                                   color=Colors.TEXT_PRIMARY),
                                            ft.Container(height=4),
                                            ft.Text("Inicializando carpeta .cronux", 
                                                   size=14, 
                                                   color=Colors.TEXT_MUTED),
                                        ], spacing=0),
                                    ], spacing=0),
                                    
                                    # Paso 2: Inicializando versión
                                    ft.Row([
                                        # Línea vertical y círculo
                                        ft.Container(
                                            content=ft.Column([
                                                ft.Container(
                                                    width=22,
                                                    height=22,
                                                    bgcolor=Colors.ACCENT_SUCCESS,
                                                    border_radius=50,
                                                    content=ft.Icon(
                                                        ft.Icons.CHECK_ROUNDED,
                                                        size=14,
                                                        color=ft.Colors.WHITE,
                                                    ),
                                                    alignment=ft.alignment.Alignment.CENTER,
                                                    shadow=ft.BoxShadow(
                                                        spread_radius=0,
                                                        blur_radius=8,
                                                        color=ft.Colors.with_opacity(0.3, Colors.ACCENT_SUCCESS),
                                                        offset=ft.Offset(0, 2),
                                                    ),
                                                ),
                                                ft.Container(
                                                    width=3,
                                                    height=45,
                                                    bgcolor=Colors.ACCENT_PRIMARY,
                                                ),
                                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                                            width=35,
                                        ),
                                        ft.Container(width=18),
                                        # Texto
                                        ft.Column([
                                            ft.Text("Inicializando versión 1.0", 
                                                   size=17, 
                                                   weight=ft.FontWeight.W_600,
                                                   color=Colors.TEXT_PRIMARY),
                                            ft.Container(height=4),
                                            ft.Text("Preparando sistema de versiones", 
                                                   size=14, 
                                                   color=Colors.TEXT_MUTED),
                                        ], spacing=0),
                                    ], spacing=0),
                                    
                                    # Paso 3: Guardando archivos (en progreso)
                                    ft.Row([
                                        # Círculo pulsante
                                        ft.Container(
                                            content=ft.Column([
                                                ft.Container(
                                                    width=22,
                                                    height=22,
                                                    bgcolor=Colors.ACCENT_PRIMARY,
                                                    border_radius=50,
                                                    content=ft.ProgressRing(
                                                        width=13,
                                                        height=13,
                                                        stroke_width=2.5,
                                                        color=ft.Colors.WHITE,
                                                    ),
                                                    alignment=ft.alignment.Alignment.CENTER,
                                                    shadow=ft.BoxShadow(
                                                        spread_radius=0,
                                                        blur_radius=18,
                                                        color=ft.Colors.with_opacity(0.5, Colors.ACCENT_PRIMARY),
                                                        offset=ft.Offset(0, 0),
                                                    ),
                                                ),
                                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                                            width=35,
                                        ),
                                        ft.Container(width=18),
                                        # Texto
                                        ft.Column([
                                            ft.Text("Guardando archivos", 
                                                   size=17, 
                                                   weight=ft.FontWeight.W_600,
                                                   color=Colors.ACCENT_PRIMARY),
                                            ft.Container(height=4),
                                            ft.Text("Copiando contenido del proyecto", 
                                                   size=14, 
                                                   color=Colors.TEXT_MUTED),
                                        ], spacing=0),
                                    ], spacing=0),
                                ], spacing=0),
                                width=420,
                            ),
                            ft.Container(expand=True),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        
                        ft.Container(expand=True),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    alignment=ft.alignment.Alignment.CENTER,
                    expand=True,
                    bgcolor=Colors.BG_PRIMARY,
                )
            )
            self.page.update()
            
            # Crear proyecto en segundo plano con async
            import asyncio
            async def crear_proyecto_async():
                try:
                    # Crear estructura del proyecto
                    carpeta_cronux = ruta_path / ".cronux"
                    carpeta_cronux.mkdir(exist_ok=True)
                    
                    datos_proyecto = {
                        "nombre": nombre,
                        "tipo": tipo,
                        "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "autor": "usuario"
                    }
                    
                    with open(carpeta_cronux / "proyecto.json", "w") as f:
                        json.dump(datos_proyecto, f, indent=2)
                    
                    # Crear versión 1.0 automáticamente
                    carpeta_versiones = carpeta_cronux / "versiones"
                    carpeta_versiones.mkdir(exist_ok=True)
                    carpeta_version = carpeta_versiones / "version_1.0"
                    carpeta_version.mkdir(exist_ok=True)
                    
                    # Copiar archivos existentes a la versión 1.0
                    archivos_copiados = 0
                    for item in ruta_path.iterdir():
                        if item.name != ".cronux" and not item.name.startswith('.'):
                            destino = carpeta_version / item.name
                            try:
                                if item.is_file():
                                    shutil.copy2(item, destino)
                                    archivos_copiados += 1
                                elif item.is_dir():
                                    shutil.copytree(item, destino)
                                    archivos_copiados += 1
                            except Exception as ex:
                                print(f"Error copiando {item}: {ex}")
                    
                    # Guardar metadatos de la versión 1.0
                    tamaño_bytes = self.calcular_tamaño_directorio(carpeta_version)
                    tamaño_formateado = self.formatear_tamaño(tamaño_bytes)
                    
                    metadatos = {
                        "version": "1.0",
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "mensaje": "Versión inicial del proyecto",
                        "archivos_guardados": archivos_copiados,
                        "tamaño_bytes": tamaño_bytes,
                        "tamaño_formateado": tamaño_formateado
                    }
                    
                    with open(carpeta_version / "metadatos.json", "w") as f:
                        json.dump(metadatos, f, indent=2)
                    
                    self.agregar_proyecto(ruta_path, nombre, tipo)
                    
                    # Esperar 3.5 segundos para mostrar la animación
                    await asyncio.sleep(3.5)
                    
                    # Abrir proyecto (esto limpiará la pantalla de carga)
                    self.abrir_proyecto(str(ruta_path))
                    
                    # Mostrar mensaje de éxito
                    self.mostrar_snackbar(f"Proyecto creado exitosamente")
                    
                except Exception as ex:
                    print(f"Error creando proyecto: {ex}")
                    self.mostrar_pantalla_inicio()
                    self.mostrar_snackbar(f"Error al crear proyecto", error=True)
            
            # Ejecutar la tarea async
            self.page.run_task(crear_proyecto_async)
        
        # Inicializar contenido del paso 1 ANTES de crear el modal (sin actualizar UI)
        actualizar_vista_paso(actualizar_ui=False)
        
        # Crear el modal con los contenedores ya inicializados
        modal = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    paso1_container,
                    paso2_container,
                ], spacing=0, tight=True),
                padding=ft.Padding.all(30),
                bgcolor=Colors.BG_SECONDARY,
                border_radius=ft.BorderRadius.only(top_left=20, top_right=20),
                height=520,
            ),
            open=True,
        )
        
        # Agregar modal a la página y actualizar
        self.page.overlay.append(modal)
        self.page.update()
    
    def abrir_carpeta_existente(self):
        try:
            ruta = seleccionar_carpeta("Seleccionar proyecto Cronux")
            
            if not ruta:
                return  # Usuario canceló
            
            ruta_path = Path(ruta)
            os.chdir(ruta_path)
            
            if not verificarCronux():
                self.mostrar_snackbar("Esta carpeta no contiene un proyecto Cronux válido", error=True)
                return
            
            try:
                with open(ruta_path / ".cronux" / "proyecto.json", "r") as f:
                    datos = json.load(f)
                    nombre = datos.get("nombre", "Proyecto sin nombre")
            except:
                nombre = ruta_path.name
            
            self.agregar_proyecto(ruta_path, nombre)
            self.abrir_proyecto(str(ruta_path))
        except Exception as ex:
            print(f"Error: {ex}")
            self.mostrar_snackbar(f"Error al seleccionar carpeta: {str(ex)}", error=True)
    
    def abrir_proyecto(self, ruta):
        ruta_path = Path(ruta)
        if not ruta_path.exists():
            self.mostrar_snackbar("La ruta del proyecto no existe", error=True)
            return
        os.chdir(ruta_path)
        if not verificarCronux():
            self.mostrar_snackbar("No es un proyecto Cronux válido", error=True)
            return
        self.proyecto_actual = ruta
        
        # Detectar versión actual comparando archivos
        self.detectar_version_actual()
            
        self.mostrar_vista_proyecto()
    
    def mostrar_vista_proyecto(self):
        self.page.controls.clear()
        
        try:
            with open(Path(self.proyecto_actual) / ".cronux" / "proyecto.json", "r") as f:
                datos_proyecto = json.load(f)
                nombre_proyecto = datos_proyecto.get("nombre", "Proyecto")
        except:
            nombre_proyecto = "Proyecto"
        
        # Header minimalista con iconos
        header = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.ARROW_BACK_ROUNDED, size=20, color=Colors.TEXT_SECONDARY),
                    on_click=lambda _: self.mostrar_pantalla_inicio(),
                    padding=8,
                    ink=True,
                    border_radius=20,
                    tooltip="Volver",
                ),
                ft.Container(width=12),
                ft.Row([
                    ft.Icon(ft.Icons.FOLDER_OUTLINED, size=18, color=Colors.TEXT_MUTED),
                    ft.Container(width=8),
                    ft.Text(nombre_proyecto, 
                           size=18, 
                           weight=ft.FontWeight.W_400, 
                           color=Colors.TEXT_PRIMARY,
                           font_family="monospace"),
                    ft.Container(width=8),
                    ft.Container(
                        content=ft.Icon(ft.Icons.EDIT_OUTLINED, size=16, color=Colors.TEXT_MUTED),
                        on_click=lambda _: self.dialogo_editar_nombre(),
                        padding=6,
                        ink=True,
                        border_radius=15,
                        tooltip="Editar nombre",
                    ),
                ]),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Icon(ft.Icons.REFRESH_ROUNDED, size=20, color=Colors.TEXT_MUTED),
                    on_click=lambda _: self.refrescar_proyecto(),
                    padding=8,
                    ink=True,
                    border_radius=20,
                    tooltip="Actualizar",
                ),
                ft.Container(width=8),
                # Botón Estadísticas
                ft.Container(
                    content=ft.Icon(ft.Icons.BAR_CHART_ROUNDED, size=20, color=Colors.TEXT_MUTED),
                    on_click=lambda _: self.mostrar_estadisticas(),
                    padding=8,
                    ink=True,
                    border_radius=20,
                    tooltip="Estadísticas",
                ),
                ft.Container(width=8),
                # Botón Exportar
                ft.Container(
                    content=ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, size=20, color=Colors.TEXT_MUTED),
                    on_click=lambda _: self.exportar_proyecto(),
                    padding=8,
                    ink=True,
                    border_radius=20,
                    tooltip="Exportar proyecto",
                ),
                ft.Container(width=8),
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SAVE_OUTLINED, color=ft.Colors.WHITE, size=16),
                        ft.Text("Guardar versión", 
                               color=Colors.TEXT_LIGHT, 
                               size=13,
                               weight=ft.FontWeight.W_500),
                    ], spacing=8),
                    bgcolor=Colors.ACCENT_PRIMARY,
                    padding=ft.Padding.symmetric(horizontal=22, vertical=12),
                    border_radius=20,
                    on_click=lambda _: self.dialogo_guardar_version(),
                    ink=True,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=20,
                        color=ft.Colors.with_opacity(0.4, Colors.ACCENT_PRIMARY),
                        offset=ft.Offset(0, 4),
                    ),
                ),
            ]),
            bgcolor=Colors.BG_SECONDARY,
            padding=ft.Padding.symmetric(horizontal=24, vertical=16),
            border=ft.Border.only(bottom=ft.BorderSide(1, Colors.BORDER_LIGHT)),
        )
        
        contenido = ft.Row([
            self.crear_timeline(),
            ft.Container(width=1, bgcolor=Colors.BORDER_LIGHT),
            self.crear_panel_detalles(),
        ], expand=True, spacing=0)
        
        self.page.add(
            ft.Column([header, contenido], spacing=0, expand=True)
        )
        self.page.update()
    
    def crear_timeline(self):
        versiones = self.obtener_versiones()
        timeline_items = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=0)
        
        if not versiones:
            timeline_items.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.HISTORY_OUTLINED, size=48, color=Colors.TEXT_MUTED),
                        ft.Container(height=12),
                        ft.Text("Sin versiones", 
                               size=14, 
                               color=Colors.TEXT_SECONDARY, 
                               weight=ft.FontWeight.W_300),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    padding=40,
                )
            )
        else:
            for i, version in enumerate(versiones):
                es_actual = version['version'] == self.version_actual
                es_final = i == len(versiones) - 1
                timeline_items.controls.append(
                    self.crear_item_timeline(version, es_actual, es_final)
                )
        
        return ft.Container(
            content=timeline_items,
            width=240,
            bgcolor=Colors.BG_SECONDARY,
            padding=30,
        )
    
    def crear_item_timeline(self, version, es_actual=False, es_final=False):
        """Timeline item con punto destacado para versión actual"""
        # Tamaño y color del círculo según si es la versión actual
        if es_actual:
            circulo_size = 14
            circulo_color = Colors.ACCENT_PRIMARY
            circulo_border = 3
            texto_color = Colors.TEXT_PRIMARY
            texto_weight = ft.FontWeight.W_600
            version_size = 16
        else:
            circulo_size = 10
            circulo_color = Colors.TIMELINE_DOT
            circulo_border = 2
            texto_color = Colors.TEXT_SECONDARY
            texto_weight = ft.FontWeight.W_400
            version_size = 15
        
        return ft.Container(
            content=ft.Row([
                # Columna del timeline (línea y círculo)
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Container(
                                width=circulo_size - circulo_border * 2,
                                height=circulo_size - circulo_border * 2,
                                bgcolor=circulo_color,
                                border_radius=50,
                                shadow=ft.BoxShadow(
                                    spread_radius=0,
                                    blur_radius=8 if es_actual else 0,
                                    color=ft.Colors.with_opacity(0.4, circulo_color) if es_actual else ft.Colors.TRANSPARENT,
                                    offset=ft.Offset(0, 0),
                                ) if es_actual else None,
                            ),
                            width=circulo_size,
                            height=circulo_size,
                            border_radius=50,
                            border=ft.Border.all(circulo_border, Colors.BG_SECONDARY),
                            bgcolor=Colors.BG_SECONDARY,
                            alignment=ft.alignment.Alignment.CENTER,
                        ),
                        ft.Container(
                            width=2,
                            height=36,
                            bgcolor=Colors.TIMELINE_LINE,
                        ) if not es_final else ft.Container(),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    width=24,
                ),
                ft.Container(width=16),
                # Información de la versión
                ft.Column([
                    ft.Text(f"v{version['version']}", 
                           size=version_size, 
                           weight=texto_weight,
                           color=texto_color),
                    ft.Container(height=2),
                    ft.Text(version['fecha'].split()[0], 
                           size=12, 
                           color=Colors.TEXT_MUTED,
                           weight=ft.FontWeight.W_300),
                ], spacing=0),
            ], spacing=0),
            padding=ft.Padding.only(bottom=4),
        )
    
    def crear_panel_detalles(self):
        self.panel_detalles = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=12, expand=True)
        versiones = self.obtener_versiones()
        
        if versiones:
            for version in versiones:
                es_actual = version['version'] == self.version_actual
                self.panel_detalles.controls.append(
                    self.crear_tarjeta_version(version, es_actual)
                )
        else:
            self.panel_detalles.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("◯", size=64, color=Colors.TEXT_MUTED),
                        ft.Container(height=15),
                        ft.Text("Sin versiones guardadas", 
                               size=16, 
                               color=Colors.TEXT_PRIMARY, 
                               weight=ft.FontWeight.W_300),
                        ft.Container(height=5),
                        ft.Text("Guarda tu primera versión para comenzar", 
                               size=13, 
                               color=Colors.TEXT_SECONDARY,
                               weight=ft.FontWeight.W_300),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    padding=60,
                    alignment=ft.alignment.Alignment.CENTER,
                )
            )
        
        return ft.Container(
            content=self.panel_detalles, 
            padding=24, 
            expand=True, 
            bgcolor=Colors.BG_PRIMARY
        )
    
    def crear_tarjeta_version(self, version, es_actual=False):
        """Tarjeta de versión con diseño idéntico al demo web"""
        # Badge de versión actual
        badge = None
        if es_actual:
            badge = ft.Container(
                content=ft.Text("ACTUAL", 
                               size=10, 
                               color=Colors.ACCENT_SECONDARY,
                               weight=ft.FontWeight.W_600),
                bgcolor=Colors.ACCENT_SECONDARY_LIGHT,
                padding=ft.Padding.symmetric(horizontal=12, vertical=5),
                border_radius=12,
            )
        
        return ft.Container(
            content=ft.Column([
                # Header con versión y badge
                ft.Row([
                    ft.Column([
                        ft.Text(f"v{version['version']}", 
                               size=18, 
                               weight=ft.FontWeight.W_600, 
                               color=Colors.TEXT_PRIMARY),
                        ft.Container(height=4),
                        ft.Text(version['fecha'], 
                               size=13, 
                               color=Colors.TEXT_MUTED),
                    ], spacing=0),
                    ft.Container(expand=True),
                    badge if badge else ft.Container(),
                ], alignment=ft.MainAxisAlignment.START),
                
                ft.Container(height=12),
                
                # Descripción
                ft.Text(version['mensaje'], 
                       size=14, 
                       color=Colors.TEXT_SECONDARY,
                       weight=ft.FontWeight.W_400),
                
                ft.Container(height=16),
                
                # Información de archivos y tamaño (más visible y prioritaria)
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.FOLDER_OUTLINED, size=18, color=Colors.ACCENT_INFO),
                                ft.Container(width=8),
                                ft.Text(f"{version.get('archivos', 'N/A')} archivos", 
                                       size=15, 
                                       weight=ft.FontWeight.W_600,
                                       color=Colors.TEXT_PRIMARY),
                            ], spacing=0),
                        ),
                        ft.Container(width=24),
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.STORAGE_OUTLINED, size=18, color=Colors.ACCENT_SUCCESS),
                                ft.Container(width=8),
                                ft.Text(version.get('tamaño', 'N/A'), 
                                       size=15, 
                                       weight=ft.FontWeight.W_600,
                                       color=Colors.TEXT_PRIMARY),
                            ], spacing=0),
                        ),
                    ]),
                    bgcolor=Colors.BG_SECONDARY,
                    padding=ft.Padding.all(12),
                    border_radius=8,
                    border=ft.Border.all(1, Colors.BORDER_LIGHT),
                ),
                
                ft.Container(height=16),
                
                # Estadísticas de cambios
                ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, size=16, color=Colors.ACCENT_SUCCESS),
                        ft.Container(width=6),
                        ft.Text(f"{version.get('agregados', 0)} agregados", 
                               size=13, 
                               color=Colors.TEXT_MUTED),
                    ], spacing=0),
                    ft.Container(width=16),
                    ft.Row([
                        ft.Icon(ft.Icons.EDIT_OUTLINED, size=16, color=Colors.ACCENT_WARNING),
                        ft.Container(width=6),
                        ft.Text(f"{version.get('modificados', 0)} modificados", 
                               size=13, 
                               color=Colors.TEXT_MUTED),
                    ], spacing=0),
                    ft.Container(width=16),
                    ft.Row([
                        ft.Icon(ft.Icons.REMOVE_CIRCLE_OUTLINE, size=16, color=Colors.ACCENT_DANGER),
                        ft.Container(width=6),
                        ft.Text(f"{version.get('eliminados', 0)} eliminados", 
                               size=13, 
                               color=Colors.TEXT_MUTED),
                    ], spacing=0),
                ]),
                
                ft.Container(height=16),
                
                # Botones de acción
                ft.Row([
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.FOLDER_OPEN_OUTLINED, size=14, color=Colors.TEXT_SECONDARY),
                            ft.Container(width=6),
                            ft.Text("Ver carpeta", 
                                   size=12, 
                                   color=Colors.TEXT_SECONDARY),
                        ], spacing=0),
                        padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                        border=ft.Border.all(1, Colors.BORDER_DEFAULT),
                        border_radius=8,
                        bgcolor=Colors.BG_PRIMARY,
                        on_click=lambda _, v=version: self.abrir_carpeta_proyecto(),
                        ink=True,
                    ),
                    ft.Container(width=8),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.RESTORE_ROUNDED, size=14, color=Colors.TEXT_SECONDARY),
                            ft.Container(width=6),
                            ft.Text("Restaurar", 
                                   size=12, 
                                   color=Colors.TEXT_SECONDARY),
                        ], spacing=0),
                        padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                        border=ft.Border.all(1, Colors.BORDER_DEFAULT),
                        border_radius=8,
                        bgcolor=Colors.BG_PRIMARY,
                        on_click=lambda _, v=version: self.confirmar_restaurar(v),
                        ink=True,
                    ),
                    ft.Container(width=8),
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.COMPARE_ARROWS_ROUNDED, size=14, color=Colors.TEXT_SECONDARY),
                            ft.Container(width=6),
                            ft.Text("Comparar", 
                                   size=12, 
                                   color=Colors.TEXT_SECONDARY),
                        ], spacing=0),
                        padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                        border=ft.Border.all(1, Colors.BORDER_DEFAULT),
                        border_radius=8,
                        bgcolor=Colors.BG_PRIMARY,
                        on_click=lambda _, v=version: self.comparar_versiones(v),
                        ink=True,
                    ),
                ]),
            ], spacing=0),
            bgcolor=Colors.BG_SECONDARY,
            border_radius=12,
            padding=20,
            border=ft.Border.all(1, Colors.BORDER_DEFAULT),
        )
    
    def obtener_versiones(self, force_refresh=False):
        """Obtiene versiones con cache para mejor rendimiento"""
        if not self.proyecto_actual:
            return []
        
        # Verificar cache
        cache_key = self.proyecto_actual
        current_time = datetime.now().timestamp()
        
        if not force_refresh and cache_key in self._cache_versiones:
            # Cache válido por 5 segundos
            if current_time - self._cache_timestamp.get(cache_key, 0) < 5:
                return self._cache_versiones[cache_key]
        
        carpeta_versiones = Path(self.proyecto_actual) / ".cronux" / "versiones"
        if not carpeta_versiones.exists():
            return []
        
        versiones = []
        versiones_dirs = sorted(carpeta_versiones.glob("version_*"), 
                               key=lambda x: self.version_a_numero(x.name.replace("version_", "")),
                               reverse=True)
        
        for i, version_dir in enumerate(versiones_dirs):
            metadatos_file = version_dir / "metadatos.json"
            if metadatos_file.exists():
                try:
                    with open(metadatos_file, "r") as f:
                        metadatos = json.load(f)
                    
                    # Calcular cambios comparando con la versión anterior
                    agregados = 0
                    modificados = 0
                    eliminados = 0
                    
                    if i < len(versiones_dirs) - 1:  # Si no es la primera versión
                        version_anterior_dir = versiones_dirs[i + 1]
                        cambios = self.calcular_cambios_entre_versiones(version_anterior_dir, version_dir)
                        agregados = cambios['agregados']
                        modificados = cambios['modificados']
                        eliminados = cambios['eliminados']
                    else:
                        # Primera versión: todos los archivos son agregados
                        agregados = metadatos.get("archivos_guardados", 0)
                    
                    versiones.append({
                        "version": metadatos["version"],
                        "fecha": metadatos["fecha"],
                        "mensaje": metadatos.get("mensaje", "Sin mensaje"),
                        "archivos": metadatos.get("archivos_guardados", "N/A"),
                        "tamaño": metadatos.get("tamaño_formateado", "N/A"),
                        "agregados": agregados,
                        "modificados": modificados,
                        "eliminados": eliminados,
                    })
                except:
                    pass
        
        # Actualizar cache
        self._cache_versiones[cache_key] = versiones
        self._cache_timestamp[cache_key] = current_time
        
        return versiones
    
    def calcular_cambios_entre_versiones(self, version_anterior_dir, version_actual_dir):
        """Calcula los archivos agregados, modificados y eliminados entre dos versiones"""
        try:
            # Obtener archivos de ambas versiones (excluyendo metadatos.json)
            archivos_anteriores = set()
            archivos_actuales = set()
            
            for item in version_anterior_dir.iterdir():
                if item.name != "metadatos.json":
                    archivos_anteriores.add(item.name)
            
            for item in version_actual_dir.iterdir():
                if item.name != "metadatos.json":
                    archivos_actuales.add(item.name)
            
            # Calcular diferencias
            agregados = len(archivos_actuales - archivos_anteriores)
            eliminados = len(archivos_anteriores - archivos_actuales)
            
            # Archivos que existen en ambas versiones (potencialmente modificados)
            archivos_comunes = archivos_anteriores & archivos_actuales
            modificados = 0
            
            for archivo in archivos_comunes:
                archivo_anterior = version_anterior_dir / archivo
                archivo_actual = version_actual_dir / archivo
                
                # Comparar tamaños o fechas de modificación
                if archivo_anterior.is_file() and archivo_actual.is_file():
                    if archivo_anterior.stat().st_size != archivo_actual.stat().st_size:
                        modificados += 1
            
            return {
                'agregados': agregados,
                'modificados': modificados,
                'eliminados': eliminados
            }
        except Exception as e:
            return {'agregados': 0, 'modificados': 0, 'eliminados': 0}
    
    def ver_cambios_version(self, version):
        """Muestra los cambios de una versión"""
        self.mostrar_snackbar(f"Mostrando cambios de v{version['version']}")
    
    def abrir_carpeta_proyecto(self):
        """Abre la carpeta del proyecto en el explorador de archivos"""
        if not self.proyecto_actual:
            self.mostrar_snackbar("No hay proyecto abierto", error=True)
            return
        
        try:
            ruta = Path(self.proyecto_actual)
            if not ruta.exists():
                self.mostrar_snackbar("La carpeta no existe", error=True)
                return
            
            # Detectar sistema operativo y abrir explorador
            import platform
            sistema = platform.system()
            
            # Minimizar la ventana temporalmente para que el explorador aparezca encima
            self.page.window_minimized = True
            self.page.update()
            
            if sistema == "Windows":
                os.startfile(str(ruta))
            elif sistema == "Darwin":  # macOS
                subprocess.run(['open', str(ruta)], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', str(ruta)], check=True)
            
            # Restaurar la ventana después de un breve delay
            import time
            time.sleep(0.3)
            self.page.window_minimized = False
            self.page.update()
            
            self.mostrar_snackbar("Carpeta abierta")
        except Exception as e:
            self.mostrar_snackbar(f"Error al abrir carpeta: {str(e)}", error=True)
    
    def version_a_numero(self, version_str):
        try:
            if "." in version_str:
                mayor, menor = version_str.split(".")
                return int(mayor) * 1000 + int(menor)
            return int(version_str) * 1000
        except:
            return 0
    
    def refrescar_proyecto(self):
        """Refresca la vista del proyecto para sincronizar con cambios del CLI"""
        # Limpiar cache
        if self.proyecto_actual in self._cache_versiones:
            del self._cache_versiones[self.proyecto_actual]
        if self.proyecto_actual in self._cache_estadisticas:
            del self._cache_estadisticas[self.proyecto_actual]
        
        # Detectar versión actual comparando archivos
        self.detectar_version_actual()
        
        # Recargar la vista
        self.mostrar_vista_proyecto()
        self.mostrar_snackbar("Proyecto actualizado")
    
    def detectar_version_actual(self):
        """Detecta qué versión está actualmente en el proyecto comparando archivos"""
        if not self.proyecto_actual:
            return
        
        try:
            directorio_proyecto = Path(self.proyecto_actual)
            carpeta_versiones = directorio_proyecto / ".cronux" / "versiones"
            
            if not carpeta_versiones.exists():
                self.version_actual = None
                return
            
            # Obtener lista de archivos actuales del proyecto (excluyendo .cronux)
            archivos_actuales = set()
            for item in directorio_proyecto.iterdir():
                if item.name != ".cronux" and not item.name.startswith('.'):
                    archivos_actuales.add(item.name)
            
            # Comparar con cada versión guardada
            for version_dir in sorted(carpeta_versiones.glob("version_*"), reverse=True):
                metadatos_file = version_dir / "metadatos.json"
                if not metadatos_file.exists():
                    continue
                
                try:
                    with open(metadatos_file, "r") as f:
                        metadatos = json.load(f)
                    
                    version_num = metadatos["version"]
                    
                    # Obtener archivos de esta versión
                    archivos_version = set()
                    for item in version_dir.iterdir():
                        if item.name != "metadatos.json":
                            archivos_version.add(item.name)
                    
                    # Si los nombres de archivos coinciden, comparar contenido
                    if archivos_actuales == archivos_version:
                        # Comparar contenido de archivos
                        coincide = True
                        for archivo in archivos_actuales:
                            archivo_actual = directorio_proyecto / archivo
                            archivo_version = version_dir / archivo
                            
                            # Si es directorio, solo verificar que exista
                            if archivo_actual.is_dir():
                                if not archivo_version.is_dir():
                                    coincide = False
                                    break
                            # Si es archivo, comparar contenido
                            elif archivo_actual.is_file():
                                if not archivo_version.is_file():
                                    coincide = False
                                    break
                                try:
                                    with open(archivo_actual, 'rb') as f1, open(archivo_version, 'rb') as f2:
                                        if f1.read() != f2.read():
                                            coincide = False
                                            break
                                except:
                                    coincide = False
                                    break
                        
                        if coincide:
                            self.version_actual = version_num
                            return
                
                except Exception as ex:
                    print(f"Error comparando versión: {ex}")
                    continue
            
            # Si no coincide con ninguna versión, no hay versión actual
            self.version_actual = None
            
        except Exception as ex:
            print(f"Error detectando versión actual: {ex}")
            self.version_actual = None
    
    def dialogo_editar_nombre(self):
        """Modal para editar el nombre del proyecto"""
        # Obtener nombre actual
        try:
            with open(Path(self.proyecto_actual) / ".cronux" / "proyecto.json", "r") as f:
                datos_proyecto = json.load(f)
                nombre_actual = datos_proyecto.get("nombre", "")
        except:
            nombre_actual = ""
        
        nombre_field = ft.TextField(
            value=nombre_actual,
            hint_text="Nombre del proyecto",
            border_color=Colors.BORDER_DEFAULT,
            focused_border_color=Colors.ACCENT_PRIMARY,
            bgcolor=Colors.BG_PRIMARY,
            color=Colors.TEXT_PRIMARY,
            text_size=15,
            cursor_color=Colors.ACCENT_PRIMARY,
            height=56,
            border_radius=12,
            content_padding=ft.Padding.symmetric(horizontal=18, vertical=16),
            autofocus=True,
        )
        
        def guardar_handler(e):
            nuevo_nombre = nombre_field.value.strip()
            
            if not nuevo_nombre:
                self.mostrar_snackbar("El nombre no puede estar vacío", error=True)
                return
            
            try:
                # Leer datos actuales
                proyecto_json = Path(self.proyecto_actual) / ".cronux" / "proyecto.json"
                with open(proyecto_json, "r") as f:
                    datos = json.load(f)
                
                # Actualizar nombre
                datos["nombre"] = nuevo_nombre
                
                # Guardar cambios
                with open(proyecto_json, "w") as f:
                    json.dump(datos, f, indent=2)
                
                # Actualizar en la lista de proyectos
                for proyecto in self.proyectos:
                    if proyecto["ruta"] == self.proyecto_actual:
                        proyecto["nombre"] = nuevo_nombre
                        break
                self.guardar_proyectos()
                
                modal.open = False
                self.page.update()
                self.mostrar_snackbar("Nombre actualizado correctamente")
                self.mostrar_vista_proyecto()
                
            except Exception as ex:
                self.mostrar_snackbar(f"Error al actualizar: {ex}", error=True)
        
        modal = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    # Header
                    ft.Text("Editar nombre del proyecto", 
                           size=22, 
                           weight=ft.FontWeight.W_500,
                           color=Colors.TEXT_PRIMARY),
                    
                    ft.Container(height=20),
                    
                    # Campo de texto
                    ft.Text("Nombre del proyecto", 
                           size=14, 
                           weight=ft.FontWeight.W_600, 
                           color=Colors.TEXT_PRIMARY),
                    ft.Container(height=12),
                    ft.Row([nombre_field], expand=True),
                    
                    ft.Container(height=24),
                    
                    # Botones
                    ft.Row([
                        ft.Container(
                            content=ft.Text("Cancelar", 
                                           color=Colors.TEXT_PRIMARY,
                                           size=15,
                                           weight=ft.FontWeight.W_500),
                            bgcolor=Colors.BG_TERTIARY,
                            padding=ft.Padding.symmetric(horizontal=32, vertical=16),
                            border_radius=25,
                            on_click=lambda _: self.cerrar_modal(modal),
                            ink=True,
                            expand=True,
                            alignment=ft.alignment.Alignment.CENTER,
                        ),
                        ft.Container(width=12),
                        ft.Container(
                            content=ft.Text("Guardar", 
                                           color=ft.Colors.WHITE, 
                                           weight=ft.FontWeight.W_600,
                                           size=15),
                            bgcolor=Colors.ACCENT_PRIMARY,
                            padding=ft.Padding.symmetric(horizontal=32, vertical=16),
                            border_radius=25,
                            on_click=guardar_handler,
                            ink=True,
                            expand=True,
                            alignment=ft.alignment.Alignment.CENTER,
                            shadow=ft.BoxShadow(
                                spread_radius=0,
                                blur_radius=20,
                                color=ft.Colors.with_opacity(0.4, Colors.ACCENT_PRIMARY),
                                offset=ft.Offset(0, 4),
                            ),
                        ),
                    ], expand=True),
                ], spacing=0, tight=True),
                padding=ft.Padding.all(30),
                bgcolor=Colors.BG_SECONDARY,
                border_radius=ft.BorderRadius.only(top_left=20, top_right=20),
                height=300,
            ),
            open=True,
        )
        
        self.page.overlay.append(modal)
        self.page.update()
    
    def dialogo_guardar_version(self):
        """Modal para guardar nueva versión"""
        mensaje_field = ft.TextField(
            hint_text="Ej: Agregué sistema de autenticación y corregí bugs en el formulario",
            multiline=True,
            min_lines=4,
            max_lines=6,
            border_color=Colors.BORDER_DEFAULT,
            focused_border_color=Colors.ACCENT_PRIMARY,
            bgcolor=Colors.BG_PRIMARY,
            color=Colors.TEXT_PRIMARY,
            text_size=15,
            cursor_color=Colors.ACCENT_PRIMARY,
            border_radius=12,
            content_padding=ft.Padding.all(16),
        )
        
        def guardar_handler(e):
            mensaje = mensaje_field.value or "Cambios sin descripción"
            try:
                numero_version = determinar_numero_version()
                carpeta_versiones = Path(self.proyecto_actual) / ".cronux" / "versiones"
                carpeta_versiones.mkdir(exist_ok=True)
                carpeta_version = carpeta_versiones / f"version_{numero_version}"
                carpeta_version.mkdir(exist_ok=True)
                directorio_actual = Path(self.proyecto_actual)
                archivos_copiados = 0
                for item in directorio_actual.iterdir():
                    if item.name != ".cronux" and not item.name.startswith('.'):
                        destino = carpeta_version / item.name
                        try:
                            if item.is_file():
                                shutil.copy2(item, destino)
                                archivos_copiados += 1
                            elif item.is_dir():
                                shutil.copytree(item, destino)
                                archivos_copiados += 1
                        except Exception as ex:
                            print(f"Error: {ex}")
                tamaño_bytes = self.calcular_tamaño_directorio(carpeta_version)
                tamaño_formateado = self.formatear_tamaño(tamaño_bytes)
                metadatos = {
                    "version": numero_version,
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "mensaje": mensaje,
                    "archivos_guardados": archivos_copiados,
                    "tamaño_bytes": tamaño_bytes,
                    "tamaño_formateado": tamaño_formateado
                }
                with open(carpeta_version / "metadatos.json", "w") as f:
                    json.dump(metadatos, f, indent=2)
                
                # Actualizar versión actual instantáneamente
                self.version_actual = numero_version
                
                modal.open = False
                self.page.update()
                self.mostrar_snackbar(f"Versión {numero_version} guardada correctamente")
                self.mostrar_vista_proyecto()
            except Exception as ex:
                self.mostrar_snackbar(f"Error al guardar: {ex}", error=True)
        
        modal = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    # Header
                    ft.Container(
                        content=ft.Row([
                            ft.Text("Guardar nueva versión", 
                                   size=22, 
                                   weight=ft.FontWeight.W_500,
                                   color=Colors.TEXT_PRIMARY),
                        ]),
                        padding=ft.Padding.only(bottom=16),
                    ),
                    
                    # Descripción
                    ft.Text("Descripción de los cambios", 
                           size=14, 
                           weight=ft.FontWeight.W_600, 
                           color=Colors.TEXT_PRIMARY),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Container(
                            content=mensaje_field,
                            expand=True,
                        )
                    ], expand=True),
                    
                    ft.Container(height=16),
                    
                    # Info
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=Colors.ACCENT_INFO),
                            ft.Text("Se guardarán todos los archivos del proyecto actual", 
                                   size=13, 
                                   color=Colors.TEXT_PRIMARY,
                                   weight=ft.FontWeight.W_400),
                        ], spacing=10),
                        padding=ft.Padding.all(12),
                        bgcolor=Colors.INFO_BG,
                        border_radius=12,
                    ),
                    
                    ft.Container(height=20),
                    
                    # Botones
                    ft.Row([
                        ft.Container(
                            content=ft.Text("Cancelar", 
                                           color=Colors.TEXT_PRIMARY,
                                           size=15,
                                           weight=ft.FontWeight.W_500),
                            bgcolor=Colors.BG_TERTIARY,
                            padding=ft.Padding.symmetric(horizontal=32, vertical=16),
                            border_radius=25,
                            on_click=lambda _: self.cerrar_modal(modal),
                            ink=True,
                            expand=True,
                            alignment=ft.alignment.Alignment.CENTER,
                        ),
                        ft.Container(width=12),
                        ft.Container(
                            content=ft.Text("Guardar versión", 
                                           color=ft.Colors.WHITE, 
                                           weight=ft.FontWeight.W_600,
                                           size=15),
                            bgcolor=Colors.ACCENT_PRIMARY,
                            padding=ft.Padding.symmetric(horizontal=32, vertical=16),
                            border_radius=25,
                            on_click=guardar_handler,
                            ink=True,
                            expand=True,
                            alignment=ft.alignment.Alignment.CENTER,
                            shadow=ft.BoxShadow(
                                spread_radius=0,
                                blur_radius=20,
                                color=ft.Colors.with_opacity(0.4, Colors.ACCENT_PRIMARY),
                                offset=ft.Offset(0, 4),
                            ),
                        ),
                    ], expand=True),
                ], spacing=0, tight=True),
                padding=ft.Padding.all(30),
                bgcolor=Colors.BG_SECONDARY,
                border_radius=ft.BorderRadius.only(top_left=20, top_right=20),
                height=420,
            ),
            open=True,
        )
        self.page.overlay.append(modal)
        self.page.update()
    
    def confirmar_restaurar(self, version):
        """Modal para confirmar restauración de versión"""
        def restaurar_handler(e):
            try:
                version_elegida = version['version']
                carpeta_version = Path(self.proyecto_actual) / ".cronux" / "versiones" / f"version_{version_elegida}"
                if not carpeta_version.exists():
                    self.mostrar_snackbar(f"La versión {version_elegida} no existe", error=True)
                    modal.open = False
                    self.page.update()
                    return
                directorio_actual = Path(self.proyecto_actual)
                for item in directorio_actual.iterdir():
                    if item.name != ".cronux" and not item.name.startswith('.'):
                        try:
                            if item.is_file():
                                item.unlink()
                            elif item.is_dir():
                                shutil.rmtree(item)
                        except Exception as ex:
                            print(f"Error: {ex}")
                for item in carpeta_version.iterdir():
                    if item.name != "metadatos.json":
                        destino = directorio_actual / item.name
                        try:
                            if item.is_file():
                                shutil.copy2(item, destino)
                            elif item.is_dir():
                                shutil.copytree(item, destino)
                        except Exception as ex:
                            print(f"Error: {ex}")
                
                # Actualizar versión actual instantáneamente
                self.version_actual = version_elegida
                
                modal.open = False
                self.page.update()
                self.mostrar_snackbar(f"Versión {version_elegida} restaurada correctamente")
                self.mostrar_vista_proyecto()
            except Exception as ex:
                self.mostrar_snackbar(f"Error al restaurar: {ex}", error=True)
        
        modal = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    # Header
                    ft.Text("Restaurar versión", 
                           size=22, 
                           weight=ft.FontWeight.W_500,
                           color=Colors.TEXT_PRIMARY),
                    
                    ft.Container(height=16),
                    
                    # Contenido
                    ft.Text(f"¿Deseas restaurar la versión {version['version']}?", 
                           size=15,
                           color=Colors.TEXT_PRIMARY,
                           weight=ft.FontWeight.W_400),
                    
                    ft.Container(height=16),
                    
                    # Advertencia compacta
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.WARNING_ROUNDED, size=16, color=Colors.ACCENT_SECONDARY),
                                ft.Text("Se reemplazarán todos los archivos actuales", 
                                       size=13, 
                                       color=Colors.TEXT_PRIMARY, 
                                       weight=ft.FontWeight.W_500),
                            ], spacing=8),
                        ], spacing=0),
                        bgcolor=Colors.ACCENT_SECONDARY_LIGHT,
                        padding=ft.Padding.all(12),
                        border_radius=10,
                        border=ft.Border.all(1, Colors.ACCENT_SECONDARY),
                    ),
                    
                    ft.Container(height=16),
                    
                    # Detalles compactos
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Fecha:", size=13, color=Colors.TEXT_SECONDARY, weight=ft.FontWeight.W_600),
                                ft.Text(version['fecha'], size=13, color=Colors.TEXT_PRIMARY),
                            ], spacing=8),
                            ft.Container(height=8),
                            ft.Text(version['mensaje'], size=13, color=Colors.TEXT_PRIMARY, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                        ], spacing=0),
                        bgcolor=Colors.BG_PRIMARY,
                        padding=ft.Padding.all(12),
                        border_radius=10,
                    ),
                    
                    ft.Container(height=20),
                    
                    # Botones
                    ft.Row([
                        ft.Container(
                            content=ft.Text("Cancelar", 
                                           color=Colors.TEXT_PRIMARY,
                                           size=15,
                                           weight=ft.FontWeight.W_500),
                            bgcolor=Colors.BG_TERTIARY,
                            padding=ft.Padding.symmetric(horizontal=32, vertical=14),
                            border_radius=25,
                            on_click=lambda _: self.cerrar_modal(modal),
                            ink=True,
                            expand=True,
                            alignment=ft.alignment.Alignment.CENTER,
                        ),
                        ft.Container(width=12),
                        ft.Container(
                            content=ft.Text("Restaurar", 
                                           color=ft.Colors.WHITE, 
                                           weight=ft.FontWeight.W_600,
                                           size=15),
                            bgcolor=Colors.ACCENT_SECONDARY,
                            padding=ft.Padding.symmetric(horizontal=32, vertical=14),
                            border_radius=25,
                            on_click=restaurar_handler,
                            ink=True,
                            expand=True,
                            alignment=ft.alignment.Alignment.CENTER,
                            shadow=ft.BoxShadow(
                                spread_radius=0,
                                blur_radius=20,
                                color=ft.Colors.with_opacity(0.4, Colors.ACCENT_SECONDARY),
                                offset=ft.Offset(0, 4),
                            ),
                        ),
                    ], expand=True),
                ], spacing=0, tight=True),
                padding=ft.Padding.all(28),
                bgcolor=Colors.BG_SECONDARY,
                border_radius=ft.BorderRadius.only(top_left=20, top_right=20),
                height=420,
            ),
            open=True,
        )
        self.page.overlay.append(modal)
        self.page.update()
    
    def calcular_tamaño_directorio(self, directorio):
        tamaño_total = 0
        try:
            for item in Path(directorio).rglob('*'):
                if item.is_file():
                    tamaño_total += item.stat().st_size
        except:
            pass
        return tamaño_total
    
    def formatear_tamaño(self, bytes_size):
        if bytes_size < 1024:
            return f"{bytes_size} B"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.1f} KB"
        elif bytes_size < 1024 * 1024 * 1024:
            return f"{bytes_size / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_size / (1024 * 1024 * 1024):.1f} GB"
    
    def comparar_versiones(self, version1, version2=None):
        """Compara dos versiones y muestra las diferencias"""
        if not version2:
            # Comparar con la versión anterior
            versiones = self.obtener_versiones()
            idx = next((i for i, v in enumerate(versiones) if v['version'] == version1['version']), -1)
            if idx < len(versiones) - 1:
                version2 = versiones[idx + 1]
            else:
                self.mostrar_snackbar("No hay versión anterior para comparar", error=True)
                return
        
        # Obtener archivos de ambas versiones
        carpeta_v1 = Path(self.proyecto_actual) / ".cronux" / "versiones" / f"version_{version1['version']}"
        carpeta_v2 = Path(self.proyecto_actual) / ".cronux" / "versiones" / f"version_{version2['version']}"
        
        archivos_v1 = set()
        archivos_v2 = set()
        
        if carpeta_v1.exists():
            for item in carpeta_v1.iterdir():
                if item.name != "metadatos.json":
                    archivos_v1.add(item.name)
        
        if carpeta_v2.exists():
            for item in carpeta_v2.iterdir():
                if item.name != "metadatos.json":
                    archivos_v2.add(item.name)
        
        # Calcular diferencias
        agregados = archivos_v1 - archivos_v2
        eliminados = archivos_v2 - archivos_v1
        comunes = archivos_v1 & archivos_v2
        
        # Verificar archivos modificados
        modificados = []
        for archivo in comunes:
            archivo_v1 = carpeta_v1 / archivo
            archivo_v2 = carpeta_v2 / archivo
            
            if archivo_v1.is_file() and archivo_v2.is_file():
                try:
                    if archivo_v1.stat().st_size != archivo_v2.stat().st_size:
                        modificados.append(archivo)
                except:
                    pass
        
        self.mostrar_modal_comparacion(version1, version2, agregados, eliminados, modificados)
    
    def mostrar_modal_comparacion(self, v1, v2, agregados, eliminados, modificados):
        """Muestra vista completa con la comparación de versiones"""
        
        # Guardar datos de comparación para la vista
        self.comparacion_actual = {
            'v1': v1,
            'v2': v2,
            'agregados': agregados,
            'eliminados': eliminados,
            'modificados': modificados
        }
        
        # Cambiar a vista de comparación
        self.vista_actual = "comparacion"
        self.mostrar_vista_comparacion()
    
    def mostrar_vista_comparacion(self):
        """Muestra la vista completa de comparación de versiones"""
        if not self.comparacion_actual:
            return
        
        v1 = self.comparacion_actual['v1']
        v2 = self.comparacion_actual['v2']
        agregados = self.comparacion_actual['agregados']
        eliminados = self.comparacion_actual['eliminados']
        modificados = self.comparacion_actual['modificados']
        
        self.page.controls.clear()
        
        # Extensiones con preview
        extensiones_preview = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg', '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml', '.sh', '.bat', '.c', '.cpp', '.h', '.java', '.go', '.rs', '.ts', '.tsx', '.jsx'}
        
        # Crear lista de cambios
        cambios_lista = []
        
        # Archivos agregados
        for archivo in sorted(agregados):
            tiene_preview = Path(archivo).suffix.lower() in extensiones_preview
            cambios_lista.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ADD_CIRCLE_OUTLINE, size=16, color=Colors.ACCENT_SUCCESS),
                        ft.Container(width=8),
                        ft.Text(archivo, size=13, color=Colors.TEXT_PRIMARY, expand=True),
                        ft.Container(
                            content=ft.Icon(ft.Icons.VISIBILITY_OUTLINED, size=14, color=Colors.ACCENT_INFO),
                            on_click=lambda _, a=archivo, ver=v1['version']: self.preview_archivo(ver, a),
                            padding=6,
                            border_radius=8,
                            ink=True,
                            tooltip="Vista previa",
                            bgcolor=Colors.INFO_BG,
                        ) if tiene_preview else ft.Container(),
                        ft.Container(width=8) if tiene_preview else ft.Container(),
                        ft.Container(
                            content=ft.Text("NUEVO", size=10, color=Colors.ACCENT_SUCCESS, weight=ft.FontWeight.W_600),
                            bgcolor=Colors.SUCCESS_BG,
                            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                            border_radius=8,
                        ),
                    ], spacing=0),
                    padding=ft.Padding.all(10),
                    bgcolor=Colors.BG_SECONDARY,
                    border_radius=8,
                )
            )
        
        # Archivos eliminados
        for archivo in sorted(eliminados):
            tiene_preview = Path(archivo).suffix.lower() in extensiones_preview
            cambios_lista.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.REMOVE_CIRCLE_OUTLINE, size=16, color=Colors.ACCENT_DANGER),
                        ft.Container(width=8),
                        ft.Text(archivo, size=13, color=Colors.TEXT_PRIMARY, expand=True),
                        ft.Container(
                            content=ft.Icon(ft.Icons.VISIBILITY_OUTLINED, size=14, color=Colors.ACCENT_INFO),
                            on_click=lambda _, a=archivo, ver=v2['version']: self.preview_archivo(ver, a),
                            padding=6,
                            border_radius=8,
                            ink=True,
                            tooltip="Vista previa",
                            bgcolor=Colors.INFO_BG,
                        ) if tiene_preview else ft.Container(),
                        ft.Container(width=8) if tiene_preview else ft.Container(),
                        ft.Container(
                            content=ft.Text("ELIMINADO", size=10, color=Colors.ACCENT_DANGER, weight=ft.FontWeight.W_600),
                            bgcolor=Colors.DANGER_BG,
                            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                            border_radius=8,
                        ),
                    ], spacing=0),
                    padding=ft.Padding.all(10),
                    bgcolor=Colors.BG_SECONDARY,
                    border_radius=8,
                )
            )
        
        # Archivos modificados
        for archivo in sorted(modificados):
            tiene_preview = Path(archivo).suffix.lower() in extensiones_preview
            cambios_lista.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.EDIT_OUTLINED, size=16, color=Colors.ACCENT_WARNING),
                        ft.Container(width=8),
                        ft.Text(archivo, size=13, color=Colors.TEXT_PRIMARY, expand=True),
                        ft.Container(
                            content=ft.Icon(ft.Icons.VISIBILITY_OUTLINED, size=14, color=Colors.ACCENT_INFO),
                            on_click=lambda _, a=archivo, ver=v1['version']: self.preview_archivo(ver, a),
                            padding=6,
                            border_radius=8,
                            ink=True,
                            tooltip="Vista previa",
                            bgcolor=Colors.INFO_BG,
                        ) if tiene_preview else ft.Container(),
                        ft.Container(width=8) if tiene_preview else ft.Container(),
                        ft.Container(
                            content=ft.Text("MODIFICADO", size=10, color=Colors.ACCENT_WARNING, weight=ft.FontWeight.W_600),
                            bgcolor=Colors.WARNING_BG,
                            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
                            border_radius=8,
                        ),
                    ], spacing=0),
                    padding=ft.Padding.all(10),
                    bgcolor=Colors.BG_SECONDARY,
                    border_radius=8,
                )
            )
        
        # Si no hay cambios
        if not cambios_lista:
            cambios_lista.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=40, color=Colors.ACCENT_SUCCESS),
                        ft.Container(height=12),
                        ft.Text("Sin cambios", size=15, color=Colors.TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40,
                    alignment=ft.alignment.Alignment(0, 0),
                )
            )
        
        # Header con botón de volver
        header = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.ARROW_BACK_ROUNDED, size=20, color=Colors.TEXT_PRIMARY),
                    on_click=lambda _: self.volver_a_proyecto(),
                    padding=10,
                    border_radius=10,
                    ink=True,
                    tooltip="Volver",
                ),
                ft.Container(width=12),
                ft.Column([
                    ft.Text("Comparación de Versiones", 
                           size=20, 
                           weight=ft.FontWeight.W_600,
                           color=Colors.TEXT_PRIMARY),
                    ft.Text(f"v{v1['version']} ← v{v2['version']}", 
                           size=13, 
                           color=Colors.TEXT_MUTED),
                ], spacing=2),
            ]),
            bgcolor=Colors.BG_SECONDARY,
            padding=ft.Padding.symmetric(horizontal=24, vertical=18),
            border=ft.Border.only(bottom=ft.BorderSide(1, Colors.BORDER_LIGHT)),
        )
        
        # Resumen de cambios
        resumen = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(len(agregados)), size=24, weight=ft.FontWeight.W_600, color=Colors.ACCENT_SUCCESS),
                        ft.Text("Nuevos", size=13, color=Colors.TEXT_MUTED),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    expand=True,
                    bgcolor=Colors.SUCCESS_BG,
                    padding=20,
                    border_radius=12,
                ),
                ft.Container(width=12),
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(len(modificados)), size=24, weight=ft.FontWeight.W_600, color=Colors.ACCENT_WARNING),
                        ft.Text("Modificados", size=13, color=Colors.TEXT_MUTED),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    expand=True,
                    bgcolor=Colors.WARNING_BG,
                    padding=20,
                    border_radius=12,
                ),
                ft.Container(width=12),
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(len(eliminados)), size=24, weight=ft.FontWeight.W_600, color=Colors.ACCENT_DANGER),
                        ft.Text("Eliminados", size=13, color=Colors.TEXT_MUTED),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                    expand=True,
                    bgcolor=Colors.DANGER_BG,
                    padding=20,
                    border_radius=12,
                ),
            ]),
            padding=ft.Padding.all(24),
        )
        
        # Lista de cambios con scroll
        lista_cambios = ft.Container(
            content=ft.Column(
                controls=cambios_lista,
                spacing=8,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=ft.Padding.symmetric(horizontal=24),
            expand=True,
        )
        
        # Layout principal
        self.page.add(
            ft.Column([
                header,
                resumen,
                lista_cambios,
            ], spacing=0, expand=True)
        )
        self.page.update()
    
    def volver_a_proyecto(self):
        """Vuelve a la vista del proyecto desde la comparación"""
        self.comparacion_actual = None
        self.mostrar_vista_proyecto()
    
    def mostrar_snackbar(self, mensaje, error=False):
        """Muestra notificación tipo toast compacta en la esquina inferior derecha"""
        # Crear toast compacto
        toast_content = ft.Container(
            content=ft.Row([
                ft.Icon(
                    ft.Icons.CHECK_CIRCLE_ROUNDED if not error else ft.Icons.ERROR_ROUNDED,
                    color=ft.Colors.WHITE,
                    size=16,
                ),
                ft.Container(width=8),
                ft.Container(
                    content=ft.Text(mensaje, 
                           color=ft.Colors.WHITE, 
                           weight=ft.FontWeight.W_500, 
                           size=13,
                           no_wrap=False,
                           max_lines=3),
                    expand=True,
                ),
            ], spacing=0, tight=True),
            bgcolor=Colors.ACCENT_SUCCESS if not error else Colors.ACCENT_DANGER,
            padding=ft.Padding.all(14),
            border_radius=8,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            width=320,  # Ancho aumentado
            visible=False,
        )
        
        # Contenedor posicionado en esquina inferior derecha
        toast_container = ft.Stack([
            ft.Container(
                content=toast_content,
                right=24,
                bottom=24,
            )
        ])
        
        # Agregar overlay
        self.page.overlay.append(toast_container)
        self.page.update()
        
        # Mostrar y ocultar
        import asyncio
        async def mostrar_y_ocultar():
            await asyncio.sleep(0.05)
            toast_content.visible = True
            self.page.update()
            
            # Esperar 3 segundos
            await asyncio.sleep(3)
            
            # Ocultar
            toast_content.visible = False
            self.page.update()
            
            # Esperar un poco y remover
            await asyncio.sleep(0.1)
            try:
                if toast_container in self.page.overlay:
                    self.page.overlay.remove(toast_container)
                    self.page.update()
            except:
                pass
        
        # Ejecutar la tarea async
        try:
            self.page.run_task(mostrar_y_ocultar)
        except:
            # Fallback a threading si run_task no está disponible
            import threading
            import time
            def mostrar_sync():
                time.sleep(0.05)
                toast_content.visible = True
                try:
                    self.page.update()
                except:
                    pass
                
                time.sleep(3)
                toast_content.visible = False
                try:
                    self.page.update()
                except:
                    pass
                
                time.sleep(0.1)
                try:
                    if toast_container in self.page.overlay:
                        self.page.overlay.remove(toast_container)
                        self.page.update()
                except:
                    pass
            
            threading.Thread(target=mostrar_sync, daemon=True).start()
    
    def exportar_proyecto(self):
        """Exporta el proyecto completo a un archivo ZIP"""
        if not self.proyecto_actual:
            return
        
        try:
            # Obtener nombre del proyecto
            try:
                with open(Path(self.proyecto_actual) / ".cronux" / "proyecto.json", "r") as f:
                    datos = json.load(f)
                    nombre_proyecto = datos.get("nombre", "proyecto")
            except:
                nombre_proyecto = "proyecto"
            
            # Crear nombre del archivo ZIP
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_zip = f"{nombre_proyecto}_{timestamp}.zip"
            
            # Usar selector nativo para guardar archivo
            ruta_zip = seleccionar_archivo(
                titulo="Guardar exportación",
                guardar=True,
                nombre_default=nombre_zip
            )
            
            if not ruta_zip:
                return  # Usuario canceló
            
            # Asegurar extensión .zip
            if not ruta_zip.endswith('.zip'):
                ruta_zip += '.zip'
            
            # Crear ZIP con todo el proyecto
            with zipfile.ZipFile(ruta_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                proyecto_path = Path(self.proyecto_actual)
                
                # Agregar todos los archivos del proyecto
                for item in proyecto_path.rglob('*'):
                    if item.is_file():
                        arcname = item.relative_to(proyecto_path.parent)
                        zipf.write(item, arcname)
            
            self.mostrar_snackbar(f"Proyecto exportado correctamente")
            
        except Exception as ex:
            self.mostrar_snackbar(f"Error al exportar: {ex}", error=True)
    
    def importar_proyecto(self):
        """Importa un proyecto desde un archivo ZIP"""
        try:
            # Seleccionar archivo ZIP
            archivo_zip = seleccionar_archivo(
                titulo="Seleccionar proyecto ZIP",
                filtros="Archivos ZIP | *.zip"
            )
            
            if not archivo_zip:
                return  # Usuario canceló
            
            # Seleccionar carpeta de destino
            carpeta_destino = seleccionar_carpeta("Seleccionar carpeta de destino")
            
            if not carpeta_destino:
                return  # Usuario canceló
            
            carpeta_destino = Path(carpeta_destino)
            
            # Extraer ZIP
            with zipfile.ZipFile(archivo_zip, 'r') as zipf:
                zipf.extractall(carpeta_destino)
            
            # Buscar la carpeta del proyecto (la que contiene .cronux)
            proyecto_importado = None
            for item in carpeta_destino.rglob('.cronux'):
                if item.is_dir():
                    proyecto_importado = item.parent
                    break
            
            if not proyecto_importado:
                self.mostrar_snackbar("El ZIP no contiene un proyecto Cronux válido", error=True)
                return
            
            # Leer nombre del proyecto
            try:
                with open(proyecto_importado / ".cronux" / "proyecto.json", "r") as f:
                    datos = json.load(f)
                    nombre = datos.get("nombre", proyecto_importado.name)
            except:
                nombre = proyecto_importado.name
            
            # Agregar a la lista
            self.agregar_proyecto(proyecto_importado, nombre)
            self.mostrar_snackbar(f"Proyecto '{nombre}' importado correctamente")
            self.mostrar_pantalla_inicio()
            
        except Exception as ex:
            self.mostrar_snackbar(f"Error al importar: {ex}", error=True)
        except Exception as ex:
            self.mostrar_snackbar(f"Error al importar: {ex}", error=True)
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas en una vista completa tipo dashboard"""
        if not self.proyecto_actual:
            return
        
        self.vista_actual = "estadisticas"
        versiones = self.obtener_versiones()
        
        if not versiones:
            self.mostrar_snackbar("No hay versiones para mostrar estadísticas", error=True)
            return
        
        # Calcular estadísticas con cache
        cache_key = self.proyecto_actual
        current_time = datetime.now().timestamp()
        
        if cache_key in self._cache_estadisticas:
            if current_time - self._cache_timestamp.get(f"{cache_key}_stats", 0) < 10:
                stats = self._cache_estadisticas[cache_key]
            else:
                stats = self._calcular_estadisticas(versiones)
                self._cache_estadisticas[cache_key] = stats
                self._cache_timestamp[f"{cache_key}_stats"] = current_time
        else:
            stats = self._calcular_estadisticas(versiones)
            self._cache_estadisticas[cache_key] = stats
            self._cache_timestamp[f"{cache_key}_stats"] = current_time
        
        # Obtener nombre del proyecto
        try:
            with open(Path(self.proyecto_actual) / ".cronux" / "proyecto.json", "r") as f:
                datos = json.load(f)
                nombre_proyecto = datos.get("nombre", "Proyecto")
        except:
            nombre_proyecto = "Proyecto"
        
        # Limpiar página
        self.page.controls.clear()
        
        # Header del dashboard
        header = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.ARROW_BACK_ROUNDED, size=20, color=Colors.TEXT_SECONDARY),
                    on_click=lambda _: self.mostrar_vista_proyecto(),
                    padding=8,
                    ink=True,
                    border_radius=20,
                    tooltip="Volver",
                ),
                ft.Container(width=16),
                ft.Icon(ft.Icons.BAR_CHART_ROUNDED, size=24, color=Colors.ACCENT_PRIMARY),
                ft.Container(width=12),
                ft.Column([
                    ft.Text("Estadísticas", 
                           size=20, 
                           weight=ft.FontWeight.W_600, 
                           color=Colors.TEXT_PRIMARY),
                    ft.Text(nombre_proyecto, 
                           size=14, 
                           color=Colors.TEXT_MUTED),
                ], spacing=2),
            ]),
            bgcolor=Colors.BG_SECONDARY,
            padding=ft.Padding.symmetric(horizontal=24, vertical=16),
            border=ft.Border.only(bottom=ft.BorderSide(1, Colors.BORDER_LIGHT)),
        )
        
        # Calcular porcentajes para distribución
        total_cambios = stats['total_agregados'] + stats['total_eliminados']
        
        # Contenido principal del dashboard
        contenido = ft.Container(
            content=ft.Column([
                # Fila superior: Métricas principales (más compactas)
                ft.Row([
                    # Versiones
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.HISTORY_ROUNDED, size=24, color=ft.Colors.WHITE),
                                bgcolor=Colors.ACCENT_PRIMARY,
                                padding=10,
                                border_radius=10,
                            ),
                            ft.Container(width=12),
                            ft.Column([
                                ft.Text("Versiones", 
                                       size=12, 
                                       color=Colors.TEXT_MUTED,
                                       weight=ft.FontWeight.W_500),
                                ft.Container(height=2),
                                ft.Text(str(stats['total_versiones']), 
                                       size=24, 
                                       weight=ft.FontWeight.W_700, 
                                       color=Colors.TEXT_PRIMARY),
                            ], spacing=0),
                        ]),
                        bgcolor=Colors.BG_SECONDARY,
                        padding=16,
                        border_radius=12,
                        expand=True,
                        border=ft.Border.all(1, Colors.BORDER_LIGHT),
                    ),
                    ft.Container(width=12),
                    # Tamaño Total
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.STORAGE_ROUNDED, size=24, color=ft.Colors.WHITE),
                                bgcolor=Colors.ACCENT_INFO,
                                padding=10,
                                border_radius=10,
                            ),
                            ft.Container(width=12),
                            ft.Column([
                                ft.Text("Tamaño Total", 
                                       size=12, 
                                       color=Colors.TEXT_MUTED,
                                       weight=ft.FontWeight.W_500),
                                ft.Container(height=2),
                                ft.Text(f"{stats['tamaño_total']:.1f} MB", 
                                       size=24, 
                                       weight=ft.FontWeight.W_700, 
                                       color=Colors.TEXT_PRIMARY),
                            ], spacing=0),
                        ]),
                        bgcolor=Colors.BG_SECONDARY,
                        padding=16,
                        border_radius=12,
                        expand=True,
                        border=ft.Border.all(1, Colors.BORDER_LIGHT),
                    ),
                    ft.Container(width=12),
                    # Archivos
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.FOLDER_OUTLINED, size=24, color=ft.Colors.WHITE),
                                bgcolor=Colors.ACCENT_SUCCESS,
                                padding=10,
                                border_radius=10,
                            ),
                            ft.Container(width=12),
                            ft.Column([
                                ft.Text("Archivos", 
                                       size=12, 
                                       color=Colors.TEXT_MUTED,
                                       weight=ft.FontWeight.W_500),
                                ft.Container(height=2),
                                ft.Text(str(stats['archivos_total']), 
                                       size=24, 
                                       weight=ft.FontWeight.W_700, 
                                       color=Colors.TEXT_PRIMARY),
                            ], spacing=0),
                        ]),
                        bgcolor=Colors.BG_SECONDARY,
                        padding=16,
                        border_radius=12,
                        expand=True,
                        border=ft.Border.all(1, Colors.BORDER_LIGHT),
                    ),
                ], expand=True),
                
                ft.Container(height=16),
                
                # Fila media: Información adicional (más compacta)
                ft.Row([
                    # Tamaño promedio
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.INSIGHTS_ROUNDED, size=16, color=Colors.ACCENT_SECONDARY),
                                ft.Container(width=6),
                                ft.Text("Tamaño Promedio", 
                                       size=12, 
                                       color=Colors.TEXT_MUTED,
                                       weight=ft.FontWeight.W_500),
                            ]),
                            ft.Container(height=8),
                            ft.Text(f"{stats['tamaño_promedio']:.2f} MB", 
                                   size=20, 
                                   weight=ft.FontWeight.W_700, 
                                   color=Colors.TEXT_PRIMARY),
                            ft.Container(height=2),
                            ft.Text("por versión", 
                                   size=11, 
                                   color=Colors.TEXT_MUTED),
                        ], spacing=0),
                        bgcolor=Colors.BG_SECONDARY,
                        padding=16,
                        border_radius=12,
                        expand=True,
                        border=ft.Border.all(1, Colors.BORDER_LIGHT),
                    ),
                    ft.Container(width=12),
                    # Total de cambios
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.SYNC_ROUNDED, size=16, color=Colors.ACCENT_WARNING),
                                ft.Container(width=6),
                                ft.Text("Total de Cambios", 
                                       size=12, 
                                       color=Colors.TEXT_MUTED,
                                       weight=ft.FontWeight.W_500),
                            ]),
                            ft.Container(height=8),
                            ft.Text(str(total_cambios), 
                                   size=20, 
                                   weight=ft.FontWeight.W_700, 
                                   color=Colors.TEXT_PRIMARY),
                            ft.Container(height=2),
                            ft.Text("en últimas 10 versiones", 
                                   size=11, 
                                   color=Colors.TEXT_MUTED),
                        ], spacing=0),
                        bgcolor=Colors.BG_SECONDARY,
                        padding=16,
                        border_radius=12,
                        expand=True,
                        border=ft.Border.all(1, Colors.BORDER_LIGHT),
                    ),
                ], expand=True),
                
                ft.Container(height=20),
                
                # Sección de actividad
                ft.Text("Actividad del Proyecto", 
                       size=18, 
                       weight=ft.FontWeight.W_600, 
                       color=Colors.TEXT_PRIMARY),
                ft.Container(height=16),
                
                # Distribución de cambios con barras horizontales
                ft.Container(
                    content=ft.Column([
                        # Agregados
                        ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.ADD_CIRCLE_ROUNDED, size=20, color=Colors.ACCENT_SUCCESS),
                                ft.Container(width=12),
                                ft.Text("Agregados", 
                                       size=15, 
                                       color=Colors.TEXT_PRIMARY,
                                       weight=ft.FontWeight.W_600),
                                ft.Container(expand=True),
                                ft.Text(str(stats['total_agregados']), 
                                       size=20, 
                                       weight=ft.FontWeight.W_700, 
                                       color=Colors.ACCENT_SUCCESS),
                                ft.Container(width=8),
                                ft.Text(f"{(stats['total_agregados']/total_cambios*100):.0f}%" if total_cambios > 0 else "0%", 
                                       size=14, 
                                       color=Colors.TEXT_MUTED),
                            ]),
                            ft.Container(height=12),
                            ft.Container(
                                content=ft.Container(
                                    width=f"{(stats['total_agregados']/total_cambios*100) if total_cambios > 0 else 0}%",
                                    height=10,
                                    bgcolor=Colors.ACCENT_SUCCESS,
                                    border_radius=5,
                                ),
                                bgcolor=Colors.SUCCESS_BG,
                                height=10,
                                border_radius=5,
                            ),
                        ], spacing=0),
                        
                        ft.Container(height=20),
                        
                        # Eliminados
                        ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.REMOVE_CIRCLE_ROUNDED, size=20, color=Colors.ACCENT_DANGER),
                                ft.Container(width=12),
                                ft.Text("Eliminados", 
                                       size=15, 
                                       color=Colors.TEXT_PRIMARY,
                                       weight=ft.FontWeight.W_600),
                                ft.Container(expand=True),
                                ft.Text(str(stats['total_eliminados']), 
                                       size=20, 
                                       weight=ft.FontWeight.W_700, 
                                       color=Colors.ACCENT_DANGER),
                                ft.Container(width=8),
                                ft.Text(f"{(stats['total_eliminados']/total_cambios*100):.0f}%" if total_cambios > 0 else "0%", 
                                       size=14, 
                                       color=Colors.TEXT_MUTED),
                            ]),
                            ft.Container(height=12),
                            ft.Container(
                                content=ft.Container(
                                    width=f"{(stats['total_eliminados']/total_cambios*100) if total_cambios > 0 else 0}%",
                                    height=10,
                                    bgcolor=Colors.ACCENT_DANGER,
                                    border_radius=5,
                                ),
                                bgcolor=Colors.DANGER_BG,
                                height=10,
                                border_radius=5,
                            ),
                        ], spacing=0),
                    ], spacing=0),
                    bgcolor=Colors.BG_SECONDARY,
                    padding=24,
                    border_radius=12,
                    border=ft.Border.all(1, Colors.BORDER_LIGHT),
                ),
            ], scroll=ft.ScrollMode.AUTO),
            padding=24,
            expand=True,
        )
        
        # Agregar a la página
        self.page.add(
            ft.Column([header, contenido], spacing=0, expand=True)
        )
        self.page.update()
    
    def _calcular_estadisticas(self, versiones):
        """Calcula estadísticas de forma optimizada"""
        total_versiones = len(versiones)
        tamaños = []
        archivos_counts = []
        
        # Obtener datos básicos
        for v in reversed(versiones):
            carpeta_v = Path(self.proyecto_actual) / ".cronux" / "versiones" / f"version_{v['version']}"
            if carpeta_v.exists():
                metadatos_file = carpeta_v / "metadatos.json"
                if metadatos_file.exists():
                    try:
                        with open(metadatos_file, "r") as f:
                            meta = json.load(f)
                            tamaños.append(meta.get("tamaño_bytes", 0) / (1024 * 1024))
                            archivos_counts.append(meta.get("archivos_guardados", 0))
                    except:
                        pass
        
        # Calcular totales y promedios
        tamaño_total = sum(tamaños)
        tamaño_promedio = tamaño_total / len(tamaños) if tamaños else 0
        archivos_total = sum(archivos_counts)
        archivos_promedio = archivos_total / len(archivos_counts) if archivos_counts else 0
        
        # Calcular cambios (optimizado - solo últimas 10 versiones)
        total_agregados = 0
        total_eliminados = 0
        
        versiones_a_analizar = min(10, len(versiones) - 1)
        
        for i in range(versiones_a_analizar):
            v1 = versiones[i]
            v2 = versiones[i + 1]
            
            carpeta_v1 = Path(self.proyecto_actual) / ".cronux" / "versiones" / f"version_{v1['version']}"
            carpeta_v2 = Path(self.proyecto_actual) / ".cronux" / "versiones" / f"version_{v2['version']}"
            
            if carpeta_v1.exists() and carpeta_v2.exists():
                archivos_v1 = {item.name for item in carpeta_v1.iterdir() if item.name != "metadatos.json"}
                archivos_v2 = {item.name for item in carpeta_v2.iterdir() if item.name != "metadatos.json"}
                
                total_agregados += len(archivos_v1 - archivos_v2)
                total_eliminados += len(archivos_v2 - archivos_v1)
        
        return {
            'total_versiones': total_versiones,
            'tamaños': tamaños,
            'archivos_counts': archivos_counts,
            'tamaño_total': tamaño_total,
            'tamaño_promedio': tamaño_promedio,
            'archivos_total': archivos_total,
            'archivos_promedio': archivos_promedio,
            'total_agregados': total_agregados,
            'total_eliminados': total_eliminados,
        }
    
    
    def preview_archivo(self, version, nombre_archivo):
        """Muestra preview de un archivo (imagen o texto)"""
        carpeta_version = Path(self.proyecto_actual) / ".cronux" / "versiones" / f"version_{version}"
        archivo_path = carpeta_version / nombre_archivo
        
        if not archivo_path.exists():
            self.mostrar_snackbar("Archivo no encontrado", error=True)
            return
        
        # Detectar tipo de archivo
        extensiones_imagen = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'}
        extensiones_texto = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yaml', '.yml', '.sh', '.bat', '.c', '.cpp', '.h', '.java', '.go', '.rs', '.ts', '.tsx', '.jsx'}
        
        ext = archivo_path.suffix.lower()
        
        contenido = None
        es_imagen = ext in extensiones_imagen
        es_texto = ext in extensiones_texto
        
        if es_imagen:
            # Mostrar imagen
            contenido = ft.Container(
                content=ft.Image(
                    src=str(archivo_path),
                    fit=ft.ImageFit.CONTAIN,
                ),
                height=400,
                alignment=ft.alignment.Alignment(0, 0),
            )
        elif es_texto:
            # Mostrar texto
            try:
                with open(archivo_path, 'r', encoding='utf-8') as f:
                    texto = f.read()
                    # Limitar a 500 líneas
                    lineas = texto.split('\n')
                    if len(lineas) > 500:
                        texto = '\n'.join(lineas[:500]) + '\n\n... (archivo truncado)'
                    
                    contenido = ft.Container(
                        content=ft.Text(
                            texto,
                            size=12,
                            color=Colors.TEXT_PRIMARY,
                            font_family="monospace",
                            selectable=True,
                        ),
                        height=400,
                        padding=12,
                        bgcolor=Colors.BG_PRIMARY,
                        border_radius=8,
                    )
            except Exception as ex:
                contenido = ft.Container(
                    content=ft.Text(f"Error al leer archivo: {ex}", size=13, color=Colors.ACCENT_DANGER),
                    padding=20,
                )
        else:
            # Tipo no soportado
            tamaño = archivo_path.stat().st_size
            contenido = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INSERT_DRIVE_FILE_OUTLINED, size=48, color=Colors.TEXT_MUTED),
                    ft.Container(height=12),
                    ft.Text("Vista previa no disponible", size=15, color=Colors.TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                    ft.Container(height=8),
                    ft.Text(f"Tipo: {ext}", size=13, color=Colors.TEXT_MUTED),
                    ft.Text(f"Tamaño: {self.formatear_tamaño(tamaño)}", size=13, color=Colors.TEXT_MUTED),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=60,
                alignment=ft.alignment.Alignment(0, 0),
            )
        
        modal = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    # Header
                    ft.Row([
                        ft.Column([
                            ft.Text("Vista Previa", 
                                   size=18, 
                                   weight=ft.FontWeight.W_600,
                                   color=Colors.TEXT_PRIMARY),
                            ft.Container(height=4),
                            ft.Text(nombre_archivo, 
                                   size=13, 
                                   color=Colors.TEXT_MUTED,
                                   max_lines=1,
                                   overflow=ft.TextOverflow.ELLIPSIS),
                        ], spacing=0, expand=True),
                        ft.Container(
                            content=ft.Icon(ft.Icons.CLOSE_ROUNDED, size=24, color=Colors.TEXT_PRIMARY),
                            on_click=lambda _: self.cerrar_modal(modal),
                            padding=8,
                            border_radius=20,
                            ink=True,
                        ),
                    ]),
                    
                    ft.Container(height=16),
                    
                    # Contenido
                    ft.Container(
                        content=ft.Column([contenido], scroll=ft.ScrollMode.AUTO),
                        expand=True,
                    ),
                ], spacing=0, tight=True),
                padding=ft.Padding.all(24),
                bgcolor=Colors.BG_SECONDARY,
                border_radius=ft.BorderRadius.only(top_left=20, top_right=20),
                height=550,
            ),
            open=True,
        )
        
        self.page.overlay.append(modal)
        self.page.update()
    
    def cerrar_modal(self, modal):
        """Cierra un modal (BottomSheet)"""
        modal.open = False
        self.page.update()


def main(page: ft.Page):
    CronuxGUI(page)


if __name__ == "__main__":
    # Configurar la aplicación con el icono correcto
    import sys
    import os
    
    # En macOS, establecer el nombre de la app antes de iniciar Flet
    if platform.system() == "Darwin":
        try:
            # Intentar establecer el nombre de la app en macOS
            from Foundation import NSBundle
            bundle = NSBundle.mainBundle()
            if bundle:
                info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
                if info:
                    info['CFBundleName'] = 'Cronux'
                    info['CFBundleDisplayName'] = 'Cronux'
        except:
            pass
    
    # Obtener la ruta del icono
    if getattr(sys, 'frozen', False):
        # Si está empaquetado con PyInstaller
        bundle_dir = sys._MEIPASS
        icon_path = os.path.join(bundle_dir, 'assets', 'cronux_cli.icns')
    else:
        # Si se ejecuta desde el código fuente
        icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'cronux_cli.icns')
    
    # Iniciar la aplicación con configuración personalizada
    ft.app(
        target=main,
        name="Cronux",
        assets_dir="assets"
    )

