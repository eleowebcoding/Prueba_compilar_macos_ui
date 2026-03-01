# 🚀 Guía: Compilar Cronux con GitHub Actions

## 📋 Resumen

Esta guía te ayudará a usar GitHub Actions para compilar tu aplicación Cronux en macOS 14+ usando Flutter/Flet, solucionando completamente el problema del doble icono.

## 🎯 Ventajas de GitHub Actions

✅ **macOS 14+ nativo** - Sin limitaciones de versión  
✅ **Flutter actualizado** - Última versión estable  
✅ **flet build macos** - Compilación oficial de Flet  
✅ **Sin doble icono** - Problema completamente resuelto  
✅ **Compilación automática** - En cada push o manualmente  
✅ **Distribución fácil** - DMG listo para descargar  

## 📁 Archivos Creados

### Workflows de GitHub Actions:
- `.github/workflows/build-macos.yml` - Compilación automática
- `.github/workflows/release.yml` - Creación de releases

### Configuración:
- `pyproject.toml` - Configuración de Flet
- `.gitignore` - Archivos a ignorar
- `README.md` - Documentación del proyecto

### Scripts de ayuda:
- `prepare_repo.sh` - Preparar repositorio

## 🚀 Pasos para Usar

### 1. Subir a GitHub

```bash
# Inicializar repositorio
git init

# Agregar archivos
git add .

# Commit inicial
git commit -m "Initial commit: Cronux GUI v3 for macOS"

# Configurar rama principal
git branch -M main

# Agregar remote (usa tu URL)
git remote add origin https://github.com/eleowebcoding/Prueba_compilar_macos_ui.git

# Push inicial
git push -u origin main
```

### 2. Compilación Automática

Después del push:

1. **Ve a tu repositorio en GitHub**
2. **Haz clic en "Actions"**
3. **Verás el workflow "Build macOS App" ejecutándose**
4. **Espera ~10-15 minutos** para que termine

### 3. Descargar la App

Una vez terminado el workflow:

1. **Haz clic en el workflow completado**
2. **Scroll down hasta "Artifacts"**
3. **Descarga el DMG** (ej: `Cronux-macOS-v3.0.0-build123`)
4. **Descomprime el ZIP** descargado
5. **Abre el DMG** y arrastra la app a Applications

## 🎯 Crear Releases

### Opción A: Release Manual

1. Ve a **Actions** en GitHub
2. Selecciona **"Create Release"**
3. Haz clic en **"Run workflow"**
4. Ingresa la versión (ej: `v3.0.0`)
5. Haz clic en **"Run workflow"**

### Opción B: Release con Tag

```bash
# Crear tag localmente
git tag v3.0.0

# Push del tag
git push origin v3.0.0
```

Esto creará automáticamente un release con el DMG.

## 📦 Resultado Esperado

Después de la compilación tendrás:

### Artifacts (siempre):
- `Cronux-macOS-v3.0.0-buildXXX.dmg` - DMG instalable
- `Cronux-App-Bundle-v3.0.0-buildXXX` - Bundle de la app

### Release (si usas tags):
- Release público con DMG
- Notas de versión automáticas
- Descarga directa para usuarios

## ✨ Características del DMG Compilado

✅ **Icono único** - Sin problema de doble icono  
✅ **Nativo de macOS** - Compilado con Flutter  
✅ **Universal Binary** - Intel + Apple Silicon  
✅ **Firmado automáticamente** - Por GitHub Actions  
✅ **Optimizado** - Tamaño reducido  
✅ **Compatible** - macOS 10.15+  

## 🔧 Personalización

### Cambiar información de la app:

Edita `pyproject.toml`:

```toml
[project]
name = "tu-app"
version = "1.0.0"
description = "Tu descripción"

[tool.flet.macos.info]
CFBundleName = "Tu App"
CFBundleDisplayName = "Tu App"
```

### Cambiar configuración de build:

Edita `.github/workflows/build-macos.yml`:

```yaml
- name: Build macOS app
  run: |
    flet build macos \
      --product "Tu App" \
      --project tu-app \
      --build-version 1.0.0 \
      # ... más opciones
```

## 🐛 Solución de Problemas

### Error: "Module not found"
- Verifica que todos los archivos estén en el repositorio
- Revisa que `cli/` y `assets/` estén incluidos

### Error: "Build failed"
- Revisa los logs en GitHub Actions
- Verifica que `cronux_gui_v3.py` sea válido
- Asegúrate de que las dependencias estén correctas

### DMG no se abre
- Descarga de nuevo desde Artifacts
- Verifica que descomprimiste el ZIP primero

## 📊 Comparación: Local vs GitHub Actions

| Aspecto | Local (macOS 12) | GitHub Actions |
|---------|------------------|----------------|
| **Doble icono** | ❌ Problema | ✅ Solucionado |
| **Flutter** | ❌ No compatible | ✅ Última versión |
| **flet build** | ❌ No funciona | ✅ Funciona perfecto |
| **Tiempo** | ⚡ Inmediato | 🕐 10-15 min |
| **Costo** | 💰 Gratis | 💰 Gratis |
| **Distribución** | 📤 Manual | 📦 Automática |

## 🎉 Resultado Final

Con GitHub Actions obtienes:

1. **App nativa de macOS** sin doble icono
2. **DMG profesional** listo para distribuir
3. **Proceso automatizado** en cada cambio
4. **Releases públicos** para tus usuarios
5. **Compatibilidad total** con macOS moderno

---

## 📞 Comandos Rápidos

```bash
# Setup inicial
git init && git add . && git commit -m "Initial commit"
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main

# Crear release
git tag v3.0.0 && git push origin v3.0.0
```

¡Tu app estará compilada sin el problema del doble icono! 🚀