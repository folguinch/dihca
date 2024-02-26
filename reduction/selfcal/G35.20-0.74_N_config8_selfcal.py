field = 'G35.20-0.74_N'
flagchannels = '0:0~14;145~176;206~221;310~323;430~440;546~556;740~752;1115~1129;1131~1144;1910~1919,1:0~10;131~144;191~206;917~928;1209~1222;1355~1371;1730~1744;1895~1919,2:0~10;575~588;607~625;647~665;885~903;1094~1106;1779~1797;2281~2291;2983~3001;3108~3119;3663~3683;3705~3726;3830~3839,3:0~10;426~457;461~483;503~527;565~586;643~666;732~780;857~869;1132~1150;1571~1581;1619~1629;1796~1815;2062~2082;2369~2391;2493~2520;2661~2672;3654~3664;3830~3839,4:0~14;145~176;206~221;310~323;430~440;546~556;740~752;1115~1129;1131~1144;1910~1919,5:0~10;131~144;191~206;917~928;1209~1222;1355~1371;1730~1744;1895~1919,6:0~10;285~295;299~314;320~335;438~453;485~495;544~554;886~901;1137~1149;1488~1503;1550~1562;1828~1844;1849~1865;1910~1919,7:0~10;426~457;461~483;503~527;565~586;643~666;732~780;857~869;1132~1150;1571~1581;1619~1629;1796~1815;2062~2082;2369~2391;2493~2520;2661~2672;3654~3664;3830~3839'
widths_avg = [60,60,120,120,60,60,60,120]
imsize = [5600, 5600]
cell = '0.01arcsec'
spw = '0,1,2,3,4,5,6,7'

# EB dependent vars
eb = '' # for eb 1: eb='.1'
refant = 'DA56'
config = 8

vis_cont = 'uvdata/%s%s.config%i.concat.ms' % (field, eb, config)
vis_cont_avg = 'uvdata/%s%s.config%i.cont_avg.ms' % (field, eb, config)

flagmanager(vis=vis_cont, mode='save', versionname='before_cont_flags')
initweights(vis=vis_cont, wtmode='weight', dowtsp=True)
flagdata(vis=vis_cont, mode='manual', spw=flagchannels, flagbackup=False)
split2(vis=vis_cont, spw=spw, outputvis=vis_cont_avg, width=widths_avg,
        datacolumn='data')
flagmanager(vis=vis_cont, mode='restore', versionname='before_cont_flags')

# Phase cal
# Step 0 --> dirty
threshold = '4mJy'
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config%i.0.cont' % (field, eb, config),
    imsize = imsize,
    spw=spw,
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
threshold = '0.8mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_1')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config%i.1.cont' % (field, eb, config),
    imsize = imsize,
    spw=spw,
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
        interp="linear")

# Step 2
os.system('rm -rf selfcal/%s%s.config%i.2.cont.*' % (field, eb, config))
threshold = '0.45mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_2')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config%i.2.cont' % (field, eb, config),
    imsize = imsize,
    spw=spw,
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
        figfile="plots/%s%s.config%i.2.phase.cal.%s.pdf" % (field, eb, config, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        applymode='calonly',
        interp="linear")

# Step 3
os.system('rm -rf selfcal/%s%s.config%i.3.cont.*' % (field, eb, config))
threshold = '0.25mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_3')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config%i.3.cont' % (field, eb, config),
    imsize = imsize,
    spw=spw,
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
caltable='selfcal/%s%s.config%i.3.phase.cal' % (field, eb, config)
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
        figfile="plots/%s%s.config%i.3.phase.cal.%s.pdf" % (field, eb, config, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        applymode='calonly',
        interp="linear")

# Step 4
os.system('rm -rf selfcal/%s%s.config%i.4.cont.*' % (field, eb, config))
threshold = '0.1mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_amp_cal_1')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config%i.4.cont' % (field, eb, config),
    imsize = imsize,
    spw=spw,
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
        interp="linear")

# Final cleaning
os.system('rm -rf selfcal/%s%s.config%i.final.cont.*' % (field, eb, config))
threshold = '0.1mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_amp_cal')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config%i.final.cont' % (field, eb, config),
    imsize = imsize,
    spw=spw,
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
