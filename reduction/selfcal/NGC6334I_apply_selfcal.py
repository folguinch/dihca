# Continuum
#applycal(vis='uvdata/NGC6334I.config8.ms',
#         gaintable=['selfcal/NGC6334I.config8.4.amp.cal'],
#         applymode='calonly',
#         interp='linear')
# line
applycal(vis='uvdata/NGC6334I.config8.ms',
         gaintable=['selfcal/NGC6334I.config8.3.phase.cal'],
         applymode='calonly',
         interp='linear')

split(vis='uvdata/NGC6334I.config8.ms',
      outputvis='uvdata/NGC6334I.config8.selfcal.ms',
      datacolumn='corrected',
      spw='0,1,2,3')
