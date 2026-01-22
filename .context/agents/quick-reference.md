---
type: agent-guide
name: quick-reference
description: Fast reference for AI agents working on Sistema Aponta
category: meta
created: 2026-01-22
status: active
---

# AI Agent Quick Reference - Sistema Aponta

## 🎯 Start Here

**Before any work**, read these in order:
1. [.context/docs/README.md](./../docs/README.md) - Navigation hub
2. [.context/docs/project-overview.md](./../docs/project-overview.md) - What is this project?
3. [.context/docs/architecture.md](./../docs/architecture.md) - How is it structured?

## 📁 Repository Paths

**Backend (this repo)**:
- Local Dev: `\\wsl.localhost\Ubuntu-24.04\home\pedroctdev\apps\api-aponta-vps`
- VPS Staging: `/home/ubuntu/aponta-sefaz/staging/backend`
- VPS Production: `/home/ubuntu/aponta-sefaz/production/backend`

**Frontend (separate repo)**:
- Local Dev: `C:\Projetos\Azure\fe-aponta`
- VPS Staging: `/home/ubuntu/aponta-sefaz/staging/frontend`
- VPS Production: `/home/ubuntu/aponta-sefaz/production/frontend`
- GitHub: https://github.com/pedroct/aponta-sefaz-frontend

## 🔑 Critical Rules

### Authentication
- ✅ **App Token JWT**: ONLY for user identification
- ✅ **Backend PAT**: For ALL Azure DevOps API calls
- ❌ **NEVER** use frontend token to call Azure API directly

### Testing
- ✅ **ALWAYS** run `npm run type-check` locally BEFORE pushing (frontend)
- ✅ **ALWAYS** run `pytest` locally BEFORE pushing (backend)
- ❌ **NEVER** push without local validation

### Deployment
- ✅ GitHub Actions auto-deploys `develop` branch to staging
- ✅ GitHub Actions auto-deploys `main` branch to production
- ✅ Manual rebuild via SSH: `docker compose up -d --build --force-recreate --no-deps {service}`

## 🏗️ Architecture Quick Map

```
Frontend (React) → Backend (FastAPI) → Azure DevOps API
                          ↓
                     PostgreSQL
```

**Layers**:
1. `app/routers/` - HTTP endpoints
2. `app/services/` - Business logic
3. `app/repositories/` - Data access
4. `app/models/` - SQLAlchemy ORM
5. `app/schemas/` - Pydantic validation

## 📚 Common Tasks

### Add New Backend Endpoint

1. Create Pydantic schemas in `app/schemas/`
2. Add endpoint in appropriate router `app/routers/`
3. Implement logic in `app/services/`
4. Add repository method if DB access needed `app/repositories/`
5. Test locally with pytest
6. Commit and push to `develop` for staging deploy

### Add New Frontend Feature

1. Create types in `client/src/lib/*-types.ts`
2. Create React Query hooks in `client/src/hooks/use-*.ts`
3. Create/modify components in `client/src/components/`
4. Add CSS in `client/src/styles/`
5. Run `npm run type-check` locally
6. Commit and push to `develop` for staging deploy

### Database Migration

1. Modify models in `app/models/`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review generated file in `alembic/versions/`
4. Test locally: `alembic upgrade head`
5. Commit migration file
6. Deploy triggers automatic migration on VPS

## 🐛 Debugging

### Check Backend Logs
```bash
ssh root@92.112.178.252
docker logs api-aponta-staging --tail 100 --follow
```

### Check Frontend Logs
```bash
ssh root@92.112.178.252
docker logs fe-aponta-staging --tail 100 --follow
```

### Check Container Status
```bash
ssh root@92.112.178.252
docker ps --filter name=aponta
```

### Test API Directly
```bash
curl -H "Authorization: Bearer {jwt_token}" \
  https://staging-aponta.treit.com.br/api/v1/health
```

## 📖 Latest Features

### Blue Cells (2026-01-22)
- **Status**: Backend deployed, frontend logic created, UI integration pending
- **Docs**: [.context/docs/features/blue-cells.md](./../docs/features/blue-cells.md)
- **Backend**: 2 new endpoints in `/api/v1/timesheet/`
- **Frontend**: 3 new files (logic, hooks, CSS)
- **Next Steps**: Integrate into React components

## 🔗 External Services

| Service | Purpose | Auth Method |
|---------|---------|-------------|
| Azure DevOps API | Work Items, Projects, Users | PAT (backend) |
| PostgreSQL | Data persistence | Username/Password |
| GitHub | Source control & CI/CD | Deploy key |

## 📝 Documentation Standards

When creating/updating docs:
- Use frontmatter with `type`, `name`, `description`, `category`
- Add creation date and status
- Link to related documents
- Include code examples for technical docs
- Update `.context/docs/README.md` index

## 🚀 Deploy Checklist

Before any deploy:
- [ ] Local tests pass
- [ ] Type checking passes (frontend)
- [ ] No console errors locally
- [ ] Commit message follows Conventional Commits
- [ ] Updated relevant documentation
- [ ] Tested in staging after deploy
- [ ] Verified logs show no errors

## 📞 Contacts & Resources

- **VPS IP**: 92.112.178.252
- **Staging URL**: https://staging-aponta.treit.com.br
- **Production URL**: https://aponta.treit.com.br
- **Azure DevOps Org**: SEFAZ Ceará
- **Database**: PostgreSQL 15 (Docker)

## 🆘 Emergency Commands

**Restart staging backend**:
```bash
ssh root@92.112.178.252 "cd /home/ubuntu/aponta-sefaz/staging/backend && docker compose restart api"
```

**Restart staging frontend**:
```bash
ssh root@92.112.178.252 "cd /home/ubuntu/aponta-sefaz/staging/frontend && docker compose restart frontend"
```

**Check database connection**:
```bash
ssh root@92.112.178.252 "docker exec postgres-aponta psql -U postgres -c '\l'"
```

## 📚 Further Reading

- [Changelog](./../docs/changelog.md) - Recent changes
- [Data Flow](./../docs/data-flow.md) - How data moves
- [Security](./../docs/security.md) - Auth details
- [Testing Strategy](./../docs/testing-strategy.md) - How to test
