import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


NOTEBOOK_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = NOTEBOOK_DIR / "POSEIDON_output" / "TRAPPIST-1e"
RESULTS_DIR = OUTPUT_DIR / "retrievals" / "results"
LOG_DIR = OUTPUT_DIR / "retrievals" / "campaign_logs"


DEFAULT_CAMPAIGN = [
    # 10 transits total observing time
    ("A0", 10, "nirspec"),
    ("A0", 10, "miri"),
    ("A0", 5, "both"),
    ("A3", 10, "nirspec"),
    ("A3", 10, "miri"),
    ("A3", 5, "both"),
    
    # 100 transits total observing time
    ("A0", 100, "nirspec"),
    ("A0", 100, "miri"),
    ("A0", 50, "both"),
    ("A3", 100, "nirspec"),
    ("A3", 100, "miri"),
    ("A3", 50, "both"),

    # 200 transits total observing time
    ("A0", 200, "nirspec"),
    ("A0", 200, "miri"),
    ("A0", 100, "both"),
    ("A3", 200, "nirspec"),
    ("A3", 200, "miri"),
    ("A3", 100, "both"),
]


def model_suffix(instrument):
    return {
        "miri": "_MIRI",
        "nirspec": "_NIRSpec",
        "both": "_NIRSpec_MIRI",
    }[instrument]


def result_path(scenario, n_transits, instrument):
    suffix = model_suffix(instrument)
    return RESULTS_DIR / (
        f"TRAPPIST1e_{scenario}_retrieval_isotherm_isochem_"
        f"{n_transits}transits{suffix}_results.txt"
    )


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the queued TRAPPIST-1e retrieval campaign sequentially."
    )
    parser.add_argument(
        "--n-live",
        type=int,
        default=1000,
        help="MultiNest live points for each retrieval.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Pass --resume to each retrieval command.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Run even when the expected results file already exists.",
    )
    return parser.parse_args()


def run_one(scenario, n_transits, instrument, n_live, resume, force, master_log):
    expected = result_path(scenario, n_transits, instrument)
    label = f"{scenario}_{n_transits}transits_{instrument}"

    if expected.exists() and not force:
        message = f"[{timestamp()}] SKIP {label}: {expected.name} exists"
        print(message, flush=True)
        master_log.write(message + "\n")
        master_log.flush()
        return 0

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    run_log_path = LOG_DIR / f"{label}.log"
    command = [
        sys.executable,
        "run_trappist_retrieval.py",
        "--scenario",
        scenario,
        "--n-transits",
        str(n_transits),
        "--instrument",
        instrument,
        "--n-live",
        str(n_live),
    ]
    if resume:
        command.append("--resume")

    start_message = f"[{timestamp()}] START {label}: {' '.join(command)}"
    print(start_message, flush=True)
    master_log.write(start_message + "\n")
    master_log.flush()

    with run_log_path.open("a", encoding="utf-8") as run_log:
        run_log.write(start_message + "\n")
        run_log.flush()
        completed = subprocess.run(
            command,
            cwd=NOTEBOOK_DIR,
            stdout=run_log,
            stderr=subprocess.STDOUT,
            text=True,
        )

    end_message = f"[{timestamp()}] END {label}: returncode={completed.returncode}"
    print(end_message, flush=True)
    master_log.write(end_message + "\n")
    master_log.flush()
    return completed.returncode


def main():
    args = parse_args()
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    master_log_path = LOG_DIR / "campaign_trappist_retrieval_queue.log"

    with master_log_path.open("a", encoding="utf-8") as master_log:
        master_log.write(f"\n[{timestamp()}] CAMPAIGN START\n")
        master_log.flush()

        for scenario, n_transits, instrument in DEFAULT_CAMPAIGN:
            returncode = run_one(
                scenario,
                n_transits,
                instrument,
                args.n_live,
                args.resume,
                args.force,
                master_log,
            )
            if returncode != 0:
                master_log.write(
                    f"[{timestamp()}] CAMPAIGN STOPPED after failure\n"
                )
                master_log.flush()
                raise SystemExit(returncode)

        master_log.write(f"[{timestamp()}] CAMPAIGN COMPLETE\n")
        master_log.flush()


if __name__ == "__main__":
    main()
