# Perguntas de Refinamento - Gestão de Apontamentos (Frontend)

**Projeto**: Extensão de Apontamento de Horas para Azure DevOps  
**Data**: 19/01/2026  
**Contexto**: Refinamento para implementação da página "Gestão de Apontamentos"
**traduções**: a palavra timesheet é substituida por Folha de Horas.

---

## ✅ Funcionalidades Confirmadas (Fora do Escopo)

| Funcionalidade | Status |
|----------------|--------|
| Modal de Apontamento | ✅ Implementado |
| Integração POST /api/v1/apontamentos | ✅ Implementado |
| Botão "+ Novo Apontamento" | ✅ Implementado |

---

## 🔍 Perguntas para Refinamento

### 1. Comportamento das Células da Grade

**1.1** Ao clicar na **célula azul** (dia atual sem horas lançadas), qual o comportamento esperado?
- [X] Abre o modal pré-populado com Work Item e data selecionados?
- [ ] Outro comportamento? Descreva.

**1.2** Ao clicar na **célula amarela** (com horas já lançadas), qual o comportamento esperado?
- [X] **Opção A**: Abre modal para **editar** o apontamento existente
- [ ] **Opção B**: Abre modal para **adicionar** mais horas (novo apontamento)
- [X] **Opção C**: Exibe popover/tooltip com detalhes + opções (editar/excluir)
- [ ] **Opção D**: Outro comportamento? Descreva.

**1.3** Se houver **múltiplos apontamentos** no mesmo dia para o mesmo Work Item (ex: 1h de manhã + 0.5h à tarde), como exibir na célula?
- [ ] **Opção A**: Soma total (1.5h)
- [ ] **Opção B**: Soma + indicador visual de múltiplos registros
- [X] **Opção C**: Outro? Descreva. Como o apontamento é por Tipo de Atividade, possa ser que tenha mais uma atividade no mesmo dia, portanro, é preciso contruir algo que seja mais amigável e visível para o usuário.

---

### 2. Edição e Exclusão de Apontamentos

**2.1** Existe fluxo implementado para **editar** um apontamento já lançado?
- [X] Sim, já implementado
- [ ] Não, precisa implementar
- Se sim, descreva o fluxo atual. A tarefa ou bug precisa está em um Estado (state) da Categorias Resolved. A Tarefa ou Bug que estiver em um Estado (State) nas Categorias Completed ou Removed não poderá ser editada. No futuro, iremos criar uma regra para que um apontamento aprovaado pelo gestor não possa ser editado. Em anexo, está uma imagem com as Categorias par que possa melhor entender. Abaixo, está o endereço da documentação oficial, caso precise detalhar o entendimento.
https://learn.microsoft.com/en-us/azure/devops/boards/work-items/workflow-and-state-categories?view=azure-devops&tabs=agile-process

**2.2** Existe fluxo implementado para **excluir** um apontamento?
- [X] Sim, já implementado
- [ ] Não, precisa implementar
- Se sim, descreva o fluxo atual. A tarefa ou bug precisa está em um Estado (state) da Categorias Resolved.

**2.3** Ao excluir, deve haver **modal de confirmação**?
- [X] Sim. Além de um Tosat de confirmação da exclusão.
- [ ] Não

---

### 3. Expansão/Colapso da Árvore Hierárquica

**3.1** Existem **controles visuais** (ícones ▶/▼) para expandir/colapsar os níveis da hierarquia (Epic, Feature, Story)?
- [X] Sim, já implementado
- [ ] Não, precisa implementar

**3.2** Qual o **estado inicial** da árvore ao carregar a página?
- [X] **Opção A**: Todos os níveis expandidos
- [ ] **Opção B**: Apenas primeiro nível (Epics) expandido
- [ ] **Opção C**: Apenas dois níveis (Epics + Features) expandidos
- [ ] **Opção D**: Lembrar estado anterior do usuário

**3.3** O estado de expansão é **persistido** ao navegar entre semanas?
- [X] Sim
- [ ] Não

---

### 4. Agregação de Dados nos Níveis Pai

**4.1** Os níveis pai (Epic, Feature, Story) devem exibir a **soma das horas dos filhos** nas colunas de dias da semana?
- [ ] Sim
- [X] Não, apenas Tasks exibem horas

**4.2** As colunas **E (Esforço)** e **H (Histórico)** nos níveis pai devem exibir:
- [X] **Opção A**: Soma dos valores dos filhos
- [ ] **Opção B**: Ficar vazias
- [ ] **Opção C**: Valor próprio do Work Item (se houver)

---

### 5. Validações e Feedback Visual

**5.1** A validação de **limite de 8h diárias** está implementada?
- [X] Sim, no frontend
- [ ] Sim, no backend
- [ ] Sim, em ambos
- [ ] Não implementada

**5.2** Após salvar um apontamento, qual o comportamento de **refresh**?
- [X] **Opção A**: Atualiza apenas a célula afetada e os valores de totais.
- [ ] **Opção B**: Atualiza toda a linha do Work Item
- [ ] **Opção C**: Refresh completo da grade
- [ ] **Opção D**: Outro? Descreva.

**5.3** Existem **loading states** (skeleton/spinner) durante o carregamento da grade?
- [ ] Sim, já implementado
- [X] Não, precisa implementar

---

### 6. Filtros

**6.1** O filtro **"Projeto Atual"** está funcional? Qual o comportamento?
- [X] Filtra Work Items pelo projeto do contexto Azure DevOps. Não está implementado.
- [ ] Outro comportamento? Descreva.

