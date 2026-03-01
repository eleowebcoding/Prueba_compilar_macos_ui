#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║           Preparando Repositorio para GitHub              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Crear .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# macOS
.DS_Store
.AppleDouble
.LSOverride
Icon?
._*
.DocumentRevisions-V100
.fseventsd
.Spotlight-V100
.TemporaryItems
.Trashes
.VolumeIcon.icns
.com.apple.timemachine.donotpresent

# Flet
.flet/

# Build artifacts
*.dmg
*.app
dmg_temp/
*_temp.dmg

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log

# Temporary files
*.tmp
*.temp
EOF

echo "✅ .gitignore creado"

# Verificar archivos necesarios
echo ""
echo "🔍 Verificando archivos necesarios..."

required_files=(
    "cronux_gui_v3.py"
    "cli/funcion_verficar.py"
    "assets/cronux_cli.icns"
    "assets/cronux_cli.png"
)

missing_files=()

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (FALTANTE)"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  Archivos faltantes detectados:"
    for file in "${missing_files[@]}"; do
        echo "   • $file"
    done
    echo ""
    echo "💡 Asegúrate de que estos archivos existan antes de hacer push"
fi

# Mostrar estructura del repositorio
echo ""
echo "📁 Estructura del repositorio:"
echo "────────────────────────────────────────────────────────────"
find . -type f -not -path "./.git/*" -not -name ".*" | head -20 | sort

echo ""
echo "🚀 Comandos para subir a GitHub:"
echo "────────────────────────────────────────────────────────────"
echo "git init"
echo "git add ."
echo "git commit -m 'Initial commit: Cronux GUI v3 for macOS'"
echo "git branch -M main"
echo "git remote add origin https://github.com/eleowebcoding/Prueba_compilar_macos_ui.git"
echo "git push -u origin main"
echo ""
echo "📋 Después del push:"
echo "1. Ve a GitHub Actions en tu repositorio"
echo "2. El workflow se ejecutará automáticamente"
echo "3. Descarga el DMG desde Artifacts"
echo "4. ¡Prueba tu app sin doble icono!"
echo ""