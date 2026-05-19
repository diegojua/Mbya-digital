# 📑 `install_manifest.md` — Roteiro de Setup JarvisAgency OS

Este roteiro documenta os passos necessários para configurar as dependências, registrar o servidor MCP e inicializar o ecossistema do **Creative OS** no ambiente do Antigravity.

---

## 🛠️ Passo 1: Preparação do Ambiente Python e Dependências

Instale os pacotes principais do ecossistema e o Playwright necessário para renderização gráfica:

```bash
# 1. Instalar pacotes essenciais do Python
pip install mcp python-dotenv requests fastmcp playwright

# 2. Instalar binários de navegadores headless do Playwright
playwright install chromium
```

---

## 📂 Passo 2: Estrutura de Pastas do Creative OS

A estrutura do projeto centraliza os blueprints, configurações e o motor de geração:

```text
/home/diego/Documentos/Mbya Digital/
├── jarvis_agency_os/
│   ├── __init__.py
│   ├── creative_engine.py      # Motor de hidratação
│   ├── renderer.py             # Renderizador Playwright (HTML -> PNG)
│   ├── ranker.py               # Avaliador de qualidade (QA)
│   ├── visual_memory.py        # Histórico e feedback loop
│   ├── blueprints/             # Templates HTML de ads
│   └── config/                 # Ficheiros de direção de arte (JSON)
├── graphify/                   # Extrator de briefing
├── xquads/                     # Redação e travas de copy
├── mcp_agent_agency.py         # Orquestrador do Servidor MCP
└── workspace/                  # Inputs e outputs das campanhas
```

---

## ⚙️ Passo 3: Configuração das Variáveis de Ambiente (`.env`)

Configure o arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sua_chave_aqui
ANTHROPIC_API_KEY=sua_chave_aqui
INSTAGRAM_ACCESS_TOKEN=seu_token_aqui
INSTAGRAM_ACCOUNT_ID=seu_id_aqui
```

---

## 🔌 Passo 4: Registro do Servidor MCP no Antigravity

Para registrar este servidor de forma a expor as ferramentas `executar_pipeline_completo_saas` e `rodar_campanha_completa` na IDE:

Adicione a entrada abaixo no seu arquivo de configuração global `~/.gemini/antigravity/mcp_config.json`:

```json
{
  "mcpServers": {
    "jarvis-agency-os-enterprise": {
      "command": "python3",
      "args": ["/home/diego/Documentos/Mbya Digital/mcp_agent_agency.py"]
    }
  }
}
```
