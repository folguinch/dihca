import os
fields = ['G335.579-0.272']
robust = 0.5
config = 'concat'
dtype = '{0}.selfcal.contsub'.format(config)
img_fmt = '{0}/dirty/{0}.{1}.spw{2}.robust{3}'

for field in fields:
    #for spw in range(4):
    for spw in [3]:
        print field, spw
        #imagename = '{0}/dirty/{0}.config8.selfcal.contsub.spw{1}.robust2.0'.format(field, spw)
        imagename = img_fmt.format(field, dtype, spw, robust)
        if os.path.isdir(imagename + '.image'):
            print('Skipping %i' % spw)
            continue
        tclean(vis = '{0}/uvdata/{0}.{1}.selfcal.ms.contsub'.format(field,
                                                                    config),
                field = field,
                #spw = '%i' % spw,
                spw = '3,7',
                imagename = imagename,
                imsize = [3600, 3600],
                cell = '0.016arcsec',
                #phasecenter= 'J2000 16:37:58.476 -47.09.05.130',  
                specmode='cube', 
                outframe='LSRK', 
                #gridder='standard', 
                gridder='mosaic', 
                #wprojplanes=128, 
                pblimit=0.2,  
                deconvolver='hogbom',
                #deconvolver='multiscale', 
                #scales=[0,5,15],
                # uvtaper = ['0.7arcsec','0.7arcsec'],
                interactive = False,
                weighting='briggs', 
                robust=robust, 
                niter=0,
                chanchunks=-1,
                parallel=True,
                threshold='0.14mJy')

        imagename = imagename + '.image'
        exportfits(imagename=imagename, fitsimage=imagename + '.fits',
                overwrite=True)

