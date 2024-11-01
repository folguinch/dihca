field = 'W33A'
flagchannels = "0:0~23;117~138;278~336;405~428;609~638;850~864;1203~1235;1467~1496;1687~1715;2221~2249;2255~2274;2982~2992;3179~3211;3830~3839,1:0~10;250~284;372~402;437~462;837~853;1337~1348;1539~1574;1587~1619;1752~1777;1787~1800;1823~1853;2007~2021;2185~2201;2247~2270;2295~2309;2322~2350;2405~2437;2702~2734;3452~3491;3782~3813;3819~3839,2:0~24;153~177;297~313;352~377;379~400;580~679;692~706;729~776;882~917;1100~1126;1785~1811;2295~2306;2746~2763;2788~2806;2988~3014;3109~3140;3390~3408;3675~3695;3712~3751;3830~3839,3:0~10;426~496;503~542;565~600;610~632;644~687;698~714;734~794;814~836;855~886;986~1014;1124~1188;1581~1595;1605~1623;1625~1644;1799~1838;2061~2097;2152~2175;2365~2405;2488~2536;2559~2587;2626~2654;2661~2693;2890~2917;2977~3001;3191~3215;3287~3307;3449~3466;3649~3684;3830~3839"
widths_avg = [120,120,120,120]
imsize = [1024, 1024]
cell = '0.05arcsec'
refant = 'DA59'

vis_cont = 'uvdata/W33A.config5.ms'
vis_cont_avg = 'uvdata/W33A.config5.cont_avg.ms'

flagmanager(vis=vis_cont, mode='save', versionname='before_cont_flags')
initweights(vis=vis_cont, wtmode='weight', dowtsp=True)
flagdata(vis=vis_cont, mode='manual', spw=flagchannels, flagbackup=False)
split2(vis=vis_cont, spw='0,1,2,3', outputvis=vis_cont_avg, width=widths_avg,
        datacolumn='data')
flagmanager(vis=vis_cont, mode='restore', versionname='before_cont_flags')

# Phase cal
# Step 0
threshold = '4mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_selfcal', merge='replace')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/W33A.config5.0.cont',
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
caltable='selfcal/W33A.config5.0.phase.cal'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='G',
        refant=refant,
        calmode='p',
        solint='30s')
plotcal(caltable=caltable,
        xaxis="time",
        yaxis="phase",
        subplot=551,
        iteration="antenna",
        plotrange=[0,0,-60,60],
        markersize=3,
        fontsize=3.0,
        figfile="plots/W33A.config5.0.phase.cal.30s.pdf",
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 1
threshold = '1mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_phase_cal_0')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/W33A.config5.1.cont',
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
caltable='selfcal/W33A.config5.1.phase.cal'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='G',
        refant=refant,
        calmode='p',
        solint='20s')
plotcal(caltable=caltable,
        xaxis="time",
        yaxis="phase",
        subplot=551,
        iteration="antenna",
        plotrange=[0,0,-60,60],
        markersize=3,
        fontsize=3.0,
        figfile="plots/W33A.config5.1.phase.cal.20s.pdf",
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 2
threshold = '0.8mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_phase_cal_1')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/W33A.config5.2.cont',
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
caltable='selfcal/W33A.config5.2.phase.cal'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='G',
        refant=refant,
        calmode='p',
        solint='15s')
plotcal(caltable=caltable,
        xaxis="time",
        yaxis="phase",
        subplot=551,
        iteration="antenna",
        plotrange=[0,0,-60,60],
        markersize=3,
        fontsize=3.0,
        figfile="plots/W33A.config5.2.phase.cal.15s.pdf",
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 3
threshold = '0.6mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_phase_cal_2')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/W33A.config5.3.cont',
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

# Amp cal
caltable='selfcal/W33A.config5.3.amp.cal'
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
        subplot=551,
        iteration="antenna",
        plotrange=[0,0,0,1.2],
        markersize=3,
        fontsize=3.0,
        figfile="plots/W33A.config5.3.amp.cal.30s.pdf",
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")
threshold = '0.6mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_phase_cal_3')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/W33A.config5.4.cont',
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
