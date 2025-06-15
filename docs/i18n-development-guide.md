# Internationalization (i18n) Development Guide

## 🌍 Wichtige Regel für alle Entwickler

**ACHTUNG: Bei jeder neuen Komponente oder Funktion, die Benutzer-sichtbare Strings enthält, MÜSSEN diese sofort in ALLE bereits implementierten Sprachen übersetzt werden!**

### Aktuell implementierte Sprachen:
- 🇺🇸 **Englisch (en)** - Standard/Fallback
- 🇩🇪 **Deutsch (de)** - Vollständig implementiert

## Workflow bei neuen Features

### 1. Neue Strings hinzufügen
```typescript
// ❌ FALSCH - Hardcoded Strings
<h1>New Feature Title</h1>

// ✅ RICHTIG - Translation Keys verwenden
<h1>{t('newFeature.title')}</h1>
```

### 2. Translation Files aktualisieren
```json
// locales/en/common.json
{
  "newFeature": {
    "title": "New Feature Title",
    "description": "This is a new feature"
  }
}

// locales/de/common.json  
{
  "newFeature": {
    "title": "Neuer Feature-Titel",
    "description": "Das ist ein neues Feature"
  }
}
```

### 3. Vor Commit prüfen
- [ ] Alle neuen Strings haben Translation Keys
- [ ] EN und DE Übersetzungen sind vollständig
- [ ] Komponente verwendet `useTranslations()` Hook
- [ ] Tests berücksichtigen i18n (falls vorhanden)

## Technische Implementation

### Translation Hook verwenden
```typescript
import { useTranslations } from 'next-intl';

export function MyComponent() {
  const t = useTranslations('myComponent');
  
  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
    </div>
  );
}
```

### Dateien-Struktur
```
src/
  locales/
    en/
      common.json       # Navigation, Buttons, allgemeine UI
      projects.json     # Projects-spezifische Strings
      tasks.json        # Tasks-spezifische Strings
      validation.json   # Formular-Validation Messages
    de/
      common.json       # Deutsche Übersetzungen
      projects.json
      tasks.json
      validation.json
```

## Checkliste für Entwickler

### Bei neuen Komponenten:
1. ✅ Translation Keys statt hardcoded Strings
2. ✅ Passende JSON-Datei wählen (common/projects/tasks/etc.)
3. ✅ EN + DE Übersetzungen hinzufügen
4. ✅ `useTranslations()` Hook implementieren
5. ✅ Testen in beiden Sprachen

### Bei Code Reviews:
- [ ] Keine hardcoded user-visible Strings
- [ ] Vollständige EN/DE Übersetzungen vorhanden
- [ ] Translation Keys sind aussagekräftig benannt

## Tools & Helpers

### Missing Translation Check
```bash
# Script um fehlende Übersetzungen zu finden
npm run i18n:check
```

### Translation Key Generator
```bash
# Automatisch Translation Keys aus Komponenten extrahieren
npm run i18n:extract
```

---

**💡 Tipp:** Denke bei jeder Entwicklung sofort an i18n - es ist viel einfacher von Anfang an richtig zu machen als nachträglich zu refactoren!