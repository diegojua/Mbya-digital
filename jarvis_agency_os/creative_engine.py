"""
Antigravity Creative Engine — Orquestrador de Geração Determinística
Gera criativos HTML a partir de blueprints + tokens + copy, renderiza em PNG e rankeia.
"""
import os
import json
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
BLUEPRINTS_DIR = os.path.join(BASE_DIR, "blueprints", "creatives")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
WORKSPACE_DIR = os.path.join(ROOT_DIR, "workspace")

sys.path.insert(0, ROOT_DIR)
from graphify.engine import process_briefing
from xquads.engine import generate_copy

# ── Blueprint Registry ──────────────────────────────────────────────────────

BLUEPRINT_REGISTRY = {
    "feed_split_editorial": {
        "file": "feed_split_editorial.html",
        "best_for": ["authority"],
        "requires_image": True,
        "description": "Split 50/50. Conteúdo esquerda, imagem direita."
    },
    "feed_fullbleed_overlay": {
        "file": "feed_fullbleed_overlay.html",
        "best_for": ["luxury", "authority"],
        "requires_image": True,
        "description": "Imagem full-bleed com card glassmorphism centralizado."
    },
    "feed_card_editorial": {
        "file": "feed_card_editorial.html",
        "best_for": ["safety", "educational"],
        "requires_image": True,
        "description": "Grid 55/45 com checklist e CTA flutuante."
    },
    "feed_dark_cinematic": {
        "file": "feed_dark_cinematic.html",
        "best_for": ["luxury", "urgency", "authority"],
        "requires_image": True,
        "description": "Dark overlay cinematográfico com headline grande."
    }
}

# ── Imagens Padrão por Nicho (Unsplash) ─────────────────────────────────────

DEFAULT_IMAGES = {
    "padaria": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1080&q=90",
    "panificadora": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1080&q=90",
    "comida": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1080&q=90",
    "odonto": "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?auto=format&fit=crop&w=1080&q=90",
    "dent": "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?auto=format&fit=crop&w=1080&q=90",
    "clinica": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1080&q=90",
    "educa": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=1080&q=90",
    "escola": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=1080&q=90",
    "default": "https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=1080&q=90"
}


def _get_image_for_niche(niche: str, workspace_dir: str) -> str:
    """Retorna URL de imagem: primeiro checa workspace local, depois Unsplash."""
    local_images = [f for f in os.listdir(workspace_dir) if f.endswith(('.png', '.jpg', '.jpeg')) and 'concept' in f.lower()]
    if local_images:
        return os.path.join(workspace_dir, local_images[0])

    for key, url in DEFAULT_IMAGES.items():
        if key in niche.lower():
            return url
    return DEFAULT_IMAGES["default"]


def _select_blueprints(design_state: str) -> list:
    """Seleciona blueprints compatíveis com o design state."""
    compatible = []
    for bp_key, bp_data in BLUEPRINT_REGISTRY.items():
        if design_state in bp_data["best_for"]:
            compatible.append(bp_key)

    if not compatible:
        compatible = list(BLUEPRINT_REGISTRY.keys())[:2]
    return compatible


def _build_checklist_html(items: list, accent_color: str = "var(--accent)") -> str:
    """Gera HTML dos itens de checklist."""
    html = ""
    for item in items[:4]:  # max 4 items
        html += f'''<div class="check-item">
        <div class="check-icon">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none"><path d="M20 6L9 17L4 12" stroke="{accent_color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </div>
        {item}
    </div>\n'''
    return html


def _build_details_html(items: list) -> str:
    """Gera HTML dos detail items (para blueprint D)."""
    html = ""
    for item in items[:4]:
        html += f'''<div class="detail-item">
        <span class="detail-dot"></span>
        <span class="detail-text">{item}</span>
    </div>\n'''
    return html


def _hydrate_blueprint(blueprint_path: str, tokens: dict) -> str:
    """Injeta tokens no blueprint HTML via substituição de placeholders."""
    with open(blueprint_path, "r", encoding="utf-8") as f:
        html = f.read()

    for key, value in tokens.items():
        placeholder = "{{" + key + "}}"
        html = html.replace(placeholder, str(value))

    return html


