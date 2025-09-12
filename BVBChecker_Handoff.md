
# BVBChecker – Projektzusammenfassung & Handover

## Überblick
Der **BVBChecker** ist ein lokaler REST-Dienst mit einfacher UI, der Ärzt:innen in der Hausarztpraxis unterstützt, schnell zu prüfen, ob ein Patient Anspruch auf **Besonderen Verordnungsbedarf (BVB)** für Heilmittel hat.

- **Eingaben:** ICD-10 Codes, optional Alter/Geschlecht, Diagnosegruppe, Heilmittelbereich
- **Ausgaben:** BVB ja/nein, dazugehörige KBV-Regel-IDs, Version der Diagnoseliste, Warnungen (z. B. zweiter ICD erforderlich)
- **Technologie:** Python/FastAPI → als **PyInstaller .exe** für Windows gebaut
- **Integration:** Läuft lokal auf `127.0.0.1:8000` – keine Internet-Verbindung, keine Speicherung von Patientendaten

## Projektstatus
- ✅ Regel-Engine (JSON/CSV-Support, ICD-Matching, Alters- & Event-Constraints)
- ✅ FastAPI REST-Service
- ✅ UI mit Copy-Paste/Drag&Drop von ICD-Codes
- ✅ Windows-PyInstaller Build (`BVBChecker.exe`)
- ✅ Installationsbundle inkl. Startskripte, Installer (`install.ps1`) & README mit Platzhaltern
- ✅ Tests für Kernlogik
- ✅ Dokumentation: Installationshandbuch & QuickStart für Ärzt:innen

## Offene Punkte / To-Do
- [ ] **Regelliste vollständig prüfen:** CSV- oder JSON-Datei mit allen KBV-Einträgen befüllen
- [ ] **Validierung in der Praxis:** Pilotbetrieb → Ergebnisse gegen KBV-Liste prüfen
- [ ] **Optional:** Diagnosegruppen-Vorschlag bei falscher Gruppe
- [ ] **Optional:** Logging in `C:\ProgramData\BVBChecker\logs\`
- [ ] **Optional:** Signieren der EXE (Code-Signing)

## Übergabe an Praxis-IT
### Installation
1. Entpacken nach: `C:\Program Files\BVBChecker\`
2. **EXE ersetzen:** `BVBChecker.exe.PLACEHOLDER` durch echte `BVBChecker.exe` austauschen
3. Regelliste ablegen:
   - JSON: `app\rules\rules.json`
   - CSV:  `app\rules\diagnoseliste_extracted.csv`
4. Start über Batchskripte:
   - `scripts\start_bvbchecker_json.bat`
   - `scripts\start_bvbchecker_csv.bat`
5. Optional mit `install.ps1` (als Admin) Shortcut & Autostart einrichten

### Nutzung
- Browser öffnen → `http://127.0.0.1:8000`
- ICD-Codes einfügen → „Check BVB“ klicken
- Ergebnisanzeige direkt im Browser

### Pflege
- Bei neuer KBV-Diagnoseliste: `rules.json` oder `diagnoseliste_extracted.csv` austauschen
- `KBV_VERSION` in Startskript/Umgebungsvariablen anpassen

## Sicherheit
- Keine Speicherung von Patientennamen oder IDs
- Rein lokaler Betrieb, keine Datenübertragung
- Unsignierte EXE → Hash/Pfad in Applocker/Defender whitelisten

---

**Projekt-Übergabe:** Dieses Dokument fasst den Status, die offenen Punkte und die Installationsschritte zusammen.  
Ziel: Der BVBChecker kann sofort produktiv getestet werden und durch IT/Ärzte selbst gepflegt werden.
