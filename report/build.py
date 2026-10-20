"""Build the Assignment-2 (Project Idea 11) report as HTML with inline SVG figures, then print to PDF via Chrome.
All model numbers are parsed from experiments/ball-retrieval-sim/{grid.txt,sensitivity.txt} or recomputed with sim.py.
"""
import os, re, sys, math, random, subprocess, html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
SIMDIR = ROOT
sys.path.insert(0, SIMDIR)
import sim  # noqa

# ----------------------------------------------------------------- data
def parse_grid():
    rows = []
    for line in open(os.path.join(SIMDIR, 'grid.txt')):
        m = re.match(r'^(uniform|drill)\s+(\d+)\s+(.+?)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$', line)
        if m:
            rows.append(dict(layout=m[1], C=int(m[2]), design=m[3].strip(), T=float(m[4]), E=float(m[5]), miss=float(m[6])))
    return rows

def parse_sens():
    rows = []
    for line in open(os.path.join(SIMDIR, 'sensitivity.txt')):
        m = re.match(r'^(.+?)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*$', line)
        if m and not line.startswith('case'):
            rows.append(dict(case=m[1].strip(), T2=float(m[2]), E2=float(m[3]), T3=float(m[4]), E3=float(m[5])))
    return rows

GRID = parse_grid(); SENS = parse_sens()
def g(layout, C, prefix):
    for r in GRID:
        if r['layout'] == layout and r['C'] == C and r['design'].startswith(prefix):
            return r
    raise KeyError((layout, C, prefix))

# ----------------------------------------------------------------- references (IEEE, numbered by first citation)
REFS = {
 'sari': 'D. Sarıcalar, K. F. Çaybaşı, B. Öztürk, and V. Sezer, "Development of an autonomous tennis ball retriever robot," <i>Mugla J. Sci. Technol.</i>, vol. 6, pp. 36–44, 2020, doi: 10.22531/muglajsci.660496.',
 'toyota': 'Toyota Times, "Toyota\'s Field Support Robots with an \'Athletes-First\' approach (Part 1)," Dec. 8, 2021. [Online]. Available: https://toyotatimes.jp/en/spotlights/supported_tokyo2020/056.html',
 'ali': 'M. F. Ali, C. K. Lam, K. V. Ch\'ng, K. Sundaraj, and W.-H. Tan, "Design and development of path planning techniques for a tennis ball retriever robot," <i>J. Telecommun. Electron. Comput. Eng.</i>, vol. 10, no. 1-15, pp. 59–65, 2018.',
 'cao': 'X. Cao <i>et al.</i>, "Research on autonomous picking algorithm for table tennis balls based on machine vision," <i>Front. Sci. Eng.</i>, vol. 2, no. 9, 2022.',
 'gu': 'S. Gu, W. Zeng, Y. Jia, and Z. Yan, "Intelligent tennis robot based on a deep neural network," <i>Appl. Sci.</i>, vol. 9, no. 18, p. 3746, 2019, doi: 10.3390/app9183746.',
 'keca': 'D. Keča, I. Kunović, J. Matić, and A. Sović Kržić, "Ball detection using deep learning implemented on an educational robot based on Raspberry Pi," <i>Sensors</i>, vol. 23, no. 8, p. 4071, 2023, doi: 10.3390/s23084071.',
 'qeng': 'Q-engineering, "YoloV8-ncnn-Raspberry-Pi-4," GitHub repository (benchmark table). [Online]. Available: https://github.com/Qengineering/YoloV8-ncnn-Raspberry-Pi-4',
 'zhang': 'T. Zhang, X. Zhang, Y. Yang, Z. Wang, and G. Wang, "Efficient golf ball detection and tracking based on convolutional neural networks and Kalman filter," arXiv:2012.09393, 2020.',
 'ortools': 'Google, "Capacitated vehicle routing problem," OR-Tools documentation. [Online]. Available: https://developers.google.com/optimization/routing/cvrp',
 'essam': 'Z. Essam <i>et al.</i>, "Development of autonomous table tennis ball retrieving robot," <i>Delta Univ. Sci. J.</i>, vol. 6, no. 1, pp. 247–254, 2023, doi: 10.21608/dusj.2023.291056.',
 'pereira': 'N. Pereira, F. Ribeiro, G. Lopes, D. Whitney, and J. Lino, "Autonomous golf ball picking robot design and development," <i>Ind. Robot</i>, vol. 39, no. 6, pp. 541–550, 2012, doi: 10.1108/01439911211268660.',
 'itf': 'International Tennis Federation, <i>ITF Rules of Tennis 2026</i>. [Online]. Available: https://www.itftennis.com/media/7221/2026-rules-of-tennis-english.pdf',
 'ittf': 'International Table Tennis Federation, <i>ITTF Statutes 2026</i>, 54th ed., 2026. [Online]. Available: https://db.ittf.com/sites/default/files/public/2026-02/2026_Statutes_v1_consolidated_tc.pdf',
 'randa': 'The R&amp;A and USGA, <i>The Equipment Rules</i>, v1.3, eff. Dec. 1, 2024.',
 'newatlas': 'B. Coxworth, "This robot is designed to clear the court," <i>New Atlas</i>, Apr. 24, 2018. [Online]. Available: https://newatlas.com/tennibot-tennis-ball-robot/54354/',
 'perma': 'permacomputing.net, "SBC power consumption." [Online]. Available: https://www.permacomputing.net/SBC_power_consumption/',
 'toboids': 'Toboids, "N20 12V 300RPM micro metal gear motor with encoder," product page. [Online]. Available: https://toboids.com/product/n20-12v-300rpm-micro-metal-gear-motor-with-encoder/',
 'robocraze': 'Robocraze, product listings (Raspberry Pi 4/5, TB6612FNG, HC-SR04, VL53L0X, chassis kit, 11.1 V Li-ion pack), accessed Oct. 20, 2026. [Online]. Available: https://robocraze.com',
 'robobazar': 'Robobazar, "ESP32-CAM WiFi Bluetooth camera module," accessed Oct. 20, 2026. [Online]. Available: https://robobazar.in/product/esp32-cam-wifi-bluetooth-camera-module-2mp/',
 'rpiprice': 'Raspberry Pi Ltd., "A new 3GB Raspberry Pi 4 for $83.75, and more memory-driven price increases," 2026. [Online]. Available: https://www.raspberrypi.com/news/',
 'tennibot': 'Tennibot, "Specifications" and "Tennis ball collector" product pages, accessed Oct. 20, 2026. [Online]. Available: https://www.tennibot.com/specs/',
 'seeker': 'Potent Tennis, "SeekerBot 2.0," product page, accessed Oct. 20, 2026. [Online]. Available: https://potenttennis.com/products/seekerbot',
 'toro': 'The Toro Company, "Range Pro 100 (30931US)," product page. [Online]. Available: https://www.toro.com/en/product/30931US',
 'itf25': 'International Tennis Federation, <i>ITF Rules of Tennis 2025</i>, Rules 2, 23 and 26. [Online]. Available: https://www.blta.bm/wp-content/uploads/2025/02/2025-rules-of-tennis-english.pdf',
 'express': '"Wimbledon\'s record number of ball kids," <i>Express</i>, Jul. 10, 2026. [Online]. Available: https://www.express.co.uk/sport/tennis/2227890/wimbledons-record-number-ball-kids',
 'indiatoday': '"India\'s 2036 Olympics bid enters key phase," <i>India Today</i>, Jun. 24, 2026. [Online]. Available: https://www.indiatoday.in/sports/other-sports/story/india-2036-olympics-bid-ioc-strategic-dialogue-host-vote-2029-2933570-2026-06-24',
 'cwg': 'Commonwealth Sport, "Amdavad 2030." [Online]. Available: https://www.commonwealthsport.com/commonwealth-games/amdavad-2030',
 'dezeen': '"Sardar Vallabhbhai Patel Sports Enclave masterplan," <i>Dezeen</i>, Feb. 23, 2026. [Online]. Available: https://www.dezeen.com/2026/02/23/sardar-vallabhbhai-patel-sports-enclave-bdp-cox-architecture-collage-design/',
 'heat': '"Gujarat heatwave: red alert in Ahmedabad, Gandhinagar," <i>Indian Express</i>, May 23, 2024. [Online]. Available: https://indianexpress.com/article/cities/ahmedabad/gujarat-heatwave-red-alert-ahmedabad-gandhinagar-9348224/',
 'iso': 'ISO 13482:2014, <i>Robots and robotic devices — Safety requirements for personal care robots</i>. Geneva: ISO, 2014.',
}
ORDER = []
def c(*keys):
    nums = []
    for k in keys:
        if k not in REFS: raise KeyError(k)
        if k not in ORDER: ORDER.append(k)
        nums.append(ORDER.index(k) + 1)
    return '[' + ', '.join(str(n) for n in nums) + ']'

