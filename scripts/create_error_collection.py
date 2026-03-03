#!/usr/bin/env python3
"""
Error Collection Script for AP Research Project
- Identifies all incorrect responses
- Samples ~80 errors stratified by model group and problem type
- Creates error collection with problem text, model response, and correct solution
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
LOGS_DIR = Path(__file__).parent.parent / "logs"
PROBLEMS_FILE = Path(__file__).parent.parent / "problems" / "problems.csv"
OUTPUT_DIR = Path(__file__).parent.parent / "errors"

# Target sample size
TARGET_SAMPLE_SIZE = 80


def load_scored_results() -> pd.DataFrame:
    """Load the scored results from analysis."""
    scored_file = LOGS_DIR / "scored_results.csv"
    df = pd.read_csv(scored_file)
    print(f"Loaded {len(df)} scored responses")
    return df


def load_problems() -> pd.DataFrame:
    """Load problems file for problem text."""
    problems = pd.read_csv(PROBLEMS_FILE)
    return problems


def identify_all_errors(scored_df: pd.DataFrame) -> pd.DataFrame:
    """Filter to only incorrect responses."""
    errors = scored_df[scored_df['is_correct'] == False].copy()
    print(f"\n=== Error Identification ===")
    print(f"Total errors: {len(errors)} out of {len(scored_df)} responses ({100*len(errors)/len(scored_df):.1f}%)")
    
    # Show error distribution by group
    print("\nErrors by model group:")
    group_errors = errors.groupby('model_group').size()
    for group, count in group_errors.items():
        print(f"  {group}: {count}")
    
    return errors


def stratified_sample(errors_df: pd.DataFrame, target_size: int = 80) -> pd.DataFrame:
    """
    Sample errors stratified by model_group and problem_type.
    Uses proportional allocation based on error distribution.
    """
    print(f"\n=== Stratified Sampling ===")
    print(f"Target sample size: {target_size}")
    
    # Create strata by model_group and problem_type
    errors_df['strata'] = errors_df['model_group'] + '_' + errors_df['problem_type']
    
    # Count errors per stratum
    stratum_counts = errors_df.groupby('strata').size().reset_index(name='count')
    stratum_counts['proportion'] = stratum_counts['count'] / stratum_counts['count'].sum()
    stratum_counts['target_sample'] = (stratum_counts['proportion'] * target_size).round().astype(int)
    
    # Ensure at least 1 from each stratum if possible, adjust to hit target
    stratum_counts['target_sample'] = stratum_counts['target_sample'].clip(lower=1)
    
    # Adjust to hit exact target
    current_sum = stratum_counts['target_sample'].sum()
    if current_sum != target_size:
        # Adjust the largest strata
        diff = target_size - current_sum
        max_idx = stratum_counts['count'].idxmax()
        stratum_counts.loc[max_idx, 'target_sample'] += diff
    
    print(f"\nStratified allocation:")
    sampled_dfs = []
    
    for _, row in stratum_counts.iterrows():
        strata = row['strata']
        n_sample = row['target_sample']
        
        strata_errors = errors_df[errors_df['strata'] == strata]
        
        if len(strata_errors) <= n_sample:
            # Take all if fewer than sample size
            sampled = strata_errors
        else:
            # Random sample
            sampled = strata_errors.sample(n=n_sample, random_state=42)
        
        sampled_dfs.append(sampled)
        group, ptype = strata.split('_', 1)
        print(f"  {group:12} | {ptype:30} | sampled {len(sampled):2} of {len(strata_errors):3}")
    
    sampled_df = pd.concat(sampled_dfs, ignore_index=True)
    print(f"\nTotal sampled: {len(sampled_df)}")
    
    return sampled_df


def create_error_collection(sampled_df: pd.DataFrame, problems_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create error collection with problem text, model response, and correct solution.
    """
    print(f"\n=== Creating Error Collection ===")
    
    # Merge with problems to get full problem text
    collection = sampled_df.merge(
        problems_df[['id', 'text', 'solution', 'type', 'level']],
        left_on='problem_id',
        right_on='id',
        how='left',
        suffixes=('', '_ref')
    )
    
    # Select and rename columns for the error collection
    error_collection = collection[[
        'problem_id',
        'problem_type',
        'level',
        'model_name',
        'model_group',
        'text',  # Problem text
        'response',  # Model response
        'extracted_answer',  # What the model answered
        'solution',  # Correct solution
        'response_time_seconds',
        'timestamp'
    ]].copy()
    
    # Rename for clarity
    error_collection.columns = [
        'problem_id',
        'problem_type',
        'difficulty_level',
        'model_name',
        'model_group',
        'problem_text',
        'model_response',
        'model_answer',
        'correct_solution',
        'response_time_sec',
        'timestamp'
    ]
    
    # Add error ID
    error_collection['error_id'] = [f"E{i+1:03d}" for i in range(len(error_collection))]
    
    # Reorder columns
    cols = ['error_id', 'problem_id', 'problem_type', 'difficulty_level', 
            'model_name', 'model_group', 'problem_text', 'model_answer', 
            'correct_solution', 'model_response', 'response_time_sec', 'timestamp']
    error_collection = error_collection[cols]
    
    print(f"Created error collection with {len(error_collection)} errors")
    
    # Show distribution
    print("\nError collection distribution:")
    print("By model group:")
    print(error_collection['model_group'].value_counts().to_string())
    print("\nBy problem type (top 10):")
    print(error_collection['problem_type'].value_counts().head(10).to_string())
    
    return error_collection


