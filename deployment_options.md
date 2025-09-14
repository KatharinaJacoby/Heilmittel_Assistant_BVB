# BVB Assistant - Deployment-Optionen mit Diagnoseliste

## 🎯 **Empfehlung: Hybrid-Ansatz**

Liefere **beide Varianten** - das gibt dem Empfänger-Team maximale Flexibilität:

### Option A: PyInstaller + Daten (für Standard-Praxen)
```
BVBChecker_Release/
├── BVBChecker.exe
├── data/
│   ├── diagnoseliste_extracted.csv    ← AUS KAGGLE!
│   ├── rules.json                     ← Konvertierte Version
│   └── metadata.json                  ← Version, Datum etc.
├── scripts/
│   ├── start_bvbchecker.bat
│   └── install.ps1
└── README.md
```

### Option B: Docker (für Tech-affine Praxen)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Echte Diagnoseliste einbetten
COPY data/diagnoseliste_extracted.csv ./data/
COPY src/ ./src/

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📋 **To-Do für dich vor Übergabe:**

### 1. Kaggle-Dataset extrahieren
- [ ] CSV aus deinem Kaggle-Notebook exportieren
- [ ] Sicherstellen, dass BVB/LHB-Codes korrekt klassifiziert sind
- [ ] Quick-Test: Bekannte Schlaganfall-ICDs (I63.x) sollten qualifizieren

### 2. Docker-Setup hinzufügen
```yaml
# docker-compose.yml
version: '3.8'
services:
  bvb-checker:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data:ro  # Read-only für Sicherheit
    environment:
      - KBV_VERSION=2025-01-01
      - LOG_LEVEL=INFO
```

### 3. Datenvalidierung einbauen
```python
# Als Startup-Check in main.py
def validate_rule_data():
    total = len(rules)
    bvb_count = sum(1 for r in rules.values() if r.eligibility == "BVB") 
    lhb_count = sum(1 for r in rules.values() if r.eligibility == "LHB")
    
    if bvb_count + lhb_count < total * 0.1:  # Weniger als 10% qualifiziert? Verdächtig!
        raise ValueError(f"Verdächtige Regeldaten: Nur {bvb_count + lhb_count}/{total} qualifizieren")
```

## 🚀 **Konkrete Übergabe-Strategie**

### Sofort liefern:
1. **Docker-Version mit echter Diagnoseliste**
   - Läuft überall konsistent
   - Einfache Updates via `docker pull`
   - Professioneller für IT-Teams

2. **PyInstaller-Version mit Daten**  
   - Wie geplant, aber mit echten Daten
   - Für Praxen ohne Docker-Know-how

### In der Übergabe-Email erwähnen:
> "Achtung: Die bisherigen Dummy-Daten wurden durch die echte KBV-Heilmittel-Diagnoseliste ersetzt. 
> System jetzt produktionsbereit für Pilotbetrieb!"

## 🎁 **Bonus-Punkte**

### Daten-Update-Mechanismus
```bash
# update_data.sh für Docker
#!/bin/bash
docker run --rm -v $(pwd)/data:/app/data bvb-checker:latest \
  python scripts/validate_and_update_rules.py
```

### Health-Check-Endpoint
```python
@app.get("/health")
def health_check():
    rule_stats = {
        "total_rules": len(rules),
        "bvb_rules": sum(1 for r in rules.values() if r.eligibility == "BVB"),
        "lhb_rules": sum(1 for r in rules.values() if r.eligibility == "LHB"),
        "data_version": os.environ.get("KBV_VERSION", "unknown")
    }
    return {"status": "healthy", "rules": rule_stats}
```

---

**Bottom Line:** Docker + echte Daten = professionelle Übergabe! 🐳✨