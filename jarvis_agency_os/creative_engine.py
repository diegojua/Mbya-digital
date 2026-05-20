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
from jarvis_agency_os.ranker import rank_creatives
from jarvis_agency_os.visual_memory_v2 import get_memory
from jarvis_agency_os.design_intelligence import apply_design_intelligence
from jarvis_agency_os.template_registry import (
    TEMPLATE_REGISTRY,
    get_template,
    normalize_formats,
    select_templates,
)

# Alias de compatibilidade para chamadas antigas.
BLUEPRINT_REGISTRY = TEMPLATE_REGISTRY

# ── Imagens Padrão por Nicho (Unsplash) ─────────────────────────────────────

DEFAULT_IMAGES = {
    "padaria": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1080&q=90",
    "panificadora": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1080&q=90",
    "comida": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1080&q=90",
    "joia": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=1080&q=90",
    "joias": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=1080&q=90",
    "joalheria": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?auto=format&fit=crop&w=1080&q=90",
    "semijoia": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?auto=format&fit=crop&w=1080&q=90",
    "aliança": "https://images.unsplash.com/photo-1603561596112-db1d75a2783d?auto=format&fit=crop&w=1080&q=90",
    "odonto": "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?auto=format&fit=crop&w=1080&q=90",
    "dent": "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?auto=format&fit=crop&w=1080&q=90",
    "clinica": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?auto=format&fit=crop&w=1080&q=90",
    "educa": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=1080&q=90",
    "escola": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=1080&q=90",
    "jiujitsu": "https://images.unsplash.com/photo-1591117207239-788bf8de6c3b?auto=format&fit=crop&w=1080&q=90",
    "jiu-jitsu": "https://images.unsplash.com/photo-1591117207239-788bf8de6c3b?auto=format&fit=crop&w=1080&q=90",
    "academia": "https://images.unsplash.com/photo-1534258936925-c58bed479fcb?auto=format&fit=crop&w=1080&q=90",
    "default": "https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=1080&q=90"
}


