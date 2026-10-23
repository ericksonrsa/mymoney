# Sprint 04 — Transaction Management & Advanced Filters

## Objetivo

Evoluir o MyMoney de um dashboard com lançamento básico para uma experiência operacional completa de consulta e manutenção das movimentações financeiras.

## Escopo entregue

### Backend — Django + DRF

- Busca textual por descrição e observações usando `q`.
- Filtros por tipo, conta, categoria e intervalo de datas.
- Filtros por valor mínimo e máximo.
- Ordenação segura por data, valor e data de criação.
- Operações de atualização e exclusão mantidas sob `IsAuthenticated` e escopo do usuário.
- Suporte operacional às transferências já previstas no domínio financeiro.

### Frontend — React + Vite + TypeScript

- Pesquisa de movimentações.
- Filtros combináveis por período, tipo, conta, categoria e faixa de valor.
- Paginação da lista de movimentações.
- Edição de transações.
- Exclusão com confirmação.
- Criação de transferências entre contas.
- Campo de observações.
- Diferenciação visual de receitas, despesas e transferências.
- Layout responsivo.

## API

`GET /api/finance/transactions/` aceita os parâmetros:

| Parâmetro | Finalidade |
|---|---|
| `q` | Busca em descrição e observações |
| `type` | `INCOME`, `EXPENSE` ou `TRANSFER` |
| `account` | Filtra pela conta de origem ou destino |
| `category` | Filtra pela categoria |
| `date_from` | Data inicial |
| `date_to` | Data final |
| `amount_min` | Valor mínimo |
| `amount_max` | Valor máximo |
| `ordering` | Data, valor ou criação; ascendente/descendente |

Os endpoints existentes continuam disponíveis:

- `POST /api/finance/transactions/`
- `GET /api/finance/transactions/<uuid>/`
- `PATCH /api/finance/transactions/<uuid>/`
- `DELETE /api/finance/transactions/<uuid>/`

## Regras de negócio

- Uma movimentação somente pode ser consultada ou alterada pelo usuário proprietário.
- Transferências utilizam conta de origem e conta de destino do mesmo usuário.
- Transferências não utilizam categoria.
- Receitas e despesas continuam vinculadas ao tipo correto de categoria.
- Valores continuam positivos.
- Origem e destino de uma transferência devem ser diferentes, conforme as validações do domínio financeiro.

## Critérios de aceite

- [x] Usuário consegue pesquisar movimentações.
- [x] Usuário consegue combinar filtros avançados.
- [x] Lista possui paginação no frontend.
- [x] Usuário consegue editar uma movimentação.
- [x] Usuário consegue excluir uma movimentação com confirmação.
- [x] Usuário consegue registrar transferência entre contas.
- [x] Usuário consegue informar observações.
- [x] Dados de outros usuários continuam isolados.
- [x] Dashboard continua sendo atualizado após alterações nas movimentações.
- [x] Interface permanece utilizável em telas menores.

## Resultado

O Sprint 04 fecha o ciclo operacional básico de movimentações: **criar → consultar → filtrar → editar → excluir → transferir**, mantendo o dashboard analítico do Sprint 03 como visão consolidada.

## Próximo sprint sugerido

Sprint 05 pode introduzir categorias e contas com manutenção completa no frontend, recorrências, importação de extratos e uma camada de orçamento/metas financeiras.
