# Continuum
#applycal(vis='uvdata/W33A.config8.concat.ms',
#         gaintable=['selfcal/W33A.config8.4.amp.cal'],
#         interp="linear")
# line
applycal(vis='uvdata/W33A.config8.concat.ms',
         gaintable=['selfcal/W33A.config8.3.phase.cal'],
         interp="linear")

split(vis='uvdata/W33A.config8.concat.ms',
      outputvis='uvdata/W33A.1.config8.selfcal.ms',
      datacolumn='corrected',
      spw='0,1,2,3')
split(vis='uvdata/W33A.config8.concat.ms',
      outputvis='uvdata/W33A.2.config8.selfcal.ms',
      datacolumn='corrected',
      spw='4,5,6,7')
split(vis='uvdata/W33A.config8.concat.ms',
      outputvis='uvdata/W33A.3.config8.selfcal.ms',
      datacolumn='corrected',
      spw='8,9,10,11')
