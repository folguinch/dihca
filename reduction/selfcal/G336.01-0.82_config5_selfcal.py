field = 'G336.01-0.82'
flagchannels = "0:0~18;125~162;249~276;410~476;509~523;537~566;667~680;744~772;982~1006;1195~1209;1221~1234;1346~1366;1603~1630;1827~1850;1963~1974;1993~2023;2354~2384;2387~2413;3075~3087;3109~3133;3162~3177;3318~3347;3830~3839,1:0~10;55~85;382~415;504~536;571~593;974~985;1087~1104;1452~1463;1663~1706;1728~1745;1956~1985;2146~2159;2385~2402;2458~2482;2538~2568;2834~2869;3214~3225;3584~3622;3830~3839,2:0~10;453~518;526~553;613~649;758~794;822~836;857~871;970~1002;1660~1686;2163~2183;2664~2674;2863~2890;2987~3013;3262~3289;3544~3573;3586~3616;3811~3824;3829~3839,3:0~10;16~31;151~165;300~372;379~422;440~476;484~504;518~560;571~582;604~676;689~699;730~759;861~887;1002~1048;1084~1107;1439~1467;1476~1518;1524~1537;1575~1600;1674~1706;1932~1973;2023~2049;2237~2279;2365~2412;2439~2457;2505~2518;2537~2568;2740~2760;2765~2791;2850~2872;3054~3064;3066~3090;3525~3557;3830~3839"
widths_avg = [120,120,120,120]
imsize = [960, 960]
cell = '0.06arcsec'

# EB dependent vars
eb = '' # for eb 1: eb='.1'
refant = 'DA43'

vis_cont = 'uvdata/%s%s.config5.ms' % (field, eb)
vis_cont_avg = 'uvdata/%s%s.config5.cont_avg.ms' % (field, eb)

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
    imagename = 'selfcal/%s%s.config5.0.cont' % (field, eb),
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
os.system('rm -rf selfcal/%s%s.config5.1.cont.*' % (field, eb))
threshold = '1.2mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_1')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config5.1.cont' % (field, eb),
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
caltable='selfcal/%s%s.config5.1.phase.cal' % (field, eb)
solint = '60s'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='T',
        refant=refant,
        calmode='p',
        combine='scan,spw',
        solint=solint)
plotcal(caltable=caltable,
        xaxis="time",
        yaxis="phase",
        subplot=551,
        iteration="antenna",
        plotrange=[0,0,-60,60],
        markersize=3,
        fontsize=3.0,
        figfile="plots/%s%s.config5.1.phase.cal.%s.pdf" % (field, eb, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        spwmap=[0,0,0,0],
        interp="linear")

# Step 2
os.system('rm -rf selfcal/%s%s.config5.2.cont.*' % (field, eb))
threshold = '0.8mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_2')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config5.2.cont' % (field, eb),
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
caltable='selfcal/%s%s.config5.2.phase.cal' % (field, eb)
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
        figfile="plots/%s%s.config5.2.phase.cal.%s.pdf" % (field, eb, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 3
os.system('rm -rf selfcal/%s%s.config5.3.cont.*' % (field, eb))
threshold = '0.5mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_3')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config5.3.cont' % (field, eb),
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
caltable='selfcal/%s%s.config5.3.phase.cal' % (field, eb)
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
        figfile="plots/%s%s.config5.3.phase.cal.%s.pdf" % (field, eb, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 4
os.system('rm -rf selfcal/%s%s.config5.4.cont.*' % (field, eb))
threshold = '0.3mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_amp_cal_1')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config5.4.cont' % (field, eb),
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
caltable='selfcal/%s%s.config5.4.amp.cal' % (field, eb)
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
        figfile="plots/%s%s.config5.4.phase.cal.%s.pdf" % (field, eb, solint),
        markersize=3,
        fontsize=3.0,
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Final cleaning
os.system('rm -rf selfcal/%s%s.config5.final.cont.*' % (field, eb))
threshold = '0.2mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_amp_cal')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config5.final.cont' % (field, eb),
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
