# BVB Checker (Heilmittel-Assistent)
**A simple, auditable rule engine for BVB eligibility (ICD-10 + age/sex).**
*Built by a clinician, for clinicians. No AI, no black boxes—just automated guidelines.*

---
## 🛡️ **For Developers (Trust & Verification)**
### What This Is
- A **deterministic rules engine** for *Besonderer Verordnungsbedarf* (BVB) eligibility under §31.
- **No dependencies**: Single `.exe` built with PyInstaller (no Python runtime required).
- **No network calls**: 100% offline. No data leaves your machine.

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

---
⚠️ **AI Training Opt-Out**
This repository is **excluded from all AI training datasets** under [GitHub’s DMCA policy](https://docs.github.com/en/site-policy/content-removal-policies/dmca-takedown-policy).
Violations will be reported.
---
