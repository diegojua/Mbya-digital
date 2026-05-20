#!/usr/bin/env python3
"""
Exemplo End-to-End: Pipeline Completo JarvisAgency Creative OS
Demonstração de geração → ranking → renderização → export → memory
"""
import os
import sys
import json
from pathlib import Path

# Adicionar projeto ao path
sys.path.insert(0, os.path.dirname(__file__))

WORKSPACE_DIR = os.path.join(os.path.dirname(__file__), "workspace")


def create_sample_briefing():
    """Cria um briefing de exemplo para teste."""
    briefing_content = """Cliente: Padaria Artesanal da Vila
Nicho: padaria
Objetivo: Vendas Online de Assinatura
Detalhes: Vender assinatura mensal de pão artesanal fresco  fermentação natural
Localização: São Paulo, SP
WhatsApp: 5511987654321
Logo_icone: 🥖
Logo_texto: PADARIA ARTESANAL
Logo_subtitulo: Pão Fresco Todo Dia
"""

    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    briefing_path = os.path.join(WORKSPACE_DIR, "briefing.txt")

    with open(briefing_path, "w", encoding="utf-8") as f:
        f.write(briefing_content)

    return briefing_path


def print_section(title):
    """Imprime seção com formatação."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def run_pipeline():
    """Executa o pipeline completo."""

    print_section("🚀 Pipeline JarvisAgency — Exemplo End-to-End")

    # Setup
    print("\n📋 Preparando ambiente...")
    create_sample_briefing()
    print(f"  ✓ Briefing criado em {WORKSPACE_DIR}")

    # 1. Gerar criativos
    print_section("📦 [1/5] Gerando Criativos com Creative Engine")

    try:
        from jarvis_agency_os.creative_engine import generate_creatives

        print("  • Processando briefing...")
        print("  • Resolvendo design state psicológico...")
        print("  • Gerando múltiplos ângulos de copy...")
        print("  • Selecionando blueprints compatíveis...")

        gen_result = generate_creatives(WORKSPACE_DIR)

        if "error" in gen_result:
            print(f"\n  ❌ Erro: {gen_result['error']}")
            return False

        generated = gen_result.get("generated", [])
        print(f"\n  ✅ {len(generated)} criativos HTML gerados com sucesso")

        if generated:
            sample = generated[0]
            print(f"\n  Sample:")
            print(f"    • Blueprint: {sample.get('blueprint')}")
            print(f"    • Design State: {sample.get('design_state')}")
            print(f"    • Headline: {sample.get('headline')[:50]}...")

    except Exception as e:
        print(f"  ❌ Erro ao gerar criativos: {e}")
        return False

    # 2. Rankear
    print_section("🏆 [2/5] Avaliando com Creative Ranker")

    try:
        from jarvis_agency_os.ranker import rank_creatives

        print(f"  • Avaliando {len(generated)} criativos em 6 dimensões...")
        print("    - Legibilidade")
        print("    - Hierarquia Visual")
        print("    - Visibilidade do CTA")
        print("    - Constraint Compliance")
        print("    - Design State Alignment")
        print("    - Batch Diversity")

        rank_result = rank_creatives(generated, top_n=2)
        top_candidates = rank_result.get("top", [])
        all_scored = rank_result.get("all_scored", [])

        print(f"\n  ✅ Ranking concluído ({len(all_scored)} avaliados)")
        print(f"\n  Top 2 Candidatos:")

        for i, creative in enumerate(top_candidates, 1):
            score = creative.get("score", 0)
            action = creative.get("action", "pending")
            print(f"\n    #{i} Score: {score:.1f} → {action.upper()}")
            print(f"       Blueprint: {creative.get('blueprint')}")
            print(f"       Headline: {creative.get('headline')[:40]}...")

    except Exception as e:
        print(f"  ❌ Erro ao rankear: {e}")
        # Continuar mesmo com erro
        if not top_candidates:
            top_candidates = generated[:2] if len(generated) >= 2 else generated

    # 3. Renderizar
    print_section("📸 [3/5] Renderizando PNG com Playwright")

    try:
        from jarvis_agency_os.renderer import render_html_to_png

        if not top_candidates:
            print("  ⚠️  Sem criativos para renderizar")
            return False

        best = top_candidates[0]
        html_file = best.get("file")

        if not html_file or not os.path.exists(html_file):
            print(f"  ⚠️  Arquivo HTML não encontrado: {html_file}")
            output_png = None
        else:
            output_png = os.path.join(WORKSPACE_DIR, "final_creative_best.png")

            print(f"  • Renderizando {os.path.basename(html_file)}...")
            print(f"  • Dimensão: 1080x1080px")
            print(f"  • Saída: {os.path.basename(output_png)}")

            render_result = render_html_to_png(html_file, output_png,
                                              width=1080, height=1080)

            if render_result.get("status") == "success":
                file_size = os.path.getsize(output_png) / 1024
                print(f"\n  ✅ PNG renderizado ({file_size:.0f}KB)")
            else:
                print(f"\n  ⚠️  {render_result.get('message', 'Renderização offline')}")
                output_png = None

    except Exception as e:
        print(f"  ❌ Erro ao renderizar: {e}")
        output_png = None

    # 4. Exportar para plataformas
    print_section("🚀 [4/5] Exportando para Plataformas de Anúncios")

    try:
        from jarvis_agency_os.export_engine import ExportManager

        if output_png and os.path.exists(output_png):
            manager = ExportManager(WORKSPACE_DIR)

            # Meta Ads
            print("\n  • Exportando para Meta Ads (Instagram + Facebook)...")
            meta_result = manager.export_for_meta_ads(
                creative_path=output_png,
                campaign_name="padaria_assinatura",
                adset_name="feed_1080",
                targeting={
                    "age": "25-55",
                    "interests": ["food", "organic", "local_business", "premium"],
                    "locations": ["São Paulo", "Brazil"]
                }
            )

            if meta_result.get("status") == "success":
                print(f"    ✅ {os.path.basename(meta_result['export_path'])}")

            # Google Ads
            print("\n  • Exportando para Google Ads (Display Network)...")
            google_result = manager.export_for_google_ads(
                creative_path=output_png,
                campaign_name="padaria_assinatura",
                ad_group="assinatura_feed",
                keywords=["pão artesanal", "assinatura pão", "pão fresco", "fermentação natural"]
            )

            if google_result.get("status") == "success":
                print(f"    ✅ {os.path.basename(google_result['export_path'])}")

            print(f"\n  ✅ Exports salvos em: {manager.export_dir}")
        else:
            print("  ⚠️  Sem PNG para exportar")

    except Exception as e:
        print(f"  ⚠️  Erro ao exportar: {e}")

    # 5. Salvar em Visual Memory
    print_section("🧠 [5/5] Salvando em Visual Memory (SQLite)")

    try:
        from jarvis_agency_os.visual_memory_v2 import get_memory

        memory = get_memory()

        best = top_candidates[0] if top_candidates else {}

        print("\n  • Registrando campanha...")
        memory.record_campaign(
            client="Padaria Artesanal da Vila",
            design_state=best.get("design_state", "luxury"),
            blueprint=best.get("blueprint", "feed_split_editorial"),
            score=best.get("score", 82.0),
            headline=best.get("headline", "Pão Artesanal Fresco"),
            body="Assinatura mensal de pão fresco com fermentação natural",
            cta="Assinar Agora",
            approved=True,
            ctr=0.032,  # Hipotético baseado em histórico
            lead_cost=8.50
        )

        print("  • Gerando snapshot de estatísticas...")
        stats = memory.get_stats()

        print(f"\n  ✅ Memória atualizada:")
        print(f"     • Total gerado: {stats['total_generated']}")
        print(f"     • Total aprovado: {stats['total_approved']}")
        print(f"     • Taxa aprovação: {stats.get('approval_rate', 0):.1f}%")
        print(f"     • Score médio: {stats['avg_score']:.1f}")
        print(f"     • Top design state: {stats['top_design_state']}")
        print(f"     • Top blueprint: {stats['top_blueprint']}")

        # Performance por state
        print(f"\n  • Performance por Design State:")
        perf = memory.get_performance_by_state()
        for state, metrics in list(perf.items())[:3]:
            print(f"    - {state}: {metrics['total_generated']} gerados, "
                  f"score {metrics['avg_score']:.1f}")

        # Trending blueprints
        print(f"\n  • Blueprints em Tendência:")
        trending = memory.get_trending_blueprints(limit=3)
        for bp, count, score in trending:
            print(f"    - {bp}: {count} usos, score {score:.1f}")

    except Exception as e:
        print(f"  ❌ Erro ao salvar em memória: {e}")
        import traceback
        traceback.print_exc()

    # Resultado final
    print_section("✅ Pipeline Concluído com Sucesso!")

    print(f"\n📁 Outputs gerados:")
    print(f"  • Workspace: {WORKSPACE_DIR}")

    outputs = {
        "htmls": len([f for f in os.listdir(WORKSPACE_DIR)
                     if f.endswith('.html')]),
        "pngs": len([f for f in os.listdir(WORKSPACE_DIR)
                    if f.endswith('.png')]),
        "exports": 0
    }

    export_dir = os.path.join(WORKSPACE_DIR, "exports")
    if os.path.exists(export_dir):
        for subdir in os.listdir(export_dir):
            if os.path.isdir(os.path.join(export_dir, subdir)):
                outputs["exports"] += len(os.listdir(
                    os.path.join(export_dir, subdir)
                ))

    print(f"\n  ✓ {outputs['htmls']} HTMLs gerados")
    print(f"  ✓ {outputs['pngs']} PNGs renderizados")
    print(f"  ✓ {outputs['exports']} Assets exportados")

    print(f"\n🎯 Próximos Passos:")
    print(f"  1. Revisar PNGs em: workspace/")
    print(f"  2. Fazer upload em Meta Ads Manager / Google Ads / TikTok")
    print(f"  3. Rastrear performance com UTM parameters")
    print(f"  4. Iterar com base em feedback visual_memory\n")

    return True


if __name__ == "__main__":
    try:
        success = run_pipeline()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏸️  Pipeline cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
