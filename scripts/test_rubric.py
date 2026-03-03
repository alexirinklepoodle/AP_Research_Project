#!/usr/bin/env python3
"""
Rubric Testing Script
Tests the error classification rubric on the error collection
"""

import pandas as pd
from pathlib import Path

# Paths
ERRORS_DIR = Path(__file__).parent.parent / "errors"
OUTPUT_DIR = Path(__file__).parent.parent / "analysis"

# Pre-coded errors based on open coding analysis
PRELIMINARY_CODES = {
    # Error ID: (Primary, Subtype, Secondary, Confidence, Notes)
    'E001': ('FACTUAL', 'F3', 'LOGIC', 'High', 'Misapplies surface energy concept; confuses mass fraction relationship'),
    'E002': ('FACTUAL', 'F1', 'COMPREHENSION', 'High', 'Hallucinates molecular structure from SMILES; claims acyl chloride'),
    'E003': ('FACTUAL', 'F1', 'PROCEDURAL', 'High', 'Hallucinates reaction mechanism; wrong molecular formula'),
    'E004': ('PROCEDURAL', 'P2', 'LOGIC', 'Medium', 'Wrong boundary condition application in Maxwell equations'),
    'E005': ('RLHF_PATTERN', 'R1', 'LOGIC', 'High', 'Elaborate step-by-step elimination but incorrect; persuasive wrong'),
    'E006': ('FACTUAL', 'F3', 'LOGIC', 'Medium', 'Misapplies continuity concept for minimal polynomials'),
    'E007': ('COMPREHENSION', 'M1', '-', 'High', 'Answers wrong question; says 8 instead of maximal expansion'),
    'E008': ('PROCEDURAL', 'P2', 'CALCULATION', 'High', 'Wrong convergence test application; ratio test misapplied'),
    'E009': ('FACTUAL', 'F3', 'LOGIC', 'Medium', 'Misapplies maximal element concept to preorders'),
    'E010': ('PROCEDURAL', 'P2', 'RLHF_PATTERN', 'Medium', 'Wrong physics derivation; verbose 13-step incorrect reasoning'),
    'E011': ('PROCEDURAL', 'P2', 'RLHF_PATTERN', 'High', 'Elaborate variational calculus but wrong; R1 pattern'),
    'E012': ('FACTUAL', 'F2', '-', 'High', 'Incorrect group theory fact about direct products'),
    'E019': ('RLHF_PATTERN', 'R5', 'LOGIC', 'High', 'Self-corrects from correct (35) to wrong (28); classic R5'),
    'E020': ('COMPREHENSION', 'M2', 'FACTUAL', 'High', 'Reasoning supports Anal (A) but concludes Genital (D)'),
    'E021': ('LOGIC', 'L1', '-', 'High', 'Invalid deduction: ionization ≠ half of total removal energy'),
    'E022': ('LOGIC', 'L1', 'FACTUAL', 'High', 'Contradicts Hooke law F∝x; says 2F gives same x'),
    'E023': ('PROCEDURAL', 'P4', 'CALCULATION', 'Medium', 'Incomplete execution; arithmetic errors throughout'),
    'E024': ('LOGIC', 'L1', 'COMPREHENSION', 'Medium', 'Invalid predicate logic translation; confuses variable roles'),
    'E025': ('COMPREHENSION', 'M1', '-', 'High', 'Misidentifies fallacy definition'),
    'E026': ('LOGIC', 'L1', 'FACTUAL', 'High', 'Contradictory reasoning; says loss increases = overfitting (wrong)'),
    'E027': ('FACTUAL', 'F2', '-', 'High', 'Incorrect medical fact about BRCA mutations'),
    'E028': ('FORMAT', 'O1', '-', 'High', 'Reasoning identifies Swaggart (D) but answer shows A'),
    'E029': ('RLHF_PATTERN', 'R5', 'COMPREHENSION', 'High', 'Starts correct analysis, self-corrects to wrong answer'),
}


def load_error_collection():
    """Load the error collection."""
    df = pd.read_csv(ERRORS_DIR / "error_collection.csv")
    return df


