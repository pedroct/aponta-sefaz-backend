# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-12

### Added
- Initial project setup for Hostinger VPS deployment
- Docker Compose with Nginx, API, and PostgreSQL 15
- Nginx reverse proxy configuration (ports 80/443)
- Multi-stage Dockerfile optimized for production
- Alembic database migrations
- FastAPI application with routers for atividades, projetos, and integracao
- Health check endpoints
- Deploy script for automated deployment
