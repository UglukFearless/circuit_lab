"""Build output files from circuit models: schematic images and netlists.

circuits/<circuit>/<variant>.kicad_sch -> build/<circuit>/schematics/<variant>.svg   picture
                                       -> build/<circuit>/netlists/<variant>.cir     SPICE netlist (for simulation)
                                       -> build/<circuit>/netlists/<variant>.xml     KiCad netlist (components, fields, nets)

Usage: build.py [circuit ...]   (all circuits by default)
"""

import sys

from circuit_tools import layout
from circuit_tools.programs import find_kicad_cli, run_kicad_cli


def main(names: list[str]) -> None:
    cli = find_kicad_cli()
    for circuit in layout.circuits(names):
        variants = layout.variants(circuit)
        svg_dir = layout.build_dir(circuit) / "schematics"
        netlist_dir = layout.build_dir(circuit) / "netlists"
        netlist_dir.mkdir(parents=True, exist_ok=True)
        for sch in variants:
            netlist = netlist_dir / f"{sch.stem}.cir"
            run_kicad_cli(cli, "sch", "export", "svg", "--exclude-drawing-sheet", "-o", str(svg_dir), str(sch))
            run_kicad_cli(cli, "sch", "export", "netlist", "--format", "spice", "-o", str(netlist), str(sch))
            run_kicad_cli(cli, "sch", "export", "netlist", "--format", "kicadxml", "-o", str(netlist.with_suffix(".xml")), str(sch))
            print(f"{circuit.name}/{sch.name}: {svg_dir / (sch.stem + '.svg')}, {netlist}, {netlist.with_suffix('.xml')}")


if __name__ == "__main__":
    main(sys.argv[1:])
