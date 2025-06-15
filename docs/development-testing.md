# Development Testing mit curl

## JWT-Bypass für Development-Testing

Für die Entwicklung und das Testen mit curl wurde eine spezielle Umgebungsvariable `DISABLE_JWT_AUTH` implementiert.

### Aktivierung des JWT-Bypass

**WICHTIG: NUR für Development und Testing verwenden!**

```bash
# Development Environment aktivieren
export DISABLE_JWT_AUTH=true

# Backend starten
cd src/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### curl-Beispiele für API-Testing

#### 1. User Information abrufen

```bash
# Mit JWT-Bypass (Development)
curl -X GET "http://localhost:8000/api/users/me"

# Mit echtem JWT (Production)
curl -X GET "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 2. User Settings abrufen

```bash
# Alle Settings
curl -X GET "http://localhost:8000/api/users/me/settings"

# Device-spezifische Settings
curl -X GET "http://localhost:8000/api/users/me/settings?device=desktop"

# Einzelne Setting
curl -X GET "http://localhost:8000/api/users/me/settings/desktop/task_list_page_size"
```

#### 3. Projekte abrufen

```bash
# Alle Projekte
curl -X GET "http://localhost:8000/api/projects/"

# Projekte mit Pagination
curl -X GET "http://localhost:8000/api/projects/?skip=0&limit=10"

# Aktive Projekte
curl -X GET "http://localhost:8000/api/projects/active"

# Wöchentliche Projekte
curl -X GET "http://localhost:8000/api/projects/weekly"
```

#### 4. Projekt aktualisieren

```bash
curl -X PUT "http://localhost:8000/api/projects/1" \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "Updated Project Name",
    "done_status": false,
    "do_this_week": true
  }'
```

#### 5. Tasks abrufen

```bash
# Alle Tasks
curl -X GET "http://localhost:8000/api/tasks/"

# Tasks für ein Projekt
curl -X GET "http://localhost:8000/api/tasks/?project_id=1"

# Tasks mit Filter
curl -X GET "http://localhost:8000/api/tasks/?is_done=false&limit=20"
```

#### 6. Dashboard-Daten

```bash
curl -X GET "http://localhost:8000/api/dashboard/stats"
```

#### 7. Weekly Review

```bash
curl -X GET "http://localhost:8000/api/weekly-review/data"
```

### Environment-Konfiguration

#### Development (.env.development)
```bash
# Backend Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DEFAULT_USER_ID=00000000-0000-0000-0000-000000000001

# JWT Bypass für Testing
DISABLE_JWT_AUTH=true

# Backend URL
BACKEND_URL=http://localhost:8000
```

#### Production (.env.production)
```bash
# Backend Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# JWT Bypass DEAKTIVIERT (Standard)
# DISABLE_JWT_AUTH=false  # Optional, da false Standard ist

# Backend URL
BACKEND_URL=https://your-production-backend.com
```

### Sicherheitshinweise

1. **DISABLE_JWT_AUTH nur für Development**: Diese Variable NIEMALS in Production auf `true` setzen!

2. **Environment-Trennung**: Verschiedene .env-Dateien für Development und Production verwenden.

3. **Credential-Sicherheit**: Alle Supabase-Credentials nur im Backend, niemals im Frontend.

4. **Deployment-Check**: Vor Deployment IMMER prüfen, dass `DISABLE_JWT_AUTH=false` oder nicht gesetzt ist.

### Testing-Workflow

1. **Development starten**:
   ```bash
   cd /mnt/c/python/gtd
   source .venv/bin/activate
   export DISABLE_JWT_AUTH=true
   cd src/backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **API testen**:
   ```bash
   # Einfacher Test ohne JWT
   curl -X GET "http://localhost:8000/api/users/me"
   ```

3. **Production-Test**:
   ```bash
   export DISABLE_JWT_AUTH=false
   # Restart backend
   # Teste mit echtem JWT Token
   ```

### Fehlerbehandlung

#### JWT-Bypass aktiv (DISABLE_JWT_AUTH=true)
- Alle API-Calls funktionieren ohne Authorization Header
- Mock-User wird verwendet: `test@example.com`
- User-ID aus DEFAULT_USER_ID Environment Variable

#### JWT-Bypass inaktiv (DISABLE_JWT_AUTH=false oder nicht gesetzt)
- Authorization Header erforderlich: `Authorization: Bearer <token>`
- Echte JWT-Verification
- HTTP 401 bei fehlendem/invalidem Token

### Beispiel Test-Session

```bash
# 1. Backend mit JWT-Bypass starten
export DISABLE_JWT_AUTH=true
cd src/backend && python -m uvicorn app.main:app --reload --port 8000

# 2. API testen
curl -X GET "http://localhost:8000/api/users/me"
# -> {"user_id":"00000000-0000-0000-0000-000000000001","email":"test@example.com","role":"authenticated"}

curl -X GET "http://localhost:8000/api/projects/"
# -> [{"id":1,"name":"Project 1",...}]

# 3. Für Production: JWT-Bypass deaktivieren
export DISABLE_JWT_AUTH=false
# Backend restart required
```