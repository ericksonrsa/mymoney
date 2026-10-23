# Sprint 12 — Faturas e consolidação de lançamentos

## Objetivo
Permitir que o usuário reúna vários lançamentos financeiros de crédito/receita e débito/despesa em uma única fatura ou demonstrativo, com totais consolidados e acompanhamento de status.

## Entregas
- Modelo de fatura com título, período, vencimento opcional, observações e status (em aberto, paga ou cancelada).
- Associação de vários lançamentos existentes a uma fatura sem duplicar nem modificar os lançamentos originais.
- Cálculo de créditos, débitos, saldo líquido (débitos menos créditos) e quantidade de lançamentos.
- Validação para impedir lançamentos de outro usuário, transferências entre contas e associação do mesmo lançamento a mais de uma fatura.
- Endpoints autenticados e filtragem por proprietário.
- Tela responsiva para criar faturas, selecionar lançamentos, consultar detalhes, filtrar por status, marcar como paga/reabrir e excluir a fatura.
- Testes de API para totais, isolamento, autenticação, duplicidade e período inválido.

## API
| Método | Endpoint | Finalidade |
|---|---|---|
| GET / POST | `/api/finance/invoices/` | Listar faturas ou criar uma consolidação |
| GET / PATCH / DELETE | `/api/finance/invoices/<uuid>/` | Consultar, atualizar status/dados ou excluir uma fatura |

Exemplo de criação:
```json
{
  "title": "Fatura principal — outubro",
  "period_start": "2026-10-01",
  "period_end": "2026-10-31",
  "due_date": "2026-11-10",
  "notes": "Consolidação mensal",
  "transactions": ["<uuid-do-lancamento-1>", "<uuid-do-lancamento-2>"]
}
```

A resposta inclui `credit_total`, `debit_total`, `net_total`, `transaction_count` e `transaction_items`.

## Regras de negócio
- Créditos correspondem a transações do tipo `INCOME`; débitos correspondem a `EXPENSE`.
- O saldo líquido é calculado como débitos menos créditos. Um valor positivo indica saldo líquido a pagar; um negativo indica créditos superiores aos débitos.
- Transferências internas são excluídas da consolidação para evitar contar movimentações entre contas como receita/despesa.
- Marcar como paga atualiza o status da fatura; não cria automaticamente uma nova transação de pagamento. Isso evita efeitos duplicados no saldo da conta. O registro do pagamento pode ser tratado em uma evolução futura.
- Excluir a fatura remove apenas o agrupamento; os lançamentos financeiros originais permanecem intactos.

## Como validar
```bash
cd backend
python manage.py test finance.test_sprint12 --verbosity 2
python manage.py makemigrations --check --dry-run
``

No frontend:
```bash
cd frontend
npm install
npm run build
``
