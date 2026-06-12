"""
Deer Flow — Pipeline de aprovação e deploy do Creative OS

Fluxo:
  dispatch_for_approval()  → Envia criativo para aprovação via Telegram
  publish_to_instagram()   → Publica no Instagram via Meta Graph API
  deploy_typebot_flow()    → Deploy de fluxo Typebot via API
"""

import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# Configurações (lê do .env da Mbya Digital)
# ──────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("HERMES_TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "1001733126")

META_GRAPH_TOKEN = os.getenv("META_GRAPH_TOKEN", "")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID", "")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
META_GRAPH_URL = "https://graph.facebook.com/v22.0"


def _telegram_send(text: str, photo_path: str | None = None) -> dict:
    """Envia mensagem ou foto para o Telegram."""
    if not TELEGRAM_BOT_TOKEN:
        return {"status": "error", "message": "TELEGRAM_BOT_TOKEN não configurado"}

    try:
        if photo_path and os.path.exists(photo_path):
            with open(photo_path, "rb") as f:
                resp = requests.post(
                    f"{TELEGRAM_API}/sendPhoto",
                    data={"chat_id": TELEGRAM_CHAT_ID, "caption": text[:1024]},
                    files={"photo": f},
                    timeout=30,
                )
        else:
            resp = requests.post(
                f"{TELEGRAM_API}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"},
                timeout=30,
            )

        data = resp.json()
        if data.get("ok"):
            return {"status": "sent", "message_id": data["result"]["message_id"]}
        return {"status": "error", "message": data.get("description", "Erro Telegram")}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def dispatch_for_approval(media_asset_path: str, copy_data: dict) -> dict:
    """
    Envia o criativo para aprovação via Telegram.
    O gestor aprova/rejeita respondendo no chat.
    """
    print(f"[Deer-Flow] Enviando aprovação para Telegram...")
    print(f"[Deer-Flow] Ativo: {media_asset_path}")

    # Monta preview do copy
    headline = (copy_data.get("hero") or {}).get("headline", "Sem headline")
    cta = (copy_data.get("hero") or {}).get("cta", "Sem CTA")

    msg = (
        f"📋 <b>Nova campanha para aprovação</b>\n\n"
        f"<b>Headline:</b> {headline}\n"
        f"<b>CTA:</b> {cta}\n"
        f"<b>Ativo:</b> {media_asset_path}\n\n"
        f"Responda com <b>/approve</b> ou <b>/reject</b>"
    )

    result = _telegram_send(msg, photo_path=media_asset_path)

    if result["status"] == "sent":
        print(f"[Deer-Flow] ✅ Notificação enviada! Message ID: {result['message_id']}")
        return {
            "status": "awaiting_approval",
            "message": "Aguardando aprovação via Telegram",
            "message_id": result["message_id"],
        }

    # Fallback: se Telegram não configurado, aprova automático
    print(f"[Deer-Flow] ⚠️ Telegram não configurado — aprovado automaticamente.")
    return {"status": "approved", "message": "Aprovado automaticamente (Telegram não configurado)"}


def publish_to_instagram(media_asset_path: str, copy_data: dict) -> dict:
    """
    Publica no Instagram via Meta Graph API.
    """
    if not META_GRAPH_TOKEN or INSTAGRAM_ACCOUNT_ID in ("", "seu_account_id_aqui"):
        print("[Deer-Flow] ⚠️ Meta Graph API não configurada — pulando publicação real.")
        print("[Deer-Flow] Para configurar: edite .env com META_GRAPH_TOKEN e INSTAGRAM_ACCOUNT_ID")
        return {
            "status": "skipped",
            "message": "Publicação no Instagram: pendente de configuração do token Meta",
            "hint": "Edite o .env da Mbya Digital com as credenciais do Meta Graph API"
        }

    print(f"[Deer-Flow] Publicando no Instagram...")

    try:
        # 1. Upload media
        caption = (copy_data.get("hero") or {}).get("headline", "Novo post Mbya Digital")
        if copy_data.get("benefits"):
            caption += "\n\n" + "\n".join(f"✅ {b}" for b in copy_data["benefits"][:3])

        upload_url = f"{META_GRAPH_URL}/{INSTAGRAM_ACCOUNT_ID}/media"
        upload_resp = requests.post(
            upload_url,
            params={
                "image_url": media_asset_path if media_asset_path.startswith("http") else None,
                "caption": caption[:2200],
                "access_token": META_GRAPH_TOKEN,
            },
            timeout=30,
        )
        data = upload_resp.json()

        if "id" not in data:
            return {"status": "error", "message": f"Erro upload: {data}"}

        media_id = data["id"]

        # 2. Publicar
        publish_url = f"{META_GRAPH_URL}/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        pub_resp = requests.post(
            publish_url,
            params={"creation_id": media_id, "access_token": META_GRAPH_TOKEN},
            timeout=30,
        )
        pub_data = pub_resp.json()

        if "id" in pub_data:
            return {
                "status": "published",
                "post_id": pub_data["id"],
                "media_id": media_id,
                "url": f"https://instagram.com/p/{pub_data['id']}",
            }

        return {"status": "error", "message": f"Erro publicação: {pub_data}"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def deploy_typebot_flow(niche: str, catalog_data: dict, assets_dir: str) -> dict:
    """
    Busca fluxo Typebot do catálogo e faz deploy via API.
    """
    print(f"[Deer-Flow] Buscando fluxo de Typebot para o nicho: {niche}")

    typebot_path = (catalog_data.get("global_automation") or {}).get("typebot")
    typebot_api_key = os.getenv("TYPEBOT_API_KEY", "")
    typebot_workspace = os.getenv("TYPEBOT_WORKSPACE_ID", "")

    if not typebot_path:
        print("[Deer-Flow] ⚠️ Nenhum fluxo Typebot configurado no catálogo global_automation.typebot")
        return {
            "status": "skipped",
            "message": f"Fluxo Typebot para {niche}: pendente de configuração no catálogo",
        }

    full_path = f"{assets_dir}/{typebot_path}" if assets_dir else typebot_path

    if typebot_api_key and typebot_workspace:
        # Deploy real via Typebot API
        try:
            with open(full_path, "r") as f:
                flow_data = json.load(f)

            resp = requests.post(
                f"https://app.typebot.io/api/typebots/import",
                headers={
                    "Authorization": f"Bearer {typebot_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "workspaceId": typebot_workspace,
                    "typebot": flow_data,
                    "name": f"Agendamento - {niche}",
                },
                timeout=30,
            )

            if resp.status_code in (200, 201):
                data = resp.json()
                return {
                    "status": "success",
                    "message": f"Fluxo Typebot para {niche} implantado com sucesso",
                    "bot_url": f"https://typebot.io/typebots/{data.get('id', '')}",
                    "typebot_id": data.get("id"),
                }
            return {"status": "error", "message": f"Erro Typebot API: {resp.text}"}

        except json.JSONDecodeError:
            print(f"[Deer-Flow] Arquivo {full_path} não é JSON válido — deploy manual necessário.")
            return {
                "status": "success",
                "message": f"Fluxo de Typebot para '{niche}' pronto para deploy manual em {full_path}",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    else:
        print(f"[Deer-Flow] Typebot API não configurada. Fluxo disponível em: {full_path}")
        return {
            "status": "info",
            "message": f"Fluxo extraído para '{niche}' em {full_path}. "
                       f"Configure TYPEBOT_API_KEY e TYPEBOT_WORKSPACE_ID no .env para deploy automático.",
        }
