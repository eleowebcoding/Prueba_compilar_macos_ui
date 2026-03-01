# Cronux GUI v3 - macOS Build Test

Sistema de control de versiones local con interfaz gráfica moderna construida con Flet.

## 🎯 Objetivo

Probar la compilación de aplicación Flet para macOS usando GitHub Actions con Flutter/Dart para evitar el problema del doble icono.

## 📦 Contenido

- `cronux_gui_v3.py` - Aplicación principal
- `cli/` - Módulos CLI del sistema
- `assets/` - Recursos (iconos, imágenes)
- `.github/workflows/` - GitHub Actions para compilación automática

## 🚀 Compilación Automática

La aplicación se compila automáticamente en GitHub Actions usando:
- macOS 14+ (latest)
- Flutter SDK
- `flet build macos`

## 📱 Características

- ✅ Interfaz moderna con Flet
- ✅ Sistema de control de versiones local
- ✅ Soporte para múltiples tipos de proyecto
- ✅ Tema claro/oscuro
- ✅ Icono personalizado
- ✅ Compilación nativa para macOS

## 🔧 Desarrollo Local

```bash
# Instalar dependencias
pip install flet

# Ejecutar en desarrollo
python cronux_gui_v3.py

# Compilar localmente (requiere macOS 14+)
flet build macos --product "Cronux" --build-version 3.0.0
```

## 📥 Descargar

Los builds compilados están disponibles en [Releases](../../releases).

---

Compilado con ❤️ usando Flet y GitHub Actions