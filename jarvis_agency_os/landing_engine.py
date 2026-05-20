"""
Landing Engine — gera landing pages HTML reais a partir do contexto da campanha.

Esta camada substitui o antigo comportamento de apenas escrever JSON. O JSON
continua existindo como manifesto, mas o pipeline passa a entregar uma página
renderizável e auditável.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from jarvis_agency_os.creative_engine import _get_image_for_niche
from jarvis_agency_os.design_intelligence import apply_design_intelligence
from jarvis_agency_os.visual_qa import evaluate_visual_quality
from jarvis_agency_os.asset_catalog import match_catalog_entry


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
BLUEPRINT_PATH = os.path.join(BASE_DIR, "blueprints", "landing_premium_agency.html")
LANDING_BLUEPRINTS = {
    "landing_premium_agency": BLUEPRINT_PATH,
    "landing_education_premium": os.path.join(BASE_DIR, "blueprints", "landing_education_premium.html"),
    "landing_legal_premium": os.path.join(BASE_DIR, "blueprints", "landing_legal_premium.html"),
}
WORKSPACE_DIR = os.path.join(ROOT_DIR, "workspace")


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.lower()).strip("_")
    return normalized or "landing"


def _hydrate(template: str, tokens: dict[str, Any]) -> str:
    html = template
    for key, value in tokens.items():
        html = html.replace("{{" + key + "}}", str(value))
    return html


def _benefits_html(items: list[Any]) -> str:
    fallback = [
        {"title": "Diagnóstico claro", "body": "Entenda o cenário antes de decidir o próximo passo."},
        {"title": "Plano personalizado", "body": "Uma estratégia prática, ajustada ao perfil e ao objetivo."},
        {"title": "Acompanhamento próximo", "body": "Suporte com comunicação direta durante a jornada."},
    ]
    normalized = []
    for item in items or fallback:
        if isinstance(item, dict):
            title = item.get("title") or item.get("headline") or item.get("name") or "Benefício"
            body = item.get("body") or item.get("description") or item.get("text") or ""
        else:
            title = str(item)
            body = "Aplicação prática para gerar mais clareza, segurança e evolução."
        normalized.append({"title": title, "body": body})
    while len(normalized) < 3:
        normalized.append(fallback[len(normalized)])

    icon = """
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M5 12.5l4.2 4.2L19 6.8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """
    html = ""
    for benefit in normalized[:3]:
        html += f"""
        <article class="benefit">
            {icon}
            <strong>{benefit['title']}</strong>
            <p>{benefit['body']}</p>
        </article>
        """
    return html


def _first_angle(copy_data: dict[str, Any]) -> dict[str, Any]:
    angles = copy_data.get("angles") or []
    if angles:
        return angles[0]
    hero = copy_data.get("hero") or {}
    headline = hero.get("headline") or copy_data.get("headline") or "Estratégia clara para avançar com confiança."
    parts = headline.split(" ", 3)
    return {
        "headline_1": " ".join(parts[:3]) if len(parts) >= 3 else headline,
        "headline_2": parts[3] if len(parts) > 3 else "",
        "body": hero.get("subheadline") or copy_data.get("subheadline") or "Atendimento especializado com clareza, método e acompanhamento próximo.",
        "badge": hero.get("badge") or "Atendimento especializado",
        "cta": hero.get("cta") or copy_data.get("ctaText") or "Fale com a equipe",
        "footer_cta": "Converse com um especialista e entenda o melhor caminho.",
        "checklist": [],
    }


def _landing_blueprint_for_niche(niche: str) -> tuple[str, str]:
    niche_lower = (niche or "").lower()
    if any(term in niche_lower for term in ["educação", "educacao", "pedagog", "reforço", "reforco", "infantil"]):
        return "landing_education_premium", LANDING_BLUEPRINTS["landing_education_premium"]
    if any(term in niche_lower for term in ["advocacia", "advogado", "juridic", "direito", "legal"]):
        return "landing_legal_premium", LANDING_BLUEPRINTS["landing_legal_premium"]
    return "landing_premium_agency", LANDING_BLUEPRINTS["landing_premium_agency"]


def _landing_content_for_niche(niche: str) -> dict[str, str]:
    """Textos de suporte por nicho para a landing não soar como template genérico."""
    niche_lower = (niche or "").lower()
    if any(term in niche_lower for term in ["educação", "educacao", "pedagog", "reforço", "reforco", "infantil"]):
        return {
            "visual_card_title": "A criança aprende melhor quando se sente segura para tentar.",
            "visual_card_text": "Acompanhamento próximo, atividades direcionadas e comunicação clara com a família.",
            "section_title": "Como o acompanhamento ajuda no dia a dia",
            "section_text": "O processo identifica dificuldades, organiza uma rotina possível e acompanha a evolução com metas simples.",
            "final_title": "Vamos entender o momento do seu filho?",
            "final_text": "Fale com a equipe e agende uma avaliação pedagógica para receber uma orientação inicial.",
        }
    if any(term in niche_lower for term in ["advocacia", "advogado", "juridic", "direito", "legal"]):
        return {
            "visual_card_title": "Decisões importantes pedem orientação jurídica clara.",
            "visual_card_text": "Análise objetiva, comunicação direta e estratégia alinhada ao risco real do caso.",
            "section_title": "Atuação jurídica com método e sigilo",
            "section_text": "O atendimento organiza documentos, riscos e próximos passos para que cada decisão seja tomada com mais segurança.",
            "final_title": "Precisa de uma orientação segura?",
            "final_text": "Fale com a equipe e receba uma análise inicial para entender o melhor caminho jurídico.",
        }
    return {
        "visual_card_title": "Uma jornada com clareza do primeiro contato ao próximo passo.",
        "visual_card_text": "A página organiza proposta, benefícios e chamada para contato em uma experiência única.",
        "section_title": "O que torna o atendimento diferente",
        "section_text": "Um processo objetivo para transformar dúvida em decisão, com comunicação clara e direção prática.",
        "final_title": "Pronto para dar o próximo passo?",
        "final_text": "Fale com a equipe e receba uma orientação inicial para entender a melhor estratégia.",
    }


def generate_landing_page(
    workspace_dir: str | None = None,
    context: dict[str, Any] | None = None,
    copy_data: dict[str, Any] | None = None,
    catalog_match: dict[str, Any] | None = None,
    catalog: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Gera uma landing page HTML e um manifesto JSON."""
    workspace_dir = workspace_dir or WORKSPACE_DIR
    os.makedirs(workspace_dir, exist_ok=True)
    output_dir = os.path.join(workspace_dir, "generated_landings")
    os.makedirs(output_dir, exist_ok=True)

    context = apply_design_intelligence(dict(context or {}))
    copy_data = dict(copy_data or {})
    angle = _first_angle(copy_data)
    palette = context.get("palette") or {}

    client_name = copy_data.get("client_name") or context.get("client_name") or "Cliente"
    niche = copy_data.get("niche") or context.get("niche") or "Atendimento especializado"
    template_key, template_path = _landing_blueprint_for_niche(niche)
    landing_content = _landing_content_for_niche(niche)
    resolved_catalog_match = catalog_match or {}
    if catalog and not resolved_catalog_match:
        resolved_catalog_match = match_catalog_entry(niche, catalog, asset_type="page")
    whatsapp = context.get("whatsapp", "5587999999999")
    whatsapp_url = f"https://wa.me/{whatsapp}"
    image_url = _get_image_for_niche(niche, workspace_dir, context.get("art_direction"), 0)

    tokens = {
        "BG_PRIMARY": palette.get("bg_primary", "#0B1020"),
        "BG_CARD": palette.get("bg_card", "#121826"),
        "TEXT_PRIMARY": palette.get("text_primary", "#F5F7FA"),
        "TEXT_MUTED": palette.get("text_muted", "#94A3B8"),
        "ACCENT": palette.get("accent", "#D4AF37"),
        "BORDER_COLOR": palette.get("border_color", "rgba(255,255,255,0.14)"),
        "FONT_HEADLINE": context.get("design_state_config", {}).get("font_headline", "Outfit"),
        "CLIENT_NAME": client_name,
        "NICHE": niche,
        "LOGO_ICON": context.get("logo_icon", "+"),
        "HEADLINE_LINE1": angle.get("headline_1", "Estratégia clara."),
        "HEADLINE_LINE2": angle.get("headline_2", "Acompanhamento próximo."),
        "BODY_TEXT": angle.get("body", ""),
        "BADGE_TEXT": angle.get("badge", "Atendimento especializado"),
        "CTA_TEXT": angle.get("cta", "Fale com a equipe"),
        "FOOTER_CTA_TEXT": angle.get("footer_cta", "Converse com nossa equipe."),
        "WHATSAPP_URL": whatsapp_url,
        "IMAGE_URL": image_url,
        "IMAGE_ALT": f"{client_name} - {niche}",
        "VISUAL_CARD_TITLE": landing_content["visual_card_title"],
        "VISUAL_CARD_TEXT": landing_content["visual_card_text"],
        "SECTION_TITLE": landing_content["section_title"],
        "SECTION_TEXT": landing_content["section_text"],
        "BENEFITS_HTML": _benefits_html(copy_data.get("benefits") or angle.get("checklist")),
        "FINAL_TITLE": landing_content["final_title"],
        "FINAL_TEXT": landing_content["final_text"],
    }

    with open(template_path, "r", encoding="utf-8") as f:
        html = _hydrate(f.read(), tokens)

    html_path = os.path.join(output_dir, f"{_slug(client_name)}_landing_page.html")
    manifest_path = os.path.join(output_dir, f"{_slug(client_name)}_landing_manifest.json")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    manifest = {
        "status": "success",
        "file": html_path,
        "manifest": manifest_path,
        "format": "landing",
        "width": 1440,
        "height": 1800,
        "client": client_name,
        "niche": niche,
        "catalog_match": resolved_catalog_match,
        "template_preview": resolved_catalog_match.get("preview_path"),
        "template_files": resolved_catalog_match.get("template_files", []),
        "template_key": template_key,
        "headline": f"{tokens['HEADLINE_LINE1']} {tokens['HEADLINE_LINE2']}".strip(),
        "cta": tokens["CTA_TEXT"],
    }
    manifest["visual_qa"] = evaluate_visual_quality(manifest)

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return manifest
