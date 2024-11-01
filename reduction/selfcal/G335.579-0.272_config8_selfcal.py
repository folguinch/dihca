field = 'G335.579-0.272'
flagchannels = "0:0~16;18~40;42~54;70~80;124~141;251~280;302~321;354~371;389~466;530~578;613~623;745~770;796~815;825~835;837~848;857~867;896~913;1049~1064;1077~1099;1155~1166;1182~1214;1233~1246;1258~1269;1324~1365;1431~1445;1509~1522;1544~1558;1605~1630;1695~1715;1724~1734;1825~1847;1950~1963;2031~2069;2073~2093;2177~2191;2340~2363;2374~2391;2399~2410;2441~2456;2562~2573;2651~2662;2767~2786;2833~2854;2870~2880;3009~3019;3100~3110;3186~3197;3212~3223;3241~3252;3315~3326;3361~3372;3376~3386;3533~3543;3550~3561;3830~3839,1:0~10;59~85;145~156;238~254;282~292;378~409;418~436;439~449;492~503;510~537;571~587;612~623;636~647;693~705;873~884;894~906;930~941;971~986;1096~1107;1307~1317;1440~1450;1457~1467;1471~1482;1562~1578;1610~1620;1687~1700;1722~1744;1787~1797;1886~1904;1957~1981;2208~2227;2244~2254;2312~2331;2354~2367;2382~2394;2430~2442;2455~2475;2524~2535;2542~2562;2610~2621;2703~2715;2839~2861;3586~3621;3830~3839,2:0~10;20~49;70~82;173~190;224~274;366~386;454~477;479~525;527~538;568~585;606~650;736~747;764~789;812~822;864~874;974~995;1062~1088;1175~1188;1248~1260;1346~1357;1376~1403;1527~1545;1591~1601;1614~1624;1661~1683;1894~1904;2050~2060;2162~2188;2268~2278;2280~2292;2327~2337;2418~2428;2461~2477;2562~2576;2624~2638;2662~2675;2846~2856;2864~2879;2988~3012;3251~3261;3342~3352;3395~3406;3440~3451;3538~3549;3586~3627;3830~3839,3:0~10;25~43;154~180;226~236;269~280;308~365;383~438;445~470;485~506;522~557;573~584;594~604;610~715;735~766;828~838;849~861;863~887;1003~1030;1033~1043;1046~1057;1094~1117;1120~1131;1136~1150;1178~1220;1236~1249;1427~1488;1491~1521;1529~1545;1559~1576;1579~1598;1669~1712;1763~1783;1786~1796;1853~1889;1951~1964;1973~1983;2021~2039;2062~2075;2100~2111;2201~2215;2237~2275;2311~2321;2327~2341;2367~2409;2418~2433;2436~2462;2496~2523;2541~2564;2566~2578;2620~2646;2662~2677;2702~2716;2731~2741;2767~2800;2828~2838;2843~2870;2875~2890;2906~2916;2921~2936;2944~2956;2989~3010;3047~3086;3107~3117;3225~3243;3313~3328;3342~3353;3398~3426;3444~3456;3512~3523;3526~3556;3685~3699;3710~3721;3733~3744;3803~3822;3830~3839"
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
        figfile="plots/%s%s.config8.2.phase.cal.%s.pdf" % (field, eb, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
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
solint = '15s'
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
