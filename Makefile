
.PHONY: run test build

# Starte den lokalen Server (Entwicklung)
run:
	uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Tests mit pytest ausführen
test:
	pytest -q --disable-warnings

# Windows-EXE mit PyInstaller bauen
build:
	pyinstaller --noconfirm --onefile \\
	  --add-data "app/templates;app/templates" \\
	  --add-data "app/static;app/static" \\
	  --add-data "app/rules;app/rules" \\
	  -n BVBChecker.exe run_server.py
