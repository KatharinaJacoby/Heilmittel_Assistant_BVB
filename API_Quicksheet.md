
# BVBChecker – API Quicksheet

## Endpunkte

### `GET /health`
Antwort:
```json
{ "status": "ok", "app": "BVBChecker" }
```

### `GET /version`
Antwort:
```json
{ "app": "BVBChecker", "kbv_version": "2025-01-01" }
```

### `POST /check`
Anfrage (Beispiel):
```json
{
  "patient": {
    "icd10_codes": ["G81.1","I69.3"],
    "age": 64,
    "sex": "m",
    "diagnosegruppe": "EX3",
    "heilmittelbereich": "PT"
  }
}
```

Antwort (Beispiel):
```json
{
  "eligible": true,
  "matched": [
    {
      "rule_id": "KBV-BVB-PT-0001",
      "title": "Hemiparese/Monoparese nach Schlaganfall",
      "diagnosegruppe": "EX3",
      "heilmittelbereich": "PT",
      "evidence": "KBV Diagnoseliste 2025-01, PT/EX3"
    }
  ],
  "kbv_version_date": "2025-01-01",
  "missing_fields": [],
  "warnings": []
}
```

### Beispielaufruf (curl)
```bash
curl -X POST http://127.0.0.1:8000/check \
  -H "Content-Type: application/json" \
  -d @example_patient.json
```
