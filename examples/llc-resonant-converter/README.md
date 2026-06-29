# Example: Half-Bridge LLC Resonant Converter

A complete worked example produced with the `ltspice-circuit` skill:
400V → 48.6V / 96W half-bridge LLC, switching at the resonant point (132 kHz),
achieving primary ZVS + secondary ZCS.

## Files
| File | What it is |
|------|-----------|
| `LLC_converter.cir` | **The netlist** — the source of truth, runs headless |
| `LLC_converter.net` | netlist (alt extension, same circuit) |
| `LLC_converter.asc` | schematic, **net-label** style (error-proof) |
| `LLC_converter_wired.asc` | schematic, **fully-wired** style (textbook look) |
| `LLC_converter*.plt` | saved plot settings (auto-shows traces on Run) |
| `LLC_converter*.raw` | simulation output (binary waveforms) |
| `LLC_converter*.log` | simulation logs (0 errors) |
| `LLC_教学文档.md` | tutorial: build + reproduce, line-by-line netlist |
| `LLC_分析文档.md` | deep analysis: principle, current paths, waveform data |
| `scripts/` | the original per-circuit analysis scripts |

## Reproduce in 30 seconds
From this folder:
```bash
# 1. simulate headless
python ../../tools/run_ltspice.py LLC_converter.cir
# 2. measure
python ../../tools/ltspice_raw.py LLC_converter.raw --stat "V(sw)" "V(vout)" "I(Lr)"
```
Or open it in the GUI and press Run (the `.plt` auto-loads V(sw)/V(vout)/I(Lr)):
```
LTspice.exe LLC_converter_wired.asc
```

## Headline results (from the .raw)
| Quantity | Value |
|----------|-------|
| Vout / Pout | 48.6 V / 96 W |
| fsw / fr | 132 kHz / 132.6 kHz |
| Gate duty / dead-time | 47.4% / 200 ns |
| I(Lr) peak / rms | 1.70 A / 1.06 A |
| Magnetizing peak-peak | 2.52 A (triangular) |
| Vcr mean / swing | 201 V (=Vin/2) / 114–286 V |
| Soft switching | ZVS (primary) ✓, ZCS (secondary) ✓ |

See `LLC_分析文档.md` for the four switching states with current-path diagrams.
