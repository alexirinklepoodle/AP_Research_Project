"""
Analysis tools for AP Research data
"""

import csv
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import json

def calculate_stats(scored_file):
    """
    Calculate basic statistics from scored data
    """
    print(f"Calculating statistics from {scored_file}")
    
    try:
        df = pd.read_csv(scored_file)
    except FileNotFoundError:
        print("✗ File not found")
        return None
    
    # Group by model
    model_stats = df.groupby('model_name').agg({
        'score_binary': ['count', 'sum', 'mean'],
        'response_length': ['mean', 'std']
    }).round(3)
    
    # Group by problem type
    type_stats = df.groupby('problem_type').agg({
        'score_binary': ['count', 'sum', 'mean']
    }).round(3)
    
    # Group by model group (RLHF vs non-RLHF)
    group_stats = df.groupby('model_group').agg({
        'score_binary': ['count', 'sum', 'mean'],
        'response_length': ['mean', 'std']
    }).round(3)
    
    # Save statistics
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    
    with open(f'data/processed/stats_{timestamp}.txt', 'w') as f:
        f.write("AP RESEARCH LLM ANALYSIS - STATISTICS\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("1. BY MODEL:\n")
        f.write(str(model_stats) + "\n\n")
        
        f.write("2. BY PROBLEM TYPE:\n")
        f.write(str(type_stats) + "\n\n")
        
        f.write("3. BY ALIGNMENT GROUP (RLHF vs non-RLHF):\n")
        f.write(str(group_stats) + "\n\n")
        
        f.write("4. OVERALL ACCURACY:\n")
        overall_acc = df['score_binary'].mean() * 100
        f.write(f"   {overall_acc:.1f}% correct\n")
    
    print("✓ Statistics calculated and saved")
    return {
        'model_stats': model_stats,
        'type_stats': type_stats,
        'group_stats': group_stats,
        'overall_accuracy': overall_acc
    }

def find_patterns(scored_file):
    """
    Look for patterns in errors for qualitative analysis
    """
    print("Looking for error patterns...")
    
    try:
        df = pd.read_csv(scored_file)
    except FileNotFoundError:
        print("✗ File not found")
        return None
    
    # Get incorrect responses only
    errors = df[df['score_binary'] == 0]
    
    if len(errors) == 0:
        print("No errors found!")
        return None
    
    # Analyze error patterns
    patterns = {
        'error_by_model': errors['model_name'].value_counts().to_dict(),
        'error_by_type': errors['problem_type'].value_counts().to_dict(),
        'error_by_group': errors['model_group'].value_counts().to_dict(),
        
        'avg_length_errors': errors['response_length'].mean(),
        'avg_length_correct': df[df['score_binary'] == 1]['response_length'].mean(),
        
        'common_extracted_answers': errors['extracted_answer'].value_counts().head(10).to_dict()
    }
    
    # Save error patterns for qualitative analysis
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    error_sample_file = f"data/processed/error_sample_{timestamp}.csv"
    
    # Create a sample of errors for manual coding (max 100)
    sample_size = min(100, len(errors))
    error_sample = errors.sample(sample_size if sample_size > 20 else len(errors))
    error_sample.to_csv(error_sample_file, index=False)
    
    # Save patterns to JSON
    patterns_file = f"data/processed/patterns_{timestamp}.json"
    with open(patterns_file, 'w') as f:
        json.dump(patterns, f, indent=2)
    
    print(f"✓ Found {len(errors)} total errors")
    print(f"✓ Sampled {len(error_sample)} errors for qualitative analysis")
    print(f"✓ Error sample saved to: {error_sample_file}")
    print(f"✓ Patterns saved to: {patterns_file}")
    
    return patterns

def create_visualizations(scored_file):
    """
    Create basic visualizations of results
    """
    try:
        df = pd.read_csv(scored_file)
    except FileNotFoundError:
        print("✗ File not found")
        return
    
    # Create visualization directory
    import os
    os.makedirs("visualizations", exist_ok=True)
    
    # 1. Accuracy by model group
    plt.figure(figsize=(10, 6))
    
    group_acc = df.groupby('model_group')['score_binary'].mean() * 100
    bars = plt.bar(group_acc.index, group_acc.values)
    
    plt.title('Accuracy by Alignment Method')
    plt.ylabel('Accuracy (%)')
    plt.ylim(0, 100)
    
    # Add value labels on bars
    for bar, acc in zip(bars, group_acc.values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{acc:.1f}%', ha='center')
    
    plt.tight_layout()
    plt.savefig('visualizations/accuracy_by_group.png', dpi=150)
    plt.close()
    
    # 2. Accuracy by problem type
    plt.figure(figsize=(10, 6))
    
    type_acc = df.groupby('problem_type')['score_binary'].mean() * 100
    bars = plt.bar(type_acc.index, type_acc.values)
    
    plt.title('Accuracy by Problem Type')
    plt.ylabel('Accuracy (%)')
    plt.ylim(0, 100)
    
    for bar, acc in zip(bars, type_acc.values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{acc:.1f}%', ha='center')
    
    plt.tight_layout()
    plt.savefig('visualizations/accuracy_by_type.png', dpi=150)
    plt.close()
    
    print("✓ Visualizations created in 'visualizations/' folder")

if __name__ == "__main__":
    # Test with the most recent scored file
    import glob
    scored_files = glob.glob("data/processed/scored_*.csv")
    if scored_files:
        latest = max(scored_files)
        calculate_stats(latest)
        find_patterns(latest)
        create_visualizations(latest)
    else:
        print("No scored files found. Run scoring_engine.py first.")