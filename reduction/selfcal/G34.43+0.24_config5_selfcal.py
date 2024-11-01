field = 'G34.43+0.24'
flagchannels = "0:0~10;14~61;77~140;178~201;213~228;241~311;336~359;370~399;444~457;475~515;523~541;576~604;621~644;681~713;728~745;814~841;898~918;1016~1044;1048~1089;1171~1200;1317~1336;1369~1389;1434~1463;1468~1500;1527~1553;1576~1593;1630~1646;1651~1685;1753~1778;1788~1857;1864~1907;1943~1960;2161~2178;2186~2246;2260~2277;2347~2367;2392~2412;2422~2443;2486~2504;2541~2561;2589~2602;2609~2619;2665~2686;2707~2722;2812~2845;2899~2923;2933~2967;2986~3035;3060~3074;3112~3140;3146~3210;3383~3402;3534~3553;3590~3602;3607~3655;3830~3839,1:0~10;69~87;152~199;215~293;320~370;401~431;446~466;473~504;518~548;612~626;702~726;730~748;765~782;801~829;915~947;966~985;992~1009;1139~1160;1181~1195;1250~1273;1277~1362;1383~1437;1440~1542;1549~1583;1606~1643;1694~1746;1751~1776;1786~1821;1828~1844;1878~1927;1971~1997;2038~2064;2074~2104;2142~2177;2191~2206;2208~2239;2259~2319;2354~2402;2447~2458;2475~2490;2532~2555;2646~2707;2824~2845;2909~2927;3037~3062;3097~3111;3146~3159;3205~3230;3320~3350;3365~3383;3417~3461;3473~3495;3536~3551;3557~3574;3630~3643;3709~3839,2:0~10;24~59;64~92;97~108;140~163;178~240;247~269;325~349;374~434;451~465;478~495;519~543;576~604;606~711;721~744;756~812;825~839;892~911;914~957;973~998;1009~1033;1124~1160;1179~1201;1212~1240;1253~1286;1322~1348;1374~1384;1400~1420;1493~1519;1526~1576;1685~1707;1815~1843;1988~2006;2315~2352;2416~2452;2477~2496;2615~2640;2711~2734;2756~2771;2774~2796;2815~2839;2994~3010;3016~3046;3097~3116;3140~3177;3239~3265;3361~3373;3410~3447;3490~3508;3542~3563;3587~3608;3687~3733;3741~3786;3830~3839,3:0~10;29~47;60~71;166~203;306~350;462~528;539~584;600~632;640~666;678~721;724~746;761~826;828~880;890~922;1005~1048;1159~1217;1241~1286;1294~1304;1338~1357;1395~1408;1583~1627;1631~1677;1681~1702;1735~1758;1832~1873;1918~1933;2009~2051;2093~2128;2181~2207;2361~2373;2396~2435;2478~2492;2522~2567;2594~2619;2662~2684;2696~2726;2897~2915;2920~2961;3007~3033;3073~3085;3097~3110;3151~3164;3201~3256;3385~3405;3503~3532;3548~3576;3593~3615;3679~3717;3830~3839"
widths_avg = [120,120,120,120]
imsize = [960, 960]
cell = '0.06arcsec'

# EB dependent vars
eb = '' # for eb 1: eb='.1'
refant = 'DA49'

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
threshold = '2.5mJy'
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
        figfile="plots/%s%s.config5.1.phase.cal.%s.pdf" % (field, eb, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 2
os.system('rm -rf selfcal/%s%s.config5.2.cont.*' % (field, eb))
threshold = '1.5mJy'
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
        figfile="plots/%s%s.config5.2.phase.cal.%s.pdf" % (field, eb, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 3
os.system('rm -rf selfcal/%s%s.config5.3.cont.*' % (field, eb))
threshold = '0.8mJy'
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
        figfile="plots/%s%s.config5.3.phase.cal.%s.pdf" % (field, eb, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 4
os.system('rm -rf selfcal/%s%s.config5.4.cont.*' % (field, eb))
threshold = '0.6mJy'
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
threshold = '0.5mJy'
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
