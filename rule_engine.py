#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rule Engine für BVB Checker
Enthält die Logik zur Bewertung von ICD-Codes für Heilmittel-Verordnungsbedarf
"""
%%writefile rule_engine.py
from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Dict

# ----------------- Data models -----------------

@dataclass
class RuleRow:
    icd: str
    title: str
    group: str
    eligibility: str                 # "BVB" | "LHB" | "NONE"
    requires_second_icd: bool
    second_icd_hint: str
    acute_window_months: Optional[int]
    notes: str
    source_url: str
    source_version: str

@dataclass
class PatientContext:
    icds: List[str]
    acute_event_date: Optional[date] = None

@dataclass
class EligibilityResult:
    icd: str
    eligible: bool
    kind: Optional[str]              # "BVB" | "LHB" | None
    conditions_met: Dict[str, bool]
    missing: List[str]
    explain: str
    source_version: str

# ----------------- Helpers -----------------

def months_between(d1: date, d2: date) -> int:
    """Whole months between d1 (later) and d2 (earlier)."""
    return (d1.year - d2.year) * 12 + (d1.month - d2.month) - (1 if d1.day < d2.day else 0)

# ----------------- Core rule evaluation -----------------

def check_rule(rule: RuleRow, ctx: PatientContext, today: date) -> EligibilityResult:
    conds: Dict[str, bool] = {}
    missing: List[str] = []

    # Is this ICD even listed for BVB/LHB?
    conds["is_listed"] = rule.eligibility in {"BVB", "LHB"}

    # Second ICD requirement
    if rule.requires_second_icd:
        conds["second_icd_present"] = any(i != rule.icd for i in ctx.icds)
        if not conds["second_icd_present"]:
            hint = rule.second_icd_hint or "siehe Liste"
            missing.append(f"Zweiter ICD erforderlich ({hint})")

    # Acute-event window requirement
    if rule.acute_window_months is not None:
        if ctx.acute_event_date:
            conds["acute_window_ok"] = months_between(today, ctx.acute_event_date) <= rule.acute_window_months
            if not conds["acute_window_ok"]:
                missing.append(f"Frist nach Akutereignis ≤ {rule.acute_window_months} Monate")
        else:
            conds["acute_window_ok"] = False
            missing.append("Datum des Akutereignisses erforderlich")

    eligible = all(conds.values()) and rule.eligibility in {"BVB", "LHB"}

    # Build robust, NaN-safe explanation
    title = (rule.title or "").strip()
    group = (rule.group or "").strip()
    notes = (rule.notes or "").strip()

    explain = f"{rule.icd} – {title or 'Diagnose'}: "
    explain += "qualifiziert" if eligible else "qualifiziert nicht"
    if rule.eligibility in {"BVB", "LHB"}:
        explain += f" für {rule.eligibility}"
    if group:
        explain += f" (Diagnosegruppe {group})"
    if notes:
        explain += f". {notes}"

    return EligibilityResult(
        icd=rule.icd,
        eligible=eligible,
        kind=rule.eligibility if eligible else None,
        conditions_met=conds,
        missing=missing,
        explain=explain.strip(),
        source_version=rule.source_version,
    )

def evaluate_patient(ctx: PatientContext, rules_by_icd: Dict[str, RuleRow], today: date) -> List[EligibilityResult]:
    results: List[EligibilityResult] = []
    for icd in ctx.icds:
        rule = rules_by_icd.get(icd)
        if rule:
            results.append(check_rule(rule, ctx, today))
        else:
            # ICD not found in rules - aus Version 1 übernehmen
            results.append(EligibilityResult(
                icd=icd,
                eligible=False,
                kind=None,
                conditions_met={"is_listed": False},
                missing=["ICD nicht in Diagnoseliste gefunden"],
                explain=f"{icd} - ICD nicht in der Heilmittel-Diagnoseliste",
                source_version="unknown"
            ))
    return results

# ----------------- Convenience utilities (UI/notebook) -----------------

def normalize_icds(s: str) -> List[str]:
    """Split free-text into normalized ICD codes."""
    import re
    toks = re.split(r"[,\s;]+", (s or "").strip())
    return [t.upper() for t in toks if t]

def icd_neighbors(icd: str, all_icds: List[str], k: int = 20) -> List[str]:
    """Return up to k ICDs in the same 'family' stem, e.g., R26.*."""
    if len(icd) >= 4 and icd[3] == ".":
        stem = icd[:4]
    else:
        stem = icd[:3] + "."
    return [x for x in sorted(all_icds) if x.startswith(stem)][:k]
