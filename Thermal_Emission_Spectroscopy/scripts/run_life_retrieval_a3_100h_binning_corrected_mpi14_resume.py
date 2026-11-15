"""Run the frozen corrected A3-100 h retrieval under exactly 14 MPI ranks.

The optional resume flag is injected only after the existing corrected-bin
adapter has validated the dataset, operator, model and command-line scope.
"""

import argparse
import sys

from mpi4py import MPI

import run_life_retrieval_a3_100h_binning_corrected as corrected


EXPECTED_RANKS = 14


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--resume-matched-checkpoint", action="store_true")
    options, forwarded = parser.parse_known_args()
    if MPI.COMM_WORLD.size != EXPECTED_RANKS:
        raise RuntimeError(
            f"Expected {EXPECTED_RANKS} MPI ranks; found {MPI.COMM_WORLD.size}"
        )
    if "--resume" in forwarded:
        raise RuntimeError("Use only the validated matched-checkpoint switch")

    sys.argv = [sys.argv[0], *forwarded]
    if options.resume_matched_checkpoint:
        if "--setup-only" in forwarded:
            raise RuntimeError("A setup-only preflight cannot resume MultiNest")
        legacy_main = corrected.legacy.main

        def resume_validated_checkpoint():
            if "--resume" in sys.argv:
                raise RuntimeError("Refusing duplicate MultiNest resume flag")
            original_argv = sys.argv[:]
            sys.argv.append("--resume")
            try:
                return legacy_main()
            finally:
                sys.argv = original_argv

        corrected.legacy.main = resume_validated_checkpoint

    if MPI.COMM_WORLD.rank == 0:
        print(
            f"[mpi14-wrapper] ranks={MPI.COMM_WORLD.size} "
            f"resume={options.resume_matched_checkpoint}",
            flush=True,
        )
    corrected.main()


if __name__ == "__main__":
    main()
