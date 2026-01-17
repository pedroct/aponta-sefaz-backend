"""
Repository para operações de banco de dados da entidade Apontamento.
"""

from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.apontamento import Apontamento
from app.models.atividade import Atividade
from app.schemas.apontamento import ApontamentoCreate, ApontamentoUpdate


class ApontamentoRepository:
    """Repository para operações CRUD de Apontamento."""

    def __init__(self, db: Session):
        self.db = db

    def _validate_atividade(self, id_atividade: UUID) -> bool:
        """
        Valida se a atividade existe e está ativa.

        Args:
            id_atividade: UUID da atividade.

        Returns:
            True se a atividade existe e está ativa.

        Raises:
            ValueError: Se a atividade não existir ou estiver inativa.
        """
        atividade = (
            self.db.query(Atividade)
            .filter(Atividade.id == id_atividade)
            .first()
        )

        if not atividade:
            raise ValueError(f"Atividade não encontrada: {id_atividade}")

        if not atividade.ativo:
            raise ValueError(f"Atividade inativa: {id_atividade}")

        return True

    def create(self, apontamento_data: ApontamentoCreate) -> Apontamento:
        """
        Cria um novo apontamento no banco de dados.

        Args:
            apontamento_data: Objeto Pydantic com os dados do novo apontamento.

        Returns:
            O objeto Apontamento recém-criado e persistido.

        Raises:
            ValueError: Se a atividade não existir ou estiver inativa.
        """
        # Validar atividade
        self._validate_atividade(apontamento_data.id_atividade)

        # Criar apontamento
        db_apontamento = Apontamento(**apontamento_data.model_dump())
        self.db.add(db_apontamento)
        self.db.commit()
        self.db.refresh(db_apontamento)

        # Recarregar com o relacionamento
        return self.get_by_id(db_apontamento.id)

    def get_by_id(self, apontamento_id: UUID) -> Apontamento | None:
        """
        Busca um apontamento específico pelo seu ID único.
        Realiza eager loading da atividade relacionada.

        Args:
            apontamento_id: UUID do apontamento.

        Returns:
            Objeto Apontamento ou None se não encontrado.
        """
        return (
            self.db.query(Apontamento)
            .options(joinedload(Apontamento.atividade))
            .filter(Apontamento.id == apontamento_id)
            .first()
        )

    def get_by_work_item(
        self,
        work_item_id: int,
        organization_name: str,
        project_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Apontamento], int]:
        """
        Lista apontamentos de um work item específico com paginação.

        Args:
            work_item_id: ID do work item no Azure DevOps.
            organization_name: Nome da organização no Azure DevOps.
            project_id: ID do projeto no Azure DevOps.
            skip: Número de registros a pular (paginação).
            limit: Máximo de registros a retornar.

        Returns:
            Tupla (lista de apontamentos, total de registros).
        """
        query = (
            self.db.query(Apontamento)
            .options(joinedload(Apontamento.atividade))
            .filter(
                Apontamento.work_item_id == work_item_id,
                Apontamento.organization_name == organization_name,
                Apontamento.project_id == project_id,
            )
        )

        # Contar total antes de paginação
        total = query.count()

        # Aplicar paginação e ordenação (mais recente primeiro)
        apontamentos = (
            query.order_by(Apontamento.data_apontamento.desc(), Apontamento.criado_em.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return apontamentos, total

    def get_totals_by_work_item(
        self,
        work_item_id: int,
        organization_name: str,
        project_id: str,
    ) -> tuple[int, int]:
        """
        Retorna o total de horas e minutos apontados para um work item.

        Args:
            work_item_id: ID do work item no Azure DevOps.
            organization_name: Nome da organização no Azure DevOps.
            project_id: ID do projeto no Azure DevOps.

        Returns:
            Tupla (total de horas, total de minutos).
        """
        result = (
            self.db.query(
                func.coalesce(func.sum(Apontamento.horas), 0).label("total_horas"),
                func.coalesce(func.sum(Apontamento.minutos), 0).label("total_minutos"),
            )
            .filter(
                Apontamento.work_item_id == work_item_id,
                Apontamento.organization_name == organization_name,
                Apontamento.project_id == project_id,
            )
            .first()
        )

        return int(result.total_horas), int(result.total_minutos)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        usuario_id: str | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> tuple[list[Apontamento], int]:
        """
        Lista apontamentos com paginação e filtros opcionais.

        Args:
            skip: Número de registros a pular (paginação).
            limit: Máximo de registros a retornar.
            usuario_id: Filtrar por usuário.
            data_inicio: Data inicial do filtro.
            data_fim: Data final do filtro.

        Returns:
            Tupla (lista de apontamentos, total de registros).
        """
        query = self.db.query(Apontamento).options(joinedload(Apontamento.atividade))

        # Aplicar filtros
        if usuario_id:
            query = query.filter(Apontamento.usuario_id == usuario_id)

        if data_inicio:
            query = query.filter(Apontamento.data_apontamento >= data_inicio)

        if data_fim:
            query = query.filter(Apontamento.data_apontamento <= data_fim)

        # Contar total antes de paginação
        total = query.count()

        # Aplicar paginação e ordenação
        apontamentos = (
            query.order_by(Apontamento.data_apontamento.desc(), Apontamento.criado_em.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return apontamentos, total

    def update(
        self, apontamento_id: UUID, apontamento_data: ApontamentoUpdate
    ) -> Apontamento | None:
        """
        Atualiza um apontamento existente.

        Args:
            apontamento_id: UUID do apontamento.
            apontamento_data: Dados para atualização.

        Returns:
            Apontamento atualizado ou None se não encontrado.

        Raises:
            ValueError: Se a nova atividade não existir ou estiver inativa.
        """
        db_apontamento = self.get_by_id(apontamento_id)
        if not db_apontamento:
            return None

        # Extrair dados de atualização
        update_data = apontamento_data.model_dump(exclude_unset=True)

        # Validar nova atividade se fornecida
        if "id_atividade" in update_data:
            self._validate_atividade(update_data["id_atividade"])

        # Atualizar campos
        for field, value in update_data.items():
            setattr(db_apontamento, field, value)

        self.db.commit()
        self.db.refresh(db_apontamento)

        return self.get_by_id(apontamento_id)

    def delete(self, apontamento_id: UUID) -> bool:
        """
        Remove um apontamento.

        Args:
            apontamento_id: UUID do apontamento.

        Returns:
            True se removido, False se não encontrado.
        """
        db_apontamento = self.get_by_id(apontamento_id)
        if not db_apontamento:
            return False

        self.db.delete(db_apontamento)
        self.db.commit()
        return True
