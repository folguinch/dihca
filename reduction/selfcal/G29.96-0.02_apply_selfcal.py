# Continuum
field = 'G29.96-0.02'
# Continuum 
#applycal(vis='uvdata/%s.config8.concat.ms' % field,
#         gaintable=['selfcal/%s.config8.4.amp.cal' % field],
#         applymode='calonly',
#         interp='linear')
# Lines
applycal(vis='uvdata/%s.config8.concat.ms' % field,
         gaintable=['selfcal/%s.config8.3.phase.cal' % field],
         applymode='calonly',
         interp='linear')

split(vis='uvdata/%s.config8.concat.ms' % field,
      outputvis='uvdata/%s.1.config8.selfcal.ms' % field,
      datacolumn='corrected',
      spw='0,1,2,3')
split(vis='uvdata/%s.config8.concat.ms' % field,
      outputvis='uvdata/%s.2.config8.selfcal.ms' % field,
      datacolumn='corrected',
      spw='4,5,6,7')
