#!/usr/bin/env python3
"""
Generador de imagen de fondo para DMG de Cronux
Crea una imagen profesional usando PIL/Pillow
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    import sys
except ImportError:
    print("❌ PIL/Pillow no está instalado")
    print("Instala con: pip install Pillow")
    sys.exit(1)

def create_dmg_background(version="3.0.0", output_file="dmg_background.png"):
    """Crea imagen de fondo profesional para DMG"""
    
    # Dimensiones del DMG
    width, height = 600, 400
    
    # Crear imagen con gradiente
    img = Image.new('RGB', (width, height), '#f8f9fa')
    draw = ImageDraw.Draw(img)
    
    # Crear gradiente sutil
    for y in range(height):
        # Gradiente de gris claro a gris más claro
        color_value = int(248 + (y / height) * 7)  # 248 a 255
        color = (color_value, color_value + 1, color_value + 2)
        draw.line([(0, y), (width, y)], fill=color)
    
    # Intentar cargar fuentes del sistema
    try:
        # macOS fonts
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        version_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        instruction_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        try:
            # Fallback fonts
            title_font = ImageFont.truetype("Arial.ttf", 36)
            subtitle_font = ImageFont.truetype("Arial.ttf", 18)
            version_font = ImageFont.truetype("Arial.ttf", 16)
            instruction_font = ImageFont.truetype("Arial.ttf", 14)
        except:
            # Default font
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            version_font = ImageFont.load_default()
            instruction_font = ImageFont.load_default()
    
    # Colores
    title_color = '#2c3e50'      # Azul oscuro
    subtitle_color = '#34495e'    # Gris azulado
    version_color = '#e74c3c'     # Rojo (color de marca)
    instruction_color = '#7f8c8d' # Gris claro
    
    # Dibujar textos
    # Título principal
    title_text = "Cronux"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, 80), title_text, fill=title_color, font=title_font)
    
    # Subtítulo
    subtitle_text = "Sistema de Control de Versiones Local"
    subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    draw.text((subtitle_x, 130), subtitle_text, fill=subtitle_color, font=subtitle_font)
    
    # Versión
    version_text = f"v{version}"
    version_bbox = draw.textbbox((0, 0), version_text, font=version_font)
    version_width = version_bbox[2] - version_bbox[0]
    version_x = (width - version_width) // 2
    draw.text((version_x, 160), version_text, fill=version_color, font=version_font)
    
    # Instrucciones
    instruction_text = "Arrastra Cronux.app a Applications para instalar"
    instruction_bbox = draw.textbbox((0, 0), instruction_text, font=instruction_font)
    instruction_width = instruction_bbox[2] - instruction_bbox[0]
    instruction_x = (width - instruction_width) // 2
    draw.text((instruction_x, 320), instruction_text, fill=instruction_color, font=instruction_font)
    
    # Agregar elementos decorativos
    # Línea decorativa arriba del título
    line_y = 60
    line_start = (width // 2 - 50, line_y)
    line_end = (width // 2 + 50, line_y)
    draw.line([line_start, line_end], fill=version_color, width=2)
    
    # Línea decorativa abajo de la versión
    line_y = 190
    line_start = (width // 2 - 30, line_y)
    line_end = (width // 2 + 30, line_y)
    draw.line([line_start, line_end], fill=instruction_color, width=1)
    
    # Guardar imagen
    img.save(output_file, 'PNG', quality=95)
    print(f"✅ Imagen de fondo creada: {output_file}")
    print(f"📐 Dimensiones: {width}x{height}")
    
    return output_file

def create_retina_background(version="3.0.0"):
    """Crea versión retina (2x) de la imagen"""
    output_file = "dmg_background@2x.png"
    
    # Dimensiones retina
    width, height = 1200, 800
    
    img = Image.new('RGB', (width, height), '#f8f9fa')
    draw = ImageDraw.Draw(img)
    
    # Gradiente
    for y in range(height):
        color_value = int(248 + (y / height) * 7)
        color = (color_value, color_value + 1, color_value + 2)
        draw.line([(0, y), (width, y)], fill=color)
    
    # Fuentes más grandes para retina
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 72)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        version_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        instruction_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        version_font = ImageFont.load_default()
        instruction_font = ImageFont.load_default()
    
    # Colores
    title_color = '#2c3e50'
    subtitle_color = '#34495e'
    version_color = '#e74c3c'
    instruction_color = '#7f8c8d'
    
    # Textos (posiciones escaladas x2)
    title_text = "Cronux"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, 160), title_text, fill=title_color, font=title_font)
    
    subtitle_text = "Sistema de Control de Versiones Local"
    subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    draw.text((subtitle_x, 260), subtitle_text, fill=subtitle_color, font=subtitle_font)
    
    version_text = f"v{version}"
    version_bbox = draw.textbbox((0, 0), version_text, font=version_font)
    version_width = version_bbox[2] - version_bbox[0]
    version_x = (width - version_width) // 2
    draw.text((version_x, 320), version_text, fill=version_color, font=version_font)
    
    instruction_text = "Arrastra Cronux.app a Applications para instalar"
    instruction_bbox = draw.textbbox((0, 0), instruction_text, font=instruction_font)
    instruction_width = instruction_bbox[2] - instruction_bbox[0]
    instruction_x = (width - instruction_width) // 2
    draw.text((instruction_x, 640), instruction_text, fill=instruction_color, font=instruction_font)
    
    # Líneas decorativas (escaladas)
    draw.line([(width // 2 - 100, 120), (width // 2 + 100, 120)], fill=version_color, width=4)
    draw.line([(width // 2 - 60, 380), (width // 2 + 60, 380)], fill=instruction_color, width=2)
    
    img.save(output_file, 'PNG', quality=95)
    print(f"✅ Imagen retina creada: {output_file}")
    
    return output_file

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Crear imagen de fondo para DMG")
    parser.add_argument("--version", default="3.0.0", help="Versión de la app")
    parser.add_argument("--output", default="dmg_background.png", help="Archivo de salida")
    parser.add_argument("--retina", action="store_true", help="Crear también versión retina")
    
    args = parser.parse_args()
    
    print("🎨 Creando imagen de fondo para DMG...")
    
    # Crear imagen normal
    create_dmg_background(args.version, args.output)
    
    # Crear versión retina si se solicita
    if args.retina:
        create_retina_background(args.version)
    
    print("🎉 ¡Imágenes creadas exitosamente!")
    print("")
    print("💡 Para usar en tu DMG:")
    print(f"   ./create_custom_dmg.sh dist/Cronux.app Cronux-v{args.version} {args.version}")