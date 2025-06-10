# GTD ETL-Pipeline – Datenintegration aus Notion in Supabase

Diese Anwendung dient dem Aufbau einer eigenen Getting-Things-Done (GTD) Infrastruktur. Ziel ist es, Notion vollständig zu ersetzen und alle Projekte, Aufgaben und Notizen in einer eigenen Web-Anwendung zu verwalten.

## Projektüberblick

Das System besteht aus zwei Hauptkomponenten:

1. **ETL-Pipeline (`src/etl_projects.py`, `src/etl_tasks.py`, ...)**
   - Extraktion der Daten aus dem Notion-Export (CSV)
   - Transformation der Inhalte (Parsing, Normalisierung, Mapping)
   - Laden in eine relationale PostgreSQL-Datenbank via Supabase

2. **Web-Anwendung (Next.js, SQL-Backend)**
   - Zugriff auf GTD-Daten (Projekte, Aufgaben etc.)
   - Unterstützung mehrerer Benutzer
   - Langfristig als PWA nutzbar (mobile Unterstützung)

---

## Technisches Setup

- **Quellformat:** Notion-Export, UTF-8-codierte CSV-Dateien
- **Zieldatenbank:** Supabase PostgreSQL (via Service Role Key)
- **Entwicklungsumgebung:** Python (.venv), Next.js (später)

**Zugangsdaten:** in `.env`  
```env
SUPABASE_URL=https://<projekt>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=...
```

---

## Zielstruktur: Tabelle `gtd_projects`

```sql
CREATE TABLE gtd_projects (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,                  -- Verweis auf Supabase Auth
    notion_export_row INTEGER,              -- Original-Zeilennummer aus CSV
    done_status BOOLEAN,                    -- ❇Done
    readings TEXT,
    field VARCHAR(50),
    keywords TEXT,
    done_duplicate BOOLEAN,                 -- ggf. redundant
    mother_project TEXT,
    related_projects TEXT,
    related_mother_projects TEXT,
    related_knowledge_vault TEXT,
    related_tasks TEXT,                     -- Komma-separierte Task-Referenzen
    do_this_week BOOLEAN,
    gtd_processes TEXT,
    add_checkboxes TEXT,
    project_name TEXT,
    source_file VARCHAR(255),               -- Name der CSV-Datei
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP                    -- weiches Löschen
);
```

---

## ETL-Prozess (truncate & insert)

### Projektstruktur
```
src/
├── etl_projects.py         # Importiert GTD-Projekte aus Notion-CSV
├── etl_tasks.py            # (folgt) Aufgabenverarbeitung
docs/
└── README.md               # Diese Dokumentation
```

### Datenquellen
```python
sources = {
    'projects_csv': 'data/from_notion/.../GTD_Projects*_all.csv',
    'tasks_csv': 'data/from_notion/.../GTD_Tasks*_all.csv',
    'notes_csv': 'data/from_notion/.../Short notes*_all.csv',
    'project_files': 'data/from_notion/.../GTD_Projects*/.md'
}
```

### Transformationen

- **Boolean-Normalisierung:** `"Yes"` → `True`, `"No"` → `False`
- **Multiline-Handling:** innerhalb von CSV-Feldern
- **Task-Link-Parsing:** `Related to Tasks (Project)` extrahiert Notion-URLs & UUIDs
- **Feld-Normalisierung:** `Field ∈ {Private, Work, NULL}`
- **Dateiquelle:** wird in `source_file` gespeichert
- **user_id:** wird als Konstante aus `.env` oder zur Laufzeit übergeben

---

## Datenmodell-Beziehungen

Für spätere Erweiterung:
```sql
CREATE TABLE task_references (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES gtd_projects(id),
    task_name TEXT,
    notion_url TEXT,
    notion_uuid VARCHAR(32),
    extracted_at TIMESTAMP DEFAULT NOW()
);
```

---

## Fehlerverarbeitung

- CSVs mit fehlerhaften Zeilen führen **nicht** zum Abbruch
- Fehlerhafte Zeilen werden übersprungen und geloggt
- Zukünftig möglich: Protokollierung in `etl_log`-Tabelle

---

## Hinweis zur Benutzerverwaltung

Die Spalte `user_id` referenziert die UUID aus der Supabase `auth.users` Tabelle. Dadurch können mehrere Benutzer ihre eigenen GTD-Projekte pflegen.

---

## Technische Details für Entwickler

### .env-Konfiguration

- Die `.env`-Datei liegt im **Projekt-Root-Verzeichnis**.
- Sie wird mit `python-dotenv` geladen.
- Beispielhafte Verwendung in Python:
```python
from dotenv import load_dotenv
load_dotenv()
```

### Supabase-Datenbankverbindung

- Die Tabelle `gtd_projects` wird beim ETL-Lauf automatisch erstellt, falls sie noch nicht existiert.
- Der Tabellenname ist fix auf `gtd_projects` gesetzt.

### Fehlerbehandlung und Logging

- Fehlerhafte oder unvollständige Zeilen im CSV werden **nicht eingefügt**, aber auch **nicht** zum Abbruch führen.
- Es erfolgt eine **konsolenbasierte Protokollierung** von Warnungen und erfolgreichen Einträgen.
- Es wird **keine Datei-Logfunktion** verwendet.

### Umgang mit Truncate/Delete

- Vor dem Entfernen bestehender Einträge wird der **Benutzer zur Bestätigung** aufgefordert.
- Nur wenn der Benutzer zustimmt, wird `TRUNCATE gtd_projects;` ausgeführt.

### Benutzer-ID (user_id)

- Die `user_id` wird aus der Supabase `auth.users` Tabelle übernommen.
- Standardverhalten: Sie wird aus einer Umgebungsvariable geladen (`DEFAULT_USER_ID`) oder per Übergabeparameter gesetzt.

---

## Beispielhafte Struktur zur Implementierung

```python
import os
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID")
```

---

## Voraussetzungen zur Ausführung

- Python 3.9+
- Abhängigkeiten (mit pip installierbar):
```bash
pip install python-dotenv pandas supabase
```

---

*Stand: 2025-06-09*
## Entscheidung für ein Python-Backend

Nach Abwägung der Vor- und Nachteile haben wir uns entschieden, ein separates Python-Backend zu implementieren. Diese Architektur bietet mehrere Vorteile:

- **Sicherheit:** Durch die Trennung von Frontend und Backend wird der direkte Datenbankzugriff aus dem Frontend vermieden. Das Backend übernimmt die Geschäftslogik und die Zugriffskontrolle, was die Sicherheit erhöht.
- **Flexibilität:** Das Backend ermöglicht es, komplexe Funktionen und Integrationen umzusetzen, die im Frontend nur schwer realisierbar wären.
- **Skalierbarkeit:** Frontend und Backend können unabhängig voneinander skaliert werden, was langfristig zu einer stabileren und performanteren Anwendung führt.

**Authentifizierung:**
Wir setzen auf eine Authentifizierung mit JWT (JSON Web Tokens), um eine sichere und skalierbare Nutzerverwaltung zu gewährleisten. Supabase unterstützt uns dabei, indem es bereits eine integrierte Auth-Lösung und die Verwaltung der Nutzer-UUIDs bereitstellt.
