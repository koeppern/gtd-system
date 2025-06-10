# GTD Projects from Notion - Datenstruktur für ETL Pipeline

## Übersicht
Diese Dokumentation beschreibt die Datenstruktur der GTD (Getting Things Done) Projekte aus dem Notion-Export für die Entwicklung einer ETL-Pipeline.

## Quell-Dateien

### Primäre Datenquellen
```
data/from_notion/ae0e8447-0156-4ccc-a206-9c6d14e0c3ac_Export-8a287a79-0e8c-4d7e-9d22-baf005669425/
├── GTD_Projects a0836eef075e4ab48b6f4d6b706b7472_all.csv          (259 Zeilen + Header)
├── GTD_Projects a0836eef075e4ab48b6f4d6b706b7472.csv               (Subset der _all.csv)
├── GTD 9caf9eb9a9a3449caa849931e788078f/
│   └── GTD_Tasks 79d6be730eff4db0a02f6cbc1d627164_all.csv          (Tasks)
├── Short notes 6ed464b8aa4945c68103de59f8931125_all.csv            (Kurze Notizen)
└── GTD_Projects a0836eef075e4ab48b6f4d6b706b7472/                  (200+ Markdown-Dateien)
    ├── [Projektname] [UUID].md
    └── ...
```

## Datenstruktur - GTD_Projects CSV

### Schema Definition (Normalisiert)
```sql
-- Normalisierte Schema-Struktur mit separater FIELDS-Tabelle

-- 1. FIELDS Lookup-Tabelle
CREATE TABLE gtd_fields (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Standard-Werte für FIELDS
INSERT INTO gtd_fields (name, description) VALUES 
    ('Private', 'Personal projects and tasks'),
    ('Work', 'Professional projects and tasks');

-- 2. GTD Projects Haupttabelle mit Foreign Key zu FIELDS
CREATE TABLE gtd_projects (
    id SERIAL PRIMARY KEY,                    -- Eindeutige ID (Auto-generiert)
    user_id UUID NOT NULL,                   -- Benutzer-ID für Multi-User Support
    notion_export_row INTEGER,               -- Original CSV Zeilennummer
    done_status BOOLEAN,                      -- ❇Done
    readings TEXT,                           -- Readings
    field_id INTEGER REFERENCES gtd_fields(id), -- Foreign Key zu FIELDS-Tabelle
    keywords TEXT,                           -- Keywords
    done_duplicate BOOLEAN,                  -- Done (Duplikat-Spalte)
    mother_project TEXT,                     -- Mother project
    related_projects TEXT,                   -- Related GTD_Projects
    related_mother_projects TEXT,            -- Related to GTD_Projects (Mother project)
    related_knowledge_vault TEXT,            -- Related to Knowledge volt (Project)
    related_tasks TEXT,                      -- Related to Tasks (Project)
    do_this_week BOOLEAN,                    -- 🌙Do this week
    gtd_processes TEXT,                      -- 🏃‍♂️ GTD_Processes
    add_checkboxes TEXT,                     -- Add checkboxes as option for answers
    project_name TEXT,                       -- Extrahiert aus den Task-Links oder Zeile 2
    source_file VARCHAR(255),                -- Quelldatei
    created_at TIMESTAMP DEFAULT NOW(),      -- Erstellungs-Timestamp
    updated_at TIMESTAMP DEFAULT NOW(),      -- Update-Timestamp
    deleted_at TIMESTAMP                     -- Soft-Delete Timestamp
);

-- 3. View für einfache Abfragen mit Field-Namen
CREATE VIEW gtd_projects_with_fields AS
SELECT 
    p.*,
    f.name as field_name,
    f.description as field_description
FROM gtd_projects p
LEFT JOIN gtd_fields f ON p.field_id = f.id;

-- 4. Indizes für Performance
CREATE INDEX idx_gtd_projects_user_id ON gtd_projects(user_id);
CREATE INDEX idx_gtd_projects_field_id ON gtd_projects(field_id);
```

### CSV-Spalten im Detail

| Spalte | Typ | Beschreibung | Beispielwerte | Besonderheiten |
|--------|-----|--------------|---------------|----------------|
| `❇Done` | Boolean | Projekt abgeschlossen | Yes/No | Primärer Status-Indikator |
| `Readings` | Text | Projektbeschreibung | "tictok news reader", "API course" | Hauptidentifikator |
| `Field` | FK zu gtd_fields | Arbeitsbereich | Private, Work, NULL | Foreign Key zu FIELDS-Tabelle |
| `Keywords` | Text | Schlagwörter | "ihk trainer ai business Fabian Deitelhoff" | Spärlich gefüllt |
| `Done` | Boolean | Duplikat-Status | Identisch mit ❇Done | Redundant |
| `Mother project` | Text | Übergeordnetes Projekt | Meist leer | Hierarchie |
| `Related GTD_Projects` | Text | Verknüpfte Projekte | Meist leer | Referenzen |
| `Related to GTD_Projects (Mother project)` | Text | Mutter-Projekt-Ref | Meist leer | Hierarchie |
| `Related to Knowledge volt (Project)` | Text | Wissens-DB Referenz | Meist leer | Externe Refs |
| `Related to Tasks (Project)` | Text | Aufgaben-Links | Notion URLs mit Task-IDs | **Hauptinhalt** |
| `🌙Do this week` | Boolean | Wöchentliche Priorität | Yes/No | Zeitplanung |
| `🏃‍♂️ GTD_Processes` | Text | GTD-Prozesse | Meist leer | Metadaten |
| `Add checkboxes as option for answers` | Text | UI-Einstellungen | Meist leer | System-Config |

