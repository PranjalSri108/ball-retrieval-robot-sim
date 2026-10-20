"""
Illustrative Monte-Carlo comparison of ball-retrieval strategies on a tennis court.
Pure Python (no numpy). All parameters are ASSUMPTIONS (see PARAMS and README.md);
results are model outputs, not measurements of any real robot.

Strategies
  S1  targeted nearest-neighbour (greedy) tour, hopper-capacity returns to depot
  S2  targeted NN tour improved with 2-opt, then split by hopper capacity
  S3  blind boustrophedon (lawn-mower) sweep of whole enclosure, intake width w
  S4  detection-aware boustrophedon: sweep only the bounding box of detected balls
"""
import math, random, statistics, json, sys

PARAMS = dict(
    # geometry (ITF Rules of Tennis 2026: 23.77 x 10.97 m doubles court; Appendix X run-back 5.48 m, side-run 3.05 m)
    court_L=23.77, court_W=10.97, runback=5.48, siderun=3.05,
    # robot (assumptions; speed chosen near 2018 Tennibot claim of 2.3 km/h ~= 0.64 m/s)
    v=0.6,            # m/s cruise speed
    omega=math.radians(90),  # rad/s point-turn rate
    t_pick=1.0,       # s dwell per ball for targeted pickup (align + intake)
    w=0.30,           # m effective intake width for sweeping
    t_unload=20.0,    # s to unload hopper at depot
    P_drive=10.0,     # W drive motors while moving (assumed; N20-class pair 1.2-7.2 W + losses)
    P_compute=3.0,    # W compute (Pi idle ~2.4-2.7 W measured; ESP32-CAM ~0.9 W)
    P_intake=3.0,     # W roller motor when running
    P_idle=1.0,       # W other electronics
    P_infra=0.0,      # W off-board infrastructure (e.g. laptop/overhead camera); 0 = robot-only boundary
)

def enclosure(p):
    L = p['court_L'] + 2 * p['runback']
    W = p['court_W'] + 2 * p['siderun']
    return L, W

def gen_balls(n, dist, p, rng):
    L, W = enclosure(p)
    balls = []
    while len(balls) < n:
        if dist == 'uniform':
            x, y = rng.uniform(0, L), rng.uniform(0, W)
        else:  # 'drill': coach feeding from one side -> balls cluster near far baseline/back fence
            x = rng.gauss(L - p['runback'] * 0.6, 2.0)
            y = rng.gauss(W / 2, 3.0)
        if 0 <= x <= L and 0 <= y <= W:
            balls.append((x, y))
    return balls

