import os
#fields = ['G336.01-0.82', 'G335.78+0.17', 'G333.12-0.56', 'G333.46-0.16']
fields = ['G335.78+0.17', 'G333.12-0.56', 'G333.46-0.16']
#config5
#imsize = 960
#cell = '0.06arcsec',
#config8
imsize = 5600
cell = '0.01arcsec',
eb = ''

for field in fields:
    for spw in range(4):
        print field, spw
        imagename = '{0}/dirty/{0}.config8.spw{1}.robust2.0'.format(field, spw)

        if os.path.exists(imagename + '.image.fits'):
            print('Skipping %i' % spw)
            continue
        tclean(vis = '{0}/uvdata/{0}.config8.ms'.format(field),
                field = field,
                spw = '%i' % spw,
                imagename = imagename,
                imsize = [imsize, imsize],
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

        # Remove other folders
        os.system('rm -r ' + imagename +
                  '{.model,.workdirectory,.sumwt,.pb,.psf,.residual}')

        # Subimage
        newimage = imagename + '.subimage.image'
        imagename = imagename + '.image'
        imsubimage(imagename=imagename, outfile=newimage, 
                   box="{0},{0},{1},{1}".format(imsize/4, imsize*3/4))
        
        # Export
        exportfits(imagename=newimage, fitsimage=imagename+'.fits', 
                   overwrite=True)

        # Clean up
        os.system('rm -r {0} {1}'.format(newimage, imagename))
