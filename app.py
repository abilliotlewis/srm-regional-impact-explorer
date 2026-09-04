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
    provenance = gr.Markdown(
        "**SYNTHETIC DEMONSTRATION DATA. These values are interface test data, not climate projections.**"
    )
    with gr.Row():
        scenario = gr.Dropdown(
            ["ssp585", "ssp245", "G6solar", "G6sulfur"], value="G6solar", label="Scenario"
        )
        metric = gr.Dropdown(
            ["tasmax_mean", "pr_mean", "rx1day", "cdd"], value="tasmax_mean", label="Metric"
        )
        season = gr.Dropdown(["ANN", "DJF", "MAM", "JJA", "SON"], value="JJA", label="Season")
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
