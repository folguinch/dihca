field = 'NGC_6334_I_N'
flagchannels = "0:0~10;59~94;125~135;147~159;192~206;350~392;395~408;480~497;582~593;601~613;627~638;676~702;725~739;922~937;1129~1140;1154~1170;1174~1187;1277~1296;1536~1557;1628~1646;1767~1782;1894~1916;1927~1952;1968~1983;2299~2314;2329~2344;2451~2463;3008~3020;3041~3064;3093~3107;3214~3225;3290~3306;3707~3717;3719~3752;3830~3839,1:0~30;76~86;164~176;252~287;326~372;376~389;422~476;499~527;545~561;570~601;621~647;802~821;834~844;901~926;1018~1045;1067~1081;1093~1111;1245~1255;1281~1291;1356~1370;1381~1399;1402~1422;1443~1454;1483~1528;1547~1559;1567~1582;1596~1638;1652~1680;1710~1737;1767~1777;1795~1807;1815~1843;1857~1870;1902~1917;1927~1941;1989~2008;2073~2093;2146~2162;2175~2200;2248~2273;2290~2301;2312~2335;2366~2379;2392~2416;2460~2498;2642~2652;2757~2803;2927~2940;3012~3023;3143~3159;3196~3212;3243~3253;3315~3325;3428~3448;3519~3555;3579~3591;3635~3645;3656~3669;3811~3839,2:0~10;94~111;245~256;292~339;546~585;590~603;671~708;831~841;885~897;919~932;1236~1247;1414~1424;1438~1459;1724~1740;2225~2251;2528~2538;2668~2678;2727~2739;2903~2913;2927~2943;3052~3066;3069~3081;3150~3161;3452~3466;3608~3623;3628~3639;3651~3667;3676~3691;3830~3839,3:0~10;87~104;221~236;244~255;372~385;396~420;451~464;466~482;510~537;551~564;590~603;607~619;674~732;759~775;798~812;931~944;1073~1092;1110~1120;1150~1173;1507~1528;1541~1554;1557~1575;1741~1767;1844~1854;1918~1931;1936~1952;2092~2104;2306~2330;2437~2472;2504~2521;2579~2589;2605~2630;2833~2860;2918~2928;3118~3131;3137~3162;3457~3469;3474~3485;3592~3622;3830~3839"
widths_avg = [120,120,120,120]
imsize = [5600, 5600]
cell = '0.01arcsec'

# EB dependent vars
eb = '' # for eb 1: eb='.1'
refant = 'DA56'
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
threshold = '0.8mJy'
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
threshold = '0.6mJy'
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
threshold = '0.3mJy'
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
caltable='selfcal/%s%s.config%i.3.phase.cal' % (field, eb, config)
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
caltable='selfcal/%s%s.config%i.4.amp.cal' % (field, eb, config)
solint = 'inf'
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
threshold = '0.06mJy'
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
