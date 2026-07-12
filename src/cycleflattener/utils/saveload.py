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



class CycleV2(pydantic.BaseModel):
    birth: float | None = None
    death: float | None = None
    filtration_value: float | None = None
    annot: str | None = None
    length: float
    kappa: float
    cycle: dict[int, float]

class CyclesFileV2(pydantic.BaseModel):
    original_cycle_indices: list[int]
    cycles: list[CycleV2]





if __name__ == "__main__":
    #EXAMPLE USAGE:

    # Writing:
    asd = CycleV2(cycle={1:-1, 3:1}, length=0, kappa=0)
    with open("foobar.json", "w", encoding="utf-8") as f:
        f.write(asd.model_dump_json(indent=4))

    # Reading
    with open("foobar.json", "r", encoding="utf-8") as f:
        read = CycleV2.model_validate_json(f.read())
        print(read)

    with open("foobar.json", "r", encoding="utf-8") as f:
        read = CycleV2(**json.load(f))
        print(read)
