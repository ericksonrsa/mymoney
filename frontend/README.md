# MyMoney Frontend

Frontend React + Vite da autenticação do MyMoney.

## Executar

```bash
npm install
npm run dev
```

Configure `VITE_API_URL` conforme o endereço da API Django. Por padrão: `http://localhost:8000/api`.

## Autenticação

- Login: `POST /auth/login/`
- Cadastro: `POST /auth/register/`
- Refresh: `POST /auth/token/refresh/`
- Usuário atual: `GET /auth/me/`
- Access token mantido em memória.
- Refresh token mantido em `sessionStorage` para sobreviver a recarregamentos da aba sem persistir após o fechamento da sessão do navegador.
- Interceptor Axios renova o access token automaticamente quando a API retorna `401`.

> Em produção, HTTPS deve ser obrigatório. Para uma evolução posterior, o refresh token pode ser movido para cookie `HttpOnly`, `Secure` e `SameSite` com proteção CSRF correspondente.
