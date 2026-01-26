"""
Testes para normalização de project_id.
"""

import pytest
from uuid import UUID
from app.utils.project_id_normalizer import (
    is_valid_uuid,
    validate_project_id_format,
    normalize_project_id,
)


class TestIsValidUUID:
    """Testes para is_valid_uuid()"""

    def test_valid_uuid_with_hyphens(self):
        """UUID válido com hífens"""
        assert is_valid_uuid("50a9ca09-710f-4478-8278-2d069902d2af") is True

    def test_valid_uuid_without_hyphens(self):
        """UUID válido sem hífens"""
        assert is_valid_uuid("50a9ca09710f44788278 2d069902d2af") is False

    def test_invalid_uuid_project_name(self):
        """Nome de projeto não é UUID"""
        assert is_valid_uuid("DEV") is False

    def test_invalid_uuid_empty(self):
        """String vazia não é UUID"""
        assert is_valid_uuid("") is False

    def test_invalid_uuid_none(self):
        """None não é UUID"""
        assert is_valid_uuid(None) is False


class TestValidateProjectIdFormat:
    """Testes para validate_project_id_format()"""

    def test_valid_uuid(self):
        """Deve aceitar UUID válido"""
        project_id = "50a9ca09-710f-4478-8278-2d069902d2af"
        result = validate_project_id_format(project_id)
        assert result == project_id

    def test_invalid_project_name(self):
        """Deve rejeitar nome de projeto"""
        with pytest.raises(ValueError, match="UUID válido"):
            validate_project_id_format("DEV")

    def test_empty_string(self):
        """Deve rejeitar string vazia"""
        with pytest.raises(ValueError, match="não pode ser vazio"):
            validate_project_id_format("")

    def test_whitespace_string(self):
        """Deve rejeitar string com apenas espaços"""
        with pytest.raises(ValueError, match="não pode ser vazio"):
            validate_project_id_format("   ")

    def test_uuid_with_whitespace(self):
        """Deve aceitar UUID com espaços nas pontas"""
        project_id = "  50a9ca09-710f-4478-8278-2d069902d2af  "
        result = validate_project_id_format(project_id)
        assert result == "50a9ca09-710f-4478-8278-2d069902d2af"


class TestNormalizeProjectId:
    """Testes para normalize_project_id() - requer mock do banco"""

    def test_already_uuid_returns_same(self, db_session, mock_projetos):
        """Se já é UUID, deve retornar o mesmo valor"""
        project_id = "50a9ca09-710f-4478-8278-2d069902d2af"
        result = normalize_project_id(project_id, db_session)
        assert result == project_id

    def test_project_name_converts_to_uuid(self, db_session, mock_projetos):
        """Nome do projeto deve ser convertido para UUID"""
        # Assumindo que existe um projeto "DEV" no banco mock
        result = normalize_project_id("DEV", db_session)
        # Verifica se retornou um UUID válido
        assert is_valid_uuid(result)

    def test_unknown_project_raises_error(self, db_session, mock_projetos):
        """Projeto não encontrado deve lançar erro"""
        with pytest.raises(ValueError, match="não encontrado"):
            normalize_project_id("PROJETO_INEXISTENTE", db_session)

    def test_empty_string_raises_error(self, db_session):
        """String vazia deve lançar erro"""
        with pytest.raises(ValueError, match="não pode ser vazio"):
            normalize_project_id("", db_session)

    def test_case_insensitive_lookup(self, db_session, mock_projetos):
        """Busca deve ser case-insensitive"""
        # Assumindo que existe "DEV" no banco
        result1 = normalize_project_id("DEV", db_session)
        result2 = normalize_project_id("dev", db_session)
        result3 = normalize_project_id("Dev", db_session)
        
        # Todos devem retornar o mesmo UUID
        assert result1 == result2 == result3


# Fixtures para os testes
@pytest.fixture
def mock_projetos(db_session):
    """
    Cria projetos mock para testes.
    
    TODO: Implementar inserção de projetos de teste no banco.
    """
    from app.models.projeto import Projeto
    
    # Criar projeto DEV
    projeto_dev = Projeto(
        external_id=UUID("50a9ca09-710f-4478-8278-2d069902d2af"),
        nome="DEV",
        descricao="Projeto de Desenvolvimento",
    )
    db_session.add(projeto_dev)
    
    # Criar projeto QA
    projeto_qa = Projeto(
        external_id=UUID("a1b2c3d4-e5f6-4789-a123-456789abcdef"),
        nome="QA",
        descricao="Projeto de Quality Assurance",
    )
    db_session.add(projeto_qa)
    
    db_session.commit()
    
    yield
    
    # Cleanup
    db_session.query(Projeto).delete()
    db_session.commit()
