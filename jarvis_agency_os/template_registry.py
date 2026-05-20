"""
Template Registry — catálogo único de formatos, dimensões e blueprints.

Antes o Creative Engine conhecia apenas um dicionário local de blueprints de
feed. Esta camada separa formato, família visual e regras mínimas, abrindo
caminho para Story, Landing Page e Carrossel sem duplicar lógica.
"""
from __future__ import annotations

import os
from typing import Any


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BLUEPRINTS_DIR = os.path.join(BASE_DIR, "blueprints", "creatives")


TEMPLATE_REGISTRY: dict[str, dict[str, Any]] = {
    "feed_education_soft_premium": {
        "file": "feed_education_soft_premium.html",
        "format": "feed",
        "family": "education_soft_premium",
        "width": 1080,
        "height": 1080,
        "best_for": ["educational", "safety", "performance"],
        "niche_only": ["educa", "escola", "pedagog", "infantil", "reforço", "reforco"],
        "requires_image": True,
        "description": "Feed educacional premium com estética acolhedora, foto editorial e CTA limpo.",
    },
    "feed_legal_premium_editorial": {
        "file": "feed_legal_premium_editorial.html",
        "format": "feed",
        "family": "legal_premium",
        "width": 1080,
        "height": 1080,
        "best_for": ["authority", "legal"],
        "niche_only": ["advocacia", "advogado", "juridic", "direito", "legal"],
        "requires_image": True,
        "description": "Feed jurídico boutique premium. Texto à esquerda, foto editorial à direita.",
    },
    "feed_split_editorial": {
        "file": "feed_split_editorial.html",
        "format": "feed",
        "family": "editorial_split",
        "width": 1080,
        "height": 1080,
        "best_for": ["authority", "performance"],
        "requires_image": True,
        "description": "Split 50/50. Conteúdo esquerda, imagem direita.",
    },
    "feed_fullbleed_overlay": {
        "file": "feed_fullbleed_overlay.html",
        "format": "feed",
        "family": "cinematic_overlay",
        "width": 1080,
        "height": 1080,
        "best_for": ["luxury", "authority"],
        "requires_image": True,
        "description": "Imagem full-bleed com card glassmorphism centralizado.",
    },
    "feed_card_editorial": {
        "file": "feed_card_editorial.html",
        "format": "feed",
        "family": "editorial_card",
        "width": 1080,
        "height": 1080,
        "best_for": ["safety", "educational"],
        "requires_image": True,
        "description": "Grid 55/45 com checklist e CTA flutuante.",
    },
    "feed_dark_cinematic": {
        "file": "feed_dark_cinematic.html",
        "format": "feed",
        "family": "dark_cinematic",
        "width": 1080,
        "height": 1080,
        "best_for": ["luxury", "urgency", "authority", "performance"],
        "requires_image": True,
        "description": "Dark overlay cinematográfico com headline grande.",
    },
    "story_premium_editorial": {
        "file": "story_premium_editorial.html",
        "format": "story",
        "family": "vertical_editorial",
        "width": 1080,
        "height": 1920,
        "best_for": ["authority", "performance", "educational", "safety", "luxury"],
        "requires_image": True,
        "description": "Story vertical premium com hero editorial, checklist e CTA fixo inferior.",
    },
    "story_education_soft_premium": {
        "file": "story_education_soft_premium.html",
        "format": "story",
        "family": "education_vertical_soft_premium",
        "width": 1080,
        "height": 1920,
        "best_for": ["educational", "safety", "performance"],
        "niche_only": ["educa", "escola", "pedagog", "infantil", "reforço", "reforco"],
        "requires_image": True,
        "description": "Story educacional premium com estética acolhedora, CTA claro e leitura rápida.",
    },
    "story_legal_authority": {
        "file": "story_legal_authority.html",
        "format": "story",
        "family": "legal_vertical_authority",
        "width": 1080,
        "height": 1920,
        "best_for": ["authority", "legal", "performance"],
        "niche_only": ["advocacia", "advogado", "juridic", "direito", "legal"],
        "requires_image": True,
        "description": "Story jurídico premium com grid editorial, sinais de autoridade e CTA inferior.",
    },
}


FORMAT_DEFAULTS = {
    "feed": {"width": 1080, "height": 1080},
    "story": {"width": 1080, "height": 1920},
    "landing": {"width": 1440, "height": 1800},
}


def normalize_formats(value: Any) -> list[str]:
    """Normaliza formatos vindos do briefing/client_override."""
    if not value:
        return ["feed"]
    if isinstance(value, str):
        raw = [part.strip().lower() for part in value.replace(";", ",").split(",")]
    else:
        raw = [str(part).strip().lower() for part in value]

    aliases = {
        "instagram_feed": "feed",
        "post": "feed",
        "square": "feed",
        "stories": "story",
        "instagram_story": "story",
        "vertical": "story",
        "lp": "landing",
        "landing_page": "landing",
        "landpage": "landing",
    }
    formats = []
    for item in raw:
        if not item:
            continue
        normalized = aliases.get(item, item)
        if normalized not in formats:
            formats.append(normalized)
    return formats or ["feed"]


def get_template(template_key: str) -> dict[str, Any]:
    """Retorna template com path absoluto resolvido."""
    data = TEMPLATE_REGISTRY[template_key].copy()
    data["key"] = template_key
    data["path"] = os.path.join(BLUEPRINTS_DIR, data["file"])
    return data


def templates_for_format(format_name: str) -> dict[str, dict[str, Any]]:
    return {
        key: value
        for key, value in TEMPLATE_REGISTRY.items()
        if value.get("format") == format_name
    }


def select_templates(
    design_state: str,
    niche: str = "",
    formats: list[str] | None = None,
    preferred_templates: list[str] | None = None,
    memory_lookup=None,
) -> list[str]:
    """Seleciona templates compatíveis por formato, nicho e estado de design."""
    selected_formats = normalize_formats(formats)
    niche_lower = (niche or "").lower()
    compatible_ranked: list[tuple[int, str]] = []

    for template_key, template in TEMPLATE_REGISTRY.items():
        if template.get("format") not in selected_formats:
            continue
        niche_only = template.get("niche_only", [])
        if niche_only and not any(term in niche_lower for term in niche_only):
            continue
        if design_state in template.get("best_for", []):
            priority = 0 if niche_only else 1
            compatible_ranked.append((priority, template_key))

    compatible = [key for _, key in sorted(compatible_ranked, key=lambda item: item[0])]

    if not compatible:
        for format_name in selected_formats:
            compatible.extend(list(templates_for_format(format_name).keys())[:2])

    preferred = []
    if preferred_templates:
        preferred = [
            key for key in preferred_templates
            if key in TEMPLATE_REGISTRY and TEMPLATE_REGISTRY[key].get("format") in selected_formats
        ]
        compatible = preferred + [key for key in compatible if key not in preferred]

    if memory_lookup:
        try:
            remembered = memory_lookup(design_state, niche=niche)
            if remembered in compatible and remembered not in preferred:
                preferred_count = len(preferred)
                remainder = compatible[preferred_count:]
                compatible = compatible[:preferred_count] + [remembered] + [
                    key for key in remainder if key != remembered
                ]
        except Exception:
            pass

    def specificity_key(template_key: str) -> tuple[int, int]:
        niche_only = TEMPLATE_REGISTRY.get(template_key, {}).get("niche_only", [])
        is_specific = bool(niche_only and any(term in niche_lower for term in niche_only))
        return (0 if is_specific else 1, compatible.index(template_key))

    compatible = sorted(compatible, key=specificity_key)
    return compatible
