field = 'G11.92-0.61'
flagchannels = "0:0~43;52~115;125~135;137~177;188~225;239~251;257~275;303~325;357~373;377~387;426~440;528~565;601~626;700~717;732~765;779~797;841~866;914~926;928~943;963~973;1110~1144;1348~1362;1470~1504;1575~1588;1591~1609;1710~1723;1823~1834;1910~1919,1:0~10;49~59;123~152;186~207;216~237;708~728;769~793;798~814;872~895;911~932;1006~1019;1041~1051;1056~1071;1088~1109;1123~1140;1147~1181;1194~1222;1350~1373;1473~1484;1725~1752;1886~1919,2:0~95;136~208;287~320;340~406;452~462;475~518;570~675;683~716;719~778;853~925;940~958;976~996;1082~1126;1142~1162;1178~1208;1286~1305;1462~1481;1488~1532;1649~1666;1781~1806;2172~2182;2281~2310;2444~2455;2584~2599;2672~2684;2720~2762;2783~2807;2982~3011;3100~3143;3377~3412;3664~3693;3706~3755;3830~3839,3:0~10;423~494;501~544;564~598;605~630;640~682;691~701;728~837;851~884;980~1011;1122~1155;1157~1174;1216~1231;1572~1588;1601~1637;1798~1830;2059~2094;2363~2401;2484~2539;2552~2579;2624~2693;2888~2917;2969~3001;3166~3176;3178~3215;3347~3363;3523~3533;3560~3570;3639~3682;3830~3839,4:0~16;25~40;56~74;143~174;203~221;308~324;357~367;527~537;548~561;605~621;736~753;846~863;1113~1141;1710~1720;1910~1919,5:0~10;130~154;192~205;217~237;419~429;665~675;711~727;770~790;798~813;874~893;912~931;1041~1051;1056~1072;1090~1107;1123~1139;1148~1181;1197~1221;1349~1372;1727~1751;1888~1919,6:0~28;32~44;67~101;140~161;167~204;237~259;283~337;339~389;432~462;470~480;540~564;593~604;643~654;744~769;825~835;887~902;1142~1153;1366~1376;1490~1504;1549~1573;1830~1846;1852~1877;1910~1919,7:0~10;423~445;452~479;481~495;506~551;564~598;610~622;643~688;695~706;728~794;802~841;852~884;986~1013;1117~1154;1160~1178;1561~1584;1620~1638;1643~1654;1799~1830;2366~2401;2491~2537;2555~2583;2621~2654;2656~2693;2901~2920;2972~3001;3003~3013;3176~3217;3349~3359;3569~3584;3640~3684;3830~3839,8:0~42;55~76;137~174;201~220;265~275;306~322;358~370;529~539;542~563;602~622;735~762;783~795;841~863;1113~1141;1352~1363;1490~1502;1597~1607;1910~1919,9:0~10;123~142;192~203;219~235;711~725;772~791;799~811;875~893;914~930;1058~1068;1091~1105;1123~1134;1151~1179;1197~1219;1355~1370;1727~1751;1888~1919,10:0~45;68~106;141~162;166~203;238~257;283~334;339~392;426~463;543~564;593~607;641~653;746~763;825~835;888~906;1141~1157;1358~1368;1393~1404;1491~1505;1548~1573;1695~1705;1832~1848;1852~1879;1910~1919,11:0~10;426~445;454~480;503~541;566~583;585~598;608~623;645~680;729~789;804~837;852~885;984~1000;1121~1155;1159~1172;1815~1828;2367~2399;2486~2533;2559~2580;2623~2649;2658~2688;2886~2896;2899~2913;2973~3000;3177~3213;3641~3680;3830~3839"
widths_avg = [60, 60, 120, 120, 60, 60, 60, 120, 60, 60, 60, 120]
imsize = [5600, 5600]
cell = '0.01arcsec'
spw = '0,1,2,3,4,5,6,7,8,9,10,11'

# EB dependent vars
eb = '' # for eb 1: eb='.1'
refant = 'DV01'
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
threshold = '0.5mJy'
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
threshold = '0.2mJy'
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
threshold = '0.1mJy'
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
threshold = '0.08mJy'
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
