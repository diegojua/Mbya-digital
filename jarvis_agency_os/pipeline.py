"""
Campaign Pipeline — orquestração única de criativos, landing, QA e memória.

Esta é a rota canônica para campanhas: escreve briefing, gera formatos pedidos,
rankeia, registra aprendizado, renderiza campeões e cria landing page real.
"""
from __future__ import annotations

import os
import hashlib
from datetime import datetime
from typing import Any

from graphify.engine import process_briefing
from xquads.engine import generate_copy
from jarvis_agency_os.asset_catalog import match_catalog_entry
from jarvis_agency_os.creative_engine import generate_creatives
from jarvis_agency_os.export_engine import export_campaign_artifacts, project_image_dir
from jarvis_agency_os.landing_engine import generate_landing_page
from jarvis_agency_os.ranker import rank_creatives
from jarvis_agency_os.renderer import render_html_to_png
from jarvis_agency_os.template_registry import normalize_formats
from jarvis_agency_os.visual_memory_v2 import get_memory


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE_DIR = os.path.join(ROOT_DIR, "workspace")
CATALOG_PATH = os.path.join(WORKSPACE_DIR, "asset_catalog.json")


def _load_catalog(catalog_path: str = CATALOG_PATH) -> dict[str, Any]:
    if os.path.exists(catalog_path):
        import json
        with open(catalog_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _write_briefing(workspace_dir: str, client_name: str, niche: str, objective: str,
                    formats: list[str], extra: dict[str, Any] | None = None) -> str:
    os.makedirs(workspace_dir, exist_ok=True)
    extra = extra or {}
    is_mbya = "mbya" in (client_name or "").lower()
    default_logo_text = "MBYA" if is_mbya else client_name.upper()
    default_logo_sub = "MARKETING" if is_mbya else niche.lower()
    path = os.path.join(workspace_dir, "briefing.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"Cliente: {client_name}\n")
        f.write(f"Nicho: {niche}\n")
        f.write(f"Objetivo: {objective}\n")
        f.write(f"Formatos: {', '.join(formats)}\n")
        f.write("Detalhes: Geração automatizada de alta conversão sob o padrão do Creative OS.\n")
        f.write(f"Localização: {extra.get('location', 'Petrolina e Juazeiro')}\n")
        f.write(f"Logo_icone: {extra.get('logo_icon', '+')}\n")
        f.write(f"Logo_texto: {extra.get('logo_text', default_logo_text)}\n")
        f.write(f"Logo_subtitulo: {extra.get('logo_sub', default_logo_sub)}\n")
        if extra.get("whatsapp"):
            f.write(f"WhatsApp: {extra['whatsapp']}\n")
    return path


def _build_experiment_id(client_name: str, objective: str, niche: str, formats: list[str]) -> str:
    payload = "|".join([
        client_name or "",
        objective or "",
        niche or "",
        ",".join(formats or []),
        datetime.now().isoformat(timespec="seconds"),
    ])
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]


def _top_by_format(scored: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    top: dict[str, dict[str, Any]] = {}
    for creative in scored:
        format_name = creative.get("format") or "feed"
        if format_name not in top:
            top[format_name] = creative
    return top


def _slides_by_format(scored: list[dict[str, Any]], format_name: str, limit: int = 3) -> list[dict[str, Any]]:
    """Seleciona múltiplos criativos do mesmo formato para pacotes como carrossel."""
    slides = [creative for creative in scored if creative.get("format") == format_name]
    return slides[:limit]


def _render_winners(workspace_dir: str, project_name: str, winners: dict[str, dict[str, Any]]) -> dict[str, Any]:
    output_dir = project_image_dir(workspace_dir, project_name, "renders")
    os.makedirs(output_dir, exist_ok=True)
    rendered = {}
    for format_name, creative in winners.items():
        output_path = os.path.join(output_dir, f"winner_{format_name}_{creative['blueprint']}.png")
        rendered[format_name] = render_html_to_png(
            creative["file"],
            output_path,
            width=creative.get("width", 1080),
            height=creative.get("height", 1080),
        )
    return rendered


def _render_carousel_slides(workspace_dir: str, project_name: str, slides: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output_dir = project_image_dir(workspace_dir, project_name, "renders", "carousel")
    os.makedirs(output_dir, exist_ok=True)
    rendered = []
    for index, creative in enumerate(slides, start=1):
        output_path = os.path.join(output_dir, f"slide_{index:02d}_{creative['blueprint']}.png")
        result = render_html_to_png(
            creative["file"],
            output_path,
            width=creative.get("width", 1080),
            height=creative.get("height", 1080),
        )
        result["slide"] = index
        result["creative_file"] = creative["file"]
        rendered.append(result)
    return rendered


def run_campaign_pipeline(
    client_name: str,
    objective: str,
    niche: str = "geral",
    workspace_dir: str | None = None,
    formats: str | list[str] | None = None,
    include_landing: bool = True,
    render_winners: bool = True,
    export_campaign: bool = True,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Executa campanha completa em uma única rota."""
    workspace_dir = workspace_dir or WORKSPACE_DIR
    selected_formats = normalize_formats(formats or "feed")
    experiment_id = (extra or {}).get("experiment_id") or _build_experiment_id(
        client_name, objective, niche, selected_formats
    )
    briefing_path = _write_briefing(workspace_dir, client_name, niche, objective, selected_formats, extra)

    generation = generate_creatives(
        workspace_dir,
        client_override={
            "client_name": client_name,
            "niche": niche,
            "objective": objective,
            "formats": selected_formats,
            **(extra or {}),
        },
    )
    if "error" in generation:
        return {"status": "error", "stage": "creative_generation", "error": generation["error"]}

    ranking = rank_creatives(generation.get("generated", []), top_n=max(2, len(selected_formats)))
    all_scored = ranking.get("all_scored", [])
    memory_records = get_memory().record_creative_batch(
        all_scored,
        context={
            "client_name": client_name,
            "niche": niche,
            "objective": objective,
            "experiment_id": experiment_id,
        },
    ) if all_scored else []

    winners = _top_by_format(all_scored)
    carousel_slides = _slides_by_format(all_scored, "carousel", limit=3) if "carousel" in selected_formats else []
    rendered = _render_winners(workspace_dir, client_name, winners) if render_winners and winners else {}
    rendered_carousel_slides = (
        _render_carousel_slides(workspace_dir, client_name, carousel_slides)
        if render_winners and carousel_slides
        else []
    )

    landing = None
    if include_landing:
        graph_result = process_briefing(workspace_dir)
        if "error" not in graph_result:
            context = graph_result["context_graph"]
            context.update({"client_name": client_name, "niche": niche, "objective": objective})
            copy_result = generate_copy(context, objective)
            catalog = _load_catalog()
            catalog_match = match_catalog_entry(niche, catalog, asset_type="page")
            landing = generate_landing_page(
                workspace_dir=workspace_dir,
                context=context,
                copy_data=copy_result.get("copy_data", {}),
                catalog_match=catalog_match,
            )

    result = {
        "status": "success",
        "briefing_path": briefing_path,
        "experiment_id": experiment_id,
        "formats": selected_formats,
        "generation": generation,
        "image_manifest": generation.get("image_manifest"),
        "image_direction": generation.get("image_direction"),
        "ranking": ranking,
        "winners": winners,
        "carousel_slides": carousel_slides,
        "rendered_winners": rendered,
        "rendered_carousel_slides": rendered_carousel_slides,
        "landing": landing,
        "memory_records": memory_records,
        "memory_stats": get_memory().get_stats(),
    }

    if export_campaign:
        result["campaign_export"] = export_campaign_artifacts(result, workspace_dir)

    return result
