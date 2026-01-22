---
type: spec
name: toolbar-button
description: Especificação do botão "Aponta Tempo" na toolbar do Work Item
category: features
created: 2026-01-22
status: pending-implementation
target: frontend
---

# Especificação Técnica: Botão "Aponta Tempo" (Toolbar Menu)

## 1. Objetivo
Adicionar um botão de ação rápida chamado **"Aponta Tempo"** na barra de ferramentas (Toolbar) do formulário de Work Item do Azure DevOps. O botão deve abrir a modal React existente (`ModalAdicionarTempo.tsx`) e injetar automaticamente o contexto do item de trabalho atual.

## 2. Ponto de Contribuição (Manifesto)
Para seguir as melhores práticas de extensibilidade do Azure DevOps, o botão deve ser registrado como um `work-item-toolbar-menu`.

**Alteração no `vss-extension.staging.json`:**
```json
{
  "contributions": [
    {
      "id": "aponta-tempo-toolbar-button",
      "type": "ms.vss-work-web.work-item-toolbar-menu",
      "targets": [
        "ms.vss-work-web.work-item-form-menu"
      ],
      "properties": {
        "name": "Aponta Tempo",
        "title": "Registrar horas nesta atividade",
        "icon": "images/icon-16.png",
        "uri": "dist/aponta-tempo-toolbar.html"
      }
    }
  ]
}
```

## 3. Regras de Negócio e Estados (Referência: Kanban v1.0.0)

O botão deve validar o estado atual do Work Item antes de permitir a abertura da modal ou habilitar a edição.

### Estados de Bloqueio (Categoria Completed/Removed)
- "Entregue" (HU)
- "Corrigido" (Bug)
- "Cancelado"

### Comportamento
- Se o item estiver em um estado de bloqueio, o botão deve passar `podeEditar={false}` para a modal
- A modal deve exibir o AlertTriangle de bloqueio (conforme implementado em ModalAdicionarTempo.tsx)

## 4. Integração com Componente React

O arquivo de entrada (`aponta-tempo-toolbar.tsx`) deve atuar como um "Host" para a modal.

### Fluxo de Dados

**Inicialização**: O SDK do Azure DevOps (azure-devops-extension-sdk) obtém o ID e Título do item

**Contexto**: O `taskId` e `taskTitle` são capturados via `WorkItemFormService`

**Injeção de Props**: Os dados capturados são passados para o componente `<ModalAdicionarTempo />`

### Mapeamento de Props para ModalAdicionarTempo.tsx

| Prop | Origem (SDK Azure DevOps) |
|------|---------------------------|
| `taskId` | `workItemFormService.getId()` |
| `taskTitle` | `workItemFormService.getFieldValue("System.Title")` |
| `projectId` | `workItemFormService.getFieldValue("System.TeamProject")` |
| `organizationName` | `SDK.getOrganizationName()` |
| `mode` | Fixo: `"create"` |
| `podeEditar` | `false` se State for "Entregue", "Corrigido" ou "Cancelado"; caso contrário `true` |

## 5. Implementação Técnica

### 5.1. Arquivo de Entrada (`aponta-tempo-toolbar.tsx`)

O arquivo referenciado no manifesto como `uri` deve inicializar o SDK e registrar o handler para o evento de clique. Como se trata de uma ação de Toolbar, o Azure DevOps espera que a extensão responda ao método `execute`.

**Lógica de Registro (SDK v2):**
```typescript
import * as SDK from "azure-devops-extension-sdk";
import { 
    WorkItemTrackingServiceIds, 
    IWorkItemFormService 
} from "azure-devops-extension-api/WorkItemTracking";

/**
 * Script de inicialização da contribuição 'aponta-tempo-toolbar-button'
 */
SDK.init().then(() => {
    SDK.register("aponta-tempo-toolbar-button", () => {
        return {
            // Este método é disparado quando o usuário clica no botão "Aponta Tempo"
            execute: async (context: any) => {
                await openTimeTrackingModal();
            }
        };
    });
});

async function openTimeTrackingModal() {
    // 1. Obter o serviço de formulário do Work Item
    const formService = await SDK.getService<IWorkItemFormService>(
        WorkItemTrackingServiceIds.WorkItemFormService
    );

    // 2. Capturar dados do item atual
    const [id, title, project, state] = await Promise.all([
        formService.getId(),
        formService.getFieldValue("System.Title"),
        formService.getFieldValue("System.TeamProject"),
        formService.getFieldValue("System.State")
    ]);

    // 3. Validar Categoria de Estado (Regra Kanban v1.0.0)
    // Bloqueia se o estado for 'Entregue' (HU), 'Corrigido' (Bug) ou 'Cancelado'
    const estadosBloqueados = ["Entregue", "Corrigido", "Cancelado"];
    const isBlocked = estadosBloqueados.includes(state as string);

    // 4. Disparar a Modal
    // Renderizar o componente ModalAdicionarTempo dentro de um root React
    renderReactModal({
        isOpen: true,
        taskId: id.toString(),
        taskTitle: title as string,
        projectId: project as string,
        organizationName: SDK.getOrganizationName(),
        podeEditar: !isBlocked
    });
}
```

### 5.2. Integração de Props

Ao disparar a modal, o script deve garantir que as propriedades mapeadas no componente `ModalAdicionarTempo.tsx` sejam preenchidas corretamente:

