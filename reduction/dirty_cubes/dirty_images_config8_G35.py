import os
fields = ['G35.13-0.74', 'G34.43+0.24MM2']
imsize = 5600
eb = ''

for field in fields:
    #for spw in [2]:
    for spw in [0,1,2,3]:
        print field, spw
        imagename = '{0}/dirty/{0}{2}.config8.spw{1}.robust2.0'.format(field,
                                                                       spw, eb)
        if os.path.exists(imagename + '.image.fits'):
            print('Skipping %i' % spw)
            continue
        tclean(vis = '{0}/uvdata/{0}{1}.config8.concat.ms'.format(field, eb),
               field = field,
               spw = '%i' % spw,
               imagename = imagename,
               imsize = [imsize, imsize],
               #cell = '0.06arcsec',
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

