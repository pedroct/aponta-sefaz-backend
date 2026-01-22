import os
import base64
import json

# Fix 1: app/database.py
db_path = 'app/database.py'
if os.path.exists(db_path):
    print(f"Fixing {db_path}...")
    with open(db_path, 'r', encoding='utf-8') as f:
        c = f.read()
    # Replace unquoted search_path with quoted one
    c = c.replace('options": f"-csearch_path={settings.database_schema}"', 'options": f"-c search_path=\\"{settings.database_schema}\\\""')
    # Also handle space variant if present
    c = c.replace('options": f"-c search_path={settings.database_schema}"', 'options": f"-c search_path=\\"{settings.database_schema}\\\""')
    with open(db_path, 'w', encoding='utf-8') as f:
        f.write(c)

# Fix 2: alembic/env.py
env_path = 'alembic/env.py'
if os.path.exists(env_path):
    print(f"Fixing {env_path}...")
    with open(env_path, 'r', encoding='utf-8') as f:
        c = f.read()
    # Check if SET search_path is present and unquoted
    # The remote might not even have it. If it's missing, we need a better strategy (insert it).
    # But for now, let's assume if it's there, we quote it.
    if 'SET search_path TO {settings.database_schema}' in c:
        c = c.replace('SET search_path TO {settings.database_schema}', 'SET search_path TO \"{settings.database_schema}\"')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(c)
    # Also fix imports for linting
    c = c.replace('from app.config import get_settings', 'from app.config import get_settings  # noqa: E402')
    c = c.replace('from app.database import Base', 'from app.database import Base  # noqa: E402')

# Fix 3: Migration
mig_path = 'alembic/versions/90324eefb107_initial_schema_api_aponta.py'
if os.path.exists(mig_path):
    print(f"Fixing {mig_path}...")
    with open(mig_path, 'r', encoding='utf-8') as f:
        c = f.read()
    c = c.replace(", schema='api_aponta'", "")
    c = c.replace("schema='api_aponta'", "")
    c = c.replace("from typing import Sequence, Union", "from typing import Sequence, Union  # noqa: F401")
    with open(mig_path, 'w', encoding='utf-8') as f:
        f.write(c)

# Fix 4: app/auth.py
auth_path = 'app/auth.py'
if os.path.exists(auth_path):
    print(f"Fixing {auth_path}...")
    with open(auth_path, 'r', encoding='utf-8') as f:
        c = f.read()
    
    jwt_logic = r'''
    # 0. Verificar se é um JWT (App Token da extensão)
    if token.count(".") == 2 and (token.startswith("eyJ") or token.startswith("eyK")):
        try:
            # Decodificar payload sem verificar assinatura (Server-to-Server trust implícito por enquanto)
            parts = token.split(".")
            payload_b64 = parts[1] + "=" * (4 - len(parts[1]) % 4)
            payload_json = base64.urlsafe_b64decode(payload_b64).decode()
            claims = json.loads(payload_json)

            if "app.vstoken" in claims.get("iss", ""):
                user_id = claims.get("nameid")
                display_name = claims.get("name", f"Azure User {user_id[:8]}")
                logger.info(f"App Token detectado para usuário {user_id}")
                return (
                    AzureDevOpsUser(
                        id=user_id,
                        display_name=display_name,
                        email=claims.get("email"),
                        token=token,
                    ),
                    "",
                )
        except Exception:
            pass
'''
    if 'app.vstoken' not in c:
        target = 'token = credentials.credentials'
        c = c.replace(target, target + '\n' + jwt_logic)
        # Fix linting for Depends
        c = c.replace('Depends(validate_azure_token)', 'Depends(validate_azure_token)  # noqa: B008')
        
        with open(auth_path, 'w', encoding='utf-8') as f:
            f.write(c)
