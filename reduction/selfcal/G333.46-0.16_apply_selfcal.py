# Continuum
field = 'G333.46-0.16'
#applycal(vis='uvdata/%s.config8.ms' % field,
#         gaintable=['selfcal/%s.config8.4.amp.cal' % field],
#         applymode='calonly',
#         interp='linear')
# line
applycal(vis='uvdata/%s.config8.ms' % field,
         gaintable=['selfcal/%s.config8.3.phase.cal' % field],
         applymode='calonly',
         interp='linear')

split(vis='uvdata/%s.config8.ms' % field,
      outputvis='uvdata/%s.config8.selfcal.ms' % field,
      datacolumn='corrected',
      spw='0,1,2,3')