# ----------------------------------------------------------------- SVG helpers
def esc(s): return html.escape(str(s))

def hbar(title, items, unit, width=640, color='#2f6db5', maxv=None, note=''):
    """items: list of (label, value, color or None)"""
    lh, top, left, right = 22, 30, 250, 60
    h = top + lh * len(items) + 30
    maxv = maxv or max(v for _, v, _ in items) * 1.08
    sc = (width - left - right) / maxv
    out = [f'<svg viewBox="0 0 {width} {h}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial" font-size="11">',
           f'<text x="{width/2}" y="16" text-anchor="middle" font-weight="bold" font-size="12">{esc(title)}</text>']
    # grid
    step = 10 ** math.floor(math.log10(maxv)); step = step if maxv / step > 4 else step / 2
    v = 0
    while v <= maxv:
        x = left + v * sc
        out.append(f'<line x1="{x:.1f}" y1="{top-4}" x2="{x:.1f}" y2="{top+lh*len(items)}" stroke="#ddd"/>')
        out.append(f'<text x="{x:.1f}" y="{top+lh*len(items)+13}" text-anchor="middle" fill="#555">{v:g}</text>')
        v += step
    for i, (lab, val, col) in enumerate(items):
        y = top + i * lh
        out.append(f'<text x="{left-6}" y="{y+14}" text-anchor="end">{esc(lab)}</text>')
        out.append(f'<rect x="{left}" y="{y+3}" width="{val*sc:.1f}" height="{lh-7}" fill="{col or color}"/>')
        out.append(f'<text x="{left+val*sc+4:.1f}" y="{y+14}">{val:.1f}</text>')
    out.append(f'<text x="{left+(width-left-right)/2}" y="{h-2}" text-anchor="middle" fill="#333">{esc(unit)}{esc(note)}</text>')
    out.append('</svg>')
    return '\n'.join(out)

def trajectories():
    """Three panels for one random layout of 30 balls (uniform): oracle tour, on-board survey+tour, blind sweep w=1.0 m."""
    p = dict(sim.PARAMS); L, W = sim.enclosure(p); depot = (0.0, W / 2)
    rng = random.Random(5); balls = sim.gen_balls(30, 'uniform', p, rng)
    s = 7.0; pw, ph = L * s, W * s; gap = 14
    def court(ox, oy):
        o = [f'<rect x="{ox}" y="{oy}" width="{pw:.1f}" height="{ph:.1f}" fill="#e9f3e6" stroke="#666"/>']
        cx0, cy0 = ox + p['runback'] * s, oy + p['siderun'] * s
        o.append(f'<rect x="{cx0:.1f}" y="{cy0:.1f}" width="{p["court_L"]*s:.1f}" height="{p["court_W"]*s:.1f}" fill="#4f8fc0" fill-opacity="0.25" stroke="#fff" stroke-width="1.5"/>')
        o.append(f'<line x1="{cx0+p["court_L"]*s/2:.1f}" y1="{cy0:.1f}" x2="{cx0+p["court_L"]*s/2:.1f}" y2="{cy0+p["court_W"]*s:.1f}" stroke="#333" stroke-width="2"/>')
        return o
    def pts(route, ox, oy, col, wdt=1.2, dash=''):
        d = ' '.join(f'{ox+x*s:.1f},{oy+y*s:.1f}' for x, y in route)
        return f'<polyline points="{d}" fill="none" stroke="{col}" stroke-width="{wdt}" {dash}/>'
    def balls_svg(ox, oy, bs):
        return ''.join(f'<circle cx="{ox+x*s:.1f}" cy="{oy+y*s:.1f}" r="2.6" fill="#e5d800" stroke="#555" stroke-width="0.5"/>' for x, y in bs)
    def depot_svg(ox, oy):
        return f'<rect x="{ox+depot[0]*s-4:.1f}" y="{oy+depot[1]*s-4:.1f}" width="8" height="8" fill="#c0392b"/>'
    total_w = 3 * pw + 2 * gap + 20; total_h = ph + 30
    out = [f'<svg viewBox="0 0 {total_w:.0f} {total_h:.0f}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial" font-size="10">']
    oy = 20
    # (a) oracle
    ox = 10
    order = sim.two_opt(depot, sim.nn_order(depot, balls)); route = sim.split_capacity(depot, order, 30)
    ra = sim.targeted(balls, depot, p, 30, True)
    out += court(ox, oy); out.append(pts(route, ox, oy, '#c0392b', 1.4)); out.append(balls_svg(ox, oy, balls)); out.append(depot_svg(ox, oy))
    out.append(f'<text x="{ox}" y="{oy-6}" font-weight="bold">(a) Design A: tour {ra["dist_m"]:.0f} m, {ra["time_s"]/60:.1f} min</text>')
    # (b) onboard survey lanes R=3 then tour
    ox = 10 + pw + gap; R = 3.0
    lanes = math.ceil(W / (2 * R)); sv = [depot]
    for i in range(lanes):
        y = min(R + i * 2 * R, W); sv += [(0, y), (L, y)] if i % 2 == 0 else [(L, y), (0, y)]
    sv.append(depot)
    out += court(ox, oy)
    out.append(pts(sv, ox, oy, '#555', 1.1, 'stroke-dasharray="4,3"')); out.append(pts(route, ox, oy, '#c0392b', 1.2))
    out.append(balls_svg(ox, oy, balls)); out.append(depot_svg(ox, oy))
    out.append(f'<text x="{ox}" y="{oy-6}" font-weight="bold">(b) Design B: survey (dashed) + tour</text>')
    # (c) blind sweep w=1.0
    ox = 10 + 2 * (pw + gap); w = 1.0
    lanesn = math.ceil(W / w); sw = [depot]
    for i in range(lanesn):
        y = min(w / 2 + i * w, W); sw += [(0, y), (L, y)] if i % 2 == 0 else [(L, y), (0, y)]
    sw.append(depot)
    p2 = dict(p); p2['w'] = 1.0; rc = sim.sweep(balls, depot, p2, 30, False)
    out += court(ox, oy); out.append(pts(sw, ox, oy, '#2f6db5', 0.8)); out.append(balls_svg(ox, oy, balls)); out.append(depot_svg(ox, oy))
    out.append(f'<text x="{ox}" y="{oy-6}" font-weight="bold">(c) Design C, w = 1.0 m: {rc["dist_m"]:.0f} m, {rc["time_s"]/60:.1f} min</text>')
    out.append('</svg>')
    return '\n'.join(out), ra, rc

