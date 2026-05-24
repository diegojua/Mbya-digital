"""
Image Direction — prompts e manifestos de imagem inspirados no Open Design.

Esta camada transforma referências do Open Design em contrato executável para
o JarvisAgency OS: cada campanha passa a ter slots de imagem, dimensões,
composição e prompts antes do HTML/render.
"""
from __future__ import annotations

import json
import os
import re
import shutil
from copy import deepcopy
from typing import Any


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
CONFIG_DIR = os.path.join(BASE_DIR, "config")
IMAGE_DIRECTIONS_PATH = os.path.join(CONFIG_DIR, "image_directions.json")
WORKSPACE_IMAGES_DIR = os.path.join(ROOT_DIR, "workspace", "project_images")
OPEN_DESIGN_LANDING_ASSETS_DIR = os.path.join(
    ROOT_DIR,
    "open-design",
    "skills",
    "open-design-landing",
    "assets",
)


DEFAULT_SLOT_ORDER = [
    "feed",
    "story",
    "carousel",
    "landing_hero",
    "landing_about",
    "landing_cta",
]


FALLBACK_ASSET_BY_SLOT = {
    "feed": "hero.png",
    "story": "hero.png",
    "carousel": "capabilities.png",
    "landing_hero": "hero.png",
    "landing_about": "about.png",
    "landing_cta": "cta.png",
}


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", (value or "").lower()).strip("_")
    return normalized or "project"


