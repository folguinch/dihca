# For continuum
#applycal(vis='uvdata/G5.89-0.37.config8.concat.ms',
#         gaintable=['selfcal/G5.89-0.37.config8.4.amp.cal'],
#         applymode='calonly',
#         interp="linear")
# For lines
applycal(vis='uvdata/G5.89-0.37.config8.concat.ms',
         gaintable=['selfcal/G5.89-0.37.config8.3.phase.cal'],
         applymode='calonly',
         interp="linear")

split(vis='uvdata/G5.89-0.37.config8.concat.ms',
      outputvis='uvdata/G5.89-0.37.1.config8.selfcal.ms',
      datacolumn='corrected',
      spw='0,1,2,3')
split(vis='uvdata/G5.89-0.37.config8.concat.ms',
      outputvis='uvdata/G5.89-0.37.2.config8.selfcal.ms',
      datacolumn='corrected',
      spw='4,5,6,7')
