"""Freeze the plate typefaces into small static masters (run locally, rarely).

Sources are SIL OFL variable fonts: Bodoni Moda, Archivo and JetBrains Mono
(github.com/google/fonts) and Noto Serif SC. Each axis is pinned to one instance
and trimmed to the characters the plates can draw. The Chinese master keeps only
the characters written in scripts/build_plates.py, so re-run this script after
changing Chinese copy there. scripts/build_plates.py subsets these masters again
per plate before embedding them.

usage: python scripts/build_fonts.py <dir with the variable fonts>
"""
from pathlib import Path
import re
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/fonts'
SRC = Path(sys.argv[1] if len(sys.argv) > 1 else '.')

LATIN = list(range(0x20, 0x7F)) + list(range(0xA0, 0x180)) + list(range(0x2010, 0x2060)) \
    + list(range(0x2190, 0x21FF)) + list(range(0x2200, 0x2270)) + list(range(0x25A0, 0x2600)) \
    + [0x20AC, 0x2116, 0x2122, 0x2212, 0x2715, 0x2726, 0x2731, 0x2733, 0x2756]

MASTERS = [
    # file name, source, axis pins
    # Low optical sizes on purpose: at opsz 96 the hairlines vanish and
    # "1,000+" reads as "1.000", "Upstream" as "l pstream".
    ('display-black.ttf', 'BodoniModa.ttf', {'wght': 900, 'opsz': 20}),
    ('display-italic.ttf', 'BodoniModa-Italic.ttf', {'wght': 700, 'opsz': 18}),
    ('display-book.ttf', 'BodoniModa.ttf', {'wght': 500, 'opsz': 9}),
    ('grotesk-condensed.ttf', 'Archivo.ttf', {'wght': 900, 'wdth': 62}),
    ('grotesk-text.ttf', 'Archivo.ttf', {'wght': 500, 'wdth': 100}),
    ('grotesk-wide.ttf', 'Archivo.ttf', {'wght': 800, 'wdth': 125}),
    ('mono.ttf', 'JetBrainsMono.ttf', {'wght': 500}),
    ('mono-bold.ttf', 'JetBrainsMono.ttf', {'wght': 800}),
    ('song-black.ttf', 'NotoSerifSC-VF.ttf', {'wght': 900}),
    ('song-text.ttf', 'NotoSerifSC-VF.ttf', {'wght': 600}),
]


def cjk_codepoints():
    source = (ROOT / 'scripts/build_plates.py').read_text(encoding='utf-8')
    chars = {ord(c) for c in source if ord(c) > 0x2E7F}
    chars |= set(range(0x3000, 0x3020)) | set(range(0xFF01, 0xFF5F))
    return sorted(chars | set(LATIN))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cjk = cjk_codepoints()
    for name, source, pins in MASTERS:
        path = SRC / source
        if not path.exists():
            path = Path('C:/Windows/Fonts') / source
        font = instancer.instantiateVariableFont(TTFont(path), pins)
        options = subset.Options()
        options.layout_features = ['kern', 'liga', 'tnum', 'lnum', 'case', 'vert', 'vrt2', 'locl']
        options.name_IDs = ['*']
        options.notdef_outline = True
        options.hinting = False
        options.desubroutinize = True
        sub = subset.Subsetter(options)
        sub.populate(unicodes=cjk if name.startswith('song') else LATIN)
        sub.subset(font)
        font.save(OUT / name)
        print(f'{name:24} {(OUT / name).stat().st_size / 1024:7.1f} KB')


if __name__ == '__main__':
    main()
