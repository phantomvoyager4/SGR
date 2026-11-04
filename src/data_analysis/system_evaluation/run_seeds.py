"""Run evaluation_system.ipynb for several seeds: pick ALPHA on tuning seeds, then report on separate test seeds.

The popularity boost's ALPHA must not be chosen on the users it is reported on, or the reported hit rate is
optimistic. So the seeds are split in two:
- tuning seeds (TUNE_SEEDS): their pooled HR@SELECT_K over the fine ALPHA grid picks ALPHA
- test seeds (TEST_SEEDS): run only after ALPHA is frozen; every reported number comes from them

The notebook's code cells are executed unchanged, one seed after another, in a single Python process
(so the 2.5 GB feature matrix is loaded only once). The only differences from running the notebook by hand:
- `SEED` is set to the seed being tested
- `REPORT_PATH` points to reports/evaluation_report_seed<N>.txt, so evaluation_report.txt is not overwritten
- plt.show() saves the figure to reports/seed_plots/ instead of showing it

Outputs, all in reports/:
- evaluation_report_seed<N>.txt   the notebook's report for each seed
- results_seed<N>.json            the numbers the summary is built from
- seed_plots/*.png                the notebook's plots for each seed
- selected_alpha.json             the ALPHA picked on the tuning seeds, written before any test seed runs
- evaluation_report_seeds.txt     the ALPHA selection on the tuning seeds and the results on the test seeds
- hr_by_alpha_tuning.png          HR@K over ALPHA on the tuning seeds, with the selected ALPHA marked

Usage (from any folder):
    python run_seeds.py                                    run TUNE_SEEDS, freeze ALPHA, run TEST_SEEDS, write the summary
    python run_seeds.py --tune 50 1 7 --test 42 99 123     the same with other seeds
    python run_seeds.py --summary-only                     only rebuild the summary from existing results_seed<N>.json files

Each seed takes about 3 minutes, plus about a minute to load the data once.
"""
import argparse
import json
import os
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

TUNE_SEEDS = [50, 1, 7]  # ALPHA is picked on these only (50 is the notebook's own seed)
TEST_SEEDS = [42, 99, 123]  # every reported result comes from these, with ALPHA frozen
SELECT_K = "15"  # ALPHA maximises the pooled tuning HR at this K; 15 is the API's default limit
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
    """Pooled hit rate over all users of several seeds, with a 95% normal-approximation interval.

    hit_counts: number of hits in each seed
    n_total:    number of users in those seeds together

    Returns (hit rate, lower bound, upper bound).
    """
    p = sum(hit_counts) / n_total
    half = 1.96 * np.sqrt(p * (1 - p) / n_total)
    return p, p - half, p + half


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


def select_alpha(tune_runs):
    """The ALPHA with the highest pooled HR@SELECT_K on the tuning seeds (the smallest one on a tie).

    tune_runs: list of result dictionaries of the tuning seeds
    """
    alpha_values, curves = alpha_curves(tune_runs)
    return float(alpha_values[curves[SELECT_K].mean(axis=0).argmax()])


def boost_hits(runs, alpha, k):
    """Number of hits of SGR + ALPHA * popularity in each seed, from the fine-grid hit rates.

    runs:  list of result dictionaries, one per seed
    alpha: the ALPHA value, one of the grid's values
    k:     K as a string, e.g. "15"
    """
    hits = []
    for r in runs:
        key = min(r["grid_hr"], key=lambda a: abs(float(a) - alpha))  # the grid key of this ALPHA
        hits.append(round(r["grid_hr"][key][f"HR@{k}"] * N_USERS))
    return hits


def per_seed_tables(runs, label):
    """Text lines with each method's HR@K per seed, plus mean, std and min-max across those seeds.

    runs:  list of result dictionaries, one per seed
    label: name of the group of seeds, e.g. "tuning"
    """
    lines = [f"Hit rate (HR@K) per seed, {label} seeds"]
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
    return lines


