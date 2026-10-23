# Sprint 11 — Qualidade, testes e integração contínua

## Objetivo
Criar uma verificação automatizada para as alterações do MyMoney e ampliar os testes de regressão dos endpoints usados pelo planejamento financeiro do Sprint 10.

## Entregas
- Workflow GitHub Actions em `.github/workflows/ci.yml`, executado em pull requests para `main`, pushes para `main` e manualmente.
- Job backend com PostgreSQL 16, Python 3.12, instalação das dependências, `manage.py check`, verificação de migrações e testes de autenticação/finanças.
- Job frontend com Node.js 22, instalação das dependências e `npm run build` para validar TypeScript e o bundle de produção.
- Testes de regressão para cálculo de orçamento, validação do tipo da categoria, progresso de metas, isolamento entre usuários, proteção das rotas e rejeição de conta pertencente a outro usuário.
- Documentação da pipeline e dos comandos para execução local.

## Arquivos
- `.github/workflows/ci.yml`
- `backend/finance/test_sprint11.py`
- `docs/SPRINT-11.md`
- `README.md`

## Como executar localmente

Backend (PostgreSQL disponível e configurado pelas variáveis `POSTGRES_*`):

```bash
cd backend
pip install -r requirements.txt
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test accounts finance --verbosity 2
```

Frontend:

```bash
cd frontend
npm install
npm run build
```

## Critérios de aceite
- A pipeline executa ambos os jobs em pull requests para `main`.
- Falhas de checagem, testes, migrações ou compilação deixam a execução marcada como falha.
- Os testes garantem que os endpoints de planejamento não exponham dados de outro usuário.
- Nenhum segredo de produção é armazenado no workflow ou no repositório.

## Limitações conhecidas
- Os testes e a compilação são executados pela pipeline do GitHub Actions; o merge não deve ser interpretado como prova de que os checks passaram até que os resultados reais sejam verificados.
- A pipeline não substitui revisão de segurança, análise de dependências ou testes de ponta a ponta no navegador.
