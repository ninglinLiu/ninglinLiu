"""Draw the profile as a folio of printed plates: animated, self-contained SVGs.

Paper, ink and three spot colours (vermilion, ultramarine, gamboge) that
overprint like a risograph. Every count is read from data/*.json, so the
daily workflow redraws the plates whenever the public evidence changes.
Typefaces (SIL OFL, see docs/ASSET_CREDITS.md) are subset per plate and
embedded, so the plates look the same on every machine.

    pip install fonttools brotli
    python scripts/build_plates.py
"""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import date
import base64
import hashlib
import html
import io
import json
import math
import mimetypes
import random
import re
import struct
import zlib

from fontTools.ttLib import TTFont
from fontTools import subset

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/plates'
FONTDIR = ROOT / 'assets/fonts'
C = json.loads((ROOT / 'data/contributions.json').read_text(encoding='utf-8'))
A = json.loads((ROOT / 'data/activity.json').read_text(encoding='utf-8'))
T = json.loads((ROOT / 'data/topics.json').read_text(encoding='utf-8'))
PRS = C['contributions']
COUNTS = Counter(p['repository'] for p in PRS)
UPDATED = C['updated_at']

PAPER, PAPER2, STAMP = '#EEE6D5', '#E1D5BE', '#FBF6EA'
INK, INK2, GREY, LIGHT = '#151311', '#24201C', '#6B6255', '#B9AE9B'
RED, BLUE, YEL, ORANGE = '#E3391D', '#2236C4', '#F2BF2A', '#EE7F2B'

# key: (master file, embedded family, fallback stack, CJK partner)
FONTS = {
    'black': ('display-black.ttf', 'NL Display Black', "Didot,'Bodoni 72',Georgia,serif", 'song'),
    'ital': ('display-italic.ttf', 'NL Display Italic', "Didot,'Bodoni 72',Georgia,serif", 'songt'),
    'book': ('display-book.ttf', 'NL Display Book', "Georgia,serif", 'songt'),
    'cond': ('grotesk-condensed.ttf', 'NL Condensed', "'Arial Narrow',Impact,sans-serif", 'song'),
    'sans': ('grotesk-text.ttf', 'NL Sans', "Arial,Helvetica,sans-serif", 'songt'),
    'wide': ('grotesk-wide.ttf', 'NL Wide', "Arial Black,Arial,sans-serif", 'song'),
    'mono': ('mono.ttf', 'NL Mono', "ui-monospace,Consolas,monospace", 'songt'),
    'monob': ('mono-bold.ttf', 'NL Mono Bold', "ui-monospace,Consolas,monospace", 'song'),
    'song': ('song-black.ttf', 'NL Song Black', "'Songti SC',SimSun,serif", 'song'),
    'songt': ('song-text.ttf', 'NL Song', "'Songti SC',SimSun,serif", 'songt'),
}
NUMERALS = '壹贰叁肆伍陆柒捌玖'

_metrics = {}
_master = {}


def metrics(key):
    if key not in _metrics:
        f = TTFont(FONTDIR / FONTS[key][0])
        _metrics[key] = (f.getBestCmap(), f['hmtx'].metrics, f['head'].unitsPerEm, f.getGlyphOrder()[0])
    return _metrics[key]


def is_cjk(ch):
    return ord(ch) > 0x2E7F


def home(key, ch):
    """The font that actually draws a character (CJK falls through to its partner)."""
    if is_cjk(ch):
        return FONTS[key][3]
    return key if ord(ch) in metrics(key)[0] else FONTS[key][3]


def width(s, key, size, ls=0.0):
    total = 0.0
    for ch in s:
        k = home(key, ch)
        cmap, hm, upm, notdef = metrics(k)
        g = cmap.get(ord(ch))
        total += (hm[g][0] if g else hm[notdef][0]) / upm * size
    return total + ls * len(s)


def fit(s, key, size, room):
    """Largest size, stepping down from `size`, at which `s` fits in `room` px."""
    while width(s, key, size) > room and size > 8:
        size -= 1
    return size


def family(key):
    name, partner = FONTS[key][1], FONTS[FONTS[key][3]][1]
    return f"'{name}','{partner}',{FONTS[key][2]}"


def esc(s):
    return html.escape(str(s), quote=False)


def shade(color, k):
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return '#%02X%02X%02X' % (int(r * k), int(g * k), int(b * k))


def png_specks(size, seed, gray, density, alpha):
    """A tiny grayscale+alpha PNG of ink specks, written with the standard library."""
    rnd = random.Random(seed)
    raw = bytearray()
    for _ in range(size):
        raw.append(0)
        for _ in range(size):
            a = int(alpha * rnd.random() ** 2) if rnd.random() < density else 0
            raw += bytes([gray, a])

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)
    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 4, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')
    return base64.b64encode(png).decode()


GRAIN_DARK = png_specks(150, 7, 40, .24, 58)
GRAIN_LIGHT = png_specks(150, 11, 236, .20, 60)
PINHOLES = png_specks(150, 23, 238, .09, 120)

BASE_CSS = '''text{font-kerning:normal}
.mul{mix-blend-mode:multiply}
.blink{animation:blink 1.2s steps(1) infinite}@keyframes blink{50%{opacity:0}}
.ofd{animation:ofd 14s linear infinite}@keyframes ofd{0%{opacity:0}2.5%,97%{opacity:1}100%{opacity:0}}
.drift{animation:drift 7s ease-in-out infinite}@keyframes drift{0%,100%{transform:translate(0,0)}50%{transform:translate(3px,-2px)}}
.hw{animation:hw 5.5s ease-in-out infinite}@keyframes hw{0%,100%{opacity:1}50%{opacity:.28}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
'''


class Plate:
    def __init__(self, name, w, h, title, bg=PAPER, grain='dark'):
        self.name, self.w, self.h, self.title, self.bg, self.grain = name, w, h, title, bg, grain
        self.body, self.defs, self.css = [], [], []
        self.chars = defaultdict(set)
        self.n = 0

    def id(self, prefix='i'):
        self.n += 1
        return f'{prefix}{self.n}'

    def add(self, *parts):
        self.body.extend(parts)

    def t(self, x, y, s, key='sans', size=20, fill=INK, anchor=None, ls=0, cls=None, style=None, extra=''):
        s = str(s)
        for ch in s:
            if ch != ' ':
                self.chars[home(key, ch)].add(ch)
        a = f'x="{x:.1f}" y="{y:.1f}" font-family="{family(key)}" font-size="{size}" fill="{fill}"'
        if anchor:
            a += f' text-anchor="{anchor}"'
        if ls:
            a += f' letter-spacing="{ls}"'
        if cls:
            a += f' class="{cls}"'
        if style:
            a += f' style="{style}"'
        if key in ('black', 'ital') and size >= 36 and fill != 'none':
            a += f' stroke="{fill}" stroke-width="{max(.65, size*.006):.2f}" paint-order="stroke fill" stroke-linejoin="round"'
        return f'<text {a} {extra}>{esc(s)}</text>'

    def face(self, key, chars):
        f = TTFont(FONTDIR / FONTS[key][0])
        opts = subset.Options()
        opts.flavor = 'woff2'
        opts.layout_features = ['kern', 'liga', 'tnum', 'lnum']
        opts.name_IDs = ['*']
        opts.hinting = False
        opts.notdef_outline = True
        sub = subset.Subsetter(opts)
        sub.populate(text=''.join(sorted(chars)))
        sub.subset(f)
        buf = io.BytesIO()
        f.flavor = 'woff2'
        f.save(buf)
        data = base64.b64encode(buf.getvalue()).decode()
        return f"@font-face{{font-family:'{FONTS[key][1]}';src:url(data:font/woff2;base64,{data}) format('woff2')}}"

    def save(self):
        faces = ''.join(self.face(k, v) for k, v in sorted(self.chars.items()) if v)
        tile = GRAIN_DARK if self.grain == 'dark' else GRAIN_LIGHT

        def tile_pattern(pid, data):
            return (f'<pattern id="{pid}" width="150" height="150" patternUnits="userSpaceOnUse">'
                    f'<image width="150" height="150" href="data:image/png;base64,{data}"/></pattern>')
        grain = tile_pattern('grain', tile) + tile_pattern('pin', PINHOLES)
        s = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
             f'width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="title">'
             f'<title id="title">{esc(self.title)}</title><defs>{grain}'
             f'<clipPath id="sheet"><rect width="{self.w}" height="{self.h}"/></clipPath>{"".join(self.defs)}</defs>'
             f'<style>{faces}{BASE_CSS}{"".join(self.css)}</style>'
             f'<g clip-path="url(#sheet)"><rect width="{self.w}" height="{self.h}" fill="{self.bg}"/>'
             f'<rect width="{self.w}" height="{self.h}" fill="url(#grain)"/>'
             f'<rect width="{self.w}" height="{self.h}" fill="url(#pin)" opacity=".3" pointer-events="none"/>'
             f'{"".join(self.body)}'
             f'</g></svg>')
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f'{self.name}.svg').write_text(s, encoding='utf-8')
        return len(s)


# ---------------------------------------------------------------- primitives

def rect(x, y, w, h, fill, extra=''):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" {extra}/>'


def line(x1, y1, x2, y2, color=INK, wd=1, extra=''):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="{wd}" {extra}/>'


def regmark(x, y, r=10, color=INK):
    return (f'<g stroke="{color}" stroke-width="1" fill="none"><circle cx="{x}" cy="{y}" r="{r}"/>'
            f'<circle cx="{x}" cy="{y}" r="{r * .45:.1f}" fill="{color}"/>'
            f'<path d="M{x - r * 1.7:.1f} {y}H{x + r * 1.7:.1f}M{x} {y - r * 1.7:.1f}V{y + r * 1.7:.1f}"/></g>')


def crops(w, h, color=INK, inset=14, length=16):
    d = ''
    for x, y, sx, sy in [(inset, inset, 1, 1), (w - inset, inset, -1, 1), (inset, h - inset, 1, -1), (w - inset, h - inset, -1, -1)]:
        d += f'M{x - sx * 6} {y}h{sx * -length}M{x} {y - sy * 6}v{sy * -length}'
    return f'<path d="{d}" stroke="{color}" stroke-width="1" fill="none" opacity=".55"/>'


