#!/usr/bin/env python3
"""
Generate binary TSV datasets from MSigDB Hallmark GMT file.
Background universe = all 4,383 unique genes across all 50 hallmarks.
Source: Liberzon et al. (2015) Cell Systems 1(6):417-425.

Usage:
    python generate_binary_tsv.py
"""

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GMT_FILE = os.path.join(SCRIPT_DIR, "h.all.v2026.1.Hs.symbols.gmt")

# Dataset 1: Cancer cell cycle & DNA damage pathways (5 sets)
SELECTED_CANCER = [
    "HALLMARK_P53_PATHWAY",
    "HALLMARK_APOPTOSIS",
    "HALLMARK_G2M_CHECKPOINT",
    "HALLMARK_E2F_TARGETS",
    "HALLMARK_DNA_REPAIR",
]

# Dataset 2: Immune/inflammatory signaling pathways (4 sets)
SELECTED_IMMUNE = [
    "HALLMARK_INTERFERON_GAMMA_RESPONSE",
    "HALLMARK_INTERFERON_ALPHA_RESPONSE",
    "HALLMARK_INFLAMMATORY_RESPONSE",
    "HALLMARK_TNFA_SIGNALING_VIA_NFKB",
]


def read_gmt(path):
    """Parse GMT file into dict of pathway_name -> set of genes."""
    pathways = {}
    with open(path, "r") as f:
        for line in f:
            parts = line.strip().split("\t")
            name = parts[0]
            genes = set(g for g in parts[2:] if g.strip())
            pathways[name] = genes
    return pathways


def write_binary_tsv(pathways_dict, selected_names, all_genes_universe, output_path):
    """
    Write binary TSV: rows = all genes in universe, columns = selected pathways.
    Genes not in any selected pathway get all-zero rows (background).
    """
    # Short names for column headers (remove HALLMARK_ prefix)
    short_names = [n.replace("HALLMARK_", "") for n in selected_names]

    # Get selected pathway gene sets
    selected_sets = [pathways_dict[name] for name in selected_names]

    # Sort all genes alphabetically
    all_genes = sorted(all_genes_universe)

    with open(output_path, "w") as f:
        f.write("\t".join(["Gene"] + short_names) + "\n")
        for gene in all_genes:
            row = [gene] + ["1" if gene in s else "0" for s in selected_sets]
            f.write("\t".join(row) + "\n")

    # Stats
    n_total = len(all_genes)
    n_in_any = sum(
        1 for g in all_genes if any(g in s for s in selected_sets)
    )
    print(f"  Written: {output_path}")
    print(f"  Total genes (N): {n_total}")
    print(f"  Genes in ≥1 pathway: {n_in_any}")
    print(f"  Background genes: {n_total - n_in_any}")
    print(f"  Columns: {len(selected_names)}")
    print()

    # Pairwise overlap stats
    for i in range(len(selected_names)):
        for j in range(i + 1, len(selected_names)):
            inter = len(selected_sets[i] & selected_sets[j])
            exp = len(selected_sets[i]) * len(selected_sets[j]) / n_total
            fe = inter / exp if exp > 0 else 0
            print(
                f"  {short_names[i][:20]:>20s} ∩ {short_names[j][:20]:>20s}: "
                f"obs={inter:3d}, exp={exp:5.1f}, FE={fe:5.2f}"
            )
    print()


def main():
    print("Reading GMT file:", GMT_FILE)
    pathways = read_gmt(GMT_FILE)
    print(f"Found {len(pathways)} hallmark gene sets\n")

    # Build universe: all unique genes across ALL 50 hallmarks
    all_genes = set()
    for genes in pathways.values():
        all_genes |= genes
    print(f"Total unique genes across all 50 hallmarks: {len(all_genes)}\n")

    # Verify selected pathways exist
    for name_list, label in [
        (SELECTED_CANCER, "Cancer"),
        (SELECTED_IMMUNE, "Immune"),
    ]:
        for name in name_list:
            if name not in pathways:
                print(f"ERROR: {name} not found in GMT file!")
                return
            print(f"  {name}: {len(pathways[name])} genes")
        print()

    # Generate Dataset 1: Cancer pathways
    print("=" * 60)
    print("DATASET 1: Cancer Cell Cycle & DNA Damage Pathways")
    print("=" * 60)
    out1 = os.path.join(SCRIPT_DIR, "dataset_msigdb_cancer_pathways.tsv")
    write_binary_tsv(pathways, SELECTED_CANCER, all_genes, out1)

    # Generate Dataset 2: Immune signaling pathways
    print("=" * 60)
    print("DATASET 2: Immune & Inflammatory Signaling Pathways")
    print("=" * 60)
    out2 = os.path.join(SCRIPT_DIR, "dataset_msigdb_immune_pathways.tsv")
    write_binary_tsv(pathways, SELECTED_IMMUNE, all_genes, out2)

    print("Done! Import these TSV files in Venn Diagram Lab using")
    print("'Binary Venn (CSV/TSV)' mode (NOT GMT mode).")


if __name__ == "__main__":
    main()
