import json
import pydantic

def make_keys_int(adict):
    return {int(k):v for k,v in adict.items()}


class CyclesFileV1(pydantic.BaseModel):
    original_cycle_birth: float
    original_cycle_death: float
    original_cycle: dict[int, float]
    filtration_value: float
    solution_cycles: list[dict[int, float]]

def save_solution_cycles_v1(bd, original_cycle, filt_value, soln_cycles:list[dict], fp):
    data = {"original_cycle_birth": bd[0],
            "original_cycle_death": bd[1],
            "original_cycle": original_cycle,
            "filtration_value": filt_value,
            "solution_cycles": soln_cycles}

    data_validated = CyclesFileV1(**data)
    fp.write(data_validated.model_dump_json())


def read_solution_cycles_v1(fp) -> CyclesFileV1:
    return CyclesFileV1(**json.load(fp))

