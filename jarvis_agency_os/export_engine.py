"""
Export Engine — Exporta criativos para Meta Ads, Google Ads e TikTok.
Responsável por converter assets PNG em formatos esperados pelas plataformas.
"""
import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Export format specifications
EXPORT_FORMATS = {
    "meta_ads": {
        "supported_dimensions": [(1080, 1080), (1200, 628), (1080, 1920)],
        "max_file_size": 4 * 1024 * 1024,  # 4MB
        "formats": ["jpg", "png"],
        "description": "Facebook / Instagram Feed & Stories"
    },
    "google_ads": {
        "supported_dimensions": [(1080, 1080), (1200, 628), (320, 480)],
        "max_file_size": 5 * 1024 * 1024,  # 5MB
        "formats": ["jpg", "png", "gif"],
        "description": "Google Display Network"
    },
    "tiktok_ads": {
        "supported_dimensions": [(1080, 1920), (540, 960)],
        "max_file_size": 100 * 1024 * 1024,  # 100MB
        "formats": ["mp4", "mov"],
        "description": "TikTok Ads"
    },
    "google_shopping": {
        "supported_dimensions": [(800, 800), (1200, 800)],
        "max_file_size": 5 * 1024 * 1024,
        "formats": ["jpg", "png"],
        "description": "Google Shopping / Merchant Center"
    }
}


def _slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", str(value or "campaign").lower()).strip("_") or "campaign"


def create_video_from_image(image_path: str, output_path: str, duration_seconds: int = 15,
                            width: int = 1080, height: int = 1920, fps: int = 30) -> Dict:
    """Converte um PNG/JPG estático em MP4 vertical para Reels/TikTok usando ffmpeg."""
    if not os.path.exists(image_path):
        return {"status": "error", "error": f"Imagem não encontrada: {image_path}"}

    ffmpeg_bin = shutil.which("ffmpeg")
    command = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-t", str(duration_seconds),
        "-r", str(fps),
        "-vf",
        (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,"
            "format=yuv420p"
        ),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path,
    ]

    if not ffmpeg_bin:
        return {
            "status": "unavailable",
            "error": "ffmpeg não encontrado no ambiente.",
            "install_hint": "Instale ffmpeg para gerar MP4 automaticamente.",
            "conversion_command": " ".join(command),
        }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    try:
        result = subprocess.run(
            [ffmpeg_bin, *command[1:]],
            capture_output=True,
            text=True,
            timeout=max(30, duration_seconds + 20),
        )
    except subprocess.TimeoutExpired:
        return {"status": "error", "error": "Timeout ao gerar vídeo com ffmpeg."}

    if result.returncode != 0:
        return {
            "status": "error",
            "error": "Falha ao gerar vídeo com ffmpeg.",
            "stderr": result.stderr[-1000:],
            "conversion_command": " ".join(command),
        }

    return {
        "status": "success",
        "path": output_path,
        "source": image_path,
        "duration_seconds": duration_seconds,
        "width": width,
        "height": height,
        "fps": fps,
    }


