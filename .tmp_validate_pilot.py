import json
import sys
from pathlib import Path

import numpy as np
from scipy.io import netcdf_file

root = Path(sys.argv[1])
cfg = json.loads((root / "output" / "resolved_config.json").read_text())
print("config", {k: cfg.get(k) for k in (
    "with_methane", "methane", "grazing", "grazing_others", "manure_input",
    "prescribe_lsuha", "others_to_crop", "landuse", "with_nitrogen",
    "fertilizer_input", "startgrid", "endgrid", "outputyear", "baseyear",
    "lastyear")})
for name in ("cftfrac", "cftfrac2", "cellfrac_agr", "harvestc_agr",
             "nfert_agr", "nmanure_agr", "n2o_nit_agr", "n2o_denit_agr",
             "nh3_agr", "n2_agr", "ch4_agr", "ch4_rice_em",
             "ch4_grassland", "ch4_emissions_wet", "ch4_emissions",
             "ch4_oxidation", "ch4_sink", "ch4_litter", "ch4_ebullition",
             "ch4_plant_gas"):
    p = root / "output" / f"{name}.nc"
    with netcdf_file(p, mode="r", mmap=False) as ds:
        vars_ = [v for v in ds.variables if v not in {"lon", "lat", "time", "time_bnds", "lon_bnds", "lat_bnds"}]
        print(name, "dims", dict(ds.dimensions), "vars", vars_)
        for v in vars_:
            raw = np.asarray(ds.variables[v].data)
            if raw.dtype.kind in "SU":
                print("  ", v, "string shape", raw.shape)
                continue
            a = np.asarray(raw, dtype=float)
            valid = a[np.isfinite(a) & (a > -1e30)]
            print("  ", v, "shape", a.shape, "min", float(valid.min()) if valid.size else None,
                  "max", float(valid.max()) if valid.size else None,
                  "mean", float(valid.mean()) if valid.size else None,
                  "finite", int(valid.size), "total", int(a.size),
                  "units", getattr(ds.variables[v], "units", b""))

with netcdf_file(root / "output" / "cftfrac.nc", mode="r", mmap=False) as f, netcdf_file(root / "output" / "pft_harvestc.nc", mode="r", mmap=False) as h:
    print("harvest_variables", list(h.variables))
    names = np.asarray(f.variables["NamePFT"].data)
    frac = np.asarray(f.variables["CFTfrac"].data, dtype=float)[-1, :, 0, 0]
    harvest_name = next(v for v in h.variables if v not in {"lon", "lat", "time", "time_bnds", "lon_bnds", "lat_bnds", "pft", "NamePFT"})
    harvest = np.asarray(h.variables[harvest_name].data, dtype=float)[-1, :, 0, 0]
    print("candidate_last_year")
    for i, raw in enumerate(names):
        label = b"".join(raw).decode("ascii", "ignore").strip()
        if frac[i] > 0 or harvest[i] > 0:
            print(i, label, "frac", float(frac[i]), "harvest", float(harvest[i]), "yield_per_frac", float(harvest[i]/frac[i]) if frac[i] > 0 else None)
