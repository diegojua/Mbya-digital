"""
Unit tests para o JarvisAgency Creative Engine.
"""
import pytest
import os
import json
import tempfile
from pathlib import Path


class TestConfigValidation:
    """Testa validação dos arquivos de configuração."""

    def test_design_states_exists(self):
        """Verifica se design_states.json existe."""
        config_dir = Path(__file__).parent.parent / "jarvis_agency_os" / "config"
        design_states_path = config_dir / "design_states.json"
        assert design_states_path.exists(), "design_states.json não encontrado"

    def test_design_states_valid_json(self):
        """Verifica se design_states.json é JSON válido."""
        config_dir = Path(__file__).parent.parent / "jarvis_agency_os" / "config"
        design_states_path = config_dir / "design_states.json"

        with open(design_states_path, "r") as f:
            data = json.load(f)

        assert "states" in data, "Falta campo 'states'"
        assert "fallback_state" in data, "Falta campo 'fallback_state'"

    def test_constraints_exists(self):
        """Verifica se constraints.json existe."""
        config_dir = Path(__file__).parent.parent / "jarvis_agency_os" / "config"
        constraints_path = config_dir / "constraints.json"
        assert constraints_path.exists(), "constraints.json não encontrado"

    def test_creative_ranker_exists(self):
        """Verifica se creative_ranker.json existe."""
        config_dir = Path(__file__).parent.parent / "jarvis_agency_os" / "config"
        ranker_path = config_dir / "creative_ranker.json"
        assert ranker_path.exists(), "creative_ranker.json não encontrado"

    def test_design_intelligence_exists(self):
        """Verifica se design_intelligence.json existe."""
        config_dir = Path(__file__).parent.parent / "jarvis_agency_os" / "config"
        path = config_dir / "design_intelligence.json"
        assert path.exists(), "design_intelligence.json não encontrado"


