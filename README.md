# Autonomous Ball-Retrieval Robot – Simulation

This is code for **BITS Pilani, Introduction to Sports Engineering, Assignment 2 (Sem-I 2026-27), Project Idea 11**. It compares three tennis-ball-retrieval robot designs by retrieval time and energy using a pure-Python Monte-Carlo simulation:
- **A**, an overhead camera with a known-ball tour;
- **B**, an on-board camera that surveys the court and then tours;
- **C**, a blind boustrophedon sweep.

> All numbers are **model outputs under stated assumptions, not hardware measurements**. See `MODEL_NOTES.md` for the parameters, their sources and the limitations.

## Run (Python 3, no external packages)
```bash
python3 sim.py 200        # 4 strategies x layouts x N x hopper size; runs self-checks C1–C6 -> results.txt, results.json
python3 grid.py           # design comparison A/B/C over hopper size, detection range/recall, intake width -> grid.txt
python3 sensitivity.py    # sensitivity to speed, pick time, intake width, power -> sensitivity.txt
python3 report/build.py   # regenerates figures + report HTML/PDF (PDF step needs Google Chrome on macOS)
```
With fixed seeds, the outputs reproduce exactly.

## Files
| File | Purpose |
|---|---|
| `sim.py` | Court model, ball layouts, nearest-neighbour + 2-opt tour, hopper-capacity splitting, sweep, on-board survey model, time/energy model, self-checks |
| `grid.py` | Design-alternative grid (200 trials, seed 42) |
| `sensitivity.py` | One-at-a-time and interaction sensitivity |
| `report/build.py` | Builds the assignment report figures and PDF from the result files |
| `archive_v1/` | First model version, before the review fixes, kept for transparency |
