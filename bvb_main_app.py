#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BVB Checker - Heilmittel Verordnungsbedarf Checker
Standalone FastAPI Application mit eingebetteter Diagnoseliste
"""

import os
import sys
from pathlib import Path
from datetime import date
from typing import List, Dict, Any
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import webbrowser
import threading
import time

# PyInstaller compatibility
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Import rule engine
sys.path.append(get_resource_path("."))
from rule_engine import RuleRow, PatientContext, evaluate_patient, normalize_icds

app = FastAPI(
    title="BVB Checker",
    description="Heilmittel Verordnungsbedarf Checker für Arztpraxen",
    version="1.0.0"
)

# CORS für lokale Nutzung
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Globale Variables
rules_dict: Dict[str, RuleRow] = {}

def load_rules():
    """Load and parse the embedded diagnosis list"""
    global rules_dict
    
    try:
        # Eingebettete CSV laden
        csv_path = get_resource_path("data/diagnoseliste_corrected.csv")
        
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Diagnoseliste nicht gefunden: {csv_path}")
            
        df = pd.read_csv(csv_path)
        
        # Data cleaning
        df = df.fillna("")
        df["requires_second_icd"] = df["requires_second_icd"].astype(str).str.lower().isin(["true", "1", "yes"])
        df["acute_window_months"] = pd.to_numeric(df["acute_window_months"], errors="coerce")
        
        # Build rules dictionary
        rules_dict = {}
        for _, row in df.iterrows():
            rule = RuleRow(
                icd=str(row["icd"]).upper().strip(),
                title=str(row.get("title", "")),
                group=str(row.get("group", "")),
                eligibility=str(row.get("eligibility", "NONE")).upper(),
                requires_second_icd=bool(row.get("requires_second_icd", False)),
                second_icd_hint=str(row.get("second_icd_hint", "")),
                acute_window_months=row.get("acute_window_months") if pd.notna(row.get("acute_window_months")) else None,
                notes=str(row.get("notes", "")),
                source_url=str(row.get("source_url", "")),
                source_version=str(row.get("source_version", "2025-07-01"))
            )
            rules_dict[rule.icd] = rule
            
        print(f"✅ Diagnoseliste geladen: {len(rules_dict)} ICDs")
        
        # Statistics
        stats = {"BVB": 0, "LHB": 0, "NONE": 0}
        for rule in rules_dict.values():
            stats[rule.eligibility] = stats.get(rule.eligibility, 0) + 1
        print(f"📊 Verteilung: BVB={stats['BVB']}, LHB={stats['LHB']}, NONE={stats['NONE']}")
        
    except Exception as e:
        print(f"❌ Fehler beim Laden der Diagnoseliste: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    load_rules()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Main UI page"""
    html_content = '''
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BVB Checker - Heilmittel Verordnungsbedarf</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; padding: 20px;
            }
            .container { 
                max-width: 800px; margin: 0 auto; 
                background: white; border-radius: 12px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.1); 
                overflow: hidden;
            }
            .header { 
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                color: white; padding: 30px; text-align: center; 
            }
            .header h1 { font-size: 2.2em; margin-bottom: 10px; }
            .header p { opacity: 0.9; font-size: 1.1em; }
            .content { padding: 40px; }
            .form-group { margin-bottom: 25px; }
            label { 
                display: block; margin-bottom: 8px; 
                font-weight: 600; color: #333; 
            }
            textarea, input { 
                width: 100%; padding: 12px; border: 2px solid #e1e5e9; 
                border-radius: 8px; font-size: 16px; 
                transition: border-color 0.3s ease;
            }
            textarea:focus, input:focus { 
                outline: none; border-color: #667eea; 
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            textarea { height: 120px; font-family: monospace; }
            .btn { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; border: none; padding: 15px 30px; 
                border-radius: 8px; font-size: 16px; font-weight: 600; 
                cursor: pointer; transition: transform 0.2s ease;
                width: 100%;
            }
            .btn:hover { transform: translateY(-2px); }
            .results { 
                margin-top: 30px; padding: 20px; 
                background: #f8f9fa; border-radius: 8px; 
                border-left: 4px solid #667eea;
            }
            .result-item { 
                margin: 15px 0; padding: 15px; 
                border-radius: 8px; border: 1px solid #e1e5e9;
                background: white;
            }
            .bvb { border-left: 4px solid #28a745; }
            .lhb { border-left: 4px solid #17a2b8; }
            .none { border-left: 4px solid #6c757d; }
            .summary { 
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                color: white; padding: 20px; border-radius: 8px; 
                margin-bottom: 20px; text-align: center;
            }
            .loading { display: none; text-align: center; margin: 20px 0; }
            .footer { 
                text-align: center; padding: 20px; 
                color: #6c757d; font-size: 14px; 
                border-top: 1px solid #e1e5e9;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏥 BVB Checker</h1>
                <p>Heilmittel Verordnungsbedarf - Schnell und einfach prüfen</p>
            </div>
            
            <div class="content">
                <form id="bvbForm">
                    <div class="form-group">
                        <label for="icds">ICD-10 Codes eingeben:</label>
                        <textarea id="icds" placeholder="Z.B.: I63.9, G35.0, R26.2&#10;Oder jeden Code in einer neuen Zeile"></textarea>
                        <small style="color: #6c757d;">Komma-getrennt oder zeilenweise eingeben</small>
                    </div>
                    
                    <div class="form-group">
                        <label for="acute_date">Datum des Akutereignisses (optional):</label>
                        <input type="date" id="acute_date">
                    </div>
                    
                    <button type="submit" class="btn">🔍 BVB/LHB prüfen</button>
                </form>
                
                <div class="loading" id="loading">
                    <p>🔄 Prüfe Verordnungsbedarf...</p>
                </div>
                
                <div id="results"></div>
            </div>
            
            <div class="footer">
                <p>BVB Checker v1.0 | Diagnoseliste Stand: Juli 2025 | Für Arztpraxen</p>
            </div>
        </div>

        <script>
            document.getElementById('bvbForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const loading = document.getElementById('loading');
                const results = document.getElementById('results');
                const icdsInput = document.getElementById('icds').value;
                const acuteDate = document.getElementById('acute_date').value;
                
                if (!icdsInput.trim()) {
                    alert('Bitte ICD-Codes eingeben');
                    return;
                }
                
                loading.style.display = 'block';
                results.innerHTML = '';
                
                try {
                    const response = await fetch('/check', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            icds: icdsInput,
                            acute_event_date: acuteDate || null
                        })
                    });
                    
                    const data = await response.json();
                    
                    loading.style.display = 'none';
                    displayResults(data);
                    
                } catch (error) {
                    loading.style.display = 'none';
                    results.innerHTML = '<div class="result-item" style="border-left-color: #dc3545;">❌ Fehler: ' + error.message + '</div>';
                }
            });
            
            function displayResults(data) {
                const results = document.getElementById('results');
                
                const bvbCount = data.results.filter(r => r.kind === 'BVB').length;
                const lhbCount = data.results.filter(r => r.kind === 'LHB').length;
                
                let html = '<div class="results">';
                
                // Summary
                if (bvbCount > 0 || lhbCount > 0) {
                    html += '<div class="summary">';
                    html += '<h3>✅ Verordnungsbedarf qualifiziert!</h3>';
                    if (bvbCount > 0) html += '<p><strong>BVB:</strong> ' + bvbCount + ' Code(s)</p>';
                    if (lhbCount > 0) html += '<p><strong>LHB:</strong> ' + lhbCount + ' Code(s)</p>';
                    html += '</div>';
                } else {
                    html += '<div style="background: #6c757d; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center;">';
                    html += '<h3>ℹ️ Kein besonderer Verordnungsbedarf</h3>';
                    html += '<p>Normale Heilmittelverordnung möglich</p>';
                    html += '</div>';
                }
                
                // Individual results
                data.results.forEach(result => {
                    const className = result.kind ? result.kind.toLowerCase() : 'none';
                    const badge = result.kind === 'BVB' ? '🟢 BVB' : result.kind === 'LHB' ? '🔵 LHB' : '⚪ NONE';
                    
                    html += '<div class="result-item ' + className + '">';
                    html += '<h4>' + badge + ' ' + result.icd + '</h4>';
                    html += '<p>' + result.explain + '</p>';
                    if (result.missing.length > 0) {
                        html += '<p style="color: #dc3545;"><strong>Fehlend:</strong> ' + result.missing.join(', ') + '</p>';
                    }
                    html += '</div>';
                });
                
                html += '</div>';
                results.innerHTML = html;
            }
        </script>
    </body>
    </html>
    '''
    return HTMLResponse(content=html_content)