def robot_sketch():
    return '''<svg viewBox="0 0 640 250" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial" font-size="10.5">
<text x="160" y="14" text-anchor="middle" font-weight="bold" font-size="12">(a) Top view (concept, not to scale)</text>
<rect x="70" y="40" width="180" height="150" rx="8" fill="#f4f4f4" stroke="#333"/>
<rect x="52" y="120" width="18" height="44" fill="#333"/><rect x="250" y="120" width="18" height="44" fill="#333"/>
<circle cx="160" cy="182" r="6" fill="#777"/>
<rect x="80" y="26" width="160" height="16" rx="7" fill="#e67e22" stroke="#333"/>
<line x1="70" y1="40" x2="40" y2="20" stroke="#333" stroke-width="2"/><line x1="250" y1="40" x2="280" y2="20" stroke="#333" stroke-width="2"/>
<rect x="100" y="60" width="120" height="55" fill="#fff8c4" stroke="#333"/><text x="160" y="91" text-anchor="middle">Hopper (C = 15–30)</text>
<rect x="148" y="44" width="24" height="12" fill="#2c3e50"/>
<rect x="85" y="125" width="60" height="22" fill="#d5e8f7" stroke="#333"/><text x="115" y="140" text-anchor="middle">MCU + driver</text>
<rect x="175" y="125" width="60" height="22" fill="#d9f2d9" stroke="#333"/><text x="205" y="140" text-anchor="middle">3S Li-ion</text>
<circle cx="95" cy="48" r="4" fill="#8e44ad"/><circle cx="225" cy="48" r="4" fill="#8e44ad"/>
<text x="300" y="34">← roller intake (motorised, spins inward)</text>
<text x="300" y="54">← camera on mast (ESP32-CAM / Pi Cam)</text>
<text x="300" y="70">← ultrasonic / ToF safety sensors (purple)</text>
<text x="300" y="86">← funnel guide arms centre the ball</text>
<text x="300" y="146">← differential drive: 2 geared DC motors</text>
<text x="300" y="162">   with encoders + rear caster</text>
<text x="300" y="196" font-style="italic" fill="#555">Tennis ball Ø 6.54–6.86 cm, 56–59.4 g (ITF)</text>
<text x="300" y="212" font-style="italic" fill="#555">→ roller-to-floor gap must be &lt; ball Ø</text>
<text x="300" y="228" font-style="italic" fill="#555">30 balls ≈ 1.7 kg payload (own arithmetic)</text>
</svg>'''

def side_sketch():
    return '''<svg viewBox="0 0 640 150" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial" font-size="10.5">
<text x="320" y="14" text-anchor="middle" font-weight="bold" font-size="12">(b) Side view of roller intake (concept)</text>
<line x1="20" y1="130" x2="620" y2="130" stroke="#333" stroke-width="2"/>
<circle cx="120" cy="113" r="17" fill="#e5d800" stroke="#555"/><text x="120" y="148" text-anchor="middle">ball</text>
<circle cx="190" cy="92" r="22" fill="#e67e22" stroke="#333"/><text x="190" y="96" text-anchor="middle">roller</text>
<path d="M 205 80 A 26 26 0 0 0 175 74" fill="none" stroke="#c0392b" stroke-width="2" marker-end="url(#ar)"/>
<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#c0392b"/></marker></defs>
<path d="M 170 128 L 300 70" stroke="#333" stroke-width="3"/><text x="250" y="118">curved ramp</text>
<rect x="300" y="40" width="150" height="85" fill="#fff8c4" stroke="#333"/><text x="375" y="88" text-anchor="middle">hopper</text>
<rect x="300" y="125" width="150" height="5" fill="#333"/>
<line x1="470" y1="20" x2="470" y2="128" stroke="#888" stroke-dasharray="3,3"/>
<text x="480" y="60">drive direction ←</text><text x="480" y="78">roller tip speed &gt; robot speed</text><text x="480" y="96">pins ball against ramp</text>
</svg>'''

def block_diagram():
    box = lambda x, y, w, h, t, f='#eef4fb': f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{f}" stroke="#2f6db5"/>' + ''.join(
        f'<text x="{x+w/2}" y="{y+h/2-6*(len(t.split("|"))-1)+i*12+4}" text-anchor="middle">{esc(s)}</text>' for i, s in enumerate(t.split('|')))
    arr = lambda x1, y1, x2, y2: f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#333" stroke-width="1.3" marker-end="url(#a2)"/>'
    o = ['<svg viewBox="0 0 660 230" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial" font-size="10.5">',
         '<defs><marker id="a2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#333"/></marker></defs>',
         '<text x="10" y="14" font-weight="bold" font-size="12">SENSING</text><text x="250" y="14" font-weight="bold" font-size="12">PERCEPTION &amp; PLANNING</text><text x="520" y="14" font-weight="bold" font-size="12">ACTUATION</text>',
         box(5, 25, 150, 40, 'Camera (ESP32-CAM,|Pi Cam or overhead)'),
         box(5, 85, 150, 40, 'Wheel encoders + IMU|(optional UWB anchors)'),
         box(5, 145, 150, 40, 'Ultrasonic / ToF|range sensors'),
         box(190, 25, 150, 40, 'Ball detection|HSV+Hough or YOLO-nano', '#fdf2e0'),
         box(190, 85, 150, 40, 'Pose estimate (EKF)|+ ball → court frame', '#fdf2e0'),
         box(190, 145, 150, 40, 'Safety monitor|stop if person/obstacle', '#fdecea'),
         box(375, 55, 130, 50, 'Planner|NN + 2-opt tour|hopper-capacity returns', '#fdf2e0'),
         box(375, 135, 130, 40, 'Motion control|PID heading + speed', '#fdf2e0'),
         box(530, 25, 120, 40, 'Motor driver →|2 geared DC motors', '#e8f6e8'),
         box(530, 95, 120, 40, 'Intake roller|(or suction for TT)', '#e8f6e8'),
         box(530, 165, 120, 40, 'Hopper → depot|unload when full', '#e8f6e8'),
         arr(155, 45, 190, 45), arr(155, 105, 190, 105), arr(155, 165, 190, 165),
         arr(340, 45, 375, 70), arr(340, 105, 375, 90), arr(440, 105, 440, 135), arr(340, 165, 375, 158),
         arr(505, 150, 530, 50), arr(505, 155, 530, 115), arr(590, 135, 590, 165),
         '<text x="10" y="222" fill="#555" font-style="italic">Data/AI component: detector (classical CV or CNN) + route optimiser; logging of time, current and pick events for evaluation.</text>',
         '</svg>']
    return '\n'.join(o)

def flowchart():
    o = ['<svg viewBox="0 0 670 235" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial" font-size="10.5">',
         '<defs><marker id="a3" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#333"/></marker></defs>']
    def b(x, y, w, h, t, shape='rect', f='#eef4fb'):
        if shape == 'dia':
            o.append(f'<polygon points="{x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}" fill="#fff8c4" stroke="#333"/>')
        else:
            o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{12 if shape=="round" else 4}" fill="{f}" stroke="#333"/>')
        lines = t.split('|')
        for i, s_ in enumerate(lines):
            o.append(f'<text x="{x+w/2}" y="{y+h/2+4-6*(len(lines)-1)+12*i}" text-anchor="middle">{esc(s_)}</text>')
    def poly(pts_, arrow=True):
        d = ' '.join(f'{x},{y}' for x, y in pts_)
        o.append(f'<polyline points="{d}" fill="none" stroke="#333" {"marker-end=\"url(#a3)\"" if arrow else ""}/>')
    lab = lambda x, y, t: o.append(f'<text x="{x}" y="{y}" font-size="9.5" fill="#333">{esc(t)}</text>')
    b(10, 45, 85, 34, 'START|(at depot)', 'round', '#e8f6e8'); poly([(95, 62), (120, 62)])
    b(120, 45, 105, 34, 'Capture frame|detect balls'); poly([(225, 62), (250, 62)])
    b(250, 30, 100, 64, 'Balls|visible?', 'dia'); poly([(350, 62), (380, 62)]); lab(353, 56, 'yes')
    b(380, 45, 120, 34, 'Plan NN + 2-opt|drive to nearest ball'); poly([(500, 62), (530, 62)])
    b(530, 45, 120, 34, 'Intake ball|hopper += 1'); poly([(590, 79), (590, 110)])
    b(530, 110, 120, 54, 'Hopper full?', 'dia')
    poly([(650, 137), (660, 137), (660, 12), (172, 12), (172, 45)]); lab(560, 24, 'no → next ball')
    poly([(590, 164), (590, 180)]); lab(596, 176, 'yes')
    b(530, 180, 120, 30, 'Return to depot, unload')
    poly([(530, 195), (160, 195), (160, 79)])
    poly([(300, 94), (300, 108)]); lab(306, 104, 'no')
    b(250, 108, 100, 50, 'Area|explored?', 'dia')
    poly([(250, 133), (195, 133), (195, 79)]); lab(222, 128, 'no')
    poly([(350, 133), (380, 133)]); lab(355, 128, 'yes')
    b(380, 118, 120, 30, 'Return, unload, STOP', 'round', '#fdecea')
    o.append('<text x="10" y="228" fill="#c0392b" font-size="10">Safety interrupt active in every state: obstacle or person within d_safe → stop, wait, re-plan.</text>')
    o.append('</svg>')
    return '\n'.join(o)

