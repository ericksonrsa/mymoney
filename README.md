# MyMoney

Sistema de controle financeiro pessoal desenvolvido com Django (backend), PostgreSQL, React + Vite (frontend) e Docker.

## Sprints

- **Sprint 01** — estrutura inicial do projeto.
- **Sprint de Autenticação** — Django REST Framework + JWT/SimpleJWT.
- **Sprint 02** — contas, categorias e transações.
- **Sprint 03** — analytics e dashboard.
- **Sprint 04** — gestão de transações e filtros avançados.
- **Sprint 05** — orçamentos e metas financeiras.
- **Sprint 06** — transações recorrentes e importação bancária CSV.
- **Sprint 07** — regras de categorização inteligente e reconciliação bancária.
- **Sprint 08** — notificações persistentes e insights financeiros mensais.
- **Sprint 09** — integração visual de notificações e insights no frontend React.
- **Sprint 10** — telas de gestão de orçamentos, metas financeiras e transações recorrentes.
- **Sprint 11** — integração contínua, checagens automatizadas e testes de regressão.\n- **Sprint 12** — faturas consolidadas com créditos, débitos, saldo líquido e acompanhamento de status.

A documentação detalhada de cada sprint está em `docs/`.

## Sprint 06 — Recurring Transactions & Bank Import

O Sprint 06 adiciona automação operacional ao domínio financeiro:

### Transações recorrentes

- Frequências semanal, mensal e anual.
- Próxima execução e data final opcional.
- Geração idempotente de lançamentos vencidos.
- Desativação automática ao fim da série.
- Isolamento por usuário.

### Importação bancária CSV

- Upload de CSV UTF-8.
- Delimitadores `,`, `;` e tabulação.
- Cabeçalhos em português e inglês para data, descrição, valor e tipo.
- Decimal com `,` ou `.`.
- Pré-visualização antes da confirmação.
- Detecção de duplicidades.
- Confirmação atômica.
- Auditoria por lote e linha de importação.
- Associação automática à primeira categoria ativa compatível.

### API — Sprint 06

| Método | Endpoint | Finalidade |
|---|---|---|
| GET/POST | `/api/finance/recurring/` | Listar/criar recorrência |
| GET/PATCH/DELETE | `/api/finance/recurring/<uuid>/` | Gerenciar recorrência |
| POST | `/api/finance/recurring/generate/` | Gerar lançamentos vencidos |
| GET | `/api/finance/imports/` | Listar lotes de importação |
| POST multipart | `/api/finance/imports/upload/` | Upload e pré-visualização CSV |
| POST | `/api/finance/imports/<uuid>/confirm/` | Confirmar importação |

A especificação completa está em [`docs/SPRINT-06.md`](docs/SPRINT-06.md).

## Configuração local

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

Configure `VITE_API_URL` no frontend quando a API não estiver em `http://localhost:8000/api`.

Não coloque valores reais de produção no repositório. Copie `.env.example` para `.env` e configure os segredos localmente.

### Testes

```bash
cd backend
python manage.py test accounts finance
```

## Sprint 07 — Intelligent Categorization & Reconciliation

O Sprint 07 adiciona regras explícitas, auditáveis e determinísticas para sugerir categorias e facilitar a conferência de extratos:

- Regras por trecho literal na descrição ou observações, sem execução de regex.
- Prioridade configurável (menor número tem precedência).
- Validação de propriedade e tipo da categoria.
- Prévia de reconciliação com correspondências exatas e possíveis candidatas por data/valor.
- Confirmação inteligente de importação, com categoria encontrada por regra e fallback para categoria ativa compatível.
- Isolamento por usuário e processamento atômico.

### API — Sprint 07

| Método | Endpoint | Finalidade |
|---|---|---|
| GET/POST | `/api/finance/categorization/rules/` | Listar/criar regras |
| GET/PATCH/DELETE | `/api/finance/categorization/rules/<uuid>/` | Gerenciar regra |
| GET | `/api/finance/imports/<uuid>/reconcile/` | Prévia de reconciliação |
| POST | `/api/finance/imports/<uuid>/confirm-smart/` | Confirmar lote com regras |

A especificação completa está em [`docs/SPRINT-07.md`](docs/SPRINT-07.md).


## Sprint 08 — Notifications & Financial Insights

- Alertas idempotentes de orçamento a partir de 80% de uso.
- Lembretes para transações recorrentes nos próximos 7 dias e metas com prazo nos próximos 30 dias.
- Caixa de notificações com filtro de não lidas e marcação de leitura.
- Insights mensais de receitas, despesas, saldo líquido, variação contra o mês anterior, principais categorias, orçamentos, metas e recorrências.
- APIs autenticadas com isolamento por usuário.

| Método | Endpoint | Finalidade |
|---|---|---|
| GET | `/api/finance/notifications/` | Listar notificações |
| POST | `/api/finance/notifications/generate/` | Gerar alertas sem duplicidade |
| PATCH | `/api/finance/notifications/<uuid>/read/` | Marcar como lida/não lida |
| GET | `/api/finance/insights/` | Consultar insights do mês |

Detalhes em [`docs/SPRINT-08.md`](docs/SPRINT-08.md).


## Sprint 09 — Dashboard & Notification Center

- Central de notificações integrada ao dashboard, com contagem de não lidas, filtros e ação para marcar como lida.
- Ação para solicitar geração de alertas financeiros, usando os endpoints do Sprint 08.
- Página de insights financeiros com seleção de mês, receitas, despesas, resultado líquido, variação mensal, categorias, orçamento, metas e lançamentos recorrentes próximos.
- Navegação entre o dashboard e os insights; estados de carregamento, erros e telas vazias.

Detalhes em [`docs/SPRINT-09.md`](docs/SPRINT-09.md).


## Sprint 12 — Faturas consolidadas

- Consolida vários lançamentos de receita/crédito e despesa/débito em uma fatura sem duplicar os lançamentos originais.
- Apresenta total de créditos, total de débitos, saldo líquido e detalhamento dos lançamentos.
- Permite definir período e vencimento, filtrar por status, marcar como paga/reabrir e excluir a fatura mantendo os lançamentos.
- Aplica isolamento por usuário e validações para evitar transferências internas, lançamentos de terceiros e associação duplicada.
- API autenticada em `/api/finance/invoices/`; tela protegida em `/invoices`.

Detalhes em [`docs/SPRINT-12.md`](docs/SPRINT-12.md).
