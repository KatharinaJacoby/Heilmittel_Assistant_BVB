#!/usr/bin/env python3
"""
Build script for BVB Checker
Creates PyInstaller executable with all dependencies
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n=== {description} ===")
    print(f"Running: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Success!")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"Error: {result.stderr}")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    dirs = ["dist", "build", "data"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"Created directory: {dir_name}")

def check_files():
    """Check if all required files exist"""
    required_files = [
        "main.py",
        "rule_engine.py", 
        "requirements.txt",
        "bvb_checker.spec",
        "data/diagnoseliste_corrected.csv"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("Missing required files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        print("\nPlease create the missing files and run again.")
        sys.exit(1)
    
    print("All required files found.")

def install_dependencies():
    """Install Python dependencies"""
    run_command(
        "pip install -r requirements.txt",
        "Installing dependencies"
    )

def build_executable():
    """Build the executable using PyInstaller"""
    run_command(
        "pyinstaller bvb_checker.spec --clean --noconfirm",
        "Building executable"
    )

def create_release_package():
    """Create a release package with installer"""
    release_dir = Path("release")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # Copy executable
    exe_source = Path("dist/BVBChecker.exe")
    if exe_source.exists():
        shutil.copy(exe_source, release_dir / "BVBChecker.exe")
        print(f"Copied executable to release/")
    else:
        print("Warning: BVBChecker.exe not found in dist/")
    
    # Create README
    readme_content = """BVB Checker - Installation
========================

Für Arztpraxen zur schnellen Prüfung von Heilmittel-Verordnungsbedarf

INSTALLATION:
1. Doppelklick auf install.bat (als Administrator ausführen)
2. BVBChecker wird installiert nach: C:\\Program Files\\BVBChecker\\
3. Desktop-Verknüpfung wird erstellt

NUTZUNG:
1. Doppelklick auf Desktop-Symbol "BVB Checker"
2. Browser öffnet sich automatisch
3. ICD-Codes eingeben und prüfen

SYSTEMANFORDERUNGEN:
- Windows 10/11
- Keine weiteren Programme erforderlich
- Funktioniert ohne Internet

SUPPORT:
Bei Problemen wenden Sie sich an Ihr IT-Team.

Version: 1.0.0
Stand: Juli 2025
"""
    
    with open(release_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("Release package created in release/")

def main():
    """Main build process"""
    print("BVB Checker Build Script")
    print("=" * 40)
    
    try:
        check_files()
        create_directories()
        install_dependencies()
        build_executable()
        create_release_package()
        
        print("\n" + "=" * 40)
        print("Build completed successfully!")
        print("\nFiles created:")
        print("- dist/BVBChecker.exe (standalone executable)")
        print("- release/ (release package)")
        print("\nNext steps:")
        print("1. Test the executable: dist/BVBChecker.exe")
        print("2. Create installer with install_creator.bat")
        print("3. Deploy to target systems")
        
    except KeyboardInterrupt:
        print("\nBuild cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nBuild failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
