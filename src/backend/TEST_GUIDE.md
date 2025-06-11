# GTD Backend Test Guide

## Übersicht

Das GTD Backend verfügt über eine umfassende Test-Suite mit **217 Tests** (Stand: aktuell), die verschiedene Aspekte der Anwendung abdecken.

## Test-Kategorien

### 1. **Supabase Connection Tests** (`test_supabase_connection.py`)
- Testet die Verbindung zur Supabase PostgreSQL-Datenbank
- Überprüft das Vorhandensein aller erforderlichen Tabellen
- Testet CRUD-Operationen und Foreign Key Constraints
- Prüft PostgreSQL-spezifische Features und Views
- **Neue Tests:**
  - `TestSupabaseConnection`: Basis-Verbindungstests
  - `TestSupabaseCRUD`: CRUD-Operationen mit echten Modellen
  - `TestConnectionResilience`: Verbindungsstabilität und Parallelität

### 2. **Model Tests** (`test_models.py`)
- Testet SQLAlchemy-Modelle (User, Project, Task, Field)
- Validiert Datenbank-Beziehungen und Constraints
- Prüft Soft-Delete-Funktionalität

### 3. **Schema Tests** (`test_schemas.py`)
- Testet Pydantic-Schemas für Validierung
- Prüft Serialisierung und Deserialisierung
- Validiert Datentypen und Feldanforderungen

### 4. **CRUD Tests** (`test_crud_operations.py`)
- Testet CRUD-Operationen für alle Entitäten
- Prüft Filterung und Paginierung
- Testet komplexe Abfragen

### 5. **API Endpoint Tests**
- `test_api_users.py`: User-Endpunkte
- `test_api_projects.py`: Project-Endpunkte
- `test_api_tasks.py`: Task-Endpunkte
- `test_api_fields.py`: Field-Endpunkte
- `test_api_dashboard.py`: Dashboard-Statistiken
- `test_api_search.py`: Such-Funktionalität
- `test_api_quick_add.py`: Quick-Add Features

### 6. **Integration Tests**
- `test_api_integration.py`: API-übergreifende Tests
- `test_api_with_data.py`: Tests mit vordefinierten Testdaten
- `test_main_app.py`: Hauptanwendungs-Tests

### 7. **Simple API Tests** (`test_simple_api.py`)
- Basis-API-Funktionalität
- Health-Check-Endpunkte
- Error-Handling

## Test-Ausführung

### Voraussetzungen

1. **Virtual Environment aktivieren:**
   ```bash
   cd /mnt/c/python/gtd
   source .venv/bin/activate  # Linux/Mac
   # oder
   .venv\Scripts\activate     # Windows
   ```

2. **Dependencies installieren:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Umgebungsvariablen setzen:**
   - Stelle sicher, dass `.env` konfiguriert ist
   - Für Tests wird `test_config.yaml` automatisch verwendet

### Alle Tests ausführen

```bash
# Zum Backend-Verzeichnis wechseln
cd src/backend

# Einfacher Test-Lauf
python -m pytest

# Mit Details
python -m pytest -v

# Mit Coverage-Report
python -m pytest --cov=app --cov-report=html
```

### Spezifische Tests ausführen

```bash
# Nur Supabase-Connection-Tests
python -m pytest tests/test_supabase_connection.py -v

# Nur eine Test-Klasse
python -m pytest tests/test_supabase_connection.py::TestSupabaseConnection -v

# Nur einen spezifischen Test
python -m pytest tests/test_supabase_connection.py::TestSupabaseConnection::test_database_connection -v

# Tests nach Keyword filtern
python -m pytest -k "supabase" -v

# Nur schnelle Tests (ohne slow-Marker)
python -m pytest -m "not slow"
```

### Test-Ausgabe-Optionen

```bash
# Kurze Ausgabe
python -m pytest -q

# Zeige Print-Statements
python -m pytest -s

# Stoppe beim ersten Fehler
python -m pytest -x

# Zeige die langsamsten Tests
python -m pytest --durations=10
```

### Parallel Testing

```bash
# Tests parallel ausführen (schneller)
python -m pytest -n auto
```

## Test-Konfiguration

Die Test-Konfiguration befindet sich in:
- `pytest.ini`: Pytest-Einstellungen
- `test_config.yaml`: Test-spezifische App-Konfiguration
- `conftest.py`: Gemeinsame Test-Fixtures

## Wichtige Hinweise

1. **Datenbank-Verbindung**: 
   - Tests verwenden die in `.env` konfigurierten Supabase-Credentials
   - Bei fehlender Verbindung werden einige Tests übersprungen

2. **Test-Isolation**:
   - Jeder Test sollte unabhängig laufen
   - Test-Daten werden nach jedem Test bereinigt

3. **Async Tests**:
   - Viele Tests sind asynchron (`@pytest.mark.asyncio`)
   - pytest-asyncio handhabt die Event-Loop automatisch

## Debugging von Tests

```bash
# Mit Python Debugger
python -m pytest tests/test_supabase_connection.py --pdb

# Zeige lokale Variablen bei Fehlern
python -m pytest -l

# Verbose Traceback
python -m pytest --tb=long
```

## Continuous Integration

Tests können in CI/CD-Pipelines integriert werden:

```yaml
# Beispiel GitHub Actions
- name: Run tests
  run: |
    python -m pytest --cov=app --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Troubleshooting

### "No such table" Fehler
- Stelle sicher, dass die Datenbank-Verbindung korrekt konfiguriert ist
- Überprüfe `.env` für Supabase-Credentials

### Import-Fehler
- Aktiviere das Virtual Environment
- Installiere alle Dependencies: `pip install -r requirements-dev.txt`

### Async-Warnungen
- Die `asyncio_default_fixture_loop_scope` ist in pytest.ini gesetzt
- Bei Problemen: `pip install --upgrade pytest-asyncio`