# Sprint 03 — Analytics & Financial Dashboard

## Objetivo

Transformar o painel financeiro do MyMoney em uma visão analítica útil para acompanhamento de receitas, despesas, fluxo de caixa, gastos por categoria e evolução patrimonial.

## Escopo entregue

### Backend — Django + DRF

- Dashboard autenticado em `GET /api/finance/dashboard/`.
- Filtros de período por `date_from` e `date_to`.
- Indicadores de saldo, receitas, despesas, transferências e quantidade de transações.
- Agregação de despesas por categoria.
- Série mensal de fluxo de caixa com receitas, despesas e resultado líquido.
- Série mensal de evolução patrimonial.
- Isolamento dos dados por usuário autenticado.
- Cobertura automatizada para agregações e filtros do dashboard.

### Frontend — React + Vite + TypeScript

- Controles de período no dashboard.
- Cards de indicadores financeiros.
- Gráfico de fluxo de caixa.
- Distribuição de gastos por categoria.
- Gráfico de evolução patrimonial.
- Listagens de contas e transações do período.
- Ações rápidas para criação de conta, categoria e transação.
- Renovação automática do access token mantida no fluxo autenticado.

## Critérios de aceite

- [x] Usuário autenticado visualiza somente os próprios dados.
- [x] Dashboard aceita período inicial e final.
- [x] Receitas e despesas são agregadas corretamente.
- [x] Gastos por categoria são calculados no período selecionado.
- [x] Fluxo de caixa mensal apresenta receitas, despesas e resultado líquido.
- [x] Evolução patrimonial apresenta uma série mensal consistente com o saldo inicial e o resultado do período.
- [x] Interface permite retornar rapidamente ao período do mês atual.
- [x] Testes automatizados cobrem isolamento e agregações principais.

## Próximo sprint sugerido

Sprint 04 pode evoluir o módulo para uma experiência completa de lançamento e consulta de movimentações, incluindo edição/exclusão no frontend, paginação, busca, filtros avançados e transferências entre contas.
