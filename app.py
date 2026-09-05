from pathlib import Path
import sys

import gradio as gr

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from srm_explorer.analysis import (available_phase6_selections, make_phase6_map,
                                   summarize_phase6_selection)
DATA_PATH = ROOT / "data" / "published" / "phase6_explorer.csv.gz"
if not DATA_PATH.exists():
    raise FileNotFoundError("Committed Phase 6 explorer summary is missing")
import pandas as pd
DATA=pd.read_csv(DATA_PATH)
AVAILABLE=available_phase6_selections(DATA)
MODELS=sorted({x[0] for x in AVAILABLE}); DEFAULT_MODEL="Four-model ensemble" if "Four-model ensemble" in MODELS else MODELS[0]

def choices(model, metric=None, season=None):
    rows=[x for x in AVAILABLE if x[0]==model]
    metrics=sorted({x[1] for x in rows}); metric=metric if metric in metrics else metrics[0]
    rows=[x for x in rows if x[1]==metric]; seasons=[s for s in ["ANN","DJF","MAM","JJA","SON"] if any(x[2]==s for x in rows)]; season=season if season in seasons else seasons[0]
    comparisons=sorted({x[3] for x in rows if x[2]==season})
    return metric,seasons,season,comparisons
DEFAULT_METRIC,SEASONS,DEFAULT_SEASON,COMPARISONS=choices(DEFAULT_MODEL,"tasmax_mean","JJA")
METRICS=sorted({x[1] for x in AVAILABLE if x[0]==DEFAULT_MODEL})
DEFAULT_COMPARISON="G6solar - G6sulfur"


def update(model: str, metric: str, season: str, comparison: str):
    figure = make_phase6_map(DATA,model,metric,season,comparison)
    summary, provenance = summarize_phase6_selection(DATA,model,metric,season,comparison)
    return figure, summary, provenance

def update_choices(model,metric,season):
    metric,seasons,season,comparisons=choices(model,metric,season)
    return gr.update(choices=sorted({x[1] for x in AVAILABLE if x[0]==model}),value=metric),gr.update(choices=seasons,value=season),gr.update(choices=comparisons,value=comparisons[0])


with gr.Blocks(title="SRM Regional Impact Explorer") as demo:
    gr.Markdown(
        "# SRM Regional Impact Explorer\n"
        "Compare regional climate indicators under solar-irradiance reduction, "
        "stratospheric aerosol intervention, and emissions scenarios."
    )
    provenance = gr.Markdown()
    with gr.Row():
        model = gr.Dropdown(MODELS, value=DEFAULT_MODEL, label="Model or ensemble")
        metric = gr.Dropdown(
            METRICS, value=DEFAULT_METRIC, label="Metric"
        )
        season = gr.Dropdown(SEASONS, value=DEFAULT_SEASON, label="Season")
        comparison = gr.Dropdown(COMPARISONS, value=DEFAULT_COMPARISON, label="Comparison")
    run = gr.Button("Update analysis", variant="primary")
    plot = gr.Plot(label="Regional pattern")
    summary = gr.Dataframe(headers=["Statistic", "Value"], interactive=False, label="Regional summary")
    inputs = [model, metric, season, comparison]
    model.change(update_choices,[model,metric,season],[metric,season,comparison])
    metric.change(update_choices,[model,metric,season],[metric,season,comparison])
    season.change(update_choices,[model,metric,season],[metric,season,comparison])
    run.click(update, inputs, [plot, summary, provenance])
    demo.load(update, inputs, [plot, summary, provenance])
    gr.Markdown(
        "G6solar represents reduced solar irradiance in a climate-model experiment. "
        "It is not a complete engineering simulation of satellite mirrors."
    )


if __name__ == "__main__":
    demo.launch()
