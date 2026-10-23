# Sprint 07 — Intelligent Categorization & Reconciliation

## Objetivo
Reduzir a classificação manual de transações importadas e tornar a conferência bancária mais segura, sem categorização opaca ou alteração automática de lançamentos já existentes.

## Escopo
- Regras por correspondência literal em descrição, ordenadas por prioridade crescente.
- Uma regra só pode apontar para categoria pertencente ao mesmo usuário.
- A categoria precisa ter o mesmo tipo da transação (receita/despesa).
- Endpoint de reconciliação retorna correspondências exatas e possíveis candidatas (mesmo valor/tipo, até três dias de diferença).
- Confirmação inteligente aplica a primeira regra compatível; na ausência de regra, usa a primeira categoria ativa compatível.
- Processamento transacional, proteção contra duplicidades e isolamento por usuário.

## API
| Método | Endpoint | Descrição |
|---|---|---|
| GET/POST | `/api/finance/categorization/rules/` | Listar e criar regras |
| GET/PATCH/DELETE | `/api/finance/categorization/rules/<uuid>/` | Gerenciar regra |
| GET | `/api/finance/imports/<uuid>/reconcile/` | Prévia de reconciliação |
| POST | `/api/finance/imports/<uuid>/confirm-smart/` | Confirmar lote usando regras |

## Formato da regra
```json
{
  "name": "Supermercado",
  "pattern": "mercado",
  "match_field": "DESCRIPTION",
  "category": "<uuid-da-categoria>",
  "priority": 10,
  "is_active": true
}
```
`match_field` aceita `DESCRIPTION`. Menor `priority` é avaliada primeiro. O Sprint 07 usa texto literal, não regex.

## Critérios de aceite
- Regras privadas por usuário.
- Rejeitar categorias de outro usuário.
- Não aplicar regra de despesa a receita, ou vice-versa.
- Apresentar candidatas sem confirmar automaticamente correspondências aproximadas.
- Repetir a confirmação não duplica transações porque o lote deixa de estar em pré-visualização.
- Testes automatizados para validação, prioridade, reconciliação e isolamento.

## Limites
- A reconciliação aproximada apenas sugere candidatas; não faz pareamento automático.
- A importação continua limitada a CSV UTF-8, conforme Sprint 06.
