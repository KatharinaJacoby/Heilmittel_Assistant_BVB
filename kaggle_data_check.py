# === KAGGLE DATEN EXPORT & VALIDIERUNG ===
# Füge das in dein Kaggle Notebook ein

import pandas as pd
import os

# 1) DATEN EXPORTIEREN (für lokale Nutzung/Docker)
def export_for_production():
    # Deine aktuellen Daten laden
    df = pd.read_csv("/kaggle/input/heilmittel-bvb/diagnoseliste_extracted.csv")
    
    # Struktur analysieren
    print("=== DATASET ANALYSE ===")
    print(f"Zeilen: {len(df)}")
    print(f"Spalten: {list(df.columns)}")
    print(f"\nEligibility Verteilung:")
    print(df['eligibility'].value_counts() if 'eligibility' in df.columns else "Keine eligibility Spalte!")
    
    # Sample anzeigen
    print(f"\n=== SAMPLE DATEN ===")
    print(df.head(10))
    
    # Nach /kaggle/working exportieren (für Download)
    df.to_csv("/kaggle/working/diagnoseliste_for_docker.csv", index=False)
    print(f"\n✅ Exportiert nach: /kaggle/working/diagnoseliste_for_docker.csv")
    
    # Zusätzlich: JSON-Format für Rule Engine
    rules_data = []
    for _, row in df.iterrows():
        rule_dict = {
            "icd": row.get('icd', ''),
            "title": row.get('title', ''),
            "group": row.get('group', ''),
            "eligibility": row.get('eligibility', 'NONE'),
            "requires_second_icd": row.get('requires_second_icd', False),
            "second_icd_hint": row.get('second_icd_hint', ''),
            "acute_window_months": row.get('acute_window_months'),
            "notes": row.get('notes', ''),
            "source_url": row.get('source_url', ''),
            "source_version": row.get('source_version', '2025-01-01')
        }
        rules_data.append(rule_dict)
    
    import json
    with open("/kaggle/working/rules.json", "w", encoding="utf-8") as f:
        json.dump(rules_data, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON exportiert nach: /kaggle/working/rules.json")
    
    return df

# 2) DATENQUALITÄT PRÜFEN
def validate_bvb_data(df):
    print("\n=== BVB/LHB VALIDIERUNG ===")
    
    # Bekannte BVB-relevante ICDs (Beispiele)
    known_bvb_icds = [
        'I63.9',  # Hirninfarkt  
        'G35',    # Multiple Sklerose
        'M79.3',  # Panniculitis
        'F32.9',  # Depression
        'M25.9'   # Gelenkerkrankung
    ]
    
    print("Prüfung bekannter BVB-relevanter ICDs:")
    for icd in known_bvb_icds:
        if icd in df['icd'].values:
            eligibility = df[df['icd'] == icd]['eligibility'].iloc[0]
            print(f"  {icd}: {eligibility} ({'✅' if eligibility in ['BVB', 'LHB'] else '❌'})")
        else:
            print(f"  {icd}: NICHT GEFUNDEN")
    
    # Statistik
    if 'eligibility' in df.columns:
        total = len(df)
        none_count = (df['eligibility'] == 'NONE').sum()
        bvb_count = (df['eligibility'] == 'BVB').sum()
        lhb_count = (df['eligibility'] == 'LHB').sum()
        
        print(f"\n📊 VERTEILUNG:")
        print(f"  Gesamt: {total}")
        print(f"  NONE:   {none_count} ({none_count/total*100:.1f}%)")
        print(f"  BVB:    {bvb_count} ({bvb_count/total*100:.1f}%)")  
        print(f"  LHB:    {lhb_count} ({lhb_count/total*100:.1f}%)")
        
        if bvb_count + lhb_count == 0:
            print("\n🚨 KRITISCH: Keine BVB/LHB Qualifikationen gefunden!")
            print("   -> Prüfe die ursprüngliche Datenquelle")
            print("   -> Eventuell müssen Klassifikationen manuell hinzugefügt werden")

# 3) AUSFÜHREN
df = export_for_production()
validate_bvb_data(df)

print("\n=== NÄCHSTE SCHRITTE ===")
print("1. Download die exportierten Dateien aus /kaggle/working/")
print("2. Falls alle 'NONE': Originaldaten prüfen oder manuell BVB/LHB zuweisen")
print("3. Für Docker: diagnoseliste_for_docker.csv + rules.json verwenden")