- **`taskId`**: Deve receber o ID numérico convertido para String. Isso ativará o modo readOnly no campo de busca da modal
- **`podeEditar`**: Deve ser `false` se o item estiver nos estados de fechamento do Kanban. Isso ativará o AlertTriangle de bloqueio
- **`onClose`**: Deve ser uma função que limpe o container React ou feche o diálogo do Azure DevOps

## 6. Arquivos a Criar/Modificar

### Frontend (C:\Projetos\Azure\fe-aponta)

1. **`vss-extension.staging.json`** - Adicionar contribuição `aponta-tempo-toolbar-button`
2. **`vss-extension.json`** - Adicionar mesma contribuição para produção
3. **`client/src/toolbar/aponta-tempo-toolbar.tsx`** - Entry point com SDK initialization
4. **`aponta-tempo-toolbar.html`** - HTML wrapper que carrega o bundle
5. **`vite.config.ts`** - Adicionar entry point para build
6. **`client/src/components/custom/ModalAdicionarTempo.tsx`** (verificar props existentes)

## 7. Instruções para Implementação

### Bootstrap da Toolbar
Criar um novo entry-point que utilize o `SDK.register` para responder ao clique no menu da toolbar

### Reaproveitamento de Código
Importar o componente `ModalAdicionarTempo` do caminho `@/components/ModalAdicionarTempo`

### Estilização
O botão na Toolbar é renderizado nativamente pelo Azure DevOps, mas a Modal disparada deve manter o layout e estilos CSS/Tailwind definidos no arquivo `.tsx` fornecido

### Sincronização
Após o salvamento bem-sucedido na modal (chamada do `handleSave`), garantir que a modal seja fechada e a mensagem de sucesso do toast seja exibida

### Validação de Negócio
Certificar-se de que a verificação de estados (`isBlocked`) utilize a lista exata do documento "Kanban v1.0.0" fornecido (especialmente os estados "Entregue" e "Corrigido")

### Limpeza
Garantir que, após o fechamento da modal (`onClose`), o estado da extensão seja resetado para permitir novas aberturas sem recarregar a página

## 8. Considerações de UX

### Campo de Busca Pré-preenchido
Como o botão está na Toolbar, o usuário espera que o campo de busca de tarefas na modal (`searchTerm`) já venha preenchido e desabilitado (ReadOnly), focando apenas na inserção das horas e comentário

### Modal Centralizada
A modal deve ser centralizada na tela (Overlay), cobrindo o formulário do Work Item

### Estados Bloqueados
Quando `podeEditar={false}`, a modal deve:
- Exibir AlertTriangle com mensagem clara
- Desabilitar campos de input (horas, comentário)
- Mostrar botão de "Cancelar" apenas (sem "Salvar")

## 9. Build e Deploy

### Vite Configuration
Adicionar entry point no `vite.config.ts`:
```typescript
build: {
  rollupOptions: {
    input: {
      // ... existing entries
      'aponta-tempo-toolbar': 'aponta-tempo-toolbar.html'
    }
  }
}
```

### Testing Local
1. Run `npm run dev` no frontend
2. Publicar extensão no modo desenvolvimento
3. Abrir Work Item e verificar botão na toolbar
4. Testar com Work Items em diferentes estados

### Deploy Staging
1. Build: `npm run build`
2. Commit changes to `develop` branch
3. GitHub Actions auto-deploy to staging
4. Test in https://staging-aponta.treit.com.br

### Deploy Production
1. Merge `develop` → `main`
2. GitHub Actions auto-deploy to production
3. Test in https://aponta.treit.com.br

## 10. Related Documentation

- [Locked Items Feature](./locked-items.md) - Usa mesma lógica de validação de estados
- [Blue Cells Feature](./blue-cells.md) - Referência de integração com Azure DevOps API
- [ModalAdicionarTempo.tsx Spec](../../docs/frontend/ESPECIFICACAO_FRONTEND_APONTAMENTO.md)

## 11. Status

- **Status**: ✅ Implemented & Deployed to Staging
- **Priority**: High
- **Target**: Frontend Repository
- **Dependencies**: Locked Items feature (state validation logic)
- **Estimated Effort**: 4-6 hours
- **Actual Effort**: ~1 hour
- **Commit**: `511a1ab` - feat(toolbar): adiciona botão 'Aponta Tempo' na toolbar do Work Item
- **Deployment**: Auto-deploying to staging via GitHub Actions

### Implementation Summary

**Files Created:**
- `client/aponta-tempo-toolbar.html` - HTML wrapper for toolbar button
- `client/aponta-tempo-toolbar.tsx` - React entry-point with SDK integration (145 lines)

**Files Modified:**
- `extension/vss-extension.staging.json` - Added toolbar contribution
- `extension/vss-extension.json` - Added toolbar contribution (production)
- `vite.config.ts` - Added build entry-point

**Key Features Implemented:**
- ✅ SDK initialization and registration
- ✅ Work Item context capture (ID, title, project, state)
- ✅ State validation (Entregue, Corrigido, Cancelado)
- ✅ Modal integration with pre-filled props
- ✅ Error handling with user-friendly messages
- ✅ React root management for modal rendering

**Testing:**
- ✅ TypeScript compilation: No errors
- ✅ Build successful: `dist/aponta-tempo-toolbar.html` generated
- ⏳ Manual testing in Azure DevOps staging environment (pending)
- ⏳ Production deployment (pending user approval)
