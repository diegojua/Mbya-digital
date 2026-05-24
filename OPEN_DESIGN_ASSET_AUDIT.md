# Auditoria Open Design Para Landpages E Posts

Objetivo: identificar quais partes da pasta `open-design/` podem melhorar as landpages e as imagens/posts do JarvisAgency OS.

## Resumo Executivo

O `open-design/` nao deve ser copiado inteiro para o pipeline. Ele e uma biblioteca de referencia com quatro grupos muito uteis:

1. **Regras de qualidade visual** em `open-design/craft/`.
2. **Design systems prontos** em `open-design/design-systems/`.
3. **Skills e receitas de landing/post** em `open-design/skills/`.
4. **Prompts e assets de imagem editorial** em `open-design/skills/open-design-landing/assets/`.

Prioridade de aproveitamento:

| Prioridade | Origem | Uso recomendado |
| :--- | :--- | :--- |
| Alta | `craft/anti-ai-slop.md` | Virar regras do nosso `visual_qa.py` e checklist de revisão. |
| Alta | `skills/open-design-landing/assets/imagegen-prompts.md` | Base para prompts profissionais de imagens de landpages e posts. |
| Alta | `skills/open-design-landing/assets/image-manifest.json` | Modelo para registrar slots de imagem por projeto. |
| Alta | `skills/open-design-landing/styles.css` | Referencia para landpages editoriais premium. |
| Media | `skills/social-carousel/SKILL.md` | Melhorar carrossel e sequencia narrativa dos posts. |
| Media | `skills/image-poster/SKILL.md` | Estruturar prompt de imagem: assunto, luz, paleta, camera, evitar. |
| Media | `design-systems/{premium,professional,editorial,luxury,enterprise,neon,futuristic,warm-editorial}` | Mapear para art directions por nicho. |
| Baixa | `apps/landing-page/` | Inspiracao de componentes; nao copiar agora. |
| Baixa | `docs/screenshots/` e `docs/assets/` | Referencias visuais/QA, nao fonte direta do produto. |

## Arquivos Mais Valiosos

### 1. Regras Anti-Template

Arquivos:

```text
open-design/craft/anti-ai-slop.md
open-design/craft/color.md
open-design/craft/typography-hierarchy.md
open-design/craft/typography-hierarchy-editorial.md
open-design/craft/animation-discipline.md
```

O que aproveitar:

- Bloquear cores default de IA, especialmente indigo/purple-blue.
- Penalizar gradiente generico de confianca.
- Bloquear emoji como icone.
- Penalizar metricas inventadas.
- Controlar excesso de accent color.
- Exigir hierarquia tipografica real.

Impacto no nosso sistema:

- Entrar em `jarvis_agency_os/visual_qa.py`.
- Entrar em `jarvis_agency_os/config/constraints.json`.
- Virar criterios extras no `creative_ranker.json`.

### 2. Landing Editorial Premium

Arquivos:

```text
open-design/skills/open-design-landing/SKILL.md
open-design/skills/open-design-landing/README.md
open-design/skills/open-design-landing/styles.css
open-design/skills/open-design-landing/example.html
open-design/skills/open-design-landing/schema.ts
open-design/skills/open-design-landing/scripts/compose.ts
open-design/skills/open-design-landing/scripts/placeholder.ts
```

O que aproveitar:

- Estrutura de landing editorial com secoes numeradas.
- Papel/textura, colagem editorial, serif italic e grids assimetricos.
- `data-od-id` para futuras revisoes/comentarios por bloco.
- Placeholder SVG profissional quando nao houver imagem real.
- Composer baseado em JSON tipado, bom modelo para evoluir nosso `landing_engine.py`.

Uso recomendado:

- Criar um blueprint oficial novo: `landing_editorial_atelier.html`.
- Criar um modo de landing premium para marcas/produtos/tecnologia.
- Nao substituir todos os templates atuais; usar como familia visual adicional.

### 3. Prompts Profissionais De Imagem

Arquivos:

```text
open-design/skills/open-design-landing/assets/imagegen-prompts.md
open-design/skills/open-design-landing/assets/image-manifest.json
open-design/skills/open-design-landing/assets/hero.png
open-design/skills/open-design-landing/assets/about.png
open-design/skills/open-design-landing/assets/capabilities.png
open-design/skills/open-design-landing/assets/method-1.png
open-design/skills/open-design-landing/assets/method-2.png
open-design/skills/open-design-landing/assets/method-3.png
open-design/skills/open-design-landing/assets/method-4.png
open-design/skills/open-design-landing/assets/lab-1.png
open-design/skills/open-design-landing/assets/lab-2.png
open-design/skills/open-design-landing/assets/lab-3.png
open-design/skills/open-design-landing/assets/lab-4.png
open-design/skills/open-design-landing/assets/lab-5.png
open-design/skills/open-design-landing/assets/work-1.png
open-design/skills/open-design-landing/assets/work-2.png
open-design/skills/open-design-landing/assets/testimonial.png
open-design/skills/open-design-landing/assets/cta.png
```

O que aproveitar:

- Prompt em camadas: style anchor + variaveis da marca + composicao por slot.
- Manifesto de slots com dimensoes e nomes fixos.
- Linguagem de colagem editorial premium.
- Assets de exemplo para calibrar o padrao visual desejado.

Uso recomendado no nosso padrao de imagens:

```text
workspace/project_images/<project_slug>/assets/
workspace/project_images/<project_slug>/generated/
workspace/project_images/<project_slug>/renders/
workspace/project_images/<project_slug>/exports/
```

Possivel modulo novo:

```text
jarvis_agency_os/image_direction.py
```

Responsabilidades:

