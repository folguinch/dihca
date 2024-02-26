#source ../../maat_venv/env/bin/activate

# AFOLI only
#~/Python/GoContinuum/goco --skip DIRTY SPLIT CONTSUB YCLEAN PBCLEAN --pos 1240 1488 --neb 3 W33A

# Create ms
# continuum
#~/Python/GoContinuum/goco --noredo --skip DIRTY AFOLI CONTSUB YCLEAN --pos 1240 1488 --neb 3 W33A
# lines
~/Python/GoContinuum/goco --noredo --skip DIRTY AFOLI SPLIT YCLEAN PBCLEAN --pos 1240 1488 --neb 3 W33A

#deactivate
