# Continuum
field = 'G343.12-0.06'
# Continuum and line
applycal(vis='uvdata/%s.config8.ms' % field,
         gaintable=['selfcal/%s.config8.3.phase.cal' % field],
         applymode='calonly',
         interp='linear')

split(vis='uvdata/%s.config8.ms' % field,
      outputvis='uvdata/%s.config8.selfcal.ms' % field,
      datacolumn='corrected',
      spw='0,1,2,3')
