"""
Knowledge Index — regras de design acionáveis a partir dos guias do projeto.

O objetivo desta camada é tirar os arquivos .md da condição de "referência
passiva" e expor regras pequenas que o pipeline consegue consultar durante QA.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

ANTI_AI_SLOP_PATH = os.path.join(ROOT_DIR, "open-design", "craft", "anti-ai-slop.md")


DEFAULT_RULES: dict[str, Any] = {
    "forbidden_hex": [
        "#6366f1",
        "#4f46e5",
        "#4338ca",
        "#3730a3",
        "#8b5cf6",
        "#7c3aed",
        "#a855f7",
    ],
    "forbidden_emoji_icons": ["✨", "🚀", "🎯", "⚡", "🔥", "💡"],
    "placeholder_image_hosts": [
        "unsplash.com",
        "placehold.co",
        "picsum.photos",
        "placekitten.com",
    ],
    "forbidden_gradient_pairs": [
        ("purple", "blue"),
        ("blue", "cyan"),
        ("indigo", "pink"),
        ("#4f46e5", "#06b6d4"),
        ("#6366f1", "#ec4899"),
    ],
    "max_raw_hex_values": 12,
    "max_accent_uses": 6,
}


@lru_cache(maxsize=1)
def load_design_knowledge() -> dict[str, Any]:
    """Carrega regras executáveis e mantém um resumo da fonte em Markdown."""
    knowledge = {
        "source_files": [],
        "rules": DEFAULT_RULES.copy(),
        "notes": [],
    }

    if os.path.exists(ANTI_AI_SLOP_PATH):
        with open(ANTI_AI_SLOP_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        knowledge["source_files"].append(ANTI_AI_SLOP_PATH)
        knowledge["notes"].append("anti-ai-slop carregado")
        if "Emoji as feature icons" in content:
            knowledge["notes"].append("emoji como ícone deve ser penalizado")
        if "External placeholder image CDNs" in content:
            knowledge["notes"].append("CDN de imagem placeholder deve ser penalizado")

    return knowledge


def get_visual_qa_rules() -> dict[str, Any]:
    """Retorna somente o conjunto de regras usado pelo QA visual."""
    return load_design_knowledge()["rules"]
