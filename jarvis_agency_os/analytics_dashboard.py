"""
Analytics Dashboard — resumo estático da Visual Memory v2.

Gera dados e HTML local para acompanhar performance de criativos, estados de
design, blueprints e experimentos A/B sem depender de serviços externos.
"""
from __future__ import annotations

import html
import json
import os
from datetime import datetime
from typing import Any, Dict, List

from jarvis_agency_os.visual_memory_v2 import get_memory


def _safe_number(value: Any, digits: int = 2) -> float:
    try:
        return round(float(value or 0), digits)
    except (TypeError, ValueError):
        return 0.0


def _safe_text(value: Any) -> str:
    return html.escape(str(value or "n/a"))


def _campaign_summary(row: Dict[str, Any]) -> Dict[str, Any]:
    impressions = int(row.get("impressions") or 0)
    conversions = int(row.get("conversions") or 0)
    spend = float(row.get("spend") or 0)
    return {
        "id": row.get("id"),
        "client": row.get("client"),
        "niche": row.get("niche"),
        "format": row.get("format"),
        "blueprint": row.get("blueprint"),
        "score": _safe_number(row.get("score"), 1),
        "visual_qa_status": row.get("visual_qa_status"),
        "human_approved": row.get("human_approved"),
        "experiment_id": row.get("experiment_id"),
        "variant_label": row.get("variant_label"),
        "impressions": impressions,
        "conversions": conversions,
        "conversion_rate": conversions / impressions if impressions > 0 else None,
        "cost_per_conversion": spend / conversions if conversions > 0 else row.get("lead_cost"),
        "file_path": row.get("file_path"),
    }


def build_dashboard_data(memory=None, limit: int = 8) -> Dict[str, Any]:
    """Monta o payload consolidado usado pelo HTML e por integrações futuras."""
    memory = memory or get_memory()
    history = memory.get_history(limit=200)
    experiment_ids = []
    for row in history:
        experiment_id = row.get("experiment_id")
        if experiment_id and experiment_id not in experiment_ids:
            experiment_ids.append(experiment_id)

    experiment_reports = [
        memory.get_experiment_report(experiment_id)
        for experiment_id in experiment_ids[:limit]
    ]

    return {
        "generated_at": datetime.now().isoformat(),
        "stats": memory.get_stats(),
        "performance_by_state": memory.get_performance_by_state(),
        "trending_blueprints": [
            {"blueprint": blueprint, "count": count, "avg_score": _safe_number(avg_score, 2)}
            for blueprint, count, avg_score in memory.get_trending_blueprints(limit=limit)
        ],
        "winning_creatives": [
            _campaign_summary(row)
            for row in memory.get_winning_creatives(limit=limit)
        ],
        "recent_creatives": [
            _campaign_summary(row)
            for row in history[:limit]
        ],
        "experiments": experiment_reports,
    }


def _metric_card(label: str, value: Any, hint: str = "") -> str:
    return (
        '<article class="metric">'
        f"<span>{_safe_text(label)}</span>"
        f"<strong>{_safe_text(value)}</strong>"
        f"<small>{_safe_text(hint)}</small>"
        "</article>"
    )


