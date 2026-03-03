#!/usr/bin/env python3
"""
Analysis script for AP Research Project
- Scores model responses against reference solutions
- Calculates accuracy rates per model and per problem type
- Performs t-test between RLHF and non-RLHF groups
"""

import pandas as pd
import numpy as np
from scipy import stats
import re
from pathlib import Path
import matplotlib.pyplot as plt

# Paths
DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
PROBLEMS_FILE = Path(__file__).parent.parent / "problems" / "problems.csv"
OUTPUT_DIR = Path(__file__).parent.parent / "logs"

# Model group mapping (as provided by user)
MODEL_GROUPS = {
    "llama3.1:8b": "RLHF",
    "mistral:7b-instruct": "non-RLHF",
    "llama3.2:1b": "RLHF",
    "gemma2:2b": "non-RLHF",
    "llama3.2:3b": "RLHF",
    "codellama:7b": "RLHF",
    "mistral:v0.1": "non-RLHF",
    "neural-chat": "non-RLHF",
}


def extract_answer_from_response(response: str) -> str:
    """
    Extract the final answer from a model's response.
    Looks for patterns like:
    - "the correct answer is: D"
    - "answer is D"
    - "final answer: D"
    - Just a single letter A/B/C/D/E at the end
    """
    response_upper = response.upper()
    
    # Pattern 1: Look for explicit answer statements
    patterns = [
        r"(?:THE\s+)?(?:CORRECT\s+)?ANSWER\s+(?:IS\s+)?(?::?\s*)?([A-E])",
        r"FINAL\s+ANSWER(?:\s+IS)?\s*(?:[:\.]?\s*)?([A-E])",
        r"OPTION\s+([A-E])",
        r"\b([A-E])\b(?:\s*(?:\.|\)|,|\s|$))",
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, response_upper)
        if matches:
            # Return the last match (usually the final conclusion)
            return matches[-1]
    
    # Fallback: look for standalone letters that might be answers
    # Check the last 200 characters for a letter
    end_section = response_upper[-200:]
    letter_matches = re.findall(r'\b([A-E])\b', end_section)
    if letter_matches:
        return letter_matches[-1]
    
    return ""


def score_response(extracted_answer: str, correct_solution) -> bool:
    """
    Compare extracted answer with correct solution.
    Returns True if correct, False otherwise.
    """
    if not extracted_answer:
        return False
    
    # Handle NaN or None solutions
    if pd.isna(correct_solution) or correct_solution is None:
        return False
    
    # Normalize both answers
    extracted = extracted_answer.strip().upper()
    correct = str(correct_solution).strip().upper()
    
    return extracted == correct


def load_and_combine_results():
    """Load all result files and combine into a single dataframe."""
    result_files = list(DATA_DIR.glob("P*_results_*.csv"))
    
    if not result_files:
        raise FileNotFoundError(f"No result files found in {DATA_DIR}")
    
    print(f"Found {len(result_files)} result files:")
    for f in result_files:
        print(f"  - {f.name}")
    
    # Load and combine all result files
    dfs = []
    for f in result_files:
        df = pd.read_csv(f)
        dfs.append(df)
        print(f"  Loaded {len(df)} rows from {f.name}")
    
    combined = pd.concat(dfs, ignore_index=True)
    print(f"\nTotal combined rows: {len(combined)}")
    
    return combined


def load_problems():
    """Load the problems file with reference solutions."""
    problems = pd.read_csv(PROBLEMS_FILE)
    print(f"Loaded {len(problems)} problems from problems.csv")
    return problems


def score_all_responses(results_df: pd.DataFrame, problems_df: pd.DataFrame) -> pd.DataFrame:
    """
    Score all responses against reference solutions.
    Adds 'extracted_answer' and 'is_correct' columns to the results.
    """
    # Merge results with problems to get reference solutions
    merged = results_df.merge(
        problems_df[['id', 'solution', 'type']],
        left_on='problem_id',
        right_on='id',
        how='left',
        suffixes=('', '_ref')
    )
    
    # Score each response
    extracted_answers = []
    is_correct = []
    
    for idx, row in merged.iterrows():
        response = row['response']
        correct_solution = row['solution']
        
        extracted = extract_answer_from_response(response)
        correct = score_response(extracted, correct_solution)
        
        extracted_answers.append(extracted)
        is_correct.append(correct)
    
    merged['extracted_answer'] = extracted_answers
    merged['is_correct'] = is_correct
    
    # Report scoring statistics
    total = len(merged)
    answered = sum(1 for a in extracted_answers if a)
    correct = sum(is_correct)
    
    print(f"\n=== Scoring Summary ===")
    print(f"Total responses: {total}")
    print(f"Responses with extractable answers: {answered} ({100*answered/total:.1f}%)")
    print(f"Correct responses: {correct} ({100*correct/total:.1f}%)")
    
    return merged


