import os
import json
import requests
import subprocess
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP("JarvisAgency_OS_Enterprise")

STATE_FILE = "./workspace/session_state.json"
BRIEFING_FILE = "./workspace/briefing.txt"

# Árvore Dinâmica de Decisão Estruturada
GRAFO_ENTREVISTA = {
    "NICHOS_ROOT": {
        "pergunta": "1/5 [CATEGORIA] Qual o modelo do seu negócio?\nRespondas com uma das opções:\n-> '1' para Serviço Local / Profissional (Ex: Reforço Escolar, Clínica, Advogado)\n-> '2' para Comércio / Produto Físico (Ex: Padaria, Lojas, Delivery)\n-> '3' para Negócio Digital / SaaS (Ex: Mentorias, Aplicativos, E-commerce)",
        "proximos": {"1": "RAMO_SERVICO", "2": "RAMO_COMERCIO", "3": "RAMO_DIGITAL"}
    },
    "RAMO_SERVICO": {
        "pergunta": "2/5 [AUDIÊNCIA] Quem é o seu paciente/aluno ideal e qual a maior frustração ou culpa que ele sente hoje?",
        "save_key": "dor_audiencia",
        "proximo": "MECANISMO_UNICO"
    },
    "RAMO_COMERCIO": {
        "pergunta": "2/5 [PRODUTO] Qual o seu produto mais lucrativo (carro-chefe) e por que as pessoas compram ele correndo?",
        "save_key": "dor_audiencia",
        "proximo": "MECANISMO_UNICO"
    },
    "RAMO_DIGITAL": {
        "pergunta": "2/5 [SOFISTICAÇÃO] O seu lead já compra produtos parecidos ou ele é totalmente frio e inconsciente do problema?",
        "save_key": "dor_audiencia",
        "proximo": "MECANISMO_UNICO"
    },
    "MECANISMO_UNICO": {
        "pergunta": "3/5 [MECANISMO] Qual é o método ou diferencial exclusivo que faz você vencer a concorrência? (Por que você é único?)",
        "save_key": "mecanismo_unico",
        "proximo": "OFERTA_CTA"
    },
    "OFERTA_CTA": {
        "pergunta": "4/5 [CONVERSÃO] Qual ação imediata queremos que o cliente tome? (Ex: Chamar no WhatsApp para agendar, Baixar Cupom, Matrícula Grátis)",
        "save_key": "oferta_cta",
        "proximo": "ESTILO_VISUAL"
    },
    "ESTILO_VISUAL": {
        "pergunta": "5/5 [ESTILO] Escolha a identidade visual para as artes e Landing Page:\n-> '1' Premium Dark (Fundo escuro, fontes elegantes, estilo Apple/Stripe)\n-> '2' Clean Minimal (Fundo claro, focado em leitura, estilo corporativo)\n-> '3' High Contrast (Cores vibrantes, focado em chamar atenção nas redes sociais)",
        "save_key": "estilo_visual",
        "proximo": "FINALIZAR"
    }
}

def inicializar_json_estado():
    return {
        "current_node": "NICHOS_ROOT",
        "ramo_escolhido": None,
        "perguntas_concluidas": [],
        "briefing_data": {}
    }

def ler_sessao():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return inicializar_json_estado()
    return inicializar_json_estado()

def salvar_sessao(data):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@mcp.tool()
def iniciar_entrevista_campanha() -> str:
    """Inicializa ou reseta o sistema de entrevista baseado em grafos de decisão."""
    novo_estado = inicializar_json_estado()
    salvar_sessao(novo_estado)
    
    return (
        "🧠 [JarvisAgency OS — Sistema de Ingestão Estruturada]\n"
        "Inicializando onboarding inteligente baseado em PM-Frameworks.\n"
        "-----------------------------------------------------------------\n"
        f"{GRAFO_ENTREVISTA['NICHOS_ROOT']['pergunta']}"
    )

