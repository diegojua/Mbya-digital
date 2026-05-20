# JarvisAgency OS Pipeline

Rota canônica atual:

```bash
./jarvisagency pipeline "Amar" "conversão" --nicho "educação infantil" --formatos feed,story
```

O pipeline executa:

- briefing estruturado em `workspace/briefing.txt`;
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
- `landing/`
- `manifests/campaign_export_manifest.json`

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

## Direção Técnica

Use `jarvis_agency_os.pipeline.run_campaign_pipeline()` como entrada principal em novas integrações. Evite criar fluxos paralelos que chamem Graphify, Xquads, Ranker e Landing Engine manualmente.
