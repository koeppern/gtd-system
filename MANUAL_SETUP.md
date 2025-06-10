# Manual Setup für GTD ETL Pipeline

## 1. Supabase Tabelle erstellen

Die GTD-Projekte Tabelle muss manuell in Supabase erstellt werden.

### Schritte:

1. Gehe zu [Supabase Dashboard](https://app.supabase.com)
2. Wähle dein Projekt aus
3. Gehe zu "SQL Editor"
4. Führe das folgende SQL aus:

```sql
CREATE TABLE gtd_projects (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    notion_export_row INTEGER,
    done_status BOOLEAN,
    readings TEXT,
    field VARCHAR(50),
    keywords TEXT,
    done_duplicate BOOLEAN,
    mother_project TEXT,
    related_projects TEXT,
    related_mother_projects TEXT,
    related_knowledge_vault TEXT,
    related_tasks TEXT,
    do_this_week BOOLEAN,
    gtd_processes TEXT,
    add_checkboxes TEXT,
    project_name TEXT,
    source_file VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Create index for user_id for performance
CREATE INDEX idx_gtd_projects_user_id ON gtd_projects(user_id);
```

## 2. ETL Pipeline ausführen

Nach der Tabellenerstellung kann die ETL Pipeline ausgeführt werden:

```bash
# Mit Bestätigung für Truncate
python3 src/etl_projects.py

# Ohne Bestätigung (Force Mode)
python3 src/etl_projects.py --force

# Ohne Truncate (Append Mode)
python3 src/etl_projects.py --no-truncate
```

## 3. Testen

Tests ausführen:
```bash
python3 -m pytest tests/test_etl_projects.py -v
```

## 4. Umgebungsvariablen

Stelle sicher, dass `.env` korrekt konfiguriert ist:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DEFAULT_USER_ID=your-user-uuid
```