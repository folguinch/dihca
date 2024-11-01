# For continuum
#applycal(vis='uvdata/IRAS_180891732.config8.concat.ms',
#         gaintable=['selfcal/IRAS_180891732.config8.4.amp.cal'],
#         applymode='calonly',
#         interp="linear")
# For lines
applycal(vis='uvdata/IRAS_180891732.config8.concat.ms',
         gaintable=['selfcal/IRAS_180891732.config8.3.phase.cal'],
         applymode='calonly',
         interp="linear")

split(vis='uvdata/IRAS_180891732.config8.concat.ms',
      outputvis='uvdata/IRAS_180891732.1.config8.selfcal.ms',
      datacolumn='corrected',
      spw='0,1,2,3')
split(vis='uvdata/IRAS_180891732.config8.concat.ms',
      outputvis='uvdata/IRAS_180891732.2.config8.selfcal.ms',
      datacolumn='corrected',
      spw='4,5,6,7')
