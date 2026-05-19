"""
Visual Memory — Aprendizado contínuo com feedback loop.
Persiste resultados de campanhas e permite que o sistema evolua.
"""
import json
import os
from datetime import datetime

MEMORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory")
MEMORY_FILE = os.path.join(MEMORY_DIR, "visual_memory.json")


def _ensure_dir():
    os.makedirs(MEMORY_DIR, exist_ok=True)


def _load_memory() -> dict:
    _ensure_dir()
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"campaigns": [], "stats": {"total_generated": 0, "total_approved": 0, "avg_score": 0}}


def _save_memory(data: dict):
    _ensure_dir()
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def record_campaign(client: str, design_state: str, blueprint: str,
                    score: float, headline: str, approved: bool = None,
                    ctr: float = None, lead_cost: float = None):
    """Registra uma campanha na memória visual."""
    memory = _load_memory()
    entry = {
        "client": client,
        "design_state": design_state,
        "blueprint": blueprint,
        "score": score,
        "headline": headline,
        "human_approved": approved,
        "ctr": ctr,
        "lead_cost": lead_cost,
        "timestamp": datetime.now().isoformat()
    }
    memory["campaigns"].append(entry)

    # Update stats
    memory["stats"]["total_generated"] = len(memory["campaigns"])
    approved_count = sum(1 for c in memory["campaigns"] if c.get("human_approved") is True)
    memory["stats"]["total_approved"] = approved_count
    scores = [c["score"] for c in memory["campaigns"] if c.get("score")]
    memory["stats"]["avg_score"] = round(sum(scores) / len(scores), 1) if scores else 0

    _save_memory(memory)
    return entry


def get_best_blueprint_for_state(design_state: str) -> str:
    """Retorna o blueprint com melhor performance histórica para um design state."""
    memory = _load_memory()
    state_campaigns = [c for c in memory["campaigns"]
                       if c["design_state"] == design_state and c.get("human_approved") is True]

    if not state_campaigns:
        return None

    # Agrupa por blueprint e calcula média de score
    bp_scores = {}
    for c in state_campaigns:
        bp = c["blueprint"]
        if bp not in bp_scores:
            bp_scores[bp] = []
        bp_scores[bp].append(c["score"])

    best_bp = max(bp_scores, key=lambda bp: sum(bp_scores[bp]) / len(bp_scores[bp]))
    return best_bp


def get_stats() -> dict:
    """Retorna estatísticas globais da memória visual."""
    return _load_memory().get("stats", {})


def get_history(limit: int = 10) -> list:
    """Retorna últimas N campanhas."""
    memory = _load_memory()
    return memory["campaigns"][-limit:]
