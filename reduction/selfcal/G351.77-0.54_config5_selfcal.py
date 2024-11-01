field = 'G351.77-0.54'
flagchannels = "0:0~10;13~27;42~93;100~144;171~217;229~253;312~326;350~409;475~496;500~519;543~562;681~702;779~805;827~849;1154~1187;1265~1306;1469~1492;1539~1562;1629~1657;1745~1792;1992~2009;2112~2127;2295~2311;2327~2342;2766~2788;3050~3065;3240~3274;3483~3508;3830~3839,1:0~22;76~97;166~189;318~338;348~371;446~465;494~534;900~910;1487~1510;1606~1646;1655~1678;1811~1849;1879~1926;2078~2092;2177~2208;2243~2274;2316~2337;2362~2381;2388~2418;2456~2498;2775~2795;3010~3026;3521~3568;3830~3839,2:0~38;76~151;223~262;279~348;408~454;505~615;621~726;789~874;885~898;914~933;972~987;1023~1078;1086~1104;1125~1154;1232~1247;1397~1417;1431~1468;1588~1629;1673~1689;1724~1744;1841~1853;1870~1891;2225~2245;2380~2403;2517~2544;2655~2711;2718~2753;2927~2947;2983~3003;3043~3083;3332~3364;3609~3630;3653~3699;3830~3839,3:0~10;377~433;450~490;510~537;548~570;587~622;674~731;750~775;796~819;928~947;1065~1090;1100~1124;1624~1637;1744~1777;2014~2049;2095~2106;2314~2341;2428~2472;2499~2525;2566~2591;2604~2628;2835~2845;2890~2905;2915~2956;3059~3072;3110~3125;3129~3153;3292~3306;3379~3393;3467~3490;3502~3517;3571~3626;3749~3767;3797~3810;3830~3839"
widths_avg = [120,120,120,120]
imsize = [960, 960]
cell = '0.06arcsec'
refant = 'DV07'

vis_cont = '../final_uvdata/%s.config5.ms' % field
vis_cont_avg = '../final_uvdata/%s.config5.cont_avg.ms' % field

flagmanager(vis=vis_cont, mode='save', versionname='before_cont_flags')
initweights(vis=vis_cont, wtmode='weight', dowtsp=True)
flagdata(vis=vis_cont, mode='manual', spw=flagchannels, flagbackup=False)
split2(vis=vis_cont, spw='0,1,2,3', outputvis=vis_cont_avg, width=widths_avg,
        datacolumn='data')
flagmanager(vis=vis_cont, mode='restore', versionname='before_cont_flags')

# Phase cal
# Step 0 --> dirty
threshold = '4mJy'
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
threshold = '9.2mJy'
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
    niter=10000,
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
        subplot=551,
        iteration="antenna",
        plotrange=[0,0,-60,60],
        markersize=3,
        fontsize=3.0,
        figfile="plots/%s.config5.1.phase.cal.%s.pdf" % (field, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 2
threshold = '3.2mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_phase_cal_1')
os.system('rm -rf selfcal/%s.config5.2.cont.*' % field)
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
    niter=10000,
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
        subplot=551,
        iteration="antenna",
        plotrange=[0,0,-60,60],
        markersize=3,
        fontsize=3.0,
        figfile="plots/%s.config5.2.phase.cal.%s.pdf" % (field, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 3
os.system('rm -rf selfcal/%s.config5.3.cont.*' % field)
threshold = '1.6mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_phase_cal_2')
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
    niter=10000,
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
        subplot=551,
        iteration="antenna",
        plotrange=[0,0,-60,60],
        markersize=3,
        fontsize=3.0,
        figfile="plots/%s.config5.3.phase.cal.%s.pdf" % (field, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 4
os.system('rm -rf selfcal/%s.config5.4.cont.*' % field)
threshold = '1.4mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_phase_cal_3')
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
    niter=10000,
    threshold=threshold) 

# Step 4 Amp cal
caltable='selfcal/%s.config5.4.amp.cal' % field
solint = '30s'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='G',
        refant=refant,
        calmode='ap',
        solint=solint,
        solnorm=True)
plotcal(caltable=caltable,
        xaxis="time",
        yaxis="amp",
        subplot=551,
        iteration="antenna",
        plotrange=[0,0,0,1.2],
        figfile="plots/%s.config5.4.phase.cal.%s.pdf" % (field, solint),
        markersize=3,
        fontsize=3.0,
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Final cleaning
threshold = '1.1mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_amp_cal')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s.config5.final.cont' % field,
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
    niter=1000,
    threshold=threshold) 
