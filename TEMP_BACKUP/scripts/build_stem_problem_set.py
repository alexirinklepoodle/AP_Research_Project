"""
build_stem_problem_set.py
Builds a combined problem set from HLE and MMLU, focused on STEM subjects.
"""

import pandas as pd
import numpy as np
import sqlite3
import csv
import os
from pathlib import Path

# ==================== CONFIGURATION ====================
# Tweak these numbers to control your final dataset size
N_PROBLEMS_HLE = 150   # Total to sample from HLE
N_PROBLEMS_MMLU = 250  # Total to sample from MMLU
TOTAL_TARGET = 350     # Your final problem count (e.g., 350-400)

# Define MMLU STEM subjects (from the "Include" list above)
MMLU_STEM_SUBJECTS = [
    'abstract_algebra', 'college_mathematics', 'elementary_mathematics', 'formal_logic', 'logical_fallacies', 'high_school_mathematics',
    'astronomy', 'college_chemistry', 'college_physics', 'conceptual_physics', 'electrical_engineering', 'high_school_chemistry', 'high_school_physics', 'computer_security',
    'anatomy', 'college_biology', 'college_medicine', 'clinical_knowledge', 'high_school_biology', 'human_aging', 'medical_genetics', 'nutrition', 'professional_medicine', 'virology',
    'college_computer_science', 'high_school_computer_science', 'machine_learning',
    'miscellaneous'
]

# ==================== 1. LOAD & SAMPLE FROM HLE ====================
def load_hle_sample(db_path='path/to/your/hle_database.db', sample_size=N_PROBLEMS_HLE):
    """
    Loads a balanced STEM sample from HLE using logic from your SQL query.
    """
    print(f"Loading {sample_size} STEM problems from HLE...")
    try:
        conn = sqlite3.connect(db_path)
        # This is a Python translation of your main HLE SQL query.
        query = f"""
        WITH quotas AS (
          SELECT * FROM (VALUES
            ('Math', 85),
            ('Physics', 25),
            ('Engineering', 20),
            ('Chemistry', 20),
            ('Biology / Medicine', 25),
            ('Computer Science / Artificial Intelligence', 25)
          ) AS t(category, take)
        ),
        q_norm AS (
          SELECT category, take,
                 LOWER(REPLACE(category, ' ', '')) AS key
          FROM quotas
        ),
        t_norm AS (
          SELECT t.*,
                 LOWER(REPLACE(t.category, ' ', '')) AS key
          FROM test AS t
          WHERE (t.image IS NULL OR t.image = '')
            AND LOWER(REPLACE(t.category, ' ', '')) IN (SELECT key FROM q_norm)
        ),
        ranked AS (
          SELECT t_norm.*,
                 q_norm.take,
                 ROW_NUMBER() OVER (PARTITION BY t_norm.key ORDER BY RANDOM()) AS rn
          FROM t_norm
          JOIN q_norm ON t_norm.key = q_norm.key
        )
        SELECT id, question, answer, answer_type, author_name, rationale, raw_subject, category
        FROM ranked
        WHERE rn <= take
        ORDER BY RANDOM()
        LIMIT {sample_size};
        """
        df_hle = pd.read_sql_query(query, conn)
        conn.close()
        print(f"  ✓ Successfully loaded {len(df_hle)} HLE problems.")
        return df_hle
    except Exception as e:
        print(f"  ✗ Error loading HLE data: {e}")
        return pd.DataFrame()

# ==================== 2. LOAD & FILTER MMLU ====================
def load_mmlu_stem(csv_path='path/to/your/mmlu/all.csv', sample_size=N_PROBLEMS_MMLU, stem_subjects=MMLU_STEM_SUBJECTS):
    """
    Loads MMLU data, filters for STEM subjects, and samples proportionally.
    """
    print(f"Loading ~{sample_size} problems from MMLU STEM subjects...")
    try:
        # Load the MMLU data. Assumes a CSV with columns: 'subject', 'question', 'choices', 'answer'
        df_mmlu = pd.read_csv(csv_path)
        
        # Filter for STEM subjects
        df_mmlu_stem = df_mmlu[df_mmlu['subject'].isin(stem_subjects)].copy()
        print(f"  ✓ Filtered to {len(df_mmlu_stem)} problems across {df_mmlu_stem['subject'].nunique()} STEM subjects.")
        
        # Proportional Sampling: Sample from each subject based on its prevalence
        subject_counts = df_mmlu_stem['subject'].value_counts()
        subject_weights = subject_counts / subject_counts.sum()
        n_per_subject = (subject_weights * sample_size).round().astype(int)
        
        # Ensure we at least take 1 from subjects with small weight and hit our target total
        n_per_subject = n_per_subject.clip(lower=1)
        # Adjust if total is off
        while n_per_subject.sum() != sample_size:
            diff = sample_size - n_per_subject.sum()
            # Add or subtract from the largest subject
            subj = n_per_subject.idxmax() if diff > 0 else n_per_subject.idxmin()
            n_per_subject[subj] += 1 if diff > 0 else -1
        
        # Perform the stratified sample
        sampled_dfs = []
        for subject, n in n_per_subject.items():
            subject_df = df_mmlu_stem[df_mmlu_stem['subject'] == subject]
            if len(subject_df) >= n:
                sampled_dfs.append(subject_df.sample(n, random_state=42))
            else:
                sampled_dfs.append(subject_df) # Take all if not enough
        df_mmlu_sampled = pd.concat(sampled_dfs, ignore_index=True)
        print(f"  ✓ Sampled {len(df_mmlu_sampled)} MMLU problems.")
        return df_mmlu_sampled
    except Exception as e:
        print(f"  ✗ Error loading MMLU data: {e}")
        return pd.DataFrame()

