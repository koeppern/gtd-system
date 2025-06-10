# Notion GTD Datenbank Export

Dieses Verzeichnis enthält einen Export der Notion-Datenbank mit einem GTD (Getting Things Done) System.

## Struktur

```
data/
└── from_notion/
    └── ae0e8447-0156-4ccc-a206-9c6d14e0c3ac_Export-8a287a79-0e8c-4d7e-9d22-baf005669425/
        ├── GTD 9caf9eb9a9a3449caa849931e788078f/
        │   └── GTD_Tasks 79d6be730eff4db0a02f6cbc1d627164_all.csv
        ├── GTD_Projects a0836eef075e4ab48b6f4d6b706b7472/
        │   └── [viele Markdown-Dateien]
        ├── GTD_Projects a0836eef075e4ab48b6f4d6b706b7472.csv
        ├── GTD_Projects a0836eef075e4ab48b6f4d6b706b7472_all.csv
        └── Short notes 6ed464b8aa4945c68103de59f8931125_all.csv
```

## CSV-Dateien

### 1. GTD_Tasks (GTD_Tasks 79d6be730eff4db0a02f6cbc1d627164_all.csv)
Enthält alle GTD-Aufgaben mit folgenden Spalten:
- **🌙Do this week**: Soll diese Woche erledigt werden
- **Task name**: Name der Aufgabe
- **🟩Done**: Erledigungsstatus
- **Date of creation**: Erstellungsdatum
- **Is project done?**: Projektstatus
- **Last editted**: Letzte Bearbeitung
- **⌛Wait for**: Wartet auf
- **✨Do today**: Heute erledigen
- **👔Field**: Bereich (Private/Work)
- **📆Do on date**: Fälligkeit
- **🚀Project**: Zugehöriges Projekt
- **📙Reading**: Leseaufgaben

Die Datei enthält hunderte von Aufgaben aus den Jahren 2021-2025.

### 2. GTD_Projects (GTD_Projects a0836eef075e4ab48b6f4d6b706b7472_all.csv)
Enthält alle GTD-Projekte mit folgenden Spalten:
- **❇Done**: Erledigungsstatus
- **Readings**: Lesematerial
- **Field**: Bereich (Private/Work)
- **Keywords**: Schlagwörter
- **Mother project**: Übergeordnetes Projekt
- **Related to Tasks**: Zugehörige Aufgaben (als Notion-Links)

Die Datei listet über 200 Projekte auf, darunter:
- Lernprojekte (LLM, RAG, Data Science, etc.)
- Private Projekte (Haushalt, Gesundheit, etc.)
- Berufliche Projekte (Dispendix, P3, EP, etc.)
- Technische Projekte (AWS, Azure, etc.)

### 3. Short notes (Short notes 6ed464b8aa4945c68103de59f8931125_all.csv)
Enthält kurze Notizen mit:
- **Name**: Notizinhalt
- **Company**: Firma
- **Date**: Datum
- **🗣️ People - database**: Verknüpfte Personen

Die Notizen stammen hauptsächlich aus dem beruflichen Kontext bei P3.

## Markdown-Dateien (GTD_Projects Ordner)

Der Ordner enthält über 200 Markdown-Dateien, jede repräsentiert ein einzelnes Projekt. Die Dateien sind nach dem Schema benannt:
`[Projektname] [UUID].md`

### Projektkategorien

1. **Lernprojekte**:
   - KI/ML: LLM, RAG, NLP, Agents, Fine-Tuning
   - Programmierung: Flutter, n8n, SQL, Python
   - Kurse: DeepLearning.ai, Coursera, Udemy

2. **Berufliche Projekte**:
   - Jobsuche und Karriereplanung
   - Firmenprojekte (Dispendix, P3, EP)
   - Technische Projekte (AWS, Azure, Docker)

3. **Private Projekte**:
   - Haushalt und Immobilie (Nibelungenstraße)
   - Gesundheit und Wellness
   - Persönliche Entwicklung

4. **Geschäftsideen**:
   - CardifyAI
   - NetworkK
   - Morning Assistant
   - Novel Writer Application

## Verwendung

Diese Daten stammen aus einem persönlichen GTD-System und enthalten:
- Aufgabenmanagement mit Prioritäten und Zeitplänen
- Projektplanung mit Verknüpfungen zwischen Aufgaben und Projekten
- Notizen und Kontaktinformationen
- Lernziele und Karriereplanung

Die Struktur folgt dem GTD-Prinzip mit klarer Trennung zwischen Aufgaben (Tasks) und Projekten (Projects), wobei Projekte mehrere zugehörige Aufgaben haben können.