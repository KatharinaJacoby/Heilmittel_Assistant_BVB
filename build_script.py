import argparse
from pathlib import Path
import PyInstaller.__main__ as pymain

print("BVB Checker Build Script\n" + "="*40)

ROOT = Path(__file__).parent.resolve()
ENTRYPOINT = ROOT / "bvb_main_app.py"                 # ← Startskript DEINES Repos
CSV_FILE  = ROOT / "diagnoseliste_extracted.csv"      # ← CSV im Repo-Root
RUNTIME_HOOK = ROOT / "pyi_runtime_hook_chdir.py"     # ← Pfade im Onefile-Build fixen

def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group()
    g.add_argument("--onefile", action="store_true", help="Single EXE (default)")
    g.add_argument("--onefolder", action="store_true", help="Folder build")
    p.add_argument("--name", default="BVBChecker")
    p.add_argument("--noconsole", action="store_true")
    args = p.parse_args()

    onefile = True if (args.onefile or not args.onefolder) else False

    missing = []
    if not ENTRYPOINT.exists(): missing.append(str(ENTRYPOINT.name))
    # requirements installiert der Workflow bereits aus requirements_txt.txt
    if CSV_FILE and not CSV_FILE.exists():
        print(f"Warn: CSV nicht gefunden: {CSV_FILE} (baue trotzdem weiter)")

    if missing:
        print("Fehlende Pflichtdateien:\n  - " + "\n  - ".join(missing))
        raise SystemExit(1)

    py_args = [
        str(ENTRYPOINT),
        f"--name={args.name}",
        "--noconfirm",
        "--clean",
        f"--runtime-hook={RUNTIME_HOOK}",
        "--hidden-import=uvicorn",
        "--hidden-import=uvicorn.lifespan.on",
        "--hidden-import=uvicorn.logging",
        ("--noconsole" if args.noconsole else "--console"),
    ]
    if onefile:
        py_args.append("--onefile")
    if CSV_FILE.exists():
        # CSV neben die EXE legen
        py_args.append(f"--add-data={CSV_FILE};.")

    print("PyInstaller args:")
    for a in py_args:
        print(" ", a)

    pymain.run(py_args)

    dist = ROOT / "dist"
    exe = dist / (f"{args.name}.exe" if onefile else f"{args.name}/{args.name}.exe")
    print("\nBuild fertig:", exe)

if __name__ == "__main__":
    main()