def d(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def heading(a, b):
    return math.atan2(b[1] - a[1], b[0] - a[0])

def turn(h0, h1):
    x = abs(h1 - h0) % (2 * math.pi)
    return min(x, 2 * math.pi - x)

def route_cost(route, p):
    """route: list of points incl. depot visits. returns (dist, turn_angle)."""
    dist, ang, h = 0.0, 0.0, 0.0
    for a, b in zip(route, route[1:]):
        if d(a, b) < 1e-9:
            continue
        hb = heading(a, b)
        ang += turn(h, hb)
        h = hb
        dist += d(a, b)
    return dist, ang

def nn_order(depot, balls):
    rem = list(balls); cur = depot; order = []
    while rem:
        j = min(range(len(rem)), key=lambda i: d(cur, rem[i]))
        cur = rem.pop(j); order.append(cur)
    return order

def two_opt(depot, order, max_iter=50):
    path = [depot] + order + [depot]
    improved, it = True, 0
    while improved and it < max_iter:
        improved = False; it += 1
        for i in range(1, len(path) - 2):
            for k in range(i + 1, len(path) - 1):
                a, b, c, e = path[i - 1], path[i], path[k], path[k + 1]
                if d(a, c) + d(b, e) < d(a, b) + d(c, e) - 1e-9:
                    path[i:k + 1] = reversed(path[i:k + 1]); improved = True
    return path[1:-1]

def split_capacity(depot, order, C):
    route = [depot]
    for i, b in enumerate(order):
        route.append(b)
        if (i + 1) % C == 0 and i + 1 < len(order):
            route.append(depot)
    route.append(depot)
    return route

def targeted(balls, depot, p, C, improve):
    order = nn_order(depot, balls)
    if improve:
        order = two_opt(depot, order)
    route = split_capacity(depot, order, C)
    dist, ang = route_cost(route, p)
    n_unload = math.ceil(len(balls) / C)
    t_move = dist / p['v'] + ang / p['omega']
    t_pick = len(balls) * p['t_pick']
    t_unl = n_unload * p['t_unload']
    T = t_move + t_pick + t_unl
    E = (p['P_drive'] * t_move + p['P_intake'] * t_pick
         + (p['P_compute'] + p['P_idle'] + p.get('P_infra', 0.0)) * T) / 3600
    return dict(time_s=T, dist_m=dist, energy_Wh=E)

def sweep(balls, depot, p, C, box):
    L, W = enclosure(p)
    if box:
        xs = [b[0] for b in balls]; ys = [b[1] for b in balls]
        x0, x1 = max(0, min(xs) - p['w'] / 2), min(L, max(xs) + p['w'] / 2)
        y0, y1 = max(0, min(ys) - p['w'] / 2), min(W, max(ys) + p['w'] / 2)
    else:
        x0, x1, y0, y1 = 0, L, 0, W
    lanes = max(1, math.ceil((y1 - y0) / p['w']))
    # waypoints of lawn-mower path along x
    pts = [depot]
    for i in range(lanes):
        y = y0 + p['w'] / 2 + i * p['w']
        y = min(y, y1)
        if i % 2 == 0:
            pts += [(x0, y), (x1, y)]
        else:
            pts += [(x1, y), (x0, y)]
    # simulate pickup along path segments; insert depot returns when hopper full
    remaining = list(balls); held = 0; route = [depot]; unloads = 0
    for a, b in zip(pts, pts[1:]):
        seglen = d(a, b)
        hit = []
        for q in remaining:
            if seglen < 1e-9:
                continue
            # projection of q on segment
            t = ((q[0]-a[0])*(b[0]-a[0]) + (q[1]-a[1])*(b[1]-a[1])) / seglen**2
            if 0 <= t <= 1:
                proj = (a[0] + t*(b[0]-a[0]), a[1] + t*(b[1]-a[1]))
                if d(proj, q) <= p['w'] / 2 + 1e-9:
                    hit.append((t, q, proj))
        hit.sort()
        done = False
        for t, q, proj in hit:
            remaining.remove(q); held += 1
            if box and not remaining:      # detection-aware: stop once last known ball is in
                route.append(proj); done = True; break
            if held == C:
                route += [proj, depot]; held = 0; unloads += 1
                if box and not remaining:
                    done = True; break
                route.append(proj)
        if done:
            break
        route.append(b)
    route.append(depot)
    dist, ang = route_cost(route, p)
    if held > 0:
        unloads += 1                       # final unload only if hopper not empty (v1 bug: always +1)
    t_move = dist / p['v'] + ang / p['omega']
    T = t_move + unloads * p['t_unload']
    # intake roller runs the whole time the robot moves in sweep mode
    E = ((p['P_drive'] + p['P_intake']) * t_move + (p['P_compute'] + p['P_idle']) * T) / 3600
    return dict(time_s=T, dist_m=dist, energy_Wh=E, missed=len(remaining))


def onboard(balls, depot, p, C, R, r, rng, max_pass=6):
    """On-board camera: survey lawn-mower pass with lane spacing 2R, each ball detected with prob r
    per pass; detected balls collected with NN+2-opt tour; repeat for missed balls.
    Pessimistic: no opportunistic detection while touring."""
    L, W = enclosure(p)
    lanes = max(1, math.ceil(W / (2 * R)))
    pts = [depot]
    for i in range(lanes):
        y = min(R + i * 2 * R, W)
        pts += [(0, y), (L, y)] if i % 2 == 0 else [(L, y), (0, y)]
    pts.append(depot)
    sd, sa = route_cost(pts, p)
    t_survey = sd / p['v'] + sa / p['omega']
    remaining = list(balls); T = E = 0.0; npass = 0
    while remaining and npass < max_pass:
        npass += 1
        seen = [b for b in remaining if rng.random() < r]
        T += t_survey
        E += (p['P_drive'] + p['P_compute'] + p['P_idle'] + p.get('P_infra', 0.0)) * t_survey / 3600
        if seen:
            res = targeted(seen, depot, p, C, True)
            T += res['time_s']; E += res['energy_Wh']
            for b in seen:
                remaining.remove(b)
    return dict(time_s=T, energy_Wh=E, missed=len(remaining), passes=npass)

def checks(p):
    """Minimal sanity checks defined before running the experiment."""
    depot = (0.0, 0.0)
    # C1: one ball straight ahead at 6 m -> 12 m path, one 180 deg turn, 1 pick, 1 unload
    r = targeted([(6.0, 0.0)], depot, p, C=90, improve=False)
    exp_T = 12 / p['v'] + math.pi / p['omega'] + p['t_pick'] + p['t_unload']
    assert abs(r['time_s'] - exp_T) < 1e-6, (r, exp_T)
    assert abs(r['dist_m'] - 12) < 1e-9
    # C2: 2-opt never longer than NN
    rng = random.Random(1)
    b = gen_balls(40, 'uniform', p, rng)
    assert targeted(b, depot, p, 999, True)['dist_m'] <= targeted(b, depot, p, 999, False)['dist_m'] + 1e-6
    # C3: blind sweep path length >= area / w (coverage lower bound) and misses no balls
    L, W = enclosure(p)
    s = sweep(b, depot, p, 999, box=False)
    assert s['dist_m'] >= L * W / p['w'] * 0.95, s
    assert s['missed'] == 0, s
    # C4: smaller hopper -> not shorter path
    assert targeted(b, depot, p, 10, False)['dist_m'] >= targeted(b, depot, p, 999, False)['dist_m'] - 1e-6
    # C5: on-board detection (r=1) never faster than oracle targeted
    ob = onboard(b, depot, p, 999, 3.0, 1.0, random.Random(3))
    assert ob['time_s'] >= targeted(b, depot, p, 999, True)['time_s'] - 1e-6 and ob['missed'] == 0
    # C6: detection-aware box sweep collects everything and is never longer than blind sweep
    s4 = sweep(b, depot, p, 999, box=True)
    assert s4['missed'] == 0 and s4['dist_m'] <= s['dist_m'] + 1e-6
    return 'checks passed: C1 single-ball closed form, C2 2-opt<=NN, C3 sweep>=A/w & no misses, C4 capacity monotone, C5 onboard>=oracle, C6 box<=blind'

def run(trials=200, seed=42):
    p = PARAMS
    print(checks(p))
    L, W = enclosure(p)
    print(f'enclosure {L:.2f} x {W:.2f} m = {L*W:.1f} m^2; depot at (0, W/2) behind near baseline')
    depot = (0.0, W / 2)
    rows = []
    for dist in ['uniform', 'drill']:
        for n in [30, 60, 90]:
            for C in [90, 30]:
                rng = random.Random(seed + n + C + (0 if dist == 'uniform' else 1000))
                acc = {k: [] for k in ['S1', 'S2', 'S3', 'S4']}
                for _ in range(trials):
                    balls = gen_balls(n, dist, p, rng)
                    acc['S1'].append(targeted(balls, depot, p, C, False))
                    acc['S2'].append(targeted(balls, depot, p, C, True))
                    acc['S3'].append(sweep(balls, depot, p, C, False))
                    acc['S4'].append(sweep(balls, depot, p, C, True))
                for s, res in acc.items():
                    T = [r['time_s'] for r in res]; E = [r['energy_Wh'] for r in res]
                    rows.append(dict(dist=dist, n=n, C=C, strategy=s,
                                     time_min_mean=statistics.mean(T) / 60,
                                     time_min_sd=statistics.stdev(T) / 60,
                                     energy_Wh_mean=statistics.mean(E),
                                     Wh_per_ball=statistics.mean(E) / n,
                                     balls_per_min=n / (statistics.mean(T) / 60),
                                     missed_mean=statistics.mean(r.get('missed', 0) for r in res)))
    return rows

if __name__ == '__main__':
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    rows = run(trials)
    hdr = f"{'dist':8}{'N':>4}{'C':>4} {'strat':5}{'T_mean(min)':>12}{'T_sd':>7}{'E(Wh)':>8}{'Wh/ball':>9}{'balls/min':>10}{'missed':>7}"
    print(hdr)
    for r in rows:
        print(f"{r['dist']:8}{r['n']:>4}{r['C']:>4} {r['strategy']:5}{r['time_min_mean']:12.2f}{r['time_min_sd']:7.2f}"
              f"{r['energy_Wh_mean']:8.2f}{r['Wh_per_ball']:9.3f}{r['balls_per_min']:10.2f}{r['missed_mean']:7.2f}")
    json.dump(dict(params={k: v for k, v in PARAMS.items()}, trials=trials, rows=rows),
              open('results.json', 'w'), indent=1)