def load_image_directions() -> dict[str, Any]:
    """Carrega configuração de direções visuais."""
    if not os.path.exists(IMAGE_DIRECTIONS_PATH):
        return {"default_direction": "premium_editorial", "directions": {}}
    with open(IMAGE_DIRECTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_image_direction(context: dict[str, Any]) -> dict[str, Any]:
    """Resolve a direção visual mais adequada pelo nicho/briefing."""
    config = load_image_directions()
    directions = config.get("directions", {})
    default_key = config.get("default_direction", "premium_editorial")
    default_direction = directions.get(default_key, {})

    haystack = " ".join(
        str(context.get(key, ""))
        for key in ("niche", "objective", "client_name", "design_state")
    ).lower()

    for key, direction in directions.items():
        if key == default_key:
            continue
        matches = direction.get("match", [])
        if any(term != "*" and term.lower() in haystack for term in matches):
            merged = deepcopy(default_direction)
            merged.update(direction)
            merged["slots"] = {
                **default_direction.get("slots", {}),
                **direction.get("slots", {}),
            }
            merged["avoid"] = list(dict.fromkeys(
                default_direction.get("avoid", []) + direction.get("avoid", [])
            ))
            merged["key"] = key
            return merged

    fallback = deepcopy(default_direction)
    fallback["key"] = default_key
    return fallback


def _brand_variables(context: dict[str, Any]) -> str:
    client = context.get("client_name") or "Cliente"
    niche = context.get("niche") or "serviço premium"
    objective = context.get("objective") or "conversão"
    accent = (
        context.get("palette", {}).get("accent")
        or context.get("accent")
        or "brand accent used sparingly"
    )
    headline = context.get("headline") or context.get("main_headline") or ""
    cta = context.get("cta") or context.get("cta_text") or ""

    lines = [
        f'Brand/client: "{client}"',
        f'Niche/offer: "{niche}"',
        f'Campaign objective: "{objective}"',
        f"Brand accent: {accent}",
    ]
    if headline:
        lines.append(f'Headline context: "{headline}"')
    if cta:
        lines.append(f'CTA context: "{cta}"')
    return "\n".join(lines)


def build_image_prompt(
    context: dict[str, Any],
    slot_id: str,
    direction: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Monta prompt estruturado para um slot de imagem."""
    resolved_direction = direction or resolve_image_direction(context)
    slots = resolved_direction.get("slots", {})
    if slot_id not in slots:
        raise KeyError(f"Slot de imagem desconhecido: {slot_id}")

    slot = slots[slot_id]
    avoid = ", ".join(resolved_direction.get("avoid", []))
    prompt = "\n\n".join([
        resolved_direction.get("style_anchor", ""),
        _brand_variables(context),
        f"Slot: {slot_id}",
        f"Target ratio/dimensions: {slot.get('ratio')} ({slot.get('width')}x{slot.get('height')})",
        f"Composition: {slot.get('composition')}",
        f"Avoid: {avoid}",
        "Important: do not render final marketing copy inside the image unless explicitly requested; leave clean areas for HTML typography.",
    ]).strip()

    return {
        "id": slot_id,
        "file": f"{slot_id}.png",
        "width": slot.get("width"),
        "height": slot.get("height"),
        "ratio": slot.get("ratio"),
        "direction": resolved_direction.get("key"),
        "design_systems": resolved_direction.get("design_systems", []),
        "prompt": prompt,
        "required": True,
    }


def build_image_manifest(
    context: dict[str, Any],
    formats: list[str] | None = None,
    slots: list[str] | None = None,
) -> dict[str, Any]:
    """Cria manifesto de imagem para campanha/landing/post."""
    resolved_direction = resolve_image_direction(context)
    requested_slots = slots
    if requested_slots is None:
        requested_slots = []
        for format_name in formats or ["feed"]:
            if format_name == "landing":
                requested_slots.extend(["landing_hero", "landing_about", "landing_cta"])
            elif format_name in {"feed", "story", "carousel"}:
                requested_slots.append(format_name)
        if not requested_slots:
            requested_slots = ["feed"]

    ordered_slots = [
        slot for slot in DEFAULT_SLOT_ORDER
        if slot in requested_slots and slot in resolved_direction.get("slots", {})
    ]
    ordered_slots.extend(
        slot for slot in requested_slots
        if slot not in ordered_slots and slot in resolved_direction.get("slots", {})
    )

    prompts = [
        build_image_prompt(context, slot_id, direction=resolved_direction)
        for slot_id in ordered_slots
    ]

    client_name = context.get("client_name") or "Cliente"
    project_slug = context.get("project_slug") or _slug(client_name)
    return {
        "status": "success",
        "schema": "jarvis-image-manifest.v1",
        "inspired_by": [
            "open-design/skills/open-design-landing/assets/imagegen-prompts.md",
            "open-design/skills/open-design-landing/assets/image-manifest.json",
        ],
        "project_slug": project_slug,
        "client": client_name,
        "niche": context.get("niche"),
        "objective": context.get("objective"),
        "direction": {
            "key": resolved_direction.get("key"),
            "description": resolved_direction.get("description"),
            "design_systems": resolved_direction.get("design_systems", []),
            "avoid": resolved_direction.get("avoid", []),
        },
        "slots": prompts,
    }


def save_image_manifest(
    context: dict[str, Any],
    workspace_dir: str | None = None,
    formats: list[str] | None = None,
    slots: list[str] | None = None,
) -> dict[str, Any]:
    """Salva manifesto e prompts em workspace/project_images/<slug>/."""
    manifest = build_image_manifest(context, formats=formats, slots=slots)
    base_dir = workspace_dir or WORKSPACE_IMAGES_DIR
    project_dir = os.path.join(base_dir, manifest["project_slug"])
    prompts_dir = os.path.join(project_dir, "prompts")
    assets_dir = os.path.join(project_dir, "assets")
    generated_dir = os.path.join(project_dir, "generated")
    renders_dir = os.path.join(project_dir, "renders")
    screenshots_dir = os.path.join(project_dir, "screenshots")
    exports_dir = os.path.join(project_dir, "exports")

    for directory in (prompts_dir, assets_dir, generated_dir, renders_dir, screenshots_dir, exports_dir):
        os.makedirs(directory, exist_ok=True)

    manifest_path = os.path.join(project_dir, "manifest.json")
    for slot in manifest["slots"]:
        prompt_path = os.path.join(prompts_dir, f"{slot['id']}.txt")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(slot["prompt"])
        slot["prompt_path"] = prompt_path
        slot["asset_path"] = os.path.join(assets_dir, slot["file"])
        fallback_name = FALLBACK_ASSET_BY_SLOT.get(slot["id"])
        fallback_path = os.path.join(OPEN_DESIGN_LANDING_ASSETS_DIR, fallback_name or "")
        if fallback_name and os.path.exists(fallback_path) and not os.path.exists(slot["asset_path"]):
            shutil.copy2(fallback_path, slot["asset_path"])
            slot["asset_source"] = fallback_path
            slot["asset_status"] = "fallback_open_design"
        elif os.path.exists(slot["asset_path"]):
            slot["asset_status"] = "ready"
        else:
            slot["asset_status"] = "missing"

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    manifest["manifest_path"] = manifest_path
    manifest["project_dir"] = project_dir
    manifest["directories"] = {
        "prompts": prompts_dir,
        "assets": assets_dir,
        "generated": generated_dir,
        "renders": renders_dir,
        "screenshots": screenshots_dir,
        "exports": exports_dir,
    }
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return manifest


if __name__ == "__main__":
    sample = {
        "client_name": "Mbya Marketing",
        "niche": "agência de marketing performance",
        "objective": "conversão",
        "formats": ["feed", "landing"],
    }
    print(json.dumps(build_image_manifest(sample, formats=sample["formats"]), indent=2, ensure_ascii=False))
