#source ../../maat_venv/env/bin/activate

# AFOLI only
#~/Python/GoContinuum/goco --skip DIRTY SPLIT CONTSUB YCLEAN PBCLEAN --neb 2 IRAS_180891732

# Create ms
# continuum
#~/Python/GoContinuum/goco --noredo --skip DIRTY AFOLI CONTSUB YCLEAN --neb 2 IRAS_180891732
# line
~/Python/GoContinuum/goco --noredo --skip DIRTY AFOLI SPLIT YCLEAN PBCLEAN --neb 2 IRAS_180891732

#deactivate
