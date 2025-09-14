
# BVBChecker – Review-Leitfaden für .NET-Dev

## Bekannte Lücken (nicht bearbeiten, nur zur Info)
- Regel-Liste noch unvollständig / nicht final gegen KBV geprüft
- Diagnosegruppen-Vorschläge fehlen
- Logging-Verzeichnis / Rotation fehlt
- Code-Signing fehlt

## Fokus-Fragen
- **API-Design & Versionierung**: Sind Endpunkte, Payloads und Fehlermeldungen zukunftssicher?
- **Regel-Engine Struktur**: Ist JSON/CSV-Schema verständlich für langfristige Pflege durch Praxis-IT?
- **Packaging & Distribution**: Empfehlungen für Windows-Installer, Rechte, Update-Flow?
- **Teststrategie**: Reichen aktuelle Tests? Welche Edge Cases ergänzen?
- **Lokale Sicherheit**: Windows-spezifische Härtung (Pfade, Execution Policy, Integrität)?

## 20-Minuten Smoke-Test
1. Service starten: `make run` → Browser öffnen `http://127.0.0.1:8000`
2. ICD-Codes einfügen → prüfen, ob BVB-Ergebnis korrekt erscheint
3. `rules.json` vs. `diagnoseliste_extracted.csv` tauschen → Service neu starten → prüfen
4. `make test` → Tests sollten grün sein