# ----------------------------------------------------------------- content
A30 = g('uniform', 30, 'A oracle overhead cam, robot-only'); A30L = g('uniform', 30, 'A oracle overhead cam, +20')
B5 = g('uniform', 30, 'B on-board R=5'); B3 = g('uniform', 30, 'B on-board R=3 m r=0.95'); B38 = g('uniform', 30, 'B on-board R=3 m r=0.8'); B2 = g('uniform', 30, 'B on-board R=2')
C03 = g('uniform', 30, 'C blind sweep w=0.3'); C06 = g('uniform', 30, 'C blind sweep w=0.6'); C10 = g('uniform', 30, 'C blind sweep w=1.0')
A15 = g('uniform', 15, 'A oracle overhead cam, robot-only'); D_A30 = g('drill', 30, 'A oracle overhead cam, robot-only'); D_S4 = g('drill', 30, 'S4'); D_C10 = g('drill', 30, 'C blind sweep w=1.0')
SB = {r['case']: r for r in SENS}

traj_svg, RA, RC = trajectories()

fig_time = hbar('Fig. 5  Time to clear 60 balls (uniform layout, hopper C = 30, mean of 200 trials)', [
    ('A: overhead camera (all balls known)', A30['T'], '#27ae60'),
    ('B: on-board, R = 5 m, recall 0.95', B5['T'], '#f39c12'),
    ('B: on-board, R = 3 m, recall 0.95', B3['T'], '#f39c12'),
    ('B: on-board, R = 3 m, recall 0.80', B38['T'], '#e67e22'),
    ('B: on-board, R = 2 m, recall 0.70', B2['T'], '#d35400'),
    ('C: blind sweep, intake 1.0 m', C10['T'], '#2f6db5'),
    ('C: blind sweep, intake 0.6 m', C06['T'], '#2f6db5'),
    ('C: blind sweep, intake 0.3 m', C03['T'], '#2f6db5')], 'minutes')
fig_energy = hbar('Fig. 6  Energy per clearing (same runs; robot-only unless stated)', [
    ('A: robot only', A30['E'], '#27ae60'), ('A: robot + 20 W laptop', A30L['E'], '#16a085'),
    ('B: R = 5 m, recall 0.95', B5['E'], '#f39c12'), ('B: R = 2 m, recall 0.70', B2['E'], '#d35400'),
    ('C: sweep 1.0 m', C10['E'], '#2f6db5'), ('C: sweep 0.3 m', C03['E'], '#2f6db5')], 'watt-hours (one 3S 2200 mAh pack ≈ 24.4 Wh)')
sens_items = [('baseline', 'baseline'), ('v=1.0', 'speed 0.6 → 1.0 m/s'), ('v=0.3', 'speed 0.6 → 0.3 m/s'), ('t_pick=3s', 'pick dwell 1 → 3 s'), ('w=1.0m', 'intake width 0.3 → 1.0 m'), ('v=1.0 and w=1.0', 'speed 1.0 m/s + width 1.0 m')]
fig_sens = hbar('Fig. 7  Sensitivity: design A tour (green) vs design C sweep (blue), N = 60, C = 90', sum([[(f'{lab} – A', SB[k]['T2'], '#27ae60'), (f'{lab} – C', SB[k]['T3'], '#2f6db5')] for k, lab in sens_items], []), 'minutes')

cover_focus = 'Athletes &amp; Coaches (training efficiency) · Organisers (event operations, ball-crew heat exposure) · Sport technologists · Sustainability'

def section(num, title, body):
    return f'''<table class="sec"><thead><tr><td><div class="hdr"><span>Section {num} – {title}</span><span class="crs">Assignment 2 · Idea 11</span></div></td></tr></thead>
<tbody><tr><td>{body}</td></tr></tbody></table>'''

S0 = f'''<div class="cover">
<p class="inst">BITS Pilani – Introduction to Sports Engineering<br>(Take-Home Assignment #2)</p>
<p>Semester: <b>I</b> &nbsp;&nbsp; Year: <b>2026-27</b></p>
<table class="kv">
<tr><td>Student Name(s)</td><td><span class="ph">[Student 1 name]</span>, <span class="ph">[Student 2 name]</span></td></tr>
<tr><td>ID No(s)</td><td><span class="ph">[20XXXXXXXXXX]</span>, <span class="ph">[20XXXXXXXXXX]</span></td></tr>
<tr><td>Title of Project</td><td><b>Autonomous Ball-Retrieval Robot for Sports Training and Major Events: a simulation-based comparison of detection, path-planning and pickup designs</b> (Project Idea 11)</td></tr>
<tr><td>Targeted focus</td><td>{cover_focus}</td></tr>
<tr><td>Primary sport</td><td>Tennis (table tennis and golf discussed as variants)</td></tr>
<tr><td>Deliverables</td><td>Concept design; Python Monte-Carlo simulator (code + outputs); design comparison on retrieval time, energy, cost and operating efficiency; deployment assessment for Ahmedabad 2030 / India 2036</td></tr>
</table>
{robot_sketch()}
<p class="cap">Fig. 1  Concept of the proposed tennis-ball retrieval robot (own concept sketch).</p>
</div>'''

S1 = f'''<h3>Motivation and real-world relevance</h3>
<p class="mot">In tennis training a coach or player repeatedly stops practice to collect dozens of balls; published robot studies describe this as tiring, time-consuming and, when a paid coach waits, a financial loss {c('sari')}. At major events the same task is done by large teams of trained ball persons standing close to play, often in hot weather. Automation in Olympic field-of-play logistics already exists: at Tokyo 2020, autonomous Field Support Robots returned javelins and hammers to athletes {c('toyota')}. India is bidding for the 2036 Olympics with Ahmedabad as its centre, and will host the 2030 Commonwealth Games there, so practice venues will need efficient, safe ball handling. This project asks: <b>which combination of ball detection, route planning and pickup mechanism clears a court fastest, with least energy and cost, and where could such a robot realistically be used at a mega-event?</b></p>
<p class="small">(Motivation: ≈150 words.)</p>
<h3>Problem statement</h3>
<p>Design an autonomous robot that (i) <b>detects</b> tennis balls lying on and around a court, (ii) <b>navigates</b> to them safely, and (iii) <b>retrieves</b> them into an on-board hopper, returning to a depot when full. Compare alternative designs on <b>retrieval time</b>, <b>energy consumption</b>, <b>cost</b> and <b>operating efficiency</b> (balls per minute), and assess deployment at large events.</p>
<h3>Key references (IEEE)</h3>
<p class="ref">[1] {REFS['sari']}</p>
<p class="ref">[2] {REFS['toyota']}</p>'''