def _render_state_rows(states: Dict[str, Dict[str, Any]]) -> str:
    if not states:
        return '<tr><td colspan="5">Sem dados por estado ainda.</td></tr>'
    rows = []
    for state, data in states.items():
        rows.append(
            "<tr>"
            f"<td>{_safe_text(state)}</td>"
            f"<td>{data.get('total_generated', 0)}</td>"
            f"<td>{data.get('total_approved', 0)}</td>"
            f"<td>{_safe_number(data.get('avg_score'), 1)}</td>"
            f"<td>{_safe_number(data.get('avg_ctr'), 4)}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def _render_blueprints(items: List[Dict[str, Any]]) -> str:
    if not items:
        return '<li class="empty">Sem blueprints aprovados ainda.</li>'
    max_count = max((item.get("count") or 0) for item in items) or 1
    rows = []
    for item in items:
        width = int(((item.get("count") or 0) / max_count) * 100)
        rows.append(
            '<li class="blueprint-row">'
            f"<div><strong>{_safe_text(item.get('blueprint'))}</strong>"
            f"<span>{item.get('count', 0)} usos · score {_safe_number(item.get('avg_score'), 1)}</span></div>"
            f'<i style="width:{width}%"></i>'
            "</li>"
        )
    return "\n".join(rows)


def _render_creatives(items: List[Dict[str, Any]]) -> str:
    if not items:
        return '<tr><td colspan="6">Sem criativos registrados ainda.</td></tr>'
    rows = []
    for item in items:
        conversion = item.get("conversion_rate")
        rows.append(
            "<tr>"
            f"<td>{_safe_text(item.get('client'))}</td>"
            f"<td>{_safe_text(item.get('format'))}</td>"
            f"<td>{_safe_text(item.get('blueprint'))}</td>"
            f"<td>{_safe_number(item.get('score'), 1)}</td>"
            f"<td>{_safe_text(item.get('visual_qa_status'))}</td>"
            f"<td>{_safe_number(conversion * 100, 2) if conversion is not None else 'n/a'}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def _render_experiments(items: List[Dict[str, Any]]) -> str:
    if not items:
        return '<li class="empty">Sem experimentos A/B registrados ainda.</li>'
    rows = []
    for report in items:
        winner = report.get("winner") or {}
        significance = report.get("significance") or {}
        rows.append(
            "<li>"
            f"<strong>{_safe_text(report.get('experiment_id'))}</strong>"
            f"<span>{report.get('variant_count', 0)} variantes · vencedor {_safe_text(winner.get('variant_label'))} · "
            f"{_safe_text(significance.get('status'))}</span>"
            "</li>"
        )
    return "\n".join(rows)


def render_dashboard_html(data: Dict[str, Any]) -> str:
    """Renderiza o dashboard como HTML autocontido."""
    stats = data.get("stats", {})
    metrics = [
        _metric_card("Criativos", stats.get("total_generated", 0), "total gerado"),
        _metric_card("Aprovados", stats.get("total_approved", 0), f"{stats.get('approval_rate', 0)}% approval"),
        _metric_card("Score médio", stats.get("avg_score", 0), "ranking + QA"),
        _metric_card("CTR médio", stats.get("avg_ctr", 0), "mídia registrada"),
        _metric_card("CPL médio", stats.get("avg_lead_cost", 0), "custo por lead"),
    ]
    payload_json = json.dumps(data, ensure_ascii=False, indent=2, default=str)
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>JarvisAgency Analytics</title>
  <style>
    body {{ margin: 0; font-family: Inter, system-ui, sans-serif; background: #f7f8fb; color: #12213f; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 40px 24px; }}
    header {{ display: flex; justify-content: space-between; gap: 24px; align-items: end; margin-bottom: 28px; }}
    h1 {{ margin: 0; font-size: 34px; line-height: 1.05; }}
    h2 {{ margin: 0 0 16px; font-size: 19px; }}
    .stamp {{ color: #64748b; font-size: 14px; }}
    .grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-bottom: 18px; }}
    .metric, section {{ background: #fff; border: 1px solid #e3e8f2; border-radius: 8px; box-shadow: 0 14px 34px rgba(18,33,63,.06); }}
    .metric {{ padding: 18px; }}
    .metric span, .metric small {{ display: block; color: #64748b; font-size: 13px; }}
    .metric strong {{ display: block; margin: 8px 0 6px; font-size: 26px; }}
    .panels {{ display: grid; grid-template-columns: 1.05fr .95fr; gap: 18px; margin-top: 18px; }}
    section {{ padding: 20px; overflow: hidden; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ padding: 11px 9px; border-bottom: 1px solid #edf1f7; text-align: left; }}
    th {{ color: #64748b; font-size: 12px; text-transform: uppercase; }}
    ul {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; }}
    li {{ padding: 12px; border: 1px solid #edf1f7; border-radius: 8px; }}
    li span {{ display: block; margin-top: 4px; color: #64748b; font-size: 13px; }}
    .blueprint-row {{ position: relative; overflow: hidden; }}
    .blueprint-row div {{ position: relative; z-index: 1; }}
    .blueprint-row i {{ position: absolute; left: 0; bottom: 0; height: 4px; background: #ed2b7c; }}
    .empty {{ color: #64748b; }}
    details {{ margin-top: 18px; }}
    pre {{ overflow: auto; padding: 18px; background: #101827; color: #dbeafe; border-radius: 8px; font-size: 12px; }}
    @media (max-width: 900px) {{ .grid, .panels {{ grid-template-columns: 1fr; }} header {{ display: block; }} }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>JarvisAgency Analytics</h1>
        <p class="stamp">Gerado em {_safe_text(data.get('generated_at'))}</p>
      </div>
      <p class="stamp">Visual Memory v2 · SQLite</p>
    </header>
    <div class="grid">{''.join(metrics)}</div>
    <div class="panels">
      <section>
        <h2>Performance Por Estado</h2>
        <table><thead><tr><th>Estado</th><th>Total</th><th>Aprov.</th><th>Score</th><th>CTR</th></tr></thead>
        <tbody>{_render_state_rows(data.get('performance_by_state', {}))}</tbody></table>
      </section>
      <section>
        <h2>Blueprints Em Alta</h2>
        <ul>{_render_blueprints(data.get('trending_blueprints', []))}</ul>
      </section>
    </div>
    <div class="panels">
      <section>
        <h2>Criativos Vencedores</h2>
        <table><thead><tr><th>Cliente</th><th>Formato</th><th>Blueprint</th><th>Score</th><th>QA</th><th>Conv. %</th></tr></thead>
        <tbody>{_render_creatives(data.get('winning_creatives', []))}</tbody></table>
      </section>
      <section>
        <h2>Experimentos A/B</h2>
        <ul>{_render_experiments(data.get('experiments', []))}</ul>
      </section>
    </div>
    <details>
      <summary>Payload JSON</summary>
      <pre>{_safe_text(payload_json)}</pre>
    </details>
  </main>
</body>
</html>
"""


def write_dashboard(output_path: str, json_path: str | None = None, memory=None, limit: int = 8) -> Dict[str, Any]:
    """Gera HTML e, opcionalmente, JSON do dashboard."""
    data = build_dashboard_data(memory=memory, limit=limit)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(render_dashboard_html(data))

    if json_path:
        os.makedirs(os.path.dirname(json_path) or ".", exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    return {
        "status": "success",
        "html": output_path,
        "json": json_path,
        "stats": data.get("stats", {}),
        "generated_at": data.get("generated_at"),
    }
