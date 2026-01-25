"""
build_college_mmlu.py
Builds a COLLEGE-LEVEL STEM problem set from MMLU ONLY.
EXCLUDES high school subjects and humanities/social sciences.
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

# DEFINE COLLEGE-LEVEL STEM SUBJECTS ONLY (EXCLUDE HIGH SCHOOL)
MMLU_COLLEGE_STEM_SUBJECTS = [
    # === MATHEMATICS & FORMAL LOGIC (College Level) ===
    'abstract_algebra',           # Advanced math
    'college_mathematics',        # College-level math
    'formal_logic',               # Advanced logic
    'logical_fallacies',          # Critical thinking
    
    # === PHYSICAL SCIENCES & ENGINEERING (College Level) ===
    'astronomy',                  # College astronomy
    'college_chemistry',          # College chemistry
    'college_physics',            # College physics
    'conceptual_physics',         # Physics concepts
    'electrical_engineering',     # Engineering discipline
    
    # === LIFE SCIENCES & MEDICINE (College/Professional Level) ===
    'anatomy',                    # Medical/college level
    'college_biology',            # College biology
    'college_medicine',           # Medical school level
    'clinical_knowledge',         # Professional medical
    'medical_genetics',           # Advanced biology
    'nutrition',                  # College-level nutrition
    'professional_medicine',      # Medical professional
    'virology',                   # Advanced microbiology
    
    # === COMPUTER SCIENCE & AI (College Level) ===
    'college_computer_science',   # College CS
    'machine_learning',           # Advanced CS/AI
    
    # === OTHER ADVANCED STEM ===
    'miscellaneous',              # Mixed advanced topics
]

# Helper function to categorize subject level
def categorize_subject_level(subject):
    """Categorize subject by difficulty level."""
    if subject.startswith('college_') or subject.startswith('professional_'):
        return 'college'
    elif subject.startswith('high_school_') or subject == 'elementary_mathematics':
        return 'high_school'
    else:
        # Subjects like 'abstract_algebra', 'machine_learning' are advanced
        return 'advanced'

# ==================== LOAD MMLU DATA ====================
def load_mmlu_data():
    """Load MMLU data for college-level STEM subjects only."""
    print("Loading COLLEGE-LEVEL MMLU STEM datasets...")
    print(f"Subjects: {len(MMLU_COLLEGE_STEM_SUBJECTS)} advanced topics")
    all_data = []
    
    for i, subject in enumerate(MMLU_COLLEGE_STEM_SUBJECTS):
        try:
            print(f"  [{i+1}/{len(MMLU_COLLEGE_STEM_SUBJECTS)}] Loading {subject}")
            # Load dataset from Hugging Face
            dataset = load_dataset("cais/mmlu", subject)
            df = pd.DataFrame(dataset['test'])  # Use test split
            df['subject'] = subject
            df['subject_level'] = categorize_subject_level(subject)
            all_data.append(df)
        except Exception as e:
            print(f"    ⚠ Skipping {subject}: {str(e)[:50]}...")
    
    if not all_data:
        print("✗ No data loaded!")
        return pd.DataFrame()
    
    # Combine all data
    combined = pd.concat(all_data, ignore_index=True)
    print(f"✓ Loaded {len(combined)} COLLEGE-LEVEL problems from {len(all_data)} subjects")
    return combined

# ==================== CREATE BALANCED SAMPLE ====================
def create_balanced_sample(df, target_count=TOTAL_PROBLEMS):
    """Create a balanced sample across college-level subjects."""
    if df.empty:
        return df
    
    # Ensure we only have college/advanced level
    if 'subject_level' in df.columns:
        df = df[df['subject_level'].isin(['college', 'advanced'])]
        print(f"✓ Filtered to {len(df)} college/advanced problems")
    
    # Calculate how many from each subject (proportional)
    subject_counts = df['subject'].value_counts()
    proportions = subject_counts / subject_counts.sum()
    
    # Allocate samples - ensure minimum of 2 per subject for statistical significance
    samples_per_subject = (proportions * target_count).round().astype(int)
    samples_per_subject = samples_per_subject.clip(lower=2)  # Min 2 per subject
    
    # Adjust if total is off
    total = samples_per_subject.sum()
    while total != target_count:
        diff = target_count - total
        # Adjust strategically
        if diff > 0:
            # Add to subject with most available problems
            subject = subject_counts.idxmax()
        else:
            # Remove from subject with largest allocation (but keep min 2)
            subject = samples_per_subject[samples_per_subject > 2].idxmax()
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
            print(f"    ⚠ Subject '{subject}' has only {len(subject_df)} problems")
        sampled_data.append(sampled)
    
    result = pd.concat(sampled_data, ignore_index=True)
    print(f"✓ Created balanced sample of {len(result)} COLLEGE-LEVEL problems")
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
        
        # Determine difficulty tag
        subject = row['subject']
        if subject.startswith('college_'):
            level = "College"
        elif subject.startswith('professional_'):
            level = "Professional"
        else:
            level = "Advanced"
        
        # Create problem entry
        problems.append({
            'id': f"P{i+1:04d}",
            'type': f"mmlu_{row['subject']}",
            'level': level,
            'text': question_text,
            'solution': answer,
            'reasoning': f"{level}-level knowledge required in {row['subject'].replace('_', ' ')}.",
            'source': 'MMLU',
            'subject': row['subject']
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
    
    # Create and save detailed summary
    summary = df.groupby(['level', 'type']).size().reset_index(name='count')
    summary_file = Path('problems') / 'problem_set_summary.csv'
    summary.to_csv(summary_file, index=False)
    
    # Also save subject-level summary
    subject_summary = df.groupby('level').agg({
        'type': 'nunique',
        'id': 'count'
    }).reset_index()
    subject_summary.columns = ['Level', 'Unique Subjects', 'Total Problems']
    subject_summary_file = Path('problems') / 'subject_level_summary.csv'
    subject_summary.to_csv(subject_summary_file, index=False)
    
    print(f"\n{'='*60}")
    print("COLLEGE-LEVEL PROBLEM SET CREATION COMPLETE!")
    print(f"{'='*60}")
    print(f"✓ Total Problems: {len(df)}")
    print(f"✓ Subjects: {df['type'].nunique()}")
    print(f"✓ Level Distribution:")
    level_counts = df['level'].value_counts()
    for level, count in level_counts.items():
        print(f"    - {level}: {count} problems")
    print(f"✓ Saved to: {output_file}")
    print(f"✓ Summary: {summary_file}")
    
    # Show preview
    print(f"\nSample Problems (one from each level):")
    print(f"{'-'*40}")
    
    # Get one sample from each level
    for level in df['level'].unique():
        sample = df[df['level'] == level].iloc[0]
        print(f"\n[{level}] ID: {sample['id']}")
        print(f"Type: {sample['type']}")
        print(f"Question: {sample['text'][:80]}...")
        print(f"Answer: {sample['solution']}")
        print(f"{'-'*40}")
    
    return output_file

# ==================== MAIN FUNCTION ====================
def main():
    print("\n" + "="*60)
    print("BUILDING COLLEGE-LEVEL MMLU STEM PROBLEM SET")
    print("="*60)
    print("NOTE: Excluding all high school and elementary level subjects")
    print("Focusing on: college, professional, and advanced STEM only")
    
    # Step 1: Load data
    print("\n1. Loading COLLEGE-LEVEL MMLU datasets...")
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
    print("RESEARCH-READY PROBLEM SET CREATED!")
    print(f"{'='*60}")
    print("✓ All problems are COLLEGE-LEVEL or higher")
    print("✓ NO high school or elementary subjects")
    print("✓ Balanced across advanced STEM disciplines")
    print("✓ Perfect for analyzing RLHF reasoning errors")
    print("\nNext, run: python3 scripts/data_collector.py")
    print("This will test Llama and Mistral on all problems.")

if __name__ == "__main__":
    main()