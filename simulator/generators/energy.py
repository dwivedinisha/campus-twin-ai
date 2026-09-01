from generators.noise_utils import next_ar1_noise

def decide_ac_status(occupancy, temperature, comfort_temp):
    return occupancy > 0 and temperature > comfort_temp

def decide_lighting_status(occupancy):
    return occupancy > 0

def calculate_energy(occupancy, temperature, ac_on, lights_on, params, prev_noise, ar_phi, rng):
    ac_load = 0.0
    if ac_on:
        temp_excess = max(0.0, temperature - params["comfort_temp_c"])
        ac_load = params["ac_power_kw"] + params["temp_sensitivity"] * temp_excess + params["AC_QUADRATIC_COEFF"] * temp_excess ** 2

    lighting_load = params["lighting_power_kw"] if lights_on else 0.0
    equipment_load = params["equipment_power_kw"] if occupancy > 0 else 0.0
    occupancy_effect = occupancy * params["occupancy_effect_kw"]
    new_noise = next_ar1_noise(prev_noise, ar_phi, params["noise_std_kw"], rng)

    total = params["base_load_kw"] + ac_load + lighting_load + equipment_load + occupancy_effect + new_noise
    return round(max(0.0, total), 2), new_noise