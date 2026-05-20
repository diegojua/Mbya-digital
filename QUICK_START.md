## 🎯 Começar Agora

### ⚡ Quick Start (5 minutos)

```bash
cd "/home/diego/Documentos/Mbya Digital"

# 1. Instalar
pip install -r requirements.txt
playwright install chromium

# 2. Validar
python3 validate_configs.py    # Deve mostrar: ✅ TODOS OS CONFIGS VÁLIDOS (3/3)

# 3. Testar
python3 test_mcp_server.py     # Deve mostrar: ✅ MCP Server Test: PASSED

# 4. Executar demo
python3 exemplo_end_to_end.py  # Pipeline completo com briefing de exemplo
```

---

## 📚 Documentação

| Arquivo | Descrição |
|---------|-----------|
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | APIs completas de cada componente |
| [RELATORIO_MELHORIAS.md](RELATORIO_MELHORIAS.md) | Relatório detalhado de todas as melhorias |
| [architecture_manifest.md](architecture_manifest.md) | Arquitetura do Creative OS |
| [install_manifest.md](install_manifest.md) | Setup original (referência) |

---

## 🧪 Validação Local

```bash
# Validar configs JSON
python3 validate_configs.py

# Testar MCP server
python3 test_mcp_server.py

# Rodar testes (requer pytest)
# pip install pytest pytest-cov
# python3 -m pytest tests/ -v
```

---

## 🚀 Deploy Automático (GitHub)

Ao fazer push para `main` ou `develop`:

```yaml
Jobs executados automaticamente:
├── Test (Python 3.10, 3.11, 3.12)
├── Lint (black, flake8, mypy)
└── Deploy Check (validation + build)
```

Ver workflow em: `.github/workflows/tests.yml`

---

## 🔑 Chaves Criadas

1. **Export Engine** — Exporte para Meta/Google/TikTok
   ```python
   from jarvis_agency_os.export_engine import ExportManager
   manager = ExportManager(workspace_dir)
   manager.export_for_meta_ads(...)
   ```

2. **Visual Memory v2** — SQLite + Analytics
   ```python
   from jarvis_agency_os.visual_memory_v2 import get_memory
   memory = get_memory()
   memory.get_stats()  # Performance dashboard
   ```

3. **Config Validator** — JSON schema check
   ```bash
   python3 validate_configs.py
   ```

4. **MCP Tester** — Diagnóstico rápido
   ```bash
   python3 test_mcp_server.py
   ```

---

## ✅ Checklist Final

- [x] Requirements.txt com versões exatas
- [x] Ambiente Python testado e validado
- [x] Assets consolidados (sem duplicação)
- [x] Configs validados (3/3 OK)
- [x] MCP server funcional
- [x] Export engine para 4 plataformas
- [x] Testes + CI/CD automático
- [x] Visual Memory v2 com SQLite
- [x] Documentação completa
- [x] Exemplo end-to-end executável

---

## 📞 Troubleshooting Rápido

### "Playwright não instalado"
```bash
playwright install chromium
```

### "Imports falhando"
```bash
python3 test_mcp_server.py  # Mostra quais imports falham
```

### "Config inválido"
```bash
python3 validate_configs.py  # Mostra qual config está quebrado
```

### "MCP server won't start"
```python
# Debug:
from mcp_agent_agency import mcp
print(mcp.name)  # Deve mostrar: jarvis_agency
```

---

## 🎓 Recursos

- **Visual Memory Analytics:** `memory.get_stats()` → Dashboard completo
- **Performance Tracking:** `memory.get_performance_by_state()` → By design state
- **Trending Analysis:** `memory.get_trending_blueprints()` → Top performers
- **Export Manifest:** `workspace/exports/export_manifest.json` → Histórico de exports

---

**Última atualização:** 19 de maio de 2026
**Status:** 🟢 Production Ready
