field = 'G14.22-0.50_S'
flagchannels = "0:0~21;69~79;150~160;170~180;197~207;213~226;316~328;433~445;616~628;747~758;903~915;942~953;1120~1150;1271~1281;1478~1488;1501~1511;1601~1614;1910~1919,1:0~10;136~162;197~214;249~259;391~401;428~441;691~701;902~919;922~935;1015~1025;1217~1227;1362~1379;1736~1750;1903~1919,2:0~10;279~293;297~307;312~329;432~447;482~492;539~553;608~618;881~896;1135~1145;1332~1342;1483~1497;1544~1559;1684~1694;1823~1839;1844~1860;1873~1883;1910~1919,3:0~10;12~25;115~151;266~276;327~339;416~444;446~471;493~526;552~574;615~625;636~656;708~768;793~812;1102~1144;1148~1160;1190~1211;1213~1224;1526~1536;1553~1564;1586~1596;1611~1622;1781~1814;1877~1901;1984~1998;2045~2069;2135~2150;2313~2323;2347~2380;2487~2511;2652~2663;2880~2890;3083~3093;3635~3653;3830~3839"
widths_avg = [120,120,120,120]
imsize = [4096, 4096]
cell = '0.01arcsec'

# EB dependent vars
eb = '' # for eb 1: eb='.1'
refant = 'DV20'

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
threshold = '0.5mJy'
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
solint = 'inf'
rmtables(caltable)
gaincal(vis=vis_cont_avg,
        caltable=caltable,
        field=field,
        gaintype='T',
        refant=refant,
        calmode='p',
        solint=solint,
        combine='scan')
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
threshold = '0.1mJy'
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
        figfile="plots/%s%s.config8.2.phase.cal.%s.pdf" % (field, eb, solint),
        showgui=True)
applycal(vis=vis_cont_avg,
        gaintable=[caltable],
        applymode='calonly',
        interp="linear")

# Step 3
os.system('rm -rf selfcal/%s%s.config8.3.cont.*' % (field, eb))
threshold = '0.08mJy'
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
solint = '40s'
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
threshold = '0.04mJy'
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
threshold = '0.03mJy'
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
