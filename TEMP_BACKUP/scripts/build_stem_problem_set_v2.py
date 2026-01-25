"""
build_stem_problem_set_v2.py
Builds a combined STEM problem set from HLE and MMLU using Hugging Face datasets.
"""

import pandas as pd
from datasets import load_dataset
import csv
from pathlib import Path

# ==================== CONFIGURATION ====================
# Adjust these numbers to control your final dataset
N_PROBLEMS_HLE = 150   # Problems to sample from HLE
N_PROBLEMS_MMLU = 250  # Problems to sample from MMLU STEM subjects
TOTAL_TARGET = 350     # Your final desired problem count

# Define MMLU STEM subjects (We EXCLUDE humanities/social sciences)
MMLU_STEM_SUBJECTS = [
    'abstract_algebra', 'college_mathematics', 'formal_logic', 'logical_fallacies',
    'astronomy', 'college_chemistry', 'college_physics', 'electrical_engineering', 'computer_security',
    'anatomy', 'college_biology', 'college_medicine', 'clinical_knowledge', 'human_aging', 'medical_genetics', 'nutrition', 'professional_medicine', 'virology',
    'college_computer_science', 'machine_learning',
    'miscellaneous'  # Often contains STEM puzzles
]

# ==================== 1. LOAD & SAMPLE FROM HLE ====================
def load_hle_sample(sample_size=N_PROBLEMS_HLE):
    """
    Loads HLE dataset and samples from its predefined STEM categories.
    """
    print(f"Loading HLE dataset and sampling {sample_size} STEM problems...")
    try:
        # Load the full HLE dataset
        ds = load_dataset("cais/hle")
        # Convert to pandas DataFrame for easier manipulation
        df_hle = pd.DataFrame(ds['train'])  # or ds['test'] depending on the split you want
        
        # Define the target STEM categories (from your SQL query)
        target_categories = [
            'Math',
            'Physics',
            'Engineering',
            'Chemistry',
            'Biology / Medicine',
            'Computer Science / Artificial Intelligence'
        ]
        
        # Filter for target categories and questions without images
        df_hle_stem = df_hle[
            (df_hle['category'].isin(target_categories)) & 
            ((df_hle['image'].isna()) | (df_hle['image'] == ''))
        ].copy()
        
        # Additional filter for difficulty if the column exists
        if 'difficulty' in df_hle_stem.columns:
            df_hle_stem = df_hle_stem[
                ~df_hle_stem['difficulty'].isin(['high_school', 'elementary', 'middle_school'])  # Adjust list based on actual values
            ]

        print(f"  ✓ Found {len(df_hle_stem)} potential HLE STEM problems.")
        
        # If we have enough, sample randomly
        if len(df_hle_stem) >= sample_size:
            df_hle_sampled = df_hle_stem.sample(sample_size, random_state=42)
        else:
            print(f"  ⚠ Warning: Only {len(df_hle_stem)} HLE STEM problems available. Taking all.")
            df_hle_sampled = df_hle_stem
        
        return df_hle_sampled
    except Exception as e:
        print(f"  ✗ Error loading HLE data: {e}")
        return pd.DataFrame()

# ==================== 2. LOAD & FILTER MMLU ====================
def load_mmlu_stem(sample_size=N_PROBLEMS_MMLU, stem_subjects=MMLU_STEM_SUBJECTS):
    """
    Loads MMLU data for specified STEM subjects and samples proportionally.
    """
    print(f"Loading MMLU dataset for {len(stem_subjects)} STEM subjects...")
    
    all_mmlu_problems = []
    
    # Load each STEM subject individually and combine
    for subject in stem_subjects:
        try:
            print(f"  Loading subject: {subject}...", end='\r')
            # Load the specific subject
            ds = load_dataset("cais/mmlu", subject)
            # Typically use the 'test' split for evaluation
            df_subject = pd.DataFrame(ds['test'])
            df_subject['subject'] = subject  # Keep track of the subject
            all_mmlu_problems.append(df_subject)
        except Exception as e:
            print(f"  ⚠ Could not load subject '{subject}': {e}")
            continue
    
    if not all_mmlu_problems:
        print("  ✗ Failed to load any MMLU data.")
        return pd.DataFrame()
    
    # Combine all subjects into one DataFrame
    df_mmlu_all = pd.concat(all_mmlu_problems, ignore_index=True)
    print(f"  ✓ Loaded {len(df_mmlu_all)} total problems across {len(all_mmlu_problems)} STEM subjects.")
    
    # Proportional Sampling based on subject frequency
    subject_counts = df_mmlu_all['subject'].value_counts()
    subject_weights = subject_counts / subject_counts.sum()
    n_per_subject = (subject_weights * sample_size).round().astype(int)
    
    # Ensure minimum of 1 per subject and adjust to hit target
    n_per_subject = n_per_subject.clip(lower=1)
    while n_per_subject.sum() != sample_size:
        diff = sample_size - n_per_subject.sum()
        subject_to_adjust = n_per_subject.idxmax() if diff > 0 else n_per_subject.idxmin()
        n_per_subject[subject_to_adjust] += 1 if diff > 0 else -1
    
    # Perform stratified sampling
    sampled_dfs = []
    for subject, n in n_per_subject.items():
        subject_df = df_mmlu_all[df_mmlu_all['subject'] == subject]
        if len(subject_df) >= n:
            sampled_dfs.append(subject_df.sample(n, random_state=42, replace=False))
        else:
            sampled_dfs.append(subject_df)  # Take all if not enough
            print(f"  ⚠ Subject '{subject}' has only {len(subject_df)} problems (wanted {n}).")
    
    df_mmlu_sampled = pd.concat(sampled_dfs, ignore_index=True)
    print(f"  ✓ Sampled {len(df_mmlu_sampled)} MMLU problems.")
    return df_mmlu_sampled

