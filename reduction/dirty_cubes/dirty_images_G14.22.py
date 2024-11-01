fields = ['G14.22-0.50_S']
config = 'config5'
if config == 'config8':
    imsize = [3600, 3600]
    cell = '0.016arcsec'
else:
    imsize = [960, 960]
    cell = '0.06arcsec'

for field in fields:
    for spw in range(4):
        print field, spw
        imagename = '{0}/dirty/{0}.{2}.spw{1}.robust2.0'.format(field, spw,
                config)
        tclean(vis = '{0}/uvdata/{0}.{1}.ms'.format(field, config),
                field = field,
                spw = '%i' % spw,
                imagename = imagename,
                imsize = imsize,
                cell = cell,
                #phasecenter= 'J2000 16:37:58.476 -47.09.05.130',  
                specmode='cube', 
                outframe='LSRK', 
                gridder='standard', 
                #wprojplanes=128, 
                pblimit=0.2,  
                deconvolver='hogbom',
                #deconvolver='multiscale', 
                #scales=[0,5,15],
                # uvtaper = ['0.7arcsec','0.7arcsec'],
                interactive = False,
                weighting='briggs', 
                robust=2.0, 
                niter=0,
                chanchunks=-1,
                parallel=True,
                threshold='0.14mJy')

        imagename = imagename + '.image'
        exportfits(imagename=imagename, fitsimage=imagename + '.fits',
                overwrite=True)

