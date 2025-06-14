# Claude Code Rules für GTD ETL Project

## Datenbank-Regeln

**WICHTIG: Diese Regeln sind absolut verpflichtend!**

1. **Niemals SQLite verwenden** - Ausschließlich Supabase (PostgreSQL) als Datenbank
2. **Keine SQLite-Mocks in Tests** - Supabase darf NIEMALS mit SQLite emuliert oder gemockt werden
3. **Immer echte Supabase-Verbindung** - Auch in Tests wird die echte Supabase-Datenbank verwendet
4. **Keine localStorage Fallbacks** - Wenn Datenbank nicht erreichbar ist, zeige Fehlermeldung statt localStorage zu verwenden. User sollen echte Datenbankfehler sehen, nicht heimliche Fallbacks.

## Code-Organisation

1. **Source Code** - Aller Quellcode befindet sich ausschließlich im Ordner `src/` und dessen Unterordnern
2. **Konfiguration** - Alle Einstellungen, Variablen und Prompts werden in YAML-Dateien im Ordner `config/` gespeichert
3. **Keine Hardcoded Values** - Niemals Werte direkt im Quellcode definieren, sondern immer aus separaten Config-Dateien oder Environment Variables laden
4. **Environment Variables** - Bei Bedarf zuerst `.env` Datei laden

## Python-Entwicklung

**WICHTIG: Für Python-Entwicklung IMMER das virtuelle Environment (.venv) verwenden!**

1. **Virtual Environment ist Pflicht** - Niemals Python-Pakete global installieren
2. **Tests erstellen** - Nach jeder Implementierung sinnvolle Tests schreiben
3. **Tests ausführen** - Alle Tests müssen vor einem Commit erfolgreich durchlaufen

## Automatische Git-Commits

**WICHTIG: Nach jeder erfolgreich abgeschlossenen Claude Code Aufgabe wird automatisch ein Git-Commit durchgeführt.**

### Commit-Regeln:

1. **Nach jeder abgeschlossenen Entwicklungsaufgabe** (ETL-Pipeline, SQL-Schema, Tests, etc.)
2. **Nach Bug-Fixes oder wichtigen Verbesserungen**
3. **Nach Erstellung oder Aktualisierung von Dokumentation**

### Commit-Message Format:

```
<type>: <kurze Beschreibung>

<optional: längere Beschreibung>

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Commit-Types:
- `feat`: Neue Features oder Funktionalitäten
- `fix`: Bug-Fixes
- `docs`: Dokumentation
- `refactor`: Code-Refactoring ohne Funktionsänderung
- `test`: Tests hinzufügen oder ändern
- `chore`: Build-Prozess, Dependencies, etc.
- `sql`: Datenbankschema oder SQL-Änderungen

### Beispiel-Commit-Messages:

```
feat: implement GTD tasks ETL pipeline

- Add CSV parsing for 2483 tasks with 18 columns
- Implement project-task mapping with 70% success rate
- Convert Notion date formats to ISO timestamps
- Add done_at timestamp support for completion tracking

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
```

```
sql: create normalized schema with done_at timestamps

- Replace boolean done fields with TIMESTAMP done_at
- Add gtd_tasks table with foreign keys to projects/fields
- Create analytics views for completion tracking
- Add auto-update triggers for metadata

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
```

```
test: update ETL tests for normalized schema

- Fix field normalization tests to expect IDs instead of strings
- Add mocking for gtd_fields table interactions
- Update transform tests for field_id foreign key structure

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Testing-Befehle

Vor Commits sollen folgende Tests ausgeführt werden:

```bash
# GTD Projects ETL Tests
python3 -m pytest tests/test_etl_projects.py -v

# Tasks ETL Tests (falls vorhanden)
python3 -m pytest tests/test_etl_tasks.py -v

# Alle Tests
python3 -m pytest tests/ -v
```

## Projektstruktur

```
gtd/
├── src/                    # ALLER Source Code (Pflicht!)
│   ├── etl_projects.py    # GTD Projects ETL
│   └── etl_tasks.py       # GTD Tasks ETL
├── config/                # Konfigurationsdateien (YAML)
│   └── *.yaml            # Alle Settings, Variablen, Prompts
├── tests/                 # Unit Tests
│   ├── test_etl_projects.py
│   └── test_etl_tasks.py
├── sql/                   # Database Schema
│   ├── create_normalized_schema.sql
│   ├── create_gtd_tasks_table.sql
│   └── update_done_fields_to_timestamps.sql
├── docs/                  # Dokumentation
│   └── gtd_projects_from_notion.md
├── data/                  # Notion Export Data
│   └── from_notion/
├── .venv/                 # Virtual Environment (Pflicht für Python!)
├── requirements.txt       # Python Dependencies
├── .env                   # Environment Variables (nicht committen)
└── CLAUDE.md             # Diese Datei
```

## Environment Setup

**WICHTIG: Immer das virtuelle Environment verwenden!**

```bash
# Virtual Environment erstellen (einmalig, falls nicht vorhanden)
cd /mnt/c/python/gtd
python3 -m venv .venv

# Virtual Environment aktivieren (bei jeder Session)
source .venv/bin/activate

# Dependencies installieren
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Environment Variables setzen (.env Datei)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DEFAULT_USER_ID=your-user-uuid
```

## Entwicklung mit Virtual Environment

```bash
# Vor jeder Entwicklung aktivieren (vom Projekt-Root):
cd /mnt/c/python/gtd
source .venv/bin/activate

# Python-Befehle dann wie gewohnt:
python src/etl_projects.py
cd src/backend && python -m pytest tests/

# Deaktivieren nach der Arbeit:
deactivate
```

## ETL Ausführung

```bash
# WICHTIG: Virtual Environment aktivieren (vom Projekt-Root)
cd /mnt/c/python/gtd
source .venv/bin/activate

# GTD Projects importieren
python src/etl_projects.py --force

# GTD Tasks importieren
python src/etl_tasks.py --force

# Backend Tests ausführen
cd src/backend && python -m pytest tests/ -v
```