### Besondere Datenmerkmale

#### 1. Task-Links in `Related to Tasks (Project)`
```
Beispiel-Format:
"Improve summarization prompt with prompt generator (https://www.notion.so/Improve-summarization-prompt-with-prompt-generator-d5c817038d8245d0b6fb5ad4e5c33835?pvs=21), integrate tts (https://www.notion.so/integrate-tts-9f1412d7f3374d1a83a37ab5501a3d9e?pvs=21)"

Struktur:
- Komma-separierte Liste
- Format: "[Task-Name] ([Notion-URL])"
- Notion-URLs enthalten UUID: d5c817038d8245d0b6fb5ad4e5c33835
```

#### 2. Zeilenumbrüche in CSV
```
Zeilen 8-10: NetworkK Projekt
"Question o1,
How I could organize the further path with Kerstin regarding the rejection of Sotir and the next steps. I have the idea that we could create a synthetic company and then create a
real demonstrations with this data, which Kerstin can then use to present the product to customers and so that we can raise funding."
```

#### 3. Datenqualität
- **Total Records**: 259 (ohne Header)
- **Vollständige Projekte**: ~200
- **Leere/Unvollständige**: ~59
- **Field-Verteilung**: ~60% Private, ~30% Work, ~10% NULL

## Markdown-Dateien Struktur

### Datei-Namenskonvention
```
[Projektname mit Sonderzeichen] [UUID].md

Beispiele:
- "tictok news reader 4145a49457da4f9bb99944b558b5e4fe.md"
- "API course dd7a426f6cbb44f2825bbd152678def2.md"
- "😊Miscellaneous - private fun 3f07b24e0fd94e729b0f43ac25cb442a.md"
```

### UUID-Extraktion
```python
# ETL-Regel für UUID-Extraktion
import re
filename_pattern = r"^(.+)\s([a-f0-9]{32})\.md$"
match = re.match(filename_pattern, filename)
if match:
    project_name = match.group(1).strip()
    project_uuid = match.group(2)
```

## ETL-Pipeline Empfehlungen

### 1. Extraktion (Extract)
```python
# Datenquellen
sources = {
    'projects_csv': 'GTD_Projects a0836eef075e4ab48b6f4d6b706b7472_all.csv',
    'tasks_csv': 'GTD_Tasks 79d6be730eff4db0a02f6cbc1d627164_all.csv',
    'notes_csv': 'Short notes 6ed464b8aa4945c68103de59f8931125_all.csv',
    'project_files': 'GTD_Projects a0836eef075e4ab48b6f4d6b706b7472/*.md'
}
```

### 2. Transformation (Transform)
```python
# Bereinigungsregeln
transformations = {
    'normalize_boolean': ['❇Done', '🌙Do this week'],
    'parse_task_links': 'Related to Tasks (Project)',
    'extract_uuids': 'task_links',
    'clean_multiline': 'alle_text_felder',
    'categorize_field': 'Field',
    'extract_project_name': 'filename_or_readings'
}
```

### 3. Laden (Load)
```python
# Ziel-Tabellen
target_tables = {
    'gtd_projects': 'Haupt-Projekt-Tabelle',
    'gtd_tasks': 'Aufgaben aus CSV + extrahierte Links',
    'project_task_relations': 'M:N Beziehungen',
    'project_files': 'Markdown-Dateien Metadaten'
}
```

## Datenbeziehungen

### Primärschlüssel-Strategie
```sql
-- Eindeutige IDs für ETL
gtd_projects.id = SERIAL (1, 2, 3, ...)
gtd_projects.notion_export_row = CSV-Zeilennummer (2, 3, 4, ...)
gtd_projects.source_readings = "tictok news reader" (aus CSV)
gtd_projects.file_uuid = "4145a49457da4f9bb99944b558b5e4fe" (aus .md Datei)
```

### Referenz-Mapping
```sql
-- Task-Link Extraktion
CREATE TABLE task_references (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES gtd_projects(id),
    task_name TEXT,
    notion_url TEXT,
    notion_uuid VARCHAR(32),
    extracted_at TIMESTAMP DEFAULT NOW()
);
```

## Validierung & Monitoring

### Datenqualitäts-Checks
```sql
-- ETL-Validierung
SELECT 
    COUNT(*) as total_projects,
    COUNT(CASE WHEN readings IS NOT NULL THEN 1 END) as projects_with_names,
    COUNT(CASE WHEN field IS NOT NULL THEN 1 END) as projects_with_field,
    COUNT(CASE WHEN related_tasks IS NOT NULL THEN 1 END) as projects_with_tasks
FROM gtd_projects;
```

### Konsistenz-Prüfungen
```sql
-- Markdown-Datei zu CSV Mapping
SELECT 
    p.id,
    p.readings as csv_name,
    f.filename as md_filename,
    CASE WHEN f.project_uuid IS NULL THEN 'MISSING_FILE' ELSE 'OK' END as status
FROM gtd_projects p
LEFT JOIN project_files f ON p.file_uuid = f.project_uuid;
```

## Nächste Schritte für ETL-Entwicklung

1. **CSV-Parser entwickeln** - Umgang mit Multiline-Fields
2. **Task-Link-Extraktor** - Regex für Notion-URLs
3. **UUID-Extraktor** - Markdown-Dateinamen parsen
4. **Datenbereinigung** - Boolean-Normalisierung, Text-Cleanup
5. **Beziehungs-Mapper** - Project-Task-Relations aufbauen
6. **Validierung** - Datenqualität und Konsistenz prüfen

---
*Erstellt für ETL-Pipeline Entwicklung | Quelle: Notion GTD Export*