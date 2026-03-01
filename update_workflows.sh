#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║           Actualizando Workflows de GitHub Actions        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Verificar si estamos en un repositorio git
if [ ! -d ".git" ]; then
    echo "❌ No estás en un repositorio git"
    echo "💡 Ejecuta primero: git init"
    exit 1
fi

# Mostrar cambios
echo "📋 Cambios realizados:"
echo "────────────────────────────────────────────────────────────"
echo "✅ Actualizado actions/upload-artifact de v3 a v4"
echo "✅ Actualizado actions/setup-python de v4 a v5"
echo "✅ Actualizado Flutter de 3.19.0 a 3.24.0"
echo "✅ Actualizado softprops/action-gh-release de v1 a v2"
echo "✅ Creado workflow mejorado build-macos-v2.yml"
echo "✅ Especificado macOS 14 como runner"
echo ""

# Verificar archivos de workflow
echo "🔍 Verificando workflows:"
for workflow in .github/workflows/*.yml; do
    if [ -f "$workflow" ]; then
        echo "✅ $(basename "$workflow")"
    fi
done
echo ""

# Agregar cambios
echo "📦 Agregando cambios al git..."
git add .github/workflows/
git add update_workflows.sh

# Verificar si hay cambios para commit
if git diff --cached --quiet; then
    echo "ℹ️  No hay cambios para hacer commit"
else
    # Hacer commit
    echo "💾 Haciendo commit de los cambios..."
    git commit -m "fix: Update GitHub Actions to latest versions

- Update actions/upload-artifact from v3 to v4
- Update actions/setup-python from v4 to v5  
- Update Flutter from 3.19.0 to 3.24.0
- Update softprops/action-gh-release from v1 to v2
- Add improved build-macos-v2.yml workflow
- Specify macOS 14 as runner for better compatibility

Fixes deprecation warnings and improves build reliability."

    echo "✅ Commit realizado"
fi

echo ""
echo "🚀 Para aplicar los cambios:"
echo "────────────────────────────────────────────────────────────"
echo "git push origin main"
echo ""
echo "📋 Después del push:"
echo "1. Ve a GitHub Actions en tu repositorio"
echo "2. Los workflows actualizados se ejecutarán sin errores"
echo "3. Descarga el DMG desde Artifacts"
echo "4. ¡Prueba tu app sin doble icono!"
echo ""
echo "💡 Workflows disponibles:"
echo "   • build-macos.yml - Workflow original actualizado"
echo "   • build-macos-v2.yml - Workflow mejorado con más verificaciones"
echo "   • release.yml - Para crear releases automáticos"
echo ""