class TestVisualMemory:
    """Testa funcionalidades de Visual Memory."""

    def test_record_campaign(self):
        """Testa gravação de campanha em memória."""
        from jarvis_agency_os.visual_memory import record_campaign

        result = record_campaign(
            client="Test Client",
            design_state="authority",
            blueprint="feed_split_editorial",
            score=85.0,
            headline="Test Headline",
            approved=True
        )

        assert result["client"] == "Test Client"
        assert result["score"] == 85.0
        assert result["human_approved"] is True

    def test_get_stats(self):
        """Testa recuperação de estatísticas."""
        from jarvis_agency_os.visual_memory import get_stats

        stats = get_stats()
        assert "total_generated" in stats
        assert "total_approved" in stats
        assert "avg_score" in stats

    def test_get_history(self):
        """Testa recuperação de histórico."""
        from jarvis_agency_os.visual_memory import get_history, record_campaign

        # Registrar uma campanha
        record_campaign(
            client="History Test",
            design_state="luxury",
            blueprint="feed_dark_cinematic",
            score=90.0,
            headline="History Test Headline"
        )

        history = get_history(limit=5)
        assert isinstance(history, list)

    def test_visual_memory_v2_persists_visual_qa_metadata(self):
        """Memória v2 deve salvar formato e status do QA visual."""
        from jarvis_agency_os.visual_memory_v2 import get_memory

        memory = get_memory()
        saved = memory.record_creative_batch([{
            "client": "QA Memory Test",
            "niche": "qa_memory_niche",
            "objective": "teste",
            "design_state": "qa_memory_state",
            "blueprint": "story_premium_editorial",
            "score": 84,
            "headline": "Headline QA",
            "body": "Body",
            "cta": "Agendar",
            "action": "human_review",
            "file": "/tmp/qa_memory_story.html",
            "format": "story",
            "width": 1080,
            "height": 1920,
            "visual_qa": {"status": "review", "score": 84, "issues": []},
            "score_breakdown": {"visual_quality": 6.7},
        }], auto_approve_actions=False)

        assert saved[0]["format"] == "story"
        assert saved[0]["visual_qa_status"] == "review"

    def test_visual_memory_v2_ignores_failed_visual_qa_for_best_blueprint(self):
        """Blueprint com QA visual fail não deve ser priorizado pela memória."""
        from jarvis_agency_os.visual_memory_v2 import get_memory

        memory = get_memory()
        state = "qa_best_state"
        niche = "qa_best_niche"

        memory.record_campaign(
            client="QA Bad Blueprint",
            niche=niche,
            design_state=state,
            blueprint="bad_visual_blueprint",
            score=99,
            headline="Bad visual",
            action="auto_approve",
            approved=True,
            visual_qa_status="fail",
            creative_hash="qa_bad_visual_blueprint_hash",
        )
        memory.record_campaign(
            client="QA Good Blueprint",
            niche=niche,
            design_state=state,
            blueprint="good_visual_blueprint",
            score=80,
            headline="Good visual",
            action="auto_approve",
            approved=True,
            visual_qa_status="pass",
            creative_hash="qa_good_visual_blueprint_hash",
        )

        assert memory.get_best_blueprint_for_state(state, niche=niche) == "good_visual_blueprint"

    def test_visual_memory_v2_reports_ab_experiment_variants(self):
        """Memória v2 deve agrupar variantes e apontar vencedor por conversão."""
        from jarvis_agency_os.visual_memory_v2 import get_memory

        memory = get_memory()
        experiment_id = "exp_test_ab_memory"
        first = memory.record_campaign(
            client="AB Test Client",
            niche="ab_niche",
            design_state="safety",
            blueprint="story_a",
            score=88,
            headline="Variant A",
            experiment_id=experiment_id,
            variant_label="story-v1",
            creative_hash="exp_test_ab_memory_a",
        )
        second = memory.record_campaign(
            client="AB Test Client",
            niche="ab_niche",
            design_state="safety",
            blueprint="story_b",
            score=84,
            headline="Variant B",
            experiment_id=experiment_id,
            variant_label="story-v2",
            creative_hash="exp_test_ab_memory_b",
        )

        memory.record_performance(first["id"], impressions=1000, conversions=80, spend=120)
        memory.record_performance(second["id"], impressions=1000, conversions=30, spend=90)

        report = memory.get_experiment_report(experiment_id)

        assert report["variant_count"] == 2
        assert report["winner"]["variant_label"] == "story-v1"
        assert report["significance"]["status"] == "significant"


class TestRanker:
    """Testa o Creative Ranker."""

    def test_score_legibility(self):
        """Testa scoring de legibilidade."""
        from jarvis_agency_os.ranker import _score_legibility

        creative_good = {
            "headline": "This is a good headline",
            "cta": "Click Here",
        }

        score = _score_legibility(creative_good)
        assert score > 50, "Headline bem-formado deve ter score > 50"

    def test_score_hierarchy(self):
        """Testa scoring de hierarquia."""
        from jarvis_agency_os.ranker import _score_hierarchy

        creative = {
            "headline": "Main Title",
            "cta": "Action Button",
            "blueprint": "feed_split_editorial"
        }

        score = _score_hierarchy(creative)
        assert score > 0, "Deve ter score positivo"

    def test_rank_creatives(self):
        """Testa ranking de criativos."""
        from jarvis_agency_os.ranker import rank_creatives

        creatives = [
            {
                "headline": "Great Headline One",
                "cta": "Learn More",
                "blueprint": "feed_split_editorial",
                "design_state": "authority",
                "body": "Excellent body copy here"
            },
            {
                "headline": "Another Headline",
                "cta": "Discover",
                "blueprint": "feed_dark_cinematic",
                "design_state": "luxury",
                "body": "Good body text"
            }
        ]

        result = rank_creatives(creatives, top_n=1)
        assert "top" in result
        assert len(result["top"]) > 0
        assert "all_scored" in result
        assert "design_intelligence" in result["all_scored"][0]["score_breakdown"]
        assert "visual_quality" in result["all_scored"][0]["score_breakdown"]
        assert "visual_qa" in result["all_scored"][0]

    def test_ranker_rejects_visual_qa_failures(self):
        """Falha visual crítica deve impedir aprovação por score textual."""
        from jarvis_agency_os.ranker import rank_creatives

        creative = {
            "headline": "Acompanhamento pedagógico com clareza",
            "cta": "Agende avaliação",
            "blueprint": "feed_split_editorial",
            "design_state": "authority",
            "body": "Excelente copy com boa hierarquia.",
            "html": """
            <html>
              <style>.title{color:#6366f1}</style>
              <body>
                <h1>{{HEADLINE}}</h1>
                <a href="#">Agende avaliação</a>
              </body>
            </html>
            """
        }

        result = rank_creatives([creative], top_n=1)
        scored = result["all_scored"][0]

        assert scored["visual_qa"]["status"] == "fail"
        assert scored["action"] == "reject"


