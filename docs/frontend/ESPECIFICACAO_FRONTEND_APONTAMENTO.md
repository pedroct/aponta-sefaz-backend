# Especificação do Produto: Extensão de Apontamento de Horas para Azure DevOps

## 1. Visão Geral
Este produto é uma extensão projetada para o Azure DevOps que facilita o registro e gerenciamento de horas trabalhadas (apontamentos) seguindo o padrão visual do 7pace Timetracker e as diretrizes de design do Azure DevOps (Design System).

## 2. Estrutura de Navegação (Páginas)
O sistema é composto pelas seguintes interfaces principais:

### 2.1 Gestão de Apontamentos (client/src/pages/FolhaDeHoras.tsx)
Página principal do sistema, apresentando uma visão semanal dos apontamentos organizados por hierarquia de trabalho.
- **Título da Página**: Gestão de Apontamentos.
- **Cabeçalho**: Interface limpa (White Label) com foco na ação principal.

### 2.2 Modal de Apontamento (client/src/components/custom/ModalAdicionarTempo.tsx)
Interface popup para entrada de dados detalhada de tempo.

## 3. Funcionalidades Implementadas

### 3.1 Timesheet (Folha de Horas)
- **Hierarquia de Escopo**: Visualização multinível baseada em Work Items do Azure DevOps:
  - 👑 **Épico** (Epic)
  - 🏆 **Feature**
  - 📘 **História** (User Story / PBI)
  - 📋 **Tarefa** (Task)
- **Grid Semanal**: Exibição dos dias da semana (Segunda a Domingo) com destaque para o dia atual.
- **Colunas Técnicas**:
  - **E (Esforço)**: Exibe a estimativa planejada para o item.
  - **H (Histórico)**: Exibe o tempo total acumulado no item até o momento.
- **Navegação Temporal**: 
  - Seleção de semanas (Anterior/Próxima).
  - Botão "Hoje" para retorno rápido à data atual.

### 3.2 Lançamento de Tempo
- **Células Editáveis**: Clique direto na célula de tempo para abrir o formulário de lançamento.
- **Destaque Visual (Blue Cells)**: Itens com status "In Progress" atribuídos ao usuário logado são destacados em azul claro no dia atual para incentivar o apontamento.
- **Destaque de Lançamento**: Células com horas já lançadas são exibidas em amarelo suave com texto em negrito.

### 3.3 Filtros e Controles
- **Barra de Ferramentas**:
  - **Novo Apontamento**: Acesso rápido para criar novos registros.
  - **Filtro "Projeto Atual"**: Filtra itens apenas do contexto atual.
  - **Filtro "Somente meus itens"**: Exibe apenas tarefas atribuídas diretamente ao usuário.

### 3.4 Regras de Validação e UX
- **Limite Diário**: Validação para evitar lançamentos superiores a 08:00 horas por dia.
- **Presetes de Duração**: Atalhos rápidos para 00:15, 00:30, 01:00, 02:00 e 04:00 horas.
- **Localização**: Interface totalmente traduzida para Português (Brasil), incluindo formatação de datas e nomes de dias.

## 4. Identidade Visual
- **Paleta de Cores**:
  - Azul Azure (#0078D4) para ações principais.
  - Cinza Neutro (#F3F2F1, #EDEBE9) para bordas e fundos.
  - Amarelo Suave (#FFF4CE) para horas registradas.
- **Tipografia**: Segue o padrão Segoe UI/Inter para legibilidade técnica.
