"""
Launcher aplikasi JEJAK TUMBUH — Posyandu Digital
Cara menjalankan:
    python run.py
atau:
    python app.py
"""
import sys
import subprocess
from pathlib import Path

if __name__ == "__main__":
    app_dir = Path(__file__).resolve().parent
    subprocess.run([sys.executable, str(app_dir / "app.py")])
