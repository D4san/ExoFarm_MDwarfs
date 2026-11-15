from pathlib import Path
import sys
from scipy.io import netcdf_file

root = Path(sys.argv[1])
for name in sys.argv[2:]:
    p = root / f"{name}.nc"
    with netcdf_file(p, mode="r", mmap=False) as ds:
        print(name, "dims", dict(ds.dimensions))
        print(" vars", list(ds.variables))
        for k, v in ds.variables.items():
            if k not in {"lon", "lat", "time", "time_bnds", "lon_bnds", "lat_bnds"}:
                print("  ", k, "shape", v.data.shape, "dtype", v.data.dtype)
