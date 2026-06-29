---
name: ltspice-circuit
description: >-
  Build, simulate, and analyze an electronic circuit in LTspice end-to-end on
  Windows. Use when the user asks to create/design an LTspice circuit (any
  topology: buck, boost, LLC, flyback, filters, amplifiers, rectifiers...),
  run a transient/AC simulation, analyze waveforms, convert a netlist into a
  visual schematic (.asc), or produce a teaching/analysis writeup of a circuit.
  Triggers on mentions of LTspice, SPICE netlist, .cir/.asc/.raw, "仿真",
  "画电路/原理图", "分析波形".
---

# LTspice circuit: build → simulate → analyze

A repeatable workflow for producing a **verified** LTspice circuit plus its
waveform analysis, headless (no clicking required) and optionally a clean
schematic. Battle-tested on the LLC example in `examples/llc-resonant-converter/`.

## When to use
The user wants any of: a new LTspice circuit from a spec, a simulation run,
waveform/metrics analysis, a netlist→schematic conversion, or a writeup.

## Environment assumptions
- Windows, LTspice installed (ADI build default: `%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe`).
- Python 3 with numpy available (for parsing `.raw`).
- Shell: PowerShell + Bash both available.

---

## The 6-step workflow

### Step 1 — Write the netlist (`.cir`)
Author a SPICE netlist directly (robust and quick to iterate). Use `.param` for
every design value so the user can sweep them later.

Template skeleton:
```spice
* <Title>
.param Vin=400 fsw=132k         ; design knobs up top
* --- sources ---
Vin VIN 0 {Vin}
* --- components --- (Rxxx Cxxx Lxxx Dxxx Mxxx Sxxx ...)
* --- models ---
.model DMOD D(Ron=0.02 Roff=1Meg Vfwd=0.55)
* --- analysis ---
.tran 0 300u 200u 20n uic        ; tstop=300u, save from 200u, maxstep=20n
.options plotwinsize=0           ; force full-resolution save for clean parsing
.end
```
Tips:
- `.tran 0 <tstop> <tstart> <maxstep> uic` — set `tstart` to skip the startup
  transient; set `maxstep` small enough to resolve the switching edges.
- Use `.ic V(node)=...` (+ `uic`) to start an output cap near steady state so
  you don't have to simulate the full RC settling time.
- Ideal switches (`Sxxx` + `.model SW`) are great for explaining topology, but
  **a switching-node leg needs a freewheel path**: add anti-parallel diodes
  (body diodes) and small `Coss` caps, or the node floats to huge voltages
  during dead time. (This was a real bug in the LLC example — see its docs.)
- AC analysis: use `.ac dec 100 10 10Meg` with an AC source (`SYMATTR Value AC 1`).

### Step 2 — Simulate headless (batch mode)
Never require the GUI for analysis. Run:
```bash
python tools/run_ltspice.py path/to/circuit.cir
```
or directly:
```
LTspice.exe -b -Run path\to\circuit.cir
```
`-b` = batch; it writes `circuit.raw` (binary waveforms) + `circuit.log`.
**Always read the `.log`** and confirm 0 errors before trusting results.

### Step 3 — Parse & measure the `.raw`
```bash
python tools/ltspice_raw.py circuit.raw                       # list signals
python tools/ltspice_raw.py circuit.raw --stat "V(out)" "I(L1)"   # min/max/rms/mean
python tools/ltspice_raw.py circuit.raw --csv wave.csv --signals "V(out),I(L1)"
```
Or as a library for custom analysis:
```python
from ltspice_raw import read_raw
import numpy as np
names, d = read_raw("circuit.raw")
t = np.abs(d["time"])
```
Common derived quantities:
- Switching frequency / duty: threshold a node, find rising/falling edges.
- RMS / mean / peak of currents; `Pout = mean(V(out)) * mean(I(load))`.
- Voltage across a 2-terminal device = `V(nodeA) - V(nodeB)`.
- For coupled inductors, branch current of the primary ≠ magnetizing current;
  derive it explicitly and **sanity-check the sign** against theory (the dot
  convention can flip it — test both `±` and keep the physically sensible one).

### Step 4 — Verify
The hard test that the circuit is correct: the numbers must be physical and
match the design intent (e.g. `Vout ≈ (Vin/2)/n` for the LLC). If you also make
a schematic (Step 5), it must produce the **same** waveforms as the netlist.

### Step 5 — (Optional) Netlist → visual schematic (`.asc`)
LTspice has **no** auto netlist→schematic. Build the `.asc` by hand:
1. Read exact pin offsets from `reference/symbol_pins.md` (or the `.asy` files).
2. Place each `SYMBOL`, compute every pin's absolute coordinate.
3. **Recommended first pass — net labels**: drop a `FLAG x y NAME` on every pin
   (use `0` for ground). Same name = connected. Zero routing errors.
4. Open it, **Run it, confirm identical waveforms** → connectivity proven.
5. **Optional second pass — full wires**: replace labels with real `WIRE`
   segments whose endpoints land exactly on pins, for a textbook look. Rotate
   diodes `R180` to point the arrow the right way. Re-run to re-verify.
6. Save plot settings as `<circuit>.plt` (same basename) so reopening + Run
   auto-shows your chosen traces.

Two schematic styles, both valid (the LLC example ships both):
- `*_labels.asc` — engineering style, label-connected, fast & error-proof.
- `*_wired.asc` — fully drawn wires, prettier for humans/teaching.

To open a `.cir`/`.asc` for the user:
```
LTspice.exe path\to\circuit.cir
```
(The Open dialog filters to `*.asc`; type the full path with extension or pick
"All Files" to open a `.cir`.)

### Step 6 — Write it up
Produce two markdown docs next to the circuit (see the LLC example for the bar):
- **教学文档 (tutorial)**: file list, topology, line-by-line netlist, exact
  reproduce steps, how to read waveforms, parameter experiments.
- **分析文档 (analysis)**: principle, architecture, per-state current-path
  diagrams (ASCII), and a data table of every measured quantity (freq, duty,
  peak/RMS currents, ripple, soft-switching checks) — all from the real `.raw`.

---

## Quality bar (do all of these)
- [ ] `.log` shows 0 errors.
- [ ] Key results are physically sensible and match the design equation.
- [ ] Every switching node has a defined current path in every sub-interval.
- [ ] If a schematic exists, it Runs and matches the netlist waveforms.
- [ ] All design values are `.param`s the user can sweep.
- [ ] Analysis numbers come from the `.raw`, not hand-waving.

## Reusable assets in this repo
- `tools/run_ltspice.py` — locate LTspice + run batch.
- `tools/ltspice_raw.py` — parse `.raw`, dump CSV, print stats (CLI + library).
- `reference/symbol_pins.md` — symbol pin coordinates & rotation math for `.asc`.
- `examples/llc-resonant-converter/` — full worked example (netlist, two
  schematics, plots, tutorial + analysis docs) to copy patterns from.

## Gotchas learned the hard way
- Ideal switch legs **need body diodes + Coss** or the node spikes to ~1e5 V in
  dead time and ZVS is meaningless.
- The new ADI LTspice installs **per-user** to `%LOCALAPPDATA%\Programs\ADI\LTspice`
  and ignores a custom install dir.
- `.raw` header is **UTF-16LE**; time is float64, other vars float32 (default).
- Opening a `.cir` from the GUI: the file dialog hides it (asc filter) — type the
  full path or switch the filter.
- Coupled-inductor primary branch current is the resonant current, **not** the
  magnetizing current — compute Imag separately and check its sign/shape.
