"""KiCad netlist (kicadxml): components and the nets on their pins."""

import xml.etree.ElementTree as ET
from pathlib import Path


def pin_nets(xml_path: Path, symbol: tuple[str, str]) -> dict[str, dict[str, str]]:
    """Reference -> {pin: net} for every component of the library symbol (lib, part)."""
    root = ET.parse(xml_path).getroot()
    refs = {c.get("ref") for c in root.iter("comp")
            if (c.find("libsource").get("lib"), c.find("libsource").get("part")) == symbol}
    pins: dict[str, dict[str, str]] = {ref: {} for ref in refs}
    for net in root.iter("net"):
        for node in net.iter("node"):
            if node.get("ref") in refs:
                pins[node.get("ref")][node.get("pin")] = net.get("name")
    return dict(sorted(pins.items()))
