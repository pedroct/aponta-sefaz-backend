# Seguranca

## Camadas
- CloudFlare (TLS, WAF e rate limiting)
- Nginx (proxy, rate limiting e headers)
- FastAPI (auth e validacao)

## Autenticacao
- Tokens do Azure DevOps (PAT ou Bearer)
- Bypass controlado por `AUTH_ENABLED` em dev

## Secrets
- Credenciais via `.env` (nao versionar)
- Evitar tokens em arquivos de config no repo

## Boas praticas
- TLS end-to-end (Full Strict)
- Logs de requests e erros
- Health checks para observabilidade basica

## Referencias
- `SECURITY.md`
- `README.md`
- `ARCHITECTURE.md`
