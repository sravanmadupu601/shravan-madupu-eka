from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from scripts import start_all
from scripts.start_all import repo_root, resolve_python, service_specs, shutdown_processes


def test_repo_root_resolution():
    root = repo_root()
    assert root.exists()
    assert (root / "services").exists()
    assert (root / "scripts").exists()


def test_service_specs_use_expected_ports_and_directories():
    root = Path("/tmp/eka-root")
    specs = service_specs(root)

<<<<<<< HEAD
    assert [spec.name for spec in specs] == ["document", "ingestion", "embedding", "rag"]
    assert [spec.port for spec in specs] == [8000, 8001, 8002, 8003]
=======
    assert [spec.name for spec in specs] == ["document", "ingestion", "embedding", "agent"]
    assert [spec.port for spec in specs] == [8000, 8001, 8002, 8004]
>>>>>>> 66bc4670a8a4d8cfce9f265229b4c468999a2711
    assert [str(spec.directory) for spec in specs] == [
        str(root / "services" / "document-service"),
        str(root / "services" / "ingestion-service"),
        str(root / "services" / "embedding-service"),
<<<<<<< HEAD
        str(root / "services" / "rag-service"),
=======
        str(root / "services" / "agent-service"),
>>>>>>> 66bc4670a8a4d8cfce9f265229b4c468999a2711
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


def test_missing_service_venv_stops_services_already_started(monkeypatch):
    started = []
    specs = [
        start_all.ServiceSpec("document", Path("document-service"), 8000),
        start_all.ServiceSpec("agent", Path("agent-service"), 8004),
    ]

    def fake_start_service(spec):
        if spec.name == "agent":
            raise FileNotFoundError("missing agent venv")
        process = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        started.append(process)
        return process

    monkeypatch.setattr(start_all, "repo_root", lambda: Path("."))
    monkeypatch.setattr(start_all, "service_specs", lambda _root: specs)
    monkeypatch.setattr(start_all, "start_service", fake_start_service)

    assert start_all.main() == 1
    assert len(started) == 1
    assert started[0].poll() is not None