def control_strip(p, x, y, sz=22, dark=False):
    inks = [(INK if not dark else PAPER, 'K'), (RED, '朱'), (BLUE, '群青'), (YEL, '藤黄')]
    out = ''
    for i, (c, label) in enumerate(inks):
        out += rect(x + i * (sz + 30), y, sz, sz, c)
        out += p.t(x + i * (sz + 30) + sz + 5, y + sz - 6, label, 'mono', 11, LIGHT if dark else GREY)
    return out


def odometer(p, x, y, s, key, size, fill, cycle=14, land=16, anchor='start'):
    adv = width('0', key, size)
    widths = [adv if ch.isdigit() else width(ch, 'monob', size*.66) for ch in s]
    total = sum(widths)
    if anchor == 'end':
        x -= total
    elif anchor == 'middle':
        x -= total / 2
    lh = size * 1.08
    cid = p.id('oc')
    p.defs.append(f'<clipPath id="{cid}"><rect x="{x - 6:.1f}" y="{y - size * .86:.1f}" width="{total + 12:.1f}" height="{size * 1.14:.1f}"/></clipPath>')
    out = [f'<g class="ofd" style="animation-duration:{cycle}s"><g clip-path="url(#{cid})">']
    cx, j = x, 0
    for ch, wd in zip(s, widths):
        if ch.isdigit():
            k = p.id('od')
            off = (10 + int(ch)) * lh
            pct = land + j * 3.2
            p.css.append(f'.{k}{{transform:translateY(-{off:.1f}px);animation:{k} {cycle}s cubic-bezier(.2,.7,.2,1) infinite}}'
                         f'@keyframes {k}{{0%{{transform:translateY(0)}}{pct:.1f}%,100%{{transform:translateY(-{off:.1f}px)}}}}')
            col = ''.join(p.t(cx + wd / 2, y + i * lh, str(i % 10), key, size, fill, anchor='middle') for i in range(20))
            out.append(f'<g class="{k}">{col}</g>')
            j += 1
        else:
            out.append(p.t(cx, y, ch, 'monob', size*.66, fill))
        cx += wd
    out.append('</g></g>')
    return ''.join(out), total


def marquee(p, x, y, unit, key, size, fill, span, speed=40, reverse=False, ls=0):
    period = width(unit, key, size, ls)
    reps = math.ceil(span / period) + 2
    k = p.id('mq')
    dur = period / speed
    a, b = (-period, 0) if reverse else (0, -period)
    p.css.append(f'.{k}{{animation:{k} {dur:.2f}s linear infinite}}'
                 f'@keyframes {k}{{from{{transform:translateX({a:.2f}px)}}to{{transform:translateX({b:.2f}px)}}}}')
    texts = ''.join(p.t(x + i * period, y, unit, key, size, fill, ls=ls) for i in range(reps))
    return f'<g class="{k}">{texts}</g>'


