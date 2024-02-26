# Continuum
field = 'G351.77-0.54'
## Continuum 
##applycal(vis='uvdata/%s.config8.ms' % field,
##         gaintable=['selfcal/%s.config8.4.amp.cal' % field],
##         interp='linear')
## Lines
#applycal(vis='uvdata/%s.config8.ms' % field,
#         gaintable=['selfcal/%s.config8.3.phase.cal' % field],
#         interp='linear')
#
#split(vis='uvdata/%s.config8.ms' % field,
#      outputvis='uvdata/%s.config8.selfcal.ms' % field,
#      datacolumn='corrected',
#      spw='0,1,2,3')

# For corrected data
# Continuum and lines
applycal(vis='uvdata/%s.config8.ms' % field,
         gaintable=['selfcal/%s.config8.3.phase.cal' % field],
         interp='linear')

split(vis='uvdata/%s.config8.ms' % field,
      outputvis='uvdata/%s.config8.selfcal.ms' % field,
      datacolumn='corrected',
      spw='0,1,2,3')

applycal(vis='uvdata/%s.config5.ms' % field,
         gaintable=['selfcal/%s.config5.3.phase.cal' % field],
         interp='linear')

split(vis='uvdata/%s.config5.ms' % field,
      outputvis='uvdata/%s.config5.selfcal.ms' % field,
      datacolumn='corrected',
      spw='0,1,2,3')
