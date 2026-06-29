#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ltspice_raw.py  --  Reusable LTspice .raw waveform parser & quick analyzer.

Parses the binary .raw file produced by `LTspice.exe -b -Run circuit.cir`
and lets you inspect / export / measure any signal without opening the GUI.

Usage
-----
  python ltspice_raw.py circuit.raw                 # list variables + basic stats
  python ltspice_raw.py circuit.raw --csv out.csv   # dump all signals to CSV
  python ltspice_raw.py circuit.raw --csv out.csv --signals "V(out),I(L1)"
  python ltspice_raw.py circuit.raw --stat "V(out)" "I(L1)"   # min/max/rms/mean

As a library
------------
  from ltspice_raw import read_raw
  names, data = read_raw("circuit.raw")   # data[name] -> numpy array
  t = data["time"]

Notes
-----
* Handles LTspice transient binary format: header in UTF-16LE, first variable
  (time) stored as float64, the rest as float32 (the common default), with an
  automatic fallback to all-float64.
* `time` may carry a sign on some points; take np.abs(time) when plotting.
"""
import sys, struct, argparse
import numpy as np


def read_raw(path):
    """Return (varnames, {name: np.ndarray}) for an LTspice .raw file."""
    with open(path, "rb") as f:
        data = f.read()

    txt = data.decode("utf-16-le", errors="ignore")
    header = txt[: txt.find("Binary:")]
    marker = "Binary:\n".encode("utf-16-le")
    bin_start = data.find(marker) + len(marker)

    info, varnames = {}, []
    lines = header.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("No. Variables:"):
            info["nvars"] = int(line.split(":")[1])
        elif line.startswith("No. Points:"):
            info["npoints"] = int(line.split(":")[1])
        elif line.startswith("Flags:"):
            info["flags"] = line.split(":")[1].strip()
        elif line.startswith("Variables:"):
            for _ in range(info["nvars"]):
                i += 1
                parts = [p for p in lines[i].split("\t") if p != ""]
                varnames.append(parts[1])
        i += 1

    nvars, npts = info["nvars"], info["npoints"]
    body = data[bin_start:]

    # default transient layout: time=float64, others=float32
    row_mixed = 8 + 4 * (nvars - 1)
    cols = [np.zeros(npts) for _ in range(nvars)]
    if row_mixed * npts == len(body):
        off = 0
        for p in range(npts):
            cols[0][p] = struct.unpack_from("<d", body, off)[0]; off += 8
            for v in range(1, nvars):
                cols[v][p] = struct.unpack_from("<f", body, off)[0]; off += 4
    else:  # fallback: all float64
        off = 0
        for p in range(npts):
            for v in range(nvars):
                cols[v][p] = struct.unpack_from("<d", body, off)[0]; off += 8

    return varnames, {name: cols[k] for k, name in enumerate(varnames)}


def _stat(x):
    return x.min(), x.max(), float(np.sqrt(np.mean(x ** 2))), x.mean()


def main():
    ap = argparse.ArgumentParser(description="Parse/analyze an LTspice .raw file")
    ap.add_argument("raw", help="path to .raw file")
    ap.add_argument("--csv", help="write signals to this CSV path")
    ap.add_argument("--signals", help="comma-separated signal names for --csv (default: all)")
    ap.add_argument("--stat", nargs="*", help="print min/max/rms/mean for these signals")
    ap.add_argument("--points", type=int, default=2000, help="max rows when writing CSV (downsampled)")
    args = ap.parse_args()

    names, data = read_raw(args.raw)
    t = np.abs(data[names[0]])
    print("Variables (%d), points %d, tspan %.4gs..%.4gs"
          % (len(names), len(t), t.min(), t.max()))
    print(", ".join(names))

    if args.stat:
        print("\nname               min        max        rms        mean")
        for s in args.stat:
            if s in data:
                mn, mx, rms, mean = _stat(data[s])
                print("%-16s %10.4g %10.4g %10.4g %10.4g" % (s, mn, mx, rms, mean))
            else:
                print("%-16s  (not found)" % s)

    if args.csv:
        import csv
        cols = [names[0]]
        if args.signals:
            cols += [s.strip() for s in args.signals.split(",") if s.strip() in data]
        else:
            cols += [n for n in names[1:]]
        idx = np.arange(len(t))
        if len(idx) > args.points:
            idx = idx[:: len(idx) // args.points]
        with open(args.csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(cols)
            for p in idx:
                w.writerow(["%.9g" % data[c][p] for c in cols])
        print("\nWrote %d rows x %d cols -> %s" % (len(idx), len(cols), args.csv))


if __name__ == "__main__":
    main()
