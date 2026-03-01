#!/usr/bin/env python3
"""
Instalador GUI para Cronux-CRX con Flet
Sistema de Control de Versiones v0.1.0 Beta
"""

import flet as ft
import os
import sys
import shutil
from pathlib import Path
import platform

# Importar módulos específicos de Windows solo si estamos en Windows
if platform.system() == "Windows":
    import winreg
    import ctypes
else:
    winreg = None
    ctypes = None


# Paleta de colores - Diseño Minimalista
class Colors:
    _theme_mode = ft.ThemeMode.LIGHT
    
    @classmethod
    def set_theme(cls, theme_mode):
        cls._theme_mode = theme_mode
    
    @classmethod
    def _get_colors(cls):
        is_dark = cls._theme_mode == ft.ThemeMode.DARK
        
        if is_dark:
            return {
                "BG_PRIMARY": "#1a1a1a",
                "BG_SECONDARY": "#242424",
                "BG_TERTIARY": "#2d2d2d",
                "BORDER_DEFAULT": "#3a3a3a",
                "TEXT_PRIMARY": "#e8e8e8",
                "TEXT_SECONDARY": "#b8b8b8",
                "TEXT_MUTED": "#888888",
                "ACCENT_PRIMARY": "#ff4757",
                "ACCENT_SUCCESS": "#10b981",
                "ACCENT_DANGER": "#ef4444",
                "ACCENT_WARNING": "#f59e0b",
                "SUCCESS_BG": "#1f3d2d",
                "DANGER_BG": "#3d1f23",
                "WARNING_BG": "#3d331f",
            }
        else:
            return {
                "BG_PRIMARY": "#f8f9fa",
                "BG_SECONDARY": "#ffffff",
                "BG_TERTIARY": "#e9ecef",
                "BORDER_DEFAULT": "#dee2e6",
                "TEXT_PRIMARY": "#1a1a1a",
                "TEXT_SECONDARY": "#4a4a4a",
                "TEXT_MUTED": "#8a8a8a",
                "ACCENT_PRIMARY": "#ff4757",
                "ACCENT_SUCCESS": "#1dd1a1",
                "ACCENT_DANGER": "#ee5a6f",
                "ACCENT_WARNING": "#feca57",
                "SUCCESS_BG": "#d4f8f0",
                "DANGER_BG": "#ffeaed",
                "WARNING_BG": "#fff4d9",
            }
    
    def __getattr__(self, name):
        colors = self._get_colors()
        if name in colors:
            return colors[name]
        raise AttributeError(f"Color '{name}' no encontrado")
    
    @property
    def BG_PRIMARY(self): return self._get_colors()["BG_PRIMARY"]
    @property
    def BG_SECONDARY(self): return self._get_colors()["BG_SECONDARY"]
    @property
    def BG_TERTIARY(self): return self._get_colors()["BG_TERTIARY"]
    @property
    def BORDER_DEFAULT(self): return self._get_colors()["BORDER_DEFAULT"]
    @property
    def TEXT_PRIMARY(self): return self._get_colors()["TEXT_PRIMARY"]
    @property
    def TEXT_SECONDARY(self): return self._get_colors()["TEXT_SECONDARY"]
    @property
    def TEXT_MUTED(self): return self._get_colors()["TEXT_MUTED"]
    @property
    def ACCENT_PRIMARY(self): return self._get_colors()["ACCENT_PRIMARY"]
    @property
    def ACCENT_SUCCESS(self): return self._get_colors()["ACCENT_SUCCESS"]
    @property
    def ACCENT_DANGER(self): return self._get_colors()["ACCENT_DANGER"]
    @property
    def ACCENT_WARNING(self): return self._get_colors()["ACCENT_WARNING"]
    @property
    def SUCCESS_BG(self): return self._get_colors()["SUCCESS_BG"]
    @property
    def DANGER_BG(self): return self._get_colors()["DANGER_BG"]
    @property
    def WARNING_BG(self): return self._get_colors()["WARNING_BG"]


Colors = Colors()