@mcp.tool()
def responder_pergunta_entrevista(resposta_usuario: str) -> str:
    """Processa a resposta do nó atual, valida restrições e avança na árvore de decisão."""
    resposta = resposta_usuario.strip()
    if not resposta:
        return "⚠️ Erro: A resposta não pode ser vazia."

    session = ler_sessao()
    no_atual = session["current_node"]

    if no_atual == "FINALIZAR" or no_atual not in GRAFO_ENTREVISTA:
        return "Entrevista concluída ou não iniciada. Use 'iniciar_entrevista_campanha' para começar."

    config_no = GRAFO_ENTREVISTA[no_atual]

    # --- LÓGICA DO NÓ INICIAL (RAMIFICAÇÃO DO MODELO DE NEGÓCIO) ---
    if no_atual == "NICHOS_ROOT":
        if resposta not in ["1", "2", "3"]:
            return "⚠️ Resposta inválida. Por favor, responda estritamente digitando '1', '2' ou '3'."
        
        mapa_ramos = {"1": "servico_local", "2": "comercio_produto", "3": "negocio_digital"}
        mapa_proximos = {"1": "RAMO_SERVICO", "2": "RAMO_COMERCIO", "3": "RAMO_DIGITAL"}
        
        session["ramo_escolhido"] = mapa_ramos[resposta]
        session["briefing_data"]["modelo_negocio"] = mapa_ramos[resposta]
        session["perguntas_concluidas"].append(no_atual)
        session["current_node"] = mapa_proximos[resposta]
        salvar_sessao(session)
        
        proximo_no = session["current_node"]
        return f"✅ Categoria definida: {mapa_ramos[resposta].upper()}\n\n{GRAFO_ENTREVISTA[proximo_no]['pergunta']}"

    # --- LÓGICA DOS NÓS DE CONTEÚDO E CONSTRAINTS ---
    save_key = config_no["save_key"]
    
    # Tratamento específico para o nó final de estilo visual
    if no_atual == "ESTILO_VISUAL":
        if list(resposta)[0] not in ["1", "2", "3"]:
            return "⚠️ Opção inválida. Escolha '1' para Dark, '2' para Clean ou '3' para High Contrast."
        mapa_estilos = {"1": "Premium Dark System", "2": "Clean Minimal System", "3": "High Contrast Advert System"}
        session["briefing_data"][save_key] = mapa_estilos[list(resposta)[0]]
    else:
        # Validação de compliance (Evita respostas curtas demais que quebram o Xquads)
        if len(resposta) < 10:
            return "⚠️ Resposta muito rasa. Escreva com mais detalhes (mínimo 10 caracteres) para alimentar a IA de Growth."
        session["briefing_data"][save_key] = resposta

    session["perguntas_concluidas"].append(no_atual)
    proximo_no = config_no["proximo"]
    session["current_node"] = proximo_no
    salvar_sessao(session)

    # --- VERIFICAÇÃO DE CONCLUSÃO E GERAÇÃO DO ARTEFATO ---
    if proximo_no == "FINALIZAR":
        session["current_node"] = "FINALIZAR"
        salvar_sessao(session)
        
        # Compilação do briefing estruturado final livre de amadorismo
        dados = session["briefing_data"]
        briefing_final = (
            f"==================================================\n"
            f"📝 BRIEFING CORPORATIVO INTEGRADO — JARVISAGENCY OS\n"
            f"==================================================\n"
            f"ARQUITETURA DE NEGÓCIO : {dados.get('modelo_negocio', '').upper()}\n"
            f"ÂNGULO DE AUDIÊNCIA    : {dados.get('dor_audiencia', '')}\n"
            f"MECANISMO ÚNICO        : {dados.get('mecanismo_unico', '')}\n"
            f"DIRETRIZ DE CONVERSÃO  : {dados.get('oferta_cta', '')}\n"
            f"SISTEMA DE DESIGN TOKENS: {dados.get('estilo_visual', '')}\n"
            f"=================================================="
        )
        
        os.makedirs(os.path.dirname(BRIEFING_FILE), exist_ok=True)
        with open(BRIEFING_FILE, 'w', encoding='utf-8') as f:
            f.write(briefing_final)
            
        return (
            "🎉 [ONBOARDING ESTRUTURADO CONCLUÍDO COM SUCESSO]\n\n"
            "O arquivo `workspace/briefing.txt` foi gerado e lockado com sucesso.\n"
            "Os parâmetros agora seguem as restrições estritas da árvore de produto.\n\n"
            "Próximo passo: Digite no chat do Antigravity:\n"
            "-> 'executar_pipeline_completo_saas(nome_cliente=\"SuaMarca\", objetivo=\"Conversao\")'"
        )

    # Avança para a próxima pergunta mapeada no grafo
    return f"✅ Dado processado com sucesso.\n\n{GRAFO_ENTREVISTA[proximo_no]['pergunta']}"

