import json
import os
import sys
import psycopg2
from datetime import datetime

# Tenta importar as configurações do app para pegar a URL do banco
try:
    # Adiciona o diretório raiz ao path para encontrar o módulo app
    sys.path.append(os.getcwd())
    from app.config import get_settings
    settings = get_settings()
    DATABASE_URL = settings.database_url
except Exception as e:
    print(f"⚠️ Não foi possível carregar settings. Usando variável de ambiente direta: {e}")
    DATABASE_URL = os.environ.get("DATABASE_URL")

def ensure_schema_exists(conn):
    print("[Métricas] Verificando/Criando schema...")
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE SCHEMA IF NOT EXISTS metrics;
            CREATE TABLE IF NOT EXISTS metrics.test_runs (
                id SERIAL PRIMARY KEY,
                project_id INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                branch_name TEXT,
                commit_sha TEXT,
                total_tests INTEGER,
                passed INTEGER,
                failed INTEGER,
                skipped INTEGER,
                duration_seconds FLOAT,
                coverage_percentage FLOAT
            );
        """)
        conn.commit()
    finally:
        cur.close()

def collect_metrics(report_path='report.json', project_id=None, branch=None, commit=None):
    print(f"[Métricas] Processando relatório: {report_path}")
    
    if not os.path.exists(report_path):
        print(f"[Métricas] Erro: Arquivo {report_path} não encontrado.")
        sys.exit(0)

    try:
        with open(report_path, 'r') as f:
            data = json.load(f)
            
        summary = data.get('summary', {})
        
        # Prioriza argumentos passados, depois variáveis de ambiente, depois default
        pid = project_id or os.environ.get("CI_PROJECT_ID", 0)
        b_name = branch or os.environ.get("CI_COMMIT_BRANCH", "local")
        c_sha = commit or os.environ.get("CI_COMMIT_SHA", "local")

        metrics = {
            "project_id": int(pid) if str(pid).isdigit() else 0,
            "branch": b_name,
            "commit": c_sha,
            "total": summary.get('total', 0),
            "passed": summary.get('passed', 0),
            "failed": summary.get('failed', 0),
            "skipped": summary.get('skipped', 0),
            "duration": data.get('duration', 0.0),
            "coverage": 0.0
        }

        print(f"[Métricas] Dados extraídos: Project ID {metrics['project_id']}, Branch {metrics['branch']}, {metrics['passed']}/{metrics['total']} passados em {metrics['duration']:.2f}s")

        if not DATABASE_URL:
            print("[Métricas] Erro: DATABASE_URL não configurada.")
            return

        print("[Métricas] Gravando no PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        ensure_schema_exists(conn)
        cur = conn.cursor()
        
        query = """
            INSERT INTO metrics.test_runs 
            (project_id, branch_name, commit_sha, total_tests, passed, failed, skipped, duration_seconds) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cur.execute(query, (
            metrics['project_id'],
            metrics['branch'],
            metrics['commit'],
            metrics['total'],
            metrics['passed'],
            metrics['failed'],
            metrics['skipped'],
            metrics['duration']
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        print("[Métricas] Status: Sucesso!")

    except Exception as e:
        print(f"[Métricas] Erro ao processar: {e}")
        # Not exiting with error to keep pipeline stable as per plan

if __name__ == "__main__":
    # Suporta: collect_metrics.py [report.json] [project_id] [branch] [commit]
    path = sys.argv[1] if len(sys.argv) > 1 else 'report.json'
    pid = sys.argv[2] if len(sys.argv) > 2 else None
    branch = sys.argv[3] if len(sys.argv) > 3 else None
    commit = sys.argv[4] if len(sys.argv) > 4 else None
    
    collect_metrics(path, pid, branch, commit)
