# Decisões de Design - Timesheet

## Filtragem de Work Items

### Decisão: Remover "Somente meus itens" do Frontend

**Status**: IMPLEMENTADO NO BACKEND ✅

### Problema

O frontend estava oferecendo um checkbox "Somente meus itens" que era redundante e causava confusão para o usuário, pois:

1. O filtro já era aplicado automaticamente pelo backend
2. O checkbox não oferecia uma opção real de "ver itens de outros usuários"
3. Criava complexidade desnecessária na UI

### Solução

**Backend (API):**
- ✅ Já implementado: O endpoint `/api/v1/timesheet` SEMPRE filtra por `user_email`
- ✅ Garantido: Apenas Work Items atribuídos ao usuário logado são retornados
- ✅ Seguro: Não há parâmetro para contornar essa filtragem

**Frontend (Extensão Azure DevOps):**
- ⏳ TODO: Remover o checkbox "Somente meus itens" da interface
- ⏳ TODO: Simplificar a lógica de requisição removendo `only_my_items` param
- ⏳ TODO: Atualizar documentação

### Código Backend Relevante

**Router** (`app/routers/timesheet.py`):
```python
async def get_timesheet(
    organization_name: str = Query(...),
    project_id: str = Query(...),
    week_start: date | None = Query(default=None),
    current_user: AzureDevOpsUser = Depends(get_current_user),  # Usuário autenticado
    service: TimesheetService = Depends(get_service),
) -> TimesheetResponse:
    """Endpoint para obter o timesheet semanal."""
    return await service.get_timesheet(
        organization=organization_name,
        project=project_id,
        week_start=week_start,
        user_email=current_user.email,  # ✅ SEMPRE filtra pelo usuário
        user_id=current_user.id,
    )
```

**Serviço** (`app/services/timesheet_service.py`):
```python
async def _get_work_items_hierarchy(
    self,
    organization: str,
    project: str,
    user_email: str | None = None,  # Sempre preenchido
) -> list[dict[str, Any]]:
    # WIQL com filtro de usuário
    assigned_filter = ""
    if user_email:
        assigned_filter = f"AND [System.AssignedTo] = '{user_email}' "
    
    wiql = f"""
    SELECT [System.Id]
    FROM WorkItemLinks
    WHERE ...
    {assigned_filter}  # ✅ Filtro obrigatório
    ...
    """
```

### Garantias

1. **Segurança**: O usuário não pode ver Work Items de outros usuários
2. **Performance**: Menos dados trafegando (já filtrado no servidor)
3. **Simplicidade**: UI mais limpa, menos opções confusas
4. **Consistência**: Comportamento previsível em todas as situações

### Impacto

- ✅ Simplifica a interface
- ✅ Melhora a compreensão do usuário
- ✅ Mantém segurança e privacidade
- ⚠️ Requer mudança no frontend (repositório separado)

### Próximos Passos

1. Remover checkbox "Somente meus itens" do componente Timesheet
2. Remover parâmetro `only_my_items` das requisições API
3. Atualizar testes e documentação
4. Comunicar a mudança aos usuários
