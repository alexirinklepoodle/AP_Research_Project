"""
Error Collection Builder for Qualitative Analysis

This script:
1. Loads scored data and extracts all incorrect responses
2. Creates stratified sample of ~60 errors (by model group and problem type)
3. Formats errors for qualitative coding with problem text, model response, correct solution
"""

import csv
import pandas as pd
import glob
import os
from datetime import datetime
from collections import defaultdict
import random

def load_latest_scored_data():
    """Load the most recent scored data file"""
    scored_files = glob.glob("data/processed/scored_*.csv")
    if not scored_files:
        print("✗ ERROR: No scored data found in data/processed/")
        print("  Run scoring_engine.py first to score the raw data")
        return None
    
    latest = max(scored_files)
    print(f"Loading scored data from: {latest}")
    return pd.read_csv(latest)

def load_problems():
    """Load problem texts from problems.csv"""
    problems = {}
    try:
        with open('problems/problems.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                problems[row['id']] = {
                    'text': row['text'],
                    'solution': row['solution'],
                    'reasoning': row.get('reasoning', ''),
                    'type': row['type'],
                    'source': row.get('source', '')
                }
        print(f"✓ Loaded {len(problems)} problems")
        return problems
    except FileNotFoundError:
        print("✗ ERROR: problems.csv not found")
        return None

def extract_all_errors(df, problems):
    """Extract all incorrect responses with full context"""
    errors = df[df['score_binary'] == 0].copy()
    
    if len(errors) == 0:
        print("✗ No errors found in the data!")
        return None
    
    print(f"\nFound {len(errors)} total errors")
    
    # Add problem text and solution to each error
    errors['problem_text'] = errors['problem_id'].apply(
        lambda pid: problems.get(pid, {}).get('text', 'NOT_FOUND')
    )
    errors['correct_solution'] = errors['problem_id'].apply(
        lambda pid: problems.get(pid, {}).get('solution', 'NOT_FOUND')
    )
    errors['problem_reasoning'] = errors['problem_id'].apply(
        lambda pid: problems.get(pid, {}).get('reasoning', '')
    )
    
    # Breakdown by model group and problem type
    print("\nError breakdown by model group:")
    print(errors['model_group'].value_counts())
    
    print("\nError breakdown by problem type:")
    print(errors['problem_type'].value_counts())
    
    return errors

def create_stratified_sample(errors, target_size=60):
    """
    Create stratified sample of errors by model group and problem type
    
    Args:
        errors: DataFrame with all errors
        target_size: Target number of errors to sample (default 60)
    
    Returns:
        DataFrame with stratified sample
    """
    # Create strata based on model_group and problem_type
    errors['strata'] = errors['model_group'] + '_' + errors['problem_type']
    
    # Count available errors per stratum
    stratum_counts = errors.groupby('strata').size()
    print(f"\nAvailable errors per stratum:")
    print(stratum_counts)
    
    # Calculate sample size per stratum (proportional allocation)
    total_errors = len(errors)
    stratum_samples = {}
    
    for stratum in stratum_counts.index:
        count = stratum_counts[stratum]
        # Proportional allocation
        proportion = count / total_errors
        sample_size = max(1, int(target_size * proportion))
        stratum_samples[stratum] = min(sample_size, count)
    
    # Adjust if we're under target
    current_total = sum(stratum_samples.values())
    if current_total < target_size:
        # Add more to largest strata
        for stratum in stratum_counts.nlargest(target_size - current_total).index:
            available = stratum_counts[stratum]
            current = stratum_samples[stratum]
            stratum_samples[stratum] = min(current + 1, available)
    
    print(f"\nSampling plan:")
    for stratum, size in stratum_samples.items():
        print(f"  {stratum}: {size} errors")
    
    # Sample from each stratum
    sampled_rows = []
    for stratum, size in stratum_samples.items():
        stratum_data = errors[errors['strata'] == stratum]
        sampled = stratum_data.sample(n=size, random_state=42)
        sampled_rows.append(sampled)
    
    sampled_errors = pd.concat(sampled_rows, ignore_index=True)
    print(f"\n✓ Created stratified sample of {len(sampled_errors)} errors")
    
    return sampled_errors

