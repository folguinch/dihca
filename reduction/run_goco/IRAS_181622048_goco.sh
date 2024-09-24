#source ../../maat_venv/env/bin/activate

# AFOLI only
FIELD="IRAS_181622048"
#~/Python/GoContinuum/goco --skip DIRTY SPLIT CONTSUB YCLEAN PBCLEAN --neb 3 "${FIELD}"

# Create ms
# continuum
# lines
~/Python/GoContinuum/goco --noredo --skip DIRTY AFOLI YCLEAN --neb 3 "${FIELD}"

#deactivate