def generate_creatives(workspace_dir: str = None, client_override: dict = None):
    """
    Pipeline completo:
    1. Graphify → context + design state
    2. Xquads → copy angles
    3. Blueprint selection → hydration
    4. Output HTMLs prontos para renderização
    """
    if workspace_dir is None:
        workspace_dir = WORKSPACE_DIR

    # 1. Context
    print("📊 [1/4] Graphify v2: Extraindo contexto e resolvendo design state...")
    graph_result = process_briefing(workspace_dir)
    if "error" in graph_result:
        return {"error": f"Graphify: {graph_result['error']}"}
    ctx = graph_result["context_graph"]

    # Apply overrides
    if client_override:
        ctx.update(client_override)

    design_state = ctx["design_state"]
    palette = ctx["palette"]
    print(f"   → Design State: {design_state}")
    print(f"   → Palette: {palette['accent']} on {palette['bg_primary']}")

    # 2. Copy
    print("✍️  [2/4] Xquads v2: Gerando copy por estado psicológico...")
    copy_result = generate_copy(ctx, ctx.get("objective", "conversão"))
    if "error" in copy_result:
        return {"error": f"Xquads: {copy_result['error']}"}

    angles = copy_result["copy_data"]["angles"]
    print(f"   → {len(angles)} ângulos de copy gerados")

    # 3. Blueprint Selection
    print("⚛️  [3/4] Structure Engine: Selecionando blueprints compatíveis...")
    blueprints = _select_blueprints(design_state)
    print(f"   → Blueprints: {blueprints}")

    # 4. Hydration — gera todas as combinações
    print("🎨 [4/4] Hidratando blueprints com tokens + copy...")
    image_url = _get_image_for_niche(ctx["niche"], workspace_dir)
    whatsapp_url = f"https://wa.me/{ctx.get('whatsapp', '5587999999999')}"

    generated = []
    output_dir = os.path.join(workspace_dir, "generated_creatives")
    os.makedirs(output_dir, exist_ok=True)

    for bp_key in blueprints:
        bp_file = os.path.join(BLUEPRINTS_DIR, BLUEPRINT_REGISTRY[bp_key]["file"])
        if not os.path.exists(bp_file):
            print(f"   ⚠️ Blueprint não encontrado: {bp_file}")
            continue

        for i, angle in enumerate(angles):
            tokens = {
                # Design tokens
                "BG_PRIMARY": palette["bg_primary"],
                "BG_CARD": palette.get("bg_card", palette["bg_primary"]),
                "TEXT_PRIMARY": palette["text_primary"],
                "TEXT_MUTED": palette["text_muted"],
                "ACCENT": palette["accent"],
                "ACCENT_GLOW": palette["accent_glow"],
                "ACCENT_CTA": palette.get("accent", "#f59e0b"),
                "BORDER_COLOR": palette["border_color"],
                "FONT_HEADLINE": ctx.get("design_state_config", {}).get("font_headline", "Outfit"),
                # Brand
                "CLIENT_NAME": ctx["client_name"],
                "LOGO_ICON": ctx.get("logo_icon", "✦"),
                "LOGO_TEXT": ctx.get("logo_text", ctx["client_name"]),
                "LOGO_SUB": ctx.get("logo_sub", ctx["niche"]),
                # Copy
                "HEADLINE_LINE1": angle["headline_1"],
                "HEADLINE_LINE2": angle["headline_2"],
                "BODY_TEXT": angle["body"],
                "BADGE_TEXT": angle["badge"],
                "CTA_TEXT": angle["cta"],
                "FOOTER_CTA_TEXT": angle["footer_cta"],
                "FOOTER_INFO": f"📍 {ctx.get('location', 'Brasil')}",
                # Checklist
                "CHECKLIST_HTML": _build_checklist_html(angle.get("checklist", [])),
                "DETAILS_HTML": _build_details_html(angle.get("checklist", [])),
                # Image
                "IMAGE_URL": image_url,
                "IMAGE_ALT": f"{ctx['client_name']} - {angle['badge']}",
                # Links
                "WHATSAPP_URL": whatsapp_url,
                "LOCATION": ctx.get("location", "Brasil"),
            }

            html = _hydrate_blueprint(bp_file, tokens)

            filename = f"{ctx['client_name'].lower().replace(' ', '_')}_{bp_key}_v{i+1}.html"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)

            generated.append({
                "file": filepath,
                "blueprint": bp_key,
                "angle_index": i,
                "design_state": design_state,
                "headline": f"{angle['headline_1']} {angle['headline_2']}",
                "cta": angle["cta"]
            })
            print(f"   ✅ Gerado: {filename}")

    print(f"\n🎉 {len(generated)} criativos gerados em: {output_dir}")

    return {
        "status": "success",
        "generated": generated,
        "output_dir": output_dir,
        "design_state": design_state,
        "total": len(generated)
    }


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Antigravity Creative Engine")
    parser.add_argument("--workspace", default=WORKSPACE_DIR, help="Diretório do workspace")
    args = parser.parse_args()

    result = generate_creatives(args.workspace)
    if "error" in result:
        print(f"\n❌ Erro: {result['error']}")
    else:
        print(f"\n📦 Resultado: {json.dumps(result, indent=2, ensure_ascii=False, default=str)}")
