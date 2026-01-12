# Architecture Documentation

**API Aponta VPS - System Architecture**

Version: 0.1.0
Last Updated: 2026-01-12

---

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagrams](#architecture-diagrams)
- [Component Descriptions](#component-descriptions)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)
- [Deployment Architecture](#deployment-architecture)
- [Technology Stack](#technology-stack)
- [Design Patterns](#design-patterns)
- [Scalability Considerations](#scalability-considerations)
- [Monitoring and Observability](#monitoring-and-observability)

---

## System Overview

API Aponta is a production-grade REST API backend built with FastAPI, designed to manage activities and projects integrated with Azure DevOps. The system is deployed on a Hostinger VPS with CloudFlare CDN/proxy for enhanced security, performance, and reliability.

### Key Features

- **RESTful API** with automatic OpenAPI (Swagger) documentation
- **CRUD Operations** for activities and projects
- **Azure DevOps Integration** with secure authentication
- **Multi-layer Security** with CloudFlare and Nginx
- **Containerized Deployment** using Docker Compose
- **Database Migrations** with Alembic
- **Health Monitoring** across all services

### System Characteristics

- **High Availability**: Health checks on all components
- **Security First**: Multi-layer security with HTTPS, rate limiting, and token authentication
- **Performance**: Nginx caching, gzip compression, connection pooling
- **Maintainability**: Clean architecture with separation of concerns
- **Scalability**: Container-based deployment ready for horizontal scaling

---

## Architecture Diagrams

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        Internet                               │
└───────────────────────────┬──────────────────────────────────┘
                            │ HTTPS (TLS 1.2/1.3)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     CloudFlare CDN                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ - DDoS Protection (L3, L4, L7)                        │  │
│  │ - SSL/TLS Termination (Full Strict Mode)             │  │
│  │ - Web Application Firewall (WAF)                      │  │
│  │ - Global CDN with Edge Caching                        │  │
│  │ - Rate Limiting (Global)                              │  │
│  │ - DNS Management                                      │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS (Origin Certificate)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              VPS Hostinger (31.97.16.12)                     │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Nginx Proxy (Alpine)                      │ │
│  │              Ports: 80 (HTTP), 443 (HTTPS)             │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ - Reverse Proxy                                  │  │ │
│  │  │ - Rate Limiting (10 req/s, burst 20)            │  │ │
│  │  │ - Gzip Compression                               │  │ │
│  │  │ - SSL/TLS (Origin Certificate)                   │  │ │
│  │  │ - CloudFlare IP Whitelisting                     │  │ │
│  │  │ - Connection Pooling (keepalive 32)              │  │ │
│  │  │ - Health Check Endpoint                          │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └───────────────────────┬────────────────────────────────┘ │
│                          │ HTTP                              │
│                          ▼                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           FastAPI Application (Python 3.12)            │ │
│  │                   Port: 8000                            │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ - REST API Endpoints                             │  │ │
│  │  │ - Azure DevOps Authentication                    │  │ │
│  │  │ - Business Logic Layer                           │  │ │
│  │  │ - SQLAlchemy ORM                                 │  │ │
│  │  │ - Pydantic Validation                            │  │ │
│  │  │ - CORS Middleware                                │  │ │
│  │  │ - Health Check                                   │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └───────────────────────┬────────────────────────────────┘ │
│                          │ PostgreSQL Protocol               │
│                          ▼                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          PostgreSQL 15 (Alpine)                        │ │
│  │                   Port: 5432                            │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │ - Relational Database                            │  │ │
│  │  │ - Schema: api_aponta                             │  │ │
│  │  │ - Tables: atividades, projetos                   │  │ │
│  │  │ - ACID Transactions                              │  │ │
│  │  │ - Persistent Volume Storage                      │  │ │
│  │  │ - Health Check                                   │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                               │
│  Network: aponta-network (Bridge)                            │
└───────────────────────────────────────────────────────────────┘

External Integration:
┌────────────────────────┐
│   Azure DevOps API     │
│   (dev.azure.com)      │
│  - Project Management  │
│  - Authentication      │
└────────────────────────┘
```

### Application Layer Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      FastAPI Application                      │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐│
│  │                    Presentation Layer                     ││
│  │  ┌────────────┐  ┌────────────┐  ┌───────────────────┐  ││
│  │  │  Routers   │  │  Schemas   │  │   Middlewares     │  ││
│  │  │            │  │            │  │                   │  ││
│  │  │ atividades │  │ AtividadeX │  │ CORS              │  ││
│  │  │ projetos   │  │ ProjetoX   │  │ Error Handler     │  ││
│  │  │ integracao │  │ ResponseX  │  │ Request Logger    │  ││
│  │  └────────────┘  └────────────┘  └───────────────────┘  ││
│  └──────────────────────────────────────────────────────────┘│
│                              │                                 │
│  ┌──────────────────────────┼───────────────────────────────┐│
│  │                    Business Layer                         ││
│  │  ┌────────────┐  ┌────────────┐  ┌───────────────────┐  ││
│  │  │  Services  │  │    Auth    │  │   Repositories    │  ││
│  │  │            │  │            │  │                   │  ││
│  │  │ AzureService│  │ JWT/Token  │  │ AtividadeRepo    │  ││
│  │  │ ProjetoSvc │  │ Validation │  │                   │  ││
│  │  └────────────┘  └────────────┘  └───────────────────┘  ││
│  └──────────────────────────────────────────────────────────┘│
│                              │                                 │
│  ┌──────────────────────────┼───────────────────────────────┐│
│  │                      Data Layer                           ││
│  │  ┌────────────┐  ┌────────────┐  ┌───────────────────┐  ││
│  │  │   Models   │  │  Database  │  │   Migrations      │  ││
│  │  │            │  │            │  │                   │  ││
│  │  │ Atividade  │  │ SQLAlchemy │  │ Alembic           │  ││
│  │  │ Projeto    │  │ Connection │  │ Versions          │  ││
│  │  └────────────┘  └────────────┘  └───────────────────┘  ││
│  └──────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

### Network Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Network                           │
│                   (aponta-network - Bridge)                  │
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │    nginx     │─────▶│     api      │─────▶│ postgres  │ │
│  │  :80, :443   │      │    :8000     │      │   :5432   │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│       │                       │                      │       │
│       │                       │                      │       │
│  External Ports          Internal Only         Persistent   │
│  (Host mapping)                                  Volume      │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Descriptions

### 1. CloudFlare CDN/Proxy

**Purpose**: First line of defense and global content delivery

**Responsibilities**:
- DNS management for api-aponta.pedroct.com.br
- SSL/TLS encryption (client to CloudFlare)
- DDoS protection (Layer 3, 4, and 7)
- Web Application Firewall (WAF)
- Global edge caching
- Rate limiting at the edge
- Origin server protection

**Configuration**:
- SSL/TLS Mode: Full (Strict)
- Origin Certificates: Installed on Nginx
- IPv4: Proxied through CloudFlare
- Security Level: Medium
- Bot Fight Mode: Enabled

**Key Features**:
- Anycast network for low latency
- Automatic HTTPS rewrites
- HTTP/2 and HTTP/3 support
- DNSSEC enabled

### 2. Nginx Reverse Proxy

**Purpose**: Application gateway and security layer

**Technology**: Nginx Alpine (lightweight container)

**Responsibilities**:
- Reverse proxy to FastAPI application
- SSL/TLS termination (CloudFlare Origin Certificate)
- Rate limiting (10 req/s with burst of 20)
- Gzip compression
- Connection pooling (keepalive 32)
- Header manipulation
- Real IP extraction from CloudFlare
- Health check endpoint

**Configuration Highlights**:
```nginx
# Rate Limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# Upstream with connection pooling
upstream api_backend {
    server api:8000;
    keepalive 32;
}

# SSL Configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
```

**Ports**:
- 80 (HTTP) - Accepts CloudFlare traffic
- 443 (HTTPS) - Origin Certificate SSL

**Health Check**:
- Endpoint: `/nginx-health`
- Interval: 30s

### 3. FastAPI Application

**Purpose**: Core business logic and REST API

**Technology**: FastAPI 0.109.0 + Uvicorn on Python 3.12

**Architecture Pattern**: Layered Architecture
- **Routers**: HTTP request handlers
- **Schemas**: Pydantic models for validation
- **Services**: Business logic layer
- **Repositories**: Data access layer
- **Models**: SQLAlchemy ORM models

**Key Components**:

#### Routers (Presentation Layer)
- `atividades.py`: CRUD endpoints for activities
- `projetos.py`: Project listing and synchronization
- `integracao.py`: Azure DevOps integration endpoints

#### Authentication
- Azure DevOps token validation
- Personal Access Token (PAT) support
- Bearer token authentication
- Development mode bypass

#### Middleware
- CORS with configurable origins
- Request/response logging
- Error handling

#### Database Integration
- SQLAlchemy 2.0 async support
- Connection pooling
- Schema-based multi-tenancy support
- Alembic migrations

**Configuration**:
- Port: 8000 (internal only)
- Workers: 1 (Uvicorn)
- Environment variables via .env file
- Health check: `/health`, `/healthz`, `/`

**API Endpoints**:
```
GET  /                          # Health check
GET  /health                    # Health check
GET  /healthz                   # Health check
GET  /api/v1                    # API info
GET  /docs                      # Swagger UI
GET  /redoc                     # ReDoc documentation

# Atividades
GET    /api/v1/atividades       # List activities
POST   /api/v1/atividades       # Create activity
GET    /api/v1/atividades/{id}  # Get activity
PUT    /api/v1/atividades/{id}  # Update activity
DELETE /api/v1/atividades/{id}  # Delete activity

# Projetos
GET    /api/v1/projetos         # List projects
POST   /api/v1/integracao/sincronizar  # Sync projects

# Integração
GET    /api/v1/integracao/projetos     # List Azure DevOps projects
```

### 4. PostgreSQL Database

**Purpose**: Persistent data storage

**Technology**: PostgreSQL 15 Alpine

**Configuration**:
- Port: 5432 (exposed for management)
- Database: gestao_projetos
- Schema: api_aponta
- User: api-aponta-user (configurable)
- Volume: postgres_data (persistent)

**Tables**:

#### atividades
```sql
- id (UUID, PK)
- nome (VARCHAR(255), NOT NULL)
- descricao (TEXT)
- ativo (BOOLEAN, DEFAULT true)
- id_projeto (UUID, FK)
- criado_em (TIMESTAMP)
- atualizado_em (TIMESTAMP)
```

#### projetos
```sql
- id (UUID, PK)
- nome (VARCHAR(255), NOT NULL)
- azure_project_id (VARCHAR)
- criado_em (TIMESTAMP)
- atualizado_em (TIMESTAMP)
```

**Features**:
- ACID compliance
- Row-level security (future)
- Automatic timestamps
- Foreign key constraints
- Indexes on frequently queried columns

**Health Check**:
- Command: `pg_isready`
- Interval: 10s

**Backup Strategy** (planned):
- Daily automated backups
- Point-in-time recovery
- Offsite backup storage

### 5. Azure DevOps Integration

**Purpose**: External authentication and project synchronization

**Integration Points**:
- Authentication via Personal Access Token (PAT)
- Project listing and synchronization
- User profile validation
- Organization data access

**API Endpoints Used**:
```
GET https://dev.azure.com/{org}/_apis/connectionData
GET https://dev.azure.com/{org}/_apis/projects
GET https://app.vssps.visualstudio.com/_apis/profile/profiles/me
```

**Authentication Flow**:
1. Client sends Bearer token or PAT
2. API validates token with Azure DevOps
3. User profile retrieved and cached
4. Token attached to user session
5. Subsequent requests use validated user context

---

## Data Flow

### Request Flow (Read Operation)

```
1. Client Request
   │
   ├─▶ HTTPS to api-aponta.pedroct.com.br
   │
2. CloudFlare Processing
   │
   ├─▶ DNS Resolution
   ├─▶ DDoS Check
   ├─▶ WAF Rules
   ├─▶ Rate Limiting (Global)
   ├─▶ Cache Check (if applicable)
   │
3. Origin Request
   │
   ├─▶ HTTPS to VPS (31.97.16.12)
   │
4. Nginx Processing
   │
   ├─▶ SSL Termination
   ├─▶ Rate Limiting (10 req/s)
   ├─▶ Real IP Extraction
   ├─▶ Proxy to api:8000
   │
5. FastAPI Processing
   │
   ├─▶ CORS Check
   ├─▶ Route Matching
   ├─▶ Authentication Validation
   │   └─▶ Azure DevOps API Call
   ├─▶ Request Validation (Pydantic)
   ├─▶ Business Logic (Service Layer)
   ├─▶ Database Query (Repository)
   │
6. PostgreSQL Processing
   │
   ├─▶ Query Execution
   ├─▶ Result Set Return
   │
7. Response Generation
   │
   ├─▶ ORM to Pydantic Model
   ├─▶ JSON Serialization
   ├─▶ Response Headers
   │
8. Nginx Response
   │
   ├─▶ Gzip Compression
   ├─▶ Cache Headers
   │
9. CloudFlare Response
   │
   ├─▶ Edge Caching (if applicable)
   ├─▶ Compression
   │
10. Client Receives Response
```

### Write Operation Flow (Create/Update)

```
1. Client Request with JSON Body
   │
   [Steps 2-5 same as above]
   │
6. FastAPI Validation
   │
   ├─▶ Schema Validation (Pydantic)
   ├─▶ Business Rules Validation
   ├─▶ Authorization Check
   │
7. Repository Layer
   │
   ├─▶ Create ORM Model Instance
   ├─▶ Begin Transaction
   │
8. PostgreSQL Processing
   │
   ├─▶ INSERT/UPDATE Query
   ├─▶ Constraint Validation
   ├─▶ Trigger Execution (if any)
   ├─▶ Transaction Commit
   │
9. Response Generation
   │
   ├─▶ Refresh ORM Instance
   ├─▶ Convert to Response Schema
   ├─▶ Return 201 Created or 200 OK
   │
   [Steps 8-10 same as read flow]
```

### Authentication Flow

```
1. Client Request with Authorization Header
   │
   └─▶ Authorization: Bearer <token>
   │
2. FastAPI Security Middleware
   │
   ├─▶ Extract Token from Header
   │
3. Authentication Validation (auth.py)
   │
   ├─▶ Check AUTH_ENABLED setting
   │   │
   │   ├─▶ If false: Return mock user
   │   │
   │   └─▶ If true: Validate with Azure DevOps
   │       │
   │       ├─▶ Try as PAT (Basic Auth)
   │       │   └─▶ GET connectionData API
   │       │
   │       ├─▶ Try as Bearer Token
   │       │   └─▶ GET connectionData API
   │       │
   │       └─▶ Extract User Profile
   │           ├─▶ User ID
   │           ├─▶ Display Name
   │           ├─▶ Email
   │           └─▶ Token (for subsequent calls)
   │
4. User Context Created
   │
   └─▶ AzureDevOpsUser object injected into endpoint
```

---

## Security Architecture

### Multi-Layer Security Model

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: CloudFlare Edge Security                            │
│ - DDoS Protection (L3, L4, L7)                               │
│ - WAF Rules                                                   │
│ - Bot Protection                                              │
│ - Rate Limiting (Global)                                      │
│ - SSL/TLS Encryption (Client to Edge)                        │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Nginx Security                                       │
│ - SSL/TLS Encryption (Edge to Origin)                        │
│ - CloudFlare IP Whitelisting                                 │
│ - Rate Limiting (10 req/s per IP)                            │
│ - Server Token Hiding                                         │
│ - Request Size Limits                                         │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Application Security                                │
│ - Azure DevOps Authentication                                │
│ - Token Validation                                            │
│ - CORS Policy Enforcement                                     │
│ - Input Validation (Pydantic)                                │
│ - SQL Injection Prevention (ORM)                             │
│ - XSS Prevention (JSON API)                                  │
└─────────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Data Security                                        │
│ - Database User Isolation                                     │
│ - Schema-based Multi-tenancy                                 │
│ - Prepared Statements                                         │
│ - Connection Encryption (internal network)                   │
└─────────────────────────────────────────────────────────────┘
```

### Security Features

#### 1. Transport Security
- **CloudFlare to Client**: TLS 1.2/1.3 with strong ciphers
- **CloudFlare to Origin**: TLS 1.2/1.3 with Origin Certificate
- **Origin to Backend**: HTTP (internal Docker network)
- **Certificate Management**: CloudFlare Origin Certificate (15-year validity)

#### 2. Authentication & Authorization
- **Token-based Authentication**: Azure DevOps PAT or Bearer tokens
- **Token Validation**: Real-time validation with Azure DevOps API
- **User Context**: Injected into all protected endpoints
- **Development Mode**: Bypass authentication for local development

#### 3. Rate Limiting
- **CloudFlare Level**: Configurable per zone
- **Nginx Level**: 10 requests/second per IP with burst of 20
- **Burst Handling**: Queued requests with nodelay processing

#### 4. Input Validation
- **Schema Validation**: Pydantic models with type checking
- **Field Constraints**: Length, format, and range validation
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **XSS Prevention**: JSON responses (automatic escaping)

#### 5. Container Security
- **Non-root User**: Application runs as appuser (non-privileged)
- **Multi-stage Build**: Minimal production image
- **No Build Tools**: Production image excludes compilers
- **Read-only Volumes**: Nginx configuration mounted as read-only

#### 6. Network Security
- **Internal Network**: Docker bridge network (aponta-network)
- **Port Exposure**: Only Nginx ports exposed to host
- **CloudFlare IPs**: Real IP extraction and validation
- **Service Isolation**: Each service in separate container

#### 7. Secrets Management
- **Environment Variables**: Sensitive data in .env file
- **No Hardcoded Secrets**: All credentials via configuration
- **Git Ignore**: .env file not versioned
- **Access Control**: File permissions on .env (600)

### Security Best Practices Implemented

1. **Least Privilege**: Containers run with minimal permissions
2. **Defense in Depth**: Multiple security layers
3. **Fail Secure**: Authentication required by default
4. **Security by Default**: Secure defaults in all configurations
5. **Audit Trail**: Request logging for security analysis
6. **Regular Updates**: Alpine-based images for security patches

---

## Deployment Architecture

### Container Orchestration

**Technology**: Docker Compose

**Network**: Bridge network (aponta-network)

**Volumes**:
- `postgres_data`: Persistent database storage
- `./nginx/nginx.conf`: Nginx configuration (read-only)
- `./nginx/ssl`: SSL certificates (read-only)

### Service Dependencies

```
postgres
  │
  ├─▶ api (depends on postgres)
  │   │
  │   └─▶ nginx (depends on api)
```

**Health Checks**:
- PostgreSQL: 10s interval, pg_isready check
- FastAPI: 30s interval, HTTP GET /health
- Nginx: 30s interval, nginx -t validation

**Restart Policy**: unless-stopped (automatic restart on failure)

### Deployment Process

```
1. Pre-deployment
   ├─▶ Validate .env file exists
   ├─▶ Check SSL certificates
   └─▶ Stop existing containers

2. Build Phase
   ├─▶ Build FastAPI image (multi-stage)
   ├─▶ Pull Nginx Alpine image
   └─▶ Pull PostgreSQL 15 Alpine image

3. Startup Phase
   ├─▶ Create Docker network
   ├─▶ Start PostgreSQL container
   │   └─▶ Wait for health check
   ├─▶ Start FastAPI container
   │   ├─▶ Run Alembic migrations
   │   └─▶ Wait for health check
   └─▶ Start Nginx container
       └─▶ Wait for health check

4. Post-deployment
   ├─▶ Verify all containers running
   ├─▶ Test health endpoints
   └─▶ Monitor logs for errors
```

### Rollback Strategy

```
1. Detect Failure
   ├─▶ Health check failures
   ├─▶ Application errors
   └─▶ Performance degradation

2. Immediate Actions
   ├─▶ Stop new deployments
   ├─▶ Preserve logs and metrics
   └─▶ Notify team

3. Rollback Execution
   ├─▶ Stop current containers
   ├─▶ Restore previous image versions
   ├─▶ Rollback database migrations (if needed)
   └─▶ Restart services

4. Verification
   ├─▶ Run health checks
   ├─▶ Test critical endpoints
   └─▶ Monitor error rates
```

### Environment Configuration

**Development**:
```
- AUTH_ENABLED=false
- API_DEBUG=true
- ENVIRONMENT=development
- Local PostgreSQL or Supabase
```

**Production**:
```
- AUTH_ENABLED=true
- API_DEBUG=false
- ENVIRONMENT=production
- VPS PostgreSQL container
- CloudFlare enabled
```

---

## Technology Stack

### Backend Framework

**FastAPI 0.109.0**
- Modern Python web framework
- Automatic OpenAPI documentation
- High performance (comparable to Node.js and Go)
- Type hints and validation
- Async support
- Dependency injection

**Python 3.12**
- Latest stable Python version
- Performance improvements
- Enhanced type hints
- Security updates

**Uvicorn**
- ASGI server
- High performance
- WebSocket support
- Graceful shutdown

### Database

**PostgreSQL 15**
- Mature relational database
- ACID compliance
- JSON support
- Full-text search
- Window functions
- Advanced indexing

**SQLAlchemy 2.0**
- Modern ORM
- Async support
- Type safety
- Relationship management
- Query builder

**Alembic**
- Database migrations
- Version control for schema
- Upgrade/downgrade support
- Auto-generation from models

### Infrastructure

**Docker**
- Containerization
- Consistent environments
- Resource isolation
- Easy deployment

**Docker Compose**
- Multi-container orchestration
- Service dependencies
- Network management
- Volume management

**Nginx Alpine**
- Lightweight reverse proxy
- High performance
- Minimal attack surface
- Low memory footprint

**CloudFlare**
- CDN and edge network
- DDoS protection
- SSL/TLS management
- DNS management
- WAF and security

### Development Tools

**Code Quality**:
- Black: Code formatting
- isort: Import sorting
- Flake8: Linting
- MyPy: Static type checking

**Testing**:
- Pytest: Testing framework
- pytest-asyncio: Async test support
- pytest-cov: Coverage reporting

**Versioning**:
- Commitizen: Conventional commits
- Git Flow: Branching strategy
- SemVer: Semantic versioning

### External Integrations

**Azure DevOps**
- REST API v7.1
- Authentication
- Project management
- Work item tracking

---

## Design Patterns

### 1. Layered Architecture

**Presentation Layer** (Routers)
- HTTP request/response handling
- Route definitions
- Request validation
- Response formatting

**Business Layer** (Services)
- Business logic
- External API integration
- Data transformation
- Complex operations

**Data Access Layer** (Repositories)
- Database operations
- Query building
- Transaction management
- ORM interaction

**Data Layer** (Models)
- Database schema definition
- Relationships
- Constraints
- Indexes

### 2. Dependency Injection

FastAPI's dependency injection system used for:
- Database session management
- User authentication
- Configuration access
- Service instantiation

```python
@router.get("/atividades")
def list_activities(
    db: Session = Depends(get_db),
    user: AzureDevOpsUser = Depends(get_current_user)
):
    # Database and user injected automatically
    pass
```

### 3. Repository Pattern

Abstracts data access logic:
```python
class AtividadeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, skip: int, limit: int):
        # Data access implementation
        pass
```

### 4. Schema Pattern (DTO)

Separate models for different purposes:
- `AtividadeCreate`: Input validation
- `AtividadeUpdate`: Partial updates
- `AtividadeResponse`: Output serialization
- `AtividadeListResponse`: List responses

### 5. Factory Pattern

Settings factory with caching:
```python
@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### 6. Middleware Pattern

Cross-cutting concerns:
- CORS handling
- Error handling
- Request logging
- Authentication

---

## Scalability Considerations

### Current Limitations

1. **Single Instance**: One API container
2. **Vertical Scaling Only**: More resources to single container
3. **No Load Balancing**: Single Nginx instance
4. **No Caching Layer**: Direct database queries
5. **No Message Queue**: Synchronous processing

### Horizontal Scaling Path

**Phase 1: Multiple API Instances**
```yaml
services:
  api:
    deploy:
      replicas: 3
```

Nginx upstream configuration:
```nginx
upstream api_backend {
    server api:8000;
    server api_2:8000;
    server api_3:8000;
}
```

**Phase 2: Add Redis Cache**
- Cache database queries
- Session storage
- Rate limiting coordination
- Pub/Sub for real-time updates

**Phase 3: Add Message Queue**
- RabbitMQ or Redis Queue
- Async job processing
- Background tasks
- Email notifications

**Phase 4: Database Scaling**
- Read replicas
- Connection pooling (PgBouncer)
- Query optimization
- Partitioning

### Performance Optimization

**Current Optimizations**:
- Nginx connection pooling (keepalive 32)
- Gzip compression
- CloudFlare edge caching
- Database indexes
- Pydantic validation caching

**Future Optimizations**:
- Redis caching layer
- Query result caching
- Database query optimization
- Connection pool tuning
- API response compression
- Static asset CDN

### Monitoring Requirements

**Metrics to Track**:
- Request rate (req/s)
- Response time (p50, p95, p99)
- Error rate (%)
- Database connections
- Memory usage
- CPU usage
- Disk I/O

**Alerting Thresholds**:
- Response time > 1s
- Error rate > 1%
- CPU usage > 80%
- Memory usage > 90%
- Disk usage > 85%

---

## Monitoring and Observability

### Current Health Checks

**Application Level**:
```
GET /health
GET /healthz
GET /

Response: {
  "status": "healthy",
  "version": "0.1.0",
  "environment": "production"
}
```

**Container Level**:
- PostgreSQL: `pg_isready` every 10s
- FastAPI: HTTP GET /health every 30s
- Nginx: `nginx -t` every 30s

### Logging

**Application Logs**:
- Startup information
- Request logs
- Error logs
- Authentication attempts
- Database queries (debug mode)

**Container Logs**:
```bash
docker compose logs -f api
docker compose logs -f nginx
docker compose logs -f postgres
```

### Future Monitoring Stack

**Planned Implementation**:

1. **Prometheus**: Metrics collection
   - Request metrics
   - Response time histograms
   - Error counters
   - Database metrics

2. **Grafana**: Visualization
   - Real-time dashboards
   - Historical analysis
   - Alerting

3. **Loki**: Log aggregation
   - Centralized logging
   - Log search and filtering
   - Correlation with metrics

4. **Alertmanager**: Alert routing
   - Email notifications
   - Slack integration
   - PagerDuty integration

### Observability Best Practices

1. **Structured Logging**: JSON format logs
2. **Correlation IDs**: Track requests across services
3. **Trace Context**: Distributed tracing
4. **Error Tracking**: Sentry integration
5. **Performance Profiling**: Query analysis

---

## Conclusion

The API Aponta architecture provides a solid foundation for a production REST API with:

- **Security**: Multi-layer protection with CloudFlare, Nginx, and application-level security
- **Performance**: Optimized with caching, compression, and connection pooling
- **Reliability**: Health checks, automatic restarts, and graceful degradation
- **Maintainability**: Clean architecture, type safety, and comprehensive documentation
- **Scalability**: Container-based deployment ready for horizontal scaling

The architecture follows industry best practices and is designed for evolution as the application grows.

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [CloudFlare Documentation](https://developers.cloudflare.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Azure DevOps REST API](https://docs.microsoft.com/en-us/rest/api/azure/devops/)

---

**Document Maintenance**:
- Update this document when architecture changes
- Review quarterly for accuracy
- Version control in Git
- Link from main README.md

**Last Review**: 2026-01-12
**Next Review**: 2026-04-12
