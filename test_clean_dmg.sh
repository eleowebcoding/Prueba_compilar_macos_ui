#!/bin/bash

# Script simple para probar DMG con fondo limpio
set -e

echo "🎨 Creando DMG con fondo limpio..."

# Usar la imagen limpia que ya creamos
DMG_BACKGROUND="fondo_dmg.png"
VOLUME_NAME="Cronux"
DMG_NAME="Cronux-Clean-Test"
DMG_TEMP="${DMG_NAME}_temp.dmg"
DMG_FINAL="${DMG_NAME}.dmg"

# Crear directorio temporal
DMG_DIR="dmg_staging"
rm -rf "$DMG_DIR"
mkdir -p "$DMG_DIR"

# Copiar contenido
echo "📦 Preparando contenido..."
cp -R TestApp.app "$DMG_DIR/" 2>/dev/null || {
    echo "Creando app de prueba..."
    mkdir -p "$DMG_DIR/TestApp.app/Contents/MacOS"
    echo '#!/bin/bash\necho "Test"' > "$DMG_DIR/TestApp.app/Contents/MacOS/TestApp"
    chmod +x "$DMG_DIR/TestApp.app/Contents/MacOS/TestApp"
}

ln -s /Applications "$DMG_DIR/Applications"

# Copiar imagen de fondo limpia
mkdir -p "$DMG_DIR/.background"
cp "$DMG_BACKGROUND" "$DMG_DIR/.background/background.png"
echo "✅ Fondo limpio agregado"

# Crear DMG temporal
echo "💿 Creando DMG..."
hdiutil create -volname "$VOLUME_NAME" -srcfolder "$DMG_DIR" -ov -format UDRW "$DMG_TEMP"

# Montar y configurar
echo "📂 Montando para configuración..."
MOUNT_DIR=$(hdiutil attach -readwrite -noverify -noautoopen "$DMG_TEMP" | grep -E '/Volumes/' | awk '{print $3}')

if [ -n "$MOUNT_DIR" ]; then
    echo "✅ Montado en: $MOUNT_DIR"
    
    # Configurar vista con fondo
    osascript << EOF
    tell application "Finder"
        tell disk "$VOLUME_NAME"
            open
            delay 2
            set current view of container window to icon view
            set toolbar visible of container window to false
            set statusbar visible of container window to false
            set the bounds of container window to {100, 100, 800, 600}
            
            set viewOptions to the icon view options of container window
            set arrangement of viewOptions to not arranged
            set icon size of viewOptions to 96
            
            -- Configurar el fondo
            try
                set background picture of viewOptions to file ".background:background.png"
                delay 1
            on error
                -- Método alternativo
                try
                    set background picture of viewOptions to POSIX file "$MOUNT_DIR/.background/background.png"
                on error
                    log "No se pudo establecer fondo"
                end try
            end try
            
            delay 2
            
            -- Posicionar iconos
            repeat with anItem in (every item of container window)
                if name of anItem ends with ".app" then
                    set position of anItem to {200, 280}
                    exit repeat
                end if
            end repeat
            
            try
                set position of item "Applications" of container window to {500, 280}
            end try
            
            update without registering applications
            delay 2
            close
        end tell
    end tell
EOF
    
    echo "✅ Layout configurado"
    
    # Esperar antes de desmontar
    sleep 3
    
    # Desmontar
    hdiutil detach "$MOUNT_DIR" || {
        echo "Reintentando desmontaje..."
        sleep 2
        hdiutil detach "$MOUNT_DIR" -force
    }
fi

# Crear DMG final
echo "🗜️ Comprimiendo..."
hdiutil convert "$DMG_TEMP" -format UDZO -imagekey zlib-level=9 -o "$DMG_FINAL"

# Limpiar
rm -f "$DMG_TEMP"
rm -rf "$DMG_DIR"

echo "✅ DMG creado: $DMG_FINAL"
echo "📊 Tamaño: $(du -sh "$DMG_FINAL" | cut -f1)"

# Abrir para probar
echo "🔍 Abriendo DMG para probar..."
open "$DMG_FINAL"