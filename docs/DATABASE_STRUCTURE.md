# GTD Database Structure - Complete Documentation

## 🎯 System Overview

Das GTD-System basiert auf einer normalisierten PostgreSQL-Datenbank in Supabase mit **4 Haupttabellen** und **3 nützlichen Views**.

**✅ Import Status:**
- **225 GTD Projects** aus Notion importiert
- **2,483 GTD Tasks** aus Notion importiert  
- **70% automatische Project-Task-Verknüpfung**
- **User**: Johannes Köppern (johannes.koeppern@googlemail.com)

---

## 📊 Database Tables (Echte Tabellen)

### 1. gtd_users - Benutzerverwaltung
```sql
CREATE TABLE gtd_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email_address VARCHAR(255) UNIQUE NOT NULL,
    timezone VARCHAR(50) DEFAULT 'Europe/Berlin',
    date_format VARCHAR(20) DEFAULT 'DD.MM.YYYY',
    time_format VARCHAR(10) DEFAULT '24h',
    weekly_review_day INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,
    deleted_at TIMESTAMP
);
```

**Aktueller Benutzer:**
- ID: `00000000-0000-0000-0000-000000000001`
- Name: Johannes Köppern
- Email: johannes.koeppern@googlemail.com

### 2. gtd_fields - Field-Kategorien (Lookup)
```sql
CREATE TABLE gtd_fields (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Standard Fields:**
- ID 1: "Private" - Persönliche Projekte und Aufgaben
- ID 2: "Work" - Berufliche Projekte und Aufgaben

### 3. gtd_projects - GTD Projekte
```sql
CREATE TABLE gtd_projects (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES gtd_users(id) ON DELETE CASCADE,
    notion_export_row INTEGER,
    project_name TEXT NOT NULL,
    readings TEXT,
    field_id INTEGER REFERENCES gtd_fields(id),
    keywords TEXT,
    mother_project TEXT,
    related_projects TEXT,
    related_mother_projects TEXT,
    related_knowledge_vault TEXT,
    related_tasks TEXT,
    done_at TIMESTAMP,  -- NULL = nicht abgeschlossen, Timestamp = abgeschlossen
    do_this_week BOOLEAN DEFAULT FALSE,
    gtd_processes TEXT,
    add_checkboxes TEXT,
    source_file VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);
```

**Imported Data:**
- **225 Projekte** aus `GTD_Projects a0836eef075e4ab48b6f4d6b706b7472_all.csv`
- Beispiele: "Build note taking application with LLM", "Build up BA knowledge"

### 4. gtd_tasks - GTD Aufgaben
```sql
CREATE TABLE gtd_tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES gtd_users(id) ON DELETE CASCADE,
    notion_export_row INTEGER,
    task_name TEXT NOT NULL,
    project_id INTEGER REFERENCES gtd_projects(id) ON DELETE SET NULL,
    project_reference TEXT,
    done_at TIMESTAMP,  -- NULL = nicht abgeschlossen, Timestamp = abgeschlossen
    do_today BOOLEAN DEFAULT FALSE,
    do_this_week BOOLEAN DEFAULT FALSE,
    is_reading BOOLEAN DEFAULT FALSE,
    wait_for BOOLEAN DEFAULT FALSE,
    postponed BOOLEAN DEFAULT FALSE,
    reviewed BOOLEAN DEFAULT FALSE,
    do_on_date DATE,
    last_edited TIMESTAMP,
    date_of_creation TIMESTAMP,
    field_id INTEGER REFERENCES gtd_fields(id),
    priority INTEGER,
    time_expenditure TEXT,
    url TEXT,
    knowledge_db_entry TEXT,
    source_file VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);
```

**Imported Data:**
- **2,483 Aufgaben** aus `GTD_Tasks 79d6be730eff4db0a02f6cbc1d627164_all.csv`
- **~70% automatisch** mit Projekten verknüpft über Fuzzy-Matching

---

## 👁️ Database Views (Virtuelle Tabellen)

### Views vs. Tabellen - Unterschied:
- **Echte Tabellen**: Speichern Daten physisch auf der Festplatte
- **Views**: Sind "gespeicherte Abfragen" die Daten aus mehreren Tabellen kombinieren
- **Views**: Verbrauchen fast keinen Speicherplatz, sind aber sehr praktisch für Abfragen

### 1. gtd_projects_with_fields
```sql
CREATE OR REPLACE VIEW gtd_projects_with_fields AS
SELECT 
    p.*,
    f.name as field_name,
    f.description as field_description,
    CASE WHEN p.done_at IS NOT NULL THEN true ELSE false END as is_done
