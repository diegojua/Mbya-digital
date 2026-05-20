# JarvisAgency Creative OS — Documentação API

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Instalação & Setup](#instalação--setup)
3. [Arquitetura](#arquitetura)
4. [APIs Principais](#apis-principais)
5. [Exemplo End-to-End](#exemplo-end-to-end)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O **JarvisAgency Creative OS** é um sistema determinístico de geração de criativos de altíssima conversão que combina:
- **Graphify**: Extração de contexto de briefing
- **Xquads**: Engine de copy com restrições de tamanho
- **Creative Engine**: Hidratação de blueprints HTML estruturais
- **Ranker**: QA visual em 6 dimensões
- **Renderer**: Renderização Playwright (PNG 1080x1080)
- **Export Engine**: Exportação para Meta Ads, Google Ads, TikTok
- **Visual Memory v2**: Persistência SQLite + feedback loop

---

## 🛠️ Instalação & Setup

### 1. Pré-requisitos
```bash
# Python 3.10+
python3 --version

# Node.js (para Playwright)
node --version npm --version
```

### 2. Clone & Enter Project
```bash
cd "/home/diego/Documentos/Mbya Digital"
```

### 3. Instalar Dependências
```bash
# Instalar requirements
pip install -r requirements.txt

# Instalar binários Playwright
playwright install chromium
```

### 4. Configurar Environment
```bash
# Copiar template
cp .env.example .env

# Editar com suas chaves
nano .env
```

### 5. Validar Setup
```bash
# Validar configs
python3 validate_configs.py

# Testar MCP server
python3 test_mcp_server.py
```

---

## 🏗️ Arquitetura

### Pipeline de Geração

```
┌─────────────┐
│  Briefing   │
└──────┬──────┘
       ↓
┌─────────────────────────┐
│  1. Graphify            │ → Extrai contexto, resolve design state
└──────┬──────────────────┘
       ↓
┌─────────────────────────┐
│  2. Xquads Copy Engine  │ → Gera ângulos de copy com constraints
└──────┬──────────────────┘
       ↓
┌─────────────────────────┐
│  3. Blueprint Selection │ → Seleciona HTML structures compatíveis
└──────┬──────────────────┘
       ↓
┌─────────────────────────┐
│  4. Hydration           │ → Injeta tokens no HTML
└──────┬──────────────────┘
       ↓
┌─────────────────────────┐
│  5. Playwright Renderer │ → Renderiza PNG 1080x1080
└──────┬──────────────────┘
       ↓
┌─────────────────────────┐
│  6. Creative Ranker     │ → Avalia em 6 dimensões
└──────┬──────────────────┘
       ↓
┌─────────────────────────┐
│  7. Visual Memory       │ → Salva em SQLite + feedback
└──────┬──────────────────┘
       ↓
┌─────────────────────────┐
│  8. Export Engine       │ → Exporta para Meta/Google/TikTok
└─────────────────────────┘
```

---

## 📚 APIs Principais

### 1. Creative Engine

```python
from jarvis_agency_os.creative_engine import generate_creatives, generate_rank_and_learn

result = generate_creatives(workspace_dir="/path/to/workspace")
# Retorna: {"generated": [...], "html_files": [...]}

# Rota recomendada: gera, rankeia e grava aprendizado persistente
result = generate_rank_and_learn(workspace_dir="/path/to/workspace", top_n=2)
# Retorna: {"generation": {...}, "ranking": {...}, "memory_records": [...]}
```

**Parâmetros:**
- `workspace_dir`: Caminho contendo `briefing.txt`

**Retorno:**
```json
{
  "generated": [
    {
      "blueprint": "feed_split_editorial",
      "design_state": "authority",
      "headline": "...",
      "file": "/path/to/creative.html"
    }
  ]
}
```

### 2. Ranker

```python
from jarvis_agency_os.ranker import rank_creatives

result = rank_creatives(creatives, top_n=3)
# Retorna: {"top": [...], "all_scored": [...]}
```

**Dimensões de Scoring (6):**
- Legibilidade (20%)
- Hierarquia Visual (20%)
- Visibilidade do CTA (20%)
- Constraint Compliance (15%)
- Design State Alignment (15%)
- Batch Diversity (10%)

### 3. Renderer

```python
from jarvis_agency_os.renderer import render_html_to_png

result = render_html_to_png(
    html_path="/path/to/file.html",
    output_path="/path/to/output.png",
    width=1080, height=1080
)
# Retorna: {"status": "success", "path": "..."}
```

### 4. Export Engine

```python
from jarvis_agency_os.export_engine import ExportManager

manager = ExportManager(workspace_dir)

# Exportar para Meta Ads
result = manager.export_for_meta_ads(
    creative_path="/path/to/creative.png",
    campaign_name="Padaria Artesanal",
    adset_name="Feed 1080x1080",
    targeting={"age": "25-45", "interests": ["food", "premium"]}
)
```

### 5. Visual Memory v2

```python
from jarvis_agency_os.visual_memory_v2 import get_memory

memory = get_memory()

# Registrar campanha
memory.record_campaign(
    client="Padaria XYZ",
    niche="padaria",
    objective="Vendas Online",
    design_state="luxury",
    blueprint="feed_split_editorial",
    score=87.5,
    headline="Pão artesanal fresco todo dia",
    cta="Reservar Fornada",
    approved=True,
    ctr=0.045,
    lead_cost=12.50
)

# Obter estatísticas
stats = memory.get_stats()
print(stats)
# {
#   "total_generated": 42,
#   "total_approved": 38,
#   "approval_rate": 90.5,
#   "avg_score": 84.3,
#   "top_design_state": "luxury"
# }

# Obter performance por estado
perf = memory.get_performance_by_state()

# Obter contexto aprendido para orientar novas criações
context = memory.get_learning_context(niche="padaria", design_state="luxury")
# {
#   "best_blueprint": "feed_fullbleed_overlay",
#   "blueprints": [{"blueprint": "...", "avg_score": 98.0}],
#   "top_creatives": [...]
# }

# Cleanup records antigos
deleted = memory.cleanup_old_records(days=90)

# Exportar backup
backup_path = memory.export_to_json()
```

#### Feedback Humano

Use quando o gestor aprovar, reprovar ou marcar uma arte como preferida. Isso pesa no aprendizado futuro.

```python
memory.set_human_feedback(
    campaign_id=5,
    approved=True,
    label="preferido",
    notes="Boa hierarquia, CTA forte e visual mais premium"
)
```

Também é possível localizar por arquivo ou hash:

```python
memory.set_human_feedback(
    file_path="workspace/generated_creatives/padaria_feed_v1.html",
    approved=False,
    label="reprovado",
    notes="Texto pequeno demais no mobile"
)
```

#### Performance Real

Use depois que a campanha rodar no Meta Ads, Google Ads ou WhatsApp. Se `ctr` e `lead_cost` não forem enviados, a memória calcula automaticamente quando houver dados suficientes.

```python
memory.record_performance(
    campaign_id=5,
    impressions=12000,
    clicks=480,
    conversions=36,
    spend=306.00,
    revenue=1800.00
)
# ctr = 480 / 12000 = 0.04
# lead_cost = 306 / 36 = 8.50
```

#### Criativos Vencedores

Combina score interno, aprovação humana, CTR, custo por lead e conversões.

```python
winners = memory.get_winning_creatives(
    niche="padaria",
    design_state="luxury",
    limit=3
)

for creative in winners:
    print(creative["blueprint"], creative["learning_score"])
```

#### CLI com Aprendizado

```bash
python3 -m jarvis_agency_os.creative_engine --workspace workspace --learn --top-n 2
```

Na próxima geração, o Jarvis consulta a memória e pode priorizar o blueprint vencedor:

```text
Memória priorizou blueprint: feed_fullbleed_overlay
```

### 6. MCP Server

```python
from mcp_agent_agency import mcp

# Ferramenta 1: Pipeline completo
result = executar_pipeline_completo_saas(
    nome_cliente="Padaria Artesanal",
    objetivo="Conversão de Vendas",
    nicho="padaria"
)

# Ferramenta 2: Campanha integrada
result = rodar_campanha_completa(
    nome_cliente="Clínica Odontológica",
    objetivo="Agendamentos",
    nicho="odonto"
)
```

---

## 🚀 Exemplo End-to-End

### Passo 1: Criar Briefing

```bash
cat > workspace/briefing.txt << 'EOF'
Cliente: Padaria Artesanal da Vila
Nicho: padaria
Objetivo: Vendas Online de Assinatura
Detalhes: Vender assinatura mensal de pão artesanal fresco
Localização: São Paulo, SP
WhatsApp: 5511987654321
Logo_icone: 🥖
Logo_texto: PADARIA ARTESANAL
Logo_subtitulo: Pão Fresco Todo Dia
EOF
```

### Passo 2: Executar Pipeline

```python
#!/usr/bin/env python3
"""
exemplo_end_to_end.py — Execução completa do pipeline
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from jarvis_agency_os.creative_engine import generate_creatives
from jarvis_agency_os.ranker import rank_creatives
from jarvis_agency_os.renderer import render_html_to_png
from jarvis_agency_os.export_engine import ExportManager
from jarvis_agency_os.visual_memory_v2 import get_memory

WORKSPACE_DIR = os.path.join(os.path.dirname(__file__), "workspace")

def main():
    print("🚀 Pipeline JarvisAgency: Padaria Artesanal")
    print("=" * 60)

    # 1. Gerar criativos
    print("\n📦 [1/5] Gerando criativos...")
    gen_result = generate_creatives(WORKSPACE_DIR)
    if "error" in gen_result:
        print(f"❌ Erro: {gen_result['error']}")
        return

    generated = gen_result["generated"]
    print(f"✅ {len(generated)} criativos gerados")

    # 2. Rankear
    print("\n🏆 [2/5] Avaliando qualidade...")
    rank_result = rank_creatives(generated, top_n=2)
    top = rank_result["top"]

    for i, creative in enumerate(top, 1):
        print(f"  #{i} {creative['blueprint']} (Score: {creative['score']})")

    # 3. Renderizar
    print("\n📸 [3/5] Renderizando PNG...")
    best = top[0]
    output_png = os.path.join(WORKSPACE_DIR, "final_creative.png")
    render_result = render_html_to_png(best["file"], output_png)

    if render_result["status"] == "success":
        print(f"✅ PNG salvo: {output_png}")
    else:
        print(f"⚠️  Fallback: {render_result.get('message')}")

    # 4. Exportar para plataformas
    print("\n🚀 [4/5] Exportando para plataformas de anúncios...")
    manager = ExportManager(WORKSPACE_DIR)

    # Meta Ads
    meta_result = manager.export_for_meta_ads(
        creative_path=output_png,
        campaign_name="padaria_assinatura",
        adset_name="feed_1080",
        targeting={
            "age": "25-55",
            "interests": ["food", "organic", "local_business"],
            "locations": ["São Paulo", "Brazil"]
        }
    )
    print(f"  ✅ Meta Ads: {meta_result.get('status', 'error')}")

    # Google Ads
    google_result = manager.export_for_google_ads(
        creative_path=output_png,
        campaign_name="padaria_assinatura",
        ad_group="assinatura_feed",
        keywords=["pão artesanal", "assinatura pão", "pão fresco"]
    )
    print(f"  ✅ Google Ads: {google_result.get('status', 'error')}")

    # 5. Salvar em Visual Memory
    print("\n🧠 [5/5] Salvando em Visual Memory...")
    memory = get_memory()
    memory.record_campaign(
        client="Padaria Artesanal da Vila",
        design_state=best["design_state"],
        blueprint=best["blueprint"],
        score=best["score"],
        headline=best["headline"],
        approved=True,
        ctr=0.032,  # Hipotético
        lead_cost=8.50
    )

    stats = memory.get_stats()
    print(f"  ✅ Registrado")
    print(f"     Total gerado: {stats['total_generated']}")
    print(f"     Total aprovado: {stats['total_approved']}")
    print(f"     Score médio: {stats['avg_score']}")

    print("\n" + "=" * 60)
    print("🎉 Pipeline concluído com sucesso!")
    print(f"\nOutputs:")
    print(f"  • PNG: {output_png}")
    print(f"  • Meta Ads Export: {meta_result.get('export_path', 'N/A')}")
    print(f"  • Google Ads Export: {google_result.get('export_path', 'N/A')}")

if __name__ == "__main__":
    main()
```

### Passo 3: Executar

```bash
python3 exemplo_end_to_end.py
```

---

## 🔧 Troubleshooting

### Problema: "Playwright não instalado"
```bash
# Solução:
playwright install chromium
```

### Problema: "Config file not found"
```bash
# Solução: Validar estrutura
python3 validate_configs.py
```

### Problema: "MCP server won't start"
```bash
# Solução: Testar imports
python3 test_mcp_server.py
```

### Problema: "Image dimensions not optimized"
```bash
# Solução: Blueprint requer 1080x1080
# Os blueprints estão otimizados para essa dimensão
```

---

## 📊 Monitoramento & Análise

### Dashboards Disponíveis

1. **Performance por Design State**
   ```python
   memory.get_performance_by_state()
   ```

2. **Blueprints em Tendência**
   ```python
   memory.get_trending_blueprints(limit=5)
   ```

3. **Histórico de Campanhas**
   ```python
   memory.get_history(limit=20, client="Padaria XYZ")
   ```

4. **Snapshot Diário**
   ```python
   memory.create_snapshot()
   ```

5. **Exportar Backup**
   ```python
   backup_path = memory.export_to_json()
   ```

---

## 📞 Suporte

Para problemas ou dúvidas:
1. Consulte `validate_configs.py` para validação
2. Execute `test_mcp_server.py` para diagnosticar
3. Verifique logs em `workspace/` e `jarvis_agency_os/memory/`

---

**Última atualização:** 19 de maio de 2026
