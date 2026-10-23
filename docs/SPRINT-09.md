# Sprint 09 — Dashboard & Notification Center

## Objetivo
Conectar as APIs do Sprint 08 à experiência React do MyMoney para tornar notificações e indicadores financeiros acessíveis no uso diário.

## Entregas
- Central de notificações dentro do dashboard.
- Contador de notificações não lidas e filtro para exibir somente as não lidas.
- Marcação individual como lida.
- Ação manual para gerar alertas de orçamento, recorrências e metas.
- Página dedicada de insights financeiros com seletor de mês.
- Indicadores de receita, despesas, resultado líquido e variação frente ao mês anterior.
- Listas de categorias de despesa, utilização de orçamentos, progresso de metas e lançamentos recorrentes próximos.
- Navegação dashboard/insights, responsividade, estados de carregamento, erro e conteúdo vazio.

## Rotas frontend
- `/dashboard`: dashboard com central de notificações.
- `/insights`: página de insights financeiros.

## APIs consumidas
- `GET /api/finance/notifications/`
- `GET /api/finance/notifications/?unread=true`
- `PATCH /api/finance/notifications/<uuid>/read/`
- `POST /api/finance/notifications/generate/`
- `GET /api/finance/insights/?month=YYYY-MM-DD`

## Critérios de aceite
- A interface só exibe dados do usuário autenticado, conforme o isolamento implementado no backend.
- É possível filtrar notificações não lidas e marcar uma notificação como lida.
- O usuário pode acionar a geração de alertas sem sair do dashboard.
- A página de insights permite selecionar um mês e mostra os indicadores retornados pela API.
- A interface informa carregamento, erros de API e listas vazias.

## Limites
- Os alertas só são gerados quando o usuário aciona a ação de geração; o agendamento automático não foi introduzido.
- Não foram adicionados gráficos de terceiros ou novas dependências: os componentes usam React e CSS existentes.
- A compilação e os testes do frontend precisam ser executados no ambiente do projeto antes da implantação.
