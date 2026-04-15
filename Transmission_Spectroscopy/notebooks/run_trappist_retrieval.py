import argparse

from trappist1e_retrieval_common import (
    OBSERVATION_TRANSIT_COUNTS,
    R_MODEL,
    SCENARIO_LABELS,
    setup_retrieval_problem,
)

from POSEIDON.retrieval import run_retrieval


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Run a TRAPPIST-1e retrieval for paired NIRSpec/MIRI "
            "synthetic observations."
        )
    )
    parser.add_argument(
        "--scenario",
        choices=sorted(SCENARIO_LABELS),
        required=True,
        help="Atmospheric scenario to retrieve.",
    )
    parser.add_argument(
        "--n-transits",
        type=int,
        choices=OBSERVATION_TRANSIT_COUNTS,
        required=True,
        help="Number of NIRSpec and MIRI transits to use.",
    )
    parser.add_argument(
        "--n-live",
        type=int,
        default=1000,
        help="Number of MultiNest live points.",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume a previous MultiNest run instead of starting clean.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    bundle = setup_retrieval_problem(args.scenario, args.n_transits)

    print("\n==============================================")
    print(
        "Running retrieval: "
        f"{args.scenario}, {args.n_transits} NIRSpec + "
        f"{args.n_transits} MIRI transits"
    )
    print("Datasets:")
    for filename in bundle["datasets"]:
        print(" -", filename)
    print("Model name:", bundle["model"]["model_name"])
    print("==============================================\n")

    run_retrieval(
        bundle["planet"],
        bundle["star"],
        bundle["model"],
        bundle["opac"],
        bundle["data_new"],
        bundle["priors"],
        bundle["wl"],
        bundle["P"],
        bundle["P_ref"],
        R=R_MODEL,
        spectrum_type="transmission",
        sampling_algorithm="MultiNest",
        N_live=args.n_live,
        verbose=False,
        resume=args.resume,
    )


if __name__ == "__main__":
    main()
