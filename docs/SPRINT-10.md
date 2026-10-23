# Sprint 10 — Planejamento Financeiro no Frontend

## Objetivo
Disponibilizar no frontend React a gestão diária dos recursos de orçamento, metas financeiras e transações recorrentes já existentes no backend.

## Entregas
- Página protegida `/management`, com navegação para dashboard e insights.
- Orçamentos por categoria e mês, com limite, gasto calculado, percentual utilizado e saldo restante.
- Criação, edição e exclusão de orçamentos.
- Metas financeiras com valor-alvo, valor acumulado, progresso, saldo restante e prazo.
- Criação, edição e exclusão de metas.
- Cadastro e edição de receitas/despesas recorrentes, com conta, categoria, frequência semanal/mensal/anual, próxima execução e data final opcional.
- Ações para pausar/reativar e excluir recorrências.
- Ação explícita para gerar lançamentos recorrentes vencidos, mostrando quantos foram criados.
- Estados de carregamento, erro, confirmação de exclusão, sucesso e listas vazias.
- Layout responsivo, sem novas dependências externas.

## Rotas
- `/management` — planejamento financeiro (protegida por autenticação).
- Acesso pela ação **Planejamento** no dashboard.
- A navegação para dashboard e insights permanece disponível na página.

## APIs consumidas
- `GET/POST /api/finance/budgets/`
- `PATCH/DELETE /api/finance/budgets/<uuid>/`
- `GET/POST /api/finance/goals/`
- `PATCH/DELETE /api/finance/goals/<uuid>/`
- `GET/POST /api/finance/recurring/`
- `PATCH/DELETE /api/finance/recurring/<uuid>/`
- `POST /api/finance/recurring/generate/`

## Critérios de aceite
- Os registros apresentados pertencem ao usuário autenticado, conforme os filtros de propriedade do backend.
- O usuário pode criar, editar e excluir orçamentos e metas.
- Os orçamentos mostram os valores calculados pelo backend para o mês selecionado.
- O usuário pode criar e editar recorrências, pausar/reativar e solicitar a geração dos lançamentos vencidos.
- Falhas da API e listas vazias são comunicadas na interface.

## Validação pendente
A compilação do frontend e os testes automatizados devem ser executados no ambiente do projeto. Não considerar a sprint pronta para produção até verificar `npm run build` e os testes backend.
