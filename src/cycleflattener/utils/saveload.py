import json
import pydantic

def make_keys_int(adict):
    return {int(k):v for k,v in adict.items()}


class CyclesFileV1(pydantic.BaseModel):
    original_cycle_birth: float
    original_cycle_death: float
    original_cycle: dict[str, float]
    filtration_value: float
    solution_cycles: list[dict[str, float]]

def save_solution_cycles_v1(bd, original_cycle, filt_value, soln_cycles:list[dict], fp):
    data = {"original_cycle_birth": bd[0],
            "original_cycle_death": bd[1],
            "original_cycle": original_cycle,
            "filtration_value": filt_value,
            "solution_cycles": soln_cycles}
    json.dump(data, fp)


def read_solution_cycles_v1(fp) -> CyclesFileV1:
    return CyclesFileV1(**json.load(fp))

