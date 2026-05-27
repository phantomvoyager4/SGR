import sys
import time
from pathlib import Path
import subprocess
import webbrowser
import shutil

def script():
    project_root = Path(__file__).resolve().parent.parent        
    src_dir = project_root / "src"
    backend = src_dir / "backend"
    frontend = src_dir / "frontend"
    # Use sys.executable to securely call global uvicorn module
    subprocess.Popen([sys.executable, '-m', 'uvicorn', 'main:app', '--reload', '--port', '8000'], cwd=backend)
    front_dir = project_root / "src" / "frontend"
    npm_path = shutil.which("npm")
    if npm_path:
        subprocess.Popen([npm_path, 'run', 'start'], cwd=front_dir)

    time.sleep(1)
    webbrowser.open("http://localhost:3000/")

if __name__ == "__main__":
    script()