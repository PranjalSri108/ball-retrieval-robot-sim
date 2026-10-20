# Ball-retrieval strategy simulation (illustrative)

Pure-Python Monte-Carlo model (no external packages). Run `python3 sim.py 200`, `python3 sensitivity.py` and `python3 grid.py`.
Outputs: `results.txt`, `results.json`, `sensitivity.txt`, `grid.txt`. v1 outputs (before review fixes) are kept as `results_v1.txt`, `sensitivity_v1.txt` and `sim_v1.py`.

## v2 changes (after the independent review)
- Fixed: the sweep no longer performs an empty final unload, and the detection-aware box sweep (S4) stops once the last known ball is collected.
- Added `onboard()`: an on-board camera model. A survey lawn-mower pass uses lane spacing 2R (R = detection range), each ball is detected with probability r per pass, detected balls are collected by an NN+2-opt tour, and the cycle repeats for missed balls (max 6 passes). This is pessimistic: there is no opportunistic detection while touring.
- Added `P_infra`, off-board power (e.g., a laptop for an overhead-camera design), to set the system energy boundary.
- Added checks C5 (on-board ≥ oracle time) and C6 (box sweep ≤ blind sweep, no misses).
- `grid.py` compares designs A, B and C across hopper C ∈ {15, 30}, R/r and w. Sensitivity now uses 200 trials and seed 42, plus P_drive = 7.2 W and an interaction case.

## What it models
- **Field:** the ITF doubles court (23.77 × 10.97 m) plus the club run-back (5.48 m) and side-run (3.05 m), giving a 34.73 × 17.07 m (592.8 m²) enclosure. The depot is behind the near baseline.
- **Ball layouts:**
  - `uniform`: random over the whole enclosure.
  - `drill`: Gaussian cluster near the far baseline and back fence, as if a coach had fed balls from one side.
- **Strategies:**
  - **S1:** targeted nearest-neighbour tour.
  - **S2:** NN tour improved with 2-opt.
  - **S3:** blind boustrophedon sweep of the whole enclosure.
  - **S4:** boustrophedon sweep of only the detected balls' bounding box.
  - All four return to the depot when the hopper (capacity C) is full.
- **Time:**
  - Travel time = path/v + turning angle/ω.
  - Targeted strategies add t_pick per ball.
  - Every hopper empty adds t_unload.
- **Energy:**
  - P_drive applies while moving.
  - P_intake applies per pick for targeted strategies, and continuously while sweeping.
  - P_compute + P_idle apply over the whole run.

## Assumptions (all are user-adjustable in `PARAMS`)
| Parameter | Value | Basis |
|---|---|---|
| v | 0.6 m/s | Chosen to be close to the 2018 Tennibot claim of 2.3 km/h (≈0.64 m/s), as reported by New Atlas |
| ω | 90°/s | Own estimate |
| t_pick | 1.0 s | Own estimate |
| w (intake width) | 0.30 m | Own estimate for a tennis roller intake. Golf range pickers are ~0.96 m wide (Toro, Belrobotics) |
| t_unload | 20 s | Own estimate |
| P_drive | 10 W | Own estimate. N20-class motor pair ≈1.2–7.2 W at no-load to stall (vendor specs), plus losses |
| P_compute | 3 W | Raspberry Pi idle ≈2.4–2.7 W (permacomputing measurements). ESP32-CAM ≈0.9 W |
| P_intake | 3 W | Own estimate |
| P_idle | 1 W | Own estimate |

## Limitations
- S1–S4 assume perfect global detection (oracle). Only `onboard()` models detection range and recall, and it has no false positives.
- There is no localisation error, no wheel slip and no acceleration phase.
- There are no obstacles or people.
- Ball positions are static.
- The targeted strategies assume every ball is visible from a global view, such as an overhead camera or a mapped exploration.
- The model also omits the cost of searching/exploring to find the balls. That favours S1/S2.
- **These are model outputs, not robot measurements.**

## Sanity checks (built into `sim.checks()`, all pass)
- **C1:** a single ball 6 m ahead gives exactly the closed-form time (12 m / v + π/ω + t_pick + t_unload).
- **C2:** the 2-opt path is never longer than the NN path.
- **C3:** the blind-sweep path is at least area/w long, and the sweep misses no balls.
- **C4:** a smaller hopper never gives a shorter path.

## Plausibility cross-checks against external numbers
- **Blind sweep (S3):** the model gives ≈10 m²/min (592.8 m² in ≈59 min). Ali et al. (2018) report a U-turn coverage robot clearing a 14 × 15 m experiment court (210 m²) in 24.2 min, ≈8.7 m²/min (the paper plans for 18 × 18 m, but its results section gives 14 × 15 m), so the model is of the same order.
- **Targeted strategy (S2):** the model gives ≈9–14 balls/min for N = 60–90. SeekerBot 2.0 claims 50 balls in ≈4–5 min (≈10–12.5 balls/min; manufacturer claim). This matches in order of magnitude, but both depend on assumed or unverified parameters.
