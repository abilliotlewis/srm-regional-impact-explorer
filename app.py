from pathlib import Path
import sys

import gradio as gr

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from srm_explorer.analysis import load_metrics, make_map, summarize_region
from generate_demo_data import build as build_demo_data

DATA_PATH = ROOT / "data" / "processed" / "regional_metrics.csv"
if not DATA_PATH.exists():
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    build_demo_data().to_csv(DATA_PATH, index=False)
DATA = load_metrics(DATA_PATH)
SCENARIOS = sorted(DATA["scenario"].unique().tolist())
METRICS = sorted(DATA["metric"].unique().tolist())
SEASONS = [s for s in ["ANN", "DJF", "MAM", "JJA", "SON"] if s in set(DATA["season"])]
DEFAULT_SCENARIO = "G6solar" if "G6solar" in SCENARIOS else SCENARIOS[0]
DEFAULT_METRIC = "tasmax_mean" if "tasmax_mean" in METRICS else METRICS[0]
DEFAULT_SEASON = "JJA" if "JJA" in SEASONS else SEASONS[0]
INITIAL_PROVENANCE = (
    "**SYNTHETIC DEMONSTRATION DATA. These values are interface test data, not climate projections.**"
    if bool(DATA["is_demo"].all())
    else f"**Model-derived records for {DATA['period'].iloc[0]}. See the source manifest and result note for provenance and limitations.**"
)


def update(scenario: str, metric: str, season: str, mode: str):
    figure = make_map(DATA, scenario, metric, season, mode)
    summary, provenance = summarize_region(DATA, scenario, metric, season, mode)
    return figure, summary, provenance


with gr.Blocks(title="SRM Regional Impact Explorer") as demo:
    gr.Markdown(
        "# SRM Regional Impact Explorer\n"
        "Compare regional climate indicators under solar-irradiance reduction, "
        "stratospheric aerosol intervention, and emissions scenarios."
    )
    provenance = gr.Markdown(INITIAL_PROVENANCE)
    with gr.Row():
        scenario = gr.Dropdown(
            SCENARIOS, value=DEFAULT_SCENARIO, label="Scenario"
        )
        metric = gr.Dropdown(
            METRICS, value=DEFAULT_METRIC, label="Metric"
        )
        season = gr.Dropdown(SEASONS, value=DEFAULT_SEASON, label="Season")
        mode = gr.Radio(
            ["Difference from SSP5-8.5", "Absolute ensemble mean"],
            value="Difference from SSP5-8.5",
            label="Display",
        )
    run = gr.Button("Update analysis", variant="primary")
    plot = gr.Plot(label="Regional pattern")
    summary = gr.Dataframe(headers=["Statistic", "Value"], interactive=False, label="Regional summary")
    run.click(update, [scenario, metric, season, mode], [plot, summary, provenance])
    demo.load(update, [scenario, metric, season, mode], [plot, summary, provenance])
    gr.Markdown(
        "G6solar represents reduced solar irradiance in a climate-model experiment. "
        "It is not a complete engineering simulation of satellite mirrors."
    )


if __name__ == "__main__":
    demo.launch()
