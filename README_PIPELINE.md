# JarvisAgency OS Pipeline

Rota canônica atual:

```bash
./jarvisagency pipeline "Amar" "conversão" --nicho "educação infantil" --formatos feed,story
```

Também aceita carrossel:

```bash
./jarvisagency pipeline "Amar" "conversão" --nicho "educação infantil" --formatos feed,story,carrossel
```

O pipeline executa:

- briefing estruturado em `workspace/briefing.txt`;
- criação de `experiment_id` para rastrear variantes A/B;
- geração de criativos HTML;
- QA visual estático e renderizado;
- ranking;
- memória visual v2;
- render dos campeões;
- landing page HTML real;
- export final da campanha.

## Saídas

Os principais arquivos ficam em:

- `workspace/generated_creatives/`
- `workspace/generated_landings/`
- `workspace/rendered_winners/`
- `workspace/exports/<campanha_timestamp>/`

A pasta `exports/<campanha_timestamp>/` organiza:

- `feed/`
- `story/`
- `carousel/`
- `landing/`
- `manifests/campaign_export_manifest.json`

Quando `carrossel` é solicitado, o pipeline também expõe `carousel_slides`
e renderiza múltiplos arquivos em `rendered_winners/carousel/` antes de copiar
o pacote para `exports/<campanha_timestamp>/carousel/`.

No log final do comando, confira:

- `Carrossel renderizado: 3/3 slides`
- `Export final: workspace/exports/<campanha_timestamp>`
- `Pacote de carrossel: 3 slides no export`

## QA Manual

Auditar um HTML:

```bash
./jarvisagency qa amar_pedagogico/story_acompanhamento_pedagogico.html --formato story --cta "Agende uma avaliação"
```

Status possíveis:

- `pass`: pode seguir;
- `review`: revisar visualmente;
- `fail`: não usar como referência/aprendizado.

## Feedback Humano

Registrar aprovação/reprovação:

```bash
./jarvisagency feedback --file workspace/generated_creatives/arquivo.html --label approved --notes "boa hierarquia"
./jarvisagency feedback --file workspace/generated_creatives/arquivo.html --label rejected --notes "texto muito perto da borda"
```

## Experimentos A/B

Cada execução de `run_campaign_pipeline()` retorna `experiment_id` e grava as
variações como `feed-v1`, `story-v2`, `carousel-v3` na Visual Memory v2.
Depois de inserir métricas reais com `record_performance()`, use
`get_experiment_report(experiment_id)` para comparar variantes por conversão,
custo por conversão e uma leitura aproximada de significância.

## Dashboard Analítico

Gerar um painel HTML local com KPIs, performance por design state, blueprints em
alta, criativos vencedores e experimentos A/B:

```bash
./jarvisagency dashboard --output workspace/analytics_dashboard.html --json workspace/analytics_dashboard.json
```

O dashboard lê a Visual Memory v2 (`visual_memory.db`) e não depende de Grafana,
Superset ou APIs externas. O JSON exportado pode alimentar essas ferramentas depois.

## Vídeo Para Reels/TikTok

O `ExportManager.export_for_tiktok_ads()` aceita MP4 pronto ou PNG/JPG renderizado.
Quando `ffmpeg` está instalado, imagens estáticas viram MP4 vertical de 15 segundos
em 1080x1920. Sem `ffmpeg`, o retorno vem como `conversion_unavailable` com o
comando de conversão sugerido.

## Fila De Publicação

Preparar uma publicação para Meta/Instagram sem enviar nada por acidente:

```bash
./jarvisagency publish-plan --asset workspace/rendered_winners/winner_story.png --caption "Nova campanha no ar" --campaign "Amar"
```

O comando salva um job em `workspace/publication_queue.jsonl`. Para testar um
webhook em dry-run, use `--dispatch-now`; para envio real, configure um endpoint
e passe `--live`.

## Direção Técnica

Use `jarvis_agency_os.pipeline.run_campaign_pipeline()` como entrada principal em novas integrações. Evite criar fluxos paralelos que chamem Graphify, Xquads, Ranker e Landing Engine manualmente.
