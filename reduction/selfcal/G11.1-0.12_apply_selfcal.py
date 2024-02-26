# Continuum
#applycal(vis='uvdata/G11.1-0.12.config8.concat.ms',
#         gaintable=['selfcal/G11.1-0.12.config8.4.amp.cal'],
#         applymode='calonly',
#         interp="linear")
# line
applycal(vis='uvdata/G11.1-0.12.config8.concat.ms',
         gaintable=['selfcal/G11.1-0.12.config8.3.phase.cal'],
         applymode='calonly',
         interp="linear")

split(vis='uvdata/G11.1-0.12.config8.concat.ms',
      outputvis='uvdata/G11.1-0.12.1.config8.selfcal.ms',
      datacolumn='corrected',
      spw='0,1,2,3')
split(vis='uvdata/G11.1-0.12.config8.concat.ms',
      outputvis='uvdata/G11.1-0.12.2.config8.selfcal.ms',
      datacolumn='corrected',
      spw='4,5,6,7')
split(vis='uvdata/G11.1-0.12.config8.concat.ms',
      outputvis='uvdata/G11.1-0.12.3.config8.selfcal.ms',
      datacolumn='corrected',
      spw='8,9,10,11')
