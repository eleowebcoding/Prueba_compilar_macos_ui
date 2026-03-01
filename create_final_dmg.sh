#!/bin/bash

# Script final para crear DMG con fondo
set -e

echo "🎨 Creando DMG final con tu fondo personalizado..."

# Configuración
DMG_BACKGROUND="fondo_dmg.png"
VOLUME_NAME="Cronux"
DMG_NAME="Cronux-Final"
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
    echo "📦 Creando app de prueba..."
    mkdir -p "TestApp.app/Contents/MacOS"
    cat > "TestApp.app/Contents/Info.plist" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>TestApp</string>
    <key>CFBundleIdentifier</key>
    <string>com.cronux.test</string>
    <key>CFBundleName</key>
    <string>Cronux</string>
    <key>CFBundleVersion</key>
    <string>3.0.0</string>
</dict>
</plist>
EOF
    echo '#!/bin/bash\necho "Cronux Test App"' > "TestApp.app/Contents/MacOS/TestApp"
    chmod +x "TestApp.app/Contents/MacOS/TestApp"
fi

# Copiar contenido
echo "📦 Preparando contenido del DMG..."
cp -R "TestApp.app" "$DMG_DIR/"
ln -s /Applications "$DMG_DIR/Applications"

# Copiar fondo
mkdir -p "$DMG_DIR/.background"
cp "$DMG_BACKGROUND" "$DMG_DIR/.background/background.png"
echo "✅ Fondo agregado: $(ls -la "$DMG_DIR/.background/")"

# Crear DMG temporal
echo "💿 Creando DMG temporal..."
hdiutil create -volname "$VOLUME_NAME" -srcfolder "$DMG_DIR" -ov -format UDRW "$DMG_TEMP"

# Montar DMG
echo "📂 Montando DMG..."
MOUNT_OUTPUT=$(hdiutil attach -readwrite -noverify -noautoopen "$DMG_TEMP" 2>&1)
MOUNT_DIR=$(echo "$MOUNT_OUTPUT" | grep -E '/Volumes/' | awk '{print $3}' | head -1)

if [ -n "$MOUNT_DIR" ]; then
    echo "✅ DMG montado en: $MOUNT_DIR"
    
    # Verificar que el fondo esté ahí
    if [ -f "$MOUNT_DIR/.background/background.png" ]; then
        echo "✅ Fondo encontrado en DMG"
        
        # Configurar usando método manual
        echo "🎨 Configurando DMG manualmente..."
        
        # Abrir Finder en el volumen
        open "$MOUNT_DIR"
        
        echo "📋 Instrucciones manuales:"
        echo "1. Se abrió el DMG en Finder"
        echo "2. Ve a Ver > Mostrar opciones de visualización"
        echo "3. Selecciona 'Imagen' en Fondo"
        echo "4. Arrastra el archivo background.png desde .background/"
        echo "5. Ajusta el tamaño de iconos a 96"
        echo "6. Posiciona los iconos como quieras"
        echo ""
        echo "Presiona ENTER cuando hayas terminado de configurar..."
        read -r
        
        # Cerrar Finder
        osascript -e 'tell application "Finder" to close every window'
        
    else
        echo "❌ Fondo no encontrado en DMG"
    fi
    
    # Desmontar con reintentos
    echo "📤 Desmontando DMG..."
    for i in {1..5}; do
        if hdiutil detach "$MOUNT_DIR" 2>/dev/null; then
            echo "✅ DMG desmontado"
            break
        else
            echo "⚠️ Reintento $i/5..."
            sleep 2
            if [ $i -eq 5 ]; then
                echo "🔧 Forzando desmontaje..."
                hdiutil detach "$MOUNT_DIR" -force
            fi
        fi
    done
    
else
    echo "❌ No se pudo montar el DMG"
    exit 1
fi

# Esperar un momento antes de convertir
sleep 3

# Crear DMG final
echo "🗜️ Creando DMG final comprimido..."
hdiutil convert "$DMG_TEMP" -format UDZO -imagekey zlib-level=9 -o "$DMG_FINAL"

# Limpiar
rm -f "$DMG_TEMP"
rm -rf "$DMG_DIR"

echo "✅ DMG creado: $DMG_FINAL"
echo "📊 Tamaño: $(du -sh "$DMG_FINAL" | cut -f1)"

# Abrir el DMG final para verificar
echo "🔍 Abriendo DMG final..."
open "$DMG_FINAL"