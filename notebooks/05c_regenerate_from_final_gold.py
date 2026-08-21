"""
Step 05c: regenerates every artifact notebook 05's cells 5-8 normally
produce, but sourced directly from the CURRENT feasibility_review_sample_GOLD.csv --
which now reflects the second-round adjudication (05b: 13-disagreement
adjudication + representation-boundary recheck), not notebook 05's original
coder1/coder2/adj reconciliation.

Do NOT re-run notebook 05 itself after this point -- it would rebuild GOLD.csv
from the original three source files and silently discard the second-round
adjudication. This script is the replacement for notebook 05 cells 5-8, run
against the already-final GOLD.csv.

Usage:
    cd /Users/sabrimanai/software/uj/detecting-contestation-xai
    .venv/bin/python notebooks/05c_regenerate_from_final_gold.py
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "02_translation_and_feasibility_audit" / "tables"
OUT = ROOT / "outputs" / "05_reliability_and_reconciliation"
(OUT / "tables").mkdir(parents=True, exist_ok=True)
(OUT / "figures").mkdir(parents=True, exist_ok=True)

DIMS = ["presence", "target", "interaction_act", "grounds", "expected_response"]

recon = pd.read_csv(TABLES / "feasibility_review_sample_GOLD.csv")
ic = recon["is_contestation"]
n = len(recon)
n_yes = int((ic == "yes").sum())
n_no = int((ic == "no").sum())
precision = n_yes / n
yes = recon[ic == "yes"]
groups = sorted(recon["participant_group"].dropna().unique())
formats = [f for f in ["Descriptive statistics", "SHAP", "LIME", "Anchor", "Counterfactual"]
           if f in set(recon["explanation_format"])]

print(f"reconciled gold (post second-round adjudication): {n} episodes | "
      f"contestation = {n_yes} ({precision:.0%}) | non = {n_no}")
print(f"groups {yes['participant_group'].nunique()}/{len(groups)}  "
      f"formats {yes['explanation_format'].nunique()}/{len(formats)}")

# --- group x format tables --------------------------------------------
gxf = (pd.crosstab(yes["participant_group"], yes["explanation_format"])
       .reindex(index=groups, columns=formats, fill_value=0))
gxf.to_csv(OUT / "confirmed_contestation_group_by_format_reconciled.csv")

audited_gxf = (pd.crosstab(recon["participant_group"], recon["explanation_format"])
               .reindex(index=groups, columns=formats, fill_value=0))
rate_gxf = (gxf / audited_gxf).round(3)
audited_gxf.to_csv(OUT / "tables" / "audited_group_by_format.csv")
rate_gxf.to_csv(OUT / "tables" / "contestation_rate_group_by_format.csv")
# (also write to the top-level OUT dir, matching where main.tex / earlier
#  scripts expect them, since notebook 05 wrote these one level up)
audited_gxf.to_csv(OUT / "audited_group_by_format.csv")
rate_gxf.to_csv(OUT / "contestation_rate_group_by_format.csv")

print("\naudited by group x format:")
print(audited_gxf.assign(Total=audited_gxf.sum(axis=1)))
print("\nconfirmed by group x format:")
print(gxf.assign(Total=gxf.sum(axis=1)))
print("\ngroup totals (audited):", audited_gxf.sum(axis=1).to_dict())
print("group totals (confirmed):", gxf.sum(axis=1).to_dict())

# --- taxonomy distributions + figure -----------------------------------
def dist_gold(col):
    s = yes[col].dropna()
    return s[s != "n/a"].value_counts()

tax_gold = {}
for c in DIMS:
    vc = dist_gold(c).rename("episodes")
    tax_gold[c] = vc
    vc.to_frame().to_csv(OUT / "tables" / f"dist_{c}_reconciled.csv")
    print(f"\n{c} (of {n_yes} reconciled contestation episodes):")
    print(vc.to_frame())

BLUE, INK, MUTED, GRID = "#2a78d6", "#0b0b0b", "#898781", "#e1e0d9"
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Helvetica", "Arial", "DejaVu Sans"],
    "axes.edgecolor": GRID, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": INK, "font.size": 9,
})

def barh_panel(ax, series, title):
    s = series.sort_values(ascending=True)
    ax.barh(s.index, s.values, color=BLUE, height=0.62, edgecolor="white", linewidth=0.6, zorder=3)
    for y, v in enumerate(s.values):
        ax.text(v + max(s.values) * 0.03, y, str(int(v)), va="center", ha="left", fontsize=8, color=INK)
    ax.set_title(title, fontsize=9.5, loc="left", color=INK, pad=6)
    ax.set_xlim(0, max(s.values) * 1.20)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", length=0, labelsize=7.5)
    ax.xaxis.grid(True, color=GRID, linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)

fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.6))
target_labels = {"explanation representation": "Explanation\nrepresentation",
                  "evidence": "Evidence", "input data": "Input data",
                  "reasoning": "Reasoning", "system competence": "System\ncompetence",
                  "prediction": "Prediction"}
barh_panel(axes[0], tax_gold["target"].rename(index=lambda k: target_labels.get(k, k)),
           f"What contestation targets  (n={n_yes})")
barh_panel(axes[1], tax_gold["presence"].rename(index=str.capitalize),
           f"How contestation is expressed  (n={n_yes})")
fig.tight_layout(pad=0.6, w_pad=2.6)
fig.savefig(OUT / "figures" / "taxonomy_distributions.pdf", bbox_inches="tight")
fig.savefig(OUT / "figures" / "taxonomy_distributions.png", dpi=300, bbox_inches="tight")
plt.close(fig)
print("\nwrote taxonomy_distributions.pdf/.png")

# --- group x dimension crosstabs ----------------------------------------
for dim in ["target", "grounds", "interaction_act"]:
    ct = pd.crosstab(yes["participant_group"], yes[dim]).reindex(index=groups, fill_value=0)
    ct.to_csv(OUT / "tables" / f"{dim}_by_group_reconciled.csv")

# --- format x interaction_act crosstab -----------------------------------
ct = pd.crosstab(yes["explanation_format"], yes["interaction_act"]).reindex(index=formats, fill_value=0)
ct.to_csv(OUT / "tables" / "interaction_act_by_format_reconciled.csv")

# --- reliability_summary.json: update the reconciled_gold block only ----
summary_path = OUT / "reliability_summary.json"
summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
summary["reconciled_gold"] = {
    "n": n, "contestation": n_yes, "precision": round(precision, 3),
    "groups": f"{yes['participant_group'].nunique()}/{len(groups)}",
    "formats": f"{yes['explanation_format'].nunique()}/{len(formats)}",
}
summary["second_round_adjudication"] = {
    "note": "Applied after the matched-context reliability recheck and the "
            "representation-boundary recheck (both documented separately); "
            "supersedes the first-round reconciled_gold above.",
    "n_before": 46, "n_after": n_yes,
}
summary_path.write_text(json.dumps(summary, indent=2))
print(f"\nupdated {summary_path}")
print("\nDONE. Now: (1) copy the new taxonomy_distributions.pdf into paper/figures/, "
      "(2) re-run notebook 06 (benchmark) -- it reads GOLD.csv directly and is safe "
      "to re-run as-is, (3) update every count/table in the paper.")
