import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont

def download_font(font_path):
    # Fonte garantida do sistema Linux
    return "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def draw_text_wrapped(draw, text, font, fill, max_width, x, y):
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        # Using textbbox to measure text length
        bbox = draw.textbbox((0, 0), " ".join(current_line), font=font)
        w = bbox[2] - bbox[0]
        if w > max_width:
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
    if current_line:
        lines.append(" ".join(current_line))

    y_text = y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        # Draw text with shadow/stroke for better visibility
        draw.text((x - w/2, y_text), line, font=font, fill=(0,0,0), stroke_width=2, stroke_fill=(255,255,255))
        draw.text((x - w/2, y_text), line, font=font, fill=fill)
        y_text += h + 10

def render_slide(image_path, text, output_path, font_path):
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        width, height = img.size

        font_size = int(height * 0.06)
        font = ImageFont.truetype(font_path, font_size)

        max_width = width * 0.8

        # We put the text in the center
        # Since I don't know the exact lines height beforehand easily with simple logic,
        # I'll just draw starting slightly above center.
        draw_text_wrapped(draw, text, font, (30, 41, 59), max_width, width/2, height/2.5)

        img.save(output_path)
        print(f"Salvo: {output_path}")
    except Exception as e:
        print(f"Erro em {image_path}: {e}")

if __name__ == "__main__":
    base_dir = "/home/diego/.gemini/antigravity/brain/6a69e0b2-8c0e-4e35-86f9-a9a4ea99a445"
    workspace = "/home/diego/Documentos/Mbya Digital/workspace"
    output_dir = os.path.join(workspace, "project_images", "amar_pedagogico", "generated")
    os.makedirs(output_dir, exist_ok=True)
    font_path = os.path.join(output_dir, "Montserrat-Bold.ttf")

    font_path = download_font(font_path)

    slides = [
        {
            "in": f"{base_dir}/amar_slide_1_1779062796795.png",
            "out": f"{output_dir}/amar_final_1.png",
            "text": "A ESCOLA ENSINA.\nA ESCOLA AMAR TRANSFORMA."
        },
        {
            "in": f"{base_dir}/amar_slide_2_1779062807932.png",
            "out": f"{output_dir}/amar_final_2.png",
            "text": "POR QUE SEU FILHO PRECISA DE MAIS?\n\nAjudamos a encaixar as\npeças do aprendizado."
        },
        {
            "in": f"{base_dir}/amar_slide_3_1779062852634.png",
            "out": f"{output_dir}/amar_final_3.png",
            "text": "CONSTRUINDO UM\nFUTURO BRILHANTE!\n\nClique no link da bio e agende\numa aula experimental."
        }
    ]

    for slide in slides:
        render_slide(slide["in"], slide["text"], slide["out"], font_path)
