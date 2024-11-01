field = 'G351.77-0.54'

# Average data
widths_avg = [120, 120, 15, 15,
              120, 120, 15, 15,
              120, 120, 15, 15,
              120, 120, 15, 15]
imsize = [10000, 10000]
cell = '0.005arcsec'
spw = ','.join(map(str, range(16)))
eb = ''
config = 9
vis_cont = 'final_uvdata/G351.77.SC.ms'
vis_cont_avg = f'uvdata/{field}{eb}.config{config}.cont_avg.ms'

flagmanager(vis=vis_cont, mode='save', versionname='before_cont_flags')
initweights(vis=vis_cont, wtmode='weight', dowtsp=True)
split(vis=vis_cont, spw=spw, outputvis=vis_cont_avg, width=widths_avg,
      datacolumn='data')
flagmanager(vis=vis_cont, mode='restore', versionname='before_cont_flags')

tclean(vis=vis_cont_avg,
       imagename=f'selfcal/{field}{eb}.config{config}.cont',
       field=field,
       imsize=imsize,
       spw=spw,
       cell=cell,
       specmode='mfs',
       outframe='LSRK', 
       deconvolver='hogbom',
       gridder='standard',
       interactive=True,
       niter=10000,
       weighting='briggs',
       robust=0.5,
       threshold='0.15mJy')
# Correct coordinate
model = f'selfcal/{field}{eb}.config{config}.cont.model'

# Config 8
flagchannels = ('0:0~33;38~48;50~94;96~144;166~196;207~259;261~271;286~302;'
                '318~405;472~496;500~524;680~709;777~788;790~804;837~849;'
                '1127~1138;1174~1189;1262~1313;1410~1440;1539~1568;1646~1657;'
                '1743~1770;1976~1986;2000~2010;2120~2131;2291~2302;2557~2593;'
                '2819~2830;3239~3259;3496~3510;3569~3581;3830~3839,'
                '1:0~10;84~103;176~192;360~374;1662~1672;1883~1905;2195~2210;'
                '2484~2502;3319~3360;3519~3537;3830~3839,'
                '2:0~32;71~150;222~259;277~343;417~450;527~591;617~653;656~668;'
                '676~694;705~731;782~813;833~869;989~1000;1047~1076;1120~1149;'
                '1445~1464;1724~1734;1854~1886;2515~2536;2693~2704;2979~2997;'
                '3062~3074;3331~3366;3664~3696;3830~3839,'
                '3:0~10;389~404;417~432;435~446;460~490;521~533;693~704;'
                '715~730;1060~1080;1526~1539;1753~1773;2022~2046;2426~2440;'
                '2451~2472;2497~2524;2555~2629;2882~2902;2926~2955;3051~3068;'
                '3102~3119;3463~3484;3508~3534;3564~3592;3602~3628;3744~3760;'
                '3830~3839')
widths_avg = [120, 120, 120, 120]
spw = '0,1,2,3'
tclean_pars = {
    'field': field,
    'imsize': [5760, 5760],
    'cell': '0.01arcsec',
    'spw': spw,
    'specmode': 'mfs', 
    'outframe': 'LSRK', 
    'gridder': 'standard', 
    'deconvolver': 'hogbom', 
    'weighting': 'briggs', 
    'robust': 0.5, 
    'savemodel': 'modelcolumn',
    'threshold': '4mJy',
    'interactive': False,
    'niter': 0,
}
plotcal_pars = {
    'xaxis': 'time',
    'yaxis': 'phase',
    'subplot': 551,
    'iteration': 'antenna',
    'plotrange': [0, 0, -60, 60],
    'markersize': 3,
    'fontsize': 3.0,
    'showgui': True,
}

# EB dependent vars
eb = '' # for eb 1: eb='.1'
refant = 'DV05'
config = 8

vis_cont = f'uvdata/{field}{eb}.config{config}.ms'
vis_cont_avg = f'uvdata/{field}{eb}.config{config}.cont_avg.ms'
tclean_pars['vis'] = vis_cont_avg

flagmanager(vis=vis_cont, mode='save', versionname='before_cont_flags')
initweights(vis=vis_cont, wtmode='weight', dowtsp=True)
flagdata(vis=vis_cont, mode='manual', spw=flagchannels, flagbackup=False)
split(vis=vis_cont, spw=spw, outputvis=vis_cont_avg, width=widths_avg,
      datacolumn='data')
flagmanager(vis=vis_cont, mode='restore', versionname='before_cont_flags')

# Phase cal
# Step 0 --> dirty
tclean(imagename=f'selfcal/{field}{eb}.config{config}.0.cont',
       startmodel=model,
       **tclean_pars) 
caltable = f'selfcal/{field}{eb}.config{config}.coord_correction.cal'
solint = 'inf'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        minsnr=1.5,
        gaintype='T',
        refant=refant,
        combine='scan',
        calmode='p',
        solint=solint)
applycal(vis=vis_cont_avg,
         gaintable=[caltable],
         interp='linear')