@app.post("/check")
async def check_bvb(request: Request):
    """Check BVB/LHB eligibility for given ICD codes"""
    try:
        data = await request.json()
        icds_input = data.get("icds", "")
        acute_event_date_str = data.get("acute_event_date")
        
        # Parse ICDs
        patient_icds = normalize_icds(icds_input)
        
        if not patient_icds:
            raise HTTPException(status_code=400, detail="Keine gültigen ICD-Codes eingegeben")
        
        # Parse acute event date
        acute_event_date = None
        if acute_event_date_str:
            try:
                acute_event_date = date.fromisoformat(acute_event_date_str)
            except ValueError:
                pass
        
        # Create patient context
        ctx = PatientContext(
            icds=patient_icds,
            acute_event_date=acute_event_date
        )
        
        # Evaluate
        results = evaluate_patient(ctx, rules_dict, today=date.today())
        
        # Format response
        response_data = {
            "icds_input": patient_icds,
            "results": [
                {
                    "icd": r.icd,
                    "eligible": r.eligible,
                    "kind": r.kind,
                    "explain": r.explain,
                    "conditions_met": r.conditions_met,
                    "missing": r.missing,
                    "source_version": r.source_version
                }
                for r in results
            ],
            "summary": {
                "bvb_count": len([r for r in results if r.kind == "BVB"]),
                "lhb_count": len([r for r in results if r.kind == "LHB"]),
                "total_eligible": len([r for r in results if r.eligible])
            }
        }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    stats = {"BVB": 0, "LHB": 0, "NONE": 0}
    for rule in rules_dict.values():
        stats[rule.eligibility] = stats.get(rule.eligibility, 0) + 1
    
    return {
        "status": "healthy",
        "rules_loaded": len(rules_dict),
        "distribution": stats,
        "version": "1.0.0"
    }

def open_browser():
    """Open browser after short delay"""
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8000")

def run_server():
    """Run the FastAPI server"""
    # Start browser in background
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run server
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000, 
        log_level="info"
    )

if __name__ == "__main__":
    print("🏥 BVB Checker wird gestartet...")
    print("📂 Lade Diagnoseliste...")
    
    try:
        load_rules()
        print("🌐 Server startet auf http://127.0.0.1:8000")
        print("🔍 Browser öffnet automatisch...")
        run_server()
    except Exception as e:
        print(f"❌ Fehler beim Start: {e}")
        input("Drücken Sie Enter zum Beenden...")
