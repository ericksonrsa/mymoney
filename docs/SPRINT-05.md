# Sprint 05 — Budgets & Financial Goals

## Objetivo

Adicionar planejamento financeiro ao MyMoney, permitindo definir limites mensais de gastos e acompanhar metas financeiras sem perder o isolamento por usuário.

## Escopo entregue

### Orçamentos

- Orçamento mensal por categoria de despesa.
- Valor planejado por categoria e mês.
- Cálculo automático do valor gasto no mês.
- Saldo restante do orçamento.
- Percentual consumido.
- Filtro de orçamentos por mês.
- Edição e exclusão de orçamentos.
- Unicidade de orçamento por usuário, categoria e mês.

### Metas financeiras

- Nome da meta.
- Valor objetivo.
- Valor acumulado atual.
- Percentual de progresso.
- Valor restante.
- Data-alvo opcional.
- Observações e ativação/desativação.
- Edição e exclusão.
- Unicidade do nome da meta por usuário.

## API

### Budgets

- `GET /api/finance/budgets/`
- `POST /api/finance/budgets/`
- `GET /api/finance/budgets/<uuid>/`
- `PATCH /api/finance/budgets/<uuid>/`
- `DELETE /api/finance/budgets/<uuid>/`
- `GET /api/finance/budgets/?month=YYYY-MM-01`

Resposta calculada inclui `spent`, `remaining` e `percentage`.

### Goals

- `GET /api/finance/goals/`
- `POST /api/finance/goals/`
- `GET /api/finance/goals/<uuid>/`
- `PATCH /api/finance/goals/<uuid>/`
- `DELETE /api/finance/goals/<uuid>/`

Resposta calculada inclui `percentage` e `remaining`.

## Regras de negócio

- Todo orçamento e toda meta pertence a um usuário autenticado.
- Orçamentos aceitam somente categorias de despesa do próprio usuário.
- O mês de orçamento deve ser representado pelo primeiro dia do mês.
- Valores planejados devem ser positivos.
- Metas devem possuir valor objetivo positivo.
- O valor atual da meta não pode ser negativo.
- A data-alvo não pode estar no passado.
- Consultas não expõem dados de outros usuários.

## Critérios de aceite

- [x] Criar orçamento mensal.
- [x] Calcular gasto real automaticamente a partir das transações.
- [x] Exibir saldo restante e percentual consumido.
- [x] Filtrar orçamento por mês.
- [x] Criar e editar metas financeiras.
- [x] Calcular progresso e valor restante das metas.
- [x] Manter isolamento por usuário.
- [x] Cobrir regras principais com testes automatizados.

## Próximo sprint sugerido

Sprint 06 pode evoluir para recorrências, importação de OFX/CSV, conciliação bancária e manutenção completa de contas e categorias no frontend.
