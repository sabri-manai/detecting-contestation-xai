"""
Step 05b: applies the second-round adjudication to the reconciled gold, using
the two filled-in decision files:
  outputs/05_reliability_and_reconciliation/tables/adjudication_13_disagreements.xlsx
  outputs/05_reliability_and_reconciliation/tables/representation_boundary_recheck.xlsx

What it does:
1. Loads the reconciled gold (46/76).
2. Applies final adjudicated presence labels for the 13 matched-context
   disagreements (only where the final call actually changes the existing
   label -- most will probably just confirm one side).
3. Applies the representation-boundary recheck: episodes marked
   still_contestation_yn = no get flipped to is_contestation = no (and
   their taxonomy fields cleared); episodes marked yes keep their label,
   with target updated if a different target was given.
4. Writes the updated gold as feasibility_review_sample_GOLD.csv (overwriting
   the file notebooks 05/06 both read), backing up the pre-adjudication
   version first.
5. Prints a summary of exactly what changed, so nothing is silently altered.

After this runs, re-execute notebooks 05 and 06 top to bottom
(jupyter nbconvert --to notebook --execute --inplace ...) to regenerate every
downstream table, figure, and benchmark number -- do NOT hand-edit paper
numbers without doing that first.

Usage:
    cd /Users/sabrimanai/software/uj/detecting-contestation-xai
    .venv/bin/python notebooks/05b_apply_final_adjudication.py
"""
import shutil
from pathlib import Path
from datetime import datetime
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "02_translation_and_feasibility_audit" / "tables"
OUT = ROOT / "outputs" / "05_reliability_and_reconciliation" / "tables"

GOLD_PATH = TABLES / "feasibility_review_sample_GOLD.csv"
ADJ_13_PATH = OUT / "adjudication_13_disagreements.xlsx"
REP_RECHECK_PATH = OUT / "representation_boundary_recheck.xlsx"
DIMS = ["presence", "target", "interaction_act", "grounds", "expected_response"]

for p in (GOLD_PATH, ADJ_13_PATH, REP_RECHECK_PATH):
    if not p.exists():
        raise FileNotFoundError(f"{p} not found.")

gold = pd.read_csv(GOLD_PATH).set_index("__utt_id")
changes = []

# --- 1. Apply the 13-disagreement adjudication -----------------------
adj13 = pd.read_excel(ADJ_13_PATH, sheet_name=0, engine="openpyxl")
adj13["final_adjudicated"] = adj13["final_adjudicated"].astype(str).str.strip().str.lower()
PL_EN = {"tak": "yes", "nie": "no", "yes": "yes", "no": "no"}
adj13["final_adjudicated"] = adj13["final_adjudicated"].map(PL_EN)
n_filled_13 = adj13["final_adjudicated"].notna().sum()
print(f"13-disagreement adjudication: {n_filled_13} / 13 filled in")

for _, r in adj13.iterrows():
    uid, final = r["__utt_id"], r["final_adjudicated"]
    if pd.isna(final) or uid not in gold.index:
        continue
    old = gold.loc[uid, "is_contestation"]
    if old != final:
        changes.append(f"{uid}: is_contestation {old} -> {final} (13-disagreement adjudication)")
        gold.loc[uid, "is_contestation"] = final
        if final == "no":
            gold.loc[uid, "presence"] = "absent"
            for d in ["target", "interaction_act", "grounds", "expected_response"]:
                gold.loc[uid, d] = "n/a"
        # if flipping no->yes, taxonomy fields are left as-is (already blank/n-a);
        # flag for manual follow-up since we have no source to seed them from here.
        elif final == "yes" and pd.isna(gold.loc[uid, "target"]):
            changes.append(f"  !! {uid} flipped to yes but has no taxonomy fields -- fill in manually")

# --- 2. Apply the representation-boundary recheck ---------------------
rep = pd.read_excel(REP_RECHECK_PATH, sheet_name=0, engine="openpyxl")
rep["still_contestation_yn"] = rep["still_contestation_yn"].astype(str).str.strip().str.lower().map(PL_EN)
n_filled_rep = rep["still_contestation_yn"].notna().sum()
print(f"representation-boundary recheck: {n_filled_rep} / 5 filled in")

for _, r in rep.iterrows():
    uid, still = r["__utt_id"], r["still_contestation_yn"]
    if pd.isna(still) or uid not in gold.index:
        continue
    if still == "no":
        old = gold.loc[uid, "is_contestation"]
        if old != "no":
            changes.append(f"{uid}: is_contestation {old} -> no (representation-boundary recheck)")
            gold.loc[uid, "is_contestation"] = "no"
            gold.loc[uid, "presence"] = "absent"
            for d in ["target", "interaction_act", "grounds", "expected_response"]:
                gold.loc[uid, d] = "n/a"
    elif gold.loc[uid, "is_contestation"] == "no":
        # The 13-disagreement adjudication (step 1, above) already excluded
        # this episode on presence grounds. A negative presence call makes
        # the boundary-recheck's target question moot regardless of what
        # that recheck says (see the paper's Construct validity paragraph)
        # -- do not let a "still yes" answer here resurrect a target label
        # on an episode that is not contestation.
        pass
    else:
        new_target = str(r.get("target_if_yes", "")).strip().lower()
        if new_target and new_target not in ("nan", ""):
            old_target = gold.loc[uid, "target"]
            if old_target != new_target:
                changes.append(f"{uid}: target {old_target} -> {new_target} (representation-boundary recheck)")
                gold.loc[uid, "target"] = new_target

# --- 3. Write out, with a backup -------------------------------------
if changes:
    backup = GOLD_PATH.with_name(f"feasibility_review_sample_GOLD.PRE_ADJUDICATION_{datetime.now():%Y%m%d_%H%M%S}.csv")
    shutil.copy(GOLD_PATH, backup)
    print(f"\nbacked up pre-adjudication gold -> {backup.name}")

    gold_out = gold.reset_index()
    gold_out.to_csv(GOLD_PATH, index=False)
    print(f"wrote updated gold -> {GOLD_PATH}")

    print(f"\n{len(changes)} change(s):")
    for c in changes:
        print(" ", c)

    n_yes = int((gold["is_contestation"] == "yes").sum())
    n_total = len(gold)
    print(f"\nnew totals: {n_yes} confirmed / {n_total} audited "
          f"(was 46 / 76 before this adjudication pass)")
    print("\nNEXT: re-run notebooks 05 and 06 top-to-bottom to regenerate every "
          "downstream number, table, and figure before touching the paper text.")
else:
    print("\nNo changes to apply yet -- fill in both files' decision columns and rerun.")
