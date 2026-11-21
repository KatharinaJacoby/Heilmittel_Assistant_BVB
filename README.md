# BVB Checker (Heilmittel-Assistent)
**A simple, auditable rule engine for BVB eligibility (ICD-10 + age/sex).**
---
## 🛡️ **For Developers (Trust & Verification)**
### What This Is
- A **deterministic rules engine** for *Besonderer Verordnungsbedarf* (BVB) eligibility under §31.
- **No dependencies**: Single `.exe` built with PyInstaller (no Python runtime required).

### How to Verify It’s Safe
1. **Check the rules**:
   All logic is defined in [`rules/rules.json`](rules/rules.json).
   Example:
   ```json
   {
     "E11.9": {  // Type 2 diabetes
       "min_age": 75,
       "sex": ["female"],
       "reason": "§31 Abs. 1",
       "source": "https://www.g-ba.de/richtlinien/34/#31"
     }
