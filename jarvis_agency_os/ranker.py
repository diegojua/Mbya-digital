"""
Creative Ranker — Scoring automático em 6 dimensões.
Avalia criativos gerados e retorna os top N para aprovação humana.
"""
import json
import os

CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")


def _load_ranker_config():
    path = os.path.join(CONFIG_DIR, "creative_ranker.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _load_constraints():
    path = os.path.join(CONFIG_DIR, "constraints.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _score_legibility(creative: dict) -> float:
    """Avalia legibilidade baseada em presença de headline e body text."""
    score = 0.0
    headline = creative.get("headline", "")
    if len(headline) > 10 and len(headline) <= 60:
        score += 50  # Headline adequado
    elif len(headline) > 0:
        score += 25
    if creative.get("cta"):
        score += 30  # CTA presente
    if len(creative.get("headline", "").split()) >= 3:
        score += 20  # Headline com profundidade
    return min(score, 100)


def _score_hierarchy(creative: dict) -> float:
    """Avalia hierarquia visual: headline > body > cta diferenciados."""
    score = 0.0
    h = creative.get("headline", "")
    cta = creative.get("cta", "")
    if h and cta and h != cta:
        score += 60
    if creative.get("blueprint"):
        score += 40  # Blueprint garante hierarquia estrutural
    return min(score, 100)


def _score_cta_visibility(creative: dict) -> float:
    """Avalia visibilidade do CTA."""
    score = 0.0
    cta = creative.get("cta", "")
    if cta:
        score += 40
        if len(cta) <= 25:
            score += 30
        # CTA com verbo de ação
        action_verbs = ["agendar", "reservar", "falar", "garantir", "começar", "saiba"]
        if any(v in cta.lower() for v in action_verbs):
            score += 30
    return min(score, 100)


def _score_constraint_compliance(creative: dict) -> float:
    """Verifica compliance com constraints.json."""
    constraints = _load_constraints()
    rules = constraints.get("mandatory_rules", {}).get("content", {})
    score = 100.0
    penalties = 0

    headline = creative.get("headline", "")
    cta = creative.get("cta", "")

    if len(headline) > rules.get("headline_max_chars", 60):
        penalties += 25
    if len(cta) > rules.get("cta_max_chars", 25):
        penalties += 25

    forbidden = constraints.get("mandatory_rules", {}).get("content", {}).get("forbidden_cta_words", [])
    for word in forbidden:
        if word.lower() in cta.lower():
            penalties += 25

    return max(score - penalties, 0)


def _score_state_alignment(creative: dict) -> float:
    """Avalia se o criativo está alinhado com o design state."""
    if creative.get("design_state"):
        return 100.0  # Blueprint foi selecionado pelo design state
    return 50.0


def _score_batch_diversity(creative: dict, batch: list, index: int) -> float:
    """Avalia diversidade: blueprint diferente dos siblings."""
    if not batch or index == 0:
        return 100.0

    my_bp = creative.get("blueprint", "")
    others = [c.get("blueprint", "") for i, c in enumerate(batch) if i != index]

    if my_bp not in others:
        return 100.0  # Totalmente diferente
    elif others.count(my_bp) == 1:
        return 60.0   # Um repetido
    return 30.0  # Muito repetido


def rank_creatives(creatives: list, top_n: int = 2) -> dict:
    """
    Rankeia um batch de criativos e retorna os top N.
    """
    config = _load_ranker_config()
    dimensions = config.get("dimensions", {})
    scoring = config.get("scoring", {})

    scored = []
    for i, creative in enumerate(creatives):
        scores = {
            "legibility": _score_legibility(creative) * dimensions.get("legibility", {}).get("weight", 0.2),
            "hierarchy": _score_hierarchy(creative) * dimensions.get("hierarchy", {}).get("weight", 0.2),
            "cta_visibility": _score_cta_visibility(creative) * dimensions.get("cta_visibility", {}).get("weight", 0.2),
            "constraint_compliance": _score_constraint_compliance(creative) * dimensions.get("constraint_compliance", {}).get("weight", 0.15),
            "design_state_alignment": _score_state_alignment(creative) * dimensions.get("design_state_alignment", {}).get("weight", 0.15),
            "batch_diversity": _score_batch_diversity(creative, creatives, i) * dimensions.get("batch_diversity", {}).get("weight", 0.1),
        }
        total = sum(scores.values())
        creative["score"] = round(total, 1)
        creative["score_breakdown"] = {k: round(v, 1) for k, v in scores.items()}

        # Determine action
        threshold_approve = scoring.get("auto_approve_threshold", 85)
        threshold_review = scoring.get("human_review_threshold", 60)
        if total >= threshold_approve:
            creative["action"] = "auto_approve"
        elif total >= threshold_review:
            creative["action"] = "human_review"
        else:
            creative["action"] = "reject"

        scored.append(creative)

    # Sort by score descending
    scored.sort(key=lambda x: x["score"], reverse=True)

    return {
        "status": "success",
        "top": scored[:top_n],
        "all_scored": scored,
        "total_evaluated": len(scored)
    }


if __name__ == "__main__":
    # Demo test
    test_creatives = [
        {"headline": "Redescubra a segurança de sorrir", "cta": "Agendar Avaliação", "blueprint": "feed_split_editorial", "design_state": "authority"},
        {"headline": "Seu sorriso merece excelência", "cta": "Fale Conosco", "blueprint": "feed_fullbleed_overlay", "design_state": "authority"},
    ]
    result = rank_creatives(test_creatives)
    print(json.dumps(result, indent=2, ensure_ascii=False))