# Step 1
os.system(f'rm -rf selfcal/{field}{eb}.config{config}.1.cont.*')
tclean_pars['interactive'] = True
tclean_pars['niter'] = 10000
tclean_pars['threshold'] = '1.0mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_1')
tclean(imagename=f'selfcal/{field}{eb}.config{config}.1.cont',
       **tclean_pars) 
caltable = f'selfcal/{field}{eb}.config{config}.1.phase.cal'
solint = 'inf'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        minsnr=1.5,
        gaintype='T',
        refant=refant,
        calmode='p',
        solint=solint)
plotcal(caltable=caltable,
        figfile=f'plots/{field}{eb}.config{config}.1.phase.cal.{solint}.pdf',
        **plotcal_pars)
applycal(vis=vis_cont_avg,
         gaintable=[caltable],
         interp='linear')

# Step 2
os.system(f'rm -rf selfcal/{field}{eb}.config{config}.2.cont.*')
tclean_pars['threshold'] = '0.8mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_2')
tclean(imagename=f'selfcal/{field}{eb}.config{config}.2.cont',
       **tclean_pars)
caltable = f'selfcal/{field}{eb}.config{config}.2.phase.cal'
solint = '30s'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        minsnr=1.5,
        gaintype='T',
        refant=refant,
        calmode='p',
        solint=solint)
plotcal(caltable=caltable,
        figfile=f'plots/{field}{eb}.config{config}.2.phase.cal.{solint}.pdf',
        **plotcal_pars)
applycal(vis=vis_cont_avg,
         gaintable=[caltable],
         interp='linear')

# Step 3
os.system(f'rm -rf selfcal/{field}{eb}.config{config}.3.cont.*')
tclean_pars['threshold'] = '0.6mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_phase_cal_3')
tclean(imagename=f'selfcal/{field}{eb}.config{config}.3.cont',
       **tclean_pars)
caltable = f'selfcal/{field}{eb}.config{config}.3.phase.cal'
solint = '15s'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        minsnr=1.5,
        gaintype='T',
        refant=refant,
        calmode='p',
        solint=solint)
plotcal(caltable=caltable,
        figfile=f'plots/{field}{eb}.config{config}.3.phase.cal.{solint}.pdf',
        **plotcal_pars)
applycal(vis=vis_cont_avg,
         gaintable=[caltable],
         interp='linear')

# Step 4
os.system(f'rm -rf selfcal/{field}{eb}.config{config}.4.cont.*' % (field, eb, config))
tclean_pars['threshold'] = '0.4mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='before_amp_cal_1')
tclean(imagename=f'selfcal/{field}{eb}.config{config}.4.cont',
       **tclean_pars)

# Step 4 Amp cal
caltable = f'selfcal/{field}{eb}.config{config}.4.amp.cal'
solint = '30s'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        minsnr=1.5,
        gaintype='T',
        refant=refant,
        calmode='ap',
        solint=solint,
        solnorm=True)
plotcal_pars['yaxis'] = 'amp'
plotcal_pars['plotrange'] = [0, 0, 0, 1.2]
plotcal(caltable=caltable,
        figfile=f'plots/{field}{eb}.config{config}.4.phase.cal.{solint}.pdf',
        **plotcal_pars)
applycal(vis=vis_cont_avg,
         gaintable=[caltable],
         interp='linear')

# Final cleaning
os.system(f'rm -rf selfcal/{field}{eb}.config{config}.final.cont.*')
tclean_pars['threshold'] = '0.25mJy'
tclean_pars['savemodel'] = 'none'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_amp_cal')
tclean(imagename=f'selfcal/{field}{eb}.config{config}.final.cont',
       **tclean_pars)


# Config 5
flagchannels = ('0:0~10;13~27;42~93;100~144;171~217;229~253;312~326;350~409;'
                '475~496;500~519;543~562;681~702;779~805;827~849;1154~1187;'
                '1265~1306;1469~1492;1539~1562;1629~1657;1745~1792;1992~2009;'
                '2112~2127;2295~2311;2327~2342;2766~2788;3050~3065;3240~3274;'
                '3483~3508;3830~3839,'
                '1:0~22;76~97;166~189;318~338;348~371;446~465;494~534;900~910;'
                '1487~1510;1606~1646;1655~1678;1811~1849;1879~1926;2078~2092;'
                '2177~2208;2243~2274;2316~2337;2362~2381;2388~2418;2456~2498;'
                '2775~2795;3010~3026;3521~3568;3830~3839,'
                '2:0~38;76~151;223~262;279~348;408~454;505~615;621~726;'
                '789~874;885~898;914~933;972~987;1023~1078;1086~1104;'
                '1125~1154;1232~1247;1397~1417;1431~1468;1588~1629;1673~1689;'
                '1724~1744;1841~1853;1870~1891;2225~2245;2380~2403;2517~2544;'
                '2655~2711;2718~2753;2927~2947;2983~3003;3043~3083;3332~3364;'
                '3609~3630;3653~3699;3830~3839,'
                '3:0~10;377~433;450~490;510~537;548~570;587~622;674~731;'
                '750~775;796~819;928~947;1065~1090;1100~1124;1624~1637;'
                '1744~1777;2014~2049;2095~2106;2314~2341;2428~2472;2499~2525;'
                '2566~2591;2604~2628;2835~2845;2890~2905;2915~2956;3059~3072;'
                '3110~3125;3129~3153;3292~3306;3379~3393;3467~3490;3502~3517;'
                '3571~3626;3749~3767;3797~3810;3830~3839')
