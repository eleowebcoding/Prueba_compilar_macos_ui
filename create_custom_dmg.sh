#!/bin/bash

# Script para crear DMG personalizado con diseño profesional
# Uso: ./create_custom_dmg.sh <app_path> <dmg_name> <version>

set -e

APP_PATH="$1"
DMG_NAME="$2"
VERSION="$3"

if [ -z "$APP_PATH" ] || [ -z "$DMG_NAME" ] || [ -z "$VERSION" ]; then
    echo "Uso: $0 <app_path> <dmg_name> <version>"
    exit 1
fi

echo "🎨 Creando DMG personalizado..."

# Configuración
VOLUME_NAME="Cronux"
DMG_BACKGROUND="dmg_background.png"
DMG_TEMP="${DMG_NAME}_temp.dmg"
DMG_FINAL="${DMG_NAME}.dmg"

# Crear directorio temporal para el DMG
DMG_DIR="dmg_staging"
rm -rf "$DMG_DIR"
mkdir -p "$DMG_DIR"

# Copiar la aplicación
echo "📦 Copiando aplicación..."
cp -R "$APP_PATH" "$DMG_DIR/"

# Crear enlace a Applications
echo "🔗 Creando enlace a Applications..."
ln -s /Applications "$DMG_DIR/Applications"

# Crear imagen de fondo personalizada si no existe
if [ ! -f "$DMG_BACKGROUND" ]; then
    echo "🎨 Creando imagen de fondo personalizada..."
    
    # Crear imagen de fondo con ImageMagick (si está disponible) o usar la existente
    if command -v convert &> /dev/null; then
        # Crear gradiente personalizado
        convert -size 600x400 gradient:#f0f0f0-#e0e0e0 \
                -font Arial-Bold -pointsize 24 -fill '#333333' \
                -gravity North -annotate +0+50 "Cronux v${VERSION}" \
                -font Arial -pointsize 14 -fill '#666666' \
                -gravity North -annotate +0+80 "Sistema de Control de Versiones Local" \
                -font Arial -pointsize 12 -fill '#999999' \
                -gravity South -annotate +0+30 "Arrastra Cronux.app a Applications para instalar" \
                "$DMG_BACKGROUND"
    elif [ -f "assets/dmgimagen.png" ]; then
        cp "assets/dmgimagen.png" "$DMG_BACKGROUND"
    else
        # Crear imagen simple con sips (disponible en macOS)
        sips -s format png --out "$DMG_BACKGROUND" /System/Library/CoreServices/CoreTypes.bundle/Contents/Resources/GenericDocumentIcon.icns 2>/dev/null || true
    fi
fi

# Copiar imagen de fondo al DMG
if [ -f "$DMG_BACKGROUND" ]; then
    mkdir -p "$DMG_DIR/.background"
    cp "$DMG_BACKGROUND" "$DMG_DIR/.background/background.png"
    echo "✅ Imagen de fondo agregada"
fi

# Crear archivo DS_Store personalizado para el layout
echo "📐 Configurando layout del DMG..."
cat > "$DMG_DIR/.DS_Store_template" << 'EOF'
# Este archivo será procesado por AppleScript
EOF

# Eliminar DMG anterior si existe
rm -f "$DMG_TEMP" "$DMG_FINAL"

# Crear DMG temporal
echo "💿 Creando DMG temporal..."
hdiutil create -volname "$VOLUME_NAME" \
               -srcfolder "$DMG_DIR" \
               -ov \
               -format UDRW \
               "$DMG_TEMP"

# Montar DMG para personalización
echo "📂 Montando DMG para personalización..."
MOUNT_DIR=$(hdiutil attach -readwrite -noverify -noautoopen "$DMG_TEMP" | grep -E '^/dev/' | sed 1q | awk '{print $3}')

if [ -z "$MOUNT_DIR" ]; then
    echo "❌ Error al montar DMG"
    exit 1
fi

echo "✅ DMG montado en: $MOUNT_DIR"

# Esperar a que el volumen esté listo
sleep 2

# Personalizar con AppleScript
echo "🎨 Aplicando diseño personalizado..."
osascript << EOF
tell application "Finder"
    tell disk "$VOLUME_NAME"
        open
        
        -- Configurar vista
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {100, 100, 740, 580}
        
        -- Configurar opciones de vista de iconos
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 128
        set background picture of viewOptions to file ".background:background.png"
        
        -- Posicionar iconos
        set position of item "Cronux.app" of container window to {180, 280}
        set position of item "Applications" of container window to {460, 280}
        
        -- Configurar ventana
        set the bounds of container window to {100, 100, 740, 580}
        
        -- Actualizar vista
        update without registering applications
        delay 2
        
        -- Cerrar y reabrir para aplicar cambios
        close
        open
        
        delay 2
    end tell
end tell
EOF

echo "✅ Diseño aplicado"

# Crear archivo .fseventsd para evitar indexación
touch "$MOUNT_DIR/.fseventsd/no_log"

# Desmontar DMG
echo "📤 Desmontando DMG..."
hdiutil detach "$MOUNT_DIR"

# Convertir a DMG comprimido final
echo "🗜️ Comprimiendo DMG final..."
hdiutil convert "$DMG_TEMP" \
                -format UDZO \
                -imagekey zlib-level=9 \
                -o "$DMG_FINAL"

# Limpiar archivos temporales
rm -f "$DMG_TEMP"
rm -rf "$DMG_DIR"
rm -f "$DMG_BACKGROUND"

# Verificar resultado
if [ -f "$DMG_FINAL" ]; then
    echo "✅ DMG creado exitosamente: $DMG_FINAL"
    echo "📊 Tamaño: $(du -sh "$DMG_FINAL" | cut -f1)"
else
    echo "❌ Error al crear DMG final"
    exit 1
fi