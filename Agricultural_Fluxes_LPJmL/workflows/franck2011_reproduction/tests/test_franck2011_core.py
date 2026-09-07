from __future__ import annotations

import math
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np
from scipy.io import netcdf_file


WORKFLOW_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORKFLOW_DIR))

from franck2011_core import (  # noqa: E402
    harvested_carbon_to_kcal,
    soft_carrying_capacity,
    summarize_global_n_flux,
)
from analyze_n_fluxes import (  # noqa: E402
    _read_series,
    _time_by_space,
    integrate_density,
)
from prepare_configs import GLOBAL_A1_OUTPUTS, _managed_config  # noqa: E402


class Franck2011CoreTests(unittest.TestCase):
    def test_wheat_carbon_to_calories(self) -> None:
        expected = 3.34 / (0.45 * 0.88)
        actual = harvested_carbon_to_kcal(
            1.0,
            dry_matter_fraction=0.88,
            kcal_per_g_moist=3.34,
        )
        self.assertAlmostEqual(actual, expected, places=12)

    def test_pasture_applies_trophic_transfer(self) -> None:
        without_transfer = harvested_carbon_to_kcal(
            1.0,
            dry_matter_fraction=0.25,
            kcal_per_g_moist=1.05,
        )
        with_transfer = harvested_carbon_to_kcal(
            1.0,
            dry_matter_fraction=0.25,
            kcal_per_g_moist=1.05,
            trophic_transfer=0.1,
        )
        self.assertAlmostEqual(with_transfer, without_transfer / 10.0)

    def test_soft_capacity_matches_equation_three(self) -> None:
        # 1e9 kcal on 1e6 m2 supports 1000 people before reserving land.
        actual = soft_carrying_capacity(1.0e9, 1.0e6, 750.0)
        self.assertAlmostEqual(actual, 1000.0 / 1.75)

    def test_n2o_global_flux_counts_two_n_atoms(self) -> None:
        nh3 = summarize_global_n_flux(1.0e12, species_n_atoms=1)
        n2o = summarize_global_n_flux(1.0e12, species_n_atoms=2)
        self.assertAlmostEqual(n2o.molecules_cm2_s, nh3.molecules_cm2_s / 2.0)
        self.assertTrue(math.isclose(n2o.total_tgn_year, 1.0))

    def test_integrate_flux_density_uses_land_area_once(self) -> None:
        flux = np.array([[1.0, 2.0], [3.0, 4.0]])
        area = np.array([[10.0, 20.0], [10.0, 20.0]])
        actual = integrate_density(flux, area)
        np.testing.assert_allclose(actual, np.array([50.0, 110.0]))

    def test_read_lpjml_classic_netcdf_variable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "nh3_agr.nc"
            with netcdf_file(path, mode="w") as dataset:
                dataset.createDimension("time", 2)
                dataset.createDimension("cell", 1)
                time = dataset.createVariable("time", "i", ("time",))
                time[:] = np.array([1996, 1997])
                variable = dataset.createVariable(
                    "ANH3_agr", "d", ("time", "cell")
                )
                variable.units = "gN/m2/yr"
                variable[:] = np.array([[1.0], [2.0]])

            series = _read_series(path, ("ANH3_agr",), "gN/m2/yr")
            np.testing.assert_allclose(
                _time_by_space(series), np.array([[1.0], [2.0]])
            )
            np.testing.assert_allclose(series.time_values, [1996, 1997])

    def test_global_a1_profile_keeps_only_auditable_n_outputs(self) -> None:
        config = _managed_config(
            {},
            mode="global",
            startgrid=0,
            endgrid=None,
            scenario="a1_2005_n",
            workflow="global-a1",
        )
        self.assertEqual(config["startgrid"], "all")
        self.assertEqual(config["endgrid"], "all")
        self.assertTrue(config["river_routing"])
        self.assertEqual(config["with_nitrogen"], "lim")
        self.assertEqual(
            tuple(item["id"] for item in config["output"]),
            GLOBAL_A1_OUTPUTS,
        )

    def test_mpi_smoke_grid_range_disables_routing(self) -> None:
        config = _managed_config(
            {},
            mode="pilot",
            startgrid=27410,
            endgrid=27417,
            scenario="a1_2005_n",
            workflow="global-a1",
        )
        self.assertEqual(config["startgrid"], 27410)
        self.assertEqual(config["endgrid"], 27417)
        self.assertFalse(config["river_routing"])


if __name__ == "__main__":
    unittest.main()
