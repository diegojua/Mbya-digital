#!/usr/bin/env python3
"""Audita landpages e componentes gerados fora das pastas oficiais."""
from __future__ import annotations

import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "open-design",
    "xquads-squads",
    "assets_globais",
}
CANONICAL_PREFIXES = (
    "development_landpages/",
    "jarvis_agency_os/blueprints/",
    "workspace/generated_landings/",
    "workspace/exports/",
)
SUSPICIOUS_PARTS = (
    "output_code",
)
LANDING_EXTENSIONS = {".html", ".tsx", ".jsx"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
LANDING_TERMS = ("landing", "landpage", "hero", "page")
BLUEPRINT_RE = re.compile(r'"(landing_[a-zA-Z0-9_]+)"\s*:')
def _is_ignored(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.relative_to(ROOT).parts)


def _is_landing_like(path: Path) -> bool:
    lower_name = path.name.lower()
    lower_parts = "/".join(part.lower() for part in path.relative_to(ROOT).parts)
    if path.suffix.lower() not in LANDING_EXTENSIONS:
        return False
    if any(term in lower_name for term in LANDING_TERMS):
        return True
    if any(term in lower_parts for term in LANDING_TERMS):
        return True
    return any(part in lower_parts for part in SUSPICIOUS_PARTS)


def _is_allowed(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    return rel.startswith(CANONICAL_PREFIXES)


def _is_image_allowed(path: Path) -> bool:
    parts = path.relative_to(ROOT).parts
    return len(parts) >= 4 and parts[0] == "workspace" and parts[1] == "project_images" and bool(parts[2])


def main() -> int:
    findings: list[str] = []
    image_findings: list[str] = []
    for current_root, dirs, files in os.walk(ROOT):
        current = Path(current_root)
        dirs[:] = [directory for directory in dirs if directory not in IGNORED_DIRS]
        if _is_ignored(current):
            continue
        for filename in files:
            path = current / filename
            if _is_landing_like(path) and not _is_allowed(path):
                findings.append(path.relative_to(ROOT).as_posix())
            if path.suffix.lower() in IMAGE_EXTENSIONS and not _is_image_allowed(path):
                image_findings.append(path.relative_to(ROOT).as_posix())

    engine_path = ROOT / "jarvis_agency_os" / "landing_engine.py"
    registered_blueprints = set(BLUEPRINT_RE.findall(engine_path.read_text(encoding="utf-8")))
    for blueprint in (ROOT / "jarvis_agency_os" / "blueprints").glob("landing_*.html"):
        key = blueprint.stem
        if key not in registered_blueprints:
            findings.append(f"{blueprint.relative_to(ROOT).as_posix()} (blueprint nao registrado)")

    if not findings and not image_findings:
        print("OK: nenhum artefato de landpage ou imagem fora das pastas oficiais.")
        return 0

    if findings:
        print("LANDPAGES/COMPONENTES FORA DO PADRAO:")
        for item in findings:
            print(f"- {item}")
    if image_findings:
        if findings:
            print()
        print("IMAGENS FORA DO PADRAO:")
        for item in image_findings:
            print(f"- {item}")
    print("\nConsulte OUTPUT_CONVENTIONS.md antes de mover ou promover esses arquivos.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