# ==================== 3. FORMAT & COMBINE ====================
def format_problems(hle_df, mmlu_df):
    """
    Formats HLE and MMLU DataFrames to the common schema for problems.csv.
    """
    formatted = []
    problem_id = 1
    
    # Format HLE Problems
    for _, row in hle_df.iterrows():
        # Construct the question text
        question_text = row['question']
        
        # Add answer choices if they exist (HLE might store them differently)
        if 'choices' in row and pd.notna(row['choices']):
            # Format choices if they're in a list
            if isinstance(row['choices'], list):
                options = "\n".join([f"{chr(65+i)}. {choice}" for i, choice in enumerate(row['choices'])])
                question_text += f"\n\nOptions:\n{options}"
        
        # Use rationale if available
        reasoning = row.get('rationale', '')
        if pd.isna(reasoning) or reasoning == '':
            reasoning = "Step-by-step solution not provided in dataset."
        
        formatted.append({
            'id': f"H{problem_id:03d}",
            'type': 'hle_' + str(row.get('category', 'unknown')).lower().replace(' ', '_').replace('/', '_').replace('\\', '_'),
            'text': question_text,
            'solution': str(row.get('answer', '')),
            'reasoning': str(reasoning),
            'source': 'HLE'
        })
        problem_id += 1
    
    # Format MMLU Problems
    for _, row in mmlu_df.iterrows():
        # MMLU typically has 'choices' as a list and 'answer' as an integer (0-3)
        question_text = row['question']
        
        # Format the multiple-choice options
        if 'choices' in row and isinstance(row['choices'], list):
            options = "\n".join([f"{chr(65+i)}. {choice}" for i, choice in enumerate(row['choices'])])
            question_text += f"\n\nOptions:\n{options}"
        
        # Convert numeric answer to letter (A, B, C, D)
        answer_int = row.get('answer', 0)
        if isinstance(answer_int, int) and 0 <= answer_int <= 3:
            solution = chr(65 + answer_int)  # 0->A, 1->B, 2->C, 3->D
        else:
            solution = str(answer_int)
        
        formatted.append({
            'id': f"M{problem_id:03d}",
            'type': 'mmlu_' + row['subject'],
            'text': question_text,
            'solution': solution,
            'reasoning': f"Standard knowledge in {row['subject'].replace('_', ' ')}.",
            'source': 'MMLU'
        })
        problem_id += 1
    
    return pd.DataFrame(formatted)

# ==================== MAIN EXECUTION ====================
def main():
    print("\n" + "="*60)
    print("BUILDING STEM PROBLEM SET FROM HUGGING FACE DATASETS")
    print("="*60)
    
    # 1. Load data from Hugging Face
    hle_df = load_hle_sample(sample_size=N_PROBLEMS_HLE)
    mmlu_df = load_mmlu_stem(sample_size=N_PROBLEMS_MMLU)
    
    if hle_df.empty and mmlu_df.empty:
        print("✗ Failed to load any data. Check your internet connection and library installation.")
        return
    
    print(f"\n✓ Data loaded successfully:")
    print(f"   - HLE: {len(hle_df)} problems")
    print(f"   - MMLU: {len(mmlu_df)} problems")
    
    # 2. Format and combine
    final_df = format_problems(hle_df, mmlu_df)
    
    # 3. Final shuffle and trim to target size
    final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)
    if len(final_df) > TOTAL_TARGET:
        final_df = final_df.head(TOTAL_TARGET)
    
    # Assign clean sequential IDs
    final_df['id'] = [f"P{i+1:04d}" for i in range(len(final_df))]
    
    # 4. Save to problems.csv
    output_path = Path('problems') / 'problems.csv'
    os.makedirs('problems', exist_ok=True)  # Ensure directory exists
    
    # Use quoting to handle commas in questions
    final_df.to_csv(output_path, index=False, quoting=csv.QUOTE_ALL, encoding='utf-8')
    
    # 5. Print summary
    print(f"\n" + "="*60)
    print("PROBLEM SET CREATION COMPLETE!")
    print("="*60)
    print(f"✓ Total Problems: {len(final_df)}")
    print(f"✓ Source Breakdown:")
    
    source_summary = final_df['source'].value_counts()
    for source, count in source_summary.items():
        print(f"   - {source}: {count} problems")
    
    print(f"✓ File saved: {output_path}")
    
    # 6. Save detailed summary
    summary_path = Path('problems') / 'problem_set_summary.csv'
    type_summary = final_df.groupby(['source', 'type']).size().reset_index(name='count')
    type_summary.to_csv(summary_path, index=False)
    print(f"✓ Detailed summary saved: {summary_path}")
    
    # 7. Preview
    print(f"\nFirst 3 problems (preview):")
    print("-" * 40)
    for i, row in final_df.head(3).iterrows():
        print(f"\nID: {row['id']} | Type: {row['type']}")
        print(f"Q: {row['text'][:100]}...")
        print(f"A: {row['solution']}")

if __name__ == "__main__":
    main()