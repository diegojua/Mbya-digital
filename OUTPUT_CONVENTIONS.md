# Output Conventions

Este repositorio tem tres tipos de saida. Todo modelo deve escolher um deles antes de criar arquivos.

## 1. Prototipos de landpage para analise

Use somente:

```text
development_landpages/<slug>/index.html
```

Exemplos:

```text
development_landpages/marketing-agency/index.html
development_landpages/tourism-agency/index.html
development_landpages/mbyaclaw/index.html
```

Regras:

- O hub de analise fica em `development_landpages/index.html`.
- Cada nova landpage de teste deve ser uma pasta propria com `index.html`.
- Nao criar landpage solta na raiz do projeto.
- Nao criar landpage em `jarvis_agency_os/workspace/output_code`.
- Nao criar prototipo dentro de `workspace/generated_landings`; essa pasta e saida automatica do pipeline.

## 2. Blueprints oficiais do gerador

Use somente:

```text
jarvis_agency_os/blueprints/landing_<nome>.html
```

Regras:

- Um blueprint oficial deve ser registrado em `jarvis_agency_os/landing_engine.py`.
- Blueprints sao templates hidratados por tokens como `{{CLIENT_NAME}}`, `{{NICHE}}`, `{{CTA_TEXT}}` e `{{IMAGE_URL}}`.
- Nao adicionar blueprint se a pagina for apenas uma exploracao visual.

## 3. Saidas geradas pelo pipeline

O pipeline escreve HTML/manifestos automaticamente em:

```text
workspace/generated_creatives/
workspace/generated_landings/
```

O pipeline escreve imagens somente em:

```text
workspace/project_images/<project_slug>/
```

Regras:

- Modelos nao devem editar manualmente essas pastas para criar uma nova pagina.
- Conteudo dessas pastas pode ser apagado/regerado pelo pipeline.
- Para gerar uma landing oficial, chame `generate_landing_page()` em vez de copiar HTML manualmente.
- Para gerar, renderizar, exportar ou receber imagens, use apenas `workspace/project_images/<project_slug>/`.

## 4. Imagens, screenshots e assets

Use um unico caminho raiz para qualquer imagem:

```text
workspace/project_images/<project_slug>/
```

Dentro da pasta do projeto, use subpastas simples:

```text
workspace/project_images/<project_slug>/assets/      # imagens recebidas ou usadas pela campanha
workspace/project_images/<project_slug>/generated/   # imagens criadas por IA ou scripts
workspace/project_images/<project_slug>/prompts/     # prompts por slot visual
workspace/project_images/<project_slug>/renders/     # PNG renderizado de HTML/criativo
workspace/project_images/<project_slug>/screenshots/ # capturas QA
workspace/project_images/<project_slug>/exports/     # arte final pronta para envio/publicacao
```

Regras:

- Toda imagem nova deve estar dentro de `workspace/project_images/<project_slug>/`.
- Todo prompt de imagem deve estar em `workspace/project_images/<project_slug>/prompts/`.
- Todo projeto/campanha com direção de imagem deve ter `workspace/project_images/<project_slug>/manifest.json`.
- O `<project_slug>` deve ser o nome do projeto/campanha em slug, por exemplo `mbyaclaw`, `amar_pedagogico`, `vortex_marketing`.
- Nao salvar imagem solta na raiz do projeto.
- Nao salvar imagem solta em `workspace/`.
- Nao salvar imagem em `development_landpages/`, exceto se for apenas referencia textual/HTML sem arquivo binario.
- Nao salvar imagem em `jarvis_agency_os/workspace/output_code/`.
- Prototipos devem referenciar imagens por caminho relativo para `workspace/project_images/<project_slug>/assets/` quando precisarem de imagem local.

## Pastas que nao devem receber landpages

```text
jarvis_agency_os/workspace/output_code/
barbearia-landing/
workspace/generated_landings/  # exceto pelo pipeline
workspace/generated_images/
workspace/rendered_winners/
workspace/exports/
workspace/campaign_assets/
workspace/*.png
workspace/*.jpg
workspace/*.jpeg
workspace/*.webp
development_landpages/*/assets/
development_landpages/screenshots/
raiz do repositorio/
```

Se um modelo precisar entregar codigo React/TSX experimental, ele deve criar uma pasta explicita dentro de `development_landpages/<slug>/` ou pedir confirmacao antes.
