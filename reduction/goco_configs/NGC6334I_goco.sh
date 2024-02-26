#source ../../maat_venv/env/bin/activate

# AFOLI only
#~/Python/GoContinuum/goco --skip DIRTY SPLIT CONTSUB YCLEAN PBCLEAN NGC6334I

# Create ms
# continuum
#~/Python/GoContinuum/goco --noredo --skip DIRTY AFOLI CONTSUB YCLEAN NGC6334I
# lines
~/Python/GoContinuum/goco --noredo --skip DIRTY AFOLI SPLIT YCLEAN PBCLEAN NGC6334I

#deactivate
