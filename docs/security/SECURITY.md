# Security Policy

**API Aponta VPS - Security Documentation**

Version: 0.1.0
Last Updated: 2026-01-12

---

## Table of Contents

- [Reporting Security Vulnerabilities](#reporting-security-vulnerabilities)
- [Security Architecture](#security-architecture)
- [Authentication and Authorization](#authentication-and-authorization)
- [Data Protection](#data-protection)
- [Network Security](#network-security)
- [Application Security](#application-security)
- [Infrastructure Security](#infrastructure-security)
- [Security Best Practices](#security-best-practices)
- [Compliance and Standards](#compliance-and-standards)
- [Incident Response](#incident-response)
- [Security Checklist](#security-checklist)
- [Third-Party Security](#third-party-security)

---

## Reporting Security Vulnerabilities

### Responsible Disclosure

We take the security of API Aponta seriously. If you discover a security vulnerability, we appreciate your help in disclosing it to us in a responsible manner.

### How to Report

**IMPORTANT**: Do NOT create public GitHub issues for security vulnerabilities.

**Contact Information**:
- **Primary Contact**: security@pedroct.com.br
- **Alternative Contact**: contato@pedroct.com.br
- **Response Time**: We aim to respond within 48 hours

### What to Include

When reporting a vulnerability, please include:

1. **Description**: Detailed description of the vulnerability
2. **Impact**: Potential impact and severity assessment
3. **Steps to Reproduce**: Clear steps to reproduce the issue
4. **Proof of Concept**: Code or screenshots demonstrating the vulnerability
5. **Suggested Fix**: Your recommendations for remediation (if any)
6. **Contact Information**: Your email for follow-up questions

### Security Report Template

```markdown
## Vulnerability Report

**Reporter**: Your Name <your.email@example.com>
**Date**: YYYY-MM-DD
**Severity**: [Critical / High / Medium / Low]

### Summary
Brief description of the vulnerability

### Description
Detailed explanation of the security issue

### Impact
What an attacker could accomplish by exploiting this

### Steps to Reproduce
1. Step one
2. Step two
3. Step three

### Proof of Concept
Code, screenshots, or examples

### Suggested Remediation
Your recommendations for fixing the issue

### Additional Information
Any other relevant details
```

### What to Expect

1. **Acknowledgment**: We will acknowledge receipt of your report within 48 hours
2. **Assessment**: We will assess the vulnerability and determine severity within 5 business days
3. **Updates**: We will keep you informed of our progress
4. **Resolution**: We aim to resolve critical issues within 30 days
5. **Credit**: We will credit you in our security advisories (if desired)

### Scope

**In Scope**:
- API endpoints and authentication mechanisms
- Database security issues
- Container and infrastructure vulnerabilities
- Configuration and deployment issues
- Cryptographic vulnerabilities
- Information disclosure
- Cross-site scripting (XSS)
- SQL injection
- Authentication bypass
- Authorization issues

**Out of Scope**:
- Social engineering attacks
- Physical attacks
- Denial of Service (DoS) attacks
- Issues in third-party dependencies (report to the vendor)
- Vulnerabilities requiring physical access to servers
- Issues affecting outdated browsers

### Bug Bounty Program

Currently, we do not have a formal bug bounty program. However, we deeply appreciate security researchers who help us maintain the security of API Aponta and will publicly acknowledge your contribution (if you wish).

---

## Security Architecture

### Multi-Layer Defense Strategy

API Aponta implements defense in depth with multiple security layers:

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Edge Security (CloudFlare)                         │
│ - DDoS Protection (L3, L4, L7)                              │
│ - Web Application Firewall (WAF)                            │
│ - Bot Protection                                             │
│ - Rate Limiting                                              │
│ - SSL/TLS Encryption                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Gateway Security (Nginx)                           │
│ - Reverse Proxy                                              │
│ - SSL/TLS Termination                                        │
│ - Rate Limiting (10 req/s)                                  │
│ - Request Filtering                                          │
│ - IP Whitelisting (CloudFlare IPs)                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Application Security (FastAPI)                     │
│ - Token Authentication                                       │
│ - Input Validation                                           │
│ - CORS Policy                                                │
│ - SQL Injection Prevention                                   │
│ - XSS Prevention                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Data Security (PostgreSQL)                         │
│ - User Isolation                                             │
│ - Schema Separation                                          │
│ - Encrypted Connections                                      │
│ - Prepared Statements                                        │
└─────────────────────────────────────────────────────────────┘
```

### Security Zones

**Public Zone** (CloudFlare):
- Exposed to internet
- DDoS protection active
- WAF rules enforced
- Rate limiting applied

**DMZ** (Nginx):
- Only accessible from CloudFlare IPs
- SSL/TLS enforced
- Request filtering
- Rate limiting

**Application Zone** (FastAPI):
- Internal Docker network only
- Authentication required
- Input validation
- Business logic

**Data Zone** (PostgreSQL):
- Internal Docker network only
- No external access
- Credential-based access
- Schema isolation

---

## Authentication and Authorization

### Authentication Mechanisms

#### 1. Azure DevOps Token Authentication

**Primary Method**: Personal Access Token (PAT) from Azure DevOps

**How It Works**:
1. User creates PAT in Azure DevOps with required scopes
2. PAT sent in Authorization header: `Bearer <token>`
3. API validates token with Azure DevOps API
4. User profile retrieved and cached for request
5. Subsequent requests use validated user context

**Token Validation**:
```
1. Extract token from Authorization header
2. Call Azure DevOps connectionData API
3. Verify response status is 200 OK
4. Extract user information (ID, name, email)
5. Create user context for request
```

**Required Token Scopes**:
- Project and Team: Read
- Work Items: Read, Write (for future features)

**Token Security**:
- Tokens transmitted only over HTTPS
- Tokens not logged or stored
- Tokens validated on every request
- No token caching or session storage

#### 2. Development Mode Authentication

For local development and testing only.

**Configuration**:
```bash
# .env
AUTH_ENABLED=false
```

**Behavior**:
- Returns mock user for all requests
- **NEVER** enable in production
- Only for local development

**Mock User**:
```json
{
  "id": "dev-user-001",
  "display_name": "Dev User",
  "email": "dev@localhost",
  "token": "mock-token"
}
```

### Authorization

**Current Implementation**:
- Authentication required for all API endpoints (except health checks)
- All authenticated users have full access to resources
- No role-based access control (RBAC) yet

**Planned Features** (v1.0.0):
- Role-based access control (Admin, User, ReadOnly)
- Resource-level permissions
- Project-based access control
- API key authentication for service-to-service

### Authentication Best Practices

**For API Consumers**:

1. **Secure Token Storage**:
   - Never hardcode tokens in source code
   - Use environment variables or secure vaults
   - Rotate tokens regularly (every 90 days)

2. **Token Transmission**:
   - Always use HTTPS
   - Never log tokens
   - Never send tokens in query parameters

3. **Token Scope**:
   - Use minimum required scopes
   - Create separate tokens for different applications
   - Revoke unused tokens

4. **Error Handling**:
   - Handle 401 errors gracefully
   - Prompt user to re-authenticate
   - Don't expose token details in error messages

**Example (Good)**:
```javascript
// Good: Token in environment variable
const token = process.env.AZURE_DEVOPS_PAT;
const headers = {
  'Authorization': `Bearer ${token}`
};
```

**Example (Bad)**:
```javascript
// BAD: Hardcoded token
const token = 'abcdef123456...';  // NEVER DO THIS

// BAD: Token in URL
fetch(`https://api.example.com/data?token=${token}`);  // NEVER DO THIS
```

---

## Data Protection

### Data Classification

**Public Data**:
- API documentation
- Health check responses
- API version information

**Internal Data**:
- Activity names and descriptions
- Project information
- Timestamps
- User display names

**Confidential Data**:
- Authentication tokens
- User emails
- Azure DevOps organization details
- Database credentials

**Restricted Data**:
- None currently stored

### Encryption

#### Data in Transit

**External (Client to CloudFlare)**:
- Protocol: TLS 1.2 / TLS 1.3
- Cipher Suites: Strong ciphers only (ECDHE, AES-GCM)
- Certificate: CloudFlare-managed certificate
- HTTPS enforced (HSTS enabled)

**Origin (CloudFlare to VPS)**:
- Protocol: TLS 1.2 / TLS 1.3
- Certificate: CloudFlare Origin Certificate (15-year validity)
- Mutual authentication: CloudFlare IPs whitelisted

**Internal (VPS)**:
- Protocol: HTTP (Docker internal network)
- Network: Isolated bridge network
- Access: Container-to-container only

**Configuration**:
```nginx
# nginx.conf
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:
            ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
```

#### Data at Rest

**Database**:
- Storage: Docker volume (postgres_data)
- Encryption: Host filesystem encryption recommended
- Backups: Should be encrypted before offsite storage

**Secrets**:
- Storage: Environment variables in .env file
- File permissions: 600 (read/write owner only)
- Version control: .env excluded via .gitignore

**Logs**:
- Location: Docker container logs
- Sensitive data: Filtered (tokens, passwords not logged)
- Retention: Manual cleanup required

### Data Minimization

**Principles**:
- Collect only necessary data
- Don't store authentication tokens
- Minimize personal information
- Regular data cleanup

**Implementation**:
- User email stored only if provided by Azure DevOps
- No session data stored
- No usage tracking or analytics
- Authentication tokens not persisted

### Data Retention

**Activity Data**:
- Retention: Indefinite (user manages via API)
- Deletion: Permanent when deleted via API
- Backups: Follow backup retention policy

**Logs**:
- Application logs: Docker container lifetime
- Nginx logs: Docker container lifetime
- Database logs: PostgreSQL container lifetime

**Recommendations**:
- Implement log rotation
- Automated backup cleanup
- Regular data audits

---

## Network Security

### Network Segmentation

**Public Network** (Internet):
- Exposed: CloudFlare edge network only
- Access: HTTPS traffic only
- Protection: DDoS, WAF, rate limiting

**Host Network** (VPS):
- Exposed Ports: 80 (HTTP), 443 (HTTPS), 5432 (PostgreSQL)
- Firewall: Host firewall recommended
- Access: Limited to CloudFlare IPs (Nginx) and management IPs (SSH, PostgreSQL)

**Docker Network** (aponta-network):
- Type: Bridge network
- Isolation: Containers isolated from host network
- Communication: Container-to-container only
- DNS: Docker internal DNS

### Firewall Configuration

**Recommended VPS Firewall Rules** (UFW):

```bash
# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH (from management IPs only)
sudo ufw allow from MANAGEMENT_IP to any port 22

# HTTP/HTTPS (from CloudFlare IPs only)
sudo ufw allow from 173.245.48.0/20 to any port 80
sudo ufw allow from 173.245.48.0/20 to any port 443
# ... (add all CloudFlare IP ranges)

# PostgreSQL (from management IPs only, if remote access needed)
sudo ufw allow from MANAGEMENT_IP to any port 5432

# Enable firewall
sudo ufw enable
```

**CloudFlare IP Ranges** (Update regularly):
- IPv4: https://www.cloudflare.com/ips-v4
- IPv6: https://www.cloudflare.com/ips-v6

### Port Security

**Exposed Ports**:

| Port | Service | Access | Purpose |
|------|---------|--------|---------|
| 22 | SSH | Management IPs only | Server administration |
| 80 | HTTP | CloudFlare IPs only | HTTP traffic (redirects to HTTPS) |
| 443 | HTTPS | CloudFlare IPs only | HTTPS traffic |
| 5432 | PostgreSQL | Management IPs only | Database administration |

**Internal Ports** (Docker network only):

| Port | Service | Container | Access |
|------|---------|-----------|--------|
| 8000 | FastAPI | api | From nginx only |
| 5432 | PostgreSQL | postgres | From api only |

### DDoS Protection

**CloudFlare Protection**:
- Layer 3/4 DDoS mitigation
- Layer 7 DDoS mitigation
- Automatic attack detection
- Traffic filtering
- Challenge pages for suspicious traffic

**Application-Level Protection**:
- Rate limiting: 10 req/s per IP (Nginx)
- Connection limits: 1024 concurrent (Nginx)
- Timeout protection: 60s read timeout
- Request size limits: Default Nginx limits

### IP Whitelisting

**CloudFlare Real IP Configuration**:

Nginx extracts real client IP from CloudFlare headers:

```nginx
# CloudFlare IP ranges
set_real_ip_from 173.245.48.0/20;
set_real_ip_from 103.21.244.0/22;
# ... (all CloudFlare ranges)
real_ip_header CF-Connecting-IP;
```

**Purpose**:
- Accurate rate limiting per client IP
- Correct access logs
- Prevent IP spoofing

---

## Application Security

### Input Validation

**Pydantic Schema Validation**:

All API inputs validated using Pydantic models:

```python
class AtividadeCreate(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    descricao: str | None = Field(default=None)
    ativo: bool = Field(default=True)
    id_projeto: UUID  # UUID validation automatic
```

**Validation Checks**:
- Type validation (string, integer, boolean, UUID)
- Length constraints (min/max)
- Format validation (UUID, email, URL)
- Required vs optional fields
- Custom validators

**Benefits**:
- Automatic 422 validation errors
- Type safety throughout application
- Self-documenting API
- Prevents injection attacks

### SQL Injection Prevention

**SQLAlchemy ORM**:

All database queries use SQLAlchemy ORM with parameterized queries:

```python
# Safe: Parameterized query
atividade = db.query(Atividade).filter(
    Atividade.id == atividade_id
).first()

# Safe: ORM methods prevent injection
db.add(atividade)
db.commit()
```

**Never Used**:
```python
# DANGEROUS: Never do raw SQL with string formatting
query = f"SELECT * FROM atividades WHERE id = '{user_input}'"  # NEVER!
```

**Protection Mechanisms**:
- Prepared statements
- Parameter binding
- ORM abstraction
- Type checking

### Cross-Site Scripting (XSS) Prevention

**API Protection**:
- JSON responses (not HTML)
- Content-Type: application/json
- No user-provided HTML rendering
- Automatic JSON escaping

**Client Responsibility**:
- Sanitize data before rendering in HTML
- Use framework escaping (React, Angular, Vue)
- Implement Content Security Policy (CSP)

### Cross-Origin Resource Sharing (CORS)

**Configuration**:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Configurable
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production Settings**:
```bash
# .env
CORS_ORIGINS=https://api-aponta.pedroct.com.br,https://*.dev.azure.com
```

**Security Considerations**:
- Whitelist specific origins (never use "*" in production)
- Include Azure DevOps origins for extension
- Test CORS headers in browser console
- Update origins as needed

### Cross-Site Request Forgery (CSRF) Protection

**Current Status**: Not implemented (API only, no cookies)

**Why Not Required**:
- Token-based authentication (not cookie-based)
- No session cookies
- No state-changing GET requests
- CORS origin validation

**Future Considerations**:
- If implementing cookie authentication, add CSRF protection
- If adding web UI, implement CSRF tokens

### Security Headers

**Nginx Security Headers** (Recommended):

```nginx
# Add to nginx.conf
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

**Content Security Policy** (Future):
```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self';" always;
```

### Dependency Security

**Current Dependencies**:
- FastAPI 0.109.0
- SQLAlchemy 2.0.25
- Pydantic 2.5.3
- PostgreSQL 15
- Nginx Alpine
- Python 3.12

**Security Practices**:
1. **Regular Updates**: Update dependencies quarterly or when security advisories released
2. **Vulnerability Scanning**: Use `pip-audit` or `safety` to scan for known vulnerabilities
3. **Minimal Dependencies**: Only include necessary packages
4. **Pinned Versions**: Use exact versions in requirements.txt

**Scanning Commands**:
```bash
# Install security scanners
pip install pip-audit safety

# Scan for vulnerabilities
pip-audit
safety check

# Check for outdated packages
pip list --outdated
```

**Update Process**:
1. Review CHANGELOG for breaking changes
2. Update in development environment
3. Run tests
4. Deploy to staging
5. Monitor for issues
6. Deploy to production

---

## Infrastructure Security

### Container Security

**Multi-Stage Builds**:

Dockerfile uses multi-stage build to minimize attack surface:

```dockerfile
# Stage 1: Builder (includes build tools)
FROM python:3.12-slim as builder
# Build dependencies...

# Stage 2: Production (minimal image)
FROM python:3.12-slim
# Only runtime dependencies
# No build tools, compilers, etc.
```

**Non-Root User**:

Application runs as non-privileged user:

```dockerfile
# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Switch to non-root user
USER appuser
```

**Benefits**:
- Limited privilege escalation
- Filesystem restrictions
- Process isolation

**Image Security**:
- Alpine-based images (minimal)
- Official images only (postgres, nginx, python)
- Regular image updates
- No unnecessary packages

**Container Scanning**:
```bash
# Scan for vulnerabilities
docker scan api-aponta:latest
trivy image api-aponta:latest
```

### Docker Security Best Practices

**Implemented**:
- Non-root users in containers
- Read-only root filesystem (where possible)
- No privileged containers
- Resource limits (via Docker Compose)
- Network isolation (bridge network)
- Secret management (environment variables)

**Configuration**:
```yaml
# docker-compose.yml
services:
  api:
    read_only: false  # Application needs write access for logs
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # If needed
```

### Secrets Management

**Current Approach**: Environment variables in .env file

**Security Measures**:
1. **File Permissions**: Set to 600 (owner read/write only)
   ```bash
   chmod 600 .env
   ```

2. **Version Control**: Excluded via .gitignore
   ```bash
   # .gitignore
   .env
   .env.*
   !.env.example
   ```

3. **Documentation**: Example file without secrets
   ```bash
   cp .env.example .env
   # Edit .env with actual values
   ```

4. **Access Control**: Restrict SSH access to VPS

**Future Improvements**:
- Docker secrets
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault

**Secret Rotation**:
- Database passwords: Quarterly or on suspected compromise
- Azure DevOps PATs: Every 90 days (Azure DevOps policy)
- SSL certificates: Automatic via CloudFlare

### VPS Hardening

**Recommended Security Measures**:

1. **SSH Security**:
   ```bash
   # /etc/ssh/sshd_config
   PermitRootLogin no
   PasswordAuthentication no
   PubkeyAuthentication yes
   AllowUsers your-user
   ```

2. **Firewall** (UFW):
   ```bash
   sudo ufw enable
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   ```

3. **Automatic Updates**:
   ```bash
   # Ubuntu/Debian
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure --priority=low unattended-upgrades
   ```

4. **Fail2Ban**:
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   sudo systemctl start fail2ban
   ```

5. **Log Monitoring**:
   ```bash
   # Monitor auth logs
   sudo tail -f /var/log/auth.log

   # Monitor Docker logs
   docker compose logs -f
   ```

6. **Regular Backups**:
   ```bash
   # Database backup
   docker exec postgres-aponta pg_dump -U api-aponta-user gestao_projetos > backup.sql

   # Encrypt backup
   gpg -c backup.sql

   # Transfer offsite
   scp backup.sql.gpg user@backup-server:/backups/
   ```

---

## Security Best Practices

### For Developers

1. **Code Reviews**:
   - Review all code changes for security issues
   - Check for hardcoded secrets
   - Validate input handling
   - Review authentication logic

2. **Testing**:
   - Test authentication/authorization
   - Fuzz test inputs
   - Test error handling
   - Security regression tests

3. **Documentation**:
   - Document security assumptions
   - Update SECURITY.md with changes
   - Maintain threat model

4. **Dependencies**:
   - Audit dependencies quarterly
   - Monitor security advisories
   - Update promptly
   - Use minimal dependencies

### For Operations

1. **Access Control**:
   - Use SSH keys (no passwords)
   - Implement principle of least privilege
   - Regular access audits
   - Revoke unused access

2. **Monitoring**:
   - Monitor logs for suspicious activity
   - Set up alerts for failures
   - Track authentication attempts
   - Monitor resource usage

3. **Backups**:
   - Daily automated backups
   - Test restore procedures
   - Encrypt backups
   - Offsite storage

4. **Updates**:
   - Apply security patches promptly
   - Test updates in staging
   - Schedule maintenance windows
   - Maintain rollback plan

### For API Consumers

1. **Token Security**:
   - Store tokens securely (environment variables, vaults)
   - Never commit tokens to git
   - Rotate tokens regularly
   - Use minimum required scopes

2. **Error Handling**:
   - Don't expose sensitive data in errors
   - Log errors securely
   - Handle authentication failures gracefully
   - Implement retry logic

3. **Rate Limiting**:
   - Respect rate limits
   - Implement exponential backoff
   - Cache responses when possible
   - Monitor rate limit headers

4. **HTTPS**:
   - Always use HTTPS
   - Validate SSL certificates
   - Don't disable certificate validation
   - Pin certificates if possible

---

## Compliance and Standards

### Standards Followed

**OWASP Top 10** (2021):
- A01: Broken Access Control - Addressed via authentication
- A02: Cryptographic Failures - TLS encryption, secure storage
- A03: Injection - Prevented via ORM, input validation
- A04: Insecure Design - Threat modeling, secure architecture
- A05: Security Misconfiguration - Secure defaults, hardening
- A06: Vulnerable Components - Dependency management
- A07: Authentication Failures - Token validation, Azure DevOps integration
- A08: Software and Data Integrity - Signed commits, dependency pinning
- A09: Security Logging - Comprehensive logging (planned)
- A10: Server-Side Request Forgery - Input validation, URL validation

**Security Standards**:
- HTTPS/TLS 1.2+ only
- Strong cipher suites
- Rate limiting
- Input validation
- Least privilege principle
- Defense in depth
- Secure defaults

### Compliance Considerations

**GDPR** (if applicable):
- Data minimization
- Right to deletion (via API)
- Data portability (JSON exports)
- Consent management (application level)

**SOC 2** (future):
- Security logging
- Access controls
- Encryption
- Monitoring and alerting

---

## Incident Response

### Incident Response Plan

**1. Detection**:
- Monitor logs for suspicious activity
- Alert on authentication failures
- Track error rates
- Monitor resource usage

**2. Assessment**:
- Determine scope and impact
- Identify affected systems
- Assess data exposure
- Classify severity

**3. Containment**:
- Isolate affected systems
- Block malicious IPs
- Revoke compromised tokens
- Preserve evidence

**4. Eradication**:
- Remove malicious code
- Patch vulnerabilities
- Update credentials
- Harden systems

**5. Recovery**:
- Restore from backups if needed
- Verify system integrity
- Monitor for recurrence
- Resume normal operations

**6. Post-Incident**:
- Document incident
- Conduct root cause analysis
- Update security measures
- Notify affected parties

### Incident Severity Levels

**Critical**:
- Data breach
- Complete service compromise
- Massive data loss

**High**:
- Authentication bypass
- Unauthorized access
- Partial data exposure

**Medium**:
- Successful attacks with limited impact
- Vulnerable dependencies
- Configuration issues

**Low**:
- Failed attack attempts
- Minor vulnerabilities
- Security warnings

### Communication Plan

**Internal**:
1. Security team notified immediately
2. Development team alerted
3. Management informed
4. Regular status updates

**External**:
1. Affected users notified (if applicable)
2. Public disclosure (if required)
3. Security advisory published
4. Patch release announcement

---

## Security Checklist

### Pre-Deployment Security Checklist

- [ ] All dependencies updated to latest secure versions
- [ ] No hardcoded secrets in code
- [ ] .env file has proper permissions (600)
- [ ] SSL certificates valid and properly configured
- [ ] Firewall rules configured correctly
- [ ] SSH key authentication enabled (no passwords)
- [ ] Docker containers running as non-root users
- [ ] Rate limiting configured
- [ ] CORS origins properly whitelisted
- [ ] Database credentials strong and unique
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting configured
- [ ] Incident response plan documented
- [ ] Security documentation up to date

### Monthly Security Checklist

- [ ] Review access logs for suspicious activity
- [ ] Check for failed authentication attempts
- [ ] Review and rotate credentials
- [ ] Update dependencies (security patches)
- [ ] Scan containers for vulnerabilities
- [ ] Test backup restore procedure
- [ ] Review and update firewall rules
- [ ] Verify SSL certificate validity
- [ ] Check disk space and resource usage
- [ ] Review and archive old logs

### Quarterly Security Checklist

- [ ] Full security audit
- [ ] Penetration testing (if applicable)
- [ ] Dependency vulnerability scan
- [ ] Review and update security policies
- [ ] Access control audit
- [ ] Disaster recovery drill
- [ ] Security training for team
- [ ] Review incident response plan
- [ ] Update threat model
- [ ] Document changes in SECURITY.md

---

## Third-Party Security

### CloudFlare

**Security Features**:
- DDoS protection
- Web Application Firewall
- SSL/TLS management
- Bot protection
- Rate limiting

**Configuration**:
- SSL/TLS Mode: Full (Strict)
- Security Level: Medium
- Bot Fight Mode: Enabled
- Origin Certificate: Installed

### Azure DevOps

**Integration Security**:
- Token-based authentication
- Minimum required scopes
- Token expiration enforced
- Real-time validation

**Best Practices**:
- Create tokens with minimal scopes
- Set expiration (max 90 days recommended)
- Regularly rotate tokens
- Revoke unused tokens

### PostgreSQL

**Security Configuration**:
- Strong password authentication
- Network isolation (Docker network)
- No public exposure
- Regular backups

**Hardening**:
- Disable unused extensions
- Limit connection count
- Configure statement timeout
- Enable query logging (debug mode)

---

## Security Resources

### Tools

**Vulnerability Scanning**:
- `pip-audit`: Python dependency scanning
- `safety`: Python security checks
- `trivy`: Container image scanning
- `docker scan`: Docker vulnerability scanning

**Testing**:
- OWASP ZAP: Web application security scanner
- Burp Suite: Security testing
- SQLMap: SQL injection testing
- Postman: API testing

**Monitoring**:
- CloudFlare Analytics: Traffic monitoring
- Docker stats: Resource monitoring
- Nginx logs: Access and error logs
- PostgreSQL logs: Query logs

### References

- **OWASP**: https://owasp.org/
- **NIST Cybersecurity Framework**: https://www.nist.gov/cyberframework
- **CIS Docker Benchmark**: https://www.cisecurity.org/benchmark/docker
- **FastAPI Security**: https://fastapi.tiangolo.com/tutorial/security/
- **PostgreSQL Security**: https://www.postgresql.org/docs/current/security.html
- **Nginx Security**: https://nginx.org/en/docs/http/ngx_http_ssl_module.html

---

## Contact

**Security Issues**: security@pedroct.com.br
**General Support**: contato@pedroct.com.br
**Documentation**: See [ARCHITECTURE.md](../architecture/ARCHITECTURE.md) and [API_DOCUMENTATION.md](../api/API_DOCUMENTATION.md)

---

**Document Version**: 1.0
**Last Updated**: 2026-01-12
**Next Review**: 2026-04-12

This security policy is reviewed and updated quarterly or when significant changes occur to the system architecture or security landscape.