def save_error_collection(errors, all_errors_df, problems):
    """
    Save error collection in format suitable for qualitative coding
    
    Creates:
    1. Full error collection (all errors)
    2. Sampled error collection (~60 errors for initial coding)
    3. Summary statistics
    """
    os.makedirs('data/processed', exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Select columns for qualitative analysis
    columns_for_coding = [
        'problem_id', 'problem_text', 'model_name', 'model_group',
        'response', 'correct_solution', 'problem_reasoning',
        'extracted_answer', 'problem_type', 'score', 'notes'
    ]
    
    # Save full error collection
    full_collection_file = f"data/processed/error_collection_full_{timestamp}.csv"
    all_errors_df[columns_for_coding].to_csv(full_collection_file, index=False)
    print(f"\n✓ Full error collection saved: {full_collection_file}")
    print(f"  Total errors: {len(all_errors_df)}")
    
    # Save sampled error collection
    sample_collection_file = f"data/processed/error_collection_sample_{timestamp}.csv"
    errors[columns_for_coding].to_csv(sample_collection_file, index=False)
    print(f"✓ Sampled error collection saved: {sample_collection_file}")
    print(f"  Sampled errors: {len(errors)}")
    
    # Create a coding-ready format with cleaner layout
    coding_file = f"data/processed/error_collection_coding_{timestamp}.csv"
    
    with open(coding_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'error_id', 'problem_id', 'model_group', 'model_name', 
            'problem_type', 'problem_text', 'model_response', 
            'correct_solution', 'extracted_answer', 'coder_notes',
            'primary_error_type', 'secondary_error_type', 'confidence'
        ])
        
        for idx, row in errors.iterrows():
            error_id = f"E{idx+1:04d}"
            writer.writerow([
                error_id,
                row['problem_id'],
                row['model_group'],
                row['model_name'],
                row['problem_type'],
                row['problem_text'],
                row['response'],
                row['correct_solution'],
                row['extracted_answer'],
                '',  # coder_notes - to be filled during coding
                '',  # primary_error_type - to be filled during coding
                '',  # secondary_error_type - to be filled during coding
                ''   # confidence - to be filled during coding
            ])
    
    print(f"✓ Coding-ready file saved: {coding_file}")
    
    # Save summary statistics
    summary_file = f"data/processed/error_summary_{timestamp}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("ERROR COLLECTION SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Generated: {timestamp}\n\n")
        
        f.write("TOTAL ERRORS\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total incorrect responses: {len(all_errors_df)}\n\n")
        
        f.write("SAMPLED ERRORS (for qualitative coding)\n")
        f.write("-" * 40 + "\n")
        f.write(f"Sample size: {len(errors)}\n\n")
        
        f.write("By Model Group:\n")
        f.write(all_errors_df['model_group'].value_counts().to_string())
        f.write("\n\n")
        
        f.write("By Problem Type:\n")
        f.write(all_errors_df['problem_type'].value_counts().to_string())
        f.write("\n\n")
        
        f.write("By Model:\n")
        f.write(all_errors_df['model_name'].value_counts().to_string())
        f.write("\n\n")
        
        f.write("STRATIFICATION\n")
        f.write("-" * 40 + "\n")
        all_errors_df['strata'] = all_errors_df['model_group'] + '_' + all_errors_df['problem_type']
        f.write("Full population:\n")
        f.write(all_errors_df['strata'].value_counts().to_string())
        f.write("\n\n")
        
        errors['strata'] = errors['model_group'] + '_' + errors['problem_type']
        f.write("Sample distribution:\n")
        f.write(errors['strata'].value_counts().to_string())
        f.write("\n")
    
    print(f"✓ Summary saved: {summary_file}")
    
    return {
        'full_collection': full_collection_file,
        'sample_collection': sample_collection_file,
        'coding_file': coding_file,
        'summary': summary_file
    }

def build_error_collection(target_sample_size=60):
    """
    Main function to build error collection for qualitative analysis
    
    Args:
        target_sample_size: Target number of errors to sample (default 60)
    
    Returns:
        Dictionary with file paths to created collections
    """
    print("=" * 60)
    print("ERROR COLLECTION BUILDER")
    print("=" * 60)
    
    # Load data
    df = load_latest_scored_data()
    if df is None:
        return None
    
    problems = load_problems()
    if problems is None:
        return None
    
    # Extract all errors
    all_errors = extract_all_errors(df, problems)
    if all_errors is None:
        return None
    
    # Create stratified sample
    sampled_errors = create_stratified_sample(all_errors, target_sample_size)
    
    # Save collections
    output_files = save_error_collection(sampled_errors, all_errors, problems)
    
    print("\n" + "=" * 60)
    print("✓ ERROR COLLECTION COMPLETE")
    print("=" * 60)
    print(f"\nNext steps:")
    print(f"1. Open {output_files['coding_file']} for qualitative coding")
    print(f"2. Read through errors and develop initial rubric categories")
    print(f"3. Use qualitative_rubric.py to formalize your coding scheme")
    
    return output_files

if __name__ == "__main__":
    # Build error collection with default sample size of 60
    build_error_collection(target_sample_size=60)