class CronuxInstaller:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "CRONUX-CRX Installer"
        self.page.window.width = 600
        self.page.window.height = 700
        self.page.window.min_width = 500
        self.page.window.min_height = 600
        self.page.window.resizable = False
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.LIGHT
        
        # Intentar cargar el icono
        try:
            icon_path = Path(__file__).parent / "assets" / "cronux_cli.png"
            if icon_path.exists():
                self.page.window_icon = str(icon_path)
        except:
            pass
        
        Colors.set_theme(self.page.theme_mode)
        self.page.bgcolor = Colors.BG_PRIMARY
        
        # Detectar sistema operativo
        self.is_windows = platform.system() == "Windows"
        
        if not self.is_windows:
            self.show_windows_only()
            return
        
        self.install_path = os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Cronux-CRX')
        self.is_installed = self.check_installation()
        
        # Verificar permisos de administrador
        if not self.is_admin():
            self.show_admin_required()
            return
        
        self.setup_ui()
    
    def close_app(self):
        """Cierra la aplicación"""
        self.page.window_destroy()
    
    def is_admin(self):
        """Verifica si tiene permisos de administrador"""
        if not self.is_windows or ctypes is None:
            return False
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def show_windows_only(self):
        """Muestra mensaje de que solo funciona en Windows"""
        self.page.controls.clear()
        
        logo_path = Path(__file__).parent / "assets" / "cronux_cli.png"
        logo = None
        if logo_path.exists():
            logo = ft.Image(src=str(logo_path), width=80, height=80)
        
        self.page.add(
            ft.Container(
                content=ft.Column([
                    logo if logo else ft.Icon(ft.Icons.DESKTOP_WINDOWS, size=80, color=Colors.ACCENT_WARNING),
                    ft.Container(height=24),
                    ft.Text("Solo para Windows",
                           size=20,
                           weight=ft.FontWeight.W_600,
                           color=Colors.TEXT_PRIMARY,
                           text_align=ft.TextAlign.CENTER),
                    ft.Container(height=16),
                    ft.Text(f"Este instalador solo funciona en Windows.\nSistema detectado: {platform.system()}",
                           size=14,
                           color=Colors.TEXT_SECONDARY,
                           text_align=ft.TextAlign.CENTER),
                    ft.Container(height=24),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Para Linux/macOS, usa:", size=13, color=Colors.TEXT_SECONDARY, weight=ft.FontWeight.W_600),
                            ft.Container(height=8),
                            ft.Text("pip install cronux-crx", size=12, color=Colors.TEXT_MUTED),
                            ft.Text("o clona el repositorio", size=12, color=Colors.TEXT_MUTED),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                        padding=20,
                        bgcolor=Colors.WARNING_BG,
                        border_radius=12,
                    ),
                    ft.Container(height=24),
                    ft.Container(
                        content=ft.Text("Cerrar", color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.W_500),
                        bgcolor=Colors.ACCENT_PRIMARY,
                        padding=ft.Padding.symmetric(horizontal=40, vertical=14),
                        border_radius=25,
                        on_click=lambda _: self.close_app(),
                        ink=True,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.Alignment(0, 0),
                expand=True,
                padding=40,
            )
        )
        self.page.update()
    
    def show_admin_required(self):
        """Muestra mensaje de permisos requeridos"""
        self.page.controls.clear()
        
        logo_path = Path(__file__).parent / "assets" / "cronux_cli.png"
        logo = None
        if logo_path.exists():
            logo = ft.Image(src=str(logo_path), width=80, height=80)
        
        self.page.add(
            ft.Container(
                content=ft.Column([
                    logo if logo else ft.Icon(ft.Icons.ADMIN_PANEL_SETTINGS, size=80, color=Colors.ACCENT_WARNING),
                    ft.Container(height=24),
                    ft.Text("Permisos de Administrador Requeridos",
                           size=20,
                           weight=ft.FontWeight.W_600,
                           color=Colors.TEXT_PRIMARY,
                           text_align=ft.TextAlign.CENTER),
                    ft.Container(height=16),
                    ft.Text("Cronux-CRX necesita permisos de administrador para:",
                           size=14,
                           color=Colors.TEXT_SECONDARY,
                           text_align=ft.TextAlign.CENTER),
                    ft.Container(height=16),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("• Instalar archivos en Program Files", size=13, color=Colors.TEXT_SECONDARY),
                            ft.Text("• Agregar al PATH del sistema", size=13, color=Colors.TEXT_SECONDARY),
                            ft.Text("• Crear accesos directos", size=13, color=Colors.TEXT_SECONDARY),
                        ], spacing=8),
                        padding=20,
                        bgcolor=Colors.WARNING_BG,
                        border_radius=12,
                    ),
                    ft.Container(height=24),
                    ft.Text("Por favor, ejecuta este instalador como administrador",
                           size=13,
                           color=Colors.TEXT_MUTED,
                           text_align=ft.TextAlign.CENTER),
                    ft.Container(height=24),
                    ft.Container(
                        content=ft.Text("Cerrar", color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.W_500),
                        bgcolor=Colors.ACCENT_PRIMARY,
                        padding=ft.Padding.symmetric(horizontal=40, vertical=14),
                        border_radius=25,
                        on_click=lambda _: self.close_app(),
                        ink=True,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.Alignment(0, 0),
                expand=True,
                padding=40,
            )
        )
        self.page.update()
    
    def check_installation(self):
        """Verifica si ya está instalado"""
        return os.path.exists(self.install_path)
    
    def setup_ui(self):
        """Configura la interfaz principal"""
        self.page.controls.clear()
        
        # Cargar logo
        logo_path = Path(__file__).parent / "assets" / "cronux_cli.png"
        logo = None
        if logo_path.exists():
            logo = ft.Image(src=str(logo_path), width=80, height=80)
        
        # Header
        header = ft.Container(
            content=ft.Column([
                ft.Container(height=30),
                logo if logo else ft.Icon(ft.Icons.HISTORY_ROUNDED, size=80, color=Colors.ACCENT_PRIMARY),
                ft.Container(height=16),
                ft.Text("CRONUX-CRX",
                       size=32,
                       weight=ft.FontWeight.W_700,
                       color=Colors.TEXT_PRIMARY),
                ft.Container(height=8),
                ft.Text("Sistema de Control de Versiones v0.1.0 Beta",
                       size=14,
                       color=Colors.TEXT_MUTED),
                ft.Container(height=30),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=Colors.BG_SECONDARY,
            border=ft.Border.only(bottom=ft.BorderSide(1, Colors.BORDER_DEFAULT)),
        )
        
        # Estado de instalación
        if self.is_installed:
            status_color = Colors.ACCENT_SUCCESS
            status_text = "INSTALADO"
            status_icon = ft.Icons.CHECK_CIRCLE
            path_text = f"Ubicación: {self.install_path}"
        else:
            status_color = Colors.TEXT_MUTED
            status_text = "NO INSTALADO"
            status_icon = ft.Icons.INFO_OUTLINE
            path_text = "Listo para instalar"
        
        status_card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(status_icon, color=status_color, size=20),
                    ft.Container(width=8),
                    ft.Text(status_text,
                           size=16,
                           weight=ft.FontWeight.W_600,
                           color=status_color),
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=8),
                ft.Text(path_text,
                       size=12,
                       color=Colors.TEXT_MUTED,
                       text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=Colors.BG_SECONDARY,
            padding=20,
            border_radius=12,
            border=ft.Border.all(1, Colors.BORDER_DEFAULT),
        )
        
        # Barra de progreso
        self.progress_bar = ft.ProgressBar(
            value=0,
            color=Colors.ACCENT_PRIMARY,
            bgcolor=Colors.BG_TERTIARY,
            height=8,
            border_radius=4,
        )
        
        self.progress_text = ft.Text("",
                                     size=12,
                                     color=Colors.TEXT_MUTED,
                                     text_align=ft.TextAlign.CENTER)
        
        progress_container = ft.Container(
            content=ft.Column([
                self.progress_bar,
                ft.Container(height=8),
                self.progress_text,
            ]),
            padding=ft.Padding.symmetric(horizontal=40),
        )
        
        # Botones
        buttons = []
        
        if not self.is_installed:
            install_btn = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DOWNLOAD_ROUNDED, color=ft.Colors.WHITE, size=18),
                    ft.Text("Instalar", color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.W_600),
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=Colors.ACCENT_PRIMARY,
                padding=ft.Padding.symmetric(horizontal=40, vertical=14),
                border_radius=25,
                on_click=lambda _: self.install(),
                ink=True,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=20,
                    color=ft.Colors.with_opacity(0.3, Colors.ACCENT_PRIMARY),
                    offset=ft.Offset(0, 4),
                ),
            )
            buttons.append(install_btn)
        else:
            uninstall_btn = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DELETE_OUTLINE, color=ft.Colors.WHITE, size=18),
                    ft.Text("Desinstalar", color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.W_600),
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=Colors.ACCENT_DANGER,
                padding=ft.Padding.symmetric(horizontal=40, vertical=14),
                border_radius=25,
                on_click=lambda _: self.uninstall(),
                ink=True,
            )
            buttons.append(uninstall_btn)
        
        close_btn = ft.Container(
            content=ft.Text("Cerrar", color=Colors.TEXT_PRIMARY, size=14, weight=ft.FontWeight.W_500),
            bgcolor=Colors.BG_SECONDARY,
            padding=ft.Padding.symmetric(horizontal=40, vertical=14),
            border_radius=25,
            border=ft.Border.all(1, Colors.BORDER_DEFAULT),
            on_click=lambda _: self.close_app(),
            ink=True,
        )
        buttons.append(close_btn)
        
        button_row = ft.Row(
            buttons,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
        )
        
        # Footer
        footer = ft.Container(
            content=ft.Text("v0.1.0 Beta - Cronux Team",
                           size=11,
                           color=Colors.TEXT_MUTED),
            padding=20,
            alignment=ft.alignment.Alignment(0, 0),
        )
        
        # Layout principal
        self.page.add(
            ft.Column([
                header,
                ft.Container(
                    content=ft.Column([
                        ft.Container(height=30),
                        status_card,
                        ft.Container(height=30),
                        progress_container,
                        ft.Container(height=40),
                        button_row,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.Padding.symmetric(horizontal=40),
                    expand=True,
                ),
                footer,
            ], spacing=0, expand=True)
        )
        self.page.update()
    
    def update_progress(self, value, text):
        """Actualiza la barra de progreso"""
        self.progress_bar.value = value
        self.progress_text.value = text
        self.page.update()

    
    def add_to_path(self):
        """Agrega al PATH del sistema"""
        if not self.is_windows or winreg is None:
            return False
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
                0,
                winreg.KEY_ALL_ACCESS
            )
            
            path_value, _ = winreg.QueryValueEx(key, 'Path')
            
            if self.install_path not in path_value:
                if not path_value.endswith(';'):
                    new_path = path_value + ';' + self.install_path
                else:
                    new_path = path_value + self.install_path
                
                winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
                
                if ctypes:
                    HWND_BROADCAST = 0xFFFF
                    WM_SETTINGCHANGE = 0x1A
                    ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment')
            
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error agregando al PATH: {e}")
            return False
    
    def remove_from_path(self):
        """Remueve del PATH del sistema"""
        if not self.is_windows or winreg is None:
            return False
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
                0,
                winreg.KEY_ALL_ACCESS
            )
            
            path_value, _ = winreg.QueryValueEx(key, 'Path')
            paths = path_value.split(';')
            paths = [p for p in paths if p != self.install_path]
            new_path = ';'.join(paths)
            
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, new_path)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error removiendo del PATH: {e}")
            return False
    
    def install(self):
        """Instala Cronux-CRX (CLI + GUI)"""
        try:
            self.update_progress(0.1, "Creando directorios...")
            os.makedirs(self.install_path, exist_ok=True)
            cronux_dir = os.path.join(self.install_path, 'cronux')
            os.makedirs(cronux_dir, exist_ok=True)
            
            self.update_progress(0.3, "Copiando CLI...")
            
            if getattr(sys, 'frozen', False):
                cli_source = os.path.join(sys._MEIPASS, 'cli')
            else:
                cli_source = os.path.join(os.path.dirname(__file__), 'cli')
            
            if not os.path.exists(cli_source):
                raise Exception(f"No se encontró la carpeta cli en: {cli_source}")
            
            for file in os.listdir(cli_source):
                if file.endswith('.py'):
                    shutil.copy2(
                        os.path.join(cli_source, file),
                        os.path.join(cronux_dir, file)
                    )
            
            self.update_progress(0.5, "Copiando GUI...")
            
            # Copiar la GUI
            gui_source = os.path.join(os.path.dirname(__file__), '..', 'cronux_gui_v3.py')
            if os.path.exists(gui_source):
                shutil.copy2(gui_source, os.path.join(self.install_path, 'cronux_gui.py'))
            
            # Copiar assets
            assets_source = os.path.join(os.path.dirname(__file__), '..', 'assets')
            assets_dest = os.path.join(self.install_path, 'assets')
            if os.path.exists(assets_source):
                if os.path.exists(assets_dest):
                    shutil.rmtree(assets_dest)
                shutil.copytree(assets_source, assets_dest)
            
            self.update_progress(0.7, "Creando launchers...")
            
            # Launcher CLI
            launcher_cli = os.path.join(self.install_path, 'crx.bat')
            with open(launcher_cli, 'w') as f:
                f.write('@echo off\n')
                f.write(f'python "{cronux_dir}\\cronux_cli.py" %*\n')
            
            # Launcher GUI
            launcher_gui = os.path.join(self.install_path, 'cronux-gui.bat')
            with open(launcher_gui, 'w') as f:
                f.write('@echo off\n')
                f.write(f'python "{self.install_path}\\cronux_gui.py"\n')
            
            self.update_progress(0.9, "Agregando al PATH...")
            self.add_to_path()
            
            self.update_progress(1.0, "Instalación completa")
            
            self.show_success_dialog()
            
        except Exception as e:
            self.update_progress(0, f"Error: {str(e)}")
    
    def uninstall(self):
        """Desinstala Cronux-CRX"""
        try:
            self.update_progress(0.3, "Removiendo del PATH...")
            self.remove_from_path()
            
            self.update_progress(0.6, "Eliminando archivos...")
            if os.path.exists(self.install_path):
                shutil.rmtree(self.install_path)
            
            self.update_progress(1.0, "Desinstalación completa")
            
            self.show_uninstall_dialog()
            
        except Exception as e:
            self.update_progress(0, f"Error: {str(e)}")
    
    def show_success_dialog(self):
        """Muestra diálogo de instalación exitosa"""
        def close_dialog(e):
            dialog.open = False
            self.page.update()
            self.close_app()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=Colors.ACCENT_SUCCESS, size=28),
                ft.Container(width=12),
                ft.Text("Instalación Exitosa", size=20, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
            ]),
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("CLI instalado correctamente", size=14, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
                            ft.Container(height=8),
                            ft.Text("1. CIERRA esta ventana", size=13, color=Colors.TEXT_SECONDARY),
                            ft.Text("2. CIERRA tu terminal actual", size=13, color=Colors.TEXT_SECONDARY),
                            ft.Text("3. ABRE una NUEVA terminal", size=13, color=Colors.TEXT_SECONDARY),
                            ft.Text("4. Ejecuta: crx --help", size=13, color=Colors.TEXT_SECONDARY),
                            ft.Container(height=16),
                            ft.Text("GUI instalada", size=14, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
                            ft.Container(height=8),
                            ft.Text("• Ejecuta: cronux-gui.bat", size=13, color=Colors.TEXT_SECONDARY),
                            ft.Text(f"• Ubicación: {self.install_path}", size=11, color=Colors.TEXT_MUTED),
                            ft.Container(height=16),
                            ft.Text("Características v0.1.0 Beta:", size=13, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
                            ft.Text("• Control de versiones completo", size=12, color=Colors.TEXT_SECONDARY),
                            ft.Text("• Interfaz gráfica moderna", size=12, color=Colors.TEXT_SECONDARY),
                            ft.Text("• Comparación de versiones", size=12, color=Colors.TEXT_SECONDARY),
                            ft.Text("• Estadísticas de proyecto", size=12, color=Colors.TEXT_SECONDARY),
                        ], spacing=6),
                        bgcolor=Colors.SUCCESS_BG,
                        padding=20,
                        border_radius=12,
                    ),
                ], tight=True),
                width=500,
            ),
            actions=[
                ft.Container(
                    content=ft.Text("Entendido", color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.W_600),
                    bgcolor=Colors.ACCENT_SUCCESS,
                    padding=ft.Padding.symmetric(horizontal=32, vertical=12),
                    border_radius=20,
                    on_click=close_dialog,
                    ink=True,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def show_uninstall_dialog(self):
        """Muestra diálogo de desinstalación exitosa"""
        def close_dialog(e):
            dialog.open = False
            self.page.update()
            self.close_app()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE, color=Colors.ACCENT_WARNING, size=28),
                ft.Container(width=12),
                ft.Text("Desinstalación Exitosa", size=20, weight=ft.FontWeight.W_600, color=Colors.TEXT_PRIMARY),
            ]),
            content=ft.Container(
                content=ft.Text(
                    "Cronux-CRX ha sido eliminado\nde tu sistema correctamente",
                    size=14,
                    color=Colors.TEXT_SECONDARY,
                    text_align=ft.TextAlign.CENTER,
                ),
                padding=20,
            ),
            actions=[
                ft.Container(
                    content=ft.Text("Cerrar", color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.W_600),
                    bgcolor=Colors.ACCENT_PRIMARY,
                    padding=ft.Padding.symmetric(horizontal=32, vertical=12),
                    border_radius=20,
                    on_click=close_dialog,
                    ink=True,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()


def main(page: ft.Page):
    CronuxInstaller(page)


if __name__ == "__main__":
    ft.app(target=main)
