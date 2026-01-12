"""
Repository para operações de banco de dados da entidade Atividade.
"""

from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.models.atividade import Atividade
from app.schemas.atividade import AtividadeCreate, AtividadeUpdate


class AtividadeRepository:
    """Repository para operações CRUD de Atividade."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, atividade_data: AtividadeCreate) -> Atividade:
        """
        Cria uma nova atividade no banco de dados.

        Args:
            atividade_data: Objeto Pydantic com os dados da nova atividade.

        Returns:
            O objeto Atividade recém-criado e persistido.
        """
        db_atividade = Atividade(**atividade_data.model_dump())
        self.db.add(db_atividade)
        self.db.commit()
        self.db.refresh(db_atividade)
        return db_atividade

    def get_by_id(self, atividade_id: UUID) -> Atividade | None:
        """
        Busca uma atividade específica pelo seu ID único.
        Realiza um JOIN com a tabela de projetos para retornar o nome do projeto.

        Args:
            atividade_id: UUID da atividade.

        Returns:
            Objeto Atividade ou None se não encontrado.
        """
        return (
            self.db.query(Atividade)
            .options(joinedload(Atividade.projeto))
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
        """
        query = self.db.query(Atividade).options(joinedload(Atividade.projeto))

        # Aplicar filtros
        if ativo is not None:
            query = query.filter(Atividade.ativo == ativo)
        if id_projeto is not None:
            query = query.filter(Atividade.id_projeto == id_projeto)

        # Contar total
        total = query.count()

        # Aplicar paginação e ordenação
        atividades = (
            query.order_by(Atividade.criado_em.desc()).offset(skip).limit(limit).all()
        )

        return atividades, total

    def update(
        self, atividade_id: UUID, atividade_data: AtividadeUpdate
    ) -> Atividade | None:
        """Atualiza uma atividade existente."""
        db_atividade = self.get_by_id(atividade_id)
        if not db_atividade:
            return None

        # Atualizar apenas campos fornecidos
        update_data = atividade_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_atividade, field, value)

        self.db.commit()
        self.db.refresh(db_atividade)
        return db_atividade

    def delete(self, atividade_id: UUID) -> bool:
        """Remove uma atividade. Retorna True se removida."""
        db_atividade = self.get_by_id(atividade_id)
        if not db_atividade:
            return False

        self.db.delete(db_atividade)
        self.db.commit()
        return True
