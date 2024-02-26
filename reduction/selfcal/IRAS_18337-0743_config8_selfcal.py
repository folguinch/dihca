field = 'IRAS_18337-0743'
flagchannels = "0:0~10;3830~3839,1:0~10;3830~3839,2:0~10;3830~3839,3:0~10;3830~3839"
widths_avg = [120,120,120,120]
imsize = [5600, 5600]
cell = '0.01arcsec'

# EB dependent vars
eb = '' # for eb 1: eb='.1'
refant = 'DV17'
config = 8

vis_cont = 'uvdata/%s%s.config%i.ms' % (field, eb, config)
vis_cont_avg = 'uvdata/%s%s.config%i.cont_avg.ms' % (field, eb, config)

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
    imagename = 'selfcal/%s%s.config%i.0.cont' % (field, eb, config),
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
os.system('rm -rf selfcal/%s%s.config%i.1.cont.*' % (field, eb, config))
threshold = '0.4mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_1')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config%i.1.cont' % (field, eb, config),
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
caltable='selfcal/%s%s.config%i.1.phase.cal' % (field, eb, config)
solint = 'inf'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='G',
        refant=refant,
        calmode='p',
        combine='spw',
        solint=solint)
plotcal(caltable=caltable,
        xaxis="time",
        yaxis="phase",
        subplot=551,
        iteration="antenna",
        plotrange=[0,0,-60,60],
        markersize=3,
        fontsize=3.0,
        figfile="plots/%s%s.config%i.1.phase.cal.%s.pdf" % (field, eb, config, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
         gaintable=[caltable],
         applymode='calonly',
         spwmap=[0,0,0,0],
         interp="linear")

# Step 2
os.system('rm -rf selfcal/%s%s.config%i.2.cont.*' % (field, eb, config))
threshold = '0.3mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_2')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config%i.2.cont' % (field, eb, config),
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
caltable='selfcal/%s%s.config%i.2.phase.cal' % (field, eb, config)
solint = '40s'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='G',
        refant=refant,
        calmode='p',
        combine='spw',
        solint=solint)
plotcal(caltable=caltable,
        xaxis="time",
        yaxis="phase",
        subplot=551,
        iteration="antenna",
        plotrange=[0,0,-60,60],
        markersize=3,
        fontsize=3.0,
        figfile="plots/%s%s.config%i.2.phase.cal.%s.pdf" % (field, eb, config, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
         gaintable=[caltable],
         applymode='calonly',
         spwmap=[0,0,0,0],
         interp="linear")

# Step 3
os.system('rm -rf selfcal/%s%s.config%i.3.cont.*' % (field, eb, config))
threshold = '0.15mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_3')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config%i.3.cont' % (field, eb, config),
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
#caltable='selfcal/%s%s.config%i.3.phase.cal' % (field, eb, config)
#solint = '20s'
#rmtables(caltable)
#gaincal(vis=vis_cont_avg,
#        caltable=caltable,
#        field=field,
#        gaintype='G',
#        refant=refant,
#        calmode='p',
#        solint=solint)
#plotcal(caltable=caltable,
#        xaxis="time",
#        yaxis="phase",
#        subplot=551,
#        iteration="antenna",
#        plotrange=[0,0,-60,60],
#        markersize=3,
#        fontsize=3.0,
#        figfile="plots/%s%s.config%i.3.phase.cal.%s.pdf" % (field, eb, config, solint),
#        showgui=True)
#applycal(vis=vis_cont_avg,
#        gaintable=[caltable],
#        applymode='calonly',
#        interp="linear")
#
## Step 4
#os.system('rm -rf selfcal/%s%s.config%i.4.cont.*' % (field, eb, config))
#threshold = '0.1mJy'
#flagmanager(vis=vis_cont_avg, mode='save', versionname='before_amp_cal_1')
#tclean(vis = vis_cont_avg,
#    field = field,
#    imagename = 'selfcal/%s%s.config%i.4.cont' % (field, eb, config),
#    imsize = imsize,
#    spw='0,1,2,3',
#    cell = cell,
#    specmode='mfs', 
#    outframe='LSRK', 
#    gridder='standard', 
#    deconvolver='hogbom', 
#    #scales=[0,5,15],
#    #uvtaper = ['1.15arcsec','0.95arcsec'],
#    interactive = True,
#    weighting='briggs', 
#    robust=0.5, 
#    savemodel='modelcolumn',
#    niter=10000,
#    threshold=threshold) 
#
# Step 4 Amp cal
caltable='selfcal/%s%s.config%i.4.amp.cal' % (field, eb, config)
solint = '30s'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='G',
        refant=refant,
        calmode='ap',
        solint=solint,
        combine='spw',
        solnorm=True)
plotcal(caltable=caltable,
        xaxis="time",
        yaxis="amp",
        subplot=551,
        iteration="antenna",
        plotrange=[0,0,0,1.2],
        figfile="plots/%s%s.config%i.4.phase.cal.%s.pdf" % (field, eb, config, solint),
        markersize=3,
        fontsize=3.0,
        showgui=True)
applycal(vis=vis_cont_avg,
         gaintable=[caltable],
         applymode='calonly',
         spwmap=[0,0,0,0],
         interp="linear")

# Final cleaning
os.system('rm -rf selfcal/%s%s.config%i.final.cont.*' % (field, eb, config))
threshold = '0.1mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_amp_cal')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config%i.final.cont' % (field, eb, config),
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
    niter=10000,
    threshold=threshold) 
