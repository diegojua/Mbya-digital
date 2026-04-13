# Workflow Detalhado

## Entrada Esperada
Entrada minima:
- objetivo do produto ou feature
- plataformas alvo
- contexto tecnico conhecido
- restricoes
- prazo ou expectativa, se existir

Se a entrada for incompleta:
1. completar com defaults seguros
2. registrar a decisao
3. explicitar riscos residuais

## STATE 1: IDEA_INTAKE
Objetivo:
- transformar uma ideia em escopo inicial claro

Saida minima:
- problema
- publico
- proposta de valor
- plataformas
- restricoes
- riscos iniciais

## STATE 2: PRD_GENERATION
Objetivo:
- gerar definicao funcional do produto

Obrigatorio:
- objetivo de negocio
- personas
- features
- requisitos funcionais
- requisitos nao funcionais
- KPIs
- riscos
- escopo de entrega

Regra:
- mesmo em pedidos tecnicos, gerar um PRD minimo

## STATE 3: SDD_GENERATION
Objetivo:
- transformar o PRD em desenho tecnico executavel

Obrigatorio:
- arquitetura
- stack
- modulos
- contratos entre modulos
- APIs
- modelo de dados
- auth e autorizacao
- observabilidade
- escalabilidade
- ADRs

Regra:
- o SDD e a fonte da verdade tecnica

## STATE 4: TASK_BREAKDOWN
Objetivo:
- decompor o SDD em tarefas executaveis

Obrigatorio:
- task id
- titulo
- owner
- dependencias
- prioridade
- estimativa
- done criteria

## STATE 5: EXECUTION_PLANNING
Objetivo:
- decidir ordem de execucao
- definir paralelizacao
- identificar caminho critico

Obrigatorio:
- plano serial
- plano paralelo
- riscos de integracao

## STATE 6: PARALLEL_DEVELOPMENT
Objetivo:
- implementar modulos e plataformas em paralelo quando houver independencia

Regras:
1. todo agente respeita PRD e SDD
2. qualquer desvio relevante vira decision record
3. todo output deve apontar entregas, testes e dependencias

## STATE 7: INTEGRATION
Objetivo:
- unificar entregas
- validar contratos
- resolver conflitos de interface, API e estado

Obrigatorio:
- status de integracao
- conflitos resolvidos
- riscos remanescentes

## STATE 8: QA_VALIDATION
Objetivo:
- validar comportamento e criterios de aceite

Obrigatorio:
- testes executados ou planejados
- gaps de validacao
- risco residual

## STATE 9: SECURITY_AUDIT
Objetivo:
- validar postura minima de seguranca e compliance

Obrigatorio:
- secrets
- auth
- autorizacao
- input validation
- dependency risk
- dados sensiveis
- compliance basico

## STATE 10: RELEASE_BUILD
Objetivo:
- preparar artefatos de release

Obrigatorio:
- versao
- changelog
- status de build
- artefatos previstos

## STATE 11: DEPLOYMENT
Objetivo:
- preparar e executar deploy quando aplicavel

Obrigatorio:
- ambiente alvo
- precondicoes
- estrategia de rollout
- rollback plan
- status final

Regra:
- se nao houver informacao suficiente, nao marcar deploy como concluido
- usar deploy-ready ou deploy-blocked

## STATE 12: REPORTING
Objetivo:
- consolidar tudo em relatorio executivo e operacional

Obrigatorio:
- estado por fase
- artefatos gerados
- pendencias
- riscos
- proximos passos

## Defaults Inteligentes
Se o usuario nao especificar stack:
- mobile cross-platform: Expo + React Native + TypeScript strict
- backend: NestJS + PostgreSQL
- web: Next.js + TypeScript strict
- analytics: eventos essenciais do funil
- auth: fluxo seguro com validacao e autorizacao por papeis quando aplicavel

## Regras de Qualidade
- evitar complexidade desnecessaria
- preferir arquitetura simples e extensivel
- testes para fluxos criticos
- instrumentacao minima para operacao
- naming consistente
- contratos claros
- output deterministico

## Regras de Seguranca
- nunca assumir secrets hardcoded
- nao expor credenciais
- validar input
- aplicar menor privilegio
- registrar risco residual

## Regras de Growth
Todo produto com interface de usuario deve prever no minimo:
- acquisition event
- activation event
- conversion event
- retention signal

## Regra de Bloqueio
Quando nao for possivel concluir uma etapa:
1. registrar blocker
2. explicar impacto
3. declarar fallback
4. apontar proxima acao para destravar