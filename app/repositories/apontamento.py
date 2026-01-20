"""
Repository para operacoes de banco de dados da entidade Apontamento.
"""

import re
from uuid import UUID
from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, cast, Integer
from app.models.apontamento import Apontamento
from app.models.atividade import Atividade
from app.schemas.apontamento import ApontamentoCreate, ApontamentoUpdate


def parse_duracao(duracao: str) -> tuple[int, int]:
    """
    Converte duracao no formato HH:mm para tupla (horas, minutos).

    Args:
        duracao: String no formato HH:mm (ex: "01:30", "08:00").

    Returns:
        Tupla (horas, minutos).
    """
    match = re.match(r"^(\d{1,2}):(\d{2})$", duracao)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0


def duracao_to_decimal(duracao: str) -> float:
    """
    Converte duracao no formato HH:mm para horas decimais.

    Args:
        duracao: String no formato HH:mm (ex: "01:30" -> 1.5).

    Returns:
        Horas em formato decimal.
    """
    horas, minutos = parse_duracao(duracao)
    return horas + (minutos / 60)


def format_duracao(total_minutos: int) -> str:
    """
    Formata total de minutos para HH:mm.

    Args:
        total_minutos: Total em minutos.

    Returns:
        String no formato HH:mm.
    """
    horas = total_minutos // 60
    minutos = total_minutos % 60
    return f"{horas:02d}:{minutos:02d}"


