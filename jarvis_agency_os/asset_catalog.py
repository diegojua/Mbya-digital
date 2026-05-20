"""
Asset Catalog — matching inteligente para templates e previews premium.

O catálogo bruto vem de pastas/ZIPs com nomes heterogêneos. Esta camada
normaliza acentos, calcula score por intenção de nicho e retorna metadados
úteis para o manifesto da landing.
"""
from __future__ import annotations

import os
import re
import unicodedata
from typing import Any


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets_globais")


NICHE_SYNONYMS = {
    "educacao": ["clases en vivo", "clases", "curso", "ebook"],
    "educacao infantil": ["clases en vivo", "clases", "curso"],
    "pedagogico": ["clases en vivo", "clases", "curso"],
    "saude": ["medical", "clinica"],
    "advocacia": ["banking", "score", "copywhite"],
    "advogado": ["banking", "score", "copywhite"],
    "juridico": ["banking", "score", "copywhite"],
    "clinica": ["clinica", "medical"],
    "odontologia": ["medical", "clinica"],
    "marketing": ["marketing digital", "social media"],
    "fitness": ["fitness", "recetas fitness"],
}


def normalize_text(value: str) -> str:
    """Remove acentos e ruído para comparação de nichos."""
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _tokens(value: str) -> set[str]:
    stopwords = {"de", "da", "do", "e", "em", "para", "com", "o", "a", "os", "as"}
    return {token for token in normalize_text(value).split() if token not in stopwords and len(token) > 2}


def _candidate_preview(page_relative_path: str) -> str | None:
    page_dir = os.path.join(ASSETS_DIR, "Templates", page_relative_path)
    if not os.path.isdir(page_dir):
        return None
    for filename in os.listdir(page_dir):
        lower = filename.lower()
        if lower.startswith(("muestra", "muesta")) and lower.endswith((".jpg", ".jpeg", ".png")):
            return os.path.join(page_dir, filename)
    return None


def _candidate_files(page_relative_path: str) -> list[str]:
    page_dir = os.path.join(ASSETS_DIR, "Templates", page_relative_path)
    if not os.path.isdir(page_dir):
        return []
    selected = []
    for filename in os.listdir(page_dir):
        if filename.lower().endswith((".json", ".zip")):
            selected.append(os.path.join(page_dir, filename))
    return sorted(selected)


def match_catalog_entry(niche: str, catalog: dict[str, Any], asset_type: str = "page") -> dict[str, Any]:
    """Retorna o melhor match do catálogo para o nicho informado."""
    if not catalog:
        return {"status": "not_found", "reason": "empty_catalog", "score": 0}

    normalized_niche = normalize_text(niche)
    niche_tokens = _tokens(normalized_niche)
    expanded_terms = set(niche_tokens)
    for key, synonyms in NICHE_SYNONYMS.items():
        key_norm = normalize_text(key)
        if key_norm in normalized_niche or any(token in key_norm for token in niche_tokens):
            for synonym in synonyms:
                expanded_terms.update(_tokens(synonym))

    best: dict[str, Any] | None = None
    for entry_key, entry_data in catalog.items():
        if entry_key == "global_automation" or asset_type not in entry_data:
            continue
        normalized_key = normalize_text(entry_key)
        key_tokens = _tokens(normalized_key)
        overlap = expanded_terms & key_tokens
        direct = normalized_key in normalized_niche or normalized_niche in normalized_key
        score = (len(overlap) * 18) + (45 if direct else 0)

        if score <= 0:
            continue

        page_relative = entry_data.get(asset_type)
        candidate = {
            "status": "matched",
            "key": entry_key,
            "score": score,
            "asset_type": asset_type,
            "relative_path": page_relative,
            "absolute_path": os.path.join(ASSETS_DIR, "Templates", page_relative),
            "preview_path": _candidate_preview(page_relative) if asset_type == "page" else None,
            "template_files": _candidate_files(page_relative) if asset_type == "page" else [],
            "matched_terms": sorted(overlap),
        }
        if not best or candidate["score"] > best["score"]:
            best = candidate

    return best or {
        "status": "not_found",
        "reason": "no_scored_match",
        "score": 0,
        "niche": niche,
        "expanded_terms": sorted(expanded_terms),
    }