- Receber `client_name`, `niche`, `format`, `design_state`.
- Selecionar um style anchor.
- Criar prompts para hero, post feed, story e carrossel.
- Salvar prompts/manifests em `workspace/project_images/<project_slug>/`.

### 4. Skills Para Posts E Carrossel

Arquivos:

```text
open-design/skills/social-carousel/SKILL.md
open-design/skills/image-poster/SKILL.md
open-design/skills/magazine-poster/SKILL.md
open-design/skills/html-ppt-xhs-post/SKILL.md
open-design/skills/html-ppt-xhs-white-editorial/SKILL.md
```

O que aproveitar:

- `social-carousel`: narrativa sequencial em 3 cards, cada card se sustenta sozinho.
- `image-poster`: prompt estruturado para imagem final.
- `magazine-poster`: poster editorial com hierarquia forte.
- `xhs-post`: boa referencia para posts verticais/card editorial.

Uso recomendado:

- Melhorar `carousel_education_steps.html`.
- Criar `carousel_professional_series.html`.
- Criar prompts de imagem por formato:
  - feed 1:1
  - story 9:16
  - carousel 1:1 sequencial

### 5. Design Systems Mais Uteis

A pasta `open-design/design-systems/` tem 142 sistemas. Os melhores para nosso uso atual:

```text
open-design/design-systems/professional/DESIGN.md
open-design/design-systems/premium/DESIGN.md
open-design/design-systems/editorial/DESIGN.md
open-design/design-systems/luxury/DESIGN.md
open-design/design-systems/enterprise/DESIGN.md
open-design/design-systems/neon/DESIGN.md
open-design/design-systems/futuristic/DESIGN.md
open-design/design-systems/warm-editorial/DESIGN.md
open-design/design-systems/clean/DESIGN.md
open-design/design-systems/modern/DESIGN.md
```

Mapeamento sugerido:

| Nosso caso | Design system base |
| :--- | :--- |
| Agencia de marketing | `professional`, `premium`, `enterprise` |
| Agencia de turismo | `warm-editorial`, `editorial`, `clean` |
| MbyaClaw / tech local-first | `futuristic`, `neon`, `enterprise` |
| Advocacia premium | `luxury`, `professional`, `editorial` |
| Educacao/pedagogico | `warm-editorial`, `clean`, `professional` |
| Posts institucionais | `professional`, `premium` |
| Posts manifesto/autoridade | `editorial`, `publication`, `magazine-poster` |

## O Que Nao Vale Integrar Agora

Evitar por enquanto:

```text
open-design/apps/web/
open-design/apps/desktop/
open-design/apps/daemon/
open-design/e2e/
open-design/node_modules/
open-design/.od/
open-design/.git/
```

Motivo:

- Sao infraestrutura do produto Open Design, nao assets diretos.
- Trazem complexidade de Node/desktop desnecessaria para o JarvisAgency OS neste momento.
- Podemos reaproveitar ideias, mas nao precisamos acoplar runtime.

## Plano De Integracao Recomendado

### Fase 1 — Regras de qualidade

Implementar:

- Importar regras de `anti-ai-slop.md` para `visual_qa.py`.
- Penalizar:
  - gradientes genericos;
  - emoji como icone;
  - excesso de accent;
  - card/tile com cara de template;
  - imagens externas genéricas quando existir asset local.

Resultado esperado:

- Menos posts com aparencia de HTML/card generico.
- Ranking favorece imagens finais mais profissionais.

### Fase 2 — Image Direction

Criar:

```text
jarvis_agency_os/image_direction.py
jarvis_agency_os/config/image_directions.json
```

Campos sugeridos:

```json
{
  "style_anchor": "...",
  "formats": {
    "feed": {"ratio": "1:1", "composition": "..."},
    "story": {"ratio": "9:16", "composition": "..."},
    "landing_hero": {"ratio": "16:9", "composition": "..."}
  },
  "avoid": ["generic stock photo", "messy text", "watermark"]
}
```

Resultado esperado:

- Cada post passa a ter uma direcao visual clara antes do HTML/render.
- As imagens geradas seguem um padrao profissional por projeto.

### Fase 3 — Blueprint editorial premium

Criar:

```text
jarvis_agency_os/blueprints/landing_editorial_atelier.html
jarvis_agency_os/blueprints/creatives/feed_editorial_poster.html
jarvis_agency_os/blueprints/creatives/carousel_professional_series.html
```

Basear em:

```text
open-design/skills/open-design-landing/styles.css
open-design/skills/social-carousel/SKILL.md
open-design/skills/magazine-poster/SKILL.md
```

Resultado esperado:

- Landpages mais autorais.
- Posts mais parecidos com campanha de agencia do que template HTML.

## Conclusao

Os arquivos que mais vao ajudar imediatamente sao:

```text
open-design/craft/anti-ai-slop.md
open-design/craft/color.md
open-design/craft/typography-hierarchy-editorial.md
open-design/skills/open-design-landing/assets/imagegen-prompts.md
open-design/skills/open-design-landing/assets/image-manifest.json
open-design/skills/open-design-landing/styles.css
open-design/skills/social-carousel/SKILL.md
open-design/skills/image-poster/SKILL.md
open-design/skills/magazine-poster/SKILL.md
open-design/design-systems/professional/DESIGN.md
open-design/design-systems/premium/DESIGN.md
open-design/design-systems/editorial/DESIGN.md
open-design/design-systems/luxury/DESIGN.md
open-design/design-systems/enterprise/DESIGN.md
open-design/design-systems/neon/DESIGN.md
open-design/design-systems/futuristic/DESIGN.md
open-design/design-systems/warm-editorial/DESIGN.md
```

Recomendacao: comecar pela Fase 1 e Fase 2. Elas melhoram tanto landpages quanto posts sem depender de migrar o app Open Design inteiro.