def _load_config(filename: str) -> dict:
    path = os.path.join(CONFIG_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _get_art_direction(niche: str) -> dict:
    """Retorna uma direção de arte dedicada quando o nicho exigir padrão premium."""
    config = _load_config("art_directions.json")
    niche_lower = (niche or "").lower()
    for direction_key, direction in config.get("directions", {}).items():
        if direction_key == config.get("default_direction"):
            continue
        matches = direction.get("match", [])
        if direction_key in niche_lower or any(term in niche_lower for term in matches):
            return {"key": direction_key, **direction}

    default_key = config.get("default_direction")
    default_direction = config.get("directions", {}).get(default_key, {})
    if default_direction:
        return {"key": default_key, **default_direction}
    return {}


def _apply_art_direction(ctx: dict) -> dict:
    """Mescla tokens da direção de arte no contexto vindo do Graphify."""
    direction = _get_art_direction(ctx.get("niche", ""))
    if not direction:
        return ctx

    if direction.get("design_state"):
        ctx["design_state"] = direction["design_state"]

    ctx.setdefault("palette", {}).update(direction.get("palette", {}))
    ctx.setdefault("design_state_config", {}).update(direction.get("typography", {}))
    ctx["art_direction"] = direction
    ctx["premium_mode"] = True
    return ctx


def _find_local_campaign_images(workspace_dir: str) -> list[str]:
    """Encontra fotos/cenas locais úteis, evitando logos e imagens de referência."""
    if not workspace_dir or not os.path.isdir(workspace_dir):
        return []

    allowed_ext = (".png", ".jpg", ".jpeg", ".webp")
    excluded_terms = ("logo", "brand", "marca", "referencia", "referência", "ref_", "muestra")
    preferred_terms = ("concept", "cena", "foto", "crianca", "criança", "pedagoga", "advogado", "hero")
    candidates = []

    for root, _, files in os.walk(workspace_dir):
        depth = os.path.relpath(root, workspace_dir).count(os.sep)
        if depth > 2:
            continue
        for filename in files:
            lower = filename.lower()
            if not lower.endswith(allowed_ext):
                continue
            if any(term in lower for term in excluded_terms):
                continue
            path = os.path.join(root, filename)
            priority = 0 if any(term in lower for term in preferred_terms) else 1
            candidates.append((priority, path))

    return [path for _, path in sorted(candidates, key=lambda item: (item[0], item[1]))]


def _get_image_for_niche(niche: str, workspace_dir: str, art_direction: dict = None, angle_index: int = 0) -> str:
    """Retorna URL de imagem: primeiro checa workspace local, depois direção de arte e fallback."""
    niche_lower = (niche or "").lower()
    search_dirs = [workspace_dir]
    if any(term in niche_lower for term in ("educa", "pedagog", "infantil", "reforço", "reforco")):
        search_dirs.extend([
            os.path.join(ROOT_DIR, "amar_pedagogico", "assets"),
            os.path.join(ROOT_DIR, "amar_pedagogico", "novo_criativo", "assets"),
            os.path.join(ROOT_DIR, "workspace", "amar_pedagogico", "assets"),
            os.path.join(ROOT_DIR, "workspace", "amar_pedagogico", "amar_pedagogico_pipeline", "assets"),
        ])

    local_images = []
    seen = set()
    for directory in search_dirs:
        for path in _find_local_campaign_images(directory):
            if path not in seen:
                seen.add(path)
                local_images.append(path)
    if local_images:
        return local_images[angle_index % len(local_images)]

    images = (art_direction or {}).get("photography", {}).get("images", [])
    if images:
        return images[angle_index % len(images)]

    for key, url in DEFAULT_IMAGES.items():
        if key in niche_lower:
            return url
    return DEFAULT_IMAGES["default"]


def _select_blueprints(design_state: str, niche: str = None, use_memory: bool = True,
                       preferred_blueprints: list = None, formats: list = None) -> list:
    """Seleciona blueprints/templates pelo registry central."""
    memory_lookup = None
    if use_memory:
        try:
            memory_lookup = get_memory().get_best_blueprint_for_state
        except Exception as exc:
            print(f"   ⚠️ Memória indisponível para seleção de blueprint: {exc}")
    selected = select_templates(
        design_state,
        niche=niche or "",
        formats=formats,
        preferred_templates=preferred_blueprints,
        memory_lookup=memory_lookup,
    )
    return selected


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


def _build_signal_html(items: list) -> str:
    """Gera os três blocos numerados usados no layout jurídico premium."""
    fallback = ["Análise objetiva", "Estratégia personalizada", "Atendimento direto"]
    selected = (items or fallback)[:3]
    while len(selected) < 3:
        selected.append(fallback[len(selected)])

    html = ""
    for index, item in enumerate(selected, start=1):
        html += f'''<div class="signal">
        <span>{index:02d}</span>
        <strong>{item}</strong>
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

    ctx = _apply_art_direction(ctx)
    ctx = apply_design_intelligence(ctx)
    design_state = ctx["design_state"]
    palette = ctx["palette"]
    requested_formats = normalize_formats(ctx.get("formats") or ctx.get("format"))
    print(f"   → Design State: {design_state}")
    print(f"   → Palette: {palette['accent']} on {palette['bg_primary']}")
    print(f"   → Formats: {', '.join(requested_formats)}")
    if ctx.get("art_direction"):
        print(f"   → Art Direction: {ctx['art_direction']['key']}")
    if ctx.get("design_intelligence"):
        print(f"   → Design Intelligence: {ctx['design_intelligence']['key']}")

    # 2. Copy
    print("✍️  [2/4] Xquads v2: Gerando copy por estado psicológico...")
    copy_result = generate_copy(ctx, ctx.get("objective", "conversão"))
    if "error" in copy_result:
        return {"error": f"Xquads: {copy_result['error']}"}

    angles = copy_result["copy_data"]["angles"]
    print(f"   → {len(angles)} ângulos de copy gerados")

    # 3. Blueprint Selection
    print("⚛️  [3/4] Structure Engine: Selecionando blueprints compatíveis...")
    blueprints = _select_blueprints(
        design_state,
        niche=ctx.get("niche"),
        preferred_blueprints=ctx.get("art_direction", {}).get("preferred_blueprints"),
        formats=requested_formats,
    )
    print(f"   → Blueprints: {blueprints}")

    # 4. Hydration — gera todas as combinações
    print("🎨 [4/4] Hidratando blueprints com tokens + copy...")
    whatsapp_url = f"https://wa.me/{ctx.get('whatsapp', '5587999999999')}"

    generated = []
    output_dir = os.path.join(workspace_dir, "generated_creatives")
    os.makedirs(output_dir, exist_ok=True)

    for bp_key in blueprints:
        template = get_template(bp_key)
        bp_file = template["path"]
        if not os.path.exists(bp_file):
            print(f"   ⚠️ Blueprint não encontrado: {bp_file}")
            continue

        for i, angle in enumerate(angles):
            image_url = _get_image_for_niche(ctx["niche"], workspace_dir, ctx.get("art_direction"), i)
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
                "SIGNAL_HTML": _build_signal_html(angle.get("checklist", [])),
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
                "template_family": template.get("family"),
                "format": template.get("format"),
                "width": template.get("width"),
                "height": template.get("height"),
                "angle_index": i,
                "design_state": design_state,
                "client": ctx["client_name"],
                "niche": ctx["niche"],
                "objective": ctx.get("objective"),
                "art_direction": ctx.get("art_direction", {}).get("key"),
                "design_intelligence": ctx.get("design_intelligence"),
                "premium_mode": ctx.get("premium_mode", False),
                "headline": f"{angle['headline_1']} {angle['headline_2']}",
                "body": angle["body"],
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


def generate_rank_and_learn(workspace_dir: str = None, top_n: int = 2,
                            client_override: dict = None) -> dict:
    """
    Gera criativos, rankeia e registra o aprendizado na Visual Memory.
    Esta é a rota recomendada para o Jarvis evoluir a cada criação.
    """
    generation = generate_creatives(workspace_dir=workspace_dir, client_override=client_override)
    if "error" in generation:
        return generation

    generated = generation.get("generated", [])
    ranked = rank_creatives(generated, top_n=top_n)

    saved_memory = []
    if ranked.get("status") == "success":
        saved_memory = get_memory().record_creative_batch(
            ranked.get("all_scored", []),
            context={
                "design_state": generation.get("design_state"),
            },
        )

    return {
        "status": "success",
        "generation": generation,
        "ranking": ranked,
        "memory_records": saved_memory,
        "memory_stats": get_memory().get_stats(),
    }


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Antigravity Creative Engine")
    parser.add_argument("--workspace", default=WORKSPACE_DIR, help="Diretório do workspace")
    parser.add_argument("--learn", action="store_true", help="Rankeia e registra aprendizado na memória persistente")
    parser.add_argument("--top-n", type=int, default=2, help="Quantidade de criativos no topo do ranking")
    args = parser.parse_args()

    if args.learn:
        result = generate_rank_and_learn(args.workspace, top_n=args.top_n)
    else:
        result = generate_creatives(args.workspace)
    if "error" in result:
        print(f"\n❌ Erro: {result['error']}")
    else:
        print(f"\n📦 Resultado: {json.dumps(result, indent=2, ensure_ascii=False, default=str)}")
