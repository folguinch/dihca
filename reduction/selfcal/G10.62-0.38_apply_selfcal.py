# Continuum
#applycal(vis='uvdata/G10.62-0.38.config8.concat.ms',
#         gaintable=['selfcal/G10.62-0.38.config8.4.amp.cal'],
#         applymode='calonly',
#         interp="linear")
# line
applycal(vis='uvdata/G10.62-0.38.config8.concat.ms',
         gaintable=['selfcal/G10.62-0.38.config8.3.phase.cal'],
         applymode='calonly',
         interp="linear")

split(vis='uvdata/G10.62-0.38.config8.concat.ms',
      outputvis='uvdata/G10.62-0.38.1.config8.selfcal.ms',
      datacolumn='corrected',
      spw='0,1,2,3')
split(vis='uvdata/G10.62-0.38.config8.concat.ms',
      outputvis='uvdata/G10.62-0.38.2.config8.selfcal.ms',
      datacolumn='corrected',
      spw='4,5,6,7')
split(vis='uvdata/G10.62-0.38.config8.concat.ms',
      outputvis='uvdata/G10.62-0.38.3.config8.selfcal.ms',
      datacolumn='corrected',
      spw='8,9,10,11')
