#!/usr/bin/env python3

"""
Script para crear imagen de fondo personalizada para DMG
Uso: python create_dmg_background.py <version> <output_file>
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math

def create_dmg_background(version="3.0.0", output_file="dmg_background.png"):
    """Crear imagen de fondo profesional para DMG - Solo fondo sin texto"""
    
    # Dimensiones del DMG (más grande para mejor diseño)
    width, height = 700, 500
    
    # Crear imagen base con gradiente moderno
    img = Image.new('RGB', (width, height), '#1a1a1a')
    draw = ImageDraw.Draw(img)
    
    # Crear gradiente diagonal moderno (oscuro a azul)
    for y in range(height):
        for x in range(width):
            # Gradiente diagonal con múltiples colores
            progress_x = x / width
            progress_y = y / height
            
            # Mezcla de colores para un gradiente moderno
            r = int(26 + (progress_x * 20) + (progress_y * 15))  # 26 -> 61
            g = int(26 + (progress_x * 35) + (progress_y * 25))  # 26 -> 86
            b = int(26 + (progress_x * 60) + (progress_y * 40))  # 26 -> 126
            
            # Limitar valores
            r = min(255, max(0, r))
            g = min(255, max(0, g))
            b = min(255, max(0, b))
            
            img.putpixel((x, y), (r, g, b))
    
    # Agregar elementos decorativos geométricos sutiles
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Círculos decorativos con transparencia muy sutil
    circle_color = (255, 255, 255, 8)  # Blanco muy transparente
    
    # Círculo grande en la esquina superior derecha
    overlay_draw.ellipse([450, -50, 650, 150], fill=circle_color)
    
    # Círculo mediano en la esquina inferior izquierda
    overlay_draw.ellipse([-50, 250, 150, 450], fill=circle_color)
    
    # Círculo pequeño en el centro-derecha
    overlay_draw.ellipse([500, 150, 600, 250], fill=circle_color)
    
    # Líneas decorativas muy sutiles
    line_color = (255, 255, 255, 5)
    for i in range(0, width, 60):
        overlay_draw.line([(i, 0), (i + 120, height)], fill=line_color, width=1)
    
    # Combinar con la imagen base
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    # Agregar patrón de puntos muy sutil
    dot_color = (255, 255, 255, 15)
    dot_overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    dot_draw = ImageDraw.Draw(dot_overlay)
    
    # Patrón de puntos muy sutil
    for x in range(80, width - 80, 100):
        for y in range(80, height - 80, 100):
            if (x + y) % 200 == 0:  # Solo algunos puntos
                dot_draw.ellipse([x-1, y-1, x+1, y+1], fill=dot_color)
    
    # Combinar puntos
    img = Image.alpha_composite(img.convert('RGBA'), dot_overlay).convert('RGB')
    
    # Guardar imagen
    img.save(output_file, 'PNG', optimize=True, quality=95)
    print(f"✅ Imagen de fondo creada: {output_file}")
    print(f"📐 Dimensiones: {width}x{height}")
    return output_file

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Crear imagen de fondo para DMG")
    parser.add_argument("--version", default="3.0.0", help="Versión de la app")
    parser.add_argument("--output", default="dmg_background.png", help="Archivo de salida")
    
    args = parser.parse_args()
    
    try:
        create_dmg_background(args.version, args.output)
        return 0
    except Exception as e:
        print(f"❌ Error al crear imagen: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())