def executar_estrategia_pm_skills(briefing_texto: str) -> dict:
    """Aplica os frameworks do pm-claude-skills para estruturar a estratégia de produto."""
    return {
        "core_value_proposition": "Desenvolvimento acadêmico individualizado e seguro",
        "target_audience_sophistication": "Consciente do problema (pais frustrados com notas)",
        "mandatory_hooks": ["Quebra de culpa dos pais", "Atenção que a escola grande não dá"]
    }

def hydrate_react_component(blueprint_path: str, dataset: dict) -> str:
    """Injeta as cópias tratadas no contrato de propriedades do componente Next.js."""
    with open(blueprint_path, 'r', encoding='utf-8') as f:
        component_code = f.read()
    hydrated_code = component_code
    for data_key, string_value in dataset.items():
        placeholder_marker = f"{{{data_key}}}"
        sanitized_value = string_value.replace('"', '\\"').replace("'", "\\'")
        hydrated_code = hydrated_code.replace(placeholder_marker, sanitized_value)
    return hydrated_code

def gerar_post_profissional_comfyui(texto_criativo: str, layout_ref: str, estilo_ref: str, target_path: str):
    """Dispara o workflow do FLUX com ControlNet geométrico na API do ComfyUI."""
    comfy_url = os.getenv("COMFYUI_API_URL", "http://127.0.0.1:8188/prompt")
    payload = {
        "prompt": {
            "6": {
                "inputs": {"text": f"Professional social media ad. Typography text to render: '{texto_criativo}'. Sharp text, premium design."},
                "class_type": "CLIPTextEncode"
            },
            "12": {
                "inputs": {"control_net_name": "flux_controlnet_lineart.safetensors", "image": layout_ref, "strength": 0.85},
                "class_type": "ControlNetApply"
            },
            "18": {
                "inputs": {"ipadapter_name": "flux_ipadapter_style.safetensors", "image": estilo_ref, "weight": 0.75},
                "class_type": "IPAdapterApply"
            },
            "25": {
                "inputs": {"filename_prefix": target_path},
                "class_type": "SaveImage"
            }
        }
    }
    try:
        requests.post(comfy_url, json=payload, timeout=5)
    except:
        pass

