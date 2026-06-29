#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_ltspice.py  --  Locate LTspice and run a netlist/schematic in batch mode.

Batch mode (`-b -Run`) simulates without opening the GUI and writes a .raw +
.log next to the input file. Pair it with tools/ltspice_raw.py to analyze.

Usage
-----
  python run_ltspice.py path\\to\\circuit.cir
  python run_ltspice.py path\\to\\circuit.asc
  python run_ltspice.py circuit.cir --exe "C:\\full\\path\\LTspice.exe"

Exit code mirrors LTspice's. On success a <circuit>.raw appears.
"""
import os, sys, glob, subprocess, argparse

# Common install locations across LTspice editions (newest ADI first).
CANDIDATES = [
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe"),
    os.path.expandvars(r"%ProgramFiles%\ADI\LTspice\LTspice.exe"),
    os.path.expandvars(r"%ProgramFiles%\LTC\LTspiceXVII\XVIIx64.exe"),
    os.path.expandvars(r"%ProgramFiles(x86)%\LTC\LTspiceXVII\XVIIx64.exe"),
]


def find_ltspice():
    for c in CANDIDATES:
        if c and os.path.isfile(c):
            return c
    # last resort: search common roots
    for root in [os.path.expandvars(r"%LOCALAPPDATA%\Programs"),
                 os.environ.get("ProgramFiles", ""),
                 os.environ.get("ProgramFiles(x86)", "")]:
        if root and os.path.isdir(root):
            hits = glob.glob(os.path.join(root, "**", "LTspice*.exe"), recursive=True)
            if hits:
                return hits[0]
    return None


def main():
    ap = argparse.ArgumentParser(description="Run an LTspice circuit in batch mode")
    ap.add_argument("circuit", help=".cir / .net / .asc file to simulate")
    ap.add_argument("--exe", help="explicit path to LTspice.exe")
    args = ap.parse_args()

    exe = args.exe or find_ltspice()
    if not exe:
        sys.exit("ERROR: LTspice.exe not found. Pass it with --exe.")
    circuit = os.path.abspath(args.circuit)
    if not os.path.isfile(circuit):
        sys.exit("ERROR: circuit file not found: " + circuit)

    print("LTspice : %s" % exe)
    print("Circuit : %s" % circuit)
    rc = subprocess.call([exe, "-b", "-Run", circuit])
    raw = os.path.splitext(circuit)[0] + ".raw"
    print("Exit code: %d" % rc)
    if os.path.isfile(raw):
        print("Wrote: %s (%d bytes)" % (raw, os.path.getsize(raw)))
    sys.exit(rc)


if __name__ == "__main__":
    main()