S2 = f'''<h3>2.1 Core idea</h3>
<p>The robot is a small differential-drive vehicle with a <b>front roller intake</b> that pins each ball against a curved ramp and lifts it into a hopper (Fig. 1). Driven-roller ("throwing") intakes were rated the most efficient option for tennis in a comparative study, compared with rotary shafts, conveyors and grippers {c('sari')}. Rather than proposing one design, we compare <b>three system architectures</b> that differ in how the robot knows where the balls are:</p>
<table class="t"><tr><th>Design</th><th>How balls are found</th><th>How they are collected</th><th>Literature precedent</th></tr>
<tr><td><b>A</b> Overhead camera</td><td>Fixed camera above the court sees all balls; ball and robot positions sent to robot</td><td>Shortest tour: nearest-neighbour (NN) + 2-opt</td><td>Overhead camera + NN tour {c('sari')}</td></tr>
<tr><td><b>B</b> On-board camera</td><td>Camera on the robot; survey lanes until area seen; detection range R, recall r</td><td>Survey, then NN + 2-opt tour of detected balls</td><td>Pi + OpenCV / CNN robots {c('gu')}</td></tr>
<tr><td><b>C</b> Blind sweeper</td><td>No detection</td><td>Lawn-mower (boustrophedon) sweep, intake width w</td><td>U-turn coverage on real court {c('ali')}; golf range robots {c('pereira')}</td></tr></table>
<h3>2.2 Block diagram and control flow</h3>
{block_diagram()}
<p class="cap">Fig. 2  System block diagram.</p>
{flowchart()}
<p class="cap">Fig. 3  Control flowchart for design B ("Area explored? – no" = drive the next survey lane and look again). Design A skips the survey; design C replaces detection with a fixed sweep path.</p>
<h3>2.3 Algorithms (AI / data-processing components)</h3>
<ul>
<li><b>Detection.</b> Baseline: HSV colour threshold + Hough circle transform (OpenCV). Thresholds such as H 20–40 have been published for yellow balls, but S/V ranges drift with lighting and must be tuned on site {c('cao')}. On a Raspberry Pi without GPU, the Hough transform gave the best speed/accuracy balance in a simple scene {c('keca')}. AI option: a nano-size YOLO model; published inference benchmarks (COCO, not ball-specific) are ≈3 FPS on a Pi 4 and ≈20 FPS on a Pi 5 for YOLOv8n {c('qeng')}. Golf-ball CNNs reach 84–96 % mAP@0.5 on a desktop GPU {c('zhang')}.</li>
<li><b>Localisation.</b> Pixel → court coordinates by a homography (perspective transform) using the court lines; robot pose from wheel encoders + IMU (EKF), or directly from the overhead camera in design A.</li>
<li><b>Route planning.</b> Pickup order as a travelling-salesman problem: NN heuristic improved by 2-opt; when the hopper (capacity C) is smaller than the number of balls, the problem becomes a capacitated vehicle-routing problem, solvable with Google OR-Tools {c('ortools')}. Our simulator uses NN + 2-opt split by capacity.</li>
<li><b>Control and safety.</b> PID heading/speed control; ultrasonic/ToF sensors trigger stop-and-replan when a person or obstacle is within a safety distance.</li></ul>
<h3>2.4 Tools, software and materials</h3>
<p><b>Software:</b> Python 3 (pure-Python simulator written for this project, no external libraries), OpenCV (detection), Google OR-Tools (optional CVRP), Arduino/ESP32 firmware, Chrome/HTML for this report. <b>Hardware (proposed, not yet built):</b> ESP32-CAM or Raspberry Pi + camera, TB6612FNG driver, 2 × N20 12 V geared motors with encoders, 25GA-370 roller motor, 3S 11.1 V 2200 mAh Li-ion pack, HC-SR04 + VL53L0X sensors, acrylic chassis, 3D-printed/plywood ramp and hopper (CAD: Fusion 360/Onshape).</p>
<p><b>Variants.</b> Table tennis (40 mm, 2.7 g ball) favours suction pickup; one low-cost suction prototype reported ≈60 % (12/20) success, with failures attributed to a servo fault {c('essam')}. Golf ranges already use mature commercial pickers that push passive disc gangs {c('pereira', 'toro')}.</p>'''

S3 = f'''<p>Source type legend: <b>R</b> = official rules, <b>L</b> = peer-reviewed literature, <b>M</b> = manufacturer/retailer data, <b>N</b> = news, <b>E</b> = our own estimate (to be measured).</p>
<table class="t">
<tr><th>#</th><th>Quantity</th><th>Value used</th><th>Type</th><th>Source / justification</th></tr>
<tr><td>1</td><td>Tennis ball mass, diameter</td><td>56.0–59.4 g; 6.54–6.86 cm</td><td>R</td><td>ITF Rules, App. I {c('itf')}</td></tr>
<tr><td>2</td><td>Table-tennis ball; golf ball</td><td>40 mm, 2.7 g; ≥42.67 mm, ≤45.93 g</td><td>R</td><td>{c('ittf', 'randa')}</td></tr>
<tr><td>3</td><td>Field size (doubles court + club run-back 5.48 m + side-run 3.05 m)</td><td>34.73 × 17.07 m = 592.8 m²</td><td>R</td><td>{c('itf')}; area = own arithmetic</td></tr>
<tr><td>4</td><td>Number of balls N; layouts</td><td>30, 60, 90; uniform and "drill" cluster near far baseline</td><td>E</td><td>Typical coaching basket sizes; manual hoppers hold ≈75 balls</td></tr>
<tr><td>5</td><td>Robot speed v</td><td>0.6 m/s</td><td>E</td><td>Close to 2.3 km/h reported for Tennibot (2018) {c('newatlas')}</td></tr>
<tr><td>6</td><td>Turn rate ω; pick dwell t<sub>pick</sub>; unload time</td><td>90 °/s; 1 s; 20 s</td><td>E</td><td>Own estimates; dwell varied 0.3–3 s in sensitivity</td></tr>
<tr><td>7</td><td>Intake width w (design C)</td><td>0.3 m (also 0.6, 1.0 m)</td><td>E</td><td>Commercial golf pickers ≈0.956 m wide {c('toro')}</td></tr>
<tr><td>8</td><td>Hopper capacity C</td><td>15 and 30 balls</td><td>E</td><td>30 balls ≈1.7 kg; 90 balls ≈5.2 kg is too heavy for a small chassis (own arithmetic)</td></tr>
<tr><td>9</td><td>Detection range R, recall r (design B)</td><td>R = 2–5 m; r = 0.70–0.95</td><td>E</td><td>Unknown for low-cost cameras – must be measured</td></tr>
<tr><td>10</td><td>Drive power P<sub>drive</sub></td><td>10 W (7.2 W tested)</td><td>M/E</td><td>2 × N20 at stall 0.3 A × 12 V = 7.2 W {c('toboids')}; 10 W is conservative</td></tr>
<tr><td>11</td><td>Compute power P<sub>compute</sub></td><td>3 W (0.9–6.4 W tested)</td><td>M</td><td>Pi 4 measured 2.7 W idle, 6.4 W stress; Pi 5 2.4/8.9 W {c('perma')}</td></tr>
<tr><td>12</td><td>Roller power; other electronics</td><td>3 W; 1 W</td><td>E</td><td>Own estimates</td></tr>
<tr><td>13</td><td>Off-board laptop (design A system boundary)</td><td>20 W</td><td>E</td><td>Own estimate</td></tr>
<tr><td>14</td><td>Battery</td><td>3S 11.1 V 2200 mAh ≈ 24.4 Wh</td><td>M</td><td>Retail listings {c('robocraze')}; Wh = own arithmetic</td></tr>
<tr><td>15</td><td>Component prices (India, Oct 2026)</td><td>see Section 5, Table 3</td><td>M</td><td>{c('robocraze', 'robobazar', 'toboids')}; Pi prices rose with DRAM costs {c('rpiprice')}</td></tr>
<tr><td>16</td><td>Commercial benchmarks</td><td>Tennibot Rover: 90 balls, 4–5 h, $2,275; SeekerBot: 50 balls in ≈4–5 min, $999</td><td>M</td><td>{c('tennibot', 'seeker')} – manufacturer claims, not verified</td></tr>
<tr><td>17</td><td>Ahmedabad design ambient</td><td>46.6 °C (May 2024)</td><td>N</td><td>{c('heat')}</td></tr></table>
<h3>Modelling assumptions</h3>
<ul><li>Balls are static; perfect pickup once the robot reaches a ball; no wheel slip, acceleration phases or localisation error.</li>
<li>Design A knows all ball positions (ideal overhead camera). Design B detects each ball with probability r per survey pass within range R and repeats the survey for missed balls (pessimistic: no detection while touring). Design C knows nothing and sweeps the whole field.</li>
<li>No false detections; no people on court during clearing (operation between sessions).</li>
<li>Energy boundary: robot only, unless the 20 W off-board laptop of design A is stated.</li></ul>'''

