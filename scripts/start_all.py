#!/usr/bin/env python3
from __future__ import annotations

import os
import socket
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib import error, request


@dataclass(frozen=True)
class ServiceSpec:
    name: str
    directory: Path
    port: int

    @property
    def health_url(self) -> str:
        return f"http://127.0.0.1:{self.port}/health"


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def service_specs(repo: Path | None = None) -> list[ServiceSpec]:
    root = repo or repo_root()
    return [
        ServiceSpec("document", root / "services" / "document-service", 8000),
        ServiceSpec("ingestion", root / "services" / "ingestion-service", 8001),
        ServiceSpec("embedding", root / "services" / "embedding-service", 8002),
        ServiceSpec("rag", root / "services" / "rag-service", 8003),
    ]


def resolve_python(service_dir: Path) -> Path:
    venv_python = service_dir / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        raise FileNotFoundError(
            f"Missing virtual environment for {service_dir.name}: {venv_python}\n"
            f"Create it with:\n"
            f"  cd {service_dir}\n"
            f"  py -m venv .venv"
        )
    return venv_python


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def stream_output(spec: ServiceSpec, pipe) -> None:
    if pipe is None:
        return
    try:
        for line in iter(pipe.readline, ""):
            if not line:
                break
            text = line.rstrip()
            if text:
                print(f"[{spec.name.upper()}] {text}", flush=True)
    except Exception:
        pass
    finally:
        try:
            pipe.close()
        except Exception:
            pass


def start_service(spec: ServiceSpec) -> subprocess.Popen[str]:
    if is_port_in_use(spec.port):
        raise RuntimeError(f"Port {spec.port} is already in use for {spec.name} service.")

    python_executable = resolve_python(spec.directory)
    command = [
        str(python_executable),
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(spec.port),
    ]
    process = subprocess.Popen(
        command,
        cwd=str(spec.directory),
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )
    thread = threading.Thread(target=stream_output, args=(spec, process.stdout), daemon=True)
    thread.start()
    return process


def wait_for_healthy(specs: Iterable[ServiceSpec], timeout_seconds: float = 30.0) -> bool:
    deadline = time.monotonic() + timeout_seconds
    remaining = list(specs)
    while time.monotonic() < deadline:
        next_remaining = []
        for spec in remaining:
            try:
                with request.urlopen(spec.health_url, timeout=2) as response:
                    if response.status == 200:
                        print(f"[{spec.name.upper()}] HEALTHY")
                        continue
            except (error.URLError, TimeoutError, OSError):
                pass
            next_remaining.append(spec)

        if not next_remaining:
            return True

        remaining = next_remaining
        time.sleep(1)

    for spec in remaining:
        print(f"[{spec.name.upper()}] NOT READY")
    return False


def shutdown_processes(processes: dict[str, subprocess.Popen[str]]) -> None:
    for name, process in list(processes.items()):
        if process.poll() is None:
            try:
                process.terminate()
            except Exception:
                pass
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                try:
                    process.kill()
                except Exception:
                    pass
                try:
                    process.wait(timeout=10)
                except Exception:
                    pass
            print(f"[{name.upper()}] stopped")


def main() -> int:
    root = repo_root()
    specs = service_specs(root)

    print("Starting EKA services...")
    print()

    processes: dict[str, subprocess.Popen[str]] = {}
    for spec in specs:
        print(f"[{spec.name.upper()}] starting on http://127.0.0.1:{spec.port}")
        try:
            process = start_service(spec)
        except FileNotFoundError as exc:
            print(f"[{spec.name.upper()}] ERROR: {exc}")
            shutdown_processes(processes)
            return 1
        except RuntimeError as exc:
            print(f"[{spec.name.upper()}] ERROR: {exc}")
            shutdown_processes(processes)
            return 1
        processes[spec.name] = process

    print()
    print("Waiting for services...")
    print()

    healthy = wait_for_healthy(specs)
    if not healthy:
        print("One or more services failed to become healthy within the startup window.")
        shutdown_processes(processes)
        return 1

    print()
    print("EKA services are running.")
    print()
    print("Document : http://127.0.0.1:8000")
    print("Ingestion : http://127.0.0.1:8001")
    print("Embedding : http://127.0.0.1:8002")
    print("RAG : http://127.0.0.1:8003")
    print("RAG Docs : http://127.0.0.1:8003/docs")
    print()
    print("Press Ctrl+C to stop all services.")

    try:
        while True:
            for spec in specs:
                process = processes[spec.name]
                if process.poll() is not None:
                    print(f"[{spec.name.upper()}] exited unexpectedly with code {process.returncode}")
                    shutdown_processes(processes)
                    return process.returncode or 1
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping EKA services...")
        shutdown_processes(processes)
        return 0
    finally:
        shutdown_processes(processes)


if __name__ == "__main__":
    raise SystemExit(main())
