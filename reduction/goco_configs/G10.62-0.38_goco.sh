#source ../../maat_venv/env/bin/activate

# AFOLI only
#~/Python/GoContinuum/goco --skip DIRTY SPLIT CONTSUB YCLEAN PBCLEAN --neb 3 G10.62-0.38
#~/Python/GoContinuum/goco --skip DIRTY SPLIT CONTSUB YCLEAN PBCLEAN --pos 1452 1402 --neb 3 G10.62-0.38

# Create ms
# continuum
#~/Python/GoContinuum/goco --noredo --skip DIRTY AFOLI CONTSUB YCLEAN --pos 1452 1402 --neb 3 G10.62-0.38
# lines
~/Python/GoContinuum/goco --noredo --skip DIRTY AFOLI SPLIT YCLEAN PBCLEAN --pos 1452 1402 --neb 3 G10.62-0.38

#deactivate
