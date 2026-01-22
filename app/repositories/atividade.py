"""
Repository para operações de banco de dados da entidade Atividade.
"""

from uuid import UUID
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import exists, inspect
from app.models.atividade import Atividade
from app.models.atividade_projeto import AtividadeProjeto
from app.models.projeto import Projeto
from app.schemas.atividade import AtividadeCreate, AtividadeUpdate


class AtividadeRepository:
    """Repository para operações CRUD de Atividade."""

    def __init__(self, db: Session):
        self.db = db

    def _table_exists(self, table_name: str) -> bool:
        """Verifica se uma tabela existe no schema configurado."""
        schema = Atividade.__table__.schema
        inspector = inspect(self.db.get_bind())
        return table_name in inspector.get_table_names(schema=schema)

    def _validate_projetos(self, ids_projetos: list[UUID]) -> list[UUID]:
        """
        Valida se todos os IDs de projetos existem no banco de dados.
        Converte external_ids para ids internos quando necessário.

        Args:
            ids_projetos: Lista de UUIDs dos projetos (podem ser id ou external_id).

        Returns:
            Lista de IDs internos (projetos.id) dos projetos válidos.

        Raises:
            ValueError: Se algum projeto não existir.
        """
        projetos_existentes = (
            self.db.query(Projeto)
            .filter(
                (Projeto.id.in_(ids_projetos))
                | (Projeto.external_id.in_(ids_projetos))
            )
            .all()
        )

        # Mapeia external_id -> id interno e id -> id
        id_map = {}
        for projeto in projetos_existentes:
            id_map[projeto.id] = projeto.id
            if projeto.external_id:
                id_map[projeto.external_id] = projeto.id

        # Converte os IDs enviados para IDs internos
        ids_internos = []
        ids_invalidos = []
        for id_enviado in ids_projetos:
            if id_enviado in id_map:
                ids_internos.append(id_map[id_enviado])
            else:
                ids_invalidos.append(id_enviado)

        if ids_invalidos:
            raise ValueError(
                f"Projetos não encontrados: {', '.join(str(id) for id in ids_invalidos)}"
            )

        # Remove duplicados mantendo ordem
        return list(dict.fromkeys(ids_internos))

    def _criar_relacionamentos_projetos(
        self, atividade: Atividade, ids_projetos: list[UUID]
    ) -> None:
        """
        Cria os relacionamentos entre a atividade e os projetos.

        Args:
            atividade: Objeto Atividade.
            ids_projetos: Lista de UUIDs dos projetos.
        """
        for id_projeto in ids_projetos:
            atividade_projeto = AtividadeProjeto(
                id_atividade=atividade.id, id_projeto=id_projeto
            )
            self.db.add(atividade_projeto)

    def _atualizar_relacionamentos_projetos(
        self, atividade: Atividade, ids_projetos: list[UUID]
    ) -> None:
        """
        Atualiza os relacionamentos entre a atividade e os projetos.
        Remove todos os relacionamentos existentes e cria os novos.

        Args:
            atividade: Objeto Atividade.
            ids_projetos: Lista de UUIDs dos projetos.
        """
        # Remove todos os relacionamentos existentes
        self.db.query(AtividadeProjeto).filter(
            AtividadeProjeto.id_atividade == atividade.id
        ).delete()

        # Cria os novos relacionamentos
        self._criar_relacionamentos_projetos(atividade, ids_projetos)

    def create(
        self, atividade_data: AtividadeCreate, criado_por: str | None = None
    ) -> Atividade:
        """
        Cria uma nova atividade no banco de dados com relacionamentos N:N.

        Args:
            atividade_data: Objeto Pydantic com os dados da nova atividade.
            criado_por: Email ou ID do usuário que está criando a atividade.

        Returns:
            O objeto Atividade recém-criado e persistido.

        Raises:
            ValueError: Se algum projeto não existir.
        """
        # Validar projetos e obter IDs internos
        ids_projetos = atividade_data.ids_projetos
        ids_projetos_internos = self._validate_projetos(ids_projetos)

        # Criar atividade sem os campos de relacionamento
        atividade_dict = atividade_data.model_dump(
            exclude={"ids_projetos", "id_projeto"}
        )
        db_atividade = Atividade(**atividade_dict, criado_por=criado_por)
        self.db.add(db_atividade)
        self.db.flush()  # Gera o ID da atividade

        # Criar relacionamentos com projetos (usando IDs internos)
        self._criar_relacionamentos_projetos(db_atividade, ids_projetos_internos)

        self.db.commit()
        self.db.refresh(db_atividade)

        # Recarregar com os relacionamentos
        return self.get_by_id(db_atividade.id)

    def get_by_id(self, atividade_id: UUID) -> Atividade | None:
        """
        Busca uma atividade específica pelo seu ID único.
        Realiza eager loading dos projetos relacionados.

        Args:
            atividade_id: UUID da atividade.

        Returns:
            Objeto Atividade ou None se não encontrado.
        """
        if not self._table_exists(Atividade.__tablename__):
            return None

        if not self._table_exists(AtividadeProjeto.__tablename__):
            return (
                self.db.query(Atividade)
                .filter(Atividade.id == atividade_id)
                .first()
            )

        return (
            self.db.query(Atividade)
            .options(
                selectinload(Atividade.atividade_projetos).joinedload(
                    AtividadeProjeto.projeto
                )
            )
            .filter(Atividade.id == atividade_id)
            .first()
        )

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        ativo: bool | None = None,
        id_projeto: UUID | None = None,
    ) -> tuple[list[Atividade], int]:
        """
        Lista atividades com paginação e filtros opcionais.
        Retorna uma tupla (lista de atividades, total de registros).

        Args:
            skip: Número de registros a pular (paginação).
            limit: Máximo de registros a retornar.
            ativo: Filtro por status ativo/inativo.
            id_projeto: Filtro por projeto (retorna atividades que contêm este projeto).

        Returns:
            Tupla (lista de atividades, total de registros).
        """
        if not self._table_exists(Atividade.__tablename__):
            return [], 0

        has_rel_table = self._table_exists(AtividadeProjeto.__tablename__)

        query = self.db.query(Atividade)

        if has_rel_table:
            query = query.options(
                selectinload(Atividade.atividade_projetos).joinedload(
                    AtividadeProjeto.projeto
                )
            )

        # Aplicar filtro de status
        if ativo is not None:
            query = query.filter(Atividade.ativo == ativo)

        # Aplicar filtro de projeto (busca atividades que contêm o projeto)
        if id_projeto is not None and has_rel_table:
            query = query.filter(
                exists().where(
                    (AtividadeProjeto.id_atividade == Atividade.id)
                    & (AtividadeProjeto.id_projeto == id_projeto)
                )
            )

        if id_projeto is not None and not has_rel_table:
            return [], 0

        # Contar total antes de paginação
        total = query.count()

        # Aplicar paginação e ordenação
        atividades = (
            query.order_by(Atividade.criado_em.desc()).offset(skip).limit(limit).all()
        )

        return atividades, total

    def update(
        self, atividade_id: UUID, atividade_data: AtividadeUpdate
    ) -> Atividade | None:
        """
        Atualiza uma atividade existente.

        Args:
            atividade_id: UUID da atividade.
            atividade_data: Dados para atualização.

        Returns:
            Atividade atualizada ou None se não encontrada.

        Raises:
            ValueError: Se algum projeto não existir.
        """
        db_atividade = self.get_by_id(atividade_id)
        if not db_atividade:
            return None

        # Extrair dados de atualização
        update_data = atividade_data.model_dump(exclude_unset=True)

        # Tratar ids_projetos separadamente
        ids_projetos = update_data.pop("ids_projetos", None)

        # Tratar retrocompatibilidade: id_projeto -> ids_projetos
        id_projeto_legado = update_data.pop("id_projeto", None)
        if ids_projetos is None and id_projeto_legado is not None:
            ids_projetos = [id_projeto_legado]

        # Atualizar relacionamentos com projetos se fornecido
        if ids_projetos is not None:
            ids_projetos_internos = self._validate_projetos(ids_projetos)
            self._atualizar_relacionamentos_projetos(db_atividade, ids_projetos_internos)

        # Atualizar campos simples
        for field, value in update_data.items():
            setattr(db_atividade, field, value)

        self.db.commit()
        self.db.refresh(db_atividade)

        # Recarregar com os relacionamentos atualizados
        return self.get_by_id(atividade_id)

    def delete(self, atividade_id: UUID) -> bool:
        """
        Remove uma atividade (CASCADE remove relacionamentos automaticamente).

        Args:
            atividade_id: UUID da atividade.

        Returns:
            True se removida, False se não encontrada.
        """
        db_atividade = self.get_by_id(atividade_id)
        if not db_atividade:
            return False

        self.db.delete(db_atividade)
        self.db.commit()
        return True
