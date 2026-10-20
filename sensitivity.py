"""One-at-a-time sensitivity for N=60 uniform, C=90 (S2 targeted 2-opt vs S3 blind sweep)."""
import random, statistics, sim
base = dict(sim.PARAMS)
cases = [('baseline', {}), ('v=0.3', {'v':0.3}), ('v=1.0', {'v':1.0}), ('t_pick=3s', {'t_pick':3.0}),
         ('t_pick=0.3s', {'t_pick':0.3}), ('w=0.6m', {'w':0.6}), ('w=1.0m', {'w':1.0}),
         ('P_compute=6.4W (Pi4 stress)', {'P_compute':6.4}), ('P_compute=0.9W (ESP32-CAM)', {'P_compute':0.9}), ('P_drive=7.2W (2xN20 stall)', {'P_drive':7.2}), ('v=1.0 and w=1.0', {'v':1.0,'w':1.0})]
print(f"{'case':30}{'S2 T(min)':>10}{'S2 Wh':>8}{'S3 T(min)':>10}{'S3 Wh':>8}")
for name, ov in cases:
    p = dict(base); p.update(ov); sim.PARAMS.clear(); sim.PARAMS.update(p)
    L, W = sim.enclosure(p); depot = (0.0, W/2); rng = random.Random(42)
    s2, s3 = [], []
    for _ in range(200):
        b = sim.gen_balls(60, 'uniform', p, rng)
        s2.append(sim.targeted(b, depot, p, 90, True)); s3.append(sim.sweep(b, depot, p, 90, False))
    m = lambda r, k: statistics.mean(x[k] for x in r)
    print(f"{name:30}{m(s2,'time_s')/60:10.2f}{m(s2,'energy_Wh'):8.2f}{m(s3,'time_s')/60:10.2f}{m(s3,'energy_Wh'):8.2f}")