FROM gtd_projects p
LEFT JOIN gtd_fields f ON p.field_id = f.id;
```

**Nutzen:** Zeigt Projekte mit Field-Namen statt IDs
- Beispiel: "Build LLM assistant [Private]" statt "Build LLM assistant [1]"

### 2. gtd_tasks_with_details
```sql
CREATE OR REPLACE VIEW gtd_tasks_with_details AS
SELECT 
    t.*,
    p.project_name,
    p.readings as project_readings,
    f.name as field_name,
    f.description as field_description,
    CASE WHEN t.done_at IS NOT NULL THEN true ELSE false END as is_done
FROM gtd_tasks t
LEFT JOIN gtd_projects p ON t.project_id = p.id
LEFT JOIN gtd_fields f ON t.field_id = f.id;
```

**Nutzen:** Zeigt Tasks mit Project-Namen und Field-Informationen

### 3. gtd_user_dashboard
```sql
CREATE OR REPLACE VIEW gtd_user_dashboard AS
SELECT 
    u.id as user_id,
    u.first_name,
    u.last_name,
    u.email_address,
    COUNT(DISTINCT p.id) as total_projects,
    COUNT(DISTINCT CASE WHEN p.done_at IS NOT NULL THEN p.id END) as completed_projects,
    COUNT(DISTINCT CASE WHEN p.done_at IS NULL THEN p.id END) as active_projects,
    COUNT(DISTINCT t.id) as total_tasks,
    COUNT(DISTINCT CASE WHEN t.done_at IS NOT NULL THEN t.id END) as completed_tasks,
    COUNT(DISTINCT CASE WHEN t.done_at IS NULL THEN t.id END) as pending_tasks,
    COUNT(DISTINCT CASE WHEN t.do_today = true AND t.done_at IS NULL THEN t.id END) as tasks_today,
    COUNT(DISTINCT CASE WHEN t.do_this_week = true AND t.done_at IS NULL THEN t.id END) as tasks_this_week,
    u.last_login_at,
    u.created_at as user_since
FROM gtd_users u
LEFT JOIN gtd_projects p ON u.id = p.user_id AND p.deleted_at IS NULL
LEFT JOIN gtd_tasks t ON u.id = t.user_id AND t.deleted_at IS NULL
WHERE u.deleted_at IS NULL
GROUP BY u.id, u.first_name, u.last_name, u.email_address, u.last_login_at, u.created_at;
```

**Nutzen:** Bietet eine Dashboard-Übersicht mit Statistiken für jeden User

---

## 🔗 Key Relationships

```
gtd_users (1) ←→ (N) gtd_projects
gtd_users (1) ←→ (N) gtd_tasks  
gtd_fields (1) ←→ (N) gtd_projects
gtd_fields (1) ←→ (N) gtd_tasks
gtd_projects (1) ←→ (N) gtd_tasks
```

---

## 📈 Current Data Status

### Johannes Köppern's GTD System:
- **User ID**: `00000000-0000-0000-0000-000000000001`
- **Total Projects**: 225
- **Total Tasks**: 2,483
- **Project-Task Mappings**: ~70% automatisch verknüpft
- **Field Distribution**: Private & Work projects

### Import Sources:
- **Projects**: `GTD_Projects a0836eef075e4ab48b6f4d6b706b7472_all.csv`
- **Tasks**: `GTD_Tasks 79d6be730eff4db0a02f6cbc1d627164_all.csv`

---

## 🔧 Key Features

### 1. Normalisierte Struktur
- Fields als separate Lookup-Tabelle (nicht VARCHAR)
- Foreign Key Relationships für Datenintegrität
- UUID für User-IDs (Multi-User-fähig)

### 2. Completion Tracking
- `done_at` Timestamps statt Boolean-Felder
- Ermöglicht Analytics: "Wann wurde was abgeschlossen?"
- NULL = nicht abgeschlossen, Timestamp = abgeschlossen

### 3. Soft Delete Pattern
- `deleted_at` Timestamps für weiches Löschen
- Daten bleiben erhalten, sind aber "gelöscht"
- Ermöglicht Wiederherstellung

### 4. Automatische Metadaten
- `created_at`, `updated_at` Triggers
- `source_file` für Nachverfolgung des Imports
- `notion_export_row` für Debugging

---

## 🎯 System Status: READY FOR USE ✅

Das GTD-System ist vollständig eingerichtet und einsatzbereit:
- ✅ Alle Tabellen erstellt und funktional
- ✅ Alle Notion-Daten importiert  
- ✅ Views für einfache Abfragen verfügbar
- ✅ User Johannes Köppern angelegt
- ✅ Datenintegrität gewährleistet

**Nächste Schritte**: Web-Frontend für das GTD-System entwickeln!

---

*Dokumentation Stand: 2025-06-10 - Nach erfolgreichem Import und Verifikation*