S4 = f'''<h3>4.1 Simulation set-up (how the evaluation was done)</h3>
<p>Because the prototype could not be funded before evaluation, the designs were compared <b>quantitatively by Monte-Carlo simulation</b>. A pure-Python simulator (<code>sim.py</code>, <code>grid.py</code>, <code>sensitivity.py</code>; see Section 8) places N balls at random, plans the robot route for each design, and computes</p>
<p class="eq">T<sub>clear</sub> = L<sub>path</sub>/v + Θ<sub>turn</sub>/ω + N·t<sub>pick</sub> + ⌈N/C⌉·t<sub>unload</sub> (+ T<sub>survey</sub> for design B)<br>
E = P<sub>drive</sub>·t<sub>move</sub> + P<sub>intake</sub>·t<sub>intake</sub> + (P<sub>compute</sub> + P<sub>idle</sub> + P<sub>infra</sub>)·T<sub>clear</sub> &nbsp;&nbsp;&nbsp; η = N<sub>collected</sub>/T<sub>clear</sub> [balls/min]</p>
<p>Each configuration was run on <b>200 random layouts</b> (fixed seed 42, so results are reproducible). Six built-in checks verify the code logic before results are printed: (C1) a single ball 6 m away gives the exact hand-calculated time; (C2) 2-opt never lengthens the NN tour; (C3) a sweep is at least area/w long and misses no ball; (C4) a smaller hopper never shortens the path; (C5) design B is never faster than ideal design A; (C6) a detection-aware sweep is never longer than a blind one. All six pass. These are self-consistency checks, not validation against a real robot.</p>
<h3>4.2 Example routes</h3>
{traj_svg}
<p class="cap">Fig. 4  Simulated routes for one random layout of 30 balls (yellow) with the depot (red square) behind the near baseline; blue = court, green = run-off. Output of <code>build.py</code> using <code>sim.py</code>.</p>
<h3>4.3 Design comparison results</h3>
{fig_time}
{fig_energy}
<div style="break-inside: avoid"><h3>4.4 Sensitivity analysis</h3>
{fig_sens}</div>
<p><b>Plausibility check (not validation).</b> The model's blind sweep covers ≈10 m²/min. A real tennis-ball robot using a U-turn sweep cleared a 14 × 15 m court in 24.2 min (≈8.7 m²/min) {c('ali')}, the same order of magnitude. The 50-balls-in-4–5-min claim for SeekerBot {c('seeker')} is also of the same order as design A, but its test conditions are unknown.</p>'''

S5 = f'''<h3>5.1 Key findings</h3>
<table class="t"><tr><th>Design (N = 60, C = 30, uniform)</th><th>Time to clear (min)</th><th>Energy (Wh)</th><th>Efficiency (balls/min)</th><th>Robot cost (est.)</th></tr>
<tr><td>A Overhead camera, ideal detection</td><td>{A30['T']:.1f}</td><td>{A30['E']:.2f} (robot) / {A30L['E']:.2f} (+ laptop)</td><td>{60/A30['T']:.1f}</td><td>Low robot; + camera mast and PC</td></tr>
<tr><td>B On-board camera, R = 5 m, r = 0.95</td><td>{B5['T']:.1f}</td><td>{B5['E']:.2f}</td><td>{60/B5['T']:.1f}</td><td>≈ ₹4–5k (ESP32-CAM)</td></tr>
<tr><td>B On-board camera, R = 3 m, r = 0.80</td><td>{B38['T']:.1f}</td><td>{B38['E']:.2f}</td><td>{60/B38['T']:.1f}</td><td>same</td></tr>
<tr><td>B On-board camera, R = 2 m, r = 0.70</td><td>{B2['T']:.1f}</td><td>{B2['E']:.2f}</td><td>{60/B2['T']:.1f}</td><td>same</td></tr>
<tr><td>C Blind sweep, w = 1.0 m</td><td>{C10['T']:.1f}</td><td>{C10['E']:.2f}</td><td>{60/C10['T']:.1f}</td><td>Large intake, heavier frame</td></tr>
<tr><td>C Blind sweep, w = 0.3 m</td><td>{C03['T']:.1f}</td><td>{C03['E']:.2f}</td><td>{60/C03['T']:.1f}</td><td>Lowest electronics cost</td></tr></table>
<p class="cap">Table 2  Simulated performance (mean of 200 layouts; model outputs from <code>grid.txt</code>, not measurements).</p>
<ol>
<li><b>Detection quality decides the winner.</b> With good on-board detection (R ≥ 3 m, r = 0.95) the targeted robot is ≈1.1–1.5× faster than a 1.0 m sweeper and ≈3–4× faster than a 0.3 m sweeper. With poor detection (R = 2 m, r = 0.7) it becomes ≈{B2['T']/C10['T']:.1f}× <i>slower</i> than the wide sweeper.</li>
<li><b>Intake width is the sweeper's main lever</b>: widening from 0.3 to 1.0 m cuts sweep time by ≈{C03['T']/C10['T']:.1f}×, but makes the machine large and heavy.</li>
<li><b>Hopper capacity matters</b>: for design A, C = 15 instead of 30 increases clearing time from {A30['T']:.1f} to {A15['T']:.1f} min (+{(A15['T']/A30['T']-1)*100:.0f} %).</li>
<li><b>Clustered balls</b> (a typical drill) favour a detection-aware sweep of only the ball region: {D_S4['T']:.1f} min vs {D_C10['T']:.1f} min for a 1.0 m blind sweep (design A: {D_A30['T']:.1f} min).</li>
<li><b>Energy is not the constraint.</b> Every case used &lt; 20 Wh, i.e. less than one 24.4 Wh battery; an off-board laptop more than doubles design A's system energy. Cost-benefit is dominated by hardware cost and human time, not electricity.</li></ol>
<h3>5.2 Indicative cost</h3>
<table class="t"><tr><th>Item</th><th>Indicative price (₹)</th><th>Item</th><th>Indicative price (₹)</th></tr>
<tr><td>ESP32-CAM</td><td>499–699 {c('robobazar')}</td><td>2 × N20 encoder motors</td><td>≈ 940–1,070 {c('toboids')}</td></tr>
<tr><td>TB6612FNG driver</td><td>≈ 154 {c('robocraze')}</td><td>Roller motor 25GA-370</td><td>≈ 445 (retail)</td></tr>
<tr><td>3S 2200 mAh pack</td><td>550–899 {c('robocraze')}</td><td>HC-SR04 + VL53L0X</td><td>≈ 200 {c('robocraze')}</td></tr>
<tr><td>Chassis kit</td><td>≈ 670–800 {c('robocraze')}</td><td><b>Core total</b></td><td><b>≈ 3,650–4,170</b></td></tr></table>
<p class="cap">Table 3  Point-in-time Indian retail prices (Oct 2026). Still needed: second MCU, roller driver, buck converter, charger, fabrication (≈ +₹500–1,000, own estimate). A Raspberry Pi 4 4 GB now costs ≈ ₹11,000+ after 2025–26 price rises {c('robocraze', 'rpiprice')}. Commercial tennis robots cost $999–2,275 {c('seeker', 'tennibot')}.</p>
<h3>5.3 Value for the targeted stakeholders</h3>
<ul><li><b>Athletes &amp; coaches:</b> more practice time; a low-cost robot (design B) at training academies. The size of the saving is unverified (only a vendor claim exists), so we propose timing real sessions.</li>
<li><b>Organisers:</b> clearing practice and warm-up courts between sessions; fewer ball-crew hours in heat. Tennis rules treat ball persons as permanent fixtures only in their recognised positions, and a ball rolling onto court during a point causes a let {c('itf25')}, so robots should <i>not</i> operate during live points.</li>
<li><b>Sport technologists:</b> an open, reproducible benchmark for comparing detection and planning methods.</li>
<li><b>Sustainability:</b> &lt; 20 Wh per clearing; battery-electric, no fuel.</li></ul>
<h3>5.4 What worked, what did not, improvements</h3>
<p><b>Worked:</b> the simulator separates the effect of detection, intake width and hopper size, and shows clear trade-offs. <b>Did not / limitations:</b> no hardware was built; detection range, recall and power are assumed; design B is a pessimistic model; people, moving balls and wheel slip are ignored. Our first version over-stated the targeted design's advantage (≈9×) because it assumed perfect detection, a 90-ball hopper and a narrow sweeper — an independent review caught this and the model was extended. <b>Improvements:</b> measure R, r and current draw on a real court; add detection while touring; model false detections; validate against a timed hardware run.</p>
<h3>5.5 Large-event deployment (Ahmedabad 2030 / India 2036)</h3>
<p>India's bid timeline foresees an IOC shortlist in March 2027 and host election in mid-2029 {c('indiatoday')}; Ahmedabad hosts the 2030 Commonwealth Games where table tennis is a core sport {c('cwg')}, and the planned SVP Sports Enclave includes a tennis centre with a 10,000-seat centre court plus outdoor courts {c('dezeen')}. Ahmedabad reached 46.6 °C in May 2024 {c('heat')}, so battery thermal design is critical. Tokyo 2020's robots needed heat and water testing, quieter motors and turf-friendly tyres, and were not used where humans were faster {c('toyota')}. Recommended role: a <b>fleet of design-A/B robots on practice courts</b>, operating between sessions, compliant with service-robot safety requirements {c('iso')}.</p>'''

