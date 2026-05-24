#!/usr/bin/env python3
"""
Gera PNGs a partir dos SVGs gerados:
- mbya_post_1080.svg -> mbya_post_1080.png (1080x1080)
- mbya_post_1080_1350.svg -> mbya_post_1080_1350.png (1080x1350)

Instalação:
    pip install cairosvg

Uso:
    python3 export_pngs.py
"""
import sys
from pathlib import Path

try:
    import cairosvg
except Exception as e:
    print("ERROR: cairosvg não está instalado. Instale com: pip install cairosvg")
    sys.exit(2)

BASE = Path(__file__).parent
svg1 = BASE / "mbya_post_1080.svg"
svg2 = BASE / "mbya_post_1080_1350.svg"
png1 = BASE / "mbya_post_1080.png"
png2 = BASE / "mbya_post_1080_1350.png"

if not svg1.exists() or not svg2.exists():
    print("ERROR: Arquivos SVG não encontrados em:")
    print(svg1)
    print(svg2)
    sys.exit(3)

print("Convertendo:")
print(f" - {svg1} -> {png1} (1080x1080)")
print(f" - {svg2} -> {png2} (1080x1350)")

try:
    cairosvg.svg2png(url=str(svg1), write_to=str(png1), output_width=1080, output_height=1080)
    cairosvg.svg2png(url=str(svg2), write_to=str(png2), output_width=1080, output_height=1350)
except Exception as e:
    print("Erro durante conversão:", e)
    sys.exit(4)

print("Conversão concluída. Arquivos gerados:")
print(png1)
print(png2)
