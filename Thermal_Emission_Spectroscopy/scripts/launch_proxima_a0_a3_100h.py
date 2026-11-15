"""Detach the explicitly authorized three-cell A3-100h A0-reference queue."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from run_proxima_a0_reference_campaign import CAMPAIGN_REL, CONDA_PREFIX, scientific_processes


def main():
    root = Path(__file__).resolve().parents[2]
    campaign = root / CAMPAIGN_REL
    parent = campaign.parent
    log_path = parent / "a0_fixed_reference_20261010.A3_100h.supervisor.log"
    pid_path = parent / "a0_fixed_reference_20261010.A3_100h.supervisor.pid"
    if any(p.exists() for p in (log_path, pid_path, campaign / "campaign_state.json")):
        raise RuntimeError("Launch records already exist; inspect live state, never duplicate")
    active = scientific_processes()
    if active:
        raise RuntimeError("Scientific processes already active: " + "\n".join(active))
    command = [str(CONDA_PREFIX / "bin/python"), "-u",
               str(root / "Thermal_Emission_Spectroscopy/scripts/run_proxima_a0_reference_campaign.py"),
               "--launch", "--mode", "both", "--scenarios", "A3", "--hours", "100"]
    with log_path.open("x", encoding="utf-8") as stream:
        process = subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT,
                                   stdin=subprocess.DEVNULL, cwd=root, start_new_session=True,
                                   env=dict(os.environ, PYTHONUNBUFFERED="1"))
    pid_path.write_text(str(process.pid) + "\n", encoding="utf-8")
    time.sleep(3)
    if process.poll() is not None:
        raise RuntimeError(f"Supervisor exited {process.returncode}; inspect {log_path}")
    print(json.dumps({"supervisor_pid": process.pid, "log": str(log_path),
                      "state": str(campaign / "campaign_state.json"),
                      "scope": "A3-100h; N2O fixed, NH3 fixed, both fixed; 3 cells"}))


if __name__ == "__main__":
    main()
