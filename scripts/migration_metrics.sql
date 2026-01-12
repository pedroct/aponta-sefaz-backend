-- Script de criação do schema de métricas
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

COMMENT ON TABLE metrics.test_runs IS 'Registros históricos de execuções de testes do pipeline CI/CD';