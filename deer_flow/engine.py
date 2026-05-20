import time

def dispatch_for_approval(media_asset_path: str, copy_data: dict):
    """
    Simula o envio de webhook para o chatbot de aprovação (Telegram/WhatsApp) e pausa.
    Na realidade, isso entraria num loop assíncrono ou cron job esperando a resposta HTTP.
    """
    print(f"[Deer-Flow] Enviando webhook com o ativo: {media_asset_path}")
    print(f"[Deer-Flow] Copy: {copy_data}")

    # Mocking wait for human approval
    print("[Deer-Flow] Aguardando aprovação (mock)... Aprovado automaticamente para fins de teste.")
    return {
        "status": "approved",
        "message": "Publicação aprovada pelo gestor."
    }

def publish_to_instagram(media_asset_path: str, copy_data: dict):
    """
    Dispara via API Graph para o Instagram.
    """
    print("[Deer-Flow] Disparando para API do Instagram...")
    return {
        "status": "published",
        "post_id": "mock_post_12345"
    }

def deploy_typebot_flow(niche: str, catalog_data: dict, assets_dir: str):
    """
    Busca o fluxo de Typebot do catálogo global e simula o deploy via API para o cliente.
    """
    print(f"[Deer-Flow] Buscando fluxo de Typebot para o nicho: {niche}")
    typebot_path = catalog_data.get("global_automation", {}).get("typebot")

    if not typebot_path:
        return {"status": "error", "message": "Arquivo +2000 FLUXOS TYPEBOT não encontrado no catálogo."}

    full_path = f"{assets_dir}/{typebot_path}"
    print(f"[Deer-Flow] Acessando arquivo ZIP gigante de Typebots: {full_path}")
    print("[Deer-Flow] Extraindo JSON simulado de conversão/agendamento para o nicho...")
    print(f"[Deer-Flow] Disparando webhook para API do Typebot para instanciar o bot de '{niche}'!")

    return {
        "status": "success",
        "message": f"Fluxo de Typebot para {niche} ativado com sucesso.",
        "bot_url": f"https://typebot.io/mock-agency-{niche}"
    }
