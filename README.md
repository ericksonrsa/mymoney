# MyMoney

Sistema de controle financeiro pessoal desenvolvido com Django (backend), PostgreSQL, React + Vite (frontend) e Docker.

## Sprint 01

Estrutura inicial do projeto:

- Arquitetura definida.
- Organização do monorepo (`backend/` e `frontend/`).
- Definição das funcionalidades do MVP.
- Preparação para autenticação, contas, categorias e transações.

## Sprint de Autenticação

A autenticação da API foi implementada no backend com Django REST Framework e JWT (SimpleJWT).

### Endpoints

| Método | Endpoint | Autenticação | Finalidade |
|---|---|---|---|
| POST | `/api/auth/register/` | Não | Cria usuário |
| POST | `/api/auth/login/` | Não | Retorna access e refresh tokens |
| POST | `/api/auth/token/refresh/` | Não | Renova o access token |
| GET | `/api/auth/me/` | Bearer JWT | Retorna o usuário autenticado |

### Segurança

- Senhas são armazenadas pelo Django usando hashing; nunca são persistidas em texto puro.
- Segredos e credenciais são fornecidos por variáveis de ambiente.
- Access token padrão: 15 minutos.
- Refresh token padrão: 7 dias.
- Rotação e blacklist de refresh tokens habilitadas.
- CORS permite explicitamente as origens configuradas.
- `IsAuthenticated` é a permissão padrão da API.

## Sprint 02 — Financial Management

O Sprint 02 entrega o primeiro domínio funcional completo do MyMoney: gestão de contas, categorias e transações financeiras sobre a base de autenticação.

### Backend

- `Account`: contas correntes, poupança, cartão de crédito, dinheiro e investimentos.
- `Category`: categorias de receitas e despesas.
- `Transaction`: receitas, despesas e transferências.
- IDs financeiros em UUID.
- Isolamento completo por usuário autenticado.
- Cálculo de saldo por conta.
- Validações de integridade para contas, categorias e transferências.
- Índices por usuário/data e usuário/tipo.
- Restrições de unicidade por usuário.

### API

| Método | Endpoint | Finalidade |
|---|---|---|
| GET/POST | `/api/finance/accounts/` | Listar/criar contas |
| GET/PUT/PATCH/DELETE | `/api/finance/accounts/<uuid>/` | Gerenciar conta |
| GET/POST | `/api/finance/categories/` | Listar/criar categorias |
| GET/PUT/PATCH/DELETE | `/api/finance/categories/<uuid>/` | Gerenciar categoria |
| GET/POST | `/api/finance/transactions/` | Listar/criar transações |
| GET/PUT/PATCH/DELETE | `/api/finance/transactions/<uuid>/` | Gerenciar transação |
| GET | `/api/finance/dashboard/` | Resumo financeiro do usuário |

A especificação completa está em [`docs/SPRINT-02.md`](docs/SPRINT-02.md).

## Sprint 03 — Analytics & Dashboard

O Sprint 03 consolida a camada analítica do MyMoney:

- Filtros de período por data inicial e final.
- Indicadores de saldo, receitas, despesas e transações.
- Fluxo de caixa mensal com receitas, despesas e resultado líquido.
- Gastos agrupados por categoria.
- Evolução patrimonial mensal.
- Componentes visuais para gráficos e distribuição de despesas.
- Testes automatizados para agregações, isolamento de dados e filtros de período.

A especificação completa está em [`docs/SPRINT-03.md`](docs/SPRINT-03.md).

## Sprint 04 — Transaction Management & Advanced Filters

O Sprint 04 transforma o lançamento de movimentações em uma experiência operacional completa:

- Busca textual por descrição e observações.
- Filtros combináveis por período, tipo, conta, categoria e valor.
- Ordenação controlada.
- Paginação, edição e exclusão no frontend.
- Transferências entre contas.
- Interface responsiva.

A especificação completa está em [`docs/SPRINT-04.md`](docs/SPRINT-04.md).

## Sprint 05 — Budgets & Financial Goals

O Sprint 05 adiciona a camada de planejamento financeiro:

### Orçamentos

- Orçamento mensal por categoria de despesa.
- Cálculo automático do gasto real a partir das transações.
- Valor restante e percentual consumido.
- Filtro por mês.
- Edição e exclusão.
- Unicidade por usuário, categoria e mês.

### Metas financeiras

- Valor objetivo e valor acumulado.
- Percentual de progresso.
- Valor restante.
- Data-alvo opcional.
- Observações e status ativo/inativo.
- Edição e exclusão.
- Isolamento por usuário.

### API

| Método | Endpoint | Finalidade |
|---|---|---|
| GET/POST | `/api/finance/budgets/` | Listar/criar orçamentos |
| GET/PATCH/DELETE | `/api/finance/budgets/<uuid>/` | Gerenciar orçamento |
| GET/POST | `/api/finance/goals/` | Listar/criar metas |
| GET/PATCH/DELETE | `/api/finance/goals/<uuid>/` | Gerenciar meta |

A especificação completa está em [`docs/SPRINT-05.md`](docs/SPRINT-05.md).

### Configuração local

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