class ApontamentoRepository:
    """Repository para operacoes CRUD de Apontamento."""

    def __init__(self, db: Session):
        self.db = db

    def _validate_atividade(self, id_atividade: UUID) -> bool:
        """
        Valida se a atividade existe e esta ativa.

        Args:
            id_atividade: UUID da atividade.

        Returns:
            True se a atividade existe e esta ativa.

        Raises:
            ValueError: Se a atividade nao existir ou estiver inativa.
        """
        atividade = (
            self.db.query(Atividade)
            .filter(Atividade.id == id_atividade)
            .first()
        )

        if not atividade:
            raise ValueError(f"Atividade nao encontrada: {id_atividade}")

        if not atividade.ativo:
            raise ValueError(f"Atividade inativa: {id_atividade}")

        return True

    def create(self, apontamento_data: ApontamentoCreate) -> Apontamento:
        """
        Cria um novo apontamento no banco de dados.

        Args:
            apontamento_data: Objeto Pydantic com os dados do novo apontamento.

        Returns:
            O objeto Apontamento recem-criado e persistido.

        Raises:
            ValueError: Se a atividade nao existir ou estiver inativa.
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
        Busca um apontamento especifico pelo seu ID unico.
        Realiza eager loading da atividade relacionada.

        Args:
            apontamento_id: UUID do apontamento.

        Returns:
            Objeto Apontamento ou None se nao encontrado.
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
        Lista apontamentos de um work item especifico com paginacao.

        Args:
            work_item_id: ID do work item no Azure DevOps.
            organization_name: Nome da organizacao no Azure DevOps.
            project_id: ID do projeto no Azure DevOps.
            skip: Numero de registros a pular (paginacao).
            limit: Maximo de registros a retornar.

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

        # Contar total antes de paginacao
        total = query.count()

        # Aplicar paginacao e ordenacao (mais recente primeiro)
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
    ) -> float:
        """
        Retorna o total de horas apontadas para um work item.

        Args:
            work_item_id: ID do work item no Azure DevOps.
            organization_name: Nome da organizacao no Azure DevOps.
            project_id: ID do projeto no Azure DevOps.

        Returns:
            Total de horas em formato decimal.
        """
        apontamentos = (
            self.db.query(Apontamento.duracao)
            .filter(
                Apontamento.work_item_id == work_item_id,
                Apontamento.organization_name == organization_name,
                Apontamento.project_id == project_id,
            )
            .all()
        )

        total_minutos = sum(
            parse_duracao(apt.duracao)[0] * 60 + parse_duracao(apt.duracao)[1]
            for apt in apontamentos
        )

        return total_minutos / 60  # Retorna em horas decimais

    def get_totals_formatted_by_work_item(
        self,
        work_item_id: int,
        organization_name: str,
        project_id: str,
    ) -> tuple[float, str]:
        """
        Retorna o total de horas apontadas e formatado para um work item.

        Args:
            work_item_id: ID do work item no Azure DevOps.
            organization_name: Nome da organizacao no Azure DevOps.
            project_id: ID do projeto no Azure DevOps.

        Returns:
            Tupla (total em horas decimais, total formatado HH:mm).
        """
        apontamentos = (
            self.db.query(Apontamento.duracao)
            .filter(
                Apontamento.work_item_id == work_item_id,
                Apontamento.organization_name == organization_name,
                Apontamento.project_id == project_id,
            )
            .all()
        )

        total_minutos = sum(
            parse_duracao(apt.duracao)[0] * 60 + parse_duracao(apt.duracao)[1]
            for apt in apontamentos
        )

        total_horas = total_minutos / 60
        total_formatado = format_duracao(total_minutos)

        return total_horas, total_formatado

    def get_summary_by_work_item(
        self,
        work_item_id: int,
        organization_name: str,
        project_id: str,
    ) -> dict:
        """
        Retorna resumo completo de apontamentos por work item.

        Returns:
            Dict com totais e agregações por atividade e usuário.
        """
        apontamentos = (
            self.db.query(Apontamento)
            .options(joinedload(Apontamento.atividade))
            .filter(
                Apontamento.work_item_id == work_item_id,
                Apontamento.organization_name == organization_name,
                Apontamento.project_id == project_id,
            )
            .all()
        )

        total_apontamentos = len(apontamentos)
        total_horas = sum(duracao_to_decimal(a.duracao) for a in apontamentos)

        if total_apontamentos > 0:
            primeira_data = min(a.data_apontamento for a in apontamentos)
            ultima_data = max(a.data_apontamento for a in apontamentos)
            media_horas = total_horas / total_apontamentos
        else:
            primeira_data = None
            ultima_data = None
            media_horas = 0.0

        por_atividade: dict[str, dict] = {}
        por_usuario: dict[str, dict] = {}

        for apontamento in apontamentos:
            horas = duracao_to_decimal(apontamento.duracao)

            atividade_id = str(apontamento.id_atividade)
            atividade_nome = (
                apontamento.atividade.nome if apontamento.atividade else ""
            )

            if atividade_id not in por_atividade:
                por_atividade[atividade_id] = {
                    "id": atividade_id,
                    "nome": atividade_nome,
                    "total_horas": 0.0,
                }
            por_atividade[atividade_id]["total_horas"] += horas

            usuario_id = apontamento.usuario_id
            usuario_nome = apontamento.usuario_nome
            if usuario_id not in por_usuario:
                por_usuario[usuario_id] = {
                    "id": usuario_id,
                    "nome": usuario_nome,
                    "total_horas": 0.0,
                }
            por_usuario[usuario_id]["total_horas"] += horas

        return {
            "work_item_id": work_item_id,
            "total_horas": total_horas,
            "total_apontamentos": total_apontamentos,
            "media_horas_por_apontamento": media_horas,
            "primeira_data": primeira_data,
            "ultima_data": ultima_data,
            "por_atividade": list(por_atividade.values()),
            "por_usuario": list(por_usuario.values()),
        }

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        usuario_id: str | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> tuple[list[Apontamento], int]:
        """
        Lista apontamentos com paginacao e filtros opcionais.

        Args:
            skip: Numero de registros a pular (paginacao).
            limit: Maximo de registros a retornar.
            usuario_id: Filtrar por usuario.
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

        # Contar total antes de paginacao
        total = query.count()

        # Aplicar paginacao e ordenacao
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
            apontamento_data: Dados para atualizacao.

        Returns:
            Apontamento atualizado ou None se nao encontrado.

        Raises:
            ValueError: Se a nova atividade nao existir ou estiver inativa.
        """
        db_apontamento = self.get_by_id(apontamento_id)
        if not db_apontamento:
            return None

        # Extrair dados de atualizacao
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
            True se removido, False se nao encontrado.
        """
        db_apontamento = self.get_by_id(apontamento_id)
        if not db_apontamento:
            return False

        self.db.delete(db_apontamento)
        self.db.commit()
        return True