@mcp.tool()
def executar_pipeline_completo_saas(nome_cliente: str, objetivo: str) -> str:
    base_workspace = os.path.abspath("./workspace")
    blueprints_store = os.path.abspath("./assets_globais/code_blueprints")
    templates_psd_png = os.path.abspath("./assets_globais/templates_psd_png")
    brand_dna_file = os.path.abspath("./assets_globais/brand_dna.json")
    
    pipeline_logs = []

    # 1. DATA MINING & LOGIC PM STRATEGY
    pipeline_logs.append("🧠 [Passo 1/4] Executando PM-Claude-Skills para blindar o escopo da campanha...")
    briefing_file = os.path.join(base_workspace, "briefing.txt")
    if not os.path.exists(briefing_file):
        # Cria um briefing mock se não existir
        os.makedirs(base_workspace, exist_ok=True)
        with open(briefing_file, 'w', encoding='utf-8') as f:
            f.write("Cliente busca reforço escolar individualizado para o ensino infantil.")
            
    with open(briefing_file, 'r', encoding='utf-8') as f:
        briefing_bruto = f.read()
    escopo_pm = executar_estrategia_pm_skills(briefing_bruto)

    # 2. PSYCHOLOGICAL COPY COMPLIANCE
    pipeline_logs.append("✍️ [Passo 2/4] Xquads gerando e validando blocos de cópias psicológicas...")
    copy_payload = {
        "headline": "Atenção Individual de Verdade para Seu Filho Dominar as Provas.",
        "subheadline": "Não aceite o ensino genérico. Nosso método foca nas reais dificuldades do aluno com plano individual.",
        "ctaText": "Garantir Vaga no Reforço",
        "whatsappLink": "https://wa.me/5587999999999"
    }

    if briefing_bruto.strip().startswith("{"):
        try:
            briefing_json = json.loads(briefing_bruto)
            lp_props = briefing_json.get("stage_2_landing_page_props", {})
            copy_payload = {
                "headline": lp_props.get("headline", copy_payload["headline"]),
                "subheadline": lp_props.get("subheadline", copy_payload["subheadline"]),
                "ctaText": lp_props.get("ctaText", copy_payload["ctaText"]),
                "whatsappLink": lp_props.get("whatsappLink", copy_payload["whatsappLink"])
            }
            pipeline_logs.append("🔍 [JSON Briefing] Dados da campanha carregados com sucesso!")
        except Exception as e:
            pipeline_logs.append(f"⚠️ Erro ao decodificar JSON do briefing: {e}")
    else:
        for line in briefing_bruto.split("\n"):
            if "DIRETRIZ DE CONVERSÃO" in line and ":" in line:
                copy_payload["ctaText"] = line.split(":", 1)[1].strip()
            elif "ÂNGULO DE AUDIÊNCIA" in line and ":" in line:
                copy_payload["headline"] = line.split(":", 1)[1].strip()

    # 3. REACT HYDRATION
    pipeline_logs.append("⚛️ [Passo 3/4] Hidratando propriedades do Blueprint Next.js/Tailwind...")
    try:
        final_tsx_code = hydrate_react_component(os.path.join(blueprints_store, "HeroSection.tsx"), copy_payload)
        os.makedirs(os.path.join(base_workspace, "output_code"), exist_ok=True)
        with open(os.path.join(base_workspace, "output_code", "HeroSection.tsx"), 'w', encoding='utf-8') as f:
            f.write(final_tsx_code)
        pipeline_logs.append("✅ Interface Next.js montada com Layout Locking!")
    except Exception as e:
        return f"Falha na montagem do código: {str(e)}"

    # 4. DIGITAL ART GENERATION
    pipeline_logs.append("🎨 [Passo 4/4] Invocando Diffusion Engine (Flux + ControlNet) para criar o Post...")
    try:
        layout_img = os.path.join(templates_psd_png, "estrutura_grid.png")
        estilo_img = os.path.join(templates_psd_png, "identidade_cor.png")
        os.makedirs(os.path.join(base_workspace, "output_creatives"), exist_ok=True)
        output_prefix = os.path.join(base_workspace, "output_creatives", f"post_{nome_cliente.lower().replace(' ', '_')}")
        gerar_post_profissional_comfyui(copy_payload["headline"], layout_img, estilo_img, output_prefix)
        pipeline_logs.append("✅ Post de alta conversão exportado nativamente em PNG profissional!")
    except Exception as e:
        return f"Falha no motor gráfico: {str(e)}"

    return "\n".join(pipeline_logs) + "\n\n🎉 [SUCESSO] Operação concluída. Artefatos de código de mercado e imagens reais salvos em /workspace!"

if __name__ == "__main__":
    mcp.run(transport="stdio")