def calculate_accuracy_per_model(scored_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate accuracy rates for each model."""
    model_stats = scored_df.groupby(['model_name', 'model_group']).agg(
        total_responses=('problem_id', 'count'),
        correct_responses=('is_correct', 'sum'),
        accuracy=('is_correct', 'mean')
    ).reset_index()
    
    model_stats['accuracy_pct'] = model_stats['accuracy'] * 100
    
    print("\n=== Accuracy Per Model ===")
    print(model_stats[['model_name', 'model_group', 'total_responses', 'accuracy_pct']].to_string(index=False))
    
    return model_stats


def calculate_accuracy_per_problem_type(scored_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate accuracy rates for each problem type."""
    type_stats = scored_df.groupby(['problem_type', 'model_group']).agg(
        total_responses=('problem_id', 'count'),
        correct_responses=('is_correct', 'sum'),
        accuracy=('is_correct', 'mean')
    ).reset_index()
    
    type_stats['accuracy_pct'] = type_stats['accuracy'] * 100
    
    print("\n=== Accuracy Per Problem Type ===")
    print(type_stats[['problem_type', 'model_group', 'total_responses', 'accuracy_pct']].to_string(index=False))
    
    return type_stats


def perform_t_test(scored_df: pd.DataFrame) -> dict:
    """
    Perform independent samples t-test between RLHF and non-RLHF groups.
    Uses per-model accuracy rates as the unit of analysis.
    """
    # Calculate per-model accuracy
    model_accuracy = scored_df.groupby(['model_name', 'model_group'])['is_correct'].mean().reset_index()
    model_accuracy.columns = ['model_name', 'model_group', 'accuracy']
    
    # Separate by group
    rlhf_accuracies = model_accuracy[model_accuracy['model_group'] == 'RLHF']['accuracy'].values
    non_rlhf_accuracies = model_accuracy[model_accuracy['model_group'] == 'non-RLHF']['accuracy'].values
    
    print("\n=== T-Test: RLHF vs non-RLHF ===")
    print(f"RLHF models (n={len(rlhf_accuracies)}): mean={rlhf_accuracies.mean():.4f}, std={rlhf_accuracies.std(ddof=1):.4f}")
    print(f"  Models: {model_accuracy[model_accuracy['model_group'] == 'RLHF']['model_name'].tolist()}")
    print(f"non-RLHF models (n={len(non_rlhf_accuracies)}): mean={non_rlhf_accuracies.mean():.4f}, std={non_rlhf_accuracies.std(ddof=1):.4f}")
    print(f"  Models: {model_accuracy[model_accuracy['model_group'] == 'non-RLHF']['model_name'].tolist()}")
    
    # Perform two-tailed independent samples t-test
    t_statistic, p_value = stats.ttest_ind(rlhf_accuracies, non_rlhf_accuracies, equal_var=False)
    
    print(f"\nT-test results:")
    print(f"  t-statistic: {t_statistic:.4f}")
    print(f"  p-value (two-tailed): {p_value:.4f}")
    
    # Effect size (Cohen's d)
    pooled_std = np.sqrt((rlhf_accuracies.std(ddof=1)**2 + non_rlhf_accuracies.std(ddof=1)**2) / 2)
    cohens_d = (rlhf_accuracies.mean() - non_rlhf_accuracies.mean()) / pooled_std
    print(f"  Cohen's d: {cohens_d:.4f}")
    
    # Interpretation
    if p_value < 0.05:
        significance = "statistically significant (p < 0.05)"
    else:
        significance = "not statistically significant (p >= 0.05)"
    
    print(f"\n  Conclusion: The difference between RLHF and non-RLHF groups is {significance}.")
    
    return {
        'rlhf_mean': rlhf_accuracies.mean(),
        'rlhf_std': rlhf_accuracies.std(ddof=1),
        'rlhf_n': len(rlhf_accuracies),
        'non_rlhf_mean': non_rlhf_accuracies.mean(),
        'non_rlhf_std': non_rlhf_accuracies.std(ddof=1),
        'non_rlhf_n': len(non_rlhf_accuracies),
        't_statistic': t_statistic,
        'p_value': p_value,
        'cohens_d': cohens_d,
    }


def save_results(scored_df: pd.DataFrame, model_stats: pd.DataFrame, 
                 type_stats: pd.DataFrame, t_test_results: dict):
    """Save all analysis results to files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save scored dataframe
    scored_df.to_csv(OUTPUT_DIR / "scored_results.csv", index=False)
    print(f"\nSaved scored results to: {OUTPUT_DIR / 'scored_results.csv'}")
    
    # Save model stats
    model_stats.to_csv(OUTPUT_DIR / "model_accuracy.csv", index=False)
    print(f"Saved model accuracy stats to: {OUTPUT_DIR / 'model_accuracy.csv'}")
    
    # Save problem type stats
    type_stats.to_csv(OUTPUT_DIR / "problem_type_accuracy.csv", index=False)
    print(f"Saved problem type accuracy stats to: {OUTPUT_DIR / 'problem_type_accuracy.csv'}")
    
    # Save t-test results
    t_test_df = pd.DataFrame([t_test_results])
    t_test_df.to_csv(OUTPUT_DIR / "t_test_results.csv", index=False)
    print(f"Saved t-test results to: {OUTPUT_DIR / 't_test_results.csv'}")


def main():
    print("=" * 60)
    print("AP Research Project - Model Analysis")
    print("=" * 60)
    
    # Load data
    print("\n[1/5] Loading data...")
    results_df = load_and_combine_results()
    problems_df = load_problems()
    
    # Score responses
    print("\n[2/5] Scoring responses against reference solutions...")
    scored_df = score_all_responses(results_df, problems_df)
    
    # Calculate accuracy per model
    print("\n[3/5] Calculating accuracy per model...")
    model_stats = calculate_accuracy_per_model(scored_df)
    
    # Calculate accuracy per problem type
    print("\n[4/5] Calculating accuracy per problem type...")
    type_stats = calculate_accuracy_per_problem_type(scored_df)
    
    # Perform t-test
    print("\n[5/5] Performing t-test between RLHF and non-RLHF groups...")
    t_test_results = perform_t_test(scored_df)
    
    # Save results
    print("\n[Saving results...]")
    save_results(scored_df, model_stats, type_stats, t_test_results)
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
