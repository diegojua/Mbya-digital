"""
Visual QA — quality gates determinísticos para criativos HTML.

Esta primeira camada não substitui screenshot/Playwright, mas já impede que
arte com sinais claros de template, tokens quebrados, CTA fraco ou ícone amador
aprenda como "boa" na memória visual.
"""
from __future__ import annotations

import os
import json
import re
import subprocess
import tempfile
from html import unescape
from typing import Any

from jarvis_agency_os.knowledge_index import get_visual_qa_rules


HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
TAG_TEXT_RE = re.compile(r"<(h[1-6]|button|a|li)[^>]*>(.*?)</\1>", re.IGNORECASE | re.DOTALL)
STYLE_BLOCK_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.IGNORECASE | re.DOTALL)
CSS_CLASS_ICON_RE = re.compile(r'class=["\'][^"\']*(icon|emoji|badge)[^"\']*["\']', re.IGNORECASE)


def _playwright_require_target() -> str:
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    playwright_path = os.path.join(
        root_dir,
        "open-design",
        "node_modules",
        ".pnpm",
        "playwright@1.59.1",
        "node_modules",
        "playwright",
    )
    return playwright_path if os.path.exists(playwright_path) else "playwright"


def _read_html(creative: dict[str, Any]) -> str:
    if creative.get("html"):
        return str(creative["html"])

    path = creative.get("file") or creative.get("filepath")
    if path and os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def _strip_tags(value: str) -> str:
    return unescape(re.sub(r"<[^>]+>", " ", value)).strip()


def _add_issue(issues: list[dict[str, Any]], severity: str, code: str, message: str, penalty: int) -> None:
    issues.append({
        "severity": severity,
        "code": code,
        "message": message,
        "penalty": penalty,
    })


def _resolve_viewport(creative: dict[str, Any], html: str) -> tuple[int, int]:
    explicit_width = creative.get("width")
    explicit_height = creative.get("height")
    if explicit_width and explicit_height:
        return int(explicit_width), int(explicit_height)

    text = " ".join(str(creative.get(key, "")) for key in ("file", "blueprint", "format")).lower()
    if "story" in text or "1080x1920" in html:
        return 1080, 1920
    return 1080, 1080


