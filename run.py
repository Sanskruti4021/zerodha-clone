"""
Master Launcher for the Zerodha Clone Stock Prediction Platform.

Usage:
    python run.py

Starts all required services in dependency order:
    1. ML FastAPI service  (port 8000)
    2. Express backend     (port 3002)
    3. Dashboard           (port 3001)
    4. Frontend            (port 3000)

Press Ctrl+C to shut down all services.
"""

import os
import sys
import signal
import subprocess
import time
import platform
from pathlib import Path


# ─── Configuration ───────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent

ML_SERVICE_DIR = PROJECT_ROOT / "ml-service"
BACKEND_DIR = PROJECT_ROOT / "backend"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

IS_WINDOWS = platform.system() == "Windows"


# ─── Process Management ─────────────────────────────────────

processes = []
shutting_down = False


def find_python():
    """Find the Python executable, preferring the ML service venv."""
    venv_python = ML_SERVICE_DIR / ".venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return str(venv_python)

    # Fallback: Unix venv path
    venv_python_unix = ML_SERVICE_DIR / ".venv" / "bin" / "python"
    if venv_python_unix.exists():
        return str(venv_python_unix)

    # Fallback: system Python
    return sys.executable


def find_npm():
    """Find npm, preferring npm.cmd on Windows."""
    if IS_WINDOWS:
        return "npm.cmd"
    return "npm"


def start_process(name, command, cwd, env=None):
    """Start a subprocess and track it."""
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    print(f"  Starting {name}...")

    try:
        proc = subprocess.Popen(
            command,
            cwd=str(cwd),
            env=merged_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            # On Windows, CREATE_NEW_PROCESS_GROUP allows proper signal handling
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if IS_WINDOWS else 0,
        )
        processes.append((name, proc))
        print(f"  ✓ {name} started (PID {proc.pid})")
        return proc
    except FileNotFoundError as e:
        print(f"  ✗ {name} failed to start: {e}")
        return None
    except Exception as e:
        print(f"  ✗ {name} failed to start: {e}")
        return None


def stream_output(proc, name):
    """Read one line of output from the process (non-blocking style)."""
    if proc and proc.stdout:
        try:
            line = proc.stdout.readline()
            if line:
                text = line.decode("utf-8", errors="replace").rstrip()
                print(f"  [{name}] {text}")
                return True
        except Exception:
            pass
    return False


def shutdown_all():
    """Terminate all child processes gracefully."""
    global shutting_down
    if shutting_down:
        return
    shutting_down = True

    print("\n" + "=" * 50)
    print("Shutting down all services...")
    print("=" * 50)

    for name, proc in reversed(processes):
        if proc and proc.poll() is None:
            print(f"  Stopping {name} (PID {proc.pid})...")
            try:
                if IS_WINDOWS:
                    # On Windows, terminate the process tree
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                        capture_output=True,
                    )
                else:
                    proc.terminate()
            except Exception as e:
                print(f"  Warning: could not stop {name}: {e}")

    # Wait briefly for processes to exit
    time.sleep(1)

    for name, proc in processes:
        if proc and proc.poll() is None:
            try:
                proc.kill()
            except Exception:
                pass

    print("All services stopped.")


def signal_handler(signum, frame):
    """Handle Ctrl+C."""
    shutdown_all()
    sys.exit(0)


# ─── Pre-flight Checks ──────────────────────────────────────

def preflight_checks():
    """Verify that required directories and files exist."""
    checks_passed = True

    # Check ML service
    if not (ML_SERVICE_DIR / "src" / "app.py").exists():
        print("  ✗ ML service app.py not found")
        checks_passed = False

    if not (ML_SERVICE_DIR / ".venv").exists():
        print("  ⚠ ML service virtual environment (.venv) not found")
        print("    Create it with: cd ml-service && python -m venv .venv")
        checks_passed = False

    # Check that models exist
    if not (ML_SERVICE_DIR / "models" / "random_forest.joblib").exists():
        print("  ⚠ ML models not found. Run training first:")
        print("    cd ml-service && .venv/Scripts/python src/train_models.py")

    # Check backend
    if not (BACKEND_DIR / "index.js").exists():
        print("  ✗ Backend index.js not found")
        checks_passed = False

    if not (BACKEND_DIR / "node_modules").exists():
        print("  ⚠ Backend node_modules not found. Run: cd backend && npm install")
        checks_passed = False

    # Check backend .env
    if not (BACKEND_DIR / ".env").exists():
        print("  ⚠ Backend .env not found. Copy from .env.example and configure.")

    # Check dashboard
    if not (DASHBOARD_DIR / "package.json").exists():
        print("  ✗ Dashboard package.json not found")
        checks_passed = False

    if not (DASHBOARD_DIR / "node_modules").exists():
        print("  ⚠ Dashboard node_modules not found. Run: cd dashboard && npm install")
        checks_passed = False

    # Check frontend
    if not (FRONTEND_DIR / "package.json").exists():
        print("  ✗ Frontend package.json not found")
        checks_passed = False

    if not (FRONTEND_DIR / "node_modules").exists():
        print("  ⚠ Frontend node_modules not found. Run: cd frontend && npm install")
        checks_passed = False

    return checks_passed