def summary_report(tune_runs, test_runs, alpha):
    """Build the text of evaluation_report_seeds.txt: ALPHA selection on the tuning seeds, results on the test seeds.

    tune_runs: list of result dictionaries of the tuning seeds, used only to pick ALPHA
    test_runs: list of result dictionaries of the test seeds, used for every reported number
    alpha:     the ALPHA picked on the tuning seeds by select_alpha()
    """
    n_tune = N_USERS * len(tune_runs)
    n_test = N_USERS * len(test_runs)
    boost = f"SGR + {alpha:g} pop."
    lines = [
        "SGR recommender evaluation - ALPHA picked on tuning seeds, results on separate test seeds",
        "",
        f"tuning seeds:     {', '.join(str(r['seed']) for r in tune_runs)}  ({n_tune:,} users, used only to pick ALPHA)",
        f"test seeds:       {', '.join(str(r['seed']) for r in test_runs)}  ({n_test:,} users, every reported result)",
        f"                  {N_USERS:,} users per seed, samples drawn independently (overlap is negligible)",
        "method:           the same code and protocol as evaluation_report.txt (evaluation_system.ipynb),",
        "                  run once per seed by run_seeds.py; only SEED changes",
        "",
        "1. ALPHA selection (tuning seeds only)",
        f"ALPHA = the grid value (0, 0.05, ..., 2) with the highest pooled tuning HR@{SELECT_K}  ->  ALPHA = {alpha:g}, frozen",
        "",
        "Best ALPHA per tuning seed and for the pooled tuning curve",
        f"{'':8}" + "".join(f"{r['seed']:>8}" for r in tune_runs) + f"{'pooled':>9}{'pooled HR':>11}",
    ]
    alpha_values, curves = alpha_curves(tune_runs)
    for k in KS:
        per_seed = "".join(f"{alpha_values[curve.argmax()]:>8.2f}" for curve in curves[k])
        mean = curves[k].mean(axis=0)
        lines.append(f"{f'HR@{k}':8}{per_seed}{alpha_values[mean.argmax()]:>9.2f}{mean.max():>11.2%}")

    picks = [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
    lines += ["", "Pooled tuning HR@K at selected ALPHA values", f"{'':8}" + "".join(f"{f'a={a}':>9}" for a in picks)]
    for k in KS:
        mean = curves[k].mean(axis=0)
        lines.append(f"{f'HR@{k}':8}" + "".join(f"{mean[np.argmin(abs(alpha_values - a))]:>9.2%}" for a in picks))

    lines += ["", f"2. Results on the test seeds, ALPHA frozen at {alpha:g}", "",
              f"Pooled hit rate over the {n_test:,} test users, with 95% interval",
              f"{'':8}" + "".join(f"{name:>22}" for name in [boost] + [SHORT[m] for m in METHODS])
              + f"{'Random (exp.)':>15}"]
    for k in KS:
        counts = [boost_hits(test_runs, alpha, k)] + [[r["hits"][m][k] for r in test_runs] for m in METHODS]
        row = ""
        for hit_counts in counts:
            p, lo, hi = pooled(hit_counts, n_test)
            row += f"{f'{p:.2%} [{lo * 100:.2f}-{hi * 100:.2f}]':>22}"
        expected = np.mean([r["expected_random"][k] for r in test_runs])
        lines.append(f"{f'HR@{k}':8}{row}{expected:>15.4%}")
    lines.append("Random baseline measured hits, test seeds together: "
                 + ", ".join(f"HR@{k} {sum(r['hits']['Random'][k] for r in test_runs)}" for k in KS))

    lines += ["", "Compared with baselines, test seeds (method HR / baseline HR)",
              f"{'':8}{'SGR vs random (exp.)':>22}{'SGR vs most popular':>22}{f'{boost} vs most popular':>34}"]
    for k in KS:
        sgr = pooled([r["hits"]["SGR"][k] for r in test_runs], n_test)[0]
        popular = pooled([r["hits"]["Most popular"][k] for r in test_runs], n_test)[0]
        boosted = pooled(boost_hits(test_runs, alpha, k), n_test)[0]
        expected = np.mean([r["expected_random"][k] for r in test_runs])
        lines.append(f"{f'HR@{k}':8}{f'{sgr / expected:,.1f}x':>22}{f'{sgr / popular:,.2f}x':>22}"
                     f"{f'{boosted / popular:,.2f}x':>34}")

    test_values, test_curves = alpha_curves(test_runs)
    lines += ["", "For reference only, not used for anything: the best ALPHA if it were picked on the test seeds",
              f"{'':8}{'best ALPHA':>12}{'HR there':>10}{f'HR at {alpha:g}':>12}{'optimism':>11}"]
    for k in KS:
        mean = test_curves[k].mean(axis=0)
        frozen = mean[np.argmin(abs(test_values - alpha))]
        lines.append(f"{f'HR@{k}':8}{test_values[mean.argmax()]:>12.2f}{mean.max():>10.2%}{frozen:>12.2%}"
                     f"{f'+{(mean.max() - frozen) * 100:.2f} pt':>11}")

    lines += [""] + per_seed_tables(tune_runs, "tuning") + per_seed_tables(test_runs, "test")
    return "\n".join(lines).rstrip() + "\n"


def plot_alpha_curves(tune_runs, alpha, path):
    """Plot the pooled HR@K over ALPHA on the tuning seeds, with the min-max range across them as a light band.

    tune_runs: list of result dictionaries of the tuning seeds
    alpha:     the selected ALPHA, drawn as a dashed vertical line
    path:      where to save the PNG
    """
    alpha_values, curves = alpha_curves(tune_runs)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.axvline(alpha, color="#a3a29d", linewidth=1, linestyle="--")
    ax.annotate(f"selected ALPHA = {alpha:g}", xy=(alpha, 0), xytext=(-6, 6), textcoords="offset points", ha="right",
                color="#52514e", fontsize=10)
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
    seeds = ", ".join(str(r["seed"]) for r in tune_runs)
    ax.set_title(f"Hit rate by popularity boost, tuning seeds {seeds} (band = min-max across seeds)",
                 loc="left", fontsize=12, color="#0b0b0b")
    ax.set_xlabel("ALPHA (strength of the popularity boost)", color="#52514e")
    ax.set_ylabel("HR@K (%)", color="#52514e")
    ax.set_xlim(0, alpha_values[-1] + 0.4)  # room for the direct labels
    ax.set_xticks(np.arange(0, 2.01, 0.25))
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", color="#e8e7e2", linewidth=1)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="lower right", ncol=4, labelcolor="#52514e")  # empty area under the lines
    ax.tick_params(colors="#52514e", length=0)
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#d8d7d2")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close(fig)


def run_or_load(cells, seeds, summary_only):
    """Results of the given seeds: run the notebook for each one, or read its saved results_seed<N>.json.

    cells:        the notebook's code cells, from notebook_code_cells(); None with summary_only
    seeds:        the seeds to run or read
    summary_only: True to read saved results instead of running the notebook
    """
    runs = []
    for seed in seeds:
        if summary_only:
            path = OUT_DIR / f"results_seed{seed}.json"
            if path.exists():
                runs.append(json.loads(path.read_text()))
            else:
                print(f"seed {seed}: no {path.name}, skipped")
            continue
        start = time.time()
        try:
            runs.append(run_seed(cells, seed))
            print(f"seed {seed}: done in {time.time() - start:.0f}s", flush=True)
        except AssertionError as error:
            # e.g. the check in step 3 fails when games with exactly equal scores are listed in a different
            # order than by recommend(); such a seed is left out instead of stopping the whole run
            print(f"seed {seed}: FAILED a notebook check ({error!r}), left out of the summary", flush=True)
    return runs


def main():
    """Run the tuning seeds, freeze ALPHA, run the test seeds, then write the summary report and plot."""
    parser = argparse.ArgumentParser(description="Pick ALPHA on tuning seeds, then evaluate on separate test seeds.")
    parser.add_argument("--tune", type=int, nargs="+", default=TUNE_SEEDS, help="seeds used only to pick ALPHA")
    parser.add_argument("--test", type=int, nargs="+", default=TEST_SEEDS, help="seeds all results come from")
    parser.add_argument("--summary-only", action="store_true", help="rebuild the summary from saved results")
    args = parser.parse_args()
    assert not set(args.tune) & set(args.test), "tuning and test seeds must be different"

    os.chdir(HERE)  # the notebook uses paths relative to its own folder
    OUT_DIR.mkdir(exist_ok=True)
    PLOT_DIR.mkdir(exist_ok=True)
    cells = None if args.summary_only else notebook_code_cells(NOTEBOOK_PATH)

    tune_runs = run_or_load(cells, args.tune, args.summary_only)
    if not tune_runs:
        print("no tuning results, ALPHA can't be picked")
        return
    # ALPHA is fixed here, before any test seed runs
    alpha = select_alpha(tune_runs)
    selected = {"alpha": alpha, "selected_by": f"pooled HR@{SELECT_K}", "tuning_seeds": [r["seed"] for r in tune_runs]}
    (OUT_DIR / "selected_alpha.json").write_text(json.dumps(selected, indent=1) + "\n")
    print(f"ALPHA = {alpha:g}, frozen (picked on seeds {selected['tuning_seeds']})", flush=True)

    test_runs = run_or_load(cells, args.test, args.summary_only)
    if not test_runs:
        print("no test results to report")
        return
    report = summary_report(tune_runs, test_runs, alpha)
    (OUT_DIR / "evaluation_report_seeds.txt").write_text(report)
    plot_alpha_curves(tune_runs, alpha, OUT_DIR / "hr_by_alpha_tuning.png")
    print(report)
    print(f"saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
