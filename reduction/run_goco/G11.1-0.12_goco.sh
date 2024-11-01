#source ../../maat_venv/env/bin/activate

# AFOLI only
FIELD="G11.1-0.12"
#~/Python/GoContinuum/goco --skip DIRTY SPLIT CONTSUB YCLEAN PBCLEAN --neb 3 "${FIELD}"

# Create ms
# continuum
#~/Python/GoContinuum/goco --noredo --skip DIRTY AFOLI CONTSUB YCLEAN --neb 3 "${FIELD}"
# lines
~/Python/GoContinuum/goco --noredo --skip DIRTY AFOLI SPLIT YCLEAN PBCLEAN --neb 3 "${FIELD}"

#deactivate
