#!/usr/bin/env python3
"""
Generate binary TSV for Case Study 2: Cancer Driver Gene Databases.
Compares four curated/computational cancer driver gene databases.

Sources:
  - Vogelstein et al. (2013) Science 339:1546-1558, Table S2A+S2B
  - COSMIC Cancer Gene Census v99 (Sondka et al. 2018, Nat Rev Cancer)
  - OncoKB Cancer Gene List (Chakravarty et al. 2017; Suehnholz et al. 2023)
  - IntOGen Compendium (Martínez-Jiménez et al. 2020, Nat Rev Cancer)

Background universe: N = 20,000 (human protein-coding genes)

Usage:
    python generate_cancer_drivers_tsv.py
"""

import csv
import os
import sys

try:
    import openpyxl
except ImportError:
    print("ERROR: openpyxl required. Install with: pip install openpyxl")
    sys.exit(1)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "2-adatsor")
N_UNIVERSE = 20000

def main():
    # 1. OncoKB Cancer Gene List
    oncokb_path = os.path.join(DATA_DIR, "cancerGeneList.tsv")
    oncokb_genes = set()
    cosmic_genes = set()
    with open(oncokb_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            symbol = row["Hugo Symbol"].strip()
            if symbol:
                oncokb_genes.add(symbol)
            if row.get("COSMIC CGC (v99)", "").strip() == "Yes":
                cosmic_genes.add(symbol)

    # 2. IntOGen drivers
    intogen_path = os.path.join(DATA_DIR, "2024-06-18_IntOGen-Drivers", "Compendium_Cancer_Genes.tsv")
    intogen_genes = set()
    with open(intogen_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if row.get("IS_DRIVER", "").strip() == "True":
                intogen_genes.add(row["SYMBOL"].strip())

    # 3. Vogelstein Table S2A + S2B
    vogelstein_path = os.path.join(DATA_DIR, "NIHMS496129-supplement-Supplementary_Material.xlsx")
    vogelstein_genes = set()
    wb = openpyxl.load_workbook(vogelstein_path, read_only=True)
    for sheet_name in ["Table S2A", "Table S2B"]:
        ws = wb[sheet_name]
        for row in list(ws.iter_rows(values_only=True))[2:]:
            if row[0] and isinstance(row[0], str):
                gene = row[0].strip()
                if gene and gene != "Gene Symbol" and not gene.startswith("Table"):
                    vogelstein_genes.add(gene)
    wb.close()

    # Summary
    print(f"Vogelstein: {len(vogelstein_genes)} genes")
    print(f"COSMIC CGC: {len(cosmic_genes)} genes")
    print(f"OncoKB:     {len(oncokb_genes)} genes")
    print(f"IntOGen:    {len(intogen_genes)} genes")

    # Build binary TSV
    selected = {"Vogelstein": vogelstein_genes, "COSMIC_CGC": cosmic_genes,
                "OncoKB": oncokb_genes, "IntOGen": intogen_genes}
    union = set()
    for s in selected.values():
        union |= s

    all_genes = sorted(union)
    for i in range(N_UNIVERSE - len(union)):
        all_genes.append(f"BG_{i+1:05d}")
    all_genes.sort()

    names = list(selected.keys())
    sets_list = [selected[n] for n in names]

    outpath = os.path.join(SCRIPT_DIR, "dataset_cancer_drivers_4db.tsv")
    with open(outpath, "w") as f:
        f.write("\t".join(["Gene"] + names) + "\n")
        for gene in all_genes:
            f.write("\t".join([gene] + ["1" if gene in s else "0" for s in sets_list]) + "\n")

    print(f"\nWritten: {outpath} ({len(all_genes)} rows)")

    # Pairwise stats
    for i in range(len(names)):
        for j in range(i+1, len(names)):
            inter = len(sets_list[i] & sets_list[j])
            exp = len(sets_list[i]) * len(sets_list[j]) / N_UNIVERSE
            fe = inter / exp if exp > 0 else 0
            oc = inter / min(len(sets_list[i]), len(sets_list[j]))
            print(f"  {names[i]:>12s} ∩ {names[j]:<12s}: obs={inter}, FE={fe:.1f}, OC={oc:.3f}")

    core = vogelstein_genes & cosmic_genes & oncokb_genes & intogen_genes
    print(f"\nCore (all 4): {len(core)} genes")

if __name__ == "__main__":
    main()