# ==================== 3. FORMAT & COMBINE ====================
def format_for_final(hle_df, mmlu_df):
    """
    Formats HLE and MMLU DataFrames to a common schema and combines them.
    """
    formatted_problems = []
    problem_id = 1
    
    # Format HLE Problems
    for _, row in hle_df.iterrows():
        # Build the full text for a multiple-choice question
        question_text = row['question']
        if pd.notna(row.get('choices')):
            # If HLE has a 'choices' column (check your data)
            question_text += "\n\nOptions:\n" + row['choices']
        # Use rationale as the reference reasoning, or a placeholder
        reasoning = row['rationale'] if pd.notna(row['rationale']) else "Step-by-step solution not provided in dataset."
        
        formatted_problems.append({
            'id': f"H{problem_id:03d}",
            'type': 'hle_' + row['category'].lower().replace(' ', '_').replace('/', '_'),
            'text': question_text,
            'solution': str(row['answer']),
            'reasoning': reasoning,
            'source': 'HLE'
        })
        problem_id += 1
    
    # Format MMLU Problems
    for _, row in mmlu_df.iterrows():
        # MMLU 'choices' is often a string like "['A', 'B', 'C', 'D']" with corresponding labels
        options_text = ""
        if isinstance(row['choices'], str):
            # Simple cleanup - you may need more complex parsing depending on MMLU format
            options_text = "\n\nOptions: " + row['choices']
        
        formatted_problems.append({
            'id': f"M{problem_id:03d}",
            'type': 'mmlu_' + row['subject'],
            'text': row['question'] + options_text,
            'solution': str(row['answer']), # Usually 'A', 'B', 'C', or 'D'
            'reasoning': f"Refer to standard knowledge in {row['subject'].replace('_', ' ')}.",
            'source': 'MMLU'
        })
        problem_id += 1
    
    return pd.DataFrame(formatted_problems)

# ==================== MAIN EXECUTION ====================
def main():
    print("\n" + "="*60)
    print("BUILDING STEM PROBLEM SET FOR AP RESEARCH")
    print("="*60)
    
    # 1. Load the data
    # YOU MUST UPDATE THESE PATHS TO WHERE YOUR DATASETS ARE STORED
    hle_df = load_hle_sample(db_path='path/to/HLE/hle.db', sample_size=N_PROBLEMS_HLE)
    mmlu_df = load_mmlu_stem(csv_path='path/to/MMLU/all.csv', sample_size=N_PROBLEMS_MMLU)
    
    if hle_df.empty and mmlu_df.empty:
        print("Failed to load any data. Please check file paths.")
        return
    
    # 2. Format and combine
    final_df = format_for_final(hle_df, mmlu_df)
    
    # 3. Final shuffle and trim to exact target
    final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)
    if len(final_df) > TOTAL_TARGET:
        final_df = final_df.head(TOTAL_TARGET)
    # Re-assign clean IDs
    final_df['id'] = [f"P{i+1:03d}" for i in range(len(final_df))]
    
    # 4. Save to problems.csv
    output_path = Path('problems') / 'problems.csv'
    final_df.to_csv(output_path, index=False, quoting=csv.QUOTE_ALL) # QUOTE_ALL handles commas in text
    print(f"\n" + "="*60)
    print(f"PROBLEM SET CREATION SUCCESSFUL!")
    print(f"✓ Total Problems: {len(final_df)}")
    print(f"✓ Source Breakout:")
    print(f"     - HLE: {len(final_df[final_df['source']=='HLE'])} problems")
    print(f"     - MMLU: {len(final_df[final_df['source']=='MMLU'])} problems")
    print(f"✓ File Saved: {output_path}")
    print("="*60)
    
    # 5. (Optional) Save a subject summary report
    summary = final_df.groupby(['source', 'type']).size().reset_index(name='count')
    summary.to_csv('problems/problem_set_summary.csv', index=False)
    print("✓ Summary report saved to 'problems/problem_set_summary.csv'")

if __name__ == "__main__":
    main()