# Continuum
field = 'IRAS_18337-0743'
#applycal(vis='uvdata/%s.config8.ms' % field,
#         gaintable=['selfcal/%s.config8.4.amp.cal' % field],
#         applymode='calonly',
#         interp='linear')
# line and continuum
applycal(vis='uvdata/%s.config8.ms' % field,
         gaintable=['selfcal/%s.config8.2.phase.cal' % field],
         applymode='calonly',
         spwmap=[0,0,0,0],
         interp='linear')

split(vis='uvdata/%s.config8.ms' % field,
      outputvis='uvdata/%s.config8.selfcal.ms' % field,
      datacolumn='corrected',
      spw='0,1,2,3')
