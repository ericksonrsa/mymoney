# Sprint 06 — Recurring Transactions & Bank Import

## Objetivo
Automatizar lançamentos recorrentes e criar uma camada segura de importação bancária por CSV, com pré-visualização, detecção de duplicidades e confirmação transacional.

## Escopo

### 1. Transações recorrentes
- Frequências semanal, mensal e anual.
- Próxima execução e data final opcional.
- Ativação/desativação automática quando a série termina.
- Geração idempotente: a mesma execução não cria uma transação duplicada.
- Isolamento por usuário.

### 2. Importação bancária CSV
- Upload de CSV UTF-8.
- Delimitadores `,`, `;` e tabulação.
- Cabeçalhos aceitos em português e inglês: data, descrição, valor e tipo.
- Valores com decimal `,` ou `.`.
- Pré-visualização antes da confirmação.
- Detecção de duplicidades por conta, data, descrição, valor e tipo.
- Confirmação em transação atômica.
- Associação automática à primeira categoria ativa compatível com o tipo.
- Lote e linhas de importação preservados para auditoria.

## API

| Método | Endpoint | Finalidade |
|---|---|---|
| GET/POST | `/api/finance/recurring/` | Listar/criar recorrência |
| GET/PATCH/DELETE | `/api/finance/recurring/<uuid>/` | Gerenciar recorrência |
| POST | `/api/finance/recurring/generate/` | Gerar lançamentos vencidos |
| GET | `/api/finance/imports/` | Listar lotes do usuário |
| POST multipart | `/api/finance/imports/upload/` | Enviar CSV e gerar prévia |
| POST | `/api/finance/imports/<uuid>/confirm/` | Confirmar importação |

## Regras de negócio

- Nenhuma conta, categoria, recorrência ou lote de outro usuário pode ser acessado.
- Recorrências de transferência não são aceitas nesta versão.
- Recorrências de receita/despesa exigem categoria do mesmo tipo.
- Importações nunca sobrescrevem transações existentes.
- Linhas duplicadas são marcadas como `DUPLICATE` e não são importadas.
- Linhas inválidas ficam em `ERROR` e não bloqueiam a pré-visualização das demais linhas.
- A confirmação é atômica por lote.

## Testes

O Sprint 06 cobre geração recorrente, isolamento por usuário, prévia CSV, detecção de duplicidades e confirmação de importação.

## Próximo sprint sugerido

**Sprint 07 — Categorization & Reconciliation Intelligence**: regras automáticas de categorização, conciliação assistida, matching por similaridade e revisão de lançamentos importados.
