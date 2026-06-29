# LTSPICE-Assistant

A reusable toolkit + Claude skill for building, simulating, and analyzing
circuits in **LTspice** — headless, repeatable, and verifiable. Point it at a
spec and get a working netlist, a clean schematic, real waveform data, and a
written analysis.

## What's inside
```
LTSPICE-Assistant/
├── .claude/skills/ltspice-circuit/SKILL.md   ← the reusable skill (the workflow)
├── tools/
│   ├── run_ltspice.py     locate LTspice + run a circuit in batch (-b -Run)
│   └── ltspice_raw.py     parse .raw → list/stat/CSV (CLI + Python library)
├── reference/
│   └── symbol_pins.md     symbol pin coordinates & rotation math for .asc
└── examples/
    └── llc-resonant-converter/   full worked example (netlist, 2 schematics,
                                   plots, raw data, tutorial + analysis docs)
```

## The workflow (see the skill for detail)
1. **Write** a `.cir` netlist (every value a `.param`).
2. **Simulate** headless: `python tools/run_ltspice.py circuit.cir` → `circuit.raw`.
3. **Analyze** the `.raw`: `python tools/ltspice_raw.py circuit.raw --stat "V(out)"`.
4. **Verify** numbers are physical and match the design equation.
5. *(optional)* **Schematic**: hand-build `.asc` (labels first, then full wires),
   Run it, confirm it matches the netlist.
6. **Write up** a tutorial + an analysis doc, all numbers from the `.raw`.

## Quick start
```bash
# requirements: Windows, LTspice installed, Python 3 + numpy
cd examples/llc-resonant-converter
python ../../tools/run_ltspice.py LLC_converter.cir
python ../../tools/ltspice_raw.py LLC_converter.raw --stat "V(vout)" "I(Lr)"
```

## Using the skill on a NEW circuit
Ask Claude Code (with this repo as the working dir) something like:
> "Build an LTspice buck converter, 12V→5V/10W, analyze the inductor current
> ripple and efficiency."

The `ltspice-circuit` skill triggers and walks the 6-step workflow, reusing the
tools here. Copy `examples/llc-resonant-converter/` as a pattern for the output
(netlist + schematic + tutorial + analysis).

## Notes
- New ADI LTspice installs per-user at `%LOCALAPPDATA%\Programs\ADI\LTspice\LTspice.exe`.
- `.raw` is binary (UTF-16LE header; time float64, vars float32) — use `ltspice_raw.py`.
- `tools/run_ltspice.py` auto-discovers common LTspice install locations.

## License
Personal/educational use. Circuits and docs authored with Claude Code.
