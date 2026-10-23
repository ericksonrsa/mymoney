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

### Frontend

- Dashboard financeiro protegido por JWT.
- Cards de saldo, receitas, despesas e transações.
- Listagem de contas.
- Listagem de transações.
- Formulários de criação de conta, categoria e transação.
- Filtros por período.
- Renovação automática do access token.

### Regras de negócio

- Toda informação financeira pertence a um usuário autenticado.
- Uma transação não pode utilizar conta ou categoria de outro usuário.
- Receitas exigem categoria de receita.
- Despesas exigem categoria de despesa.
- Transferências exigem conta de destino do mesmo usuário e não utilizam categoria.
- Origem e destino de uma transferência devem ser diferentes.
- Valores das transações devem ser positivos.

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