def export_campaign_artifacts(pipeline_result: Dict, workspace_dir: str) -> Dict:
    """
    Organiza os artefatos finais em uma pasta única da campanha.

    Estrutura:
      exports/campaign_slug/feed
      exports/campaign_slug/story
      exports/campaign_slug/landing
      exports/campaign_slug/manifests
    """
    client = (
        (pipeline_result.get("landing") or {}).get("client")
        or next(iter(pipeline_result.get("winners", {}).values()), {}).get("client")
        or "campaign"
    )
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    campaign_slug = f"{_slug(client)}_{timestamp}"
    base_dir = os.path.join(workspace_dir, "exports", campaign_slug)
    manifests_dir = os.path.join(base_dir, "manifests")
    os.makedirs(manifests_dir, exist_ok=True)

    exported = {
        "status": "success",
        "campaign": client,
        "export_dir": base_dir,
        "formats": {},
        "landing": {},
        "manifest_path": os.path.join(manifests_dir, "campaign_export_manifest.json"),
        "created_at": datetime.now().isoformat(),
    }

    rendered = pipeline_result.get("rendered_winners", {})
    for format_name, render_result in rendered.items():
        source_path = render_result.get("path")
        if not source_path or not os.path.exists(source_path):
            exported["formats"][format_name] = {"status": "missing_render", "source": source_path}
            continue
        format_dir = os.path.join(base_dir, format_name)
        os.makedirs(format_dir, exist_ok=True)
        target_path = os.path.join(format_dir, os.path.basename(source_path))
        shutil.copy2(source_path, target_path)
        exported["formats"][format_name] = {
            "status": "success",
            "source": source_path,
            "path": target_path,
        }

    rendered_carousel_slides = pipeline_result.get("rendered_carousel_slides") or []
    if rendered_carousel_slides:
        carousel_dir = os.path.join(base_dir, "carousel")
        os.makedirs(carousel_dir, exist_ok=True)
        exported["formats"].setdefault("carousel", {"status": "success", "slides": []})
        exported["formats"]["carousel"].setdefault("slides", [])
        for slide_result in rendered_carousel_slides:
            source_path = slide_result.get("path")
            if not source_path or not os.path.exists(source_path):
                exported["formats"]["carousel"]["slides"].append({
                    "status": "missing_render",
                    "slide": slide_result.get("slide"),
                    "source": source_path,
                })
                continue
            target_path = os.path.join(carousel_dir, os.path.basename(source_path))
            shutil.copy2(source_path, target_path)
            exported["formats"]["carousel"]["slides"].append({
                "status": "success",
                "slide": slide_result.get("slide"),
                "source": source_path,
                "path": target_path,
            })

    landing = pipeline_result.get("landing") or {}
    if landing.get("file") and os.path.exists(landing["file"]):
        landing_dir = os.path.join(base_dir, "landing")
        os.makedirs(landing_dir, exist_ok=True)
        target_html = os.path.join(landing_dir, os.path.basename(landing["file"]))
        shutil.copy2(landing["file"], target_html)
        exported["landing"]["html"] = target_html
        if landing.get("manifest") and os.path.exists(landing["manifest"]):
            target_manifest = os.path.join(manifests_dir, os.path.basename(landing["manifest"]))
            shutil.copy2(landing["manifest"], target_manifest)
            exported["landing"]["manifest"] = target_manifest

    with open(exported["manifest_path"], "w", encoding="utf-8") as f:
        json.dump(exported, f, indent=2, ensure_ascii=False)

    return exported