# ─── Wait for Service ────────────────────────────────────────

def wait_for_service(proc, name, keyword, timeout=30):
    """Wait until a keyword appears in the process output, or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        if proc.poll() is not None:
            # Process exited unexpectedly — drain output for diagnostics
            remaining = proc.stdout.read().decode("utf-8", errors="replace")
            if remaining:
                for line in remaining.split("\n"):
                    if line.strip():
                        print(f"  [{name}] {line.rstrip()}")
            print(f"  ✗ {name} exited unexpectedly (code {proc.returncode})")
            return False

        if proc.stdout:
            line = proc.stdout.readline()
            if line:
                text = line.decode("utf-8", errors="replace").rstrip()
                print(f"  [{name}] {text}")
                if keyword.lower() in text.lower():
                    return True

    print(f"  ⚠ {name} did not start within {timeout}s (may still be starting)")
    return True  # Don't block — it might just be slow


# ─── Main ────────────────────────────────────────────────────

def main():
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, signal_handler)

    print("=" * 50)
    print("Zerodha Clone — Stock Prediction Platform")
    print("=" * 50)
    print()

    # Pre-flight checks
    print("Pre-flight checks:")
    if not preflight_checks():
        print("\nSome critical checks failed. Please fix the issues above.")
        sys.exit(1)
    print("  ✓ Pre-flight checks passed")
    print()

    python_exe = find_python()
    npm_cmd = find_npm()

    print(f"Python: {python_exe}")
    print(f"NPM:    {npm_cmd}")
    print()

    # ── 1. Start ML Service ──

    print("─" * 50)
    print("1. ML FastAPI Service (port 8000)")
    print("─" * 50)

    ml_proc = start_process(
        "ML Service",
        [
            python_exe, "-m", "uvicorn",
            "src.app:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--log-level", "info",
        ],
        cwd=ML_SERVICE_DIR,
    )

    if ml_proc:
        wait_for_service(ml_proc, "ML Service", "uvicorn running", timeout=30)
    print()

    # ── 2. Start Backend ──

    print("─" * 50)
    print("2. Express Backend (port 3002)")
    print("─" * 50)

    backend_proc = start_process(
        "Backend",
        [npm_cmd, "start"],
        cwd=BACKEND_DIR,
    )

    if backend_proc:
        wait_for_service(backend_proc, "Backend", "App started", timeout=20)
    print()

    # ── 3. Start Dashboard ──

    print("─" * 50)
    print("3. Dashboard (port 3001)")
    print("─" * 50)

    dashboard_env = {"PORT": "3001", "BROWSER": "none"}
    dashboard_proc = start_process(
        "Dashboard",
        [npm_cmd, "start"],
        cwd=DASHBOARD_DIR,
        env=dashboard_env,
    )

    if dashboard_proc:
        wait_for_service(dashboard_proc, "Dashboard", "compiled", timeout=60)
    print()

    # ── 4. Start Frontend ──

    print("─" * 50)
    print("4. Frontend (port 3000)")
    print("─" * 50)

    frontend_env = {"PORT": "3000", "BROWSER": "none"}
    frontend_proc = start_process(
        "Frontend",
        [npm_cmd, "start"],
        cwd=FRONTEND_DIR,
        env=frontend_env,
    )

    if frontend_proc:
        wait_for_service(frontend_proc, "Frontend", "compiled", timeout=60)
    print()

    # ── Summary ──

    print("=" * 50)
    print("ALL SERVICES STARTED")
    print("=" * 50)
    print()
    print("  Frontend:    http://localhost:3000")
    print("  Dashboard:   http://localhost:3001")
    print("  Backend:     http://localhost:3002")
    print("  ML Service:  http://localhost:8000")
    print("  ML Health:   http://localhost:8000/health")
    print()
    print("Press Ctrl+C to shut down all services.")
    print("=" * 50)
    print()

    # Keep running and forward output
    try:
        while True:
            any_output = False
            all_dead = True

            for name, proc in processes:
                if proc and proc.poll() is None:
                    all_dead = False
                    if stream_output(proc, name):
                        any_output = True
                elif proc and proc.poll() is not None:
                    # Check if it just died
                    pass

            if all_dead:
                print("\nAll services have stopped.")
                break

            if not any_output:
                time.sleep(0.2)

    except KeyboardInterrupt:
        pass
    finally:
        shutdown_all()


if __name__ == "__main__":
    main()
