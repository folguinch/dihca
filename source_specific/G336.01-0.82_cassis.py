"""For details see hand notes."""
import glob
import os
import ScriptEnvironment
from Component import Component
from Range import Range
from LineAnalysisScripting import UserInputs
from cassisStats import writeStats
from FileReader import FileReader
from Plot import Plot
from java.io import File

rms = 16. # K
tuning = [216.91, 234.85]
Range.unit = 'GHz'
range1 = Range(216.940, 216.9495)
range2 = Range(218.435, 218.445)
range3 = Range(220.073, 220.083)
range4 = Range(233.793, 233.799)
range5 = Range(234.678, 234.688)
range6 = Range(234.692, 234.702)
eup_range = [0, 500]
#tuningBand = 40

use = 'lte'
geom = 'slab'
telescope = 'alma_c8_g336'
#suff = '.lis' % (ncomp, use, geom)

species_name = 'CH3OH'
#moltag = 32003
moltag = 32504

basedir = '/data/share/binary_project/results/G336.01-0.82/CH3OH'
datadir = basedir + '/spectra'
savedir = datadir + '_%s_fit/' % use

spectra = glob.glob(datadir + '/spec_*.dat')
#spectra = [datadir + '/spec_x2589_y2599.dat']

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
        template='All Species',
        tmb2ta=False,
        outputFile=output_file,
        warning=False,
        selectedLines={'1': range1, '2': range2, '3': range3, 
                       '4': range4, '5': range5, '6': range6},
        rmsLines={'1-6': rms},
        calLines={'1-6': 0.1},
        #selectedLines={'2': range2, '3': range3},
        #rmsLines={'2-3': rms},
        #calLines={'2-3': 0.3},
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
        # See notes for size calculation
        nmol = {'min':1.0e10, 'max':1.0e22, 'nstep':1, 'log_mode':True},
        temp = {'min':30.0, 'max':2000.0, 'nstep':1, 'log_mode':False},
        fwhm = {'min':0.2, 'max':7.0, 'nstep':1, 'log_mode':False},
        size = {'min':0.4, 'max':0.4, 'nstep':1, 'log_mode':False}, 
        vlsr = {'min':-8, 'max':8, 'nstep':1, 'log_mode':False},
        #iso = {'min':1,    'max':1, 'nstep':1,'log_mode':False},
        interacting = True,
        #reducePhysicalParam = {"temp": 8, "vslr": 8, "fwhm": 8, "nmol": 8, "size": 8, 'iso': 1},
        #reducePhysicalParam = {"nmol": 6,    "temp": 6,    "fwhm": 6,  "size": 6, 
        #                      "vlsr": 6, "n_H2":6},
        model = use,
    )
    #comp_2 = Component(
    #    # Needed for any model
    #    # See notes for size calculation
    #    nmol = {'min':6.6e18, 'max':6.65e18, 'nstep':1, 'log_mode':True},
    #    temp = {'min':89.5, 'max':89.5, 'nstep':1, 'log_mode':False},
    #    fwhm = {'min':3.32, 'max':3.32, 'nstep':1, 'log_mode':False},
    #    size = {'min':1, 'max':1, 'nstep':1, 'log_mode':False}, 
    #    vlsr = {'min':3.5, 'max':3.5, 'nstep':1, 'log_mode':False},
    #    #iso = {'min':100,    'max':100,    'nstep':1,'log_mode':False},
    #    interacting = True,
    #    #reducePhysicalParam = {"nmol": 8, "temp": 8, "fwhm": 8, "size": 8, "vslr": 8},
    #    model = use,
    #)

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
    #params_1 = {"nmol":1E18, "temp":200, "fwhm":2., "size":0.4, "vlsr":0}
    #params_1 = {"nmol":5E18, "temp":70, "fwhm":2., "size":0.4, "vlsr":0}
    #params_1 = {"nmol":5E18, "temp":80, "fwhm":2., "size":0.4, "vlsr":0}
    # Specific
    params_1 = {"nmol":1E18, "temp":70, "fwhm":2., "size":0.4, "vlsr":0}
    #params_2 = {"nmol":6.62e18, "temp":89.5, "fwhm":3.32, "size":1, "vlsr":3.5}
    userInputs.initComponentsForMCMC([comp_1, params_1])
    #userInputs.initComponentsForMCMC([comp_1, params_1],[comp_2, params_2])

    # Computation of the minimum chi2
    userInputs.computeChi2MinUsingMCMC(drawNumber, cutOff, ratioAtCutOff)


    # =============================================================================
    # ANALYSIS OF THE RESULTS
    # =============================================================================

    # A. Plot the best model and save the corresponding spectra and config files
    lineModel = userInputs.plotBestModel(moltag=moltag, overSampling=3, telescope=telescope)
    lineModel.saveConfig(File(output_file.replace('.log','.lam')))
    bestPhysicalModels = userInputs.getBestPhysicalModels()
    userInputs.saveBestPhysicalModels(output_file.replace('.log','.lis'),
                                      overSampling=3)
    #userInputs.plotBestModel(moltag=moltag, overSampling=3, tuningBand=60)

    # B. Compute and write the statistics of the parameters
    writeStats(userInputs, sigmaClip = 3, 
               outputFile=output_file.replace('.log','.txt'))
    break
