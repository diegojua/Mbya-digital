# Mapeamento do fluxo `jarvis_agency_os`

## 1. Entrada principal no MCP

Arquivo: `mcp_agent_agency.py`

- `executar_pipeline_completo_saas(nome_cliente, objetivo, nicho, formatos)`
  - chama `jarvis_agency_os.pipeline.run_campaign_pipeline(...)`
- `rodar_campanha_completa(nome_cliente, objetivo, nicho)`
  - chama `executar_pipeline_completo_saas(...)`
  - depois executa fluxo adicional de Open-Design + Deer-Flow

---

## 2. `jarvis_agency_os.pipeline.run_campaign_pipeline`

Este é o fluxo canônico do Creative OS.

Passos:

1. `_write_briefing(...)`
   - grava `workspace/briefing.txt`
2. `generate_creatives(...)`
   - `jarvis_agency_os.creative_engine.generate_creatives`
3. `rank_creatives(...)`
   - `jarvis_agency_os.ranker.rank_creatives`
4. `get_memory().record_creative_batch(...)`
   - `jarvis_agency_os.visual_memory_v2.get_memory`
5. `_render_winners(...)`
   - `jarvis_agency_os.renderer.render_html_to_png`
6. `_render_carousel_slides(...)`
   - renderiza carrossel se houver formato `carousel`
7. `generate_landing_page(...)` quando `include_landing=True`
   - `graphify.engine.process_briefing`
   - `xquads.engine.generate_copy`
   - `jarvis_agency_os.asset_catalog.match_catalog_entry`
   - `jarvis_agency_os.landing_engine.generate_landing_page`
8. `export_campaign_artifacts(...)`
   - `jarvis_agency_os.export_engine`

---

## 3. `jarvis_agency_os.creative_engine`

Função principal: `generate_creatives(...)`

Fluxo interno:

1. `process_briefing(workspace_dir)`
   - extrai contexto e define `design_state`
2. `_apply_art_direction(ctx)`
   - aplica direção de arte de `config/art_directions.json`
3. `apply_design_intelligence(ctx)`
4. `normalize_formats(...)` + `select_templates(...)`
5. `generate_copy(ctx, objective)`
   - chama `xquads` para gerar copy/tokens
6. `_hydrate_blueprint(...)`
   - injeta tokens no HTML do blueprint
7. grava HTML em `workspace/generated_creatives`

Também há `generate_rank_and_learn(...)` para geração + ranking + aprendizado.

---

## 4. `jarvis_agency_os.landing_engine`

Função principal: `generate_landing_page(...)`

- Gera landing page HTML real + manifesto JSON
- Usa blueprint de landing premium conforme nicho
- Preenche tokens com copy, palette e conteúdo de nicho
- Salva em `workspace/generated_landings`

---

## 5. Integrações diretas usadas por `mcp_agent_agency.py`

- `jarvis_agency_os.asset_catalog.match_catalog_entry`
- `jarvis_agency_os.renderer.render_html_to_png`
- `jarvis_agency_os.landing_engine.generate_landing_page`

Esses módulos participam também do fluxo de Open-Design e Deer-Flow dentro de `rodar_campanha_completa`.

---

## 6. Resumo do fluxo end-to-end

`mcp_agent_agency.py`
- `executar_pipeline_completo_saas`
  → `jarvis_agency_os.pipeline.run_campaign_pipeline`
    → `jarvis_agency_os.creative_engine.generate_creatives`
      → `graphify`
      → `xquads`
      → `blueprints` + `hydrate`
    → `jarvis_agency_os.ranker.rank_creatives`
    → `jarvis_agency_os.visual_memory_v2.get_memory`
    → `jarvis_agency_os.renderer.render_html_to_png`
    → `jarvis_agency_os.landing_engine.generate_landing_page`
    → `jarvis_agency_os.export_engine.export_campaign_artifacts`

`rodar_campanha_completa`
- `executar_pipeline_completo_saas`
- `open_design_inject`
  → `asset_catalog.match_catalog_entry`
  → `landing_engine.generate_landing_page`
- `deer_flow.deploy_typebot_flow`
- `deer_flow.dispatch_for_approval`

---

## 7. Arquivos-chave do `jarvis_agency_os`

- `creative_engine.py`
- `pipeline.py`
- `renderer.py`
- `ranker.py`
- `visual_memory.py` / `visual_memory_v2.py`
- `landing_engine.py`
- `export_engine.py`
- `asset_catalog.py`
- `template_registry.py`
- `design_intelligence.py`
- `blueprints/`
- `config/`
