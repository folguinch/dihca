field = 'G11.1-0.12'
flagchannels = '0:0~34;129~140;304~319;325~345;381~392;417~442;568~579;626~650;706~716;860~882;1078~1088;1483~1505;1522~1532;1700~1717;1843~1854;1879~1893;2203~2214;2233~2261;2265~2289;2402~2412;2946~2956;2986~3003;3198~3219;3830~3839,1:0~10;265~288;387~412;1837~1856;2716~2743;3466~3490;3797~3822;3830~3839,2:0~10;568~593;604~623;642~665;884~900;1087~1112;1776~1797;2977~3002;3106~3124;3665~3685;3701~3726;3830~3839,3:0~10;102~112;130~140;422~485;499~533;560~590;603~613;640~669;726~779;854~872;1131~1164;1599~1620;1791~1817;2054~2082;2146~2163;2363~2388;2497~2519;2652~2663;2675~2685;2857~2877;3830~3839'
widths_avg = [120,120,120,120]
imsize = [1024, 1024]
cell = '0.05arcsec'
refant = 'DA59'

vis_cont = 'uvdata/G11.1-0.12.config5.ms'
vis_cont_avg = 'uvdata/G11.1-0.12.config5.cont_avg.ms'

flagmanager(vis=vis_cont, mode='save', versionname='before_cont_flags')
initweights(vis=vis_cont, wtmode='weight', dowtsp=True)
flagdata(vis=vis_cont, mode='manual', spw=flagchannels, flagbackup=False)
split2(vis=vis_cont, spw='0,1,2,3', outputvis=vis_cont_avg, width=widths_avg,
        datacolumn='data')
flagmanager(vis=vis_cont, mode='restore', versionname='before_cont_flags')

# Dirty image
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/G11.1-0.12.config5.dirty.cont',
    imsize = imsize,
    spw='0,1,2,3',
    cell = cell,
    specmode='mfs', 
    outframe='LSRK', 
    gridder='standard', 
    deconvolver='multiscale', 
    scales=[0,5,15],
    #uvtaper = ['1.15arcsec','0.95arcsec'],
    interactive = False,
    weighting='briggs', 
    robust=0.5, 
    #savemodel='modelcolumn',
    niter=1,
    threshold='4mJy') 

# Phase cal
# Step 0
threshold = '4.0mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_selfcal', merge='replace')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/G11.1-0.12.config5.0.cont',
    imsize = imsize,
    spw='0,1,2,3',
    cell = cell,
    specmode='mfs', 
    outframe='LSRK', 
    gridder='standard', 
    deconvolver='multiscale', 
    scales=[0,5,15],
    #uvtaper = ['1.15arcsec','0.95arcsec'],
    interactive = True,
    weighting='briggs', 
    robust=0.5, 
    savemodel='modelcolumn',
    niter=100,
    threshold=threshold) 
caltable='selfcal/G11.1-0.12.config5.0.phase.cal'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        combine='scan,spw',
        caltable=caltable,
        field=field,
        gaintype='G',
        refant=refant,
        calmode='p',
        solint='960s')
plotcal(caltable=caltable,
        xaxis="time",
        yaxis="phase",
        subplot=551,
        iteration="antenna",
        plotrange=[0,0,-60,60],
        markersize=3,
        fontsize=3.0,
        figfile="plots/G11.1-0.12.config5.0.phase.cal.960s.pdf",
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear", 
        spwmap=[0,0,0,0])

# Step 1
threshold = '0.8mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_phase_cal_0')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/G11.1-0.12.config5.1.cont',
    imsize = imsize,
    spw='0,1,2,3',
    cell = cell,
    specmode='mfs', 
    outframe='LSRK', 
    gridder='standard', 
    deconvolver='multiscale', 
    scales=[0,5,15],
    #uvtaper = ['1.15arcsec','0.95arcsec'],
    interactive = True,
    weighting='briggs', 
    robust=0.5, 
    savemodel='modelcolumn',
    niter=100,
    threshold=threshold)
caltable='selfcal/G11.1-0.12.config5.1.phase.cal'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        combine='scan,spw',
        caltable=caltable,
        field=field,
        gaintype='G',
        refant=refant,
        calmode='p',
        solint='420s')
plotcal(caltable=caltable,
        xaxis="time",
        yaxis="phase",
        subplot=551,
        iteration="antenna",
        plotrange=[0,0,-60,60],
        markersize=3,
        fontsize=3.0,
        figfile="plots/G11.1-0.12.config5.1.phase.cal.420s.pdf",
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear", 
        spwmap=[0,0,0,0])

# Step 2
threshold = '0.5mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_phase_cal_1')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/G11.1-0.12.config5.2.cont',
    imsize = imsize,
    spw='0,1,2,3',
    cell = cell,
    specmode='mfs', 
    outframe='LSRK', 
    gridder='standard', 
    deconvolver='multiscale', 
    scales=[0,5,15],
    #uvtaper = ['1.15arcsec','0.95arcsec'],
    interactive = True,
    weighting='briggs', 
    robust=0.5, 
    savemodel='modelcolumn',
    niter=100,
    threshold=threshold)
#caltable='selfcal/G11.1-0.12.config5.2.phase.cal'
#rmtables(caltable)
#gaincal(vis=vis_cont_avg,
#        combine='scan,spw',
#        caltable=caltable,
#        field=field,
#        gaintype='G',
#        refant=refant,
#        calmode='p',
#        solint='60s')
#1 of 98 solutions flagged due to SNR < 3 in spw=0 at 2017/05/07/11:04:14.0

# Amp cal
caltable='selfcal/G11.1-0.12.config5.2.amp.cal'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        combine='scan,spw',
        caltable=caltable,
        field=field,
        gaintype='G',
        refant=refant,
        calmode='ap',
        solint='420s',
        solnorm=True)
plotcal(caltable=caltable,
        xaxis="time",
        yaxis="amp",
        subplot=551,
        iteration="antenna",
        plotrange=[0,0,0,1.2],
        markersize=3,
        fontsize=3.0,
        figfile="plots/G11.1-0.12.config5.2.amp.cal.420s.pdf",
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear",
        spwmap=[0,0,0,0])

# Step 3
threshold = '0.35mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_amp_cal_2')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/G11.1-0.12.config5.3.cont',
    imsize = imsize,
    spw='0,1,2,3',
    cell = cell,
    specmode='mfs', 
    outframe='LSRK', 
    gridder='standard', 
    deconvolver='multiscale', 
    scales=[0,5,15],
    #uvtaper = ['1.15arcsec','0.95arcsec'],
    interactive = True,
    weighting='briggs', 
    robust=0.5, 
    savemodel='modelcolumn',
    niter=100,
    threshold=threshold) 
