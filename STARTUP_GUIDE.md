# GTD Development Startup Guide

## 🚀 Quick Start Scripts

Das Projekt verfügt über ausführbare Bash-Scripts zum einfachen Starten der Entwicklungsumgebung.

### 📁 Verfügbare Scripts

```bash
./start-backend.sh     # Startet nur das FastAPI Backend (Port 8000)
./start-frontend.sh    # Startet nur das Frontend (Port 3000)
./start-dev.sh         # Startet beide Server parallel
```

## 🔧 Backend starten

```bash
# Aus dem Projekt-Root-Verzeichnis:
./start-backend.sh
```

**Was passiert:**
- ✅ Überprüft Virtual Environment (erstellt es falls nötig)
- ✅ Aktiviert `.venv` automatisch
- ✅ Installiert Dependencies falls nötig
- ✅ Testet Datenbank-Verbindung
- ✅ Startet FastAPI Server mit Auto-Reload

**Verfügbar unter:**
- 🌐 Backend API: http://localhost:8000/api
- 📖 API Dokumentation: http://localhost:8000/api/docs
- 🔄 Alternative Docs: http://localhost:8000/api/redoc

## 🎨 Frontend starten

```bash
# Aus dem Projekt-Root-Verzeichnis:
./start-frontend.sh
```

**Was passiert:**
- ✅ Erkennt Frontend-Framework automatisch (Next.js/React/Vite)
- ✅ Installiert Node.js Dependencies falls nötig
- ✅ Erstellt `.env.local` falls nicht vorhanden
- ✅ Überprüft Backend-Verfügbarkeit
- ✅ Startet Development Server

**Verfügbar unter:**
- 🌐 Frontend: http://localhost:3000

## 🚀 Full Stack Development

```bash
# Startet Backend UND Frontend parallel:
./start-dev.sh
```

**Features:**
- 🔄 Startet beide Server gleichzeitig
- 🛑 Ctrl+C stoppt beide Server sauber
- 📊 Überwacht beide Prozesse
- 🎯 Perfekt für Full-Stack Development

## ⚙️ Voraussetzungen

### Backend
- Python 3.8+
- Virtual Environment wird automatisch erstellt
- `.env` Datei mit Supabase-Credentials

### Frontend
- Node.js 16+
- npm oder yarn
- `package.json` im Frontend-Verzeichnis

## 🐛 Troubleshooting

### Backend startet nicht
```bash
# Prüfe .env Datei
cat .env

# Prüfe Python Version
python3 --version

# Manuell Virtual Environment erstellen
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Frontend startet nicht
```bash
# Prüfe Node.js Installation
node --version
npm --version

# Dependencies neu installieren
cd src/frontend  # oder dein Frontend-Verzeichnis
rm -rf node_modules package-lock.json
npm install
```

### Port bereits belegt
```bash
# Backend Port (8000) freigeben
lsof -ti:8000 | xargs kill -9

# Frontend Port (3000) freigeben  
lsof -ti:3000 | xargs kill -9
```

## 📁 Projekt-Struktur

```
gtd/
├── start-backend.sh      # Backend Startup Script
├── start-frontend.sh     # Frontend Startup Script  
├── start-dev.sh          # Combined Startup Script
├── .venv/                # Virtual Environment
├── requirements.txt      # Python Dependencies
├── .env                  # Environment Variables
├── src/
│   ├── backend/          # FastAPI Backend
│   └── frontend/         # Next.js Frontend
└── STARTUP_GUIDE.md      # Diese Datei
```

## 🎯 Entwicklungsworkflow

1. **Erste Einrichtung:**
   ```bash
   git clone <repo>
   cd gtd
   cp .env.example .env
   # .env mit Supabase-Credentials füllen
   ```

2. **Tägliche Entwicklung:**
   ```bash
   ./start-dev.sh
   # Beide Server sind bereit!
   ```

3. **Nur Backend testen:**
   ```bash
   ./start-backend.sh
   # API Tests unter http://localhost:8000/api/docs
   ```

4. **Nur Frontend entwickeln:**
   ```bash
   ./start-frontend.sh
   # UI Entwicklung auf http://localhost:3000
   ```

## 🔐 Sicherheitshinweise

- ⚠️ Scripts prüfen `.env` Dateien automatisch
- ⚠️ Keine Credentials in den Scripts selbst
- ⚠️ Development-Modus aktiviert Auto-Reload
- ⚠️ Nicht für Production verwenden