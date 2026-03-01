#!/bin/bash

# Script para firmar aplicación macOS
# Uso: ./sign_app.sh <app_path> [certificate_name]

set -e

APP_PATH="$1"
CERT_NAME="$2"

if [ -z "$APP_PATH" ]; then
    echo "Uso: $0 <app_path> [certificate_name]"
    echo ""
    echo "Ejemplos:"
    echo "  $0 dist/Cronux.app"
    echo "  $0 dist/Cronux.app 'Developer ID Application: Tu Nombre'"
    echo ""
    exit 1
fi

echo "🔐 Configurando firma de código..."

# Si no se especifica certificado, buscar automáticamente
if [ -z "$CERT_NAME" ]; then
    echo "🔍 Buscando certificados disponibles..."
    
    # Buscar certificados Developer ID
    AVAILABLE_CERTS=$(security find-identity -v -p codesigning | grep "Developer ID Application" | head -1)
    
    if [ -n "$AVAILABLE_CERTS" ]; then
        CERT_NAME=$(echo "$AVAILABLE_CERTS" | sed 's/.*) "//' | sed 's/".*//')
        echo "✅ Certificado encontrado: $CERT_NAME"
    else
        echo "⚠️  No se encontraron certificados Developer ID"
        echo ""
        echo "📋 Certificados disponibles:"
        security find-identity -v -p codesigning
        echo ""
        echo "💡 Para obtener un certificado Developer ID:"
        echo "   1. Únete al Apple Developer Program"
        echo "   2. Crea un certificado Developer ID Application"
        echo "   3. Descárgalo e instálalo en Keychain"
        echo ""
        echo "🔧 Alternativa - Firma ad-hoc (solo para pruebas locales):"
        echo "   Ejecuta: $0 $APP_PATH '-'"
        echo ""
        exit 1
    fi
fi

# Verificar que la app existe
if [ ! -d "$APP_PATH" ]; then
    echo "❌ Aplicación no encontrada: $APP_PATH"
    exit 1
fi

echo "📦 Aplicación: $APP_PATH"
echo "🔑 Certificado: $CERT_NAME"

# Función para firmar recursivamente
sign_recursively() {
    local path="$1"
    local cert="$2"
    
    # Firmar frameworks y librerías primero
    find "$path" -name "*.framework" -o -name "*.dylib" -o -name "*.so" | while read -r item; do
        if [ -f "$item" ] || [ -d "$item" ]; then
            echo "🔐 Firmando: $(basename "$item")"
            codesign --force --verify --verbose --sign "$cert" "$item" 2>/dev/null || true
        fi
    done
    
    # Firmar ejecutables
    find "$path" -type f -perm +111 | while read -r item; do
        if file "$item" | grep -q "Mach-O"; then
            echo "🔐 Firmando ejecutable: $(basename "$item")"
            codesign --force --verify --verbose --sign "$cert" "$item" 2>/dev/null || true
        fi
    done
}

# Crear entitlements si no existen
ENTITLEMENTS_FILE="entitlements.plist"
if [ ! -f "$ENTITLEMENTS_FILE" ]; then
    echo "📝 Creando entitlements..."
    cat > "$ENTITLEMENTS_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.app-sandbox</key>
    <false/>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.network.server</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
    <key>com.apple.security.files.downloads.read-write</key>
    <true/>
</dict>
</plist>
EOF
fi

echo "🔐 Iniciando proceso de firma..."

# Firmar componentes internos primero
echo "📦 Firmando componentes internos..."
sign_recursively "$APP_PATH/Contents" "$CERT_NAME"

# Firmar la aplicación principal
echo "🔐 Firmando aplicación principal..."
if [ "$CERT_NAME" = "-" ]; then
    # Firma ad-hoc
    codesign --force --deep --sign - "$APP_PATH"
    echo "✅ Aplicación firmada con firma ad-hoc"
else
    # Firma con certificado Developer ID
    codesign --force \
             --options runtime \
             --entitlements "$ENTITLEMENTS_FILE" \
             --sign "$CERT_NAME" \
             --deep \
             "$APP_PATH"
    echo "✅ Aplicación firmada con certificado Developer ID"
fi

# Verificar firma
echo "🔍 Verificando firma..."
codesign --verify --deep --strict --verbose=2 "$APP_PATH"

if [ $? -eq 0 ]; then
    echo "✅ Firma verificada correctamente"
    
    # Mostrar información de la firma
    echo ""
    echo "📋 Información de la firma:"
    codesign --display --verbose=4 "$APP_PATH"
    
    # Limpiar archivo temporal
    rm -f "$ENTITLEMENTS_FILE"
    
    echo ""
    echo "🎉 Aplicación firmada exitosamente!"
    echo ""
    echo "💡 Próximos pasos:"
    if [ "$CERT_NAME" != "-" ]; then
        echo "   1. Para distribución pública, considera notarizar la app"
        echo "   2. Comando de notarización:"
        echo "      xcrun notarytool submit app.zip --apple-id tu@email.com --team-id TEAM_ID --password app-password"
        echo "   3. Después de notarizar, grapa el ticket:"
        echo "      xcrun stapler staple '$APP_PATH'"
    else
        echo "   1. Esta firma ad-hoc solo funciona en tu Mac"
        echo "   2. Para distribución, necesitas un certificado Developer ID"
    fi
    
else
    echo "❌ Error en la verificación de firma"
    exit 1
fi