S6 = f'''<h3>Reflection</h3>
<p class="mot">We learned that "autonomous" is not one decision but a chain: how well the robot sees, how it orders its route, and how wide and large its intake and hopper are. Our first model looked impressive (9× faster than sweeping) but rested on hidden ideal assumptions; extending it showed the advantage depends on detection quality. Writing assumptions in a sourced table, separating manufacturer claims from measurements, and adding automatic code checks made the work honest and reproducible. We also learned that sports rules, heat and safety standards shape a robot's real use as much as engineering does.</p>
<p class="small">(Reflection: ≈95 words.)</p>
<h3>Future scope and real-world applications</h3>
<ul>
<li><b>Measure the decisive parameters</b> (detection range, recall, current draw, pick success) on a BITS tennis court with a low-cost prototype, then re-run the model.</li>
<li><b>Fleet operation</b>: several small robots sharing one overhead camera, solved as a multi-vehicle capacitated routing problem (OR-Tools).</li>
<li><b>Shared infrastructure</b>: reuse court-side cameras already installed for line-calling or broadcast as design A's "eye".</li>
<li><b>Closed training loop</b>: pair the collector with a ball machine; a commercial product already markets a loop in which the collector "delivers balls back" to the ball machine {c('tennibot')}.</li>
<li><b>Table-tennis variant</b> with suction intake for halls (CWG 2030), and <b>golf-range</b> or <b>pickleball</b> versions.</li>
<li><b>Indian-climate design</b>: heat-rated battery enclosure and shaded docking for 45 °C+ conditions.</li>
<li><b>Deployment</b>: Khelo India training centres and the SVP Sports Enclave practice courts.</li></ul>'''

S7 = f'''<div class="summary">
<h2 style="margin-top:0">Autonomous Ball-Retrieval Robot – One-Page Summary</h2>
<p><b>Problem.</b> Ball collection wastes practice time and needs large ball-crew teams at events, often in heat {c('sari')}. Autonomous field-of-play robots were already used at Tokyo 2020 {c('toyota')}. Which robot design clears a tennis court fastest, with least energy and cost?</p>
<p><b>Concept.</b> Small differential-drive robot with a roller intake and hopper. Three architectures compared: <b>A</b> overhead camera + shortest tour; <b>B</b> on-board camera (survey + tour); <b>C</b> blind lawn-mower sweep.</p>
<p><b>Method.</b> Pure-Python Monte-Carlo simulator: 592.8 m² court enclosure, 60 balls, 200 random layouts per case, explicit sourced assumptions, six automatic correctness checks, sensitivity to speed, pick time, intake width, hopper size, detection range and recall.</p>
<table class="t"><tr><th>Design (C = 30)</th><th>Time (min)</th><th>Energy (Wh)</th><th>Balls/min</th></tr>
<tr><td>A overhead camera</td><td>{A30['T']:.1f}</td><td>{A30['E']:.1f} (+laptop {A30L['E']:.1f})</td><td>{60/A30['T']:.1f}</td></tr>
<tr><td>B on-board, good detection (R 5 m, r 0.95)</td><td>{B5['T']:.1f}</td><td>{B5['E']:.1f}</td><td>{60/B5['T']:.1f}</td></tr>
<tr><td>B on-board, poor detection (R 2 m, r 0.7)</td><td>{B2['T']:.1f}</td><td>{B2['E']:.1f}</td><td>{60/B2['T']:.1f}</td></tr>
<tr><td>C sweep 1.0 m / 0.3 m</td><td>{C10['T']:.1f} / {C03['T']:.1f}</td><td>{C10['E']:.1f} / {C03['E']:.1f}</td><td>{60/C10['T']:.1f} / {60/C03['T']:.1f}</td></tr></table>
<p class="small">Model outputs, not measurements.</p>
<p><b>Findings.</b> (1) Targeted pickup wins only if detection is good; poor detection makes it slower than a wide sweeper. (2) Intake width is the sweeper's main lever (≈{C03['T']/C10['T']:.1f}× from 0.3 → 1.0 m). (3) Small hoppers cost time (+{(A15['T']/A30['T']-1)*100:.0f} % for C = 15). (4) Energy &lt; 20 Wh per clearing – cost is dominated by hardware and human time. (5) Core parts for an ESP32-CAM robot ≈ ₹3.7–4.2k vs $999–2,275 for commercial robots.</p>
<p><b>Stakeholders.</b> Coaches/athletes gain practice time; organisers can clear practice courts between sessions and reduce ball-crew heat exposure; robots should not enter live play under current tennis rules {c('itf25')}.</p>
<p><b>Ahmedabad 2030 / India 2036.</b> Fleet of low-cost robots for practice courts at the SVP Sports Enclave and Khelo India centres; heat-rated batteries for 46 °C conditions {c('heat')}.</p>
<p><b>Next step.</b> Build the ₹4–5k prototype, measure detection range, recall and power on a real court, and recalibrate the model.</p>
</div>'''

