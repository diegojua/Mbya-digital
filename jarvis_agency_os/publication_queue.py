"""
Publication Queue — preparo seguro de webhooks e agendamento local.

Esta camada cria payloads auditáveis para publicação, salva uma fila em JSONL
e só dispara HTTP quando um endpoint explícito é configurado.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests


DEFAULT_QUEUE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "workspace",
    "publication_queue.jsonl",
)


def _iso_now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _default_schedule() -> str:
    return (datetime.now() + timedelta(minutes=15)).isoformat(timespec="seconds")


def build_publication_payload(
    asset_path: str,
    caption: str,
    platform: str = "meta_ads",
    campaign_name: str = "campaign",
    scheduled_at: str | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Monta payload padrão para webhook/API de publicação."""
    if not asset_path:
        raise ValueError("asset_path is required")
    if not caption:
        raise ValueError("caption is required")

    return {
        "job_id": str(uuid.uuid4()),
        "status": "queued",
        "platform": platform,
        "campaign_name": campaign_name,
        "asset_path": asset_path,
        "caption": caption,
        "scheduled_at": scheduled_at or _default_schedule(),
        "metadata": metadata or {},
        "created_at": _iso_now(),
    }


def enqueue_publication(payload: Dict[str, Any], queue_path: str = DEFAULT_QUEUE_PATH) -> Dict[str, Any]:
    """Salva um job de publicação em fila JSONL local."""
    os.makedirs(os.path.dirname(queue_path), exist_ok=True)
    with open(queue_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")

    return {
        "status": "queued",
        "job_id": payload.get("job_id"),
        "queue_path": queue_path,
        "scheduled_at": payload.get("scheduled_at"),
    }


def load_publication_queue(queue_path: str = DEFAULT_QUEUE_PATH) -> List[Dict[str, Any]]:
    """Lê a fila local de publicações."""
    if not os.path.exists(queue_path):
        return []

    jobs = []
    with open(queue_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            jobs.append(json.loads(line))
    return jobs


def dispatch_webhook(payload: Dict[str, Any], endpoint: str | None = None,
                     token: str | None = None, timeout: int = 15,
                     dry_run: bool = True) -> Dict[str, Any]:
    """
    Dispara payload para um webhook externo.

    Por padrão roda em dry-run. Para envio real, passe endpoint e dry_run=False.
    """
    endpoint = endpoint or os.environ.get("JARVIS_PUBLICATION_WEBHOOK_URL")
    token = token or os.environ.get("JARVIS_PUBLICATION_WEBHOOK_TOKEN")

    if dry_run or not endpoint:
        return {
            "status": "dry_run",
            "endpoint_configured": bool(endpoint),
            "payload": payload,
        }

    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    response = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
    return {
        "status": "sent" if response.ok else "error",
        "status_code": response.status_code,
        "response": response.text[:1000],
        "job_id": payload.get("job_id"),
    }


def schedule_publication(
    asset_path: str,
    caption: str,
    platform: str = "meta_ads",
    campaign_name: str = "campaign",
    scheduled_at: str | None = None,
    metadata: Dict[str, Any] | None = None,
    queue_path: str = DEFAULT_QUEUE_PATH,
    dispatch_now: bool = False,
    dry_run: bool = True,
    endpoint: str | None = None,
) -> Dict[str, Any]:
    """Cria payload, salva na fila e opcionalmente dispara webhook."""
    payload = build_publication_payload(
        asset_path=asset_path,
        caption=caption,
        platform=platform,
        campaign_name=campaign_name,
        scheduled_at=scheduled_at,
        metadata=metadata,
    )
    queued = enqueue_publication(payload, queue_path=queue_path)
    result = {"status": "queued", "queued": queued, "payload": payload}
    if dispatch_now:
        result["dispatch"] = dispatch_webhook(
            payload,
            endpoint=endpoint,
            dry_run=dry_run,
        )
    return result
