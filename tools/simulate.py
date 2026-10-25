"""Scenario: every switch state for every chandelier variant, RMS voltage on each lamp.

Input:  build/chandelier/netlists/<variant>.cir, .xml (run build.py first)
Output: console, build/chandelier/sim/results.md, build/chandelier/sim/raw/*.raw
"""

import itertools

from spicelib import RawRead, SimRunner, SpiceEditor
from spicelib.simulators.ngspice_simulator import NGspiceSimulator

from circuit_tools import layout
from circuit_tools.measure import rms, time_axis, voltage
from circuit_tools.netlist import pin_nets
from circuit_tools.programs import find_ngspice

CIRCUIT = layout.CIRCUITS / "chandelier"
LAMP = ("Device", "Lamp")  # KiCad library symbol that marks a lamp
TRAN = ".tran 0.1m 200m"
RMS_WINDOW = (0.1, 0.2)  # s, after start-up


def main() -> None:
    netlists = layout.build_dir(CIRCUIT) / "netlists"
    out = layout.build_dir(CIRCUIT) / "sim"
    (out / "raw").mkdir(parents=True, exist_ok=True)
    runner = SimRunner(simulator=NGspiceSimulator.create_from(find_ngspice()), output_folder=out / "raw")
    lines = ["# Chandelier: RMS voltage on each lamp, V", ""]
    for sch in layout.variants(CIRCUIT):
        cir, xml = netlists / f"{sch.stem}.cir", netlists / f"{sch.stem}.xml"
        if not (cir.is_file() and xml.is_file()):
            raise SystemExit(f"{sch.stem}: netlists not found in {netlists} - run 'uv run tools/build.py {CIRCUIT.name}' first")
        # Lamp pin 2 is '+', pin 1 is '-'.
        lamps = {ref: (pins["2"], pins["1"]) for ref, pins in pin_nets(xml, LAMP).items()}
        lines += [f"## {sch.stem}", "",
                  "| B1 | B2 | " + " | ".join(lamps) + " |",
                  "|---|---|" + "---|" * len(lamps)]
        for b1, b2 in itertools.product((0, 1), repeat=2):
            netlist = SpiceEditor(cir)
            netlist.set_parameters(b1=b1, b2=b2)
            netlist.add_instruction(TRAN)
            raw_path, _log = runner.run_now(netlist, run_filename=f"{sch.stem}_b1{b1}_b2{b2}.cir", exe_log=True)
            raw = RawRead(raw_path)
            t = time_axis(raw)
            values = [rms(t, voltage(raw, l) - voltage(raw, n), RMS_WINDOW) for l, n in lamps.values()]
            state = lambda b: "on" if b else "off"
            lines.append(f"| {state(b1)} | {state(b2)} | " + " | ".join(f"{v:.0f}" for v in values) + " |")
        lines.append("")
    report = "\n".join(lines)
    (out / "results.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
