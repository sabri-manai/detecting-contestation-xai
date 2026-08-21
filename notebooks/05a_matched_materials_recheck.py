"""
Computes raw agreement + Cohen's kappa between the blind matched-context
recheck (matched_materials_recheck.xlsx) and the original primary-annotator
(coder1) presence labels, on the same 36 episodes. Prints disagreements for
adjudication. This is step 05a: it runs after notebook 05's first-pass
reconciliation and before 05b's final adjudication.

Usage:
    cd /Users/sabrimanai/software/uj/detecting-contestation-xai
    .venv/bin/python notebooks/05a_matched_materials_recheck.py [path_to_filled_xlsx]
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "02_translation_and_feasibility_audit" / "tables"
OUT = ROOT / "outputs" / "05_reliability_and_reconciliation" / "tables"

filled_path = Path(sys.argv[1]) if len(sys.argv) > 1 else OUT / "matched_materials_recheck.xlsx"
if not filled_path.exists():
    raise FileNotFoundError(f"{filled_path} not found -- pass the filled file's path as an argument.")

new = pd.read_excel(filled_path, sheet_name=0, engine="openpyxl")
new["presence_yn"] = new["presence_yn"].astype(str).str.strip().str.lower()
PL_EN = {"tak": "yes", "nie": "no", "yes": "yes", "no": "no"}
new["presence_yn"] = new["presence_yn"].map(PL_EN)
new = new[new["presence_yn"].isin(["yes", "no"])].copy()
print(f"episodes completed: {len(new)} / 36")
if len(new) == 0:
    print("Nothing filled in yet -- fill in the presence_yn column and rerun.")
    sys.exit(0)

coder1 = pd.read_csv(TABLES / "feasibility_review_sample_HUMAN.csv").set_index("__utt_id")

def cohens_kappa(a, b):
    cats = sorted(set(a) | set(b)); idx = {c: i for i, c in enumerate(cats)}
    M = np.zeros((len(cats), len(cats)))
    for x, y in zip(a, b): M[idx[x], idx[y]] += 1
    tot = M.sum(); po = np.trace(M) / tot
    pe = sum((M[i, :].sum() / tot) * (M[:, i].sum() / tot) for i in range(len(cats)))
    return (po - pe) / (1 - pe) if pe != 1 else 1.0

rows = []
for _, r in new.iterrows():
    uid = r["__utt_id"]
    if uid not in coder1.index:
        print(f"!! {uid} not found in coder1 -- skipping"); continue
    rows.append({
        "__utt_id": uid,
        "new_recheck": r["presence_yn"],
        "orig_coder1": coder1.loc[uid, "is_contestation"],
        "notes": r.get("notes_optional", ""),
    })
cmp_df = pd.DataFrame(rows)

a = cmp_df["orig_coder1"].tolist()
b = cmp_df["new_recheck"].tolist()
raw = float(np.mean([x == y for x, y in zip(a, b)]))
kappa = cohens_kappa(a, b)

print(f"\nn = {len(cmp_df)}")
print(f"raw agreement = {raw:.1%}")
print(f"Cohen's kappa  = {kappa:.3f}")
print("\nconfusion (rows = original coder1, cols = new matched-materials recheck):")
print(pd.crosstab(cmp_df["orig_coder1"], cmp_df["new_recheck"]))

disagree = cmp_df[cmp_df["orig_coder1"] != cmp_df["new_recheck"]]
print(f"\n{len(disagree)} disagreements:")
print(disagree.to_string(index=False))

cmp_df.to_csv(OUT / "matched_materials_recheck_RESULTS.csv", index=False)
print(f"\nwrote {OUT / 'matched_materials_recheck_RESULTS.csv'}")