class TestVisualQA:
    """Testa os quality gates visuais estáticos."""

    def test_visual_qa_penalizes_unresolved_tokens_and_emoji_icons(self):
        from jarvis_agency_os.visual_qa import evaluate_visual_quality

        creative = {
            "headline": "Seu filho aprende melhor",
            "cta": "Agende uma avaliação",
            "html": """
            <html>
              <style>.icon{color:#6366f1}</style>
              <body>
                <h1>{{HEADLINE}}</h1>
                <button>🎯 Agende uma avaliação</button>
              </body>
            </html>
            """
        }

        result = evaluate_visual_quality(creative)
        codes = {issue["code"] for issue in result["issues"]}

        assert result["status"] == "fail"
        assert "unresolved_tokens" in codes
        assert "emoji_icon" in codes
        assert "default_ai_indigo" in codes

    def test_visual_qa_passes_clean_button_html(self):
        from jarvis_agency_os.visual_qa import evaluate_visual_quality

        creative = {
            "headline": "Acompanhamento pedagógico com clareza",
            "cta": "Agende uma avaliação",
            "html": """
            <html>
              <style>
                :root { --accent: #2f80ed; }
                .cta { background: var(--accent); color: white; }
              </style>
              <body>
                <h1>Acompanhamento pedagógico com clareza</h1>
                <a class="cta" href="#">Agende uma avaliação</a>
                <svg viewBox="0 0 24 24"><path d="M4 12h16"/></svg>
              </body>
            </html>
            """
        }

        result = evaluate_visual_quality(creative)

        assert result["score"] >= 90
        assert result["status"] in {"pass", "review"}

    def test_visual_qa_includes_rendered_layout_issues(self, monkeypatch):
        import jarvis_agency_os.visual_qa as visual_qa

        def fake_rendered_layout(html_path, width=1080, height=1080):
            return {
                "status": "fail",
                "source": "rendered_layout",
                "metrics": {},
                "issues": [
                    {
                        "severity": "critical",
                        "code": "text_clipped",
                        "message": "Texto aparece cortado ou com overflow.",
                        "penalty": 25,
                    }
                ],
            }

        monkeypatch.setattr(visual_qa, "evaluate_rendered_layout", fake_rendered_layout)

        with tempfile.TemporaryDirectory() as tmpdir:
            html_path = os.path.join(tmpdir, "story.html")
            Path(html_path).write_text(
                "<html><body><h1>Headline</h1><a href='#'>Agende uma avaliação</a></body></html>",
                encoding="utf-8",
            )

            result = visual_qa.evaluate_visual_quality({
                "file": html_path,
                "headline": "Headline",
                "cta": "Agende uma avaliação",
            })

        codes = {issue["code"] for issue in result["issues"]}
        assert result["status"] == "fail"
        assert "text_clipped" in codes
        assert result["rendered"]["source"] == "rendered_layout"


class TestDesignIntelligence:
    """Testa a camada de Design Intelligence."""

    def test_resolve_education_profile(self):
        """Educação infantil deve usar o perfil dedicado."""
        from jarvis_agency_os.design_intelligence import resolve_design_profile

        profile = resolve_design_profile({
            "client_name": "Amar",
            "niche": "educação infantil acompanhamento pedagógico",
            "objective": "conversão"
        })

        assert profile["key"] == "educacao_infantil_premium"
        assert "ícones educacionais em SVG line" in " ".join(profile["icon_rules"])

    def test_build_design_brief(self):
        """Briefing visual deve conter quality gates."""
        from jarvis_agency_os.design_intelligence import build_design_brief

        brief = build_design_brief({
            "client_name": "Almeida & Rocha",
            "niche": "advocacia",
            "objective": "autoridade"
        })

        assert "Design Intelligence Brief" in brief
        assert "Quality Gates" in brief
        assert "advocacia_premium" in brief


