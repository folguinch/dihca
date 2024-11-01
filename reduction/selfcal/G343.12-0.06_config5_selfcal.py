
# At 211GHz max width per binned channel is 58-60MHz. Observed channel
# size=488.281kHz. 
#=> 60/488~=120 so 120*488.281<58MHz. The averaged continuum wil
#l have 3840/120=32 bins.
#see: https://casaguides.nrao.edu/index.php/Image_Continuum


field = 'G343.12-0.06'
flagchannels = "0:0~17;29~39;107~131;333~344;376~417;419~440;526~539;727~749;1172~1183;1314~1350;1586~1607;1796~1829;2341~2358;2376~2387;3290~3326;3830~3839,1:0~10;30~68;183~194;216~233;309~319;322~335;355~418;423~435;470~513;549~574;593~609;665~689;853~869;913~925;949~975;1075~1090;1140~1151;1431~1443;1451~1468;1492~1503;1538~1553;1649~1687;1698~1731;1751~1783;1861~1891;1903~1966;2022~2034;2039~2053;2060~2071;2123~2141;2166~2177;2190~2211;2226~2241;2297~2321;2360~2386;2409~2429;2433~2465;2506~2548;2592~2606;2686~2699;2816~2848;2976~2987;3191~3206;3350~3378;3514~3530;3570~3605;3776~3787;3830~3839,2:0~10;44~79;189~211;244~295;471~569;585~606;622~667;750~818;985~1016;1078~1094;1404~1417;1682~1699;1795~1820;2578~2589;2638~2664;2680~2706;2885~2902;3004~3037;3283~3312;3567~3585;3610~3649;3830~3839,3:0~10;322~389;400~448;461~493;509~519;541~576;589~610;627~689;708~730;751~777;881~904;1020~1082;1493~1544;1546~1560;1597~1615;1698~1737;1781~1798;1952~1994;2046~2064;2078~2089;2115~2126;2261~2298;2384~2429;2434~2447;2455~2484;2521~2550;2557~2591;2675~2688;2760~2778;2784~2815;2851~2865;2898~2916;2937~2950;2952~2975;3004~3031;3067~3085;3089~3113;3177~3204;3338~3368;3544~3582;3830~3839"
widths_avg = [120,120,120,120]
imsize = [960,960]
cell = '0.06arcsec'
refant = 'DV07'

vis_cont = '%s.config5.ms' % field
vis_cont_avg = '%s.config5.cont_avg.ms' % field

flagmanager(vis=vis_cont, mode='save', versionname='before_cont_flags')
initweights(vis=vis_cont, wtmode='weight', dowtsp=True)
flagdata(vis=vis_cont, mode='manual', spw=flagchannels, flagbackup=False)
split2(vis=vis_cont, spw='0,1,2,3', outputvis=vis_cont_avg, width=widths_avg,
        datacolumn='data')
flagmanager(vis=vis_cont, mode='restore', versionname='before_cont_flags')

# Phase cal
# Step 0 --> dirty image
threshold = '2.6mJy'
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s.config5.0.cont' % field,
    imsize = imsize,
    spw='0,1,2,3',
    cell = cell,
    specmode='mfs', 
    outframe='LSRK', 
    gridder='standard', 
    deconvolver='hogbom', 
    #scales=[0,5,15],
    #uvtaper = ['1.15arcsec','0.95arcsec'],
    interactive = False,
    weighting='briggs', 
    robust=0.5, 
    #savemodel='modelcolumn',
    niter=0,
    threshold=threshold) 


# Step 1
threshold = '2.6mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_phase_cal_0')
os.system('rm -rf selfcal/%s.config5.1.cont.*' % field)
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s.config5.1.cont' % field,
    imsize = imsize,
    spw='0,1,2,3',
    cell = cell,
    specmode='mfs', 
    outframe='LSRK', 
    gridder='standard', 
    deconvolver='hogbom', 
    #scales=[0,5,15],
    #uvtaper = ['1.15arcsec','0.95arcsec'],
    interactive = True,
    weighting='briggs', 
    robust=0.5, 
    savemodel='modelcolumn',
    niter=4000,
    threshold=threshold) 
caltable='selfcal/%s.config5.1.phase.cal' % field
solint = '30s'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='G',
        refant=refant,
        calmode='p',
        solint=solint)
