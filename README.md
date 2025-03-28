# 📊 Wortanzahl-Analyse Tool

## Überblick

Ein modernes CLI- und Web-Tool zur Analyse von DOCX-Dokumenten mit Unterstützung für lokale Dateien und Google Drive.

## Funktionen

- 🔍 Wortzählung in lokalen DOCX-Dokumenten
- 🌐 Google Drive Integration
- 📈 Detaillierte Wortstatistiken
- 🖥️ CLI- und Web-Benutzeroberfläche

## Voraussetzungen

- Python 3.11+
- Conda oder venv
- Google Drive API Zugriff (optional)

## Installation

1. Repository klonen:
```bash
git clone https://github.com/[Ihr-Benutzername]/wortanzahl-tool.git
cd wortanzahl-tool
```

2. Conda-Umgebung erstellen:
```bash
conda env create -f environment.yml
conda activate wortanzahl
```

3. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

## Google Drive Setup

1. Google Cloud Console öffnen
2. Neues Projekt erstellen
3. Google Drive API aktivieren
4. OAuth 2.0 Client-ID erstellen
5. `credentials.json` herunterladen und im Projektverzeichnis speichern

## Verwendung

### CLI-Modus

#### Lokale Dateien
```bash
python -m src.ui.cli local dokument1.docx dokument2.docx
```

#### Google Drive
```bash
python -m src.ui.cli drive --folder ORDNER_ID
python -m src.ui.cli drive --query "Suchbegriff"
```

### Web-UI

```bash
streamlit run src/ui/web.py
```

## Konfiguration

- Umgebungsvariablen in `.env` konfigurieren
- Google Drive Credentials in `credentials.json`

## Entwicklung

- Testing: `pytest`
- Code-Formatierung: `black .`
- Type-Checking: `mypy src`

## Lizenz

MIT License

## Mitwirken

Pull Requests sind willkommen. Für größere Änderungen bitte zuerst ein Issue öffnen.

## Kontakt

[Ihre Kontaktinformationen]