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
- direção de imagem por nicho inspirada no Open Design;
- manifesto de prompts/assets em `workspace/project_images/<nome_do_projeto>/manifest.json`;
- criação de `experiment_id` para rastrear variantes A/B;
- geração de criativos HTML como arquivo-fonte;
- QA visual estático e renderizado;
- ranking;
- memória visual v2;
- render dos campeões em PNG profissional;
- landing page HTML real;
- export final da campanha.

## Saídas

Os principais arquivos ficam em:

- `workspace/generated_creatives/`
- `workspace/generated_landings/`
- `workspace/project_images/<nome_do_projeto>/manifest.json`
- `workspace/project_images/<nome_do_projeto>/prompts/*.txt`
- `workspace/project_images/<nome_do_projeto>/renders/`
- `workspace/project_images/<nome_do_projeto>/exports/<timestamp>/`

A pasta `workspace/project_images/<nome_do_projeto>/exports/<timestamp>/` organiza:

- `feed/`
- `story/`
- `carousel/`
- `landing/`
- `manifests/campaign_export_manifest.json`

Quando `carrossel` é solicitado, o pipeline também expõe `carousel_slides`
e renderiza múltiplos arquivos em `workspace/project_images/<nome_do_projeto>/renders/carousel/`
antes de copiar o pacote para `exports/<timestamp>/carousel/`.

No log final do comando, confira:

- `Image Direction: marketing_agency` ou outra direção resolvida;
- `Image manifest: workspace/project_images/<nome_do_projeto>/manifest.json`;
- `Carrossel renderizado: 3/3 slides`
- `Imagem feed/story pronta: workspace/project_images/<nome_do_projeto>/renders/...`
- `Export final: workspace/project_images/<nome_do_projeto>/exports/<timestamp>`
- `Pacote de carrossel: 3 slides no export`

## Direção De Imagem

Gerar ou inspecionar prompts sem rodar a campanha completa:

```bash
./jarvisagency image-direction --cliente "Mbya Marketing" --nicho "agência de marketing performance" --formatos feed,landing
```

Salvar o manifesto e os prompts no workspace:

```bash
./jarvisagency image-direction --cliente "Mbya Marketing" --nicho "agência de marketing performance" --formatos feed,landing --save
```

O comando cria:

- `workspace/project_images/<slug>/manifest.json`
- `workspace/project_images/<slug>/prompts/feed.txt`
- `workspace/project_images/<slug>/prompts/landing_hero.txt`
- `workspace/project_images/<slug>/assets/`
- `workspace/project_images/<slug>/generated/`
- `workspace/project_images/<slug>/renders/`
- `workspace/project_images/<slug>/exports/`

Esses prompts são a ponte entre o Open Design e os blueprints HTML: primeiro se define a direção visual, depois o HTML consome `{{IMAGE_URL}}`.

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

## Backup Da Memória

Criar backup completo da Visual Memory v2 em JSON e réplica SQLite:

```bash
./jarvisagency memory-backup --output-dir workspace/backups
```

O backup JSON facilita inspeção e migração futura para PostgreSQL. A cópia
SQLite preserva o banco pronto para restauração local.

## Vídeo Para Reels/TikTok

O `ExportManager.export_for_tiktok_ads()` aceita MP4 pronto ou PNG/JPG renderizado.
Quando `ffmpeg` está instalado, imagens estáticas viram MP4 vertical de 15 segundos
em 1080x1920. Sem `ffmpeg`, o retorno vem como `conversion_unavailable` com o
comando de conversão sugerido.

## Fila De Publicação

Preparar uma publicação para Meta/Instagram sem enviar nada por acidente:

```bash
./jarvisagency publish-plan --asset workspace/project_images/amar/renders/winner_story.png --caption "Nova campanha no ar" --campaign "Amar"
```

O comando salva um job em `workspace/publication_queue.jsonl`. Para testar um
webhook em dry-run, use `--dispatch-now`; para envio real, configure um endpoint
e passe `--live`.

## Direção Técnica

Use `jarvis_agency_os.pipeline.run_campaign_pipeline()` como entrada principal em novas integrações. Evite criar fluxos paralelos que chamem Graphify, Xquads, Ranker e Landing Engine manualmente.

Para posts, trate `workspace/generated_creatives/*.html` como fonte técnica. A imagem final para publicar deve ser sempre o PNG em `workspace/project_images/<nome_do_projeto>/renders/` ou o pacote em `workspace/project_images/<nome_do_projeto>/exports/`.
