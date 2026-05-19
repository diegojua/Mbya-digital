import json
import os

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "jarvis_agency_os", "config")

def _load_constraints():
    path = os.path.join(CONFIG_DIR, "constraints.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def _validate_copy(text, max_chars, field_name):
    """Valida constraints de caracteres e retorna (text, warnings)."""
    warnings = []
    if len(text) > max_chars:
        warnings.append(f"[CONSTRAINT] {field_name} excede {max_chars} chars ({len(text)}). Truncado.")
        text = text[:max_chars-3] + "..."
    return text, warnings

# ── Banco de Copy por Design State ──────────────────────────────────────────

COPY_BANK = {
    "safety": {
        "angles": [
            {
                "headline_1": "Seu filho está com dificuldades na escola?",
                "headline_2": "Talvez ele só precise da atenção certa.",
                "body": "Na sala cheia, muitas crianças acabam ficando para trás. Ensinamos respeitando o ritmo único do seu pequeno.",
                "badge": "Atenção Individual",
                "checklist": ["Acompanhamento Individualizado", "Alfabetização & Letramento", "Autonomia de Estudo"],
                "cta": "Saiba Mais",
                "footer_cta": "Reserve a vaga dele com nossa equipe"
            },
            {
                "headline_1": "Notas baixas não definem a",
                "headline_2": "capacidade do seu filho.",
                "body": "Muitas vezes, a dificuldade não é falta de inteligência, mas sim a falta de um acompanhamento próximo, afetivo e especializado.",
                "badge": "Vagas Limitadas",
                "checklist": ["Apoio Escolar Personalizado", "Desenvolvimento da Autonomia", "Mais Segurança nas Provas"],
                "cta": "Falar Conosco",
                "footer_cta": "Devolva a alegria de aprender"
            },
            {
                "headline_1": "Aprender pode voltar a ser",
                "headline_2": "leve para seu filho.",
                "body": "Acompanhamento escolar individualizado da alfabetização ao 7º ano. Devolva a confiança nas lições diárias.",
                "badge": "Pedagogia Afetiva",
                "checklist": ["Reforço Escolar", "Atividades Lúdicas", "Suporte Emocional"],
                "cta": "Agendar Visita",
                "footer_cta": "Conheça nosso espaço"
            }
        ]
    },
    "authority": {
        "angles": [
            {
                "headline_1": "Redescubra a segurança de",
                "headline_2": "sorrir sem hesitar.",
                "body": "Tecnologia clínica digital 3D, sedação assistida indolor e reabilitações completas planejadas para seu absoluto conforto.",
                "badge": "Tecnologia Digital 3D",
                "checklist": ["Implantes de Carga Imediata", "Lentes de Contato Cerâmicas", "Sedação Assistida"],
                "cta": "Agendar Avaliação",
                "footer_cta": "Atendimento Premium de Verdade"
            },
            {
                "headline_1": "Seu sorriso merece a",
                "headline_2": "assinatura da excelência.",
                "body": "Com alinhadores invisíveis 3D e tratamento sob sedação suave, restaure sua autoestima no conforto de um spa.",
                "badge": "Odontologia Spa",
                "checklist": ["Alinhadores Invisíveis", "Odontologia Sem Dor"],
                "cta": "Fale Conosco",
                "footer_cta": "Conforto e precisão digital"
            }
        ]
    },
    "luxury": {
        "angles": [
            {
                "headline_1": "Pão de Verdade.",
                "headline_2": "Fermentado por 48h.",
                "body": "Alimentação limpa, respeito ao tempo e ingredientes puros. Conheça a verdadeira fermentação ancestral.",
                "badge": "Fornada Quente",
                "checklist": ["Trigo Importado", "Sem Químicos", "Assado 7x ao Dia"],
                "cta": "Reservar Fornada",
                "footer_cta": "Reservas limitadas via WhatsApp"
            },
            {
                "headline_1": "O Sabor do Pão de Verdade,",
                "headline_2": "Assado Sete Vezes Ao Dia.",
                "body": "Fermentação natural de 48 horas e ingredientes puros. Mude sua relação com o pão de cada dia.",
                "badge": "Fermentação Natural",
                "checklist": ["Trigo Rígido", "Tempo Lento", "Forno de Pedra"],
                "cta": "Garantir Lote",
                "footer_cta": "Tiragem diária limitada"
            }
        ]
    },
    "urgency": {
        "angles": [
            {
                "headline_1": "Últimas vagas para",
                "headline_2": "transformar seus resultados.",
                "body": "Não perca a oportunidade de escalar seu negócio com um método testado e comprovado.",
                "badge": "Oferta Limitada",
                "checklist": ["Resultados em 30 dias", "Suporte Dedicado", "Garantia Total"],
                "cta": "Garantir Vaga",
                "footer_cta": "Vagas encerrando em breve"
            }
        ]
    },
    "educational": {
        "angles": [
            {
                "headline_1": "Domine as habilidades que",
                "headline_2": "o mercado realmente valoriza.",
                "body": "Metodologia prática com projetos reais. Aprenda fazendo, não apenas assistindo.",
                "badge": "Método Prático",
                "checklist": ["Projetos Reais", "Mentoria Individual", "Certificação"],
                "cta": "Começar Agora",
                "footer_cta": "Próxima turma com vagas abertas"
            }
        ]
    },
    "legal": {
        "angles": [
            {
                "headline_1": "Proteção jurídica sólida para",
                "headline_2": "blindar a sua empresa.",
                "body": "Assessoria empresarial preventiva e gestão estratégica de riscos. Evite litígios dispendiosos com soluções sob medida.",
                "badge": "Assessoria Preventiva",
                "checklist": ["Auditoria de Contratos", "Blindagem Patrimonial", "Defesa Trabalhista"],
                "cta": "Falar com Advogado",
                "footer_cta": "Consulte nosso corpo jurídico"
            },
            {
                "headline_1": "Decisões estratégicas seguras,",
                "headline_2": "resultados sustentáveis.",
                "body": "Atuação especializada em direito societário, contratos e planejamento tributário. Garanta compliance e segurança corporativa.",
                "badge": "Direito Corporativo",
                "checklist": ["Planejamento Tributário", "Direito Societário", "Compliance Geral"],
                "cta": "Agendar Consulta",
                "footer_cta": "Segurança e sigilo profissional"
            }
        ]
    }
}


def generate_copy(context_graph: dict, objective: str):
    """
    Gera copys baseadas no design state psicológico.
    Retorna N ângulos de copy para o Creative Ranker avaliar.
    """
    client_name = context_graph.get("client_name", "Nossa Empresa")
    niche = context_graph.get("niche", "geral")
    design_state = context_graph.get("design_state", "authority")
    details = context_graph.get("details", "")
    constraints = _load_constraints()

    max_headline = constraints.get("mandatory_rules", {}).get("content", {}).get("headline_max_chars", 60)
    max_sub = constraints.get("mandatory_rules", {}).get("content", {}).get("subheadline_max_chars", 120)
    max_cta = constraints.get("mandatory_rules", {}).get("content", {}).get("cta_max_chars", 25)

    # Buscar ângulos do banco para o design state
    state_bank = COPY_BANK.get(design_state, COPY_BANK.get("authority"))
    angles = state_bank.get("angles", [])

    all_warnings = []
    validated_angles = []

    for angle in angles:
        h1 = angle["headline_1"]
        h2 = angle["headline_2"]
        body = angle["body"]
        cta = angle["cta"]

        # Substituir nome do cliente onde fizer sentido
        body = body.replace("{{CLIENT_NAME}}", client_name)

        # Validar constraints
        h1, w1 = _validate_copy(h1, max_headline, "headline_1")
        h2, w2 = _validate_copy(h2, max_headline, "headline_2")
        cta, w3 = _validate_copy(cta, max_cta, "cta")
        all_warnings.extend(w1 + w2 + w3)

        validated_angles.append({
            "headline_1": h1,
            "headline_2": h2,
            "body": body,
            "badge": angle.get("badge", ""),
            "checklist": angle.get("checklist", []),
            "cta": cta,
            "footer_cta": angle.get("footer_cta", ""),
            "design_state": design_state
        })

    # Legacy compat: build hero dict from first angle
    first = validated_angles[0] if validated_angles else {}
    copy_data = {
        "client_name": client_name,
        "niche": niche,
        "objective": objective,
        "design_state": design_state,
        "hero": {
            "headline": f"{first.get('headline_1', '')} {first.get('headline_2', '')}".strip(),
            "subheadline": first.get("body", ""),
            "cta": first.get("cta", "Falar com Especialista")
        },
        "angles": validated_angles,
        "benefits": [{"title": item, "desc": ""} for item in first.get("checklist", [])],
        "testimonials": [],
        "footer": {
            "disclaimer": f"Administrado por {client_name}. Sujeito a termos de uso.",
            "copyright": f"© 2026 {client_name}. Design por JarvisAgency."
        }
    }

    return {
        "status": "success",
        "copy_data": copy_data,
        "angles_count": len(validated_angles),
        "warnings": all_warnings
    }


def fetch_psd_template(niche: str, catalog_data: dict, assets_dir: str):
    """Localiza PSD correspondente ao nicho no catálogo."""
    niche = niche.lower()
    niche_key = next((k for k in catalog_data.keys() if k != "global_automation" and (niche in k or k in niche)), None)

    if not niche_key or "psd" not in catalog_data.get(niche_key, {}):
        return {"status": "warning", "message": f"Nenhum PSD para '{niche}'. Usando template genérico."}

    return {
        "status": "success",
        "psd_pack": catalog_data[niche_key]["psd"],
        "message": "Artes PSD disponibilizadas."
    }
