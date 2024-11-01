import os

RSLT = '../results'
IMGS = '../clean'
field = 'G335.579-0.272'
source = 'alma1'
imgsuffix = 'config8.selfcal.cont_avg.robust0.5.image.pbcor'
suffix = '.'.join([source, imgsuffix, 'imfit'])

imagename = os.path.join(IMGS, '.'.join([field, imgsuffix]))
estimates = os.path.join(RSLT, '.'.join([field, suffix, 'estimates.txt']))
region = os.path.join(RSLT, '.'.join([field, suffix, 'region.crtf']))
residual = os.path.join(RSLT, '.'.join([field, suffix, 'residual']))
logfile = os.path.join(RSLT, '.'.join([field, suffix, 'log.txt']))
newestimates = os.path.join(RSLT, '.'.join([field, suffix, 'results.txt']))
summary = os.path.join(RSLT, '.'.join([field, suffix, 'summary.txt']))
rms = 5.6E-5

imfit(imagename=imagename, estimates=estimates, region=region,
    residual=residual, logfile=logfile, newestimates=newestimates,
    summary=summary, rms=rms)

