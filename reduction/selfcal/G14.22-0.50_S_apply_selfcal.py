# Continuum
#applycal(vis='uvdata/G14.22-0.50_S.config8.ms',
#         gaintable=['selfcal/G14.22-0.50_S.config8.4.amp.cal'],
#         applymode='calonly',
#         interp="linear")
# line
applycal(vis='uvdata/G14.22-0.50_S.config8.ms',
         gaintable=['selfcal/G14.22-0.50_S.config8.3.phase.cal'],
         applymode='calonly',
         interp="linear")

split(vis='uvdata/G14.22-0.50_S.config8.ms',
      outputvis='uvdata/G14.22-0.50_S.config8.selfcal.ms',
      datacolumn='corrected',
      spw='0,1,2,3')
