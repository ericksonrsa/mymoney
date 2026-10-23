# Sprint 08 — Notifications & Financial Insights

## Objetivo
Ajudar o usuário a agir sobre o próprio cenário financeiro com alertas persistentes e indicadores mensais calculados a partir dos lançamentos já registrados.

## Escopo entregue
- Notificações persistidas, privadas por usuário e marcáveis como lidas/não lidas.
- Geração idempotente de alertas para orçamento com 80% ou mais de uso.
- Lembretes informativos de lançamentos recorrentes com vencimento nos próximos 7 dias.
- Lembretes de metas financeiras ativas com prazo nos próximos 30 dias.
- Chave de deduplicação por usuário para evitar recriação do mesmo alerta.
- Endpoint de insights mensais: receitas, despesas, saldo do período, variação em relação ao mês anterior, principais categorias de despesa, orçamento por categoria, progresso das metas e recorrências nos próximos 30 dias.
- Endpoints protegidos por autenticação e consultas limitadas ao usuário autenticado.

## API

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/api/finance/notifications/` | Lista notificações e total não lido |
| GET | `/api/finance/notifications/?unread=true` | Lista apenas notificações não lidas |
| POST | `/api/finance/notifications/generate/` | Gera alertas aplicáveis sem duplicar os existentes |
| PATCH | `/api/finance/notifications/<uuid>/read/` | Marca como lida; envie `{"is_read": true}` ou `false` |
| GET | `/api/finance/insights/` | Insights do mês atual |
| GET | `/api/finance/insights/?month=YYYY-MM-DD` | Insights de um mês; qualquer dia informado é normalizado para o primeiro dia do mês |

## Formato de resposta de insights
- `summary`: receita, despesas, saldo líquido e variação percentual contra o mês anterior.
- `top_expense_categories`: até cinco categorias por valor total de despesas.
- `budgets`: valor definido, gasto, saldo restante e percentual utilizado.
- `goals`: progresso das metas ativas.
- `upcoming_recurring`: recorrências ativas previstas para os próximos 30 dias.

Valores monetários são retornados como strings decimais para evitar perda de precisão. Quando o mês anterior não tem receitas/despesas, a variação percentual é `null` (ambos zerados) ou `100` (atual maior que zero).

## Critérios de aceite
- Nenhuma notificação ou insight revela dados de outro usuário.
- Executar a geração de notificações várias vezes não duplica alertas com a mesma chave.
- Notificações podem ser marcadas como lidas ou não lidas.
- Orçamentos a partir de 80% geram aviso; 100% ou mais gera severidade crítica.
- Insights respeitam o mês selecionado e excluem transferências de receitas/despesas.

## Limites
- A geração de notificações é acionada por endpoint; não existe envio de e-mail, SMS ou push nem agendamento automático nesta sprint.
- Insights são calculados sob demanda e não persistem snapshots.
- Não substitui aconselhamento financeiro profissional.
