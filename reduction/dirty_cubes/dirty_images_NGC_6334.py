import os
#fields = ['IRAS_165474247', 'IRAS_165623959']
#fields = ['NGC6334I', 'NGC_6334_I_N']
fields = ['IRAS_165474247']
imsize = 5600

for field in fields:
    for spw in [3]:
        print field, spw
        imagename = '{0}/dirty/{0}.config8.spw{1}.robust2.0'.format(field, spw)
        if os.path.exists(imagename + '.image.fits'):
            newimage = imagename + '.subimage.image.fits'
            imagename = imagename + '.image.fits'
            imsubimage(imagename=imagename, outfile=newimage, 
                       box="{0},{0},{1},{1}".format(imsize/4, imsize*3/4))
            print('Skipping %i' % spw)
            continue
        tclean(vis = '{0}/uvdata/{0}.config8.ms'.format(field),
               field = field,
               spw = '%i' % spw,
               imagename = imagename,
               imsize = [imsize, imsize],
               cell = '0.01arcsec',
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

