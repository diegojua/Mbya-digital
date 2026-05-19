import os
import json
import re
import subprocess
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Importando os módulos locais do ecossistema
from graphify.engine import process_briefing
from xquads.engine import generate_copy, fetch_psd_template
from deer_flow.engine import dispatch_for_approval, publish_to_instagram, deploy_typebot_flow

# Novas camadas determinísticas do Creative OS
from jarvis_agency_os.creative_engine import generate_creatives
from jarvis_agency_os.ranker import rank_creatives
from jarvis_agency_os.visual_memory import record_campaign
from jarvis_agency_os.renderer import render_html_to_png

load_dotenv()

# Inicializa o servidor FastMCP
mcp = FastMCP("jarvis_agency")

WORKSPACE_DIR = os.path.join(os.path.dirname(__file__), "workspace")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets_globais")
OPEN_DESIGN_PATH = os.environ.get("OPEN_DESIGN_PATH", "/home/diego/Documentos/Mbya Digital/open-design")
CATALOG_PATH = os.path.join(WORKSPACE_DIR, "asset_catalog.json")

def load_catalog():
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def open_design_inject(copy_data: dict, palette: str, niche: str, catalog: dict):
    """
    Realiza a injeção/hidratação estruturada dos dados no blueprint JSON de renderização do Next.js.
    """
    niche_key = next((k for k in catalog.keys() if k != "global_automation" and (niche.lower() in k or k in niche.lower())), None)
    
    template_data = {"_base_template": "default"}
    if niche_key and "page" in catalog[niche_key]:
        page_dir = os.path.join(ASSETS_DIR, "Templates", catalog[niche_key]["page"])
        print(f"[Open-Design] Mapeando template premium do diretório: {page_dir}")
        template_data["_base_template"] = page_dir
    else:
        print(f"[Open-Design] Nenhum template premium específico encontrado para '{niche}'. Usando fallback.")

    try:
        template_data["client_name"] = copy_data.get("client_name", "Nossa Empresa")
        template_data["niche"] = niche
        template_data["palette"] = palette
        template_data["hero"] = copy_data.get("hero", {})
        template_data["benefits"] = copy_data.get("benefits", [])
        template_data["testimonials"] = copy_data.get("testimonials", [])
        template_data["footer"] = copy_data.get("footer", {})
        
        output_path = os.path.join(WORKSPACE_DIR, "rendered_template.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)
            
        return {"status": "success", "asset_path": output_path}
    except Exception as e:
        return {"error": f"Falha no Open-Design JSON Parser: {str(e)}"}

@mcp.tool()
def executar_pipeline_completo_saas(nome_cliente: str, objetivo: str, nicho: str = "geral") -> str:
    """
    Pipeline JarvisAgency OS: Pesquisa Mercado (Graphify) -> Xquads (Copy) -> 
    Next.js Hydration (Landing Page) -> Creative Engine HTML Blueprint -> Playwright Render -> Ranker -> Visual Memory.
    """
    logs = []
    logs.append(f"🚀 Iniciando pipeline SaaS unificado para {nome_cliente} (Nicho: {nicho})...")

    # Atualizar o briefing.txt para guiar o motor
    briefing_path = os.path.join(WORKSPACE_DIR, "briefing.txt")
    with open(briefing_path, "w", encoding="utf-8") as f:
        f.write(f"Cliente: {nome_cliente}\n")
        f.write(f"Nicho: {nicho}\n")
        f.write(f"Objetivo: {objetivo}\n")
        f.write(f"Detalhes: Geração automatizada de alta conversão sob o padrão do Creative OS.\n")
        f.write(f"Localização: Petrolina e Juazeiro\n")
        f.write(f"Logo_icone: ✦\n")
        f.write(f"Logo_texto: {nome_cliente.upper()}\n")
        f.write(f"Logo_subtitulo: {nicho.lower()}\n")

    # 1. Geração de Variações de Criativos via HTML Blueprints
    logs.append("📦 [Passo 1/4] Disparando Creative Engine: Hidratando blueprints estruturais...")
    res_generation = generate_creatives(WORKSPACE_DIR)
    if "error" in res_generation:
        return f"❌ Erro na geração: {res_generation['error']}"
    
    generated = res_generation["generated"]
    logs.append(f"✅ {len(generated)} variações de criativos HTML criadas com sucesso.")

    # 2. Avaliação de Qualidade (Creative Ranker)
    logs.append("🏆 [Passo 2/4] Executando Creative Ranker: Avaliando legibilidade e hierarquia...")
    res_ranking = rank_creatives(generated, top_n=2)
    top_candidates = res_ranking["top"]
    
    logs.append("   Resultados da avaliação:")
    for c in res_ranking["all_scored"]:
        logs.append(f"   → Variação [{c['blueprint']}]: Score {c['score']} ({c['action']})")

    # 3. Renderização via Playwright do Melhor Candidato
    logs.append("📸 [Passo 3/4] Playwright Renderer: Gerando PNG final do criativo campeão...")
    best = top_candidates[0]
    out_png_name = f"final_{nome_cliente.lower().replace(' ', '_')}_{best['blueprint']}.png"
    out_png_path = os.path.join(WORKSPACE_DIR, out_png_name)
    
    render_res = render_html_to_png(best["file"], out_png_path)
    if render_res.get("status") == "success":
        logs.append(f"✅ Criativo campeão renderizado perfeitamente em PNG: {out_png_name}")
    else:
        logs.append(f"⚠️ Playwright Offline. O criativo HTML está disponível para visualização: {best['file']}")

    # 4. Gravação na Visual Memory
    logs.append("🧠 [Passo 4/4] Salvando aprendizado na Visual Memory...")
    record_campaign(
        client=nome_cliente,
        design_state=best["design_state"],
        blueprint=best["blueprint"],
        score=best["score"],
        headline=best["headline"],
        approved=best["action"] == "auto_approve"
    )

    return "\n".join(logs) + f"\n\n🎉 [SUCESSO] Campanha finalizada. Criativo campeão: {best['blueprint']} (Score: {best['score']})."

@mcp.tool()
def rodar_campanha_completa(nome_cliente: str, objetivo: str, nicho: str = "geral") -> str:
    """
    Inicia o fluxo completo de marketing do JarvisAgency MCP integrado ao novo Creative OS.
    """
    yield f"🚀 Iniciando campanha integrada JarvisAgency MCP para: {nome_cliente}..."
    
    # 1. Pipeline SaaS
    yield "📊 [1/4] Processando e gerando criativos baseados em Design States..."
    result_str = executar_pipeline_completo_saas(nome_cliente, objetivo, nicho)
    yield result_str

    # 2. Next.js Hydration (Landing Page)
    yield "🖌️ [2/4] Hydration: Preparando modelo estruturado da Landing Page..."
    catalog = load_catalog()
    graph_result = process_briefing(WORKSPACE_DIR)
    context = graph_result["context_graph"]
    copy_result = generate_copy(context, objetivo)
    copy_data = copy_result["copy_data"]

    design_result = open_design_inject(copy_data, context.get("palette", {}).get("accent", "#d9a752"), nicho, catalog)
    if "error" in design_result:
        yield f"❌ Erro no Open-Design: {design_result['error']}"
        return

    # 3. Deer-Flow
    yield "🤖 [3/4] Deer-Flow: Instanciando Chatbot de Atendimento..."
    deploy_typebot_flow(nicho, catalog, ASSETS_DIR)
    
    yield "⏳ [4/4] Deer-Flow: Registrando aprovação da campanha no pipeline..."
    dispatch_for_approval(design_result["asset_path"], copy_data)
    
    yield "🎉 Campanha registrada com sucesso no pipeline de tráfego!"


if __name__ == "__main__":
    mcp.run()
