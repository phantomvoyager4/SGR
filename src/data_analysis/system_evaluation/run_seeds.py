"""Run evaluation_system.ipynb for several seeds and combine the results into one report.

The notebook's code cells are executed unchanged, one seed after another, in a single Python process
(so the 2.5 GB feature matrix is loaded only once). The only differences from running the notebook by hand:
- `SEED` is set to the seed being tested
- `REPORT_PATH` points to reports/evaluation_report_seed<N>.txt, so evaluation_report.txt is not overwritten
- plt.show() saves the figure to reports/seed_plots/ instead of showing it

Outputs, all in reports/:
- evaluation_report_seed<N>.txt   the notebook's report for each seed
- results_seed<N>.json            the numbers the summary is built from
- seed_plots/*.png                the notebook's plots for each seed
- evaluation_report_seeds.txt     all seeds combined: per-seed tables, mean, spread, pooled HR with 95% intervals
- hr_by_alpha_seeds.png           HR@K over ALPHA, mean of all seeds, with the min-max range across seeds

Usage (from any folder):
    python run_seeds.py                  run the default SEEDS, then write the summary
    python run_seeds.py 3 4 5            run seeds 3, 4 and 5, then write the summary for them
    python run_seeds.py --summary-only   only rebuild the summary from existing results_seed<N>.json files

Each seed takes about 2.5 minutes, plus about a minute to load the data once.
"""
import json
import os
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # draw plots to files, no windows
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
NOTEBOOK_PATH = HERE / "evaluation_system.ipynb"
OUT_DIR = HERE / "reports"
PLOT_DIR = OUT_DIR / "seed_plots"

SEEDS = [50, 1, 7, 42, 99, 123]  # 50 is the notebook's own seed, the other 5 are the extra samples
N_USERS = 2000  # must match N_USERS in the notebook
KS = ["5", "10", "15", "20"]  # must match KS in the notebook (as strings, because JSON keys are strings)
METHODS = ["SGR", "SGR (no date filter)", "Most popular"]
SHORT = {"SGR": "SGR", "SGR (no date filter)": "SGR no filter", "Most popular": "Most popular"}
K_COLORS = {"5": "#86b6ef", "10": "#3987e5", "15": "#1c5cab", "20": "#0d366b"}  # light (small K) to dark (large K)


def notebook_code_cells(path):
    """Read a Jupyter notebook and return the source code of its code cells, in order.

    path: path to the .ipynb file
    """
    notebook = json.loads(path.read_text(encoding="utf-8"))
    return ["".join(cell["source"]) for cell in notebook["cells"] if cell["cell_type"] == "code"]


def run_seed(cells, seed):
    """Run the notebook's code cells for one seed and return its results as a dictionary.

    cells: the notebook's code cells, from notebook_code_cells()
    seed:  the random seed used to sample the users

    Writes reports/evaluation_report_seed<seed>.txt, reports/results_seed<seed>.json and the seed's plots.
    """
    old_seed = "SEED = 50\n"
    old_report = 'REPORT_PATH = Path("evaluation_report.txt")'
    assert old_seed in cells[0] and old_report in cells[0], "the first code cell no longer sets SEED / REPORT_PATH as expected"
    report_path = OUT_DIR / f"evaluation_report_seed{seed}.txt"
    first_cell = cells[0].replace(old_seed, f"SEED = {seed}\n").replace(old_report, f"REPORT_PATH = Path(r\"{report_path}\")")

    plot_names = ["hr_by_k", "hr_by_alpha"]  # the notebook's plots, in the order they are drawn
    plot_count = [0]

    def save_plot(*args, **kwargs):
        """Replacement for plt.show(): save the current figure as reports/seed_plots/<name>_seed<seed>.png.

        args, kwargs: whatever the notebook passes to plt.show(); ignored
        """
        name = plot_names[plot_count[0]] if plot_count[0] < len(plot_names) else f"plot{plot_count[0] + 1}"
        plt.savefig(PLOT_DIR / f"{name}_seed{seed}.png", dpi=120)
        plt.close("all")
        plot_count[0] += 1

    plt.show = save_plot
    namespace = {"__name__": "__main__"}  # the notebook's variables, like one kernel per seed
    for i, source in enumerate([first_cell] + cells[1:]):
        exec(compile(source, f"<notebook cell {i + 1}>", "exec"), namespace)

    results = {
        "seed": seed,
        "hr": namespace["hr"],
        "hits": namespace["hits"],
        "expected_random": namespace["expected_random"],
        "boost_hits": {str(alpha): hits for alpha, hits in namespace["boost_hits"].items()},
        "grid_hr": {str(alpha): row for alpha, row in namespace["grid_hr"].T.to_dict().items()},
    }
    # round-trip through JSON so the results look the same as when they are read back from the file
    results = json.loads(json.dumps(results, default=float))
    (OUT_DIR / f"results_seed{seed}.json").write_text(json.dumps(results, indent=1))
    return results


