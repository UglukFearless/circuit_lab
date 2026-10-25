"""Repository layout.

circuits/<circuit>/<variant>.kicad_sch   circuit model, one KiCad project (.kicad_sch + .kicad_pro) per variant
build/<circuit>/                         output files of the circuit
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CIRCUITS = ROOT / "circuits"
BUILD = ROOT / "build"


def circuits(names: list[str] | None = None) -> list[Path]:
    """Circuit folders: the given names, or every circuit when none are given."""
    found = {p.name: p for p in sorted(CIRCUITS.iterdir()) if p.is_dir()}
    if not names:
        return list(found.values())
    missing = [n for n in names if n not in found]
    if missing:
        raise SystemExit(f"circuit not found in {CIRCUITS}: {', '.join(missing)}")
    return [found[n] for n in names]


def variants(circuit: Path) -> list[Path]:
    """Variant schematics: .kicad_sch files with a .kicad_pro of the same name (KiCad autosaves have none)."""
    found = sorted(sch for sch in circuit.glob("*.kicad_sch") if sch.with_suffix(".kicad_pro").is_file())
    if not found:
        raise SystemExit(f"{circuit.name}: no variants (.kicad_sch + .kicad_pro) in {circuit}")
    return found


def build_dir(circuit: Path) -> Path:
    return BUILD / circuit.name
