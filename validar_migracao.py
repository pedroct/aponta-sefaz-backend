#!/usr/bin/env python3
"""
Script de teste para validar a normalização de project_id.
Executa verificações antes e depois da migração.
"""

import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.apontamento import Apontamento
from app.models.projeto import Projeto
from sqlalchemy import text, func


def verificar_projetos():
    """Verifica projetos disponíveis na tabela projetos."""
    print("=" * 80)
    print("VERIFICANDO PROJETOS DISPONÍVEIS")
    print("=" * 80)
    
    db = SessionLocal()
    try:
        projetos = db.query(Projeto).all()
        
        if not projetos:
            print("⚠️  ATENÇÃO: Nenhum projeto encontrado na tabela 'projetos'!")
            print("   Adicione projetos antes de executar a migração.")
            return False
        
        print(f"\n✓ {len(projetos)} projeto(s) encontrado(s):\n")
        
        for projeto in projetos:
            print(f"  Nome: {projeto.nome}")
            print(f"  UUID: {projeto.external_id}")
            print(f"  Descrição: {projeto.descricao or 'N/A'}")
            print()
        
        return True
        
    finally:
        db.close()


def verificar_apontamentos_por_formato():
    """Verifica quantos apontamentos existem por formato de project_id."""
    print("=" * 80)
    print("VERIFICANDO FORMATO DOS APONTAMENTOS")
    print("=" * 80)
    
    db = SessionLocal()
    try:
        # Contar por formato
        result = db.execute(text("""
            SELECT 
                CASE 
                    WHEN project_id LIKE '%-%' AND LENGTH(project_id) >= 36 THEN 'UUID'
                    ELSE 'NOME'
                END as formato,
                COUNT(*) as total
            FROM apontamentos
            GROUP BY formato
            ORDER BY formato DESC
        """))
        
        formatos = dict(result.fetchall())
        
        total = sum(formatos.values())
        uuid_count = formatos.get('UUID', 0)
        nome_count = formatos.get('NOME', 0)
        
        print(f"\nTotal de apontamentos: {total}")
        print(f"  ✓ UUID (novo formato): {uuid_count}")
        print(f"  ⚠ NOME (formato antigo): {nome_count}")
        
        if nome_count > 0:
            print(f"\n⚠️  {nome_count} registro(s) precisam ser migrados!")
            
            # Mostrar quais nomes existem
            result = db.execute(text("""
                SELECT DISTINCT project_id, COUNT(*) as total
                FROM apontamentos
                WHERE project_id NOT LIKE '%-%' 
                  AND LENGTH(project_id) < 36
                GROUP BY project_id
                ORDER BY total DESC
            """))
            
            print("\nNomes de projeto encontrados:")
            for row in result:
                print(f"  - '{row[0]}': {row[1]} registro(s)")
        else:
            print("\n✓ Todos os apontamentos já estão no formato UUID!")
        
        return nome_count == 0
        
    finally:
        db.close()


def testar_normalizacao():
    """Testa a função de normalização sem modificar o banco."""
    print("\n" + "=" * 80)
    print("TESTANDO NORMALIZAÇÃO (SEM MODIFICAR O BANCO)")
    print("=" * 80)
    
    from app.utils.project_id_normalizer import (
        is_valid_uuid,
        normalize_project_id,
        validate_project_id_format,
    )
    
    db = SessionLocal()
    try:
        # Testes de validação
        print("\n1. Teste de validação de UUID:")
        test_cases = [
            ("50a9ca09-710f-4478-8278-2d069902d2af", True),
            ("DEV", False),
            ("", False),
        ]
        
        for value, expected in test_cases:
            result = is_valid_uuid(value)
            status = "✓" if result == expected else "✗"
            print(f"  {status} is_valid_uuid('{value}') = {result}")
        
        # Teste de normalização com projetos reais
        print("\n2. Teste de normalização com projetos do banco:")
        
        # Buscar projetos
        projetos = db.query(Projeto).limit(3).all()
        
        for projeto in projetos:
            # Testar com UUID
            try:
                result = normalize_project_id(str(projeto.external_id), db)
                print(f"  ✓ normalize('{projeto.external_id}') = '{result}'")
            except Exception as e:
                print(f"  ✗ normalize('{projeto.external_id}') falhou: {e}")
            
            # Testar com nome
            try:
                result = normalize_project_id(projeto.nome, db)
                print(f"  ✓ normalize('{projeto.nome}') = '{result}'")
            except Exception as e:
                print(f"  ✗ normalize('{projeto.nome}') falhou: {e}")
        
        # Testar com projeto inexistente
        print("\n3. Teste com projeto inexistente (deve falhar):")
        try:
            result = normalize_project_id("PROJETO_INEXISTENTE", db)
            print(f"  ✗ Deveria ter falhado mas retornou: {result}")
        except ValueError as e:
            print(f"  ✓ Falhou como esperado: {e}")
        
    finally:
        db.close()