def pooled(hit_counts, n_total):
    """Pooled hit rate over all users of all seeds, with a 95% normal-approximation interval.

    hit_counts: number of hits in each seed
    n_total:    number of users in all seeds together

    Returns (hit rate, lower bound, upper bound).
    """
    p = sum(hit_counts) / n_total
    half = 1.96 * np.sqrt(p * (1 - p) / n_total)
    return p, p - half, p + half


def summary_report(runs):
    """Build the text of evaluation_report_seeds.txt from the results of several seeds.

    runs: list of result dictionaries, one per seed, from run_seed() or results_seed<N>.json
    """
    seeds = [r["seed"] for r in runs]
    n_total = N_USERS * len(runs)
    lines = [
        "SGR recommender evaluation - multiple seeds",
        "",
        f"seeds:            {', '.join(map(str, seeds))}  ({len(seeds)} random samples of {N_USERS:,} users)",
        f"users evaluated:  {n_total:,} in total (samples drawn independently; overlap between them is negligible)",
        "method:           the same code and protocol as evaluation_report.txt (evaluation_system.ipynb),",
        "                  run once per seed by run_seeds.py; only SEED changes",
        "",
        "Hit rate (HR@K) per seed",
    ]
    for name in METHODS:
        values = np.array([[r["hr"][name][k] for k in KS] for r in runs])
        lines.append(f"  {name}")
        lines.append(f"  {'seed':>8}" + "".join(f"{f'HR@{k}':>12}" for k in KS))
        for r, row in zip(runs, values):
            lines.append(f"  {r['seed']:>8}" + "".join(f"{v:>12.2%}" for v in row))
        lines.append(f"  {'mean':>8}" + "".join(f"{v:>12.2%}" for v in values.mean(axis=0)))
        lines.append(f"  {'std':>8}" + "".join(f"{v:>12.2%}" for v in values.std(axis=0, ddof=1)))
        lines.append(f"  {'min-max':>8}" + "".join(f"{f'{lo * 100:.2f}-{hi * 100:.2f}':>12}"
                                                   for lo, hi in zip(values.min(axis=0), values.max(axis=0))))
        lines.append("")

    lines += [f"Pooled hit rate over all {n_total:,} users, with 95% interval",
              f"{'':8}" + "".join(f"{SHORT[name]:>22}" for name in METHODS) + f"{'Random (exp.)':>15}"]
    for k in KS:
        row = ""
        for name in METHODS:
            p, lo, hi = pooled([r["hits"][name][k] for r in runs], n_total)
            row += f"{f'{p:.2%} [{lo * 100:.2f}-{hi * 100:.2f}]':>22}"
        expected = np.mean([r["expected_random"][k] for r in runs])
        lines.append(f"{f'HR@{k}':8}{row}{expected:>15.4%}")
    lines.append("Random baseline measured hits, all seeds together: "
                 + ", ".join(f"HR@{k} {sum(r['hits']['Random'][k] for r in runs)}" for k in KS))

    lines += ["", "SGR compared with baselines, pooled (SGR HR / baseline HR)",
              f"{'':8}{'vs random (expected)':>22}{'vs most popular':>18}"]
    for k in KS:
        sgr = pooled([r["hits"]["SGR"][k] for r in runs], n_total)[0]
        popular = pooled([r["hits"]["Most popular"][k] for r in runs], n_total)[0]
        expected = np.mean([r["expected_random"][k] for r in runs])
        lines.append(f"{f'HR@{k}':8}{f'{sgr / expected:,.1f}x':>22}{f'{sgr / popular:,.1f}x':>18}")

    alphas = list(runs[0]["boost_hits"])
    lines += ["", "Experiment: SGR + ALPHA * popularity, pooled HR@K",
              f"{'':8}" + "".join(f"{f'a={a}':>9}" for a in alphas) + f"{'Popular':>10}"]
    for k in KS:
        row = "".join(f"{pooled([r['boost_hits'][a][k] for r in runs], n_total)[0]:>9.2%}" for a in alphas)
        popular = pooled([r["hits"]["Most popular"][k] for r in runs], n_total)[0]
        lines.append(f"{f'HR@{k}':8}{row}{popular:>10.2%}")

    alpha_values, curves = alpha_curves(runs)
    lines += ["", "Fine ALPHA grid (0 to 2, step 0.05): best ALPHA per seed and for the pooled curve",
              f"{'':8}" + "".join(f"{s:>8}" for s in seeds) + f"{'pooled':>9}{'pooled HR':>11}{'HR at a=2':>11}"]
    for k in KS:
        per_seed = "".join(f"{alpha_values[curve.argmax()]:>8.2f}" for curve in curves[k])
        mean = curves[k].mean(axis=0)
        lines.append(f"{f'HR@{k}':8}{per_seed}{alpha_values[mean.argmax()]:>9.2f}{mean.max():>11.2%}{mean[-1]:>11.2%}")

    picks = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
    lines += ["", "Pooled HR@K at selected ALPHA values", f"{'':8}" + "".join(f"{f'a={a}':>9}" for a in picks)]
    for k in KS:
        mean = curves[k].mean(axis=0)
        lines.append(f"{f'HR@{k}':8}" + "".join(f"{mean[np.argmin(abs(alpha_values - a))]:>9.2%}" for a in picks))
    return "\n".join(lines) + "\n"