def evaluate_rendered_layout(html_path: str, width: int = 1080, height: int = 1080) -> dict[str, Any]:
    """
    Mede layout real via Playwright/Chromium.

    Retorna fallback quando Node/Playwright não está disponível, mantendo o QA
    estável em máquinas diferentes.
    """
    if not html_path or not os.path.exists(html_path):
        return {"status": "unavailable", "issues": [], "metrics": {}, "source": "rendered_layout"}

    require_target = _playwright_require_target()
    payload = {
        "htmlPath": os.path.abspath(html_path),
        "width": width,
        "height": height,
        "requireTarget": require_target,
    }

    node_script = r"""
const fs = require('fs');
const payload = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

(async () => {
  const { chromium } = require(payload.requireTarget);
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: payload.width, height: payload.height },
    deviceScaleFactor: 1
  });
  await page.goto('file://' + payload.htmlPath, { waitUntil: 'networkidle' });
  await page.waitForTimeout(350);

  const result = await page.evaluate(() => {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const doc = document.documentElement;
    const body = document.body;

    const rectData = (el) => {
      const rect = el.getBoundingClientRect();
      const style = window.getComputedStyle(el);
      const text = (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ');
      return {
        tag: el.tagName.toLowerCase(),
        className: String(el.className || ''),
        text: text.slice(0, 90),
        left: rect.left,
        top: rect.top,
        right: rect.right,
        bottom: rect.bottom,
        width: rect.width,
        height: rect.height,
        display: style.display,
        visibility: style.visibility,
        overflowX: style.overflowX,
        overflowY: style.overflowY,
        scrollWidth: el.scrollWidth,
        clientWidth: el.clientWidth,
        scrollHeight: el.scrollHeight,
        clientHeight: el.clientHeight,
      };
    };

    const isVisible = (data) =>
      data.display !== 'none' &&
      data.visibility !== 'hidden' &&
      data.width > 1 &&
      data.height > 1;

    const importantSelector = 'h1,h2,h3,p,a,button,li,[class*="cta"],[class*="card"],[class*="headline"]';
    const important = Array.from(document.querySelectorAll(importantSelector))
      .map(rectData)
      .filter(isVisible);

    const leafText = Array.from(document.querySelectorAll('h1,h2,h3,p,a,button,li,span,strong,small'))
      .filter((el) => (el.innerText || el.textContent || '').trim().length > 0)
      .filter((el) => !Array.from(el.children).some((child) => (child.innerText || child.textContent || '').trim().length > 0))
      .map(rectData)
      .filter(isVisible);

    const outsideViewport = important.filter((item) =>
      item.left < -1 || item.top < -1 || item.right > vw + 1 || item.bottom > vh + 1
    );

    const clippedText = leafText.filter((item) => {
      const clipsX = item.overflowX !== 'visible' && item.scrollWidth > item.clientWidth + 2;
      const clipsY = item.overflowY !== 'visible' && item.scrollHeight > item.clientHeight + 2;
      return clipsX || clipsY;
    });

    const edgeRisk = leafText.filter((item) =>
      item.left < 24 || item.right > vw - 24 || item.top < 24 || item.bottom > vh - 24
    );

    const failedImages = Array.from(document.images)
      .filter((img) => !img.complete || img.naturalWidth === 0 || img.naturalHeight === 0)
      .map((img) => img.getAttribute('src') || '');

    return {
      viewport: { width: vw, height: vh },
      document: {
        scrollWidth: Math.max(doc.scrollWidth, body ? body.scrollWidth : 0),
        scrollHeight: Math.max(doc.scrollHeight, body ? body.scrollHeight : 0)
      },
      counts: {
        important: important.length,
        leafText: leafText.length,
        images: document.images.length
      },
      outsideViewport: outsideViewport.slice(0, 8),
      clippedText: clippedText.slice(0, 8),
      edgeRisk: edgeRisk.slice(0, 8),
      failedImages: failedImages.slice(0, 8)
    };
  });

  await browser.close();
  console.log(JSON.stringify({ status: 'success', result }));
})().catch((error) => {
  console.error(error && error.stack ? error.stack : String(error));
  process.exit(1);
});
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        payload_path = os.path.join(tmpdir, "payload.json")
        script_path = os.path.join(tmpdir, "visual_qa_render.js")
        with open(payload_path, "w", encoding="utf-8") as f:
            json.dump(payload, f)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(node_script)

        try:
            result = subprocess.run(
                ["node", script_path, payload_path],
                capture_output=True,
                text=True,
                timeout=20,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            return {
                "status": "unavailable",
                "issues": [],
                "metrics": {},
                "error": str(exc),
                "source": "rendered_layout",
            }

    if result.returncode != 0:
        return {
            "status": "unavailable",
            "issues": [],
            "metrics": {},
            "error": result.stderr[:500],
            "source": "rendered_layout",
        }

    try:
        rendered = json.loads(result.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError) as exc:
        return {
            "status": "unavailable",
            "issues": [],
            "metrics": {},
            "error": str(exc),
            "source": "rendered_layout",
        }

    metrics = rendered.get("result", {})
    issues: list[dict[str, Any]] = []
    document = metrics.get("document", {})

    if document.get("scrollWidth", width) > width + 2:
        _add_issue(issues, "critical", "horizontal_overflow", "Layout gera rolagem horizontal.", 25)
    if height <= 1920 and document.get("scrollHeight", height) > height + 8:
        _add_issue(issues, "warning", "vertical_overflow", "Conteúdo excede a altura do criativo.", 12)
    if metrics.get("outsideViewport"):
        _add_issue(issues, "critical", "element_outside_viewport", "Elementos importantes estão fora da tela.", 25)
    if metrics.get("clippedText"):
        _add_issue(issues, "critical", "text_clipped", "Texto aparece cortado ou com overflow.", 25)
    if metrics.get("edgeRisk"):
        _add_issue(issues, "warning", "unsafe_edge_spacing", "Texto muito próximo da borda/safe area.", 8)
    if metrics.get("failedImages"):
        _add_issue(issues, "critical", "image_load_failed", "Uma ou mais imagens não carregaram.", 20)

    status = "pass"
    if any(issue["severity"] == "critical" for issue in issues):
        status = "fail"
    elif issues:
        status = "review"

    return {
        "status": status,
        "issues": issues,
        "metrics": metrics,
        "source": "rendered_layout",
    }


def evaluate_visual_quality(creative: dict[str, Any]) -> dict[str, Any]:
    """
    Avalia qualidade visual provável a partir do HTML e metadados.

    Retorna score 0-100, lista de issues e status. A saída é estável para uso
    em testes, ranking e memória.
    """
    rules = get_visual_qa_rules()
    html = _read_html(creative)
    issues: list[dict[str, Any]] = []

    if not html:
        _add_issue(issues, "warning", "html_missing", "HTML não disponível para QA visual.", 15)
        return {"score": 85, "status": "review", "issues": issues, "source": "static_html"}

    lower_html = html.lower()
    style_blocks = "\n".join(STYLE_BLOCK_RE.findall(html))
    lower_css = style_blocks.lower()

    if "{{" in html or "}}" in html:
        _add_issue(issues, "critical", "unresolved_tokens", "Há placeholders não hidratados no HTML.", 35)

    if (creative.get("blueprint") or creative.get("file") or creative.get("filepath")) and "data-od-id=" not in html:
        _add_issue(
            issues,
            "info",
            "missing_data_od_id",
            "Blueprint sem data-od-id; revisão por bloco fica limitada.",
            3,
        )

    for host in rules.get("placeholder_image_hosts", []):
        if host in lower_html:
            _add_issue(
                issues,
                "warning",
                "placeholder_image_host",
                f"Imagem externa genérica detectada: {host}.",
                10,
            )
            break

    raw_hex_values = HEX_RE.findall(style_blocks or html)
    unique_hex = {value.lower() for value in raw_hex_values}
    max_raw_hex = int(rules.get("max_raw_hex_values", 12))
    if len(unique_hex) > max_raw_hex:
        _add_issue(
            issues,
            "warning",
            "too_many_raw_hex",
            f"Excesso de cores soltas ({len(unique_hex)} hex diferentes).",
            8,
        )

    for hex_value in rules.get("forbidden_hex", []):
        if hex_value.lower() in lower_css:
            _add_issue(
                issues,
                "critical",
                "default_ai_indigo",
                f"Cor default de template/IA detectada: {hex_value}.",
                20,
            )
            break

    for first, second in rules.get("forbidden_gradient_pairs", []):
        if "gradient" in lower_css and first.lower() in lower_css and second.lower() in lower_css:
            _add_issue(
                issues,
                "warning",
                "generic_trust_gradient",
                "Gradiente clichê de template detectado.",
                12,
            )
            break

    forbidden_emojis = rules.get("forbidden_emoji_icons", [])
    for tag, content in TAG_TEXT_RE.findall(html):
        text = _strip_tags(content)
        if any(emoji in text for emoji in forbidden_emojis):
            _add_issue(
                issues,
                "warning",
                "emoji_icon",
                f"Emoji usado como ícone em <{tag}>.",
                10,
            )
            break

    if CSS_CLASS_ICON_RE.search(html) and not re.search(r"<svg\b", html, re.IGNORECASE):
        _add_issue(
            issues,
            "warning",
            "icon_without_svg",
            "Elementos de ícone sem SVG monoline detectável.",
            8,
        )

    cta = str(creative.get("cta", "")).strip()
    if cta:
        normalized_html = re.sub(r"\s+", " ", _strip_tags(html)).lower()
        if cta.lower() not in normalized_html:
            _add_issue(
                issues,
                "critical",
                "cta_not_rendered",
                "CTA do metadado não aparece no HTML renderizado.",
                25,
            )
        elif not re.search(rf"<(a|button)[^>]*>[^<]*{re.escape(cta)}", html, re.IGNORECASE):
            _add_issue(
                issues,
                "warning",
                "cta_not_button_like",
                "CTA aparece no texto, mas não como botão/link claro.",
                8,
            )

    headline = str(creative.get("headline", "")).strip()
    if len(headline) > 90:
        _add_issue(
            issues,
            "warning",
            "headline_too_long_visual",
            "Headline longa demais para layout estável de feed/story.",
            10,
        )

    if lower_html.count("object-fit: cover") and "object-position" not in lower_html:
        _add_issue(
            issues,
            "info",
            "cover_without_focal_point",
            "Imagem usa object-fit: cover sem ponto focal definido.",
            4,
        )

    path = creative.get("file") or creative.get("filepath")
    rendered_report = None
    if path and os.path.exists(path):
        width, height = _resolve_viewport(creative, html)
        rendered_report = evaluate_rendered_layout(path, width=width, height=height)
        if str(creative.get("format", "")).lower() == "landing":
            rendered_report = {
                **rendered_report,
                "issues": [
                    issue for issue in rendered_report.get("issues", [])
                    if issue.get("code") not in {"vertical_overflow", "element_outside_viewport"}
                ],
            }
        issues.extend(rendered_report.get("issues", []))

    total_penalty = sum(issue["penalty"] for issue in issues)
    score = max(0, min(100, 100 - total_penalty))
    status = "pass"
    if any(issue["severity"] == "critical" for issue in issues) or score < 70:
        status = "fail"
    elif issues:
        status = "review"

    return {
        "score": score,
        "status": status,
        "issues": issues,
        "source": "static_html+rendered_layout" if rendered_report else "static_html",
        "rendered": rendered_report,
    }