S8 = f'''<h3>8.1 Coding / data analytics (concrete proof)</h3>
<p>All results in Sections 4–5 are produced by code written for this project (pure Python, no external libraries), which reproduces exactly from a fixed random seed:</p>
<table class="t"><tr><th>File</th><th>Purpose</th></tr>
<tr><td><code>sim.py</code></td><td>Court model, ball generator, NN + 2-opt tour, capacity splitting, boustrophedon sweep, on-board survey model, time/energy accounting, six self-checks</td></tr>
<tr><td><code>grid.py</code></td><td>Design comparison A/B/C over hopper size, detection range/recall and intake width (200 trials each) → <code>grid.txt</code></td></tr>
<tr><td><code>sensitivity.py</code></td><td>One-at-a-time and interaction sensitivity → <code>sensitivity.txt</code></td></tr>
<tr><td><code>build.py</code></td><td>Generates all figures (SVG) and this report directly from the result files</td></tr></table>
<p>Console output of <code>python3 sim.py 200</code> (first lines):</p>
<pre>checks passed: C1 single-ball closed form, C2 2-opt&lt;=NN, C3 sweep&gt;=A/w &amp; no misses,
               C4 capacity monotone, C5 onboard&gt;=oracle, C6 box&lt;=blind
enclosure 34.73 x 17.07 m = 592.8 m^2; depot at (0, W/2) behind near baseline</pre>
<p>Core of the route planner (excerpt from <code>sim.py</code>):</p>
<pre>def nn_order(depot, balls):                 # greedy nearest-neighbour pickup order
    rem = list(balls); cur = depot; order = []
    while rem:
        j = min(range(len(rem)), key=lambda i: d(cur, rem[i]))
        cur = rem.pop(j); order.append(cur)
    return order

def two_opt(depot, order, max_iter=50):     # remove crossing edges
    path = [depot] + order + [depot]
    ...  # reverse segment i..k whenever d(a,c)+d(b,e) &lt; d(a,b)+d(c,e)</pre>
<p><b>Code link:</b> <span class="ph">[upload the folder <code>experiments/ball-retrieval-sim/</code> to GitHub/Drive and paste the link here]</span></p>
<h3>8.2 AI / ML component</h3>
<p>The detection stage is designed for a nano YOLO model (or HSV + Hough baseline). <b>Status: not yet trained.</b> No accuracy figures are claimed in this report. Planned evidence: precision, recall and confusion matrix on ≈100 labelled frames from our own court.</p>
<h3>8.3 Hardware, demo video, control system</h3>
<p><b>Status: not built.</b> Prototype funding is available only after evaluation; the bill of materials (Table 3), concept sketch (Fig. 1) and test protocol are ready. Planned test: half-court, N = 10 and 30 balls, uniform and clustered, ≥ 3 trials each; measure time to clear, balls collected, misses, Wh (INA219 current sensor) and detection range; compare with a person using a pick-up tube. Video link: <span class="ph">[to be added if a prototype is built]</span>.</p>
<h3>References</h3>
'''

def refs_html():
    return '\n'.join(f'<p class="ref">[{i+1}] {REFS[k]}</p>' for i, k in enumerate(ORDER))

CSS = '''
@page { size: A4; margin: 14mm 15mm 14mm 15mm;
  @bottom-right { content: "Page " counter(page) " of " counter(pages); font: 9px Helvetica, Arial; color: #666; }
  @bottom-left { content: "Assignment 2 – Project Idea 11 – [ID 1] / [ID 2]"; font: 9px Helvetica, Arial; color: #666; } }
body { font-family: "Times New Roman", Times, serif; font-size: 11pt; line-height: 1.32; color: #111; margin: 0; }
table.sec { width: 100%; border-collapse: collapse; page-break-before: always; }
table.sec:first-of-type { page-break-before: auto; }
table.sec > thead > tr > td, table.sec > tbody > tr > td { padding: 0; }
.hdr { display: flex; justify-content: space-between; border-bottom: 2px solid #1d4f8f; padding-bottom: 3px; margin-bottom: 8px; font-family: Helvetica, Arial; font-size: 12pt; font-weight: bold; color: #1d4f8f; }
.hdr .crs { font-size: 8pt; font-weight: normal; color: #555; align-self: flex-end; }
h3 { break-after: avoid; page-break-after: avoid; font-family: Helvetica, Arial; font-size: 11.5pt; color: #1d4f8f; margin: 9px 0 4px; }
h2 { font-family: Helvetica, Arial; color: #1d4f8f; font-size: 14pt; }
p { margin: 4px 0 6px; text-align: justify; }
ul, ol { margin: 3px 0 6px 0; padding-left: 20px; } li { margin-bottom: 3px; }
table.t { border-collapse: collapse; width: 100%; font-size: 9.5pt; margin: 4px 0; page-break-inside: avoid; }
table.t th, table.t td { border: 1px solid #999; padding: 2px 5px; vertical-align: top; text-align: left; }
table.t th { background: #e3ecf7; }
.cap { font-size: 9pt; font-style: italic; text-align: center; margin-top: 0; }
.ref { font-size: 9.2pt; margin: 2px 0; text-align: left; padding-left: 22px; text-indent: -22px; }
.small { font-size: 8.5pt; color: #555; }
.mot { background: #f6f9fd; border-left: 3px solid #1d4f8f; padding: 5px 8px; }
.eq { text-align: center; font-size: 10.5pt; background: #fafafa; padding: 4px; }
pre { font-size: 8.4pt; background: #f4f4f4; border: 1px solid #ddd; padding: 5px 7px; white-space: pre-wrap; margin: 3px 0 6px; }
code { font-size: 9pt; }
.ph { background: #fff3a0; padding: 0 2px; }
.cover .inst { font-family: Helvetica, Arial; font-size: 15pt; font-weight: bold; color: #1d4f8f; text-align: center; margin: 10px 0 8px; }
.cover > p { text-align: center; }
table.kv { width: 100%; border-collapse: collapse; margin: 10px 0 12px; font-size: 11pt; }
table.kv td { border: 1px solid #aaa; padding: 5px 8px; vertical-align: top; } table.kv td:first-child { width: 28%; background: #e3ecf7; font-weight: bold; }
.summary p { margin: 3px 0 5px; font-size: 10.5pt; }
svg { display: block; margin: 4px auto; page-break-inside: avoid; }
'''

def build():
    body = [section(0, 'Cover Page', S0), section(1, 'Problem Definition', S1), section(2, 'Concept / Design / Algorithm / Methodology', S2),
            section(3, 'Assumptions and Data Source', S3), section(4, 'Prototype / Simulation / Analysis / Testing', S4),
            section(5, 'Results and Discussion', S5), section(6, 'Reflection and Future Scope', S6),
            section(7, 'One-Page Summary of the Work', S7)]
    s8 = S8 + refs_html()  # refs after all citations collected
    body.append(section(8, 'Bonus – Evidence of Coding, AI and Automation', s8))
    doc = f'<!doctype html><html><head><meta charset="utf-8"><title>Assignment 2 – Project Idea 11</title><style>{CSS}</style></head><body>{"".join(body)}</body></html>'
    out = os.path.join(HERE, 'report.html'); open(out, 'w').write(doc)
    # word count of self-generated prose (approx.: strip tags, svg, pre, refs)
    txt = re.sub(r'<svg.*?</svg>|<pre>.*?</pre>|<p class="ref">.*?</p>', ' ', doc, flags=re.S)
    txt = re.sub(r'<style>.*?</style>|<[^>]+>', ' ', txt, flags=re.S)
    print('approx words (excl. figures, code, references):', len(re.findall(r'[A-Za-z0-9€₹%.,\-]+', txt)))
    print('refs cited:', len(ORDER), 'of', len(REFS), 'unused:', [k for k in REFS if k not in ORDER])
    print('trajectory check: oracle', round(RA['time_s']/60, 2), 'min; sweep1.0', round(RC['time_s']/60, 2), 'min')
    return out

if __name__ == '__main__':
    out = build()
    pdf = os.path.join(HERE, 'Assignment2_Idea11_ID1_ID2.pdf')
    chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    subprocess.run([chrome, '--headless', '--disable-gpu', '--no-pdf-header-footer', f'--print-to-pdf={pdf}', 'file://' + out],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print('wrote', pdf)