def save_error_collection(error_collection: pd.DataFrame):
    """Save error collection to files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save full CSV
    csv_path = OUTPUT_DIR / "error_collection.csv"
    error_collection.to_csv(csv_path, index=False)
    print(f"\nSaved error collection to: {csv_path}")
    
    # Save summary statistics
    summary_path = OUTPUT_DIR / "error_collection_summary.txt"
    with open(summary_path, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("ERROR COLLECTION SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"Total errors in collection: {len(error_collection)}\n\n")
        
        f.write("DISTRIBUTION BY MODEL GROUP:\n")
        f.write("-" * 40 + "\n")
        group_dist = error_collection['model_group'].value_counts()
        for group, count in group_dist.items():
            f.write(f"  {group}: {count} ({100*count/len(error_collection):.1f}%)\n")
        
        f.write("\n\nDISTRIBUTION BY PROBLEM TYPE:\n")
        f.write("-" * 40 + "\n")
        type_dist = error_collection['problem_type'].value_counts()
        for ptype, count in type_dist.items():
            f.write(f"  {ptype}: {count}\n")
        
        f.write("\n\nDISTRIBUTION BY MODEL:\n")
        f.write("-" * 40 + "\n")
        model_dist = error_collection['model_name'].value_counts()
        for model, count in model_dist.items():
            f.write(f"  {model}: {count}\n")
        
        f.write("\n\nDISTRIBUTION BY DIFFICULTY LEVEL:\n")
        f.write("-" * 40 + "\n")
        level_dist = error_collection['difficulty_level'].value_counts()
        for level, count in level_dist.items():
            f.write(f"  {level}: {count}\n")
    
    print(f"Saved summary to: {summary_path}")
    
    # Save a readable text version with first few errors as examples
    examples_path = OUTPUT_DIR / "error_examples.txt"
    with open(examples_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("ERROR COLLECTION - SAMPLE ERRORS\n")
        f.write("=" * 80 + "\n\n")
        
        for idx, row in error_collection.head(5).iterrows():
            f.write(f"{'='*80}\n")
            f.write(f"Error ID: {row['error_id']}\n")
            f.write(f"Problem ID: {row['problem_id']}\n")
            f.write(f"Model: {row['model_name']} ({row['model_group']})\n")
            f.write(f"Problem Type: {row['problem_type']} ({row['difficulty_level']})\n")
            f.write(f"Model Answer: {row['model_answer']}\n")
            f.write(f"Correct Solution: {row['correct_solution']}\n")
            f.write(f"{'-'*80}\n")
            f.write(f"PROBLEM TEXT:\n{row['problem_text']}\n")
            f.write(f"{'-'*80}\n")
            f.write(f"MODEL RESPONSE (truncated to 500 chars):\n{row['model_response'][:500]}...\n")
            f.write("\n\n")
    
    print(f"Saved examples to: {examples_path}")


def main():
    print("=" * 60)
    print("Error Collection Creation")
    print("=" * 60)
    
    # Load data
    print("\n[1/4] Loading data...")
    scored_df = load_scored_results()
    problems_df = load_problems()
    
    # Identify all errors
    print("\n[2/4] Identifying all errors...")
    errors_df = identify_all_errors(scored_df)
    
    # Stratified sampling
    print("\n[3/4] Sampling errors (stratified)...")
    sampled_df = stratified_sample(errors_df, TARGET_SAMPLE_SIZE)
    
    # Create error collection
    print("\n[4/4] Creating error collection...")
    error_collection = create_error_collection(sampled_df, problems_df)
    
    # Save results
    print("\n[Saving...]")
    save_error_collection(error_collection)
    
    print("\n" + "=" * 60)
    print("Error collection creation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
