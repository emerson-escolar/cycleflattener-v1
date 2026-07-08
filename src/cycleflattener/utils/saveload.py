import json

def save_solution_cycles(bd, original_cycle, filt_value, soln_cycles:list[dict], fp):
    data = {"original_cycle_birth": bd[0],
            "original_cycle_death": bd[1],
            "original_cycle": original_cycle,
            "filtration_value": filt_value,
            "solution_cycles": soln_cycles}
    json.dump(data, fp)