class TestTemplateRegistry:
    """Testa o catálogo central de templates."""

    def test_normalize_formats(self):
        from jarvis_agency_os.template_registry import normalize_formats

        assert normalize_formats("instagram_feed, stories") == ["feed", "story"]
        assert normalize_formats("carrossel, landing_page") == ["carousel", "landing"]
        assert normalize_formats(None) == ["feed"]

    def test_select_story_template(self):
        from jarvis_agency_os.template_registry import select_templates

        selected = select_templates(
            "educational",
            niche="educação infantil",
            formats=["story"],
        )

        assert selected[0] == "story_education_soft_premium"
        assert "story_premium_editorial" in selected
        assert all(key.startswith("story_") for key in selected)

    def test_select_education_feed_template_first(self):
        from jarvis_agency_os.template_registry import select_templates

        selected = select_templates(
            "educational",
            niche="educação infantil acompanhamento pedagógico",
            formats=["feed"],
        )

        assert selected[0] == "feed_education_soft_premium"

    def test_select_education_carousel_template_first(self):
        from jarvis_agency_os.template_registry import select_templates

        selected = select_templates(
            "safety",
            niche="educação infantil acompanhamento pedagógico",
            formats=["carousel"],
        )

        assert selected[0] == "carousel_education_steps"

    def test_select_legal_story_template_first(self):
        from jarvis_agency_os.template_registry import select_templates

        selected = select_templates(
            "authority",
            niche="advocacia empresarial",
            formats=["story"],
        )

        assert selected[0] == "story_legal_authority"


class TestLandingEngine:
    """Testa geração real de landing pages."""

    def test_generate_landing_page_creates_html_and_manifest(self):
        from jarvis_agency_os.landing_engine import generate_landing_page

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_landing_page(
                workspace_dir=tmpdir,
                context={
                    "client_name": "Amar",
                    "niche": "educação infantil",
                    "whatsapp": "5587999999999",
                    "palette": {
                        "bg_primary": "#FFE8F2",
                        "bg_card": "#FFFFFF",
                        "text_primary": "#12336B",
                        "text_muted": "#607089",
                        "accent": "#ED2B7C",
                        "border_color": "rgba(18,51,107,0.14)",
                    },
                    "design_state_config": {"font_headline": "Outfit"},
                },
                copy_data={
                    "client_name": "Amar",
                    "niche": "educação infantil",
                    "angles": [{
                        "headline_1": "Aprender com",
                        "headline_2": "mais confiança",
                        "body": "Acompanhamento pedagógico com plano claro para cada criança.",
                        "badge": "Acompanhamento pedagógico",
                        "cta": "Agende uma avaliação",
                        "footer_cta": "Atendimento próximo para famílias.",
                        "checklist": ["Mais foco", "Mais autonomia", "Melhor aprendizado"],
                    }],
                },
            )

            assert result["status"] == "success"
            assert result["format"] == "landing"
            assert result["template_key"] == "landing_education_premium"
            assert os.path.exists(result["file"])
            assert os.path.exists(result["manifest"])
            assert result["visual_qa"]["status"] in {"pass", "review", "fail"}
            html = Path(result["file"]).read_text(encoding="utf-8")
            assert "Vamos entender o momento do seu filho?" in html
            assert "avaliação pedagógica" in html

    def test_generate_legal_landing_uses_legal_template(self):
        from jarvis_agency_os.landing_engine import generate_landing_page

        with tempfile.TemporaryDirectory() as tmpdir:
            result = generate_landing_page(
                workspace_dir=tmpdir,
                context={
                    "client_name": "Advocacia Test",
                    "niche": "advocacia empresarial",
                    "palette": {
                        "bg_primary": "#0B1020",
                        "bg_card": "#121826",
                        "text_primary": "#F5F7FA",
                        "text_muted": "#94A3B8",
                        "accent": "#D4AF37",
                        "border_color": "rgba(212,175,55,0.18)",
                    },
                    "design_state_config": {"font_headline": "Outfit"},
                },
                copy_data={
                    "client_name": "Advocacia Test",
                    "niche": "advocacia empresarial",
                    "angles": [{
                        "headline_1": "Segurança jurídica",
                        "headline_2": "para decisões importantes",
                        "body": "Atendimento jurídico com clareza, estratégia e sigilo profissional.",
                        "badge": "Advocacia moderna",
                        "cta": "Fale com especialista",
                        "footer_cta": "Orientação inicial para reduzir riscos.",
                        "checklist": ["Análise de risco", "Estratégia personalizada", "Sigilo profissional"],
                    }],
                },
            )

            assert result["status"] == "success"
            assert result["template_key"] == "landing_legal_premium"
            html = Path(result["file"]).read_text(encoding="utf-8")
            assert "Precisa de uma orientação segura?" in html
            assert "Atuação jurídica com método e sigilo" in html


