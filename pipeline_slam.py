"""Fit PV maps using SLAM."""
from configparser import ConfigParser
from pathlib import Path
import sys
sys.path.insert(0, '/home/faoch/clones/SLAM/')

import numpy as np
from pvanalysis import PVAnalysis
from line_little_helper.molecule import Molecule

from pipeline_feria import SOURCES, SECTIONS
from source_pipeline_extracted import SAVED_MOLS

MOLECULE = 'CH3OH'
TRANSITION = '18(3,15)-17(4,14)A,vt=0'
RESULTS = Path('/mnt/metis/dihca/results')

def run_slam(fitsfile, outdir):
    outname = outdir / 'pvanalysis'  # file name header for outputs
    incl = 80.  # deg
    vsys = -53.  # km/s
    dist = 3250.  # pc
    rms = 1.5e-3  # Jy/beam
    thr = 3.  # rms
    ridgemode = 'gauss'  # 'mean' or 'gauss'
    xlim = [-1000, 0, 0, 1000]  # au; [-outlim, -inlim, inlim, outlim]
    vlim = np.array([-10, 0, 0, 10]) + vsys  # km/s
    Mlim = [5, 40]  # M_sun; to exclude unreasonable points
    xlim_plot = [100., 800.]  # au; [inlim, outlim]
    vlim_plot = [0, 6.]  # km/s
    use_velocity = False  # cuts along the velocity direction
    use_position = True  # cuts along the positional direction
    include_vsys = True  # vsys offset. False means vsys=0.
    include_dp = False  # False means a single power
    include_pin = False  # False means pin=0.5 (Keplerian).
    fixed_pin = 0.5  # Fixed pin when include_pin is False.
    fixed_dp = 0.0  # Fixed dp when include_dp is False.
    show_pv = True  # figures will be made regardless of this option.
    show_corner = True  # figures will be made regardless of this option.
    minabserr = 0.1  # minimum absolute errorbar in the unit of bmaj or dv.
    minrelerr = 0.01  # minimum relative errorbar.
    calc_evidence = False # If calculate Bayesian evidence or not.
    quadrant = '13'

    impv = PVAnalysis(fitsfile, rms, vsys, dist, incl=incl, pa=None)
    impv.get_edgeridge(f'{outname}', thr=thr, ridgemode=ridgemode,
                    use_position=use_position, use_velocity=use_velocity,
                    Mlim=Mlim, xlim=np.array(xlim) / dist, vlim=vlim,
                    minabserr=minabserr, minrelerr=minrelerr,quadrant=quadrant,
                    nanbeforemax=True, nanopposite=True, nanbeforecross=True)
    impv.write_edgeridge(outname=f'{outname}')
    impv.fit_edgeridge(include_vsys=include_vsys,
                    include_dp=include_dp,
                    include_pin=include_pin,
                    fixed_pin=fixed_pin, fixed_dp=fixed_dp,
                    outname=f'{outname}', rangelevel=0.8,
                    show_corner=show_corner,
                    calc_evidence=calc_evidence)
    impv.output_fitresult()
    impv.plot_fitresult(vlim=vlim_plot, xlim=xlim_plot, flipaxis=False,
                        clevels=[-9,-6,-3,3,6,9], outname=f'{outname}',
                        show=show_pv, logcolor=True, Tbcolor=False,
                        kwargs_pcolormesh={'cmap':'viridis'},
                        kwargs_contour={'colors':'lime'},
                        fmt={'edge':'v', 'ridge':'o'},
                        linestyle={'edge':'--', 'ridge':'-'},
                        plotridgepoint=True, plotedgepoint=True,
                        plotridgemodel=True, plotedgemodel=True)

if __name__ == '__main__':
    # Set config sections
    section_src, section_pv = SECTIONS[MOLECULE]

    # Load molecule information
    molecule = Molecule.from_json(SAVED_MOLS[MOLECULE])
    restfreq = molecule.transition_info(TRANSITION).restfreq

    for src, hmcs in SOURCES.items():
        for hmc in hmcs:
            fitsfile = RESULTS / f'{src}/c5c8/per_hot_core/{hmc}_pvmaps'
            fitsfile = fitsfile / 'G335.579-0.272_hmc2_rotation.CH3OH_spw0.ra247.74430_dec-48.73089.PA202.fits'
            outdir = RESULTS / f'{src}/c5c8/per_hot_core/{hmc}_slam'
            outdir.mkdir(exist_ok=True)
            run_slam(fitsfile, outdir)
