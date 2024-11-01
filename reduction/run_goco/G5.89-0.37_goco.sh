#source ../../maat_venv/env/bin/activate

# AFOLI only
#~/Python/GoContinuum/goco --skip DIRTY SPLIT CONTSUB YCLEAN PBCLEAN --pos 1360 1466 --neb 2 G5.89-0.37

# Create ms
# continuum
#~/Python/GoContinuum/goco --noredo --skip DIRTY AFOLI CONTSUB YCLEAN --pos 1360 1466 --neb 2 G5.89-0.37
# line
~/Python/GoContinuum/goco --noredo --skip DIRTY AFOLI SPLIT YCLEAN PBCLEAN --pos 1360 1466 --neb 2 G5.89-0.37

#deactivate
