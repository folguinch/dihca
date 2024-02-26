field = 'G335.579-0.272'
flagchannels = "0:0~12;14~63;66~77;83~97;126~162;188~225;245~286;288~303;349~364;378~392;405~436;440~475;482~495;505~523;541~563;610~622;642~661;663~680;690~706;748~768;791~808;851~877;898~912;918~931;982~1007;1066~1081;1144~1157;1188~1209;1217~1254;1342~1362;1483~1499;1504~1518;1538~1569;1606~1627;1633~1666;1691~1719;1742~1759;1794~1808;1826~1852;1866~1880;1917~1940;1957~1985;1990~2021;2033~2077;2088~2104;2108~2126;2179~2192;2326~2341;2358~2382;2390~2411;2426~2441;2449~2464;2472~2490;2514~2531;2557~2582;2590~2609;2653~2669;2708~2724;2728~2738;2752~2766;2769~2784;2835~2854;2872~2890;2978~3008;3012~3023;3071~3088;3104~3133;3154~3180;3183~3212;3225~3241;3276~3304;3319~3349;3352~3373;3421~3436;3552~3568;3633~3646;3703~3732;3752~3828;3830~3839,1:0~10;58~97;199~210;237~250;317~361;386~437;439~455;489~507;509~533;571~595;612~629;639~668;681~712;861~888;896~915;929~945;971~990;1012~1023;1081~1108;1133~1146;1156~1176;1193~1203;1306~1321;1343~1358;1420~1436;1443~1462;1469~1525;1553~1627;1630~1647;1655~1706;1708~1722;1724~1744;1772~1804;1833~1843;1858~1880;1886~1911;1919~1938;1956~1984;1990~2006;2039~2051;2056~2072;2075~2088;2119~2131;2140~2160;2182~2195;2209~2231;2241~2273;2311~2340;2354~2370;2379~2402;2428~2447;2455~2482;2523~2564;2611~2623;2638~2651;2688~2700;2702~2716;2760~2783;2814~2869;2992~3006;3078~3091;3163~3176;3208~3224;3265~3280;3291~3302;3307~3322;3366~3377;3380~3400;3482~3496;3498~3512;3532~3544;3588~3623;3642~3656;3699~3719;3721~3736;3759~3771;3793~3803;3830~3839,2:0~10;21~52;56~82;94~108;140~151;170~194;220~274;299~312;323~338;366~384;423~446;455~525;528~552;566~584;602~651;658~669;672~687;763~789;813~840;856~877;970~1002;1025~1042;1061~1079;1099~1130;1163~1190;1211~1227;1245~1263;1342~1366;1372~1402;1404~1416;1530~1548;1661~1684;1813~1828;1836~1851;1956~1983;2022~2035;2046~2059;2140~2160;2162~2194;2222~2236;2262~2294;2322~2338;2360~2373;2407~2421;2435~2446;2461~2480;2560~2575;2602~2618;2621~2637;2662~2681;2841~2858;2864~2887;2945~2960;2987~3021;3086~3108;3144~3158;3173~3188;3196~3225;3258~3271;3336~3354;3362~3374;3389~3406;3434~3452;3534~3581;3589~3627;3645~3656;3724~3740;3799~3839,3:0~44;107~121;150~195;222~233;277~294;307~366;384~424;444~469;479~505;518~560;567~586;605~710;712~727;734~767;828~840;847~862;864~905;972~985;1001~1058;1084~1151;1178~1206;1213~1227;1233~1256;1313~1329;1423~1469;1475~1520;1526~1546;1557~1575;1581~1599;1677~1714;1755~1797;1850~1872;1874~1893;1938~1966;2017~2057;2061~2075;2098~2110;2123~2134;2197~2223;2235~2274;2311~2322;2324~2341;2366~2408;2417~2462;2466~2481;2505~2525;2541~2575;2615~2633;2657~2691;2694~2718;2726~2753;2763~2800;2841~2872;2878~2894;2918~2934;2937~2954;2988~3004;3043~3117;3183~3199;3201~3214;3226~3252;3255~3268;3314~3327;3347~3374;3392~3426;3437~3456;3507~3520;3523~3557;3576~3588;3684~3704;3708~3723;3732~3748;3754~3765;3802~3828;3830~3839"
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

# Correct coordinate
model='selfcal/%s.config8.final.cont.model' % field
# Phase cal
# Step 0 --> dirty
threshold = '4mJy'
tclean(vis = vis_cont_avg,
    field = field,
    imagename = 'selfcal/%s%s.config5.0.cont' % (field, eb),
    startmodel = model,
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
    savemodel='modelcolumn',
    niter=0,
    threshold=threshold) 
caltable='selfcal/%s%s.config5.coord_correction.cal' % (field, eb)
solint = 'inf'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='G',
        refant=refant,
        combine='scan',
        calmode='p',
        solint=solint)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 1
os.system('rm -rf selfcal/%s%s.config5.1.cont.*' % (field, eb))
threshold = '3.5mJy'
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
threshold = '2.0mJy'
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
threshold = '1.0mJy'
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
threshold = '0.8mJy'
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
threshold = '0.8mJy'
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

# Select best
caltable = 'selfcal/%s%s.config5.4.amp.cal' % (field, eb)
vis_selfcal = 'uvdata/%s%s.config5.selfcal.ms' % (field, eb)
applycal(vis=vis_cont,
        gaintable=[caltable],
        interp="linear")
split(vis=vis_cont,
        outputvis=vis_selfcal,
        field=field,
        datacolumn='corrected',
        keepflags=True)

