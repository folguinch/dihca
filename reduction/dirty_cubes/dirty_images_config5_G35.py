import os#, argparse

#fields = ['IRAS_180891732', 'G5.89-0.37']
fields = ['G34.43+0.24MM2', 'G35.13-0.74'] #, 'G10.62-0.38', 'IRAS_181622048', 'G11.1-0.12']
config = 5
uvdata = 'uvdata'

    # Config
config = 'config%i' % config
if config == 'config5':
    ebs = ['1.', '2.']
    spws = ['0', '1', '2', '3']
    imsize = 960
    cell = '0.06arcsec'
    subim = False
    vis_fmt = '{0}/' + uvdata + '/{0}.{1}' + config + '.ms'
    img_fmt = '{0}/dirty/{0}.{2}' + config + '.spw{1}.robust2.0'
elif config == 'config8':
    #spws = ['0,4', '1,5', '2,6', '3,7']
    ebs = ['']
    spws = ['0,4,8', '1,5,9', '2,6,10', '3,7,11']
    imsize = 5600
    cell = '0.01arcsec'
    subim = True
    vis_fmt = '{0}/' + uvdata + '/{0}.{1}' + config + '.concat.ms'
    img_fmt = '{0}/dirty/{0}.{2}' + config + '.concat.spw{1}.robust2.0'
else:
    raise NotImplementedError

for field in fields:
    for eb in ebs:
        for i, spw in enumerate(spws):
            vis = vis_fmt.format(field, eb)
            imagename = img_fmt.format(field, i, eb)
            if os.path.exists(imagename + '.image.fits'):
                print('Skipping %s' % spw)
                continue

            tclean(vis = vis,
                field = field,
                spw = spw,
                imagename = imagename,
                imsize = [imsize, imsize],
                cell = cell,
                #phasecenter= 'J2000 16:37:58.476 -47.09.05.130',  
                specmode = 'cube', 
                outframe = 'LSRK', 
                gridder = 'standard', 
                #wprojplanes=128, 
                pblimit = 0.2,  
                deconvolver = 'hogbom', 
                #scales=[0,5,15],
                # uvtaper = ['0.7arcsec','0.7arcsec'],
                interactive = False,
                weighting = 'briggs', 
                robust = 2.0, 
                niter = 0,
                chanchunks = -1,
                parallel = True,
                threshold = '0.14mJy')

            # Remove other folders
            os.system('rm -r ' + imagename +
                    '{.model,.workdirectory,.sumwt,.pb,.psf,.residual}')

            # Subimage
            if subim:
                newimage = imagename + '.subimage.image'
                imagename = imagename + '.image'
                imsubimage(imagename=imagename, outfile=newimage, 
                        box="{0},{0},{1},{1}".format(imsize/4, imsize*3/4))
            else:
                newimage = imagename = imagename + '.image'
            
            # Export
            exportfits(imagename=newimage, fitsimage=imagename+'.fits', 
                    overwrite=True)

            # Clean up
            if newimage == imagename:
                os.system('rm -r {0}'.format(newimage))
            else:
                os.system('rm -r {0} {1}'.format(newimage, imagename))