plotcal(caltable=caltable,
        xaxis="time",
        yaxis="phase",
        subplot=331,
        iteration="antenna",
        plotrange=[0,0,-60,60],
        #markersize=3,
        #fontsize=3.0,
        figfile="plots/%s.config5.1.phase.cal.%s.pdf" % (field, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 2
os.system('rm -rf selfcal/%s.config5.2.cont.*' % field)
threshold = '0.64mJy'
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s.config5.2.cont' % field,
    imsize = imsize,
    spw='0,1,2,3',
    cell = cell,
    specmode='mfs', 
    outframe='LSRK', 
    gridder='standard', 
    deconvolver='hogbom', 
    #scales=[0,5,15],
    #uvtaper = ['1.15arcsec','0.95arcsec'],
    interactive = True,
    weighting='briggs', 
    robust=0.5, 
    savemodel='modelcolumn',
    niter=4000,
    threshold=threshold) 
caltable='selfcal/%s.config5.2.phase.cal' % field
solint = '20s'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='G',
        refant=refant,
        calmode='p',
        solint=solint)
plotcal(caltable=caltable,
        xaxis="time",
        yaxis="phase",
        subplot=331,
        iteration="antenna",
        plotrange=[0,0,-60,60],
        #markersize=3,
        #fontsize=3.0,
        figfile="plots/%s.config5.2.phase.cal.%s.pdf" % (field, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 3
os.system('rm -rf selfcal/%s.config5.3.cont.*' % field)
threshold = '0.48mJy'
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s.config5.3.cont' % field,
    imsize = imsize,
    spw='0,1,2,3',
    cell = cell,
    specmode='mfs', 
    outframe='LSRK', 
    gridder='standard', 
    deconvolver='hogbom', 
    #scales=[0,5,15],
    #uvtaper = ['1.15arcsec','0.95arcsec'],
    interactive = True,
    weighting='briggs', 
    robust=0.5, 
    savemodel='modelcolumn',
    niter=4000,
    threshold=threshold) 

caltable='selfcal/%s.config5.3.phase.cal' % field
solint = '10s'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='G',
        refant=refant,
        calmode='p',
        solint=solint)
plotcal(caltable=caltable,
        xaxis="time",
        yaxis="phase",
        subplot=331,
        iteration="antenna",
        plotrange=[0,0,-60,60],
        #markersize=3,
        #fontsize=3.0,
        figfile="plots/%s.config5.3.phase.cal.%s.pdf" % (field, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")





# Amp cal ---> no aplicar, empeoro el rms y se perdio flujo.
os.system('rm -rf selfcal/%s.config5.4.cont.*' % field)
threshold = '0.38mJy'
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s.config5.4.cont' % field,
    imsize = imsize,
    spw='0,1,2,3',
    cell = cell,
    specmode='mfs', 
    outframe='LSRK', 
    gridder='standard', 
    deconvolver='hogbom', 
    #scales=[0,5,15],
    #uvtaper = ['1.15arcsec','0.95arcsec'],
    interactive = True,
    weighting='briggs', 
    robust=0.5, 
    savemodel='modelcolumn',
    niter=4000,
    threshold=threshold) 



caltable='selfcal/%s.config5.5.amp.cal' % field
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='G',
        refant=refant,
        calmode='ap',
        solint='30s',
        solnorm=True)
plotcal(caltable=caltable,
        xaxis="time",
        yaxis="amp",
        subplot=331,
        iteration="antenna",
        plotrange=[0,0,0,1.2],
        #markersize=3,
        #fontsize=3.0,
        figfile="plots/%s.config5.5.amp.cal.%s.pdf" % (field, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

threshold = '0.34mJy'
tclean(vis = vis_cont_avg,
    field = field,
    imagename =  'selfcal/%s.config5.5.cont' % field,
    imsize = imsize,
    spw='0,1,2,3',
    cell = cell,
    specmode='mfs', 
    outframe='LSRK', 
    gridder='standard', 
    deconvolver='hogbom', 
    #scales=[0,5,15],
    #uvtaper = ['1.15arcsec','0.95arcsec'],
    interactive = True,
    weighting='briggs', 
    robust=0.5, 
    savemodel='modelcolumn',
    niter=4000,
    threshold=threshold) 
