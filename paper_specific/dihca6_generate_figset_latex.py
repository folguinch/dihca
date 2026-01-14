from pathlib import Path
import textwrap

figs = Path('/data/folguin/Documents/Papers/dihca6/submission2/figures')
fig1_map = figs / 'fig01set/figset.txt'
fig2_map = figs / 'fig02set/figset.txt'
fig3_map = figs / 'fig03set/figset.txt'
outfig = figs / 'figsets.tex'

template = [r'\begin{{figure}}',
            r'\plotone{{{0}}}',
            r'\caption{{{1}}}',
            r'\end{{figure}}']
template = '\n'.join(template)

texlines = []
with fig1_map.open() as f:
    lines = f.readlines()

for ln in lines:
    fig, cap = ln.split('&')
    texlines.append(template.format(fig.strip(), cap.strip()))


template = [r'\begin{{figure*}}',
            r'\plotone{{{0}}}',
            r'\caption{{{1}}}',
            r'\end{{figure*}}']
template = '\n'.join(template)

with fig2_map.open() as f:
    lines = f.readlines()

for ln in lines:
    fig, cap = ln.split('&')
    texlines.append(template.format(fig.strip(), cap.strip()))

with fig3_map.open() as f:
    lines = f.readlines()

for ln in lines:
    fig, cap = ln.split('&')
    texlines.append(template.format(fig.strip(), cap.strip()))

texlines = '\n'.join(texlines)
outfig.write_text(texlines)
