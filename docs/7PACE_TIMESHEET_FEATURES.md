# Análise de Funcionalidades e Regras de Negócios - 7pace Timetracker Timesheet

Este documento contém uma lista de funcionalidades e regras de negócios extraídas da documentação da página "7pace Timetracker's Timesheet page", servindo como referência para futuras melhorias e implementações no sistema Aponta.

## 1. Funcionalidades (Features)

### Visualização e Navegação
*   **Grid de Timesheet Semanal:** Visualização estilo planilha com *Work Items* nas linhas e dias da semana nas colunas.
*   **Navegação Temporal:** Botões para navegar para semana anterior, próxima e atalho para retornar à "Semana Atual".
*   **Totais Automáticos:**
    *   Total de horas por item de trabalho na semana (coluna de total).
    *   Total de horas por dia (rodapé da coluna).
    *   Exibição do "Effort" (esforço) estimado e total rastreado até o momento.
*   **Hierarquia:** Opção para mostrar/ocultar itens pais (*Show/Hide Parents*) para visualizar a árvore completa do item.
*   **Expansão:** Controles (+/-) para expandir ou colapsar níveis de itens na visualização.

### Entrada e Manipulação de Dados
*   **Adição de Tempo (Múltiplas Formas):**
    *   **Botão "Add Time":** Modal principal para adicionar tempo novo (configurável em modos *Timeframe*, *Duration* ou *Mixed*).
    *   **Edição In-Cell (Célula):** Digitação direta na célula para dias vazios ou com apenas 1 registro (comportamento estilo Excel).
    *   **List Editor (Modal de Lista):** Interface para gerenciar múltiplos registros no mesmo dia/item. Permite adicionar até 5 entradas simultâneas, definir *Activity Type* e Comentários.
*   **Edição e Exclusão:**
    *   Edição de valores de horas existentes.
    *   Exclusão via tecla `Delete` (diretamente na célula selecionada) ou ícone de "remover linha" dentro do modal.
*   **Atalhos de Teclado:** Otimização para navegação e edição rápida sem mouse (uso de `Tab`, `Enter`, `Setas`, `Ctrl+S`, `Ctrl+Del`).

### Filtros e Visualização
*   **Barra de Filtros:**
    *   **Current Project:** Filtra para exibir apenas itens do projeto atualmente selecionado.
    *   **This Week's Iterations:** Mostra todos os itens da iteração ativa (Sprint atual).
    *   **My Items Only:** Filtra apenas itens atribuídos ao usuário logado.
    *   **Show items from previous weeks:** Permite visualizar itens trabalhados em semanas anteriores (1, 2 ou 4 semanas atrás), mesmo que não tenham apontamentos na semana atual, facilitando o preenchimento recorrente.

### Fluxo de Aprovação
*   **Submissão:** Botão para enviar a timesheet da semana para aprovação de um gerente.
*   **Revogação:** Permite ao usuário cancelar o envio da timesheet (se ainda não tiver sido aprovada).
*   **Status da Semana:** Indicador visual do estado atual da semana (ex: "Week is submitted", "Week is open").

---

## 2. Regras de Negócios (Business Rules)

### Regras de Exibição e Filtros
*   **Dependência de Filtros:**
    *   O filtro *"View by This Week's Iterations"* só pode ser ativado se o filtro *"Current Project"* estiver ativo.
    *   O filtro *"My Items Only"* tipicamente só fica disponível se *"Current Project"* estiver ativo.
*   **Comportamento Padrão:**
    *   Se nenhum filtro estiver ativo, a tela deve mostrar apenas os itens que **já possuem** horas registradas na semana selecionada.
*   **Itens de Semanas Anteriores:**
    *   Quando a opção *"Show items from..."* está ativa, os itens trazidos de semanas anteriores devem ser exibidos com um destaque visual (ex: fundo azul claro nas linhas), indicando que foram trazidos pelo histórico e não possuem horas na semana atual.

### Regras de Edição de Célula
*   **Edição Direta vs. Modal:**
    *   **0 ou 1 registro:** Células vazias ou com registro único permitem edição direta de texto (duplo clique ou Enter).
    *   **Mais de 1 registro:** Células com múltiplos apontamentos no mesmo dia bloqueiam a edição direta e obrigam a abertura do *"Add Time dialog box"* para evitar ambiguidade.
    *   **Indicadores Visuais:** Ícones distintos devem indicar se a célula contém um único registro ou múltiplos.

### Regras de Sugestão Inteligente (Blue Highlighted Cells)
*   As células devem ser destacadas (ex: fundo azul negrito) para sugerir onde preencher horas se:
    1.  O item estava atribuído ao usuário logado naquele dia específico.
    2.  O item estava em um estado de "Em andamento" (*In Progress*) ou equivalente configurado.
    *   **Objetivo:** Facilitar o preenchimento lembrando o usuário em quais itens ele trabalhou naquele dia baseando-se no histórico de atribuição.

### Regras de Submissão e Aprovação
*   **Bloqueio Pós-Aprovação:**
    *   Se a timesheet da semana for aprovada pelo gerente, a semana inteira torna-se **Read-Only** (somente leitura). O usuário não pode mais editar, excluir ou adicionar horas naquela semana.
*   **Revogação:**
    *   O usuário só tem permissão para revogar a submissão enquanto o status não for "Approved" (Aprovado).

### Validações e Restrições
*   **Itens Fechados:**
    *   Se a configuração *"Prevent Time Entry Against Closed Items"* estiver ativa, o sistema deve impedir o lançamento de horas em itens que já estão concluídos/fechados e exibir uma mensagem informativa.
*   **Rastreamento Ativo:**
    *   Se um usuário tentar excluir um worklog que está sendo rastreado no momento (via client desktop ou web), o sistema deve interromper o rastreamento automaticamente antes de processar a exclusão.
