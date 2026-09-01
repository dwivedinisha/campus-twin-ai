import numpy as np

def next_ar1_noise(previous_noise, phi, target_std, rng):
    shock_std = target_std * np.sqrt(max(1e-6, 1 - phi ** 2))
    return phi * previous_noise + rng.normal(0, shock_std)