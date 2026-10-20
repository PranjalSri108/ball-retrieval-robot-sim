"""Design-alternative grid (v2): oracle overhead camera (A) vs on-board camera (B) vs blind sweep (C)
across hopper capacity, intake width, detection range R and recall r. All parameters are ASSUMPTIONS.
P_infra=20 W is an assumed off-board laptop for design A's 'system' energy boundary."""
import random, statistics, sim
base = dict(sim.PARAMS)
TRIALS, SEED = 200, 42
def run(label, fn, n, dist, over):
    p = dict(base); p.update(over)
    L, W = sim.enclosure(p); depot = (0.0, W/2)
    rng = random.Random(SEED); rng2 = random.Random(SEED + 1)
    res = []
    for _ in range(TRIALS):
        b = sim.gen_balls(n, dist, p, rng)
        res.append(fn(b, depot, p, rng2))
    T = statistics.mean(r['time_s'] for r in res)/60; E = statistics.mean(r['energy_Wh'] for r in res)
    miss = statistics.mean(r.get('missed', 0) for r in res)
    return label, T, E, miss
rows = []
for dist in ['uniform', 'drill']:
    n = 60
    for C in [15, 30]:
        rows.append((dist, C) + run('A oracle overhead cam, robot-only', lambda b,d,p,g: sim.targeted(b,d,p,C,True), n, dist, {}))
        rows.append((dist, C) + run('A oracle overhead cam, +20 W laptop', lambda b,d,p,g: sim.targeted(b,d,p,C,True), n, dist, {'P_infra':20.0}))
        for R, r in [(5,0.95),(3,0.95),(3,0.8),(2,0.7)]:
            rows.append((dist, C) + run(f'B on-board R={R} m r={r}', lambda b,d,p,g,R=R,r=r: sim.onboard(b,d,p,C,R,r,g), n, dist, {}))
        for w in [0.3, 0.6, 1.0]:
            rows.append((dist, C) + run(f'C blind sweep w={w} m', lambda b,d,p,g: sim.sweep(b,d,p,C,False), n, dist, {'w':w}))
        rows.append((dist, C) + run('S4 box sweep w=0.3 m (needs detection)', lambda b,d,p,g: sim.sweep(b,d,p,C,True), n, dist, {}))
print(f"N=60, {TRIALS} trials, seed {SEED}")
print(f"{'layout':8}{'C':>4}  {'design':42}{'T(min)':>8}{'E(Wh)':>8}{'missed':>8}")
for dist, C, lab, T, E, m in rows:
    print(f"{dist:8}{C:>4}  {lab:42}{T:8.2f}{E:8.2f}{m:8.2f}")
