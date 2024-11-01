field = 'G333.23-0.06'
flagchannels = "0:0~34;56~120;192~218;319~350;405~418;422~433;456~526;604~628;642~652;759~770;811~849;883~894;993~1003;1051~1063;1117~1128;1166~1176;1252~1264;1266~1277;1281~1292;1410~1432;1551~1561;1563~1574;1669~1694;1881~1907;1983~1994;2238~2248;2357~2367;2386~2396;2422~2445;2457~2472;2476~2486;2494~2506;2524~2534;2579~2589;2658~2670;2772~2782;2792~2802;3148~3159;3181~3191;3225~3235;3293~3304;3336~3349;3355~3374;3383~3411;3426~3438;3484~3494;3496~3507;3651~3661;3696~3714;3749~3759;3778~3788;3827~3839,1:0~10;13~24;65~75;102~112;123~147;195~208;231~242;261~280;302~324;335~345;365~375;399~424;441~511;575~598;601~620;624~655;679~706;746~756;758~779;798~808;822~832;861~872;894~908;937~947;965~979;1037~1068;1073~1092;1124~1134;1153~1168;1221~1233;1252~1262;1368~1385;1405~1416;1472~1482;1502~1513;1531~1560;1614~1629;1705~1717;1730~1748;1756~1771;1792~1810;1819~1829;1836~1846;1923~1934;1953~1965;1971~1981;2022~2045;2140~2150;2206~2216;2246~2264;2274~2302;2352~2362;2394~2405;2446~2468;2521~2532;2607~2631;2703~2713;2766~2781;2902~2929;3057~3068;3274~3291;3327~3337;3612~3622;3651~3677;3829~3839,2:0~10;71~82;117~128;134~144;162~175;182~211;354~364;396~417;419~456;464~489;546~567;596~606;668~678;702~742;836~854;911~938;967~977;982~993;1002~1018;1057~1068;1183~1195;1271~1281;1292~1302;1323~1333;1353~1363;1467~1477;1595~1624;1760~1770;1881~1892;1896~1907;2102~2122;2156~2166;2182~2197;2223~2243;2308~2319;2504~2519;2521~2531;2547~2558;2612~2623;2676~2686;2802~2826;2867~2878;2927~2952;3032~3046;3113~3124;3283~3294;3492~3508;3526~3559;3655~3665;3672~3682;3830~3839,3:0~10;86~111;140~151;185~196;231~309;323~346;356~378;385~409;421~437;463~488;504~516;544~604;606~617;676~695;772~788;793~823;826~841;915~925;951~963;985~996;1096~1106;1112~1123;1131~1141;1201~1211;1221~1232;1273~1283;1377~1402;1420~1438;1443~1454;1469~1479;1517~1534;1617~1649;1702~1719;1797~1808;1817~1829;1878~1903;1962~1984;2000~2010;2185~2213;2311~2346;2353~2372;2381~2393;2449~2462;2480~2500;2603~2613;2713~2741;2859~2880;3442~3452;3470~3491;3623~3634;3649~3663;3830~3839"
widths_avg = [120,120,120,120]
imsize = [4096, 4096]
cell = '0.01arcsec'

# EB dependent vars
eb = '' # for eb 1: eb='.1'
refant = 'DV05'

vis_cont = 'uvdata/%s%s.config8.ms' % (field, eb)
vis_cont_avg = 'uvdata/%s%s.config8.cont_avg.ms' % (field, eb)

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
    imagename = 'selfcal/%s%s.config8.0.cont' % (field, eb),
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
os.system('rm -rf selfcal/%s%s.config8.1.cont.*' % (field, eb))
threshold = '1.0mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_1')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config8.1.cont' % (field, eb),
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
caltable='selfcal/%s%s.config8.1.phase.cal' % (field, eb)
solint = '60s'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='T',
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
        figfile="plots/%s%s.config8.1.phase.cal.%s.pdf" % (field, eb, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        applymode='calonly',
        interp="linear")

# Step 2
os.system('rm -rf selfcal/%s%s.config8.2.cont.*' % (field, eb))
threshold = '0.8mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_2')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config8.2.cont' % (field, eb),
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
caltable='selfcal/%s%s.config8.2.phase.cal' % (field, eb)
solint = '30s'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='T',
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
        figfile="plots/%s%s.config8.2.phase.cal.%s.pdf" % (field, eb, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        applymode='calonly',
        interp="linear")

# Step 3
os.system('rm -rf selfcal/%s%s.config8.3.cont.*' % (field, eb))
threshold = '0.5mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_3')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config8.3.cont' % (field, eb),
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
caltable='selfcal/%s%s.config8.3.phase.cal' % (field, eb)
solint = '20s'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='T',
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
        figfile="plots/%s%s.config8.3.phase.cal.%s.pdf" % (field, eb, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        applymode='calonly',
        interp="linear")

# Step 4
os.system('rm -rf selfcal/%s%s.config8.4.cont.*' % (field, eb))
threshold = '0.1mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_amp_cal_1')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config8.4.cont' % (field, eb),
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
caltable='selfcal/%s%s.config8.4.amp.cal' % (field, eb)
solint = '60s'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='T',
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
        figfile="plots/%s%s.config8.4.phase.cal.%s.pdf" % (field, eb, solint),
        markersize=3,
        fontsize=3.0,
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        applymode='calonly',
        interp="linear")

# Final cleaning
os.system('rm -rf selfcal/%s%s.config8.final.cont.*' % (field, eb))
threshold = '0.1mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_amp_cal')
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config8.final.cont' % (field, eb),
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
