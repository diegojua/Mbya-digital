import os
import re
import json

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "jarvis_agency_os", "config")

def _load_config(filename):
    path = os.path.join(CONFIG_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _resolve_design_state(niche: str, states_config: dict) -> tuple:
    """
    Resolve o design state psicológico baseado no nicho.
    Retorna (state_key, state_data).
    """
    niche_lower = niche.lower()
    for state_key, state_data in states_config.get("states", {}).items():
        for keyword in state_data.get("niches", []):
            if keyword in niche_lower:
                return state_key, state_data

    fallback = states_config.get("fallback_state", "authority")
    return fallback, states_config.get("states", {}).get(fallback, {})

def process_briefing(workspace_dir: str):
    """
    Lê o briefing.txt, extrai metadados, resolve o design state psicológico
    e retorna o contexto unificado com tokens atômicos.
    """
    briefing_path = os.path.join(workspace_dir, "briefing.txt")
    if not os.path.exists(briefing_path):
        return {"error": "briefing.txt não encontrado"}

    with open(briefing_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extração dinâmica de metadados
    metadata = {}
    for line in content.split('\n'):
        match = re.match(r'^([^:]+):\s*(.*)$', line)
        if match:
            metadata[match.group(1).strip().lower()] = match.group(2).strip()

    client_name = metadata.get("cliente", "Cliente Geral")
    niche = metadata.get("nicho", "geral").lower()
    objective = metadata.get("objetivo", "Reconhecimento de Marca")
    details = metadata.get("detalhes", "")
    whatsapp = metadata.get("whatsapp", "5587999999999")
    location = metadata.get("localização", metadata.get("localizacao", "Brasil"))
    logo_text = metadata.get("logo_texto", client_name)
    logo_icon = metadata.get("logo_icone", "✦")
    logo_sub = metadata.get("logo_subtitulo", niche)

    # Carregar configs
    states_config = _load_config("design_states.json")
    dna_config = _load_config("brand_dna_v2.json")
    constraints_config = _load_config("constraints.json")

    # Resolver design state
    state_key, state_data = _resolve_design_state(niche, states_config)

    # Construir paleta a partir do design state
    palette = {
        "bg_primary": state_data.get("bg_primary", "#050b11"),
        "bg_card": state_data.get("bg_card", "#08111c"),
        "text_primary": state_data.get("text_primary", "#ffffff"),
        "text_muted": state_data.get("text_muted", "#8fa0b0"),
        "accent": state_data.get("accent", "#d9a752"),
        "accent_glow": state_data.get("accent_glow", "rgba(217,167,82,0.35)"),
        "border_color": state_data.get("border_color", "rgba(217,167,82,0.15)")
    }

    # Mapeamento de keywords por nicho para copy
    niche_keywords = {
        "educa": ["educação", "reforço", "pedagogia", "aprendizado", "crianças"],
        "clinica": ["saúde", "bem-estar", "consulta", "tratamento", "atendimento"],
        "odonto": ["sorriso", "implante", "alinhador", "odontologia", "dente"],
        "comida": ["sabor", "gastronomia", "receitas", "delicioso", "artesanal"],
        "padaria": ["pão", "fermentação", "forno", "massa", "artesanal"],
        "finan": ["finanças", "investimento", "retorno", "rendimento", "cripto"],
    }
    keywords = ["marketing", "conversão", "leads", "resultados"]
    for key, words in niche_keywords.items():
        if key in niche:
            keywords = words
            break

    return {
        "status": "success",
        "context_graph": {
            "client_name": client_name,
            "niche": niche,
            "objective": objective,
            "details": details,
            "whatsapp": whatsapp,
            "location": location,
            "logo_text": logo_text,
            "logo_icon": logo_icon,
            "logo_sub": logo_sub,
            "extracted_keywords": keywords,
            "palette": palette,
            "design_state": state_key,
            "design_state_config": state_data,
            "typography": dna_config.get("typography", {}),
            "composition": dna_config.get("composition", {}),
            "constraints": constraints_config,
            "raw_text": content
        }
    }
