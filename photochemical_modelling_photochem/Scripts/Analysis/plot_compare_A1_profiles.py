import argparse
import subprocess
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def parse_profile_text(text):
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    header = lines[0].split()
    data = np.loadtxt(lines[1:])
    if data.ndim == 1:
        data = data[None, :]
    return header, data


def load_current(path):
    return parse_profile_text(Path(path).read_text(encoding="utf-8"))


def load_git(repo_root, git_path):
    text = subprocess.check_output(["git", "show", f"HEAD:{git_path}"], cwd=repo_root, text=True)
    return parse_profile_text(text)


def reorder_desc_pressure(data):
    if data.shape[0] < 2:
        return data
    if np.all(np.diff(data[:, 0]) < 0):
        return data
    return data[::-1]


def chem_from_atmosphere_output(path):
    with Path(path).open("r", encoding="utf-8") as handle:
        header = handle.readline().strip().split()
        data = np.loadtxt(handle)
    if data.ndim == 1:
        data = data[None, :]
    keep = [name for name in header if name not in {"alt", "press", "den", "temp", "eddy"} and not name.endswith("_r")]
    idx = {name: i for i, name in enumerate(header)}
    matrix = np.column_stack([data[:, idx["press"]]] + [data[:, idx[name]] for name in keep])
    return ["PRESS"] + keep, reorder_desc_pressure(matrix)


def main():
    parser = argparse.ArgumentParser(description="Plot visual comparison between original, custom photochem A1, and official photochem ModernEarth.")
    parser.add_argument("--output", default=r"output/figures/Earth_A1_profile_comparison.png")
    parser.add_argument(
        "--official-output",
        default=r"photochemical_modelling_photochem\Results\Official_ModernEarth\ModernEarth_official_steady_state.txt",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[3]
    current_path = repo_root / "Transmission_Spectroscopy" / "profiles" / "Earth_A1_Current_chem.txt"
    git_path = "Transmission_Spectroscopy/profiles/Earth_A1_Current_chem.txt"
    official_path = repo_root / args.official_output

    old_header, old_data = load_git(repo_root, git_path)
    new_header, new_data = load_current(current_path)

    old_data = reorder_desc_pressure(old_data)
    new_data = reorder_desc_pressure(new_data)

    official_loaded = official_path.exists()
    if official_loaded:
        official_header, official_data = chem_from_atmosphere_output(official_path)
    else:
        official_header, official_data = None, None

    old_pressure = old_data[:, 0]
    new_pressure = new_data[:, 0]

    species = ["CH4", "O3", "N2O", "NH3", "H2O", "CO2", "O2", "N2"]
    old_idx = {name: i for i, name in enumerate(old_header)}
    new_idx = {name: i for i, name in enumerate(new_header)}
    official_idx = {name: i for i, name in enumerate(official_header)} if official_loaded else {}

    fig, axes = plt.subplots(2, 4, figsize=(17, 10), sharey=True)
    axes = axes.ravel()

    max_pressure = max(old_pressure.max(), new_pressure.max(), official_data[:, 0].max() if official_loaded else 0.0)
    min_pressure = min(old_pressure.min(), new_pressure.min(), official_data[:, 0].min() if official_loaded else old_pressure.min())

    for ax, sp in zip(axes, species):
        old_values = old_data[:, old_idx[sp]]
        new_values = new_data[:, new_idx[sp]]
        ax.plot(old_values, old_pressure, label="Original", lw=2.0, color="#1f77b4")
        ax.plot(new_values, new_pressure, label="Photochem A1", lw=2.0, color="#d62728", ls="--")
        if official_loaded and sp in official_idx:
            official_values = official_data[:, official_idx[sp]]
            official_pressure = official_data[:, 0]
            ax.plot(official_values, official_pressure, label="Photochem official", lw=2.0, color="#2ca02c", ls=":")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_ylim(max_pressure, min_pressure)
        ax.grid(True, which="both", alpha=0.25)
        ax.set_title(sp)
        ax.set_xlabel("Mixing ratio")

    for ax in axes[::4]:
        ax.set_ylabel("Pressure [bar]")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=min(3, len(labels)), frameon=False)
    title = "Earth A1 profiles: original vs photochem A1"
    if official_loaded:
        title += " vs photochem official ModernEarth"
    fig.suptitle(title, y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.95])

    output_path = repo_root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    print(output_path)


if __name__ == "__main__":
    main()