class ExportManager:
    """Gerencia exportação de criativos para múltiplas plataformas."""

    def __init__(self, workspace_dir: str):
        self.workspace_dir = workspace_dir
        self.export_dir = os.path.join(workspace_dir, "exports")
        os.makedirs(self.export_dir, exist_ok=True)
        self.export_log = []

    def export_for_meta_ads(self, creative_path: str, campaign_name: str,
                           adset_name: str, targeting: Dict = None) -> Dict:
        """
        Exporta criativo para Meta Ads (Instagram + Facebook).

        Args:
            creative_path: Caminho do PNG gerado
            campaign_name: Nome da campanha
            adset_name: Nome do conjunto de anúncios
            targeting: Dict com targeting (age, interests, locations, etc)

        Returns:
            Dict com metadata e path do arquivo pronto para upload
        """
        if not os.path.exists(creative_path):
            return {"error": f"Arquivo não encontrado: {creative_path}"}

        try:
            basename = os.path.splitext(os.path.basename(creative_path))[0]
            export_subdir = os.path.join(self.export_dir, "meta_ads")
            os.makedirs(export_subdir, exist_ok=True)

            # Validar dimensões
            from PIL import Image
            img = Image.open(creative_path)
            dimensions = img.size

            if dimensions not in EXPORT_FORMATS["meta_ads"]["supported_dimensions"]:
                return {
                    "warning": f"Dimensões {dimensions} não otimizadas para Meta Ads",
                    "recommended": EXPORT_FORMATS["meta_ads"]["supported_dimensions"]
                }

            # Copiar arquivo
            export_filename = f"{campaign_name}_{adset_name}_{basename}.jpg"
            export_path = os.path.join(export_subdir, export_filename)

            # Converter PNG to JPG se necessário (melhor compressão)
            if creative_path.lower().endswith('.png'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
                rgb_img.save(export_path, quality=95)
            else:
                import shutil
                shutil.copy2(creative_path, export_path)

            # Gerar metadata para upload via API
            metadata = {
                "platform": "meta_ads",
                "campaign_name": campaign_name,
                "adset_name": adset_name,
                "asset_path": export_path,
                "dimensions": dimensions,
                "targeting": targeting or {},
                "upload_instructions": {
                    "step_1": "Ir em Meta Ads Manager > Criar Anúncio",
                    "step_2": f"Fazer upload de: {export_path}",
                    "step_3": "Configurar targeting conforme metadata['targeting']",
                    "api_endpoint": "https://graph.instagram.com/me/adsets"
                },
                "timestamp": datetime.now().isoformat()
            }

            self.export_log.append(metadata)

            return {
                "status": "success",
                "platform": "meta_ads",
                "export_path": export_path,
                "metadata": metadata,
                "file_size": os.path.getsize(export_path),
                "instructions": "Faça upload em Meta Ads Manager"
            }
        except Exception as e:
            return {"error": f"Falha na exportação Meta Ads: {str(e)}"}

    def export_for_google_ads(self, creative_path: str, campaign_name: str,
                             ad_group: str, keywords: List[str] = None) -> Dict:
        """
        Exporta criativo para Google Ads (Display Network).
        """
        if not os.path.exists(creative_path):
            return {"error": f"Arquivo não encontrado: {creative_path}"}

        try:
            basename = os.path.splitext(os.path.basename(creative_path))[0]
            export_subdir = os.path.join(self.export_dir, "google_ads")
            os.makedirs(export_subdir, exist_ok=True)

            from PIL import Image
            img = Image.open(creative_path)
            dimensions = img.size

            export_filename = f"{campaign_name}_{ad_group}_{basename}.jpg"
            export_path = os.path.join(export_subdir, export_filename)

            # Converter para JPG
            if creative_path.lower().endswith('.png'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
                rgb_img.save(export_path, quality=95)
            else:
                import shutil
                shutil.copy2(creative_path, export_path)

            metadata = {
                "platform": "google_ads",
                "campaign_name": campaign_name,
                "ad_group": ad_group,
                "asset_path": export_path,
                "dimensions": dimensions,
                "keywords": keywords or [],
                "upload_instructions": {
                    "step_1": "Ir em Google Ads > Criar Anúncio de Rede de Display",
                    "step_2": f"Fazer upload de: {export_path}",
                    "step_3": "Configurar palavras-chave",
                    "api_endpoint": "https://www.googleapis.com/dfareporting/v4/userprofiles/*/creatives"
                },
                "timestamp": datetime.now().isoformat()
            }

            self.export_log.append(metadata)

            return {
                "status": "success",
                "platform": "google_ads",
                "export_path": export_path,
                "metadata": metadata,
                "file_size": os.path.getsize(export_path),
                "instructions": "Faça upload em Google Ads"
            }
        except Exception as e:
            return {"error": f"Falha na exportação Google Ads: {str(e)}"}

    def export_for_tiktok_ads(self, video_path: str, campaign_name: str,
                             objective: str = "traffic", duration_seconds: int = 15) -> Dict:
        """
        Exporta vídeo para TikTok Ads.
        Aceita MP4 pronto ou converte PNG/JPG para MP4 vertical quando ffmpeg estiver disponível.
        """
        if not os.path.exists(video_path):
            return {"error": f"Arquivo não encontrado: {video_path}"}

        try:
            export_subdir = os.path.join(self.export_dir, "tiktok_ads")
            os.makedirs(export_subdir, exist_ok=True)

            basename = os.path.splitext(os.path.basename(video_path))[0]
            export_filename = f"{campaign_name}_{basename}.mp4"
            export_path = os.path.join(export_subdir, export_filename)

            source_ext = os.path.splitext(video_path)[1].lower()
            conversion = None
            if source_ext in {".mp4", ".mov"}:
                shutil.copy2(video_path, export_path)
            else:
                conversion = create_video_from_image(
                    video_path,
                    export_path,
                    duration_seconds=duration_seconds,
                    width=1080,
                    height=1920,
                )
                if conversion.get("status") != "success":
                    return {
                        "status": "conversion_unavailable" if conversion.get("status") == "unavailable" else "error",
                        "platform": "tiktok_ads",
                        "source_path": video_path,
                        "export_path": export_path,
                        "conversion": conversion,
                    }

            metadata = {
                "platform": "tiktok_ads",
                "campaign_name": campaign_name,
                "objective": objective,
                "asset_path": export_path,
                "source_path": video_path,
                "duration_seconds": duration_seconds,
                "upload_instructions": {
                    "step_1": "Ir em TikTok Ads Manager",
                    "step_2": f"Fazer upload de: {export_path}",
                    "step_3": "Configurar objetivo da campanha",
                    "api_endpoint": "https://business-api.tiktok.com/open_api/v1.3/ad/creative/create/"
                },
                "timestamp": datetime.now().isoformat()
            }

            self.export_log.append(metadata)

            return {
                "status": "success",
                "platform": "tiktok_ads",
                "export_path": export_path,
                "metadata": metadata,
                "conversion": conversion,
                "file_size": os.path.getsize(export_path),
                "instructions": "Faça upload em TikTok Ads Manager"
            }
        except Exception as e:
            return {"error": f"Falha na exportação TikTok: {str(e)}"}

    def export_for_google_shopping(self, creative_path: str, product_id: str,
                                  product_name: str, price: float) -> Dict:
        """
        Exporta imagem de produto para Google Shopping / Merchant Center.
        """
        if not os.path.exists(creative_path):
            return {"error": f"Arquivo não encontrado: {creative_path}"}

        try:
            export_subdir = os.path.join(self.export_dir, "google_shopping")
            os.makedirs(export_subdir, exist_ok=True)

            export_filename = f"{product_id}_{product_name}.jpg"
            export_path = os.path.join(export_subdir, export_filename)

            from PIL import Image
            img = Image.open(creative_path)

            if creative_path.lower().endswith('.png'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
                rgb_img.save(export_path, quality=95)
            else:
                import shutil
                shutil.copy2(creative_path, export_path)

            metadata = {
                "platform": "google_shopping",
                "product_id": product_id,
                "product_name": product_name,
                "price": price,
                "asset_path": export_path,
                "dimensions": Image.open(export_path).size,
                "upload_instructions": {
                    "step_1": "Ir em Google Merchant Center",
                    "step_2": "Editar produto com ID: " + product_id,
                    "step_3": f"Fazer upload de imagem: {export_path}",
                    "api_endpoint": "https://www.googleapis.com/content/v2.1/merchantId/products"
                },
                "timestamp": datetime.now().isoformat()
            }

            self.export_log.append(metadata)

            return {
                "status": "success",
                "platform": "google_shopping",
                "export_path": export_path,
                "metadata": metadata,
                "file_size": os.path.getsize(export_path),
                "instructions": "Faça upload em Google Merchant Center"
            }
        except Exception as e:
            return {"error": f"Falha na exportação Google Shopping: {str(e)}"}

    def save_export_manifest(self) -> str:
        """Salva manifest com todos os exports realizados."""
        manifest_path = os.path.join(self.export_dir, "export_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(self.export_log, f, indent=2, ensure_ascii=False)
        return manifest_path


def batch_export(creative_files: List[str], platforms: List[str],
                workspace_dir: str, metadata: Dict) -> Dict:
    """
    Exporta um lote de criativos para múltiplas plataformas.

    Args:
        creative_files: Lista de caminhos de PNG
        platforms: Lista de plataformas ["meta_ads", "google_ads", "tiktok_ads"]
        workspace_dir: Diretório workspace
        metadata: Dict com campaign_name, adset_name, etc

    Returns:
        Dict com resultados de cada export
    """
    manager = ExportManager(workspace_dir)
    results = {}

    for platform in platforms:
        results[platform] = []

        for creative_file in creative_files:
            if platform == "meta_ads":
                result = manager.export_for_meta_ads(
                    creative_file,
                    metadata.get("campaign_name", "default"),
                    metadata.get("adset_name", "default"),
                    metadata.get("targeting")
                )
            elif platform == "google_ads":
                result = manager.export_for_google_ads(
                    creative_file,
                    metadata.get("campaign_name", "default"),
                    metadata.get("ad_group", "default"),
                    metadata.get("keywords")
                )
            elif platform == "tiktok_ads":
                result = manager.export_for_tiktok_ads(
                    creative_file,
                    metadata.get("campaign_name", "default")
                )
            else:
                result = {"error": f"Plataforma não suportada: {platform}"}

            results[platform].append(result)

    # Salvar manifest
    manifest = manager.save_export_manifest()

    return {
        "status": "completed",
        "total_files": len(creative_files),
        "platforms_processed": len(platforms),
        "export_results": results,
        "manifest_path": manifest
    }
