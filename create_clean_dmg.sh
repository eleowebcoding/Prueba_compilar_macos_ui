#!/bin/bash

# Script para crear DMG limpio y bien centrado
set -e

echo "🎨 Creando DMG limpio y centrado..."

# Configuración
VOLUME_NAME="Cronux"
DMG_NAME="Cronux-Normal"
DMG_TEMP="${DMG_NAME}_temp.dmg"
DMG_FINAL="${DMG_NAME}.dmg"

# Limpiar archivos anteriores
rm -f "$DMG_TEMP" "$DMG_FINAL"

# Crear directorio temporal
DMG_DIR="dmg_staging"
rm -rf "$DMG_DIR"
mkdir -p "$DMG_DIR"

# Crear app de prueba si no existe
if [ ! -d "TestApp.app" ]; then
    echo "📦 Creando app Cronux de prueba..."
    mkdir -p "TestApp.app/Contents/MacOS"
    cat > "TestApp.app/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Cronux</string>
    <key>CFBundleIdentifier</key>
    <string>com.cronux.app</string>
    <key>CFBundleName</key>
    <string>Cronux</string>
    <key>CFBundleDisplayName</key>
    <string>Cronux</string>
    <key>CFBundleVersion</key>
    <string>3.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>3.0.0</string>
</dict>
</plist>
EOF
    echo '#!/bin/bash\necho "Cronux - Sistema de Control de Versiones"' > "TestApp.app/Contents/MacOS/Cronux"
    chmod +x "TestApp.app/Contents/MacOS/Cronux"
fi

# Copiar contenido
echo "📦 Preparando contenido del DMG..."
cp -R "TestApp.app" "$DMG_DIR/Cronux.app"
ln -s /Applications "$DMG_DIR/Applications"

# Crear DMG temporal
echo "💿 Creando DMG temporal..."
hdiutil create -volname "$VOLUME_NAME" -srcfolder "$DMG_DIR" -ov -format UDRW "$DMG_TEMP"

# Montar DMG
echo "📂 Montando DMG para configuración..."
MOUNT_OUTPUT=$(hdiutil attach -readwrite -noverify -noautoopen "$DMG_TEMP" 2>&1)
MOUNT_DIR=$(echo "$MOUNT_OUTPUT" | grep -E '/Volumes/' | awk '{print $3}' | head -1)

if [ -n "$MOUNT_DIR" ]; then
    echo "✅ DMG montado en: $MOUNT_DIR"
    
    # Configurar vista normal de macOS
    echo "🎨 Configurando layout normal..."
    osascript << EOF
    tell application "Finder"
        tell disk "$VOLUME_NAME"
            open
            delay 2
            
            -- Configurar vista básica normal
            set current view of container window to icon view
            set toolbar visible of container window to false
            set statusbar visible of container window to false
            
            -- Tamaño de ventana
            set the bounds of container window to {200, 200, 700, 450}
            
            -- Configurar iconos con diseño normal
            set viewOptions to the icon view options of container window
            set arrangement of viewOptions to not arranged
            set icon size of viewOptions to 128
            set text size of viewOptions to 12
            
            -- Sin fondo personalizado (usar el por defecto de macOS)
            
            delay 2
            close
        end tell
    end tell
EOF
    
    echo "✅ Layout normal configurado"
    
    # Esperar antes de desmontar
    sleep 3
    
    # Desmontar con reintentos
    echo "📤 Desmontando DMG..."
    for i in {1..3}; do
        if hdiutil detach "$MOUNT_DIR" 2>/dev/null; then
            echo "✅ DMG desmontado"
            break
        else
            echo "⚠️ Reintento $i/3..."
            sleep 2
            if [ $i -eq 3 ]; then
                hdiutil detach "$MOUNT_DIR" -force
            fi
        fi
    done
    
else
    echo "❌ No se pudo montar el DMG"
    exit 1
fi

# Esperar más tiempo antes de convertir
sleep 5

# Crear DMG final
echo "🗜️ Creando DMG final comprimido..."
hdiutil convert "$DMG_TEMP" -format UDZO -imagekey zlib-level=9 -o "$DMG_FINAL"

# Limpiar
rm -f "$DMG_TEMP"
rm -rf "$DMG_DIR"

echo "✅ DMG limpio creado: $DMG_FINAL"
echo "📊 Tamaño: $(du -sh "$DMG_FINAL" | cut -f1)"

# Abrir para verificar
echo "🔍 Abriendo DMG para verificar..."
open "$DMG_FINAL"