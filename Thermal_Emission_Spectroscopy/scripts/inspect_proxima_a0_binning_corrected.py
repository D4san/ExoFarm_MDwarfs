"""Read-only live snapshot of the three corrected A3-1000h A0 constraints."""

import json
import os
from pathlib import Path
import re
import sys

import launch_proxima_a0_binning_corrected as campaign


def process_rows():
    rows = []
    for folder in Path("/proc").iterdir():
        if not folder.name.isdigit():
            continue
        try:
            args = (folder / "cmdline").read_bytes().decode().rstrip("\0").split("\0")
            if str(campaign.RUNNER) not in args:
                continue
            # Inspect only known MPI rank variables, never expose other env values.
            environment = (folder / "environ").read_bytes().split(b"\0")
            rank_values = {}
            for item in environment:
                key, _, value = item.partition(b"=")
                if key in (b"PMI_RANK", b"PMI_SIZE", b"OMPI_COMM_WORLD_RANK",
                           b"OMPI_COMM_WORLD_SIZE", b"OMP_NUM_THREADS"):
                    rank_values[key.decode()] = value.decode()
            stat = (folder / "stat").read_text().rsplit(")", 1)[1].split()
            rows.append({"pid": int(folder.name), "args": args,
                         "cpu_seconds": (int(stat[11]) + int(stat[12])) / os.sysconf("SC_CLK_TCK"),
                         "mpi_environment": rank_values})
        except (OSError, UnicodeError, ValueError, IndexError):
            continue
    return rows


def tail(path):
    if not path.is_file():
        return ""
    with path.open("rb") as stream:
        stream.seek(max(0, path.stat().st_size - 16000))
        return stream.read().decode(errors="replace")


def main():
    state = json.loads(campaign.STATE.read_text())
    processes = process_rows()
    pid = int(campaign.PID.read_text())
    try:
        supervisor_args = Path(f"/proc/{pid}/cmdline").read_bytes().decode().split("\0")
    except OSError:
        supervisor_args = []
    report = {"timestamp": campaign.now(), "status": state["status"],
              "error": state.get("error", state.get("failure")),
              "supervisor_pid": pid,
              "supervisor_identity_alive": str(Path(campaign.__file__)) in supervisor_args,
              "preflight_variant": state.get("preflight_variant"),
              "preflight": state.get("preflight"),
              "available_GiB": campaign.available_kib() / 1024 ** 2,
              "mpi_jobs": campaign.science_jobs(), "cases": []}
    memory = Path("/proc/meminfo").read_text()
    report["swap_used_MiB"] = (int(re.search(r"SwapTotal:\s*(\d+)", memory)[1])
                               - int(re.search(r"SwapFree:\s*(\d+)", memory)[1])) / 1024
    for case in state["cases"]:
        production = case["run_dir"]
        selected = [row for row in processes if production in row["args"]
                    and Path(row["args"][0]).name.startswith("python")]
        log = Path(case["launch_log"])
        content = tail(log)
        replacements = re.findall(r"Replacements:\s*(\d+)", content)
        evaluations = re.findall(r"Total Samples:\s*(\d+)", content)
        report["cases"].append({
            "variant": case["variant"], "status": case["status"],
            "preflight": case.get("preflight"), "mpiexec_pid": case.get("pid"),
            "effective_free_dimension": case["effective_free_dimension"],
            "active_python_ranks": len(selected),
            "ranks": [{key: value for key, value in row.items() if key != "args"}
                      for row in selected],
            "replacements": int(replacements[-1]) if replacements else None,
            "total_samples": int(evaluations[-1]) if evaluations else None,
            "log_tail": content.splitlines()[-5:],
            "raw_file_count": len(list(Path(production).glob("**/MultiNest_raw/*"))),
        })
    if state["status"] == "PREFLIGHT":
        name = state["preflight_variant"]
        folder = state.get("preflight_folder", "preflight")
        report["preflight_tail"] = tail(campaign.CAMPAIGN / folder / (name + ".log")).splitlines()[-5:]
        path = str(campaign.SCRATCH / folder / name)
        selected = [row for row in processes if path in row["args"]
                    and Path(row["args"][0]).name.startswith("python")]
        report["preflight_active_python_ranks"] = len(selected)
        report["preflight_cpu_seconds"] = [row["cpu_seconds"] for row in selected]
    if "--compact" in sys.argv:
        for job in report["mpi_jobs"]:
            job.pop("command", None)
        for case in report["cases"]:
            case["rank_pids"] = [row["pid"] for row in case["ranks"]]
            case["rank_cpu_seconds"] = [row["cpu_seconds"] for row in case["ranks"]]
            case.pop("ranks")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
