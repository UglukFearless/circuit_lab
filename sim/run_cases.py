"""Scenario: every switch state for every chandelier variant, RMS voltage on each lamp.

Input:  build/netlists/<variant>.cir, .xml (run build.py first)
Output: console, build/sim/results.md, build/sim/raw/*.raw
"""

import itertools
import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from spicelib import RawRead, SimRunner, SpiceEditor
from spicelib.simulators.ngspice_simulator import NGspiceSimulator

ROOT = Path(__file__).parent.parent
NETLISTS = ROOT / "build" / "netlists"
OUT = ROOT / "build" / "sim"
VARIANTS = ["chandelier_as_is", "chandelier_fixed"]

LAMP = ("Device", "Lamp")  # KiCad library symbol that marks a lamp
GROUND = {"GND", "0"}
TRAN = ".tran 0.1m 200m"
RMS_WINDOW = (0.1, 0.2)  # s, after start-up


def find_ngspice() -> str:
    for candidate in (os.environ.get("NGSPICE"), "ngspice_con", "ngspice"):
        if candidate and (path := shutil.which(candidate)):
            return path
    raise FileNotFoundError("ngspice not found: set NGSPICE or add it to PATH")


def lamp_nets(xml_path: Path) -> dict[str, tuple[str, str]]:
    """Lamp reference -> (net on pin 2 '+', net on pin 1 '-'), from the KiCad netlist."""
    root = ET.parse(xml_path).getroot()
    lamps = {c.get("ref") for c in root.iter("comp")
             if (c.find("libsource").get("lib"), c.find("libsource").get("part")) == LAMP}
    pins: dict[str, dict[str, str]] = {ref: {} for ref in lamps}
    for net in root.iter("net"):
        for node in net.iter("node"):
            if node.get("ref") in lamps:
                pins[node.get("ref")][node.get("pin")] = net.get("name")
    return {ref: (p["2"], p["1"]) for ref, p in sorted(pins.items())}


def voltage(raw: RawRead, net: str) -> np.ndarray:
    if net in GROUND:
        return np.zeros(len(raw.get_axis()))
    return np.asarray(raw.get_trace(f"V({net})").get_wave())


def rms(t: np.ndarray, v: np.ndarray) -> float:
    m = (t >= RMS_WINDOW[0]) & (t <= RMS_WINDOW[1])
    return float(np.sqrt(np.trapezoid(v[m] ** 2, t[m]) / (t[m][-1] - t[m][0])))


def main() -> None:
    runner = SimRunner(simulator=NGspiceSimulator.create_from(find_ngspice()), output_folder=OUT / "raw")
    lines = ["# Chandelier: RMS voltage on each lamp, V", ""]
    for variant in VARIANTS:
        cir, xml = NETLISTS / f"{variant}.cir", NETLISTS / f"{variant}.xml"
        if not (cir.is_file() and xml.is_file()):
            raise SystemExit(f"{cir.stem}: netlists not found in {NETLISTS} - run build.py first")
        lamps = lamp_nets(xml)
        lines += [f"## {variant}", "",
                  "| B1 | B2 | " + " | ".join(lamps) + " |",
                  "|---|---|" + "---|" * len(lamps)]
        for b1, b2 in itertools.product((0, 1), repeat=2):
            netlist = SpiceEditor(cir)
            netlist.set_parameters(b1=b1, b2=b2)
            netlist.add_instruction(TRAN)
            raw_path, _log = runner.run_now(netlist, run_filename=f"{variant}_b1{b1}_b2{b2}.cir", exe_log=True)
            raw = RawRead(raw_path)
            t = np.abs(np.asarray(raw.get_axis()))
            values = [rms(t, voltage(raw, l) - voltage(raw, n)) for l, n in lamps.values()]
            state = lambda b: "on" if b else "off"
            lines.append(f"| {state(b1)} | {state(b2)} | " + " | ".join(f"{v:.0f}" for v in values) + " |")
        lines.append("")
    report = "\n".join(lines)
    (OUT / "results.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