def simular_migracao():
    """Simula a migração sem executá-la de fato."""
    print("\n" + "=" * 80)
    print("SIMULANDO MIGRAÇÃO (DRY RUN)")
    print("=" * 80)
    
    db = SessionLocal()
    try:
        # Buscar apontamentos com formato antigo
        result = db.execute(text("""
            SELECT DISTINCT project_id 
            FROM apontamentos 
            WHERE project_id NOT LIKE '%-%'
              AND LENGTH(project_id) < 36
        """))
        
        project_names = [row[0] for row in result]
        
        if not project_names:
            print("\n✓ Nenhum registro para migrar!")
            return
        
        print(f"\n{len(project_names)} project_id(s) serão migrados:\n")
        
        for project_name in project_names:
            # Buscar UUID correspondente
            uuid_result = db.execute(text("""
                SELECT CAST(external_id AS TEXT), nome
                FROM projetos 
                WHERE UPPER(nome) = UPPER(:project_name)
                LIMIT 1
            """), {"project_name": project_name})
            
            row = uuid_result.fetchone()
            
            # Contar apontamentos
            count_result = db.execute(text("""
                SELECT COUNT(*) 
                FROM apontamentos 
                WHERE project_id = :project_name
            """), {"project_name": project_name})
            
            count = count_result.scalar()
            
            if row:
                project_uuid, projeto_nome = row
                print(f"  ✓ '{project_name}' → '{project_uuid}'")
                print(f"    Projeto: {projeto_nome}")
                print(f"    Afetará {count} registro(s)")
            else:
                print(f"  ✗ '{project_name}' → PROJETO NÃO ENCONTRADO!")
                print(f"    ⚠️  {count} registro(s) NÃO serão migrados")
            
            print()
        
    finally:
        db.close()


def main():
    """Executa todos os testes."""
    print("\n")
    print("█" * 80)
    print(" " * 20 + "VALIDAÇÃO DE MIGRAÇÃO PROJECT_ID")
    print("█" * 80)
    print()
    
    try:
        # 1. Verificar projetos
        tem_projetos = verificar_projetos()
        
        if not tem_projetos:
            print("\n❌ Adicione projetos na tabela antes de continuar!")
            return 1
        
        input("\n🔍 Pressione ENTER para continuar...")
        
        # 2. Verificar apontamentos
        tudo_migrado = verificar_apontamentos_por_formato()
        
        input("\n🔍 Pressione ENTER para continuar...")
        
        # 3. Testar normalização
        testar_normalizacao()
        
        input("\n🔍 Pressione ENTER para continuar...")
        
        # 4. Simular migração
        if not tudo_migrado:
            simular_migracao()
        
        # Resumo final
        print("\n" + "=" * 80)
        print("RESUMO")
        print("=" * 80)
        
        if tudo_migrado:
            print("\n✅ Sistema está pronto! Todos os registros já estão no formato UUID.")
        else:
            print("\n⚠️  Migração necessária!")
            print("\nPara executar a migração:")
            print("  alembic upgrade head")
            print("\nDepois execute este script novamente para validar.")
        
        print("\n" + "█" * 80)
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Teste cancelado pelo usuário.")
        return 130
    except Exception as e:
        print(f"\n\n❌ Erro durante a validação: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
