"""
build_mmlu_problems.py
Builds a STEM problem set from MMLU ONLY (no HLE authentication needed).
"""

import pandas as pd
from datasets import load_dataset
import csv
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ==================== CONFIGURATION ====================
TOTAL_PROBLEMS = 350  # Your final problem count

# DEFINE STEM SUBJECTS ONLY (exclude humanities/social sciences)
MMLU_STEM_SUBJECTS = [
    # Mathematics & Formal Logic
    'abstract_algebra', 'college_mathematics', 'elementary_mathematics', 
    'formal_logic', 'logical_fallacies', 'high_school_mathematics',
    
    # Physical Sciences & Engineering
    'astronomy', 'college_chemistry', 'college_physics', 
    'conceptual_physics', 'electrical_engineering', 'high_school_chemistry', 
    'high_school_physics', 'computer_security',
    
    # Life Sciences & Medicine
    'anatomy', 'college_biology', 'college_medicine', 'clinical_knowledge', 
    'high_school_biology', 'human_aging', 'medical_genetics', 
    'nutrition', 'professional_medicine', 'virology',
    
    # Computer Science & AI
    'college_computer_science', 'high_school_computer_science', 'machine_learning',
    
    # Other STEM
    'miscellaneous'
]

# ==================== LOAD MMLU DATA ====================
def load_mmlu_data():
    """Load MMLU data for all STEM subjects."""
    print("Loading MMLU STEM datasets...")
    all_data = []
    
    for i, subject in enumerate(MMLU_STEM_SUBJECTS):
        try:
            print(f"  [{i+1}/{len(MMLU_STEM_SUBJECTS)}] Loading {subject}")
            # Load dataset from Hugging Face
            dataset = load_dataset("cais/mmlu", subject)
            df = pd.DataFrame(dataset['test'])  # Use test split
            df['subject'] = subject
            all_data.append(df)
        except Exception as e:
            print(f"    ⚠ Skipping {subject}: {str(e)[:50]}...")
    
    if not all_data:
        print("✗ No data loaded!")
        return pd.DataFrame()
    
    # Combine all data
    combined = pd.concat(all_data, ignore_index=True)
    print(f"✓ Loaded {len(combined)} total problems from {len(all_data)} subjects")
    return combined

# ==================== CREATE BALANCED SAMPLE ====================
def create_balanced_sample(df, target_count=TOTAL_PROBLEMS):
    """Create a balanced sample across subjects."""
    if df.empty:
        return df
    
    # Calculate how many from each subject (proportional)
    subject_counts = df['subject'].value_counts()
    proportions = subject_counts / subject_counts.sum()
    
    # Allocate samples
    samples_per_subject = (proportions * target_count).round().astype(int)
    
    # Adjust if total is off
    total = samples_per_subject.sum()
    while total != target_count:
        diff = target_count - total
        # Adjust the largest subject
        subject = samples_per_subject.idxmax() if diff > 0 else samples_per_subject.idxmin()
        samples_per_subject[subject] += 1 if diff > 0 else -1
        total = samples_per_subject.sum()
    
    # Sample from each subject
    sampled_data = []
    for subject, n in samples_per_subject.items():
        subject_df = df[df['subject'] == subject]
        if len(subject_df) >= n:
            sampled = subject_df.sample(n, random_state=42)
        else:
            sampled = subject_df  # Take all if not enough
        sampled_data.append(sampled)
    
    result = pd.concat(sampled_data, ignore_index=True)
    print(f"✓ Created balanced sample of {len(result)} problems")
    return result

# ==================== FORMAT FOR CSV ====================
def format_for_csv(df):
    """Format MMLU data for our problems.csv format."""
    problems = []
    
    for i, row in df.iterrows():
        # Build question with options
        question_text = row['question']
        
        # Add multiple choice options if available
        if 'choices' in row and isinstance(row['choices'], list):
            options = "\n".join([f"{chr(65+j)}. {choice}" for j, choice in enumerate(row['choices'])])
            question_text += f"\n\nOptions:\n{options}"
        
        # Convert answer from number (0-3) to letter (A-D)
        answer_num = row.get('answer', 0)
        if isinstance(answer_num, int) and 0 <= answer_num <= 3:
            answer = chr(65 + answer_num)  # 0->A, 1->B, etc.
        else:
            answer = str(answer_num)
        
        # Create problem entry
        problems.append({
            'id': f"P{i+1:04d}",
            'type': f"mmlu_{row['subject']}",
            'text': question_text,
            'solution': answer,
            'reasoning': f"Requires knowledge of {row['subject'].replace('_', ' ')}.",
            'source': 'MMLU'
        })
    
    return pd.DataFrame(problems)

# ==================== SAVE RESULTS ====================
def save_results(df):
    """Save the problem set and summary."""
    # Create directories
    os.makedirs('problems', exist_ok=True)
    
    # Save main CSV
    output_file = Path('problems') / 'problems.csv'
    df.to_csv(output_file, index=False, quoting=csv.QUOTE_ALL, encoding='utf-8')
    
    # Create and save summary
    summary = df.groupby(['source', 'type']).size().reset_index(name='count')
    summary_file = Path('problems') / 'problem_set_summary.csv'
    summary.to_csv(summary_file, index=False)
    
    print(f"\n{'='*60}")
    print("PROBLEM SET CREATION COMPLETE!")
    print(f"{'='*60}")
    print(f"✓ Total Problems: {len(df)}")
    print(f"✓ Subjects: {df['type'].nunique()}")
    print(f"✓ Saved to: {output_file}")
    print(f"✓ Summary: {summary_file}")
    
    # Show preview
    print(f"\nSample Problem:")
    print(f"{'-'*40}")
    sample = df.iloc[0]
    print(f"ID: {sample['id']}")
    print(f"Type: {sample['type']}")
    print(f"Question: {sample['text'][:100]}...")
    print(f"Answer: {sample['solution']}")
    
    return output_file

# ==================== MAIN FUNCTION ====================
def main():
    print("\n" + "="*60)
    print("BUILDING MMLU STEM PROBLEM SET")
    print("="*60)
    
    # Step 1: Load data
    print("\n1. Loading MMLU datasets...")
    mmlu_data = load_mmlu_data()
    if mmlu_data.empty:
        print("Failed to load any data. Check internet connection.")
        return
    
    # Step 2: Create balanced sample
    print("\n2. Creating balanced sample...")
    sampled_data = create_balanced_sample(mmlu_data, TOTAL_PROBLEMS)
    
    # Step 3: Format for CSV
    print("\n3. Formatting problems...")
    formatted_problems = format_for_csv(sampled_data)
    
    # Step 4: Save
    print("\n4. Saving results...")
    save_results(formatted_problems)
    
    print(f"\n{'='*60}")
    print("READY FOR DATA COLLECTION!")
    print(f"{'='*60}")
    print("Next, run: python3 scripts/data_collector.py")
    print("This will test Llama and Mistral on all problems.")

if __name__ == "__main__":
    main()