**6.2** O filtro **"Somente meus itens"** está funcional? Qual o comportamento?
- [X] Filtra por `System.AssignedTo` do usuário logado. Não está implementado.
- [ ] Outro comportamento? Descreva.

**6.3** O estado dos filtros (checkboxes) é **persistido** entre sessões/reloads?
- [X] Sim
- [ ] Não

---

### 7. Dados e Endpoints

**7.1** Qual **endpoint** fornece os dados hierárquicos da grade com os apontamentos por dia?
- [ ] Endpoint único (ex: `GET /api/v1/timesheet?week=2026-01-19`)
- [ ] Combinação de múltiplas chamadas no frontend
- Descreva o fluxo atual: não há um fluxo atual, apenas a documentação do Azure DevOps API sobre os tipos de Work Item. Aqui deixo para que você decida a melhor aborgem.

**7.2** A coluna **H (Histórico)** representa:
- [ ] **Opção A**: Total de horas de **todos os tempos** no Work Item
- [X] **Opção B**: Total de horas apenas da **semana atual**

**7.3** O **SEMANAL Σ** representa:
- [ ] **Opção A**: Soma das horas da semana atual
- [X] **Opção B**: Mesmo valor do Histórico (H)

**7.4**  Hierarquia de Work Items
- Estrutura em árvore (Épico → Feature → User Story → Task/Bug).
- Totais agregados por nível.
- Expansão/colapso dos nós.

**8.5** Atualização de horas tranbalhadas no Work Item (Task ou Bug)
- Atualiza automaticamente `CompletedWork` e `RemainingWork`.
- Sincroniza status após cada apontamento.
- Mantém dados locais mesmo se a API estiver indisponível.

---

## 7. Fluxos principais

### 7.1 Lançar horas
1. Usuário abre a aplicação.
2. Clica em “Novo apontamento”.
3. Seleciona tarefa, data, duração e tipo de atividade.
4. Salva.
5. Sistema grava localmente e sincroniza com Azure DevOps.
- Validação de dados (horas válidas, data não futura, tarefa obrigatória).

### 7.2 Revisar semana
1. Usuário visualiza a grade semanal.
2. Analisa totais diários e semanais.
3. Expande itens para ver detalhes.

## 8. Regras de negócio
- Não permitir horas negativas.
- Permiter apontamento de no mínomo 00:15 até 08:00 de duração por dia
- Total diário não pode exceder 08:00.
- `RemainingWork` não pode ficar negativo.
- Somente tarefas (Task/Bug) são atualizadas diretamente no Azure DevOps.

## 9. Requisitos não funcionais
- **Desempenho:** carregamento rápido e cache inteligente.
- **Confiabilidade:** salvar localmente se a sincronização falhar.
- **Segurança:** autenticação via Azure DevOps (PAT ou similar).
- **Usabilidade:** interface responsiva, com foco em rapidez no lançamento.

## 10. Como funciona (visão geral)
1. O front-end busca Work Items e apontamentos via API.
2. O usuário registra horas no modal.
3. O back-end grava o apontamento e atualiza o Azure DevOps.
4. A grade semanal reflete o novo total imediatamente.

## 11. Métricas de sucesso
- Tempo médio para registrar um apontamento < 30s.
- Taxa de sincronização bem-sucedida > 99%.
- Aumento da visibilidade de esforço por sprint/projeto.

### 12. Tecnologias (Confirmação)

**12.1** Stack tecnológica atual:
- Framework: _______________
- Versão: _______________
- Biblioteca de componentes UI: _______________
- Gerenciamento de estado: _______________

**12.2** Estrutura de arquivos - confirme os paths:
- Página principal: `client/src/pages/FolhaDeHoras.tsx` Sim
- Modal: `client/src/components/custom/ModalAdicionarTempo.tsx` Sim
- Outros componentes relevantes: _______________

---

## 📋 Resumo - Itens a Verificar

| # | Funcionalidade | Implementado? | Prioridade |
|---|----------------|---------------|------------|
| 1 | Clique em célula → modal pré-populado | ❓ | Alta |
| 2 | Edição de apontamento existente | ❓ | Alta |
| 3 | Exclusão de apontamento | ❓ | Alta |
| 4 | Agregação de horas nos níveis pai | ❓ | Média |
| 5 | Controles expandir/colapsar árvore | ❓ | Média |
| 6 | Validação limite 8h diárias | ❓ | Média |
| 7 | Loading states (skeleton/spinner) | ❓ | Média |
| 8 | Persistência de filtros | ❓ | Baixa |
| 9 | Persistência de estado de expansão | ❓ | Baixa |

---

## 📎 Referências

- **Backend API de PRODUÇÃO Base URL**: `https://api-aponta.pedroct.com.br/api/v1`
- **Backend API DESENVOLVIMENTO LOCAL Base URL**: `http://localhost:8000/api/v1`
- **Endpoints relevantes**:
  - `POST /apontamentos` - Criar apontamento
  - `PUT /apontamentos/{id}` - Atualizar apontamento
  - `DELETE /apontamentos/{id}` - Excluir apontamento
  - `GET /apontamentos/work-item/{id}` - Listar apontamentos de um Work Item
  - `GET /work-items/search` - Buscar Work Items
  - `GET /atividades` - Listar tipos de atividade

- **Documento de especificação**: `docs/frontend/ESPECIFICACAO_FRONTEND_APONTAMENTO.md`

---

Por favor, responda cada pergunta para que possamos definir o plano de implementação! 🎯