def create_coding_spreadsheet():
    """Create a coding spreadsheet with preliminary codes for testing."""
    df = load_error_collection()
    
    # Add coding columns
    df['primary_category'] = ''
    df['subtype'] = ''
    df['secondary_category'] = ''
    df['confidence'] = ''
    df['coder_notes'] = ''
    
    # Fill in preliminary codes
    for error_id, (primary, subtype, secondary, confidence, notes) in PRELIMINARY_CODES.items():
        mask = df['error_id'] == error_id
        df.loc[mask, 'primary_category'] = primary
        df.loc[mask, 'subtype'] = subtype
        df.loc[mask, 'secondary_category'] = secondary if secondary != '-' else ''
        df.loc[mask, 'confidence'] = confidence
        df.loc[mask, 'coder_notes'] = notes
    
    # Save coding spreadsheet
    output_path = OUTPUT_DIR / "error_coding_spreadsheet.csv"
    df.to_csv(output_path, index=False)
    print(f"Created coding spreadsheet: {output_path}")
    
    return df


def generate_coding_summary(coded_df):
    """Generate summary statistics for coded errors."""
    # Filter to only coded errors
    coded = coded_df[coded_df['primary_category'] != '']
    
    print("\n" + "=" * 60)
    print("PRELIMINARY CODING SUMMARY")
    print("=" * 60)
    print(f"\nTotal errors coded: {len(coded)} / {len(coded_df)}")
    
    # Primary category distribution
    print("\n--- PRIMARY CATEGORY DISTRIBUTION ---")
    primary_dist = coded['primary_category'].value_counts()
    for cat, count in primary_dist.items():
        pct = 100 * count / len(coded)
        print(f"  {cat}: {count} ({pct:.1f}%)")
    
    # Subtype distribution
    print("\n--- SUBTYPE DISTRIBUTION ---")
    subtype_dist = coded['subtype'].value_counts()
    for subtype, count in subtype_dist.items():
        print(f"  {subtype}: {count}")
    
    # Confidence distribution
    print("\n--- CONFIDENCE DISTRIBUTION ---")
    conf_dist = coded['confidence'].value_counts()
    for conf, count in conf_dist.items():
        print(f"  {conf}: {count}")
    
    # RLHF pattern analysis
    print("\n--- RLHF_PATTERN ANALYSIS ---")
    rlhf_errors = coded[coded['primary_category'] == 'RLHF_PATTERN']
    if len(rlhf_errors) > 0:
        print(f"Total RLHF patterns: {len(rlhf_errors)}")
        subtype_dist = rlhf_errors['subtype'].value_counts()
        for subtype, count in subtype_dist.items():
            print(f"  {subtype}: {count}")
        
        # By model group
        print("\nRLHF patterns by model group:")
        group_dist = rlhf_errors['model_group'].value_counts()
        for group, count in group_dist.items():
            print(f"  {group}: {count}")
    
    # Save summary
    summary_path = OUTPUT_DIR / "coding_summary.txt"
    with open(summary_path, 'w') as f:
        f.write("PRELIMINARY CODING SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total errors coded: {len(coded)} / {len(coded_df)}\n\n")
        
        f.write("PRIMARY CATEGORY DISTRIBUTION:\n")
        for cat, count in primary_dist.items():
            pct = 100 * count / len(coded)
            f.write(f"  {cat}: {count} ({pct:.1f}%)\n")
        
        f.write("\n\nSUBTYPE DISTRIBUTION:\n")
        for subtype, count in subtype_dist.items():
            f.write(f"  {subtype}: {count}\n")
    
    print(f"\nSaved summary to: {summary_path}")


def main():
    print("=" * 60)
    print("Error Classification Rubric - Testing Phase")
    print("=" * 60)
    
    # Create coding spreadsheet
    print("\n[1/2] Creating coding spreadsheet with preliminary codes...")
    coded_df = create_coding_spreadsheet()
    
    # Generate summary
    print("\n[2/2] Generating coding summary...")
    generate_coding_summary(coded_df)
    
    print("\n" + "=" * 60)
    print("Rubric testing complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review preliminary codes in: analysis/error_coding_spreadsheet.csv")
    print("2. Code remaining errors using rubric: analysis/error_classification_rubric.md")
    print("3. Refine categories based on inter-rater reliability testing")


if __name__ == "__main__":
    main()