def alpha_curves(runs):
    """HR@K over the fine ALPHA grid for every seed.

    runs: list of result dictionaries, one per seed

    Returns (ALPHA values, {K: array of shape (number of seeds, number of ALPHA values)}).
    All seeds have the same number of users, so the mean over seeds equals the pooled hit rate.
    """
    grid = sorted(runs[0]["grid_hr"], key=float)
    alpha_values = np.array([float(a) for a in grid])
    curves = {k: np.array([[r["grid_hr"][a][f"HR@{k}"] for a in grid] for r in runs]) for k in KS}
    return alpha_values, curves


def plot_alpha_curves(runs, path):
    """Plot the mean HR@K over ALPHA across seeds, with the min-max range across seeds as a light band.

    runs: list of result dictionaries, one per seed
    path: where to save the PNG
    """
    alpha_values, curves = alpha_curves(runs)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for k in KS:
        mean = curves[k].mean(axis=0) * 100
        ax.fill_between(alpha_values, curves[k].min(axis=0) * 100, curves[k].max(axis=0) * 100,
                        color=K_COLORS[k], alpha=0.15, linewidth=0)
        ax.plot(alpha_values, mean, "-", color=K_COLORS[k], linewidth=2, label=f"HR@{k}")
        # dot at the highest point of the line
        peak = mean.argmax()
        ax.plot(alpha_values[peak], mean[peak], "o", color=K_COLORS[k], markersize=8,
                markeredgecolor="white", markeredgewidth=2)
        # direct label at the end of the line, in text color
        ax.annotate(f"HR@{k}  {mean[-1]:.2f}%", xy=(alpha_values[-1], mean[-1]),
                    xytext=(8, 0), textcoords="offset points", va="center", color="#0b0b0b", fontsize=10)
    ax.set_title(f"Hit rate by popularity boost, mean of {len(runs)} seeds (band = min-max across seeds)",
                 loc="left", fontsize=12, color="#0b0b0b")
    ax.set_xlabel("ALPHA (strength of the popularity boost)", color="#52514e")
    ax.set_ylabel("HR@K (%)", color="#52514e")
    ax.set_xlim(0, alpha_values[-1] + 0.4)  # room for the direct labels
    ax.set_xticks(np.arange(0, 2.01, 0.25))
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", color="#e8e7e2", linewidth=1)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="lower center", ncol=4, labelcolor="#52514e")
    ax.tick_params(colors="#52514e", length=0)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#d8d7d2")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close(fig)


def main():
    """Run the seeds given on the command line (or SEEDS), then write the combined report and plot."""
    os.chdir(HERE)  # the notebook uses paths relative to its own folder
    OUT_DIR.mkdir(exist_ok=True)
    PLOT_DIR.mkdir(exist_ok=True)

    args = sys.argv[1:]
    summary_only = "--summary-only" in args
    seeds = [int(a) for a in args if a != "--summary-only"] or SEEDS

    runs = []
    if summary_only:
        for seed in seeds:
            path = OUT_DIR / f"results_seed{seed}.json"
            if path.exists():
                runs.append(json.loads(path.read_text()))
            else:
                print(f"seed {seed}: no {path.name}, skipped")
    else:
        cells = notebook_code_cells(NOTEBOOK_PATH)
        for seed in seeds:
            start = time.time()
            try:
                runs.append(run_seed(cells, seed))
                print(f"seed {seed}: done in {time.time() - start:.0f}s", flush=True)
            except AssertionError as error:
                # e.g. the check in step 3 fails when games with exactly equal scores are listed in a different
                # order than by recommend(); such a seed is left out instead of stopping the whole run
                print(f"seed {seed}: FAILED a notebook check ({error!r}), left out of the summary", flush=True)

    if not runs:
        print("no results to summarise")
        return
    report = summary_report(runs)
    (OUT_DIR / "evaluation_report_seeds.txt").write_text(report)
    plot_alpha_curves(runs, OUT_DIR / "hr_by_alpha_seeds.png")
    print(report)
    print(f"saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