class TestAssetCatalog:
    """Testa matching inteligente do catálogo global."""

    def test_normalize_text_removes_accents(self):
        from jarvis_agency_os.asset_catalog import normalize_text

        assert normalize_text("Educação Infantil — Clínica") == "educacao infantil clinica"

    def test_match_catalog_entry_uses_synonyms(self):
        from jarvis_agency_os.asset_catalog import match_catalog_entry

        catalog = {
            "clases en vivo": {"page": "PÁGINAS PREMIUM/12 CLASES EN VIVO"},
            "medical": {"page": "PÁGINAS PREMIUM/56 MEDICAL"},
            "global_automation": {"typebot": "ignore.zip"},
        }

        result = match_catalog_entry("educação infantil acompanhamento pedagógico", catalog)

        assert result["status"] == "matched"
        assert result["key"] == "clases en vivo"
        assert "clases" in result["matched_terms"]


class TestExportEngine:
    """Testa o Export Engine."""

    def test_export_manager_creation(self):
        """Testa criação de ExportManager."""
        from jarvis_agency_os.export_engine import ExportManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExportManager(tmpdir)
            assert os.path.exists(manager.export_dir)

    def test_export_formats_defined(self):
        """Testa se todos os formatos de export estão definidos."""
        from jarvis_agency_os.export_engine import EXPORT_FORMATS

        expected_platforms = ["meta_ads", "google_ads", "tiktok_ads", "google_shopping"]
        for platform in expected_platforms:
            assert platform in EXPORT_FORMATS, f"Plataforma {platform} não definida"

    def test_export_campaign_artifacts_creates_manifest(self):
        from jarvis_agency_os.export_engine import export_campaign_artifacts

        with tempfile.TemporaryDirectory() as tmpdir:
            png_path = os.path.join(tmpdir, "winner_story.png")
            Path(png_path).write_bytes(b"fakepng")
            html_path = os.path.join(tmpdir, "landing.html")
            manifest_path = os.path.join(tmpdir, "landing_manifest.json")
            Path(html_path).write_text("<html></html>", encoding="utf-8")
            Path(manifest_path).write_text("{}", encoding="utf-8")

            result = export_campaign_artifacts({
                "winners": {"story": {"client": "Export Test", "blueprint": "story_premium_editorial"}},
                "rendered_winners": {"story": {"status": "success", "path": png_path}},
                "landing": {"file": html_path, "manifest": manifest_path, "client": "Export Test"},
            }, tmpdir)

            assert result["status"] == "success"
            assert os.path.exists(result["manifest_path"])
            assert result["formats"]["story"]["status"] == "success"

    def test_export_campaign_artifacts_copies_carousel_slides(self):
        from jarvis_agency_os.export_engine import export_campaign_artifacts

        with tempfile.TemporaryDirectory() as tmpdir:
            winner = os.path.join(tmpdir, "winner_carousel.png")
            slide_1 = os.path.join(tmpdir, "slide_01.png")
            slide_2 = os.path.join(tmpdir, "slide_02.png")
            Path(winner).write_bytes(b"fakepng")
            Path(slide_1).write_bytes(b"fakepng")
            Path(slide_2).write_bytes(b"fakepng")

            result = export_campaign_artifacts({
                "winners": {"carousel": {"client": "Carousel Export", "blueprint": "carousel_education_steps"}},
                "rendered_winners": {"carousel": {"status": "success", "path": winner}},
                "rendered_carousel_slides": [
                    {"status": "success", "path": slide_1, "slide": 1},
                    {"status": "success", "path": slide_2, "slide": 2},
                ],
                "landing": {},
            }, tmpdir)

            assert result["status"] == "success"
            assert result["formats"]["carousel"]["status"] == "success"
            assert len(result["formats"]["carousel"]["slides"]) == 2
            assert all(os.path.exists(slide["path"]) for slide in result["formats"]["carousel"]["slides"])

    def test_tiktok_export_reports_missing_ffmpeg_for_static_image(self, monkeypatch):
        from jarvis_agency_os import export_engine
        from jarvis_agency_os.export_engine import ExportManager

        monkeypatch.setattr(export_engine.shutil, "which", lambda _name: None)

        with tempfile.TemporaryDirectory() as tmpdir:
            image_path = os.path.join(tmpdir, "story.png")
            Path(image_path).write_bytes(b"fakepng")

            manager = ExportManager(tmpdir)
            result = manager.export_for_tiktok_ads(image_path, "Video Test")

            assert result["status"] == "conversion_unavailable"
            assert result["platform"] == "tiktok_ads"
            assert result["conversion"]["status"] == "unavailable"
            assert "ffmpeg" in result["conversion"]["install_hint"]


