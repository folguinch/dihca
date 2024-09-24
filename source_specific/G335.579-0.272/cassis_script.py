import glob
import os
import ScriptEnvironment
from Component import Component
from Range import Range
from LineAnalysisScripting import UserInputs
from cassisStats import writeStats
from FileReader import FileReader
from Plot import Plot

rms = 17. # K
tuning = [219.873, 233.935]
Range.unit = 'GHz'
range1 = Range(219.975, 219.990)
range2 = Range(219.987, 220.000)
range3 = Range(232.835, 232.865)
range4 = Range(232.852, 232.858)
range5 = Range(233.914, 233.920)
eup_range = [100, 1500]

use = 'lte'
geom = 'slab'
telescope = 'alma_c8'
#suff = '.lis' % (ncomp, use, geom)

source_name = 'G335ALMA1'
species_name = 'CH3OH'
#moltag = 32003
moltag = 32504

basedir = '/home/myso/share/binary_project/G333_G335/G335.579-0.272/'
datadir = basedir + 'results_final/concat/CH3OH/spectra/'
savedir = datadir + '%s_fit/' % use

spectra = glob.glob(datadir + 'spec_x1[7-9][0-9][0-9]_y*.dat')

for i, spectrum in enumerate(spectra):
    fname = os.path.basename(spectrum)
    output_file = savedir + fname.replace('.dat','.log')
    if os.path.exists(output_file):
        lisfile = output_file.replace('.log','.lis')
        if not os.path.exists(lisfile):
            print('Results do not exist: ', lisfile)
            print('Removing log and re-running')
            os.remove(output_file)
        else:
            print('skipping: ', output_file)
            continue

    userInputs = UserInputs(
        inputFile=spectrum,
        telescope=telescope,
        tuningRange=tuning,
        moltags=[moltag],
        template='Full CDMS',
        tmb2ta=False,
        outputFile=output_file,
        warning=False,
        selectedLines={'2': range1, '3': range2}, #'4': range3, '5': range4, '6-7': range5},
        rmsLines={'2-3': rms},
        calLines={'2-3': 0.1}, #'4-7': 0.2},
        eup=eup_range,
        continuum = 'continuum-0',
        plotTitle='CH3OH'
    )

    # =============================================================================
    ## MODEL INPUTS
    # =============================================================================
    # Type of models :
    # LTE  : nmol, tex, fwhm, size, vlsr and iso if there are different moltags
    # RADEX: nmol, collisionFile, n_collisioners, tkin, fwhm, size, vlsr and iso
    # =============================================================================

    # Parameters for the first component
    # -----------------------------------
    comp_1 = Component(
        # Needed for any model
        nmol = {'min':1.0e14, 'max':1.0e22, 'nstep':1, 'log_mode':True},
        temp = {'min':30.0, 'max':1000.0, 'nstep':1, 'log_mode':False},
        fwhm = {'min':0.2, 'max':7.0, 'nstep':1, 'log_mode':False},
        size = {'min':1, 'max':1, 'nstep':1, 'log_mode':False},
        vlsr = {'min':-5, 'max':5, 'nstep':1, 'log_mode':False},
        #iso = {'min':100,    'max':100,    'nstep':1,'log_mode':False},
        interacting = True,
        #reducePhysicalParam = {"nmol": 2.0, "temp": 1.5, "fwhm":1.5, "size": 2.0,
        #    "vslr": 1.5},
        #reducePhysicalParam = {"nmol": 6,    "temp": 6,    "fwhm": 6,  "size": 6, 
        #                      "vlsr": 6, "n_H2":6},
        model = use,
        # only needed for RADEX 
        #collisioner = ["H2"],
        #n_H2 = {'min':1.0e8,  'max':1.0e13,  'nstep':1, 'log_mode':True},
        #collisionFile = ["ch3oh.dat"],
        #geometry = geom,
    )


    # =============================================================================
    # COMPUTATION OF THE  MINIMAL CHI2
    # =============================================================================

    # Initialization of the parameters for MCMC 
    drawNumber = 1000
    cutOff = 100
    ratioAtCutOff = 0.1

    # Initialization of the physical parameters (optional)
    # Empty dictionary means random initial parameter
    # Set the initial parameters by specifying the keys and and the values
    params_1 = {"nmol":1E17, "temp":200, "fwhm":2., "size":1, "vlsr":0.0}
    userInputs.initComponentsForMCMC([comp_1, params_1])

    # Computation of the minimum chi2
    userInputs.computeChi2MinUsingMCMC(drawNumber, cutOff, ratioAtCutOff)


    # =============================================================================
    # ANALYSIS OF THE RESULTS
    # =============================================================================

    # A. Plot the best model
    userInputs.plotBestModel(moltag=moltag, overSampling=3, tuningBand=60)

    # B. Compute and write the statistics of the parameters
    # (for more details, print the documentation with 'print writeStats.__doc__')
    writeStats(userInputs, sigmaClip = 3, 
               outputFile=output_file.replace('.log','.txt'))
    userInputs.saveBestPhysicalModels(output_file.replace('.log','.lis'),
                                      overSampling=3)

