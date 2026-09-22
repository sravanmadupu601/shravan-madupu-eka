from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts.start_all import repo_root, resolve_python, service_specs, shutdown_processes


def test_repo_root_resolution():
    root = repo_root()
    assert root.exists()
    assert (root / "services").exists()
    assert (root / "scripts").exists()


def test_service_specs_use_expected_ports_and_directories():
    root = Path("/tmp/eka-root")
    specs = service_specs(root)

    assert [spec.name for spec in specs] == ["document", "ingestion", "embedding"]
    assert [spec.port for spec in specs] == [8000, 8001, 8002]
    assert [str(spec.directory) for spec in specs] == [
        str(root / "services" / "document-service"),
        str(root / "services" / "ingestion-service"),
        str(root / "services" / "embedding-service"),
    ]


def test_resolve_python_prefers_local_venv(tmp_path):
    service_dir = tmp_path / "service"
    venv_dir = service_dir / ".venv" / "Scripts"
    venv_dir.mkdir(parents=True)
    expected = venv_dir / "python.exe"
    expected.write_text("python", encoding="utf-8")

    assert resolve_python(service_dir) == expected


def test_shutdown_processes_terminates_children():
    process = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(30)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    shutdown_processes({"demo": process})
    assert process.poll() is not None
