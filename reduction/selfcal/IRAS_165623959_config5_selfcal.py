field = 'IRAS_165623959'
flagchannels = "0:0~10;60~70;84~101;158~168;345~355;369~386;395~405;623~633;676~686;700~721;730~743;1274~1320;1465~1477;1557~1577;1759~1800;2006~2017;2241~2251;2869~2879;2975~2985;3095~3105;3252~3295;3830~3839,1:0~31;129~139;350~361;366~376;379~389;509~519;546~556;1550~1561;1574~1836;1877~1900;2495~2510;3830~3839,2:0~10;507~517;578~595;809~835;1019~1038;3322~3332;3830~3839,3:0~10;352~413;429~458;491~517;572~595;665~711;789~800;1064~1108;1980~2032;2296~2322;2433~2445;2790~2811;3207~3235;3368~3392;3830~3839"
widths_avg = [120,120,120,120]
imsize = [1920, 1920]
cell = '0.03arcsec'

##################### EB1 #########################
refant = 'DA49'

vis_cont = 'uvdata/%s.1.config5.ms' % field
vis_cont_avg = 'uvdata/%s.1.config5.cont_avg.ms' % field

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
    imagename = 'selfcal/%s.1.config5.0.cont' % field,
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
os.system('rm -rf selfcal/%s.1.config5.1.cont.*' % field)
threshold = '1.5mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_1')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s.1.config5.1.cont' % field,
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
caltable='selfcal/%s.1.config5.1.phase.cal' % field
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
        figfile="plots/%s.1.config5.1.phase.cal.%s.pdf" % (field, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 2
os.system('rm -rf selfcal/%s.1.config5.2.cont.*' % field)
threshold = '0.6mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_2')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s.1.config5.2.cont' % field,
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
caltable='selfcal/%s.1.config5.2.phase.cal' % field
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
        figfile="plots/%s.1.config5.2.phase.cal.%s.pdf" % (field, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 3
os.system('rm -rf selfcal/%s.1.config5.3.cont.*' % field)
threshold = '0.4mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_3')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s.1.config5.3.cont' % field,
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
caltable='selfcal/%s.1.config5.3.phase.cal' % field
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
        figfile="plots/%s.1.config5.3.phase.cal.%s.pdf" % (field, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 4
os.system('rm -rf selfcal/%s.1.config5.4.cont.*' % field)
threshold = '0.4mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_amp_cal_1')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s.1.config5.4.cont' % field,
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
caltable='selfcal/%s.1.config5.4.amp.cal' % field
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
        figfile="plots/%s.1.config5.4.phase.cal.%s.pdf" % (field, solint),
        markersize=3,
        fontsize=3.0,
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Final cleaning
threshold = '0.4mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_amp_cal')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s.1.config5.final.cont' % field,
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
    #savemodel='modelcolumn',
    niter=1000,
    threshold=threshold) 

##################### EB2 #########################
refant = 'DA53'

vis_cont = 'uvdata/%s.2.config5.ms' % field
vis_cont_avg = 'uvdata/%s.2.config5.cont_avg.ms' % field

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
    imagename = 'selfcal/%s.2.config5.0.cont' % field,
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
os.system('rm -rf selfcal/%s.2.config5.1.cont.*' % field)
threshold = '1.3mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_1')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s.2.config5.1.cont' % field,
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
caltable='selfcal/%s.2.config5.1.phase.cal' % field
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
        figfile="plots/%s.2.config5.1.phase.cal.%s.pdf" % (field, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 2
os.system('rm -rf selfcal/%s.2.config5.2.cont.*' % field)
threshold = '0.8mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_2')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s.2.config5.2.cont' % field,
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
caltable='selfcal/%s.2.config5.2.phase.cal' % field
solint = '15s'
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
        figfile="plots/%s.2.config5.2.phase.cal.%s.pdf" % (field, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 3
os.system('rm -rf selfcal/%s.2.config5.3.cont.*' % field)
threshold = '0.3mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_3')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s.2.config5.3.cont' % field,
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
caltable='selfcal/%s.2.config5.3.phase.cal' % field
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
        figfile="plots/%s.2.config5.3.phase.cal.%s.pdf" % (field, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 4
os.system('rm -rf selfcal/%s.2.config5.4.cont.*' % field)
threshold = '0.3mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_amp_cal_1')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s.2.config5.4.cont' % field,
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
caltable='selfcal/%s.2.config5.4.amp.cal' % field
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
        figfile="plots/%s.2.config5.4.phase.cal.%s.pdf" % (field, solint),
        markersize=3,
        fontsize=3.0,
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Final cleaning
threshold = '0.3mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_amp_cal')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s.2.config5.final.cont' % field,
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
    #savemodel='modelcolumn',
    niter=1000,
    threshold=threshold) 
