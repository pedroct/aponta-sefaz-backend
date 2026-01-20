# API Documentation

**API Aponta - Complete REST API Reference**

Version: 0.1.0
Base URL: `https://api-aponta.pedroct.com.br`
Last Updated: 2026-01-18

---

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Base URL and Endpoints](#base-url-and-endpoints)
- [Common Response Codes](#common-response-codes)
- [Rate Limiting](#rate-limiting)
- [Pagination](#pagination)
- [Health Endpoints](#health-endpoints)
- [Atividades Endpoints](#atividades-endpoints)
- [Projetos Endpoints](#projetos-endpoints)
- [Integração Endpoints](#integração-endpoints)
- [Apontamentos Endpoints](#apontamentos-endpoints)
- [Work Items Endpoints](#work-items-endpoints)
- [User Endpoints](#user-endpoints)
- [Error Handling](#error-handling)
- [Interactive Documentation](#interactive-documentation)
- [SDK and Code Examples](#sdk-and-code-examples)

---

## Overview

API Aponta is a RESTful API for managing activities and projects with Azure DevOps integration. The API follows REST principles, uses JSON for request/response bodies, and provides comprehensive error messages.

### Key Features

- RESTful design with predictable endpoints
- JSON request and response bodies
- Token-based authentication
- Comprehensive error messages
- Automatic OpenAPI documentation
- CORS support for web applications
- Timesheet (apontamentos) management with Azure DevOps sync
- Work items search (ID/title)
- Authenticated user profile endpoint
- Rate limiting for abuse prevention
- Health monitoring endpoints

### API Characteristics

- **Protocol**: HTTPS only
- **Format**: JSON (application/json)
- **Authentication**: Bearer token (Azure DevOps PAT)
- **Versioning**: URI versioning (/api/v1)
- **Character Encoding**: UTF-8
- **Timezone**: All timestamps in UTC (ISO 8601 format)

---

## Authentication

### Overview

All API endpoints (except health checks) require authentication using Azure DevOps Personal Access Tokens (PAT) or Bearer tokens from the Azure DevOps Extension SDK.

### Authentication Methods

#### 1. Personal Access Token (PAT)

Used for server-to-server communication and development.

**Header Format**:
```http
Authorization: Bearer YOUR_AZURE_DEVOPS_PAT
```

**Example**:
```bash
curl -H "Authorization: Bearer abcdef123456..." \
  https://api-aponta.pedroct.com.br/api/v1/atividades
```

#### 2. Azure DevOps Extension Token

Used by Azure DevOps extensions using the SDK.

**Header Format**:
```http
Authorization: Bearer EXTENSION_SDK_TOKEN
```

### Creating a Personal Access Token

1. Go to Azure DevOps: https://dev.azure.com/{your-organization}
2. Click on User Settings > Personal Access Tokens
3. Click "New Token"
4. Configure:
   - **Name**: API Aponta Access
   - **Organization**: Your organization
   - **Expiration**: Custom (recommended: 90 days)
   - **Scopes**:
     - Project and Team: Read
     - Work Items: Read, Write
5. Click "Create" and copy the token immediately

### Token Validation

The API validates tokens by:
1. Extracting the token from the Authorization header
2. Making a request to Azure DevOps API to validate
3. Retrieving user profile information
4. Caching user context for the request

**Validated User Information**:
- User ID (Azure DevOps GUID)
- Display Name
- Email (if available)
- Organization membership

### Development Mode

For local development, authentication can be disabled:

```bash
# .env file
AUTH_ENABLED=false
```

In this mode, a mock user is returned for all requests.

### Authentication Errors

**401 Unauthorized** - Missing or invalid token
```json
{
  "detail": "Token de autenticação não fornecido"
}
```

**401 Unauthorized** - Expired token
```json
{
  "detail": "Token inválido ou expirado. Detalhes: Status 401: ..."
}
```

**401 Unauthorized** - Token without required scopes
```json
{
  "detail": "Token não possui permissões necessárias"
}
```

---

## Base URL and Endpoints

### Production

```
Base URL: https://api-aponta.pedroct.com.br
API Version: v1
Full Base: https://api-aponta.pedroct.com.br/api/v1
```

### API Structure

```
/                           # Health check
/health                     # Health check
/healthz                    # Health check
/api/v1                     # API info
/docs                       # Swagger UI (interactive)
/redoc                      # ReDoc documentation

/api/v1/atividades          # Activities resource
/api/v1/apontamentos        # Timesheets resource
/api/v1/projetos            # Projects resource
/api/v1/integracao          # Integration endpoints
/api/v1/work-items          # Work Items search
/api/v1/user                # Authenticated user
```

---

## Common Response Codes

### Success Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request succeeded, response body included |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request succeeded, no response body |

### Client Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource does not exist |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |

### Server Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 500 | Internal Server Error | Unexpected server error |
| 502 | Bad Gateway | Upstream service unavailable |
| 503 | Service Unavailable | Service temporarily unavailable |

---

## Rate Limiting

### Overview

Rate limiting is applied at multiple layers to prevent abuse and ensure fair usage.

### Limits

**Nginx Layer**:
- **Rate**: 10 requests per second per IP
- **Burst**: 20 requests (queued)
- **Scope**: Per IP address

**CloudFlare Layer**:
- **Rate**: Configurable per zone
- **Scope**: Global

### Rate Limit Headers

Response headers include rate limit information:

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1642089600
```

### Rate Limit Exceeded Response

**Status Code**: 429 Too Many Requests

```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

**Headers**:
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Reset: 1642089600
```

### Best Practices

1. **Implement exponential backoff** when receiving 429 responses
2. **Monitor rate limit headers** to avoid hitting limits
3. **Cache responses** when possible to reduce requests
4. **Use webhooks** instead of polling (when available)
5. **Request rate limit increase** if needed (contact support)

---

## Pagination

### Overview

List endpoints support pagination to limit response size and improve performance.

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| skip | integer | 0 | Number of records to skip |
| limit | integer | 100 | Maximum records to return (max: 1000) |

### Example Request

```bash
GET /api/v1/atividades?skip=0&limit=50
```

### Example Response

```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nome": "Desenvolvimento da API",
      "descricao": "Implementar endpoints REST",
      "ativo": true,
      "id_projeto": "660e8400-e29b-41d4-a716-446655440001",
      "nome_projeto": "API Aponta",
      "criado_em": "2026-01-10T10:00:00Z",
      "atualizado_em": "2026-01-10T10:00:00Z"
    }
  ],
  "total": 150
}
  **Nota**: Atividades possuem relação N:N com projetos. Use `ids_projetos` (lista) nos requests de criação/atualização. O campo `id_projeto` ainda é aceito por retrocompatibilidade. As respostas incluem `projetos` e também `id_projeto`/`nome_projeto` para compatibilidade.


```

### Response Fields

- **items**: Array of resources
- **total**: Total number of records (across all pages)

### Calculating Pages

```javascript
const totalPages = Math.ceil(response.total / limit);
const currentPage = Math.floor(skip / limit) + 1;
const hasNextPage = (skip + limit) < response.total;
```

### Navigation Example

```javascript
// First page
GET /api/v1/atividades?skip=0&limit=50

// Second page
GET /api/v1/atividades?skip=50&limit=50

// Third page
GET /api/v1/atividades?skip=100&limit=50
```

---

## Health Endpoints

### GET /

Root health check endpoint.

**Authentication**: Not required

**Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "production"
}
```

**Status Codes**:
- 200: Service is healthy

---

### GET /health

Standard health check endpoint.

**Authentication**: Not required

**Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "production"
}
```

**Status Codes**:
- 200: Service is healthy
- 503: Service is unhealthy

---

### GET /healthz

Kubernetes-style health check endpoint.

**Authentication**: Not required

**Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "environment": "production"
}
```

---

### GET /api/v1

API information endpoint.

**Authentication**: Not required

**Response**:
```json
{
  "name": "API Aponta",
  "version": "0.1.0",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

---

## Atividades Endpoints

Manage activities (atividades) in the system.

### Data Model

```typescript
interface Atividade {
  id: string;                 // UUID
  nome: string;               // 1-255 characters
  descricao: string | null;   // Optional description
  ativo: boolean;             // Active status
  projetos: { id: string; nome: string }[]; // Associated projects
  id_projeto?: string;         // UUID - Legacy project reference
  nome_projeto?: string | null; // Legacy project name
  criado_em: string;          // ISO 8601 timestamp (UTC)
  atualizado_em: string;      // ISO 8601 timestamp (UTC)
}
```

---

### GET /api/v1/atividades

List all activities with pagination and optional filters.

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| skip | integer | No | 0 | Records to skip (pagination) |
| limit | integer | No | 100 | Max records (1-1000) |
| ativo | boolean | No | - | Filter by active status |
| id_projeto | UUID | No | - | Filter by project ID |

**Example Request**:
```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api-aponta.pedroct.com.br/api/v1/atividades?skip=0&limit=50&ativo=true"
```

**Example Response** (200 OK):
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "nome": "Desenvolvimento da API",
      "descricao": "Implementar endpoints REST para gestão de atividades",
      "ativo": true,
      "projetos": [
        {
          "id": "660e8400-e29b-41d4-a716-446655440001",
          "nome": "API Aponta"
        }
      ],
      "id_projeto": "660e8400-e29b-41d4-a716-446655440001",
      "nome_projeto": "API Aponta",
      "criado_em": "2026-01-10T10:00:00.000Z",
      "atualizado_em": "2026-01-12T15:30:00.000Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "nome": "Configuração do banco de dados",
      "descricao": "Setup do PostgreSQL e migrations",
      "ativo": true,
      "projetos": [
        {
          "id": "660e8400-e29b-41d4-a716-446655440001",
          "nome": "API Aponta"
        }
      ],
      "id_projeto": "660e8400-e29b-41d4-a716-446655440001",
      "nome_projeto": "API Aponta",
      "criado_em": "2026-01-09T08:00:00.000Z",
      "atualizado_em": "2026-01-09T08:00:00.000Z"
    }
  ],
  "total": 25
}
```

**Status Codes**:
- 200: Success
- 401: Unauthorized
- 422: Invalid query parameters

---

### GET /api/v1/atividades/{id}

Get a specific activity by ID.

**Authentication**: Required

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Activity ID |

**Example Request**:
```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api-aponta.pedroct.com.br/api/v1/atividades/550e8400-e29b-41d4-a716-446655440000"
```

**Example Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "nome": "Desenvolvimento da API",
  "descricao": "Implementar endpoints REST para gestão de atividades",
  "ativo": true,
  "projetos": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "nome": "API Aponta"
    }
  ],
  "id_projeto": "660e8400-e29b-41d4-a716-446655440001",
  "nome_projeto": "API Aponta",
  "criado_em": "2026-01-10T10:00:00.000Z",
  "atualizado_em": "2026-01-12T15:30:00.000Z"
}
```

**Status Codes**:
- 200: Success
- 401: Unauthorized
- 404: Activity not found
- 422: Invalid UUID format

**Error Response** (404):
```json
{
  "detail": "Atividade com ID 550e8400-e29b-41d4-a716-446655440000 não encontrada"
}
```

---

### POST /api/v1/atividades

Create a new activity.

**Authentication**: Required

**Request Body**:
```json
{
  "nome": "Nova Atividade",
  "descricao": "Descrição detalhada da atividade",
  "ativo": true,
  "ids_projetos": ["660e8400-e29b-41d4-a716-446655440001"]
}
```

**Field Validation**:

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| nome | string | Yes | 1-255 characters |
| descricao | string | No | Any length or null |
| ativo | boolean | No | Default: true |
| ids_projetos | UUID[] | Yes | Minimum 1 project ID |
| id_projeto | UUID | No | Legacy single project ID |

**Example Request**:
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Implementar autenticação",
    "descricao": "Adicionar autenticação Azure DevOps",
    "ativo": true,
    "ids_projetos": ["660e8400-e29b-41d4-a716-446655440001"]
  }' \
  "https://api-aponta.pedroct.com.br/api/v1/atividades"
```

**Example Response** (201 Created):
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "nome": "Implementar autenticação",
  "descricao": "Adicionar autenticação Azure DevOps",
  "ativo": true,
  "projetos": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "nome": "API Aponta"
    }
  ],
  "id_projeto": "660e8400-e29b-41d4-a716-446655440001",
  "nome_projeto": "API Aponta",
  "criado_em": "2026-01-12T16:00:00.000Z",
  "atualizado_em": "2026-01-12T16:00:00.000Z"
}
```

**Status Codes**:
- 201: Created successfully
- 400: Bad request (invalid JSON)
- 401: Unauthorized
- 422: Validation error

**Validation Error Response** (422):
```json
{
  "detail": [
    {
      "loc": ["body", "nome"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "nome"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length",
      "ctx": {"limit_value": 1}
    }
  ]
}
```

---

### PUT /api/v1/atividades/{id}

Update an existing activity. All fields are optional.

**Authentication**: Required

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Activity ID |

**Request Body** (all fields optional):
```json
{
  "nome": "Nome atualizado",
  "descricao": "Nova descrição",
  "ativo": false,
  "ids_projetos": ["660e8400-e29b-41d4-a716-446655440002"]
}
```

**Example Request**:
```bash
curl -X PUT \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Implementar autenticação JWT",
    "ativo": false
  }' \
  "https://api-aponta.pedroct.com.br/api/v1/atividades/770e8400-e29b-41d4-a716-446655440003"
```

**Example Response** (200 OK):
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "nome": "Implementar autenticação JWT",
  "descricao": "Adicionar autenticação Azure DevOps",
  "ativo": false,
  "projetos": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "nome": "API Aponta"
    }
  ],
  "id_projeto": "660e8400-e29b-41d4-a716-446655440001",
  "nome_projeto": "API Aponta",
  "criado_em": "2026-01-12T16:00:00.000Z",
  "atualizado_em": "2026-01-12T16:15:00.000Z"
}
```

**Status Codes**:
- 200: Updated successfully
- 400: Bad request (invalid JSON)
- 401: Unauthorized
- 404: Activity not found
- 422: Validation error

---

### DELETE /api/v1/atividades/{id}

Delete an activity permanently.

**Authentication**: Required

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | UUID | Yes | Activity ID |

**Example Request**:
```bash
curl -X DELETE \
  -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api-aponta.pedroct.com.br/api/v1/atividades/770e8400-e29b-41d4-a716-446655440003"
```

**Example Response** (204 No Content):
```
(empty body)
```

**Status Codes**:
- 204: Deleted successfully
- 401: Unauthorized
- 404: Activity not found
- 422: Invalid UUID format

**Error Response** (404):
```json
{
  "detail": "Atividade com ID 770e8400-e29b-41d4-a716-446655440003 não encontrada"
}
```

---

## Projetos Endpoints

Manage projects and synchronization with Azure DevOps.

---

### GET /api/v1/projetos

List projects from local cache.

**Authentication**: Required

**Query Parameters**: None

**Example Request**:
```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api-aponta.pedroct.com.br/api/v1/projetos"
```

**Example Response** (200 OK):
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "external_id": "12345678-1234-1234-1234-123456789012",
    "nome": "API Aponta",
    "descricao": "Backend API for Azure DevOps extension",
    "url": "https://dev.azure.com/myorg/_apis/projects/12345678-1234-1234-1234-123456789012",
    "estado": "wellFormed",
    "last_sync_at": "2026-01-18T12:00:00.000Z",
    "created_at": "2026-01-01T00:00:00.000Z",
    "updated_at": "2026-01-18T12:00:00.000Z"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440002",
    "external_id": "87654321-4321-4321-4321-210987654321",
    "nome": "Frontend Dashboard",
    "descricao": "Web dashboard for project management",
    "url": "https://dev.azure.com/myorg/_apis/projects/87654321-4321-4321-4321-210987654321",
    "estado": "wellFormed",
    "last_sync_at": "2026-01-18T12:00:00.000Z",
    "created_at": "2025-12-15T00:00:00.000Z",
    "updated_at": "2026-01-18T12:00:00.000Z"
  }
]
```

**Status Codes**:
- 200: Success
- 401: Unauthorized

---

### POST /api/v1/integracao/sincronizar

Synchronize projects from Azure DevOps to local database.

**Authentication**: Required

**Request Body**: None

**Example Request**:
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api-aponta.pedroct.com.br/api/v1/integracao/sincronizar"
```

**Example Response** (200 OK):
```json
{
  "total_azure": 5,
  "synced": 5,
  "created": 2,
  "updated": 3
}
```

**Status Codes**:
- 200: Synchronization successful
- 401: Unauthorized
- 500: Azure DevOps API error
- 503: Service temporarily unavailable

**Error Response** (500):
```json
{
  "detail": "Erro ao sincronizar projetos do Azure DevOps: Connection timeout"
}
```

---

## Integração Endpoints

Azure DevOps integration endpoints for testing and validation.

---

### GET /api/v1/integracao/projetos

List projects directly from Azure DevOps API (not cached).

**Authentication**: Required

**Purpose**: Test Azure DevOps integration and token permissions.

**Query Parameters**: None

**Example Request**:
```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api-aponta.pedroct.com.br/api/v1/integracao/projetos"
```

**Example Response** (200 OK):
```json
{
  "count": 3,
  "value": [
    {
      "id": "12345678-1234-1234-1234-123456789012",
      "name": "API Aponta",
      "description": "Backend API for Azure DevOps extension",
      "url": "https://dev.azure.com/myorg/_apis/projects/12345678-1234-1234-1234-123456789012",
      "state": "wellFormed",
      "revision": 15,
      "visibility": "private",
      "lastUpdateTime": "2026-01-10T12:00:00.000Z"
    },
    {
      "id": "87654321-4321-4321-4321-210987654321",
      "name": "Frontend Dashboard",
      "description": "Web dashboard for project management",
      "url": "https://dev.azure.com/myorg/_apis/projects/87654321-4321-4321-4321-210987654321",
      "state": "wellFormed",
      "revision": 8,
      "visibility": "private",
      "lastUpdateTime": "2026-01-05T09:30:00.000Z"
    }
  ]
}
```

**Status Codes**:
- 200: Success
- 401: Unauthorized (invalid or expired token)
- 403: Forbidden (token lacks required permissions)
- 500: Azure DevOps API error

**Token Permission Requirements**:
- Project and Team: Read

---

## Apontamentos Endpoints

Timesheet endpoints for registering worked hours and syncing with Azure DevOps.

---

### POST /api/v1/apontamentos

Create a new apontamento (worked hours record).

**Authentication**: Required

**Request Body**:
```json
{
  "work_item_id": 12345,
  "project_id": "50a9ca09-710f-4478-8278-2d069902d2af",
  "organization_name": "my-org",
  "usuario_id": "00000000-0000-0000-0000-000000000000",
  "usuario_nome": "Pedro CT",
  "usuario_email": "pedro@example.com",
  "data_apontamento": "2026-01-18",
  "duracao": "02:30",
  "id_atividade": "770e8400-e29b-41d4-a716-446655440003",
  "comentario": "Implementação de endpoint"
}
```

**Example Response** (201 Created):
```json
{
  "id": "dd0f1133-3f54-4c6a-9b86-53b5b6a3c7f1",
  "work_item_id": 12345,
  "project_id": "50a9ca09-710f-4478-8278-2d069902d2af",
  "organization_name": "my-org",
  "data_apontamento": "2026-01-18",
  "duracao": "02:30",
  "duracao_horas": 2.5,
  "id_atividade": "770e8400-e29b-41d4-a716-446655440003",
  "atividade": {
    "id": "770e8400-e29b-41d4-a716-446655440003",
    "nome": "Desenvolvimento"
  },
  "comentario": "Implementação de endpoint",
  "usuario_id": "00000000-0000-0000-0000-000000000000",
  "usuario_nome": "Pedro CT",
  "usuario_email": "pedro@example.com",
  "criado_em": "2026-01-18T12:00:00Z",
  "atualizado_em": "2026-01-18T12:00:00Z"
}
```

---

### GET /api/v1/apontamentos/work-item/{work_item_id}

List apontamentos for a specific work item.

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| organization_name | string | Yes | Azure DevOps organization name |
| project_id | string | Yes | Azure DevOps project ID or name |
| skip | integer | No | Records to skip (default 0) |
| limit | integer | No | Max records (default 100) |

**Example Response** (200 OK):
```json
{
  "items": [
    {
      "id": "dd0f1133-3f54-4c6a-9b86-53b5b6a3c7f1",
      "work_item_id": 12345,
      "project_id": "50a9ca09-710f-4478-8278-2d069902d2af",
      "organization_name": "my-org",
      "data_apontamento": "2026-01-18",
      "duracao": "02:30",
      "duracao_horas": 2.5,
      "id_atividade": "770e8400-e29b-41d4-a716-446655440003",
      "atividade": { "id": "770e8400-e29b-41d4-a716-446655440003", "nome": "Desenvolvimento" },
      "comentario": "Implementação de endpoint",
      "usuario_id": "00000000-0000-0000-0000-000000000000",
      "usuario_nome": "Pedro CT",
      "usuario_email": "pedro@example.com",
      "criado_em": "2026-01-18T12:00:00Z",
      "atualizado_em": "2026-01-18T12:00:00Z"
    }
  ],
  "total": 1,
  "total_horas": 2.5,
  "total_formatado": "02:30"
}
```

---

### GET /api/v1/apontamentos/work-item/{work_item_id}/resumo

Returns summary totals for a specific work item.

**Query Parameters**: `organization_name`, `project_id`

---

### GET /api/v1/apontamentos/work-item/{work_item_id}/azure-info

Fetches work item time fields directly from Azure DevOps.

**Query Parameters**: `organization_name`, `project_id`

---

### GET /api/v1/apontamentos/{apontamento_id}

Get an apontamento by ID.

---

### PUT /api/v1/apontamentos/{apontamento_id}

Update an apontamento (data, duration, activity, comment).

---

### DELETE /api/v1/apontamentos/{apontamento_id}

Delete an apontamento and recalculate Azure DevOps work item time.

---

## Work Items Endpoints

Search work items in Azure DevOps.

---

### GET /api/v1/work-items/search

Search work items by ID or title.

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| query | string | Yes | Text or ID to search (min 2 chars) |
| project_id | string | No | Azure DevOps project ID or name |
| organization_name | string | No | Azure DevOps organization name |
| limit | integer | No | Max results (1-50) |

**Example Response** (200 OK):
```json
{
  "results": [
    {
      "id": 12345,
      "title": "Corrigir validação do formulário",
      "type": "Task",
      "project": "API Aponta",
      "url": "https://dev.azure.com/myorg/Project/_workitems/edit/12345",
      "originalEstimate": 8,
      "completedWork": 2,
      "remainingWork": 6,
      "state": "Active"
    }
  ],
  "count": 1
}
```

---

## User Endpoints

Authenticated user profile.

---

### GET /api/v1/user

Returns the authenticated user profile from Azure DevOps.

**Example Response** (200 OK):
```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "displayName": "Pedro CT",
  "emailAddress": "pedro@example.com",
  "avatarUrl": null
}
```

---

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

For validation errors (422), additional detail is provided:

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "error description",
      "type": "error_type",
      "ctx": {
        "additional": "context"
      }
    }
  ]
}
```

### Common Error Scenarios

#### Invalid UUID Format

**Request**:
```bash
GET /api/v1/atividades/invalid-uuid
```

**Response** (422):
```json
{
  "detail": [
    {
      "loc": ["path", "atividade_id"],
      "msg": "value is not a valid uuid",
      "type": "type_error.uuid"
    }
  ]
}
```

#### Missing Required Field

**Request**:
```json
POST /api/v1/atividades
{
  "descricao": "Missing required nome field"
}
```

**Response** (422):
```json
{
  "detail": [
    {
      "loc": ["body", "nome"],
      "msg": "field required",
      "type": "value_error.missing"
    },
    {
      "loc": ["body", "id_projeto"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### Resource Not Found

**Request**:
```bash
GET /api/v1/atividades/550e8400-e29b-41d4-a716-446655440099
```

**Response** (404):
```json
{
  "detail": "Atividade com ID 550e8400-e29b-41d4-a716-446655440099 não encontrada"
}
```

#### Rate Limit Exceeded

**Response** (429):
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

**Headers**:
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Reset: 1642089600
```

#### Server Error

**Response** (500):
```json
{
  "detail": "Internal server error. Please contact support if the problem persists."
}
```

### Error Handling Best Practices

1. **Check Status Code**: Always check the HTTP status code first
2. **Parse Error Detail**: Read the `detail` field for specific error information
3. **Handle Validation Errors**: For 422 errors, iterate through the `detail` array
4. **Implement Retry Logic**: For 429 and 5xx errors with exponential backoff
5. **Log Errors**: Keep error logs for debugging and monitoring
6. **User-Friendly Messages**: Transform technical errors into user-friendly messages

### Example Error Handling (JavaScript)

```javascript
async function fetchAtividade(id) {
  try {
    const response = await fetch(
      `https://api-aponta.pedroct.com.br/api/v1/atividades/${id}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (!response.ok) {
      const error = await response.json();

      switch (response.status) {
        case 401:
          throw new Error('Sessão expirada. Faça login novamente.');
        case 404:
          throw new Error('Atividade não encontrada.');
        case 429:
          throw new Error('Muitas requisições. Tente novamente em alguns segundos.');
        case 422:
          const messages = error.detail.map(e => e.msg).join(', ');
          throw new Error(`Erro de validação: ${messages}`);
        default:
          throw new Error(error.detail || 'Erro ao buscar atividade.');
      }
    }

    return await response.json();
  } catch (error) {
    console.error('Erro:', error);
    throw error;
  }
}
```

---

## Interactive Documentation

### Swagger UI

**URL**: https://api-aponta.pedroct.com.br/docs

Interactive documentation with:
- All endpoints and operations
- Request/response schemas
- Try it out functionality
- Authentication support
- Response examples
- Schema definitions

**Features**:
- Test API directly from browser
- Authenticate with Bearer token
- See request/response in real-time
- Download OpenAPI specification

### ReDoc

**URL**: https://api-aponta.pedroct.com.br/redoc

Clean, responsive API documentation with:
- Three-panel layout
- Search functionality
- Deep linking to sections
- Code samples
- Request/response examples

### OpenAPI Specification

**URL**: https://api-aponta.pedroct.com.br/openapi.json

Download the complete OpenAPI 3.0 specification for:
- Code generation
- API testing tools
- Documentation generation
- Contract testing

---

## SDK and Code Examples

### JavaScript/TypeScript

#### Installation

```bash
npm install axios
# or
npm install @azure/identity
```

#### Example Client

```typescript
// api-client.ts
import axios, { AxiosInstance } from 'axios';

class ApiApontaClient {
  private client: AxiosInstance;

  constructor(token: string, baseURL = 'https://api-aponta.pedroct.com.br') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
  }

  // List atividades
  async listAtividades(params?: {
    skip?: number;
    limit?: number;
    ativo?: boolean;
    id_projeto?: string;
  }) {
    const { data } = await this.client.get('/api/v1/atividades', { params });
    return data;
  }

  // Get atividade
  async getAtividade(id: string) {
    const { data } = await this.client.get(`/api/v1/atividades/${id}`);
    return data;
  }

  // Create atividade
  async createAtividade(atividade: {
    nome: string;
    descricao?: string;
    ativo?: boolean;
    id_projeto: string;
  }) {
    const { data } = await this.client.post('/api/v1/atividades', atividade);
    return data;
  }

  // Update atividade
  async updateAtividade(id: string, updates: Partial<{
    nome: string;
    descricao: string;
    ativo: boolean;
    id_projeto: string;
  }>) {
    const { data } = await this.client.put(`/api/v1/atividades/${id}`, updates);
    return data;
  }

  // Delete atividade
  async deleteAtividade(id: string) {
    await this.client.delete(`/api/v1/atividades/${id}`);
  }

  // List projetos
  async listProjetos() {
    const { data } = await this.client.get('/api/v1/projetos');
    return data;
  }

  // Sync projetos
  async syncProjetos() {
    const { data } = await this.client.post('/api/v1/integracao/sincronizar');
    return data;
  }
}

// Usage
const client = new ApiApontaClient('your-azure-devops-pat');

// List activities
const activities = await client.listAtividades({ limit: 50, ativo: true });

// Create activity
const newActivity = await client.createAtividade({
  nome: 'Nova tarefa',
  descricao: 'Descrição da tarefa',
  ativo: true,
  id_projeto: '660e8400-e29b-41d4-a716-446655440001'
});
```

### Python

#### Installation

```bash
pip install requests
```

#### Example Client

```python
# api_client.py
import requests
from typing import Optional, Dict, List
from dataclasses import dataclass

@dataclass
class Atividade:
    id: str
    nome: str
    descricao: Optional[str]
    ativo: bool
    id_projeto: str
    nome_projeto: Optional[str]
    criado_em: str
    atualizado_em: str

class ApiApontaClient:
    def __init__(self, token: str, base_url: str = "https://api-aponta.pedroct.com.br"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })

    def list_atividades(
        self,
        skip: int = 0,
        limit: int = 100,
        ativo: Optional[bool] = None,
        id_projeto: Optional[str] = None
    ) -> Dict:
        """List atividades with pagination and filters."""
        params = {"skip": skip, "limit": limit}
        if ativo is not None:
            params["ativo"] = ativo
        if id_projeto:
            params["id_projeto"] = id_projeto

        response = self.session.get(f"{self.base_url}/api/v1/atividades", params=params)
        response.raise_for_status()
        return response.json()

    def get_atividade(self, id: str) -> Dict:
        """Get a specific atividade by ID."""
        response = self.session.get(f"{self.base_url}/api/v1/atividades/{id}")
        response.raise_for_status()
        return response.json()

    def create_atividade(
        self,
        nome: str,
        id_projeto: str,
        descricao: Optional[str] = None,
        ativo: bool = True
    ) -> Dict:
        """Create a new atividade."""
        payload = {
            "nome": nome,
            "id_projeto": id_projeto,
            "descricao": descricao,
            "ativo": ativo
        }
        response = self.session.post(
            f"{self.base_url}/api/v1/atividades",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def update_atividade(self, id: str, **updates) -> Dict:
        """Update an atividade."""
        response = self.session.put(
            f"{self.base_url}/api/v1/atividades/{id}",
            json=updates
        )
        response.raise_for_status()
        return response.json()

    def delete_atividade(self, id: str) -> None:
        """Delete an atividade."""
        response = self.session.delete(f"{self.base_url}/api/v1/atividades/{id}")
        response.raise_for_status()

    def list_projetos(self) -> List[Dict]:
        """List all projetos."""
        response = self.session.get(f"{self.base_url}/api/v1/projetos")
        response.raise_for_status()
        return response.json()

    def sync_projetos(self) -> Dict:
        """Sync projetos from Azure DevOps."""
        response = self.session.post(f"{self.base_url}/api/v1/integracao/sincronizar")
        response.raise_for_status()
        return response.json()

# Usage
client = ApiApontaClient(token="your-azure-devops-pat")

# List activities
activities = client.list_atividades(limit=50, ativo=True)
print(f"Found {activities['total']} activities")

# Create activity
new_activity = client.create_atividade(
    nome="Nova tarefa",
    descricao="Descrição da tarefa",
    id_projeto="660e8400-e29b-41d4-a716-446655440001"
)
print(f"Created activity: {new_activity['id']}")
```

### cURL Examples

#### List Activities
```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api-aponta.pedroct.com.br/api/v1/atividades?skip=0&limit=50"
```

#### Create Activity
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Nova atividade",
    "descricao": "Descrição detalhada",
    "ativo": true,
    "id_projeto": "660e8400-e29b-41d4-a716-446655440001"
  }' \
  "https://api-aponta.pedroct.com.br/api/v1/atividades"
```

#### Update Activity
```bash
curl -X PUT \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Nome atualizado",
    "ativo": false
  }' \
  "https://api-aponta.pedroct.com.br/api/v1/atividades/550e8400-e29b-41d4-a716-446655440000"
```

#### Delete Activity
```bash
curl -X DELETE \
  -H "Authorization: Bearer YOUR_TOKEN" \
  "https://api-aponta.pedroct.com.br/api/v1/atividades/550e8400-e29b-41d4-a716-446655440000"
```

---

## Support and Resources

### Documentation

- **API Documentation**: This document
- **Architecture**: See [ARCHITECTURE.md](../architecture/ARCHITECTURE.md)
- **Security**: See [SECURITY.md](../security/SECURITY.md)
- **Deployment**: See [DEPLOY_INSTRUCTIONS.md](../deploy/DEPLOY_INSTRUCTIONS.md)

### Interactive Tools

- **Swagger UI**: https://api-aponta.pedroct.com.br/docs
- **ReDoc**: https://api-aponta.pedroct.com.br/redoc
- **OpenAPI Spec**: https://api-aponta.pedroct.com.br/openapi.json

### Contact

- **Email**: contato@pedroct.com.br
- **Issues**: GitHub Issues (if applicable)
- **Support**: contato@pedroct.com.br

---

## Changelog

### Version 0.1.0 (Current)

- Initial API release
- CRUD endpoints for atividades
- Azure DevOps authentication
- Project synchronization
- Health monitoring
- Rate limiting
- Pagination support

### Planned Features (v0.2.0)

- Webhook support
- Batch operations
- Advanced filtering
- Export functionality
- Real-time notifications

---

**Document Version**: 1.0
**Last Updated**: 2026-01-12
**API Version**: 0.1.0

For the latest documentation, always refer to the interactive docs at:
- https://api-aponta.pedroct.com.br/docs
- https://api-aponta.pedroct.com.br/redoc
