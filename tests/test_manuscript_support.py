from pathlib import Path
import hashlib
import json
import re
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_manuscript_support import build_key_results


def key_results() -> pd.DataFrame:
    return pd.read_csv(ROOT / "docs/MANUSCRIPT_KEY_RESULTS.csv")


def test_manuscript_key_results_rebuild_exactly():
    committed = key_results()
    rebuilt = build_key_results()
    pd.testing.assert_frame_equal(
        committed,
        rebuilt,
        check_dtype=False,
        atol=5e-8,
        rtol=0,
    )
    assert len(committed) == 48
    assert set(committed["model"]) == {
        "CNRM-ESM2-1",
        "IPSL-CM6A-LR",
        "MPI-ESM1-2-LR",
        "UKESM1-0-LL",
    }
    assert set(zip(committed["variable"], committed["season"])) == {
        ("tasmax", "JJA"),
        ("tasmax", "MAM"),
        ("pr", "JJA"),
        ("pr", "ANN"),
    }


def test_manuscript_jja_temperature_headline_values():
    data = key_results()
    data = data[(data["variable"] == "tasmax") & (data["season"] == "JJA")]
    expected = {
        "original_box": (-0.3080213, 0.0914899, 4, 0),
        "southeast_land": (-0.3744556, 0.0951763, 4, 0),
        "gulf_coast": (-0.3725135, 0.1234199, 2, 2),
    }
    for domain, (mean, spread, below, includes) in expected.items():
        rows = data[data["domain"] == domain]
        assert len(rows) == 4
        assert (rows["mean_difference"] < 0).all()
        assert np.isclose(rows.iloc[0]["ensemble_mean"], mean)
        assert np.isclose(rows.iloc[0]["inter_model_sd"], spread)
        assert rows.iloc[0]["temporal_ci_negative_count"] == below
        assert rows.iloc[0]["temporal_ci_includes_zero_count"] == includes


def test_manuscript_weaker_result_counts():
    data = key_results()
    mam = data[(data["variable"] == "tasmax") & (data["season"] == "MAM")]
    for _, rows in mam.groupby("domain"):
        assert rows.iloc[0]["positive_mean_count"] == 2
        assert rows.iloc[0]["negative_mean_count"] == 2
        assert rows.iloc[0]["temporal_ci_negative_count"] == 1
        assert rows.iloc[0]["temporal_ci_includes_zero_count"] == 3

    jja_pr = data[(data["variable"] == "pr") & (data["season"] == "JJA")]
    expected = {
        "original_box": (3, 1, 2, 2),
        "southeast_land": (3, 1, 1, 3),
        "gulf_coast": (2, 2, 2, 2),
    }
    for domain, counts in expected.items():
        row = jja_pr[jja_pr["domain"] == domain].iloc[0]
        actual = (
            row["positive_mean_count"],
            row["negative_mean_count"],
            row["temporal_ci_positive_count"],
            row["temporal_ci_includes_zero_count"],
        )
        assert actual == counts

    annual_pr = data[(data["variable"] == "pr") & (data["season"] == "ANN")]
    original = annual_pr[annual_pr["domain"] == "original_box"].iloc[0]
    land = annual_pr[annual_pr["domain"] == "southeast_land"].iloc[0]
    assert (original["positive_mean_count"], original["negative_mean_count"]) == (4, 0)
    assert (land["positive_mean_count"], land["negative_mean_count"]) == (2, 2)
    assert (annual_pr["temporal_ci_includes_zero_count"] == 4).all()


def test_manuscript_spatial_agreement_counts():
    common = pd.read_csv(ROOT / "docs/phase6_monthly_common_grid.csv.gz")
    direct = common[
        (common["comparison"] == "G6solar - G6sulfur")
        & (common["season"] == "JJA")
    ]
    tas = direct[direct["metric"] == "tasmax_mean"]
    precipitation = direct[direct["metric"] == "pr_mean"]
    assert len(tas) == len(precipitation) == 364
    assert (tas["mean"] < 0).all()
    assert tas.groupby(["positive_count", "negative_count"]).size().to_dict() == {
        (0, 4): 326,
        (1, 3): 38,
    }
    assert precipitation.groupby(
        ["positive_count", "negative_count"]
    ).size().to_dict() == {
        (1, 3): 22,
        (2, 2): 87,
        (3, 1): 212,
        (4, 0): 43,
    }


def test_manuscript_leave_one_out_claims():
    loo = pd.read_csv(ROOT / "docs/phase6_leave_one_model_out.csv")
    direct = loo[loo["comparison"] == "G6solar - G6sulfur"]
    jja_tas = direct[
        (direct["metric"] == "tasmax_mean") & (direct["season"] == "JJA")
    ]
    assert len(jja_tas) == 24
    assert (jja_tas["leave_one_out_mean"] < 0).all()
    assert not jja_tas["sign_changed"].any()
    precipitation = direct[direct["metric"] == "pr_mean"]
    changed = precipitation[precipitation["sign_changed"]]
    assert len(changed) == 15
    assert len(changed[["domain", "season"]].drop_duplicates()) == 14


def test_manuscript_block_length_claims():
    data = pd.read_csv(ROOT / "docs/phase7_block_length_sensitivity.csv")
    assert len(data) == 36
    stable_models = data[data["model"].isin(["CNRM-ESM2-1", "MPI-ESM1-2-LR"])]
    assert (stable_models["interval_classification"] == "below_zero").all()
    ipsl_gulf = data[
        (data["model"] == "IPSL-CM6A-LR") & (data["domain"] == "gulf_coast")
    ].set_index("tested_block_length_years")
    assert ipsl_gulf["interval_classification"].to_dict() == {
        3: "below_zero",
        5: "includes_zero",
        7: "includes_zero",
    }
    ukesm_gulf = data[
        (data["model"] == "UKESM1-0-LL") & (data["domain"] == "gulf_coast")
    ]
    assert (ukesm_gulf["interval_classification"] == "includes_zero").all()


def test_manuscript_documents_and_figure_references_are_complete():
    required = [
        "MANUSCRIPT_EVIDENCE_TABLE.md",
        "MANUSCRIPT_METHODS_SPEC.md",
        "MANUSCRIPT_RESULTS_OUTLINE.md",
        "MANUSCRIPT_FIGURE_PLAN.md",
        "MANUSCRIPT_DAILY_EXTREMES_DECISION.md",
        "MANUSCRIPT_LITERATURE_CROSSCHECK.md",
        "MANUSCRIPT_KEY_RESULTS.csv",
        "MANUSCRIPT_SUPPORT_SUMMARY.md",
    ]
    assert all((ROOT / "docs" / name).is_file() for name in required)
    figure_plan = (ROOT / "docs/MANUSCRIPT_FIGURE_PLAN.md").read_text()
    figures = set(re.findall(r"`([^`]+\.png)`", figure_plan))
    assert figures
    assert all((ROOT / "docs" / name).is_file() for name in figures)
    assert "Phase 5 direct comparison" not in (ROOT / "README.md").read_text()


def test_phase1_to_7_reference_outputs_are_unchanged():
    inventory = json.loads(
        (ROOT / "data/reference_outputs_phase1_7.json").read_text()
    )
    assert len(inventory) >= 35
    for name, expected in inventory.items():
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        assert actual == expected
