"""External programs: kicad-cli, ngspice."""

import os
import shutil
import subprocess
from pathlib import Path

KICAD_CLI_DEFAULT = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/KiCad/10.0/bin/kicad-cli.exe"


def find_kicad_cli() -> str:
    for candidate in (os.environ.get("KICAD_CLI"), shutil.which("kicad-cli"), KICAD_CLI_DEFAULT):
        if candidate and Path(candidate).is_file():
            return str(candidate)
    raise FileNotFoundError("kicad-cli not found: set KICAD_CLI or add it to PATH")


def find_ngspice() -> str:
    for candidate in (os.environ.get("NGSPICE"), "ngspice_con", "ngspice"):
        if candidate and (path := shutil.which(candidate)):
            return path
    raise FileNotFoundError("ngspice not found: set NGSPICE or add it to PATH")


def run_kicad_cli(cli: str, *args: str) -> None:
    result = subprocess.run([cli, *args], capture_output=True, text=True)
    # kicad-cli reports model errors to stderr but still exits 0 - treat any stderr as failure.
    if result.returncode != 0 or result.stderr.strip():
        raise RuntimeError(f"kicad-cli {' '.join(args)}\n{result.stdout}{result.stderr}")