widths_avg = [120, 120, 120, 120]
spw = '0,1,2,3'
tclean_pars = {
    'field': field,
    'imsize': [960, 960],
    'cell': '0.06arcsec',
    'spw': spw,
    'specmode': 'mfs', 
    'outframe': 'LSRK', 
    'gridder': 'standard', 
    'deconvolver': 'hogbom', 
    'weighting': 'briggs', 
    'robust': 0.5, 
    'savemodel': 'modelcolumn',
    'threshold': '4mJy',
    'interactive': False,
    'niter': 0,
}
plotcal_pars = {
    'xaxis': 'time',
    'yaxis': 'phase',
    'subplot': 551,
    'iteration': 'antenna',
    'plotrange': [0, 0, -60, 60],
    'markersize': 3,
    'fontsize': 3.0,
    'showgui': True,
}

refant = 'DV07'
config = 5

vis_cont = f'uvdata/{field}.config{config}.ms'
vis_cont_avg = f'uvdata/{field}.config{config}.cont_avg.ms'
tclean_pars['vis'] = vis_cont_avg

flagmanager(vis=vis_cont, mode='save', versionname='before_cont_flags')
initweights(vis=vis_cont, wtmode='weight', dowtsp=True)
flagdata(vis=vis_cont, mode='manual', spw=flagchannels, flagbackup=False)
split(vis=vis_cont, spw=spw, outputvis=vis_cont_avg, width=widths_avg,
      datacolumn='data')
flagmanager(vis=vis_cont, mode='restore', versionname='before_cont_flags')

# Phase cal
# Step 0 --> dirty
tclean(imagename=f'selfcal/{field}{eb}.config{config}.0.cont',
       startmodel=model,
       **tclean_pars) 
caltable = f'selfcal/{field}{eb}.config{config}.coord_correction.cal'
solint = 'inf'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        minsnr=1.2,
        gaintype='T',
        refant=refant,
        combine='scan',
        calmode='p',
        solint=solint)
applycal(vis=vis_cont_avg,
         gaintable=[caltable],
         interp='linear')

# Step 1
os.system(f'rm -rf selfcal/{field}.config{config}.1.cont.*')
tclean_pars['interactive'] = True
tclean_pars['niter'] = 10000
tclean_pars['threshold'] = '9.2mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_phase_cal_0')
tclean(imagename=f'selfcal/{field}.config{config}.1.cont',
       **tclean_pars)
caltable = f'selfcal/{field}.config{config}.1.phase.cal'
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
        figfile=f'plots/{field}.config{config}.1.phase.cal.{solint}.pdf',
        **plotcal_pars)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        interp="linear")

# Step 2
os.system(f'rm -rf selfcal/{field}.config{config}.2.cont.*')
tclean_pars['threshold'] = '3.2mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_phase_cal_1')
tclean(imagename=f'selfcal/{field}.config{config}.2.cont',
       **tclean_pars)
caltable = f'selfcal/{field}.config{config}.2.phase.cal'
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
        figfile=f'plots/{field}.config{config}.2.phase.cal.{solint}.pdf',
        **plotcal_pars)
applycal(vis=vis_cont_avg,
         gaintable=[caltable],
         interp="linear")

# Step 3
os.system(f'rm -rf selfcal/{field}.config{config}.3.cont.*')
tclean_pars['threshold'] = '1.6mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_phase_cal_2')
tclean(imagename=f'selfcal/{field}.config{config}.3.cont',
       **tclean_pars)
caltable = f'selfcal/{field}.config{config}.3.phase.cal'
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
        figfile=f'plots/{field}.config{config}.3.phase.cal.{solint}.pdf',
        **plotcal_pars)
applycal(vis=vis_cont_avg,
         gaintable=[caltable],
         interp="linear")

# Step 4
os.system(f'rm -rf selfcal/{field}.config{config}.4.cont.*')
tclean_pars['threshold'] = '1.4mJy'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_phase_cal_3')
tclean(imagename=f'selfcal/{field}.config{config}.4.cont',
       **tclean_pars)

# Step 4 Amp cal
caltable = f'selfcal/{field}.config{config}.4.amp.cal'
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
plotcal_pars['yaxis'] = 'amp'
plotcal_pars['plotrange'] = [0, 0, 0, 1.2]
plotcal(caltable=caltable,
        figfile=f'plots/{field}.config{config}.4.phase.cal.{solint}.pdf',
        **plotcal_pars)
applycal(vis=vis_cont_avg,
         gaintable=[caltable],
         interp="linear")

# Final cleaning
tclean_pars['threshold'] = '1.1mJy'
tclean_pars['savemodel'] = 'none'
flagmanager(vis=vis_cont_avg, mode='save', versionname='after_amp_cal')
tclean(imagename=f'selfcal/{field}.config{config}.final.cont',
       **tclean_pars)
