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
from jarvis_agency_os.landing_engine import generate_landing_page
from jarvis_agency_os.asset_catalog import match_catalog_entry
from jarvis_agency_os.pipeline import run_campaign_pipeline

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

def open_design_inject(copy_data: dict, palette: str, niche: str, catalog: dict, context: dict = None):
    """
    Realiza a injeção/hidratação estruturada dos dados no blueprint JSON de renderização do Next.js.
    """
    catalog_match = match_catalog_entry(niche, catalog, asset_type="page")

    template_data = {"_base_template": "default", "catalog_match": catalog_match}
    if catalog_match.get("status") == "matched":
        page_dir = catalog_match["absolute_path"]
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

        landing = generate_landing_page(
            workspace_dir=WORKSPACE_DIR,
            context=context or {"niche": niche, "palette": {"accent": palette}},
            copy_data=copy_data,
            catalog_match=catalog_match,
        )

        return {
            "status": "success",
            "asset_path": landing["file"],
            "manifest_path": landing["manifest"],
            "legacy_json_path": output_path,
            "visual_qa": landing.get("visual_qa"),
        }
    except Exception as e:
        return {"error": f"Falha no Open-Design JSON Parser: {str(e)}"}

@mcp.tool()
def executar_pipeline_completo_saas(nome_cliente: str, objetivo: str, nicho: str = "geral",
                                    formatos: str = "feed") -> str:
    """
    Pipeline JarvisAgency OS: Pesquisa Mercado (Graphify) -> Xquads (Copy) ->
    Next.js Hydration (Landing Page) -> Creative Engine HTML Blueprint -> Playwright Render -> Ranker -> Visual Memory.
    """
    logs = []
    logs.append(f"🚀 Iniciando pipeline SaaS unificado para {nome_cliente} (Nicho: {nicho})...")

    result = run_campaign_pipeline(
        client_name=nome_cliente,
        objective=objetivo,
        niche=nicho,
        workspace_dir=WORKSPACE_DIR,
        formats=formatos,
        include_landing=True,
        render_winners=True,
    )
    if result.get("status") != "success":
        return f"❌ Erro no pipeline: {result.get('stage')} — {result.get('error')}"

    generation = result["generation"]
    ranking = result["ranking"]
    logs.append(f"✅ Briefing atualizado: {result['briefing_path']}")
    logs.append(f"🧪 Experimento A/B: {result['experiment_id']}")
    logs.append(f"📦 Criativos gerados: {generation.get('total', 0)}")
    logs.append("🏆 Resultados por variação:")
    for creative in ranking.get("all_scored", []):
        qa_status = (creative.get("visual_qa") or {}).get("status", "n/a")
        logs.append(
            f"   → [{creative.get('format')}:{creative['blueprint']}] "
            f"Score {creative['score']} ({creative['action']}, QA {qa_status})"
        )
    for format_name, creative in result.get("winners", {}).items():
        render_path = (result.get("rendered_winners", {}).get(format_name) or {}).get("path")
        logs.append(f"📸 Campeão {format_name} HTML-fonte: {creative['file']}")
        if render_path:
            logs.append(f"🖼️ Imagem {format_name} pronta: {render_path}")
    carousel_slides = result.get("rendered_carousel_slides") or []
    if carousel_slides:
        rendered_count = sum(1 for slide in carousel_slides if slide.get("status") == "success")
        logs.append(f"🎞️ Carrossel renderizado: {rendered_count}/{len(carousel_slides)} slides")
    if result.get("landing"):
        logs.append(f"🌐 Landing gerada: {result['landing']['file']}")
    if result.get("campaign_export"):
        export = result["campaign_export"]
        logs.append(f"📁 Export final: {export.get('export_dir')}")
        carousel_export = (export.get("formats") or {}).get("carousel") or {}
        if carousel_export.get("slides"):
            logs.append(f"📦 Pacote de carrossel: {len(carousel_export['slides'])} slides no export")
    logs.append(f"🧠 Memória atualizada: {len(result.get('memory_records', []))} registros")

    return "\n".join(logs) + "\n\n🎉 [SUCESSO] Campanha finalizada pelo Campaign Pipeline."

@mcp.tool()
def rodar_campanha_completa(nome_cliente: str, objetivo: str, nicho: str = "geral") -> str:
    """
    Inicia o fluxo completo de marketing do JarvisAgency MCP integrado ao novo Creative OS.
    """
    logs = []
    logs.append(f"🚀 Iniciando campanha integrada JarvisAgency MCP para: {nome_cliente}...")

    # 1. Pipeline SaaS
    logs.append("📊 [1/4] Processando e gerando criativos baseados em Design States...")
    result_str = executar_pipeline_completo_saas(nome_cliente, objetivo, nicho)
    logs.append(result_str)

    # 2. Next.js Hydration (Landing Page)
    logs.append("🖌️ [2/4] Hydration: Preparando modelo estruturado da Landing Page...")
    catalog = load_catalog()
    graph_result = process_briefing(WORKSPACE_DIR)
    context = graph_result["context_graph"]
    copy_result = generate_copy(context, objetivo)
    copy_data = copy_result["copy_data"]

    design_result = open_design_inject(
        copy_data,
        context.get("palette", {}).get("accent", "#d9a752"),
        nicho,
        catalog,
        context=context,
    )
    if "error" in design_result:
        logs.append(f"❌ Erro no Open-Design: {design_result['error']}")
        return "\n".join(logs)

    # 3. Deer-Flow
    logs.append("🤖 [3/4] Deer-Flow: Instanciando Chatbot de Atendimento...")
    deploy_result = deploy_typebot_flow(nicho, catalog, ASSETS_DIR)
    logs.append(f"   → {deploy_result.get('message', 'Ok')}")

    logs.append("⏳ [4/4] Deer-Flow: Registrando aprovação da campanha no pipeline...")
    approval_result = dispatch_for_approval(design_result["asset_path"], copy_data)
    logs.append(f"   → {approval_result.get('message', 'Ok')}")

    logs.append("🎉 Campanha registrada com sucesso no pipeline de tráfego!")
    return "\n".join(logs)


if __name__ == "__main__":
    mcp.run()
