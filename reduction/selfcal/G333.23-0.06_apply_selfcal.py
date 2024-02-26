# For continuum and lines
applycal(vis='uvdata/G333.23-0.06.config8.ms',
         gaintable=['selfcal/G333.23-0.06.config8.3.phase.cal'],
         applymode='calonly',
         interp="linear")

split(vis='uvdata/G333.23-0.06.config8.ms',
      outputvis='uvdata/G333.23-0.06.config8.selfcal.ms',
      datacolumn='corrected',
      spw='0,1,2,3')
