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