def halftone(x0, y0, x1, y1, step, color, fx, fy, reach, rmax, wave=True):
    groups = defaultdict(list)
    yy = y0
    row = 0
    while yy <= y1:
        xx = x0 + (step / 2 if row % 2 else 0)
        col = 0
        while xx <= x1:
            d = math.hypot(xx - fx, yy - fy) / reach
            r = rmax * max(0.0, 1 - d)
            if r > .7:
                groups[(row + col) // 2].append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="{r:.2f}"/>')
            xx += step
            col += 1
        yy += step * .87
        row += 1
    out = f'<g fill="{color}">'
    for k in sorted(groups):
        attrs = f' class="hw" style="animation-delay:-{k * .16:.2f}s"' if wave else ''
        out += f'<g{attrs}>{"".join(groups[k])}</g>'
    return out + '</g>'


def seal(p, cx, cy, size, rot=-4, cls=''):
    fid = p.id('sf')
    p.defs.append(
        f'<filter id="{fid}" x="-8%" y="-8%" width="116%" height="116%">'
        f'<feTurbulence type="fractalNoise" baseFrequency=".8" numOctaves="2" seed="4" result="n"/>'
        f'<feDisplacementMap in="SourceGraphic" in2="n" scale="{size * .018:.1f}" xChannelSelector="R" yChannelSelector="G" result="d"/>'
        f'<feTurbulence type="fractalNoise" baseFrequency=".09" numOctaves="3" seed="9" result="m"/>'
        f'<feColorMatrix in="m" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 -2.4 2.2" result="mask"/>'
        f'<feComposite in="d" in2="mask" operator="in"/></filter>')
    s = size * .43
    half = size / 2
    body = rect(cx - half, cy - half, size, size, RED, f'rx="{size * .05:.1f}"')
    body += p.t(cx, cy - s * .5 + s * .38, '刘', 'song', round(s), PAPER, 'middle')
    body += p.t(cx, cy + s * .5 + s * .38, '羽', 'song', round(s), PAPER, 'middle')
    return f'<g class="{cls}"><g transform="rotate({rot} {cx} {cy})" filter="url(#{fid})">{body}</g></g>'


def ring_text(p, cx, cy, r, s, key='mono', size=13, fill=INK, dur=48):
    pid = p.id('rp')
    p.defs.append(f'<path id="{pid}" d="M{cx - r} {cy}a{r} {r} 0 1 1 {2 * r} 0a{r} {r} 0 1 1 {-2 * r} 0"/>')
    for ch in s:
        if ch != ' ':
            p.chars[home(key, ch)].add(ch)
    circ = 2 * math.pi * r - 2
    k = p.id('spin')
    p.css.append(f'.{k}{{transform-box:view-box;transform-origin:{cx}px {cy}px;animation:{k} {dur}s linear infinite}}'
                 f'@keyframes {k}{{to{{transform:rotate(360deg)}}}}')
    return (f'<g class="{k}"><text font-family="{family(key)}" font-size="{size}" fill="{fill}">'
            f'<textPath href="#{pid}" xlink:href="#{pid}" textLength="{circ:.1f}" lengthAdjust="spacing">{esc(s)}</textPath></text></g>')


def plate_head(p, numeral, title, x=30, base=190, nsize=180, tkey='ital', tsize=170, tfill=INK, gap=14, limit=None):
    """Big vermilion numeral and display title, the opening of every plate."""
    p.add(p.t(x, base, numeral, 'song', nsize, RED))
    tx = x + width(numeral, 'song', nsize) + gap
    tsize = fit(title, tkey, tsize, (limit or p.w - 20) - tx)
    p.add(p.t(tx, base - nsize * .06, title, tkey, tsize, tfill))


def rule(p, y, x0=36, x1=None):
    x1 = x1 or p.w - 36
    p.add(line(x0, y, x1, y, INK, 3), line(x0, y + 6, x1, y + 6, INK, 1))


def kicker(p, x, y, lines, anchor='end', color=GREY, size=13):
    for i, s in enumerate(lines):
        p.add(p.t(x, y + i * (size + 9), s, 'mono', size, color, anchor, ls=.6))


def b64file(path):
    return base64.b64encode(path.read_bytes()).decode()


def pr_type(title):
    for tok in re.findall(r'[a-z]+', title.lower())[:3]:
        if tok in ('fix', 'fixes', 'fixed', 'bugfix', 'hotfix'):
            return 'fix'
        if tok in ('docs', 'doc', 'documentation', 'readme', 'typo', 'typos'):
            return 'docs'
        if tok in ('test', 'tests', 'testing'):
            return 'test'
        if tok in ('refactor', 'feat', 'feature', 'perf', 'chore', 'add', 'build', 'ci', 'style'):
            return 'other'
    return 'other'


TYPE_COLOR = {'fix': RED, 'docs': YEL, 'test': BLUE, 'other': PAPER}


def ticker_items(n=14):
    dull = re.compile(r'typo|spelling|duplicated word|whitespace|grammar|wording', re.I)
    seen, out = Counter(), []
    for pr in sorted(PRS, key=lambda q: q['merged_at'], reverse=True):
        if dull.search(pr['title']) or seen[pr['repository']] >= 2:
            continue
        seen[pr['repository']] += 1
        title = ''.join(c for c in pr['title'].replace('`', '') if ord(c) < 0x2E80).strip()
        if len(title) > 78:
            title = title[:76].rstrip() + '…'
        out.append(f"{pr['repository']} #{pr['number']}  {title}")
        if len(out) == n:
            break
    return out


# ---------------------------------------------------------------- 〇 masthead

def masthead(m):
    W, H = (600, 1150) if m else (1200, 880)
    n, repos = len(PRS), len(COUNTS)
    p = Plate('masthead' + ('-m' if m else ''), W, H,
              f'Yu Liu（ninglin liu）刘羽: AI agents, full-stack products, code-made animation and on-chain systems. '
              f'1,000+ omniAI registered users; {n} merged upstream PRs across {repos} repositories.')
    # halftone sun behind the name
    if m:
        p.add(halftone(250, 60, 600, 560, 17, YEL, 560, 120, 470, 7.4))
    else:
        p.add(halftone(470, 52, 1200, 650, 21, YEL, 1080, 140, 720, 9.2))
    # top bar
    p.add(rect(0, 0, W, 44, INK))
    left = 'GITHUB.COM/NINGLINLIU · FOLIO 2026' if m else 'GITHUB.COM/NINGLINLIU  ·  FOLIO 2026  ·  上海 SHANGHAI / REMOTE'
    p.add(p.t(22, 28, left, 'mono', 13, PAPER, ls=.8))
    right = f'EDITION {UPDATED}' if m else f'EDITION {UPDATED}  ·  REDRAWN DAILY 01:19 UTC'
    p.add(p.t(W - 22, 28, right, 'mono', 13, PAPER, 'end', ls=.8))
    rw = width(right, 'mono', 13, .8)
    p.add(f'<circle class="blink" cx="{W - 34 - rw:.1f}" cy="23" r="5" fill="{RED}"/>')

    # the name: vermilion song, keyline drift, ultramarine italic overprinting it
    if m:
        cx, cb, cs = 18, 352, 280
        lx, lb, ls_ = 44, 446, 166
    else:
        cx, cb, cs = 22, 452, 392
        lx, lb, ls_ = 258, 578, 224
    p.add(p.t(cx, cb, '刘羽', 'song', cs, RED))
    keyline = p.t(cx - 7, cb - 6, '刘羽', 'song', cs, 'none', extra=f'stroke="{INK}" stroke-width="1.4"')
    p.add(f'<g class="drift">{keyline}</g>')
    p.add(p.t(lx, lb, 'Yu Liu', 'ital', ls_, BLUE, cls='mul'))
    p.add(p.t(572 if m else 1000, 477 if m else 604,
              '（ninglin liu）', 'mono', 24, BLUE, 'end'))

    # the search that produces the numbers, typed out
    q = 'is:pr author:ninglinLiu is:merged -user:ninglinLiu'
    qy = 500 if m else 632
    qsize = 13 if m else 17
    qx = 24 if m else 40
    qw = width('> ' + q, 'mono', qsize)
    k = p.id('type')
    p.defs.append(f'<clipPath id="{k}c"><rect class="{k}" x="{qx}" y="{qy - 20}" width="{qw + 4:.1f}" height="28"/></clipPath>')
    p.css.append(f'.{k}{{transform-box:fill-box;transform-origin:left;animation:{k} 11s steps({len(q) + 2}) infinite}}'
                 f'@keyframes {k}{{0%{{transform:scaleX(0)}}38%,100%{{transform:scaleX(1)}}}}')
    p.add(f'<g clip-path="url(#{k}c)">{p.t(qx, qy, "> " + q, "mono", qsize, INK)}</g>')
    res = f'→ {n} merged'
    p.add(p.t(qx + qw + 12, qy, res, 'monob', qsize, RED))
    p.add(rect(qx + qw + 16 + width(res, 'monob', qsize), qy - qsize * .8, qsize * .55, qsize * .95, INK, 'class="blink"'))

    # ledger of facts, rolling odometers
    facts = [('壹', '1,000+', 'OMNIAI REGISTERED USERS', '注册用户'),
             ('贰', str(n), 'MERGED UPSTREAM PRS', '合并的上游 PR'),
             ('叁', str(repos), 'UPSTREAM REPOSITORIES', '上游仓库')]
    for i, (num, val, en, zh) in enumerate(facts):
        if m:
            x, y = 26, 610 + i * 112
            size = 74
        else:
            x, y = 848, 168 + i * 126
            size = 72
        p.add(p.t(x, y - size - 12, num, 'song', 22, RED))
        p.add(p.t(x + 30, y - size - 15, en, 'mono', 17 if m else 13, INK, ls=.3))
        od, wd = odometer(p, x - 2, y, val, 'black', size, INK, land=12 + i * 8)
        p.add(od)
        if m:
            p.add(p.t(x + wd + 14, y - 6, zh, 'songt', 18, GREY))
        else:
            p.add(p.t(W - 36, y - size - 15, zh, 'songt', 15, GREY, 'end'))
            p.add(line(x, y + 22, W - 36, y + 22, INK, 1, 'stroke-dasharray="1 4"'))

    # two crossing tickers: real merged PRs, and what I work on
    ty = 960 if m else 712
    tick = '   ■   '.join(ticker_items()) + '   ■   '
    p.add(f'<g transform="rotate(-3.2 {W / 2} {ty})">{rect(-120, ty - 34, W + 240, 58, YEL)}'
          f'{marquee(p, -120, ty + 6, tick, "cond", 25 if m else 30, INK, W + 240, speed=46)}</g>')
    words = 'AI AGENTS · 智能体 ● FULL-STACK PRODUCTS · 全栈产品 ● CREATIVE DEV TOOLS · 代码动画 ● ON-CHAIN DATA · 链上数据 ● '
    by = ty + 50
    p.add(f'<g transform="rotate(2.3 {W / 2} {by})">{rect(-120, by - 22, W + 240, 44, INK)}'
          f'{marquee(p, -120, by + 6, words, "wide", 15 if m else 17, PAPER, W + 240, speed=32, reverse=True, ls=1.2)}</g>')

    # seal stamped over the tickers, with a slow ring of words
    sx, sy, ss = (488, 760, 92) if m else (1098, 556, 98)
    p.add(ring_text(p, sx, sy, ss * .86, 'OPEN SOURCE ● AGENTS ● FULL STACK ● ON-CHAIN ● MOTION ● ', 'monob', 12 if m else 13, INK))
    p.add(seal(p, sx, sy, ss))

    # byline and print furniture
    if m:
        p.add(p.t(24, 1052, 'Yu Liu (刘羽) · IoT Engineering, XJTLU', 'book', 22, INK))
        p.add(p.t(24, 1082, 'AI agents · full-stack · animation in code · on-chain', 'book', 18, GREY))
        p.add(control_strip(p, 24, 1104, 16))
    else:
        p.add(p.t(40, 808, 'Yu Liu (刘羽). IoT Engineering at XJTLU; Shanghai, or remote.', 'book', 23, INK))
        p.add(p.t(40, 840, 'I build AI agents and full-stack products, make animation with code, and read on-chain data.', 'book', 19, GREY))
        p.add(control_strip(p, 920, 818, 20))
        p.add(regmark(1166, 826, 8))
    p.add(crops(W, H, INK))
    return p.save()


# ---------------------------------------------------------------- 壹 omniAI

SIGNS = [(73, 292), (300, 282), (456, 304), (543, 535), (443, 527), (308, 610), (63, 564)]


def omniai(m):
    W, H = (600, 1960) if m else (1200, 1090)
    p = Plate('omniai' + ('-m' if m else ''), W, H,
              'omniAI: a bilingual financial research agent with a 3D landing scene, 1,000+ registered users. '
              'Pipeline: ask, retrieve, call tools, stream, cite.')
    if m:
        plate_head(p, '壹', 'omniAI', 18, 150, 118, 'black', 104)
        kicker(p, 24, 196, ['PLATE 壹 · LIVE PRODUCT · OMNIAIHELLO.COM'], 'start', GREY, 12)
        rule(p, 214, 24, W - 24)
    else:
        plate_head(p, '壹', 'omniAI', 26, 196, 180, 'black', 160, limit=W - 300)
        kicker(p, W - 36, 84, ['PLATE 壹 · LIVE PRODUCT', 'OMNIAIHELLO.COM', 'NEXT.JS · TYPESCRIPT · THREE.JS'])
        rule(p, 226)

    # left column: the number and the sentence
    x0 = 24 if m else 40
    nb = 344 if m else 388
    od, wd = odometer(p, x0 - 2, nb, '1,000+', 'black', 112 if m else 136, BLUE, land=14)
    p.add(od)
    p.add(p.t(x0, nb + 40, 'REGISTERED USERS', 'cond', 26, INK, ls=.6))
    p.add(p.t(x0 + width('REGISTERED USERS', 'cond', 26, .6) + 12, nb + 40, '注册用户', 'songt', 21, GREY))
    lines = ['A bilingual research agent', 'for markets, set inside a', '3D shop you can turn and zoom.']
    ly = nb + 104
    for i, s in enumerate(lines):
        p.add(p.t(x0, ly + i * 42, s, 'ital', 33 if m else 34, INK))
    zy = ly + len(lines) * 42 + 8
    p.add(p.t(x0, zy, '双语金融研究 Agent，', 'songt', 20, GREY))
    p.add(p.t(x0, zy + 30, '开在一间能拖着转的 3D 小店里。', 'songt', 20, GREY))

    # the photograph, offset-printed, with a cursor visiting the clickable signs
    if m:
        px, py, pw = 24, zy + 70, 552
    else:
        px, py, pw = 548, 256, 616
    ph = pw * 862 / 704
    s = pw / 704
    p.add(rect(px + 14, py + 14, pw, ph, RED))
    p.add(f'<image x="{px}" y="{py}" width="{pw}" height="{ph:.1f}" preserveAspectRatio="xMidYMid slice" '
          f'href="data:image/jpeg;base64,{b64file(ROOT / "assets/film/omniai-diorama.jpg")}"/>')
    p.add(rect(px, py, pw, ph, 'none', f'stroke="{INK}" stroke-width="3"'))
    pts = [(px + a * s, py + b * s) for a, b in SIGNS]
    cyc = 15.4
    step = 100 / len(pts)
    for i, (x, y) in enumerate(pts):
        p.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{RED}" stroke="{PAPER}" stroke-width="1.2"/>')
        k = p.id('rip')
        a = i * step
        p.css.append(f'.{k}{{opacity:0;transform-box:fill-box;transform-origin:center;animation:{k} {cyc}s ease-out infinite}}'
                     f'@keyframes {k}{{0%,{a + 3.9:.2f}%{{opacity:0;transform:scale(.3)}}{a + 4.4:.2f}%{{opacity:1;transform:scale(.4)}}'
                     f'{a + 11:.2f}%{{opacity:0;transform:scale(2.6)}}100%{{opacity:0;transform:scale(2.6)}}}}')
        p.add(f'<circle class="{k}" cx="{x:.1f}" cy="{y:.1f}" r="14" fill="none" stroke="{YEL}" stroke-width="3"/>')
    k = p.id('cur')
    frames = []
    for i, (x, y) in enumerate(pts):
        px0, py0 = pts[i - 1]
        a = i * step
        frames.append(f'{a:.2f}%{{transform:translate({px0:.1f}px,{py0:.1f}px)}}{a + 3.6:.2f}%{{transform:translate({x:.1f}px,{y:.1f}px)}}')
    frames.append(f'100%{{transform:translate({pts[-1][0]:.1f}px,{pts[-1][1]:.1f}px)}}')
    p.css.append(f'.{k}{{transform:translate({pts[0][0]:.1f}px,{pts[0][1]:.1f}px);animation:{k} {cyc}s cubic-bezier(.5,0,.2,1) infinite}}'
                 f'@keyframes {k}{{{"".join(frames)}}}')
    p.add(f'<g class="{k}"><path d="M0 0 L0 25 L6.5 19 L11 29 L15.5 27 L11 17.5 L19.5 17.5 Z" fill="{PAPER}" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"/></g>')
    cy = py + ph + (40 if m else 44)
    caption = 'FIG. 1 · omniaihello.com · 3D workspace' if m else 'FIG. 1  omniaihello.com: drag to rotate, scroll to zoom, pick a sign to explore.'
    p.add(p.t(px, cy, caption, 'mono', 18 if m else 13, INK))
    p.add(p.t(px, cy + 24, '图 1 · 落地页场景：拖动旋转，滚轮缩放，点招牌进入。', 'songt', 15, GREY))

    # pipeline with a travelling token
    stages = [('ASK', '提问'), ('RETRIEVE', '检索 · RAG'), ('CALL TOOLS', '有边界的工具调用'), ('STREAM', 'SSE 流式回答'), ('CITE', '回答带出处')]
    gap = 44
    sy0 = (cy + 92) if m else 744
    p.add(p.t(x0, sy0 - 40, 'HOW AN ANSWER IS MADE', 'mono', 13, GREY, ls=.8))
    p.add(line(x0 + 12, sy0 - 8, x0 + 12, sy0 - 8 + gap * 4, INK, 2))
    cyc2 = 10
    for i, (en, zh) in enumerate(stages):
        y = sy0 + i * gap
        p.add(f'<circle cx="{x0 + 12}" cy="{y - 8}" r="6" fill="{PAPER}" stroke="{INK}" stroke-width="2"/>')
        p.add(p.t(x0 + 36, y, en, 'cond', 26, INK, ls=.5))
        k = p.id('hl')
        a = i * 20
        p.css.append(f'.{k}{{opacity:0;animation:{k} {cyc2}s linear infinite}}'
                     f'@keyframes {k}{{0%,{max(a - .01, 0):.2f}%{{opacity:0}}{a + 1:.2f}%,{a + 15:.2f}%{{opacity:1}}{a + 17:.2f}%,100%{{opacity:0}}}}')
        p.add(p.t(x0 + 36, y, en, 'cond', 26, RED, ls=.5, cls=k))
        p.add(p.t(x0 + 200, y - 2, zh, 'songt', 18, GREY))
    k = p.id('tok')
    kf = []
    for i in range(5):
        a = i * 20
        kf.append(f'{a:.1f}%{{transform:translateY({i * gap}px);opacity:1}}{a + 14:.1f}%{{transform:translateY({i * gap}px)}}')
    kf.append(f'96%{{transform:translateY({4 * gap}px);opacity:1}}99%{{transform:translateY({4 * gap}px);opacity:0}}100%{{transform:translateY(0);opacity:0}}')
    p.css.append(f'.{k}{{animation:{k} {cyc2}s cubic-bezier(.6,0,.3,1) infinite}}@keyframes {k}{{{"".join(kf)}}}')
    p.add(f'<g class="{k}"><circle cx="{x0 + 12}" cy="{sy0 - 8}" r="9" fill="{RED}"/></g>')

    spec_y = sy0 + gap * 4 + (60 if m else 64)
    specs = [('AGENT', 'RAG · tool calling · SSE · structured output · MCP'),
             ('PRODUCT', 'bilingual Next.js · Three.js scene · market charts'),
             ('ROLE', 'project lead · implementation · agent · releases')]
    for i, (a, b) in enumerate(specs):
        y = spec_y + i * (62 if m else 28)
        p.add(p.t(x0, y, a, 'monob', 16 if m else 13, RED, ls=.6))
        p.add(p.t(x0 if m else x0+82, y+26 if m else y, b, 'mono', 17 if m else 13, INK))
    p.add(crops(W, H))
    return p.save()


# ---------------------------------------------------------------- 贰 upstream board

def upstream(m):
    n, repos = len(PRS), len(COUNTS)
    rows = sorted(COUNTS.items(), key=lambda r: (-r[1], r[0]))
    rh = 31 if not m else 78
    top = 410 if not m else 470
    board_h = 46 + len(rows) * rh + 44
    W = 600 if m else 1200
    H = top + board_h + 46
    p = Plate('upstream' + ('-m' if m else ''), W, H,
              f'{n} merged PRs in {repos} upstream repositories, one row per repository, one tick per pull request, '
              f'coloured by type: fix, docs, test, other.')
    if m:
        plate_head(p, '贰', 'Upstream', 18, 150, 118, 'ital', 104)
        rule(p, 186, 24, W - 24)
        od, wd = odometer(p, 22, 300, str(n), 'black', 112, BLUE, land=14)
        p.add(od)
        p.add(p.t(30 + wd, 262, 'MERGED PULL REQUESTS', 'cond', 22, INK, ls=.5))
        p.add(p.t(30 + wd, 290, f'{repos} REPOSITORIES · {UPDATED}', 'mono', 12, GREY))
        p.add(p.t(24, 350, 'Merged into repositories I don’t own.', 'ital', 26, INK))
        p.add(p.t(24, 382, '合并进别人仓库的 PR：修 bug、补测试、重构、改文档。', 'songt', 16, GREY))
        ly = 424
    else:
        plate_head(p, '贰', 'Upstream', 26, 196, 180, 'ital', 170, limit=860)
        od, wd = odometer(p, W - 36, 190, str(n), 'black', 136, BLUE, land=14, anchor='end')
        p.add(od)
        p.add(p.t(W - 36, 76, 'MERGED PULL REQUESTS', 'cond', 24, INK, 'end', ls=.6))
        rule(p, 226)
        p.add(p.t(40, 286, 'Merged into repositories I don’t own: fixes, tests, refactors, docs.', 'ital', 31, INK))
        p.add(p.t(40, 322, '合并进别人仓库的 PR：修 bug、补测试、做重构、改文档。', 'songt', 20, GREY))
        p.add(p.t(W - 36, 322, f'{repos} REPOSITORIES · AS OF {UPDATED}', 'mono', 13, GREY, 'end'))
        ly = 366
    # legend
    lx = 24 if m else 40
    for label, key in [('FIX', 'fix'), ('DOCS', 'docs'), ('TEST', 'test'), ('REFACTOR · FEAT · OTHER', 'other')]:
        p.add(rect(lx, ly - 13, 14, 14, TYPE_COLOR[key], f'stroke="{INK}" stroke-width="1"'))
        p.add(p.t(lx + 20, ly, label, 'mono', 12, INK))
        lx += 20 + width(label, 'mono', 12) + 22
    if not m:
        p.add(p.t(W - 36, ly, 'ONE TICK = ONE MERGED PR', 'mono', 12, GREY, 'end'))

    bx, bw = (14, W - 28) if m else (36, W - 72)
    p.add(rect(bx + 10, top + 10, bw, board_h, RED))
    p.add(rect(bx, top, bw, board_h, INK))
    hy = top + 29
    cols = {'rank': bx + 14, 'repo': bx + 48, 'flap': bx + (474 if m else 470), 'tick': bx + (48 if m else 586), 'last': bx + bw - 16}
    p.add(p.t(cols['rank'], hy, '#', 'mono', 11, LIGHT))
    p.add(p.t(cols['repo'], hy, 'UPSTREAM REPOSITORY', 'mono', 11, LIGHT, ls=.6))
    p.add(p.t(cols['flap'], hy, 'MERGED', 'mono', 11, LIGHT, ls=.6))
    if not m:
        p.add(p.t(cols['tick'], hy, 'BY TYPE', 'mono', 11, LIGHT, ls=.6))
    if not m:
        p.add(p.t(cols['last'], hy, 'LAST MERGED', 'mono', 11, LIGHT, 'end', ls=.6))
    p.add(line(bx, top + 44, bx + bw, top + 44, '#3A342E', 1))
    last = {}
    for pr in PRS:
        last[pr['repository']] = max(last.get(pr['repository'], ''), pr['merged_at'])
    by_repo = defaultdict(list)
    for pr in sorted(PRS, key=lambda q: q['merged_at']):
        by_repo[pr['repository']].append(pr_type(pr['title']))
    tick_room = (cols['last'] - (0 if m else 110)) - cols['tick']
    pitch = min(5.0, tick_room / max(COUNTS.values()))
    tw = max(1.2, pitch * .62)
    cyc = len(rows) * 1.1
    # scanning row highlight
    k = p.id('scan')
    p.css.append(f'.{k}{{animation:{k} {cyc:.1f}s steps({len(rows)},end) infinite}}'
                 f'@keyframes {k}{{to{{transform:translateY({len(rows) * rh}px)}}}}')
    p.add(f'<g class="{k}">{rect(bx, top + 46, bw, rh - 2, "#3B2A22")}{rect(bx, top + 46, 4, rh - 2, RED)}</g>')
    seg = 100 / len(rows)
    rnd = random.Random(5)
    for r, (repo, count) in enumerate(rows):
        y = top + 46 + r * rh
        base = y + rh * .68
        if m:
            p.add(p.t(cols['rank'], y+30, f'{r+1:02d}', 'mono', 16, LIGHT))
            p.add(p.t(cols['repo'], y+30, repo, 'monob', fit(repo, 'monob', 20, 398), PAPER))
            od,_=odometer(p, bx+bw-16, y+34, str(count), 'cond', 32, YEL if r==0 else PAPER, anchor='end')
            p.add(od)
            p.add(''.join(rect(cols['tick']+i*pitch, y+47, tw, 13, TYPE_COLOR[t]) for i,t in enumerate(by_repo[repo])))
            p.add(line(bx+10,y+rh-1,bx+bw-10,y+rh-1,'#2C2722',1))
            continue
        p.add(p.t(cols['rank'], base, f'{r + 1:02d}', 'mono', 12, LIGHT))
        owner, name = repo.split('/')
        if m and len(repo) > 25:
            owner = owner[:max(3, 24 - len(name))] + '…'
        p.add(f'<text x="{cols["repo"]}" y="{base:.1f}" font-family="{family("mono")}" font-size="{13 if m else 15}" fill="{LIGHT}">'
              f'{esc(owner)}/<tspan fill="{PAPER}" font-family="{family("monob")}">{esc(name)}</tspan></text>')
        for ch in owner + '/':
            p.chars[home('mono', ch)].add(ch)
        for ch in name:
            p.chars[home('monob', ch)].add(ch)
        # split-flap count
        digits = f'{count:>3}'
        a = r * seg
        for j, d in enumerate(digits):
            cx = cols['flap'] + j * (24 if m else 27)
            p.add(rect(cx, y + 3, 22 if m else 24, rh - 7, '#2A2520', 'rx="2"'))
            p.add(line(cx, y + 3 + (rh - 7) / 2, cx + (22 if m else 24), y + 3 + (rh - 7) / 2, INK, 1.2))
            if d == ' ':
                continue
            kf = p.id('fl')
            p.css.append(f'.{kf}{{animation:{kf} {cyc:.1f}s linear infinite}}'
                         f'@keyframes {kf}{{0%,{a:.2f}%{{opacity:1}}{a + .01:.2f}%,{a + seg * .7:.2f}%{{opacity:0}}{a + seg * .7 + .01:.2f}%,100%{{opacity:1}}}}')
            gx = cx + (11 if m else 12)
            p.add(p.t(gx, base + 1, d, 'monob', 17 if m else 19, YEL if r == 0 else PAPER, 'middle', cls=kf))
            for q in range(2):
                kn = p.id('fn')
                lo, hi = a + seg * .35 * q, a + seg * .35 * (q + 1)
                p.css.append(f'.{kn}{{opacity:0;animation:{kn} {cyc:.1f}s linear infinite}}'
                             f'@keyframes {kn}{{0%,{lo:.2f}%{{opacity:0}}{lo + .01:.2f}%,{hi:.2f}%{{opacity:1}}{hi + .01:.2f}%,100%{{opacity:0}}}}')
                p.add(p.t(gx, base + 1, str(rnd.randint(0, 9)), 'monob', 17 if m else 19, LIGHT, 'middle', cls=kn))
        # ticks, one per PR, in merge order
        ticks = ''.join(rect(cols['tick'] + i * pitch, y + 6, tw, rh - 12, TYPE_COLOR[t]) for i, t in enumerate(by_repo[repo]))
        p.add(ticks)
        if not m:
            p.add(p.t(cols['last'], base, last[repo][:10], 'mono', 12, LIGHT, 'end'))
        p.add(line(bx + 10, y + rh - 1, bx + bw - 10, y + rh - 1, '#2C2722', 1))
    fy = top + board_h - 16
    foot = 'SOURCE: GITHUB SEARCH · ' + ('REDRAWN DAILY' if m else 'is:pr author:ninglinLiu is:merged -user:ninglinLiu · REDRAWN DAILY 01:19 UTC')
    p.add(p.t(bx + 14, fy, foot, 'mono', 11, LIGHT, ls=.4))
    p.add(crops(W, H))
    return p.save()


# ---------------------------------------------------------------- 叁 film strip

def film(m):
    W, H = (600, 1010) if m else (1200, 850)
    p = Plate('film' + ('-m' if m else ''), W, H,
              'Script to Video: frames from a rendered showcase running as a film strip; research, voice, motion, delivery.')
    if m:
        plate_head(p, '叁', 'Script', 18, 150, 118, 'black', 92)
        p.add(p.t(150, 236, 'to Video', 'black', 92, INK))
        rule(p, 266, 24, W - 24)
        p.add(p.t(24, 318, 'Hand an agent an article;', 'ital', 28, INK))
        p.add(p.t(24, 352, 'get back a narrated 3D explainer.', 'ital', 28, INK))
        p.add(p.t(24, 388, '文章进去，动画出来，工程文件一并交付。', 'songt', 17, GREY))
        band_y, fw, pitch = 430, 240, 258
    else:
        plate_head(p, '叁', 'Script to Video', 26, 196, 180, 'black', 118)
        kicker(p, W - 36, 38, ['PLATE 叁 · CREATIVE TOOLING · AGENT SKILL · THREE.JS · FFMPEG'])
        rule(p, 226)
        p.add(p.t(40, 284, 'Hand an agent an article; get back a narrated 3D explainer and its editable project.', 'ital', 29, INK))
        p.add(p.t(40, 318, '文章进去，动画出来，工程文件一并交付。', 'songt', 20, GREY))
        band_y, fw, pitch = 356, 336, 360
    fh = fw * 9 / 16
    bh = fh + 70
    frames = sorted((ROOT / 'assets/film').glob('frame-*.jpg'))
    for i, f in enumerate(frames):
        p.defs.append(f'<image id="fr{i}" width="{fw}" height="{fh:.1f}" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{b64file(f)}"/>')
    period = pitch * len(frames)
    reps = math.ceil((W + 300) / period) + 1
    strip = rect(-200, band_y, period * reps + 400, bh, INK)
    for i in range(int((period * reps + 400) / 26)):
        x = -200 + i * 26
        strip += rect(x, band_y + 8, 13, 9, PAPER, 'rx="2"') + rect(x, band_y + bh - 17, 13, 9, PAPER, 'rx="2"')
    for r in range(reps):
        for i in range(len(frames)):
            x = r * period + i * pitch
            strip += f'<use href="#fr{i}" xlink:href="#fr{i}" x="{x}" y="{band_y + 40}"/>'
            strip += p.t(x, band_y + 34, f'▸ {i + 1:02d}A   NL·2026   SHOWCASE · BINANCE-1029', 'mono', 10, YEL, ls=.8)
    k = p.id('film')
    p.css.append(f'.{k}{{animation:{k} {period / 34:.1f}s linear infinite}}@keyframes {k}{{to{{transform:translateX(-{period}px)}}}}')
    p.add(f'<g transform="rotate(-1.6 {W / 2} {band_y + bh / 2})"><g class="{k}">{strip}</g></g>')

    # storyboard track with a playhead
    stages = [('01', 'RESEARCH', '查证据 · 写脚本'), ('02', 'VOICE', '配旁白 · 对时间轴'),
              ('03', 'MOTION', 'Three.js 搭景 · 运镜'), ('04', 'DELIVER', 'MP4 + 可编辑工程')]
    rnd = random.Random(3)
    ty = band_y + bh + (70 if m else 74)
    if m:
        cw, x0 = 276, 24
    else:
        cw, x0 = 279, 36
    for i, (num, en, zh) in enumerate(stages):
        if m:
            x, y = x0 + (i % 2) * (cw + 0), ty + (i // 2) * 150
        else:
            x, y = x0 + i * (cw + 4), ty
        p.add(p.t(x, y, num, 'mono', 13, RED))
        p.add(p.t(x + 28, y, en, 'cond', 26, INK, ls=.6))
        p.add(p.t(x, y + 28, zh, 'songt', 16, GREY))
        p.add(rect(x, y + 44, cw - 6, 44, PAPER2))
        bars = ''
        for b in range(int((cw - 16) / 6)):
            hgt = 6 + abs(math.sin(b * .7 + i)) * 22 * rnd.uniform(.4, 1)
            bars += rect(x + 6 + b * 6, y + 66 - hgt / 2, 3, hgt, BLUE)
        p.add(bars)
    if m:
        for row in range(2):
            y = ty + row * 150
            k = p.id('ph')
            p.css.append(f'.{k}{{animation:{k} 9s linear infinite;animation-delay:-{row * 4.5}s}}@keyframes {k}{{to{{transform:translateX({2 * cw - 6}px)}}}}')
            p.add(f'<g class="{k}">{rect(x0 - 1, y + 36, 3, 60, RED)}<path d="M{x0 - 6} {y + 34}h13l-6.5 8z" fill="{RED}"/></g>')
    else:
        k = p.id('ph')
        span = 4 * (cw + 4) - 10
        p.css.append(f'.{k}{{animation:{k} 12s linear infinite}}@keyframes {k}{{to{{transform:translateX({span}px)}}}}')
        p.add(f'<g class="{k}">{rect(x0 - 1, ty + 34, 3, 62, RED)}<path d="M{x0 - 6} {ty + 32}h13l-6.5 8z" fill="{RED}"/></g>')
    fy = H - 30
    p.add(p.t(x0, fy, 'FRAMES FROM THE PUBLISHED SHOWCASE · ninglinliu.github.io/script-to-video-skill', 'mono', 11 if m else 12, GREY))
    p.add(crops(W, H))
    return p.save()


# ---------------------------------------------------------------- 肆 index of projects

DESKS = [
    ('AI ENGINEERING', 'AI 工程', RED, [
        ('BID', 'Business Bid Agent', 'Bid documents: requirement extraction, local knowledge retrieval, structured drafting, DOCX out.', 'RAG · DOCX', 'PRIVATE'),
        ('XFIN', 'Xfinresearch Lab', 'Financial research agent with source tracking, deterministic tools and structured reports.', 'Python · Agents', 'PUBLIC'),
        ('CIO', 'ETF / CIO Reliability', 'Event-driven backtests, execution contracts, independently reconciled ledgers.', 'Python · CLI', 'PUBLIC'),
        ('WOLF', 'LLM Werewolf Arena', 'Multi-agent game: personas, role-specific behaviour, isolated private memory.', 'Python · LLM', 'PUBLIC'),
    ]),
    ('WEB3 · DATA · TRADING', '链上 · 数据 · 交易', BLUE, [
        ('EATLQ', 'EATLQ', 'On-chain data, crypto research and trading-system engineering.', 'Python · SQL · EVM · ClickHouse', 'PUBLIC'),
        ('SHDW', 'Solana Shadow Hunter', 'Copy-trading pipeline, event dedup, risk circuit breakers, Telegram alerts.', 'Python · Solana · Jupiter', 'PUBLIC'),
        ('ZKP', 'zkParallel', 'Parallel ZK batch-verification experiments on Monad testnet.', 'Solidity · Hardhat · Next.js', 'PUBLIC'),
        ('EDGE', 'EdgeNet.AI', 'Verifiable decentralised AI inference; Proof-of-Inference prototype.', 'Solidity · TypeScript · DePIN', 'PUBLIC'),
        ('DCPY', 'On-chain Data Copyright', 'Dataset licensing, tokenised receipts and on-chain provenance.', 'Solidity · ERC-721 · IPFS', 'PUBLIC'),
        ('SHRMP', 'ShrimpNest', 'Solana on-chain analytics and intelligence pipeline.', 'TypeScript · Solana', 'PUBLIC'),
    ]),
]


def index(m):
    W = 600 if m else 1200
    rh = 150 if m else 66
    rows = sum(len(d[3]) for d in DESKS)
    top = 380 if m else 360
    H = top + len(DESKS) * 44 + rows * rh + 150
    p = Plate('index' + ('-m' if m else ''), W, H,
              'Index of other projects: ' + '; '.join(f'{r[1]}: {r[2]}' for d in DESKS for r in d[3]))
    if m:
        plate_head(p, '肆', 'Index', 18, 150, 118, 'ital', 112)
        rule(p, 186, 24, W - 24)
        p.add(p.t(24, 240, 'Agents for paperwork and research;', 'ital', 26, INK))
        p.add(p.t(24, 272, 'systems that read the chain.', 'ital', 26, INK))
        p.add(p.t(24, 308, '写标书、做研究的 Agent，和读链上数据的系统。', 'songt', 17, GREY))
        p.add(p.t(24, 342, f'{rows} LISTINGS · 2 DESKS', 'mono', 12, GREY))
    else:
        plate_head(p, '肆', 'Index', 26, 196, 180, 'ital', 170)
        kicker(p, W - 36, 84, ['PLATE 肆 · OTHER WORK', f'{rows} LISTINGS · 2 DESKS', 'REPOSITORIES LINKED BELOW'])
        rule(p, 226)
        p.add(p.t(40, 288, 'Agents for paperwork and research; systems that read the chain.', 'ital', 31, INK))
        p.add(p.t(40, 324, '写标书、做研究的 Agent，和读链上数据的系统。', 'songt', 20, GREY))
    y = top
    r_all = 0
    cyc = rows * 1.6
    seg = 100 / rows
    x0 = 24 if m else 36
    x1 = W - x0
    for desk, zh, color, items in DESKS:
        p.add(rect(x0, y, x1 - x0, 36, INK))
        p.add(p.t(x0 + 14, y + 25, desk, 'cond', 22, PAPER, ls=1))
        p.add(p.t(x0 + 22 + width(desk, 'cond', 22, 1), y + 24, zh, 'songt', 16, LIGHT))
        p.add(p.t(x1 - 14, y + 23, f'{len(items)} LISTINGS', 'mono', 11, LIGHT, 'end'))
        y += 44
        for sym, name, desc, stack, status in items:
            k = p.id('row')
            a = r_all * seg
            p.css.append(f'.{k}{{opacity:0;animation:{k} {cyc:.1f}s linear infinite}}'
                         f'@keyframes {k}{{0%,{a:.2f}%{{opacity:0}}{a + .01:.2f}%,{a + seg:.2f}%{{opacity:1}}{a + seg + .01:.2f}%,100%{{opacity:0}}}}')
            p.add(rect(x0, y - 2, x1 - x0, rh - 4, YEL, f'class="{k} mul"'))
            if m:
                p.add(p.t(x0 + 4, y + 44, sym, 'cond', 44, color))
                sw = max(width(sym, 'cond', 44), 92)
                p.add(p.t(x0 + sw + 16, y + 26, name, 'black', 25, INK))
                p.add(p.t(x0 + sw + 16, y + 52, stack, 'mono', 16, GREY))
                p.add(p.t(x1 - 4, y + 24, status, 'mono', 10, RED if status == 'PRIVATE' else GREY, 'end', ls=.8))
                words, lines_, cur = desc.split(), [], ''
                for wd_ in words:
                    if width(cur + ' ' + wd_, 'sans', 20) > x1 - x0 - 10:
                        lines_.append(cur)
                        cur = wd_
                    else:
                        cur = (cur + ' ' + wd_).strip()
                lines_.append(cur)
                for i, ln in enumerate(lines_):
                    p.add(p.t(x0 + 4, y + 82 + i * 25, ln, 'sans', 20, INK2))
            else:
                p.add(p.t(x0 + 8, y + 46, sym, 'cond', 48, color))
                p.add(p.t(x0 + 190, y + 26, name, 'black', 23, INK))
                p.add(p.t(x0 + 190, y + 50, desc, 'sans', 16, INK2))
                p.add(p.t(x1 - 110, y + 26, stack, 'mono', 12, GREY, 'end'))
                p.add(rect(x1 - 96, y + 11, 90, 22, 'none', f'stroke="{RED if status == "PRIVATE" else INK}" stroke-width="1.2"'))
                p.add(p.t(x1 - 51, y + 26, status, 'mono', 11, RED if status == 'PRIVATE' else INK, 'middle', ls=.8))
            p.add(line(x0, y + rh - 6, x1, y + rh - 6, INK, 1, 'stroke-dasharray="1 4"'))
            y += rh
            r_all += 1
    # a little chain of blocks: each project's name hashed, linked, moving
    cy = H - 74
    blocks = [(r[0], hashlib.sha256(r[1].encode()).hexdigest()[:8]) for d in DESKS for r in d[3]]
    pitch = 150 if not m else 128
    period = pitch * len(blocks)
    chain = ''
    for rep in range(3):
        for i, (sym, hx) in enumerate(blocks):
            x = rep * period + i * pitch
            chain += rect(x, cy - 26, 96, 52, PAPER, f'stroke="{INK}" stroke-width="1.5"')
            chain += p.t(x + 8, cy - 6, sym, 'monob', 13, INK)
            chain += p.t(x + 8, cy + 14, '0x' + hx, 'mono', 11, GREY)
            chain += line(x + 96, cy, x + pitch, cy, INK, 1.5, 'stroke-dasharray="3 3"')
    k = p.id('chain')
    p.css.append(f'.{k}{{animation:{k} {period / 22:.1f}s linear infinite}}@keyframes {k}{{to{{transform:translateX(-{period}px)}}}}')
    p.add(f'<g class="{k}">{chain}</g>')
    p.add(p.t(x0, H - 20, 'BLOCKS: SHA-256 OF EACH PROJECT NAME · 纯装饰，不是链上数据', 'mono', 10, GREY))
    p.add(crops(W, H))
    return p.save()


# ---------------------------------------------------------------- 伍 toolkit

AREAS = [('AGENTS', 'RAG · Tool calling · MCP · SSE · JSON Schema'),
         ('WEB', 'React · Next.js · Tailwind CSS · Three.js'),
         ('DATA', 'pandas · NumPy · SQL · ClickHouse · Redis · SQLite'),
         ('SHIP', 'Linux · Docker · Git · CI/CD')]


def toolkit(m):
    W, H = (600, 1270) if m else (1200, 900)
    p = Plate('toolkit' + ('-m' if m else ''), W, H,
              'Toolkit. Languages: Python, Java, TypeScript, Solidity. ' + '. '.join(f'{a}: {b}' for a, b in AREAS))
    if m:
        plate_head(p, '伍', 'Toolkit', 18, 150, 118, 'ital', 104)
        rule(p, 186, 24, W - 24)
        words = [('Python', 'black', fit('Python', 'black', 150, W - 48), INK, 24, 330, None),
                 ('Java', 'cond', 170, RED, 24, 500, None),
                 ('TypeScript', 'ital', fit('TypeScript', 'ital', 118, W - 48), BLUE, 24, 620, None),
                 ('Solidity', 'wide', fit('Solidity', 'wide', 74, W - 48), INK, 24, 716, None)]
    else:
        plate_head(p, '伍', 'Toolkit', 26, 196, 180, 'ital', 170)
        kicker(p, W - 36, 84, ['PLATE 伍 · TOOLKIT', 'LANGUAGES · AGENTS · WEB · DATA · SHIP'])
        rule(p, 226)
        words = [('Python', 'black', 180, INK, 30, 424, None), ('Java', 'cond', 230, RED, W - 36, 440, 'end'),
                 ('TypeScript', 'ital', 140, BLUE, W - 36, 572, 'end'), ('Solidity', 'wide', 66, INK, 36, 560, None)]
    for i, (wd, key, size, color, x, y, anchor) in enumerate(words):
        k = p.id('mis')
        p.css.append(f'.{k}{{animation:{k} 12s ease-in-out infinite;animation-delay:-{i * 3}s}}'
                     f'@keyframes {k}{{0%,80%,100%{{transform:translate(0,0)}}86%{{transform:translate(5px,-3px)}}92%{{transform:translate(-2px,1px)}}}}')
        p.add(f'<g class="{k}">{p.t(x, y, wd, key, size, color, anchor, cls="mul")}</g>')
    # marquee band
    by = 790 if m else 624
    unit = ' ● '.join(b.replace(' · ', ' ● ') for _, b in AREAS).upper() + ' ● '
    p.add(f'<g transform="rotate(-1.4 {W / 2} {by})">{rect(-60, by - 26, W + 120, 50, BLUE)}'
          f'{marquee(p, -60, by + 8, unit, "cond", 26, PAPER, W + 120, speed=36, ls=1)}</g>')
    # four columns
    cy = 860 if m else 700
    for i, (a, b) in enumerate(AREAS):
        if m:
            x, y = 24 + (i % 2) * 280, cy + (i // 2) * 190
        else:
            x, y = 40 + i * 284, cy
        p.add(p.t(x, y, a, 'cond', 26, RED, ls=1))
        p.add(line(x, y + 10, x + (250 if m else 262), y + 10, INK, 1.5))
        for j, item in enumerate(b.split(' · ')):
            p.add(p.t(x, y + 38 + j * 26, item, 'mono', 20 if m else 15, INK))
    if m:
        p.add(p.t(W - 24, 490, '核心语言', 'songt', 20, GREY, 'end'))
    else:
        p.add(p.t(40, 600, '核心语言', 'songt', 20, GREY))
    p.add(crops(W, H))
    return p.save()


# ---------------------------------------------------------------- 陆 activity + languages

LANG_FILLS = [INK, RED, BLUE, YEL, 'url(#hk)', 'url(#hr)', 'url(#hb)', 'url(#dk)']


def activity(m):
    W, H = (600, 1180) if m else (1200, 860)
    days = A['calendar']
    total = sum(d['count'] for d in days)
    active = sum(d['count'] > 0 for d in days)
    best = run = 0
    for d in days:
        run = run + 1 if d['count'] else 0
        best = max(best, run)
    peak = max(d['count'] for d in days)
    langs = A['languages']
    lt = sum(x['bytes'] for x in langs)
    p = Plate('activity' + ('-m' if m else ''), W, H,
              f'GitHub activity {days[0]["date"]} to {days[-1]["date"]}: {total:,} contributions on {active} active days; '
              f'longest streak {best} days; best day {peak}. Languages by code bytes: '
              + ', '.join(f'{x["name"]} {x["bytes"] / lt * 100:.1f}%' for x in langs[:8]))
    p.defs.append(
        f'<pattern id="hk" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">{rect(0, 0, 7, 7, PAPER)}{rect(0, 0, 3, 7, INK)}</pattern>'
        f'<pattern id="hr" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)">{rect(0, 0, 7, 7, PAPER)}{rect(0, 0, 3, 7, RED)}</pattern>'
        f'<pattern id="hb" width="6" height="6" patternUnits="userSpaceOnUse">{rect(0, 0, 6, 6, PAPER)}<circle cx="3" cy="3" r="1.9" fill="{BLUE}"/></pattern>'
        f'<pattern id="dk" width="5" height="5" patternUnits="userSpaceOnUse">{rect(0, 0, 5, 5, PAPER)}<circle cx="2.5" cy="2.5" r="1.3" fill="{INK}"/></pattern>')
    if m:
        plate_head(p, '陆', '365 days', 18, 150, 118, 'ital', 96)
        rule(p, 186, 24, W - 24)
        p.add(p.t(24, 222, f'{days[0]["date"]} → {days[-1]["date"]} · PUBLIC CONTRIBUTION CALENDAR', 'mono', 11, GREY))
        sx, sy, ox, oy, hk = 8.6, 3.7, 82, 352, 11
    else:
        plate_head(p, '陆', '365 days', 26, 196, 180, 'ital', 170, limit=W - 300)
        kicker(p, W - 36, 84, ['PLATE 陆 · ACTIVITY', f'{days[0]["date"]} → {days[-1]["date"]}', 'PUBLIC CONTRIBUTION CALENDAR'])
        rule(p, 226)
        sx, sy, ox, oy, hk = 12.4, 5.2, 112, 376, 16
    start = date.fromisoformat(days[0]['date'])
    offset = (start.weekday() + 1) % 7
    tops = [PAPER2, YEL, ORANGE, RED, BLUE]
    city = ''
    for i, d in enumerate(days):
        week, wday = (i + offset) // 7, (i + offset) % 7
        x = ox + (week - wday) * sx
        y = oy + (week + wday) * sy
        hh = 2 if not d['count'] else 6 + math.log1p(d['count']) * hk
        top = tops[d['level']]
        a, b, c, dd = (x, y), (x + sx - 1, y + sy), (x, y + 2 * sy), (x - sx + 1, y + sy)

        def poly(pts, col):
            return '<polygon points="' + ' '.join(f'{u:.1f},{v:.1f}' for u, v in pts) + f'" fill="{col}"/>'
        cube = poly([dd, c, (c[0], c[1] - hh), (dd[0], dd[1] - hh)], shade(top, .8))
        cube += poly([b, c, (c[0], c[1] - hh), (b[0], b[1] - hh)], shade(top, .64))
        cube += poly([(u, v - hh) for u, v in (a, b, c, dd)], top)
        if d['count']:
            city += f'<g class="rise" style="animation-delay:-{week * .19:.2f}s">{cube}</g>'
        else:
            city += cube
    p.css.append('.rise{transform-box:fill-box;transform-origin:50% 100%;animation:rise 6s ease-in-out infinite}'
                 '@keyframes rise{0%,100%{transform:scaleY(1)}50%{transform:scaleY(1.22)}}')
    p.add(city)
    # last day flag
    i = len(days) - 1
    week, wday = (i + offset) // 7, (i + offset) % 7
    fx, fy = ox + (week - wday) * sx, oy + (week + wday) * sy - (6 + math.log1p(days[-1]['count']) * hk)
    p.add(line(fx, fy, fx, fy - 74, INK, 1.5), f'<path d="M{fx} {fy - 74}h26l-6 7 6 7h-26z" fill="{RED}" class="blink"/>')
    date_on_left = fx + 32 + width(days[-1]['date'], 'mono', 11) > W - 24
    p.add(p.t(fx - 8 if date_on_left else fx + 32, fy - 62,
              days[-1]['date'], 'mono', 11, INK, 'end' if date_on_left else None))
    # legend
    lx, ly = (24, 520) if m else (40, 690)
    p.add(p.t(lx, ly, 'LESS', 'mono', 11, GREY))
    for j, c in enumerate(tops):
        p.add(rect(lx + 40 + j * 20, ly - 11, 14, 14, c))
    p.add(p.t(lx + 146, ly, 'MORE · HEIGHT = LOG(CONTRIBUTIONS)', 'mono', 11, GREY))
    # stats
    stats = [(f'{total:,}', 'CONTRIBUTIONS', '贡献'), (str(active), 'ACTIVE DAYS', '活跃天数'),
             (f'{best}', 'LONGEST STREAK', '最长连续'), (str(peak), 'BEST DAY', '单日最多')]
    for j, (v, en, zh) in enumerate(stats):
        if m:
            x, y = 24 + (j % 2) * 286, 640 + (j // 2) * 140
        else:
            x, y = 792 + (j % 2) * 206, 352 + (j // 2) * 160
        od, wd = odometer(p, x - 2, y, v, 'black', 60 if m else 58, INK, land=12 + j * 6)
        p.add(od)
        p.add(p.t(x, y + 34, en, 'cond', 20, RED, ls=.8))
        p.add(p.t(x, y + 60, zh, 'songt', 16, GREY))
    # language strip
    sy0 = 920 if m else 744
    x0, x1 = (24, W - 24) if m else (40, W - 40)
    p.add(p.t(x0, sy0 - 18, f'LANGUAGES · CODE BYTES IN {len(A["repositories"])} PUBLIC REPOSITORIES · 按代码字节统计', 'mono', 11, GREY))
    x = x0
    for j, lang in enumerate(langs):
        wseg = (x1 - x0) * lang['bytes'] / lt
        p.add(rect(x, sy0, wseg, 26, LANG_FILLS[j] if j < 8 else PAPER2, f'stroke="{INK}" stroke-width=".8"'))
        x += wseg
    cols = 2 if m else 4
    for j, lang in enumerate(langs[:8]):
        name = {'Jupyter Notebook': 'Jupyter'}.get(lang['name'], lang['name'])
        x = x0 + (j % cols) * ((x1 - x0) / cols)
        y = sy0 + 56 + (j // cols) * 28
        p.add(rect(x, y - 12, 14, 14, LANG_FILLS[j], f'stroke="{INK}" stroke-width=".8"'))
        p.add(p.t(x + 22, y, name, 'mono', 13, INK))
        p.add(p.t(x + (x1 - x0) / cols - 24, y, f'{lang["bytes"] / lt * 100:.1f}%', 'monob', 13, INK, 'end'))
    p.add(crops(W, H))
    return p.save()


# ---------------------------------------------------------------- 柒 stamps

def stamps(m):
    cols = 4 if m else 10
    W = 600 if m else 1200
    x0 = 24 if m else 36
    cell = (W - 2 * x0) / cols
    sh = cell * 1.2
    groups = [('DEVELOPMENT & PLATFORMS', '开发与平台', [i for i in T if i['group'] == 'development']),
              ('WEB3 & ON-CHAIN', '链上生态', [i for i in T if i['group'] == 'web3'])]
    top = 330
    H = top + sum(60 + math.ceil(len(g[2]) / cols) * sh for g in groups) + 70
    H = int(H)
    p = Plate('stamps' + ('-m' if m else ''), W, H, 'Ecosystem stamps: ' + ', '.join(i['name'] for i in T))
    if m:
        plate_head(p, '柒', 'Ecosystem', 18, 150, 118, 'ital', 84)
        rule(p, 186, 24, W - 24)
        p.add(p.t(24, 240, 'Tools I build with; chains I read.', 'ital', 27, INK))
        p.add(p.t(24, 276, '常用的工具，常看的链。', 'songt', 17, GREY))
    else:
        plate_head(p, '柒', 'Ecosystem', 26, 196, 180, 'ital', 160, limit=W - 300)
        kicker(p, W - 36, 84, ['PLATE 柒 · ECOSYSTEM', f'{len(T)} STAMPS · CURATED'])
        rule(p, 226)
        p.add(p.t(40, 286, 'Tools I build with; chains I read.', 'ital', 31, INK))
        p.add(p.t(40 + width('Tools I build with; chains I read.', 'ital', 31) + 18, 286, '常用的工具，常看的链。', 'songt', 20, GREY))
    rnd = random.Random(26)
    y = top
    no = 0
    icon_cache = {}
    marks = []
    for label, zh, items in groups:
        p.add(p.t(x0, y + 20, label, 'cond', 22, INK, ls=1))
        p.add(p.t(x0 + width(label, 'cond', 22, 1) + 10, y + 19, zh, 'songt', 15, GREY))
        p.add(line(x0, y + 32, W - x0, y + 32, INK, 1.5))
        y += 52
        for i, icon in enumerate(items):
            no += 1
            cx = x0 + (i % cols) * cell + cell / 2
            cy = y + (i // cols) * sh + sh / 2
            sw, shh = cell - 12, sh - 14
            dark = icon['group'] == 'web3' and icon['slug'] != 'circle'
            face = INK2 if dark else STAMP
            fg = PAPER if dark else INK
            g = rect(-sw / 2, -shh / 2, sw, shh, face)
            g += rect(-sw / 2 + 6, -shh / 2 + 6, sw - 12, shh - 12, 'none', f'stroke="{fg}" stroke-opacity=".35" stroke-width="1"')
            # perforations
            r = 2.6
            nx, ny = int(sw / 8), int(shh / 8)
            for k in range(nx + 1):
                xx = -sw / 2 + k * sw / nx
                g += f'<circle cx="{xx:.1f}" cy="{-shh / 2:.1f}" r="{r}" fill="{PAPER}"/><circle cx="{xx:.1f}" cy="{shh / 2:.1f}" r="{r}" fill="{PAPER}"/>'
            for k in range(ny + 1):
                yy = -shh / 2 + k * shh / ny
                g += f'<circle cx="{-sw / 2:.1f}" cy="{yy:.1f}" r="{r}" fill="{PAPER}"/><circle cx="{sw / 2:.1f}" cy="{yy:.1f}" r="{r}" fill="{PAPER}"/>'
            isz = sw * .46
            path = ROOT / 'assets/icons' / icon.get('file', icon['slug'] + '.svg')
            if path not in icon_cache:
                mime = mimetypes.guess_type(path.name)[0] or 'image/svg+xml'
                iid = p.id('ic')
                p.defs.append(f'<image id="{iid}" width="100" height="100" href="data:{mime};base64,{b64file(path)}"/>')
                icon_cache[path] = iid
            g += f'<use href="#{icon_cache[path]}" xlink:href="#{icon_cache[path]}" transform="translate({-isz / 2:.1f} {-shh / 2 + 16:.1f}) scale({isz / 100:.3f})"/>'
            name = icon['name'].upper()
            fs = 18 if m else 14
            while width(name, 'cond', fs, .4) > sw - 14 and fs > 14:
                fs -= 1
            g += p.t(0, shh / 2 - 15, name, 'cond', fs, fg, 'middle', ls=.4)
            g += p.t(-sw / 2 + 10, -shh / 2 + 18, f'{no:02d}', 'mono', 9, fg, extra='opacity=".7"')
            rot = rnd.uniform(-3.2, 3.2)
            p.add(f'<g transform="translate({cx:.1f} {cy:.1f}) rotate({rot:.2f})">'
                  f'<rect x="{-sw / 2 + 3:.1f}" y="{-shh / 2 + 4:.1f}" width="{sw:.1f}" height="{shh:.1f}" fill="{INK}" opacity=".16"/>{g}</g>')
        rem = len(items) % cols
        if rem:  # a postmark lands in the blank corner of the sheet
            marks.append((x0 + (rem + (cols - rem) / 2) * cell, y + (len(items) // cols) * sh + sh / 2))
        y += math.ceil(len(items) / cols) * sh + 8
    # postmarks, stamped in turn
    for j, (mx, my) in enumerate(marks):
        r = 74 if not m else 52
        k = p.id('pm')
        a = j * 50
        p.css.append(f'.{k}{{opacity:0;transform-box:fill-box;transform-origin:center;animation:{k} 12s ease-out infinite}}'
                     f'@keyframes {k}{{0%,{a:.1f}%{{opacity:0;transform:scale(1.5)}}{a + 3:.1f}%{{opacity:.92;transform:scale(1)}}'
                     f'{a + 44:.1f}%{{opacity:.92;transform:scale(1)}}{a + 49:.1f}%,100%{{opacity:0;transform:scale(1)}}}}')
        wx = mx + r * .9 if mx < W * .6 else mx - r * .9 - 144
        waves = ''.join(f'<path d="M{wx:.1f} {my - 26 + q * 13:.1f} q18 -9 36 0 t36 0 t36 0 t36 0" fill="none" stroke="{RED}" stroke-width="3"/>' for q in range(5))
        ring = ring_text(p, mx, my, r * .74, f'NINGLINLIU ● SHANGHAI ● {UPDATED} ● ', 'monob', 12 if not m else 10, RED, dur=9999)
        mark = (f'<circle cx="{mx}" cy="{my}" r="{r}" fill="none" stroke="{RED}" stroke-width="3.5"/>'
                f'<circle cx="{mx}" cy="{my}" r="{r * .56:.1f}" fill="none" stroke="{RED}" stroke-width="2"/>'
                + ring + p.t(mx, my + 7, UPDATED[5:].replace('-', '.'), 'monob', 20 if not m else 16, RED, 'middle') + waves)
        if m:
            mark=mark.replace(waves,'')
        p.add(f'<g class="{k} mul" transform="rotate({-12 + j * 20} {mx} {my})"><g>{mark}</g></g>')
    p.add(crops(W, H))
    return p.save()


# ---------------------------------------------------------------- 捌 contact + colophon

def colophon(m):
    W, H = (600, 1000) if m else (1200, 660)
    p = Plate('colophon' + ('-m' if m else ''), W, H,
              'Contact: x07514475479@gmail.com · LinkedIn yu-liu-359521383 · X @ninglin000. Colophon: set in Bodoni Moda, '
              'Archivo, JetBrains Mono and Noto Serif SC; plates redrawn daily by GitHub Actions.', bg=INK, grain='light')
    p.add(halftone(0, 0, W, H, 18 if m else 22, '#2A2521', W * .1, H, W * .9, 8.5 if m else 10.5))
    if m:
        p.add(p.t(24, 40, 'PLATE 捌 · CONTACT · COLOPHON', 'mono', 12, LIGHT, ls=.8))
        p.add(p.t(14, 290, '来信', 'song', 250, RED))
        p.add(p.t(24, 370, 'x07514475479', 'ital', 50, PAPER))
        p.add(p.t(24, 424, '@gmail.com', 'ital', 50, PAPER))
        rows = [('LINKEDIN', '/in/yu-liu-359521383'), ('X', '@ninglin000'), ('WEB', 'omniaihello.com'), ('GITHUB', '@ninglinLiu')]
        for i, (a, b) in enumerate(rows):
            p.add(p.t(24, 486 + i * 34, a, 'monob', 17, RED, ls=.8))
            p.add(p.t(150, 486 + i * 34, b, 'mono', 20, PAPER))
        p.add(p.t(24, 626, '欢迎来信，中文英文都行。', 'songt', 18, LIGHT))
        cy0 = 690
        lines = ['COLOPHON', 'Set in Bodoni Moda, Archivo, JetBrains', 'Mono and Noto Serif SC (SIL OFL).',
                 'Drawn in Python from public GitHub', 'data; redrawn daily at 01:19 UTC.', f'This edition: {UPDATED}.']
        for i, s in enumerate(lines):
            p.add(p.t(24, cy0 + i * 22, s, 'monob' if i == 0 else 'mono', 12, RED if i == 0 else LIGHT, ls=.4))
        p.add(p.t(24, cy0 + 6 * 22 + 10, '排版：Bodoni Moda · Archivo · JetBrains Mono · 思源宋体', 'songt', 13, LIGHT))
        sx, sy, ss = 470, 860, 112
        p.add(control_strip(p, 24, H - 46, 16, dark=True))
    else:
        p.add(p.t(40, 52, 'PLATE 捌 · CONTACT · COLOPHON', 'mono', 13, LIGHT, ls=.8))
        p.add(p.t(26, 352, '来信', 'song', 300, RED))
        p.add(p.t(40, 452, 'x07514475479@gmail.com', 'ital', fit('x07514475479@gmail.com', 'ital', 62, 700), PAPER))
        rows = [('LINKEDIN', '/in/yu-liu-359521383'), ('X', '@ninglin000'), ('WEB', 'omniaihello.com')]
        x = 40
        for a, b in rows:
            p.add(p.t(x, 510, a, 'monob', 13, RED, ls=.8))
            p.add(p.t(x + width(a, 'monob', 13, .8) + 10, 510, b, 'mono', 16, PAPER))
            x += width(a, 'monob', 13, .8) + width(b, 'mono', 16) + 44
        p.add(p.t(40, 556, '欢迎来信，中文英文都行。', 'songt', 20, LIGHT))
        cx0, cy0 = 780, 120
        p.add(line(cx0 - 24, 90, cx0 - 24, 470, '#3A342E', 1))
        lines = ['COLOPHON', '', 'Set in Bodoni Moda, Archivo,', 'JetBrains Mono and Noto Serif SC,',
                 'all under the SIL Open Font License.', '', 'Every plate is drawn by', 'scripts/build_plates.py from public',
                 'GitHub data and redrawn each day', 'at 01:19 UTC by GitHub Actions.', '', f'This edition: {UPDATED}.']
        for i, s in enumerate(lines):
            if s:
                p.add(p.t(cx0, cy0 + i * 24, s, 'monob' if i == 0 else 'mono', 14, RED if i == 0 else LIGHT, ls=.3))
        p.add(p.t(cx0, cy0 + 12 * 24 + 18, '字体均采用 SIL 开源授权。', 'songt', 15, LIGHT))
        sx, sy, ss = 1080, 540, 132
        p.add(control_strip(p, 40, H - 52, 18, dark=True))
        p.add(p.t(W - 40, H - 36, 'END OF FOLIO · 完', 'mono', 12, LIGHT, 'end', ls=1))
    k = p.id('stamp')
    p.css.append(f'.{k}{{transform-box:fill-box;transform-origin:center;animation:{k} 9s cubic-bezier(.3,1.4,.5,1) infinite}}'
                 f'@keyframes {k}{{0%{{opacity:0;transform:scale(1.6) rotate(8deg)}}6%{{opacity:1;transform:scale(1) rotate(0)}}90%{{opacity:1;transform:scale(1)}}100%{{opacity:0;transform:scale(1)}}}}')
    p.add(seal(p, sx, sy, ss, rot=6, cls=k))
    p.add(crops(W, H, LIGHT))
    return p.save()


PLATES = [masthead, omniai, upstream, film, index, toolkit, activity, stamps, colophon]


def main():
    total = 0
    for fn in PLATES:
        for m in (False, True):
            size = fn(m)
            total += size
            print(f'{fn.__name__ + ("-m" if m else ""):14} {size / 1024:8.1f} KB')
    print(f'{len(PLATES) * 2} plates, {total / 1024 / 1024:.2f} MB, {len(PRS)} PRs / {len(COUNTS)} repositories, edition {UPDATED}')


if __name__ == '__main__':
    main()
