# Continuum
# line
applycal(vis='uvdata/IRAS_181622048.config8.concat.ms',
         gaintable=['selfcal/IRAS_181622048.config8.3.phase.cal'],
         applymode='calonly',
         interp="linear")

split(vis='uvdata/IRAS_181622048.config8.concat.ms',
      outputvis='uvdata/IRAS_181622048.1.config8.selfcal.ms',
      datacolumn='corrected',
      spw='0,1,2,3')
split(vis='uvdata/IRAS_181622048.config8.concat.ms',
      outputvis='uvdata/IRAS_181622048.2.config8.selfcal.ms',
      datacolumn='corrected',
      spw='4,5,6,7')
split(vis='uvdata/IRAS_181622048.config8.concat.ms',
      outputvis='uvdata/IRAS_181622048.3.config8.selfcal.ms',
      datacolumn='corrected',
      spw='8,9,10,11')
