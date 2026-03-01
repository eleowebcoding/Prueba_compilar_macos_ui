# 🔐 Guía de Firma de Código para macOS

## 📋 ¿Por qué Firmar tu App?

Sin firma de código, macOS mostrará advertencias como:
- ⚠️ "No se puede abrir porque proviene de un desarrollador no identificado"
- ⚠️ "macOS no puede verificar que esta app esté libre de malware"
- ⚠️ La app puede ser bloqueada por Gatekeeper

## 🎯 Tipos de Firma

### 1. **Firma Ad-hoc** (Gratis - Solo para pruebas)
```bash
./sign_app.sh dist/Cronux.app -
```
- ✅ Gratis
- ✅ Funciona en tu Mac
- ❌ No funciona en otras Macs
- ❌ Sigue mostrando advertencias

### 2. **Developer ID Application** (Recomendado - $99/año)
```bash
./sign_app.sh dist/Cronux.app "Developer ID Application: Tu Nombre"
```
- ✅ Funciona en cualquier Mac
- ✅ Reduce advertencias de seguridad
- ✅ Permite distribución fuera de App Store
- 💰 Requiere Apple Developer Program ($99/año)

### 3. **Notarización** (Máxima Compatibilidad)
- ✅ Sin advertencias de seguridad
- ✅ Máxima confianza del usuario
- ✅ Distribución profesional
- 💰 Requiere Developer ID + proceso adicional

## 🚀 Configuración Paso a Paso

### Paso 1: Obtener Certificado Developer ID

1. **Únete al Apple Developer Program**
   - Ve a [developer.apple.com](https://developer.apple.com)
   - Paga $99/año por la membresía

2. **Crear Certificado**
   - Ve a Certificates, Identifiers & Profiles
   - Crea un "Developer ID Application" certificate
   - Descarga e instala en Keychain

3. **Verificar Instalación**
   ```bash
   security find-identity -v -p codesigning
   ```

### Paso 2: Firmar tu App

```bash
# Automático (busca certificado)
./sign_app.sh dist/Cronux.app

# Manual (especifica certificado)
./sign_app.sh dist/Cronux.app "Developer ID Application: Tu Nombre (TEAM_ID)"
```

### Paso 3: Crear DMG Firmado

```bash
# Crear DMG personalizado
./create_custom_dmg.sh dist/Cronux.app Cronux-v3.0.0 3.0.0

# Firmar el DMG también
codesign --sign "Developer ID Application: Tu Nombre" Cronux-v3.0.0.dmg
```

## 🔒 Notarización (Opcional pero Recomendado)

### Paso 1: Preparar para Notarización
```bash
# Crear ZIP de la app
ditto -c -k --keepParent dist/Cronux.app Cronux.zip
```

### Paso 2: Subir para Notarización
```bash
xcrun notarytool submit Cronux.zip \
  --apple-id tu@email.com \
  --team-id TEAM_ID \
  --password "app-specific-password" \
  --wait
```

### Paso 3: Grapar el Ticket
```bash
xcrun stapler staple dist/Cronux.app
xcrun stapler staple Cronux-v3.0.0.dmg
```

## 🛠️ Configuración en GitHub Actions

Para firmar automáticamente en GitHub Actions, necesitas:

### 1. Agregar Secretos al Repositorio

Ve a Settings → Secrets and variables → Actions:

```
APPLE_CERTIFICATE_BASE64: [certificado en base64]
APPLE_CERTIFICATE_PASSWORD: [contraseña del certificado]
APPLE_ID: [tu Apple ID]
APPLE_TEAM_ID: [tu Team ID]
APPLE_APP_PASSWORD: [contraseña específica de app]
```

### 2. Actualizar Workflow

```yaml
- name: Import Code Signing Certificate
  run: |
    echo "${{ secrets.APPLE_CERTIFICATE_BASE64 }}" | base64 --decode > certificate.p12
    security create-keychain -p "" build.keychain
    security import certificate.p12 -k build.keychain -P "${{ secrets.APPLE_CERTIFICATE_PASSWORD }}" -T /usr/bin/codesign
    security set-keychain-settings build.keychain
    security unlock-keychain -p "" build.keychain

- name: Sign App
  run: |
    codesign --force --options runtime --sign "Developer ID Application" dist/Cronux.app

- name: Notarize App
  run: |
    ditto -c -k --keepParent dist/Cronux.app Cronux.zip
    xcrun notarytool submit Cronux.zip --apple-id "${{ secrets.APPLE_ID }}" --team-id "${{ secrets.APPLE_TEAM_ID }}" --password "${{ secrets.APPLE_APP_PASSWORD }}" --wait
    xcrun stapler staple dist/Cronux.app
```

## 💡 Alternativas Gratuitas

### 1. Firma Ad-hoc + Instrucciones para Usuarios
```bash
./sign_app.sh dist/Cronux.app -
```

Incluye estas instrucciones para usuarios:
1. Descarga la app
2. Ve a Preferencias del Sistema → Seguridad y Privacidad
3. Haz clic en "Abrir de todas formas"

### 2. Distribución via Homebrew
```bash
# Los usuarios pueden instalar via Homebrew Cask
brew install --cask cronux
```

### 3. Instrucciones de Bypass Manual
```bash
# Los usuarios pueden ejecutar:
sudo xattr -rd com.apple.quarantine /Applications/Cronux.app
```

## 📊 Comparación de Opciones

| Método | Costo | Advertencias | Distribución | Confianza |
|--------|-------|--------------|--------------|-----------|
| Sin firma | Gratis | ❌ Muchas | ❌ Limitada | ❌ Baja |
| Ad-hoc | Gratis | ⚠️ Algunas | ❌ Solo tu Mac | ⚠️ Media |
| Developer ID | $99/año | ⚠️ Pocas | ✅ Cualquier Mac | ✅ Alta |
| Notarizado | $99/año | ✅ Ninguna | ✅ Profesional | ✅ Máxima |

## 🎯 Recomendación

### Para Desarrollo Personal:
- Usa firma ad-hoc: `./sign_app.sh dist/Cronux.app -`

### Para Distribución Pública:
1. Invierte en Apple Developer Program ($99/año)
2. Firma con Developer ID
3. Considera notarización para máxima confianza

### Para Proyectos Open Source:
- Documenta el proceso de firma
- Proporciona instrucciones claras para usuarios
- Considera usar GitHub Releases con advertencias claras

---

## 📞 Comandos Rápidos

```bash
# Verificar certificados disponibles
security find-identity -v -p codesigning

# Firmar app (automático)
./sign_app.sh dist/Cronux.app

# Crear DMG personalizado
./create_custom_dmg.sh dist/Cronux.app Cronux-v3.0.0 3.0.0

# Verificar firma
codesign --verify --deep --strict --verbose=2 dist/Cronux.app
```

¡Tu app estará lista para distribución profesional! 🚀