class TestAnalyticsDashboard:
    """Testa geração do dashboard analítico."""

    class FakeMemory:
        def get_history(self, limit=200, client=None, design_state=None):
            return [{
                "id": 1,
                "client": "Dashboard Client",
                "niche": "educação",
                "format": "story",
                "blueprint": "story_education_soft_premium",
                "score": 91.4,
                "visual_qa_status": "pass",
                "human_approved": 1,
                "experiment_id": "exp_dashboard",
                "variant_label": "story-v1",
                "impressions": 1000,
                "conversions": 80,
                "spend": 120,
                "file_path": "/tmp/story.html",
            }]

        def get_experiment_report(self, experiment_id):
            return {
                "experiment_id": experiment_id,
                "variant_count": 1,
                "winner": {"variant_label": "story-v1"},
                "variants": [],
                "significance": {"status": "needs_more_data"},
            }

        def get_stats(self):
            return {
                "total_generated": 10,
                "total_approved": 7,
                "approval_rate": 70,
                "avg_score": 88.4,
                "avg_ctr": 0.03,
                "avg_lead_cost": 12.5,
            }

        def get_performance_by_state(self):
            return {
                "safety": {
                    "total_generated": 5,
                    "total_approved": 4,
                    "avg_score": 90,
                    "avg_ctr": 0.04,
                }
            }

        def get_trending_blueprints(self, limit=8):
            return [("story_education_soft_premium", 3, 91.2)]

        def get_winning_creatives(self, niche=None, design_state=None, limit=8):
            return self.get_history(limit=limit)

    def test_dashboard_data_and_html_render(self):
        from jarvis_agency_os.analytics_dashboard import build_dashboard_data, render_dashboard_html

        data = build_dashboard_data(memory=self.FakeMemory(), limit=4)
        html = render_dashboard_html(data)

        assert data["stats"]["total_generated"] == 10
        assert data["experiments"][0]["experiment_id"] == "exp_dashboard"
        assert "JarvisAgency Analytics" in html
        assert "story_education_soft_premium" in html

    def test_write_dashboard_outputs_files(self):
        from jarvis_agency_os.analytics_dashboard import write_dashboard

        with tempfile.TemporaryDirectory() as tmpdir:
            html_path = os.path.join(tmpdir, "dashboard.html")
            json_path = os.path.join(tmpdir, "dashboard.json")

            result = write_dashboard(html_path, json_path=json_path, memory=self.FakeMemory())

            assert result["status"] == "success"
            assert os.path.exists(html_path)
            assert os.path.exists(json_path)


