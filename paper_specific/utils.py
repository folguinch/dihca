import numpy as np

def round_to_significant_figures(number, sig_figs=2):
    #if number == 0:
    #    return 0.0
    # Calculate the power of 10 to shift the number
    power = np.floor(np.log10(abs(number))) - (sig_figs - 1)
    # Scale, round, and then scale back
    rounded_number = np.round(number / (10**power)) * (10**power)
    return rounded_number, power

