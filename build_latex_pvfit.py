"""Build Latex table with pv map fitting results."""
from configparser import ConfigParser
from pathlib import Path

from common_paths import CONFIGS

cfgs = CONFIGS / 'plots/papers'
keys_unres = ('alpha', 'amplitude', 'vsys', 'offset0')
keys_kep = ('amplitude', 'mass')
lines = {}
for cfg in cfgs.glob('group_pv_maps.*.cfg'):
    print(cfg)
    config = ConfigParser()
    config.read(cfg)

    for section in config.sections():
        if 'function' not in config[section]:
            continue
        print(section)
        if 'keplerian' in section:
            src = section[:-14]
            lines.setdefault(src, list())
            line = []
            for key in keys_kep:
                val = config[section][f'model_{key}']
                err = config[section][f'model_sd_{key}']
                line += [f' {val}\pm{err} ']
            lines[src] = lines[src] + line
        if 'unrestricted' in section:
            src = section[:-17]
            lines.setdefault(src, list())
            line = []
            for key in keys_unres:
                val = config[section][f'model_{key}']
                err = config[section][f'model_sd_{key}']
                line += [f' {val}\pm{err} ']
            lines[src] = line + lines[src]

join_lines = [key + ' & ' + ' & '.join(val) for key, val in sorted(lines.items())]

print('\n'.join(join_lines))