class TestGraphify:
    """Testa o Graphify Engine."""

    def test_process_briefing_with_mock_data(self):
        """Testa processamento de briefing com dados mock."""
        from graphify.engine import process_briefing

        with tempfile.TemporaryDirectory() as tmpdir:
            # Criar briefing mock
            briefing_path = os.path.join(tmpdir, "briefing.txt")
            with open(briefing_path, "w") as f:
                f.write("Cliente: Test Client\n")
                f.write("Nicho: educacao\n")
                f.write("Objetivo: Conversão\n")
                f.write("Formatos: feed, story\n")

            result = process_briefing(tmpdir)

            # Se sucesso, deve ter context_graph
            if "error" not in result:
                assert "context_graph" in result
                assert result["context_graph"]["formats"] == "feed, story"


class TestXquads:
    """Testa o Xquads Copy Engine."""

    def test_validate_copy_constraint(self):
        """Testa validação de constraints de copy."""
        from xquads.engine import _validate_copy

        short_text = "Short"
        result, warnings = _validate_copy(short_text, max_chars=100, field_name="test")

        assert len(warnings) == 0, "Texto curto não deve gerar warnings"
        assert result == short_text

    def test_pedagogical_copy_override(self):
        """Educação infantil deve receber copy própria, não texto de curso genérico."""
        from xquads.engine import generate_copy

        result = generate_copy({
            "client_name": "Amar",
            "niche": "educação infantil acompanhamento pedagógico",
            "design_state": "safety",
        }, "conversão")

        first = result["copy_data"]["angles"][0]
        assert first["headline_1"] == "Acompanhamento pedagógico é"
        assert "futuro do seu filho" in first["headline_2"]
        assert first["cta"] == "Fale com nossa equipe"

    def test_validate_copy_truncation(self):
        """Testa truncamento de copy longo."""
        from xquads.engine import _validate_copy

        long_text = "A" * 150
        result, warnings = _validate_copy(long_text, max_chars=50, field_name="test")

        assert len(warnings) > 0, "Texto longo deve gerar warnings"
        assert len(result) <= 50, "Resultado deve ser truncado"


