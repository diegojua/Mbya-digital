"""
Design Intelligence — diretrizes visuais reutilizáveis para criativos.

Esta camada transforma briefing/nicho em um perfil de direção visual com
tokens, regras, anti-patterns e quality gates. A ideia é trazer o rigor de uma
skill de UI/UX para dentro do pipeline sem acoplar o projeto a um repositório
externo.
"""
from __future__ import annotations

import json
import os
from typing import Any

CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
CONFIG_PATH = os.path.join(CONFIG_DIR, "design_intelligence.json")


def load_design_intelligence() -> dict[str, Any]:
    """Carrega a configuração de design intelligence."""
    if not os.path.exists(CONFIG_PATH):
        return {"default_profile": "premium_agency", "profiles": {}}

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _matches_profile(text: str, profile_key: str, profile: dict[str, Any]) -> bool:
    if profile_key in text:
        return True

    matches = profile.get("match", [])
    return any(term == "*" or term.lower() in text for term in matches)


def resolve_design_profile(context: dict[str, Any]) -> dict[str, Any]:
    """Resolve o perfil de design mais adequado para o contexto."""
    config = load_design_intelligence()
    profiles = config.get("profiles", {})
    default_key = config.get("default_profile", "premium_agency")
    default_profile = profiles.get(default_key, {})

    text = " ".join(
        str(context.get(key, ""))
        for key in ("niche", "client_name", "objective", "details", "tema")
    ).lower()

    selected_key = default_key
    selected_profile = default_profile

    for key, profile in profiles.items():
        if key == default_key:
            continue
        if _matches_profile(text, key, profile):
            selected_key = key
            selected_profile = profile
            break

    merged = {
        "key": selected_key,
        "description": selected_profile.get("description", default_profile.get("description", "")),
        "style_keywords": list(default_profile.get("style_keywords", [])),
        "layout_rules": list(default_profile.get("layout_rules", [])),
        "icon_rules": list(default_profile.get("icon_rules", [])),
        "anti_patterns": list(default_profile.get("anti_patterns", [])),
        "quality_gates": dict(default_profile.get("quality_gates", {})),
    }

    for list_key in ("style_keywords", "layout_rules", "icon_rules", "anti_patterns"):
        for item in selected_profile.get(list_key, []):
            if item not in merged[list_key]:
                merged[list_key].append(item)

    merged["quality_gates"].update(selected_profile.get("quality_gates", {}))
    if selected_profile.get("palette"):
        merged["palette"] = selected_profile["palette"]
    if selected_profile.get("typography"):
        merged["typography"] = selected_profile["typography"]

    return merged


def apply_design_intelligence(context: dict[str, Any]) -> dict[str, Any]:
    """Aplica tokens do perfil visual no contexto do Creative Engine."""
    profile = resolve_design_profile(context)
    context["design_intelligence"] = profile

    if profile.get("palette"):
        context.setdefault("palette", {}).update(profile["palette"])
    if profile.get("typography"):
        context.setdefault("design_state_config", {}).update(profile["typography"])

    return context


def build_design_brief(context: dict[str, Any]) -> str:
    """Gera um briefing visual em Markdown para humanos ou agentes."""
    profile = resolve_design_profile(context)

    def bullets(items: list[str]) -> str:
        return "\n".join(f"- {item}" for item in items)

    gates = "\n".join(f"- **{name}:** {value}" for name, value in profile.get("quality_gates", {}).items())

    return f"""# Design Intelligence Brief

**Perfil:** {profile.get("key")}
**Descrição:** {profile.get("description")}

## Estilo
{bullets(profile.get("style_keywords", []))}

## Regras de Layout
{bullets(profile.get("layout_rules", []))}

## Ícones
{bullets(profile.get("icon_rules", []))}

## Evitar
{bullets(profile.get("anti_patterns", []))}

## Quality Gates
{gates}
"""


def evaluate_design_metadata(creative: dict[str, Any]) -> dict[str, Any]:
    """
    Avalia metadados disponíveis antes do render visual.

    Não substitui QA por screenshot, mas penaliza sinais ruins e recompensa
    criativos que carregam um perfil de direção visual.
    """
    profile = creative.get("design_intelligence") or {}
    score = 55.0
    notes: list[str] = []

    if profile.get("key"):
        score += 20
        notes.append(f"perfil aplicado: {profile['key']}")
    else:
        notes.append("sem perfil de design intelligence")

    blueprint = creative.get("blueprint", "")
    if blueprint:
        score += 10
    if creative.get("premium_mode"):
        score += 5

    text_blob = " ".join(
        str(creative.get(key, ""))
        for key in ("headline", "body", "cta", "blueprint")
    ).lower()

    penalties = 0
    for pattern in profile.get("anti_patterns", []):
        if pattern.lower() in text_blob:
            penalties += 5
            notes.append(f"anti-pattern textual: {pattern}")

    if len(creative.get("headline", "")) > 75:
        penalties += 8
        notes.append("headline longa para criativo de feed/story")

    score = max(0.0, min(100.0, score - penalties))
    return {"score": score, "notes": notes}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gera briefing de Design Intelligence")
    parser.add_argument("--niche", default="geral")
    parser.add_argument("--client", default="Cliente")
    parser.add_argument("--objective", default="conversão")
    args = parser.parse_args()

    ctx = {"niche": args.niche, "client_name": args.client, "objective": args.objective}
    print(build_design_brief(ctx))
