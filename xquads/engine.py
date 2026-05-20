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
                "headline_1": "Autoridade começa com",
                "headline_2": "clareza na oferta.",
                "body": "Comunique valor, diferenciação e próximo passo com uma presença visual mais madura e preparada para conversão.",
                "badge": "Posicionamento premium",
                "checklist": ["Mensagem clara", "Design consistente", "CTA visível"],
                "cta": "Falar com especialista",
                "footer_cta": "Estratégia, identidade e performance trabalhando na mesma direção."
            },
            {
                "headline_1": "Transforme atenção em",
                "headline_2": "confiança de compra.",
                "body": "Uma comunicação premium reduz ruído, organiza a decisão do cliente e aumenta a percepção de valor da marca.",
                "badge": "Estratégia visual",
                "checklist": ["Hierarquia forte", "Prova de valor", "Experiência limpa"],
                "cta": "Começar agora",
                "footer_cta": "Criativos pensados para parecer marca, não template."
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
    "performance": {
        "angles": [
            {
                "headline_1": "Entre no tatame e",
                "headline_2": "supere seus limites.",
                "body": "Aulas de jiu-jitsu para iniciantes e avançados, com treino técnico, disciplina e acompanhamento próximo.",
                "badge": "Aula Experimental",
                "checklist": ["Defesa Pessoal", "Condicionamento Físico", "Turmas Iniciantes", "Treino Infantil e Adulto"],
                "cta": "Agendar Aula",
                "footer_cta": "Primeira aula experimental via WhatsApp"
            },
            {
                "headline_1": "Jiu-jitsu para ganhar",
                "headline_2": "confiança de verdade.",
                "body": "Aprenda técnica, controle emocional e força funcional em um ambiente seguro para todos os níveis.",
                "badge": "Vagas Abertas",
                "checklist": ["Professor Faixa Preta", "Ambiente Familiar", "Evolução por Graduação", "Treinos Semanais"],
                "cta": "Falar no WhatsApp",
                "footer_cta": "Turmas manhã, tarde e noite"
            },
            {
                "headline_1": "Seu próximo nível começa",
                "headline_2": "com uma queda no tatame.",
                "body": "Treinos guiados para desenvolver técnica, resistência e mentalidade competitiva sem perder segurança.",
                "badge": "Treino Guiado",
                "checklist": ["Base Técnica", "Preparação Física", "Disciplina", "Comunidade Forte"],
                "cta": "Reservar Vaga",
                "footer_cta": "Vagas limitadas por turma"
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

NICHE_COPY_OVERRIDES = {
    "pedagogia_infantil": {
        "match": ["educação infantil", "educacao infantil", "pedagog", "reforço", "reforco", "acompanhamento pedagógico", "acompanhamento pedagogico"],
        "angles": [
            {
                "headline_1": "Acompanhamento pedagógico é",
                "headline_2": "investir no futuro do seu filho.",
                "body": "Cada criança aprende de um jeito. O suporte certo transforma dificuldades em conquistas, com acolhimento, método e rotina.",
                "badge": "Desenvolvimento infantil",
                "checklist": ["Plano individual de aprendizagem", "Mais foco e autonomia", "Evolução acompanhada de perto"],
                "cta": "Fale com nossa equipe",
                "footer_cta": "Converse com a equipe Amar e entenda o melhor caminho para o seu filho."
            },
            {
                "headline_1": "Seu filho está com",
                "headline_2": "dificuldades na escola?",
                "body": "O acompanhamento pedagógico ajuda a identificar obstáculos, fortalecer a confiança e tornar o aprendizado mais leve.",
                "badge": "Avaliação pedagógica",
                "checklist": ["Mais confiança", "Melhor aprendizado", "Rotina de estudos"],
                "cta": "Agende avaliação",
                "footer_cta": "Agende uma avaliação e receba orientação personalizada."
            },
            {
                "headline_1": "Dificuldade escolar não precisa",
                "headline_2": "virar insegurança.",
                "body": "Com orientação certa, a criança ganha repertório, autonomia e segurança para avançar no próprio ritmo.",
                "badge": "Aprender com leveza",
                "checklist": ["Apoio individualizado", "Estratégia por idade", "Família mais orientada"],
                "cta": "Falar no WhatsApp",
                "footer_cta": "Atendimento acolhedor para famílias que querem agir cedo."
            }
        ]
    },
    "legal_premium": {
        "match": ["advocacia", "advogado", "juridic", "direito", "legal"],
        "angles": [
            {
                "headline_1": "Você conhece todos",
                "headline_2": "os seus direitos?",
                "body": "Atendimento jurídico especializado com estratégia, clareza e suporte personalizado para pessoas e empresas.",
                "badge": "Atendimento jurídico especializado",
                "checklist": ["Análise objetiva", "Estratégia personalizada", "Atendimento direto"],
                "cta": "Fale com um especialista",
                "footer_cta": "Consultoria jurídica para decisões trabalhistas, cíveis, empresariais e previdenciárias."
            },
            {
                "headline_1": "Proteja seus direitos",
                "headline_2": "antes de decidir.",
                "body": "Orientação jurídica clara para reduzir riscos, organizar próximos passos e agir com segurança.",
                "badge": "Estratégia e clareza",
                "checklist": ["Diagnóstico inicial", "Plano de ação", "Comunicação transparente"],
                "cta": "Agendar conversa",
                "footer_cta": "Atendimento digital e presencial com sigilo profissional."
            },
            {
                "headline_1": "Segurança jurídica para",
                "headline_2": "decisões importantes.",
                "body": "Suporte especializado para pessoas e empresas que precisam de uma resposta objetiva antes do problema crescer.",
                "badge": "Advocacia moderna",
                "checklist": ["Atendimento direto", "Análise de risco", "Suporte personalizado"],
                "cta": "Falar no WhatsApp",
                "footer_cta": "Equipe preparada para orientar seu próximo movimento."
            }
        ]
    },
    "odontology": {
        "match": ["odonto", "dent", "odontologia", "implante", "sorriso"],
        "angles": [
            {
                "headline_1": "Redescubra a segurança de",
                "headline_2": "sorrir sem hesitar.",
                "body": "Tecnologia clínica digital 3D, sedação assistida indolor e reabilitações completas planejadas para seu absoluto conforto.",
                "badge": "Tecnologia Digital 3D",
                "checklist": ["Implantes de Carga Imediata", "Lentes de Contato Cerâmicas", "Sedação Assistida"],
                "cta": "Agendar Avaliação",
                "footer_cta": "Atendimento premium de verdade"
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
    "jewelry": {
        "match": ["joia", "joias", "joalheria", "semijoia", "semi joia", "aliança", "alianca", "ouro", "prata"],
        "angles": [
            {
                "headline_1": "Joias que marcam",
                "headline_2": "momentos para sempre.",
                "body": "Coleções em ouro, prata e peças selecionadas para presentear com elegância, brilho e significado.",
                "badge": "Coleção Especial",
                "checklist": ["Ouro e Prata", "Presentes Especiais", "Peças Selecionadas", "Atendimento Personalizado"],
                "cta": "Ver Coleção",
                "footer_cta": "Escolha sua peça pelo WhatsApp"
            },
            {
                "headline_1": "O presente certo tem",
                "headline_2": "brilho próprio.",
                "body": "Anéis, colares, pulseiras e brincos para transformar datas especiais em lembranças inesquecíveis.",
                "badge": "Presente Premium",
                "checklist": ["Embalagem Especial", "Opções para Ela", "Compra por WhatsApp", "Retirada na Loja"],
                "cta": "Escolher Presente",
                "footer_cta": "Atendimento rápido para presentes"
            },
            {
                "headline_1": "Alianças para celebrar",
                "headline_2": "a história de vocês.",
                "body": "Modelos clássicos e modernos para noivado, casamento e renovação de votos, com acabamento impecável.",
                "badge": "Alianças",
                "checklist": ["Modelos Clássicos", "Design Moderno", "Acabamento Premium", "Consulta de Medidas"],
                "cta": "Consultar Modelos",
                "footer_cta": "Fale com nossa consultora"
            }
        ]
    }
}


def _split_headline(headline: str) -> tuple:
    """Divide headline longa em duas linhas equilibradas."""
    words = headline.strip().split()
    if len(words) <= 4:
        return headline.strip(), ""

    midpoint = max(2, len(words) // 2)
    return " ".join(words[:midpoint]), " ".join(words[midpoint:])


def _context_defaults_for_niche(niche: str) -> dict:
    """Defaults para briefing com headline/CTA explícitos, sem cair em texto jurídico genérico."""
    niche_lower = (niche or "").lower()
    if any(term in niche_lower for term in ["educação", "educacao", "pedagog", "reforço", "reforco", "infantil"]):
        return {
            "body": "Acompanhamento pedagógico com acolhimento, método e suporte personalizado para fortalecer o aprendizado da criança.",
            "badge": "Acompanhamento pedagógico",
            "checklist": ["Plano individual", "Mais foco e autonomia", "Evolução acompanhada"],
            "footer_cta": "Converse com a equipe e entenda o melhor caminho para seu filho.",
        }
    if any(term in niche_lower for term in ["advocacia", "advogado", "juridic", "direito", "legal"]):
        return {
            "body": "Atendimento jurídico especializado com estratégia, clareza e suporte personalizado.",
            "badge": "Atendimento jurídico especializado",
            "checklist": ["Análise objetiva", "Estratégia personalizada", "Atendimento direto"],
            "footer_cta": "Consultoria jurídica para decisões trabalhistas, cíveis, empresariais e previdenciárias.",
        }
    return {
        "body": "Atendimento especializado com clareza, método e acompanhamento próximo.",
        "badge": "Atendimento especializado",
        "checklist": ["Diagnóstico claro", "Plano personalizado", "Suporte próximo"],
        "footer_cta": "Converse com nossa equipe e entenda o melhor caminho.",
    }


def _custom_angle_from_context(context_graph: dict) -> dict:
    headline = context_graph.get("headline", "").strip()
    subtext = context_graph.get("subtext", "").strip()
    cta = context_graph.get("cta", "").strip()
    if not headline and not subtext and not cta:
        return {}

    defaults = _context_defaults_for_niche(context_graph.get("niche", ""))
    h1, h2 = _split_headline(headline or "Estratégia clara para avançar com confiança.")
    return {
        "headline_1": h1,
        "headline_2": h2,
        "body": subtext or defaults["body"],
        "badge": context_graph.get("badge") or defaults["badge"],
        "checklist": defaults["checklist"],
        "cta": cta or "Fale com um especialista",
        "footer_cta": context_graph.get("details") or defaults["footer_cta"]
    }


def _get_niche_angles(niche: str):
    """Retorna ângulos específicos quando o nicho pede copy dedicada."""
    niche_lower = niche.lower()
    for override in NICHE_COPY_OVERRIDES.values():
        if any(term in niche_lower for term in override["match"]):
            return override["angles"]
    return None


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

    custom_angle = _custom_angle_from_context(context_graph)

    # Buscar copy explícita do briefing, depois ângulos por nicho; se não houver, usa o design state.
    niche_angles = _get_niche_angles(niche)
    state_bank = COPY_BANK.get(design_state, COPY_BANK.get("authority"))
    angles = [custom_angle] if custom_angle else niche_angles or state_bank.get("angles", [])

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
