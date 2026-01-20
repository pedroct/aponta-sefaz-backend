Especificação Técnica: Sistema de Apontamento de Horas (Azure DevOps Integration)
1. Visão Geral
Este documento descreve a implementação de uma ferramenta de Apontamento de Horas integrada à Azure DevOps Services REST API. O sistema consiste em uma grade hierárquica (Timesheet) e um modal de entrada de dados para registro de esforço.

2. Estrutura da Interface (Frontend)
A. Grade Hierárquica (Timesheet Grid)
Hierarquia de Itens: Exibição em árvore respeitando os níveis: Epic > Feature > User Story > Task/Bug.
Colunas de Metadados:
ID: Identificador único do item no Azure DevOps.
Title: Título com ícone correspondente ao WorkItemType.
E (Estimate): Mapeado para Microsoft.VSTS.Scheduling.OriginalEstimate.
Total: Somatória do campo Microsoft.VSTS.Scheduling.CompletedWork.
Colunas Temporais: Grade semanal (ex: seg 12 a dom 18) para exibição dos Apontamentos.
Totais: Linha de rodapé com a soma vertical das horas por dia e total da semana (Semanal).

B. Modal de Apontamento de Tempo
O modal deve capturar os seguintes campos para salvar na tabela de Apontamentos:
Usuário: Identificação do desenvolvedor (Nome e Avatar).
Tarefa: Campo de busca/seleção para vincular o ID da Task/Bug.
Data: Seletor de data para o registro do esforço.
Duração:
Entrada manual de tempo (formato HH:mm).
Botões de atalho: +0.5h, +1h, +2h, +4h.
Tipo de Atividade: Dropdown para categorização (ex: Documentação, Desenvolvimento).
Comentário: Campo de texto para descrição do trabalho realizado.

3. Arquitetura de Dados (Backend)
A. Modelo de Banco de Dados Local
Tabela WorkItems: Cache dos campos System.Id, System.Title, System.WorkItemType, OriginalEstimate, RemainingWork, CompletedWork.
Tabela WorkItemHierarchy: Mapeamento de ParentId e ChildId.
Tabela Apontamentos: Registros de tempo vinculados a um WorkItemId, contendo Data, Horas, TipoAtividade e Comentario.

B. Regras de Sincronização e Roll-up
1. Sincronização Azure (PATCH): Ao salvar um Apontamento, o backend deve atualizar a Task na Azure:
CompletedWork = (Valor Atual na Azure + Horas do Apontamento).
RemainingWork = (Valor Atual na Azure - Horas do Apontamento, mínimo 0).

2. Cálculo de $Somatório na Grade:
Para Tasks/Bugs: Soma dos Apontamentos locais filtrados pelo período.
Para Pai (Story/Feature/Epic): Soma recursiva das horas de todos os itens filhos.

4. Integração com APIs Azure DevOps (v7.2-preview.3)
Leitura da Estrutura (WIQL POST)
SELECT [System.Id] FROM WorkItemLinks 
WHERE ([Source].[System.TeamProject] = @project AND [Source].[System.WorkItemType] = 'Epic') 
AND ([System.Links.LinkType] = 'System.LinkTypes.Hierarchy-Forward') 
AND ([Target].[System.WorkItemType] IN ('Feature', 'User Story', 'Task', 'Bug')) 
MODE (Recursive)

Escrita de Dados (Update PATCH)
URL: PATCH https://dev.azure.com/{org}/_apis/wit/workitems/{id}?api-version=7.2-preview.3
Body: JSON Patch operations (op: add) para os campos CompletedWork e RemainingWork.
