"""Build derived artifacts from sources: schematic images and SPICE netlists.

schematics/<name>.kicad_sch -> build/schematics/<name>.svg   picture
                            -> build/netlists/<name>.cir   SPICE netlist (for simulation)
                            -> build/netlists/<name>.xml   KiCad netlist (components, fields, nets)
"""

import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
SCHEMATICS = ROOT / "schematics"
BUILD = ROOT / "build"
KICAD_CLI_DEFAULT = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/KiCad/10.0/bin/kicad-cli.exe"


def find_kicad_cli() -> str:
    for candidate in (os.environ.get("KICAD_CLI"), shutil.which("kicad-cli"), KICAD_CLI_DEFAULT):
        if candidate and Path(candidate).is_file():
            return str(candidate)
    raise FileNotFoundError("kicad-cli not found: set KICAD_CLI or add it to PATH")


def kicad(cli: str, *args: str) -> None:
    result = subprocess.run([cli, *args], capture_output=True, text=True)
    # kicad-cli reports model errors to stderr but still exits 0 - treat any stderr as failure.
    if result.returncode != 0 or result.stderr.strip():
        raise RuntimeError(f"kicad-cli {' '.join(args)}\n{result.stdout}{result.stderr}")


def main() -> None:
    cli = find_kicad_cli()
    for sch in sorted(SCHEMATICS.glob("*.kicad_sch")):
        svg_dir = BUILD / "schematics"
        netlist = BUILD / "netlists" / f"{sch.stem}.cir"
        netlist.parent.mkdir(parents=True, exist_ok=True)
        kicad(cli, "sch", "export", "svg", "--exclude-drawing-sheet", "-o", str(svg_dir), str(sch))
        kicad(cli, "sch", "export", "netlist", "--format", "spice", "-o", str(netlist), str(sch))
        kicad(cli, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(netlist.with_suffix(".xml")), str(sch))
        print(f"{sch.name}: {svg_dir / (sch.stem + '.svg')}, {netlist}, {netlist.with_suffix('.xml')}")


if __name__ == "__main__":
    main()
