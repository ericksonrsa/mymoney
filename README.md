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

### Fluxo

1. O frontend envia usuário e senha para `/api/auth/login/`.
2. Django valida as credenciais usando o sistema de autenticação nativo.
3. O servidor retorna um access token e um refresh token.
4. O frontend envia `Authorization: Bearer <access_token>` nas APIs protegidas.
5. Quando o access token expira, o frontend usa `/api/auth/token/refresh/` para obter outro.
6. O endpoint `/api/auth/me/` usa `request.user` e exige `IsAuthenticated`.

### Segurança

- Senhas são armazenadas pelo Django usando seu mecanismo de hashing; nunca são persistidas em texto puro.
- `DJANGO_SECRET_KEY`, senha do PostgreSQL e demais credenciais devem ser fornecidos por variáveis de ambiente.
- `.env` está no `.gitignore` e somente `.env.example` é versionado.
- Access token padrão: 15 minutos.
- Refresh token padrão: 7 dias.
- Rotação e blacklist de refresh tokens estão habilitadas.
- CORS permite explicitamente as origens configuradas em `CORS_ALLOWED_ORIGINS`.
- A API usa `IsAuthenticated` como permissão padrão; endpoints públicos de login/registro/refresh fazem override explícito.

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

Não coloque valores reais de produção no repositório. Copie `.env.example` para `.env` e configure os segredos localmente.

### Testes

```bash
cd backend
python manage.py test accounts
```
