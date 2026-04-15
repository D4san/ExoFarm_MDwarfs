import subprocess
import sys
from pathlib import Path

from common import list_runs, log_output_path


def main():
    script_path = Path(__file__).with_name("run_case.py")
    run_ids = [run["id"] for run in list_runs("earth_sun")]
    processes = []

    for run_id in run_ids:
        log_path = log_output_path(run_id)
        log_handle = log_path.open("w", encoding="utf-8")
        process = subprocess.Popen(
            [sys.executable, str(script_path), run_id],
            cwd=str(script_path.parent),
            stdout=log_handle,
            stderr=subprocess.STDOUT,
        )
        processes.append((run_id, process, log_handle))
        print(f"Launched {run_id} (log: {log_path})")

    failures = []
    for run_id, process, log_handle in processes:
        return_code = process.wait()
        log_handle.close()
        print(f"{run_id} finished with return code {return_code}")
        if return_code != 0:
            failures.append(run_id)

    if failures:
        raise SystemExit(f"Earth suite finished with failures: {', '.join(failures)}")


if __name__ == "__main__":
    main()