class TestIntegration:
    """Testes de integração entre componentes."""

    def test_full_pipeline_structure(self):
        """Testa que todos os componentes do pipeline existem."""
        try:
            from jarvis_agency_os.creative_engine import generate_creatives
            from jarvis_agency_os.pipeline import run_campaign_pipeline
            from jarvis_agency_os.ranker import rank_creatives
            from jarvis_agency_os.renderer import render_html_to_png
            from jarvis_agency_os.visual_memory import record_campaign
            from jarvis_agency_os.export_engine import ExportManager
            from graphify.engine import process_briefing
            from xquads.engine import generate_copy

            assert True, "Todos os componentes disponíveis"
        except ImportError as e:
            pytest.fail(f"Falta componente: {e}")

    def test_campaign_pipeline_generates_story_without_rendering(self):
        """Pipeline unificado deve gerar, rankear e aprender em workspace isolado."""
        from jarvis_agency_os.pipeline import run_campaign_pipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_campaign_pipeline(
                client_name="Pipeline Test",
                objective="conversão",
                niche="educação infantil",
                workspace_dir=tmpdir,
                formats="story",
                include_landing=False,
                render_winners=False,
            )

            assert result["status"] == "success"
            assert result["formats"] == ["story"]
            assert result["generation"]["total"] > 0
            assert result["ranking"]["total_evaluated"] > 0
            assert "story" in result["winners"]

    def test_campaign_pipeline_selects_winner_for_each_requested_format(self):
        """Feed e Story não podem competir a ponto de um formato sumir dos vencedores."""
        from jarvis_agency_os.pipeline import run_campaign_pipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_campaign_pipeline(
                client_name="Amar Test",
                objective="conversão",
                niche="educação infantil acompanhamento pedagógico",
                workspace_dir=tmpdir,
                formats="feed,story",
                include_landing=False,
                render_winners=False,
                export_campaign=False,
            )

            assert result["status"] == "success"
            assert set(result["winners"].keys()) == {"feed", "story"}
            assert result["winners"]["feed"]["blueprint"] == "feed_education_soft_premium"
            assert result["winners"]["story"]["blueprint"] == "story_education_soft_premium"
            assert result["winners"]["feed"]["cta"] in {
                "Fale com nossa equipe",
                "Agende avaliação",
                "Falar no WhatsApp",
            }

    def test_campaign_pipeline_generates_education_carousel(self):
        """Carrossel deve ser um formato de campanha selecionável e rankeável."""
        from jarvis_agency_os.pipeline import run_campaign_pipeline

        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_campaign_pipeline(
                client_name="Amar Carousel",
                objective="conversão",
                niche="educação infantil acompanhamento pedagógico",
                workspace_dir=tmpdir,
                formats="carrossel",
                include_landing=False,
                render_winners=False,
                export_campaign=False,
            )

            assert result["status"] == "success"
            assert result["experiment_id"]
            assert result["formats"] == ["carousel"]
            assert "carousel" in result["winners"]
            assert result["winners"]["carousel"]["blueprint"] == "carousel_education_steps"
            assert result["winners"]["carousel"]["width"] == 1080
            assert result["winners"]["carousel"]["height"] == 1080
            assert len(result["carousel_slides"]) == 3
            assert all(slide["format"] == "carousel" for slide in result["carousel_slides"])
            assert all(record["experiment_id"] == result["experiment_id"] for record in result["memory_records"])

    def test_mcp_server_available(self):
        """Testa se MCP server pode ser importado."""
        try:
            from mcp_agent_agency import mcp
            assert mcp is not None
            assert mcp.name == "jarvis_agency"
        except Exception as e:
            pytest.fail(f"MCP server não disponível: {e}")

    def test_local_image_selector_prefers_campaign_photos(self):
        """Fotos de campanha devem ser escolhidas antes de logo/referência."""
        from jarvis_agency_os.creative_engine import _get_image_for_niche

        with tempfile.TemporaryDirectory() as tmpdir:
            assets_dir = os.path.join(tmpdir, "assets")
            os.makedirs(assets_dir)
            logo_path = os.path.join(assets_dir, "amar_logo.png")
            photo_path = os.path.join(assets_dir, "pedagoga_crianca_crop.png")

            Path(logo_path).write_bytes(b"fake")
            Path(photo_path).write_bytes(b"fake")

            selected = _get_image_for_niche("educação infantil", tmpdir)

            assert selected == photo_path

    def test_education_image_selector_uses_project_assets_when_workspace_has_no_photo(self):
        """Campanhas pedagógicas devem preferir foto local do projeto antes de fallback externo."""
        from jarvis_agency_os.creative_engine import _get_image_for_niche

        selected = _get_image_for_niche("educação infantil acompanhamento pedagógico", "/tmp/workspace_sem_foto")

        assert "amar_pedagogico" in selected
        assert selected.endswith("pedagoga_crianca_crop.png") or selected.endswith("nova_cena_pedagogica.png")

    def test_select_blueprints_respects_story_format(self):
        """Creative Engine deve conseguir selecionar templates verticais."""
        from jarvis_agency_os.creative_engine import _select_blueprints

        selected = _select_blueprints(
            "educational",
            niche="educação infantil",
            formats=["story"],
            use_memory=False,
        )

        assert selected[0] == "story_education_soft_premium"
        assert "story_premium_editorial" in selected
        assert all(key.startswith("story_") for key in selected)


# Markers para categorizar testes
def pytest_configure(config):
    config.addinivalue_line("markers", "unit: marca testes unitários")
    config.addinivalue_line("markers", "integration: marca testes de integração")
    config.addinivalue_line("markers", "slow: marca testes lentos")
