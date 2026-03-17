from trappist1e_retrieval_common import setup_retrieval_problem, R_MODEL
from POSEIDON.retrieval import run_retrieval


def main():
    bundle = setup_retrieval_problem("A3", 10)

    print("\n==============================================")
    print("Running retrieval: A3, 10 transits")
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
        N_live=1000,
        verbose=False,
        resume=False,
    )


if __name__ == "__main__":
    main()