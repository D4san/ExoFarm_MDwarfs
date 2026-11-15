"""Read-only inspection of the installed POSEIDON fixed-prior contract."""

import inspect
import os
from pathlib import Path

import POSEIDON
from POSEIDON import core, retrieval

print("POSEIDON:", POSEIDON.__file__)
print("define_model:", inspect.signature(core.define_model))
print("set_priors:", inspect.signature(core.set_priors))
print("run_retrieval:", inspect.signature(retrieval.run_retrieval))
print("CPU:", os.cpu_count())
print("FILES:", Path(core.__file__), Path(retrieval.__file__))
for function in (core.define_model, core.set_priors):
    lines = inspect.getsource(function).splitlines()
    selected = set()
    for index, line in enumerate(lines):
        if any(word in line for word in ("fixed", "prior_range", "param_species")):
            selected.update(range(max(0, index - 2), min(len(lines), index + 4)))
    print("SOURCE", function.__name__)
    for index in sorted(selected):
        print(f"{index+1}: {lines[index]}")
lines = Path(retrieval.__file__).read_text().splitlines()
selected = set()
for index, line in enumerate(lines):
    if any(word in line for word in ("prior_ranges[", "pymultinest.run", "n_dims", "sampling_efficiency")):
        selected.update(range(max(0, index - 3), min(len(lines), index + 5)))
print("SOURCE retrieval.py")
for index in sorted(selected):
    print(f"{index+1}: {lines[index]}")
