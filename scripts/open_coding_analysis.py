#!/usr/bin/env python3
"""
Open Coding Analysis for Error Collection
Reads through errors and helps identify patterns for rubric development
"""

import pandas as pd
from pathlib import Path

# Paths
ERRORS_DIR = Path(__file__).parent.parent / "errors"
OUTPUT_DIR = Path(__file__).parent.parent / "analysis"

def load_error_collection():
    """Load the error collection."""
    df = pd.read_csv(ERRORS_DIR / "error_collection.csv")
    return df

def categorize_by_error_patterns():
    """
    Open coding analysis - reading through errors to identify patterns.
    This function displays errors for manual coding and pattern identification.
    """
    df = load_error_collection()
    
    print("=" * 80)
    print("OPEN CODING ANALYSIS - ERROR PATTERN IDENTIFICATION")
    print("=" * 80)
    print(f"\nTotal errors to analyze: {len(df)}\n")
    
    # Group by problem type for systematic analysis
    problem_types = df['problem_type'].unique()
    
    # Create analysis output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    analysis_file = OUTPUT_DIR / "open_coding_notes.md"
    
    with open(analysis_file, 'w') as f:
        f.write("# Open Coding Analysis - Error Pattern Identification\n\n")
        f.write(f"**Total Errors Analyzed:** {len(df)}\n\n")
        f.write("---\n\n")
        
        # Analyze each error in detail
        f.write("## Detailed Error Analysis\n\n")
        
        for idx, row in df.iterrows():
            f.write(f"### {row['error_id']} | {row['model_name']} ({row['model_group']})\n\n")
            f.write(f"**Problem Type:** {row['problem_type']} | **Level:** {row['difficulty_level']}\n\n")
            f.write(f"**Model Answer:** `{row['model_answer']}` | **Correct:** `{row['correct_solution']}`\n\n")
            
            # Truncate problem text if too long
            problem_text = row['problem_text'][:800] + "..." if len(row['problem_text']) > 800 else row['problem_text']
            f.write(f"**Problem:**\n{problem_text}\n\n")
            
            # Truncate response for readability
            response = row['model_response'][:1000] + "..." if len(row['model_response']) > 1000 else row['model_response']
            f.write(f"**Model Response (truncated):**\n{response}\n\n")
            
            f.write("**Initial Coding Notes:** [To be filled during analysis]\n\n")
            f.write("---\n\n")
    
    print(f"Created detailed analysis file: {analysis_file}")
    
    # Create summary statistics for pattern identification
    print("\n" + "=" * 80)
    print("INITIAL PATTERN OBSERVATIONS")
    print("=" * 80)
    
    # Error distribution by model group
    print("\n1. ERROR DISTRIBUTION BY MODEL GROUP:")
    group_dist = df.groupby('model_group').size()
    for group, count in group_dist.items():
        print(f"   {group}: {count} ({100*count/len(df):.1f}%)")
    
    # Error distribution by problem type
    print("\n2. ERROR DISTRIBUTION BY PROBLEM TYPE:")
    type_dist = df.groupby('problem_type').size().sort_values(ascending=False)
    for ptype, count in type_dist.head(10).items():
        print(f"   {ptype}: {count}")
    
    # Error distribution by difficulty
    print("\n3. ERROR DISTRIBUTION BY DIFFICULTY:")
    level_dist = df.groupby('difficulty_level').size().sort_values(ascending=False)
    for level, count in level_dist.items():
        print(f"   {level}: {count}")
    
    # Sample errors from each problem type for coding
    print("\n4. SAMPLE ERRORS FOR OPEN CODING (first from each type):")
    for ptype in type_dist.index[:5]:
        sample = df[df['problem_type'] == ptype].iloc[0]
        print(f"\n   {ptype}:")
        print(f"   - Model: {sample['model_name']} ({sample['model_group']})")
        print(f"   - Answer: {sample['model_answer']} | Correct: {sample['correct_solution']}")
    
    return df

def create_coding_template():
    """Create a template for systematic error coding."""
    template = """# Error Coding Template

## Coding Categories (Emergent from Open Coding)

For each error, code the following:

### Primary Error Category (select one):
- [ ] LOGIC: Logic/Inferential Breakdown
- [ ] FACTUAL: Factual/Knowledge Deficiency  
- [ ] PROCEDURAL: Procedural/Structural Error
- [ ] CALCULATION: Simple Calculation Error
- [ ] COMPREHENSION: Problem Misunderstanding
- [ ] FORMAT: Format/Output Error
- [ ] RLHF_PATTERN: RLHF-associated Pattern
- [ ] OTHER: Other (specify)

### Secondary Error Category (if applicable):
- [ ] Same as above

### Specific Error Subtype:
(Describe the specific nature of the error)

### Confidence Level:
- [ ] High (clear error pattern)
- [ ] Medium (probable error pattern)
- [ ] Low (uncertain classification)

### Notes:
(Any additional observations about the error)

---

## Error Record

**Error ID:** 
**Model:** 
**Problem Type:** 
**Model Answer:** 
**Correct Answer:** 

**Problem Text:**


**Model Response:**


**Coding Decision:**


"""
    
    template_path = OUTPUT_DIR / "coding_template.md"
    with open(template_path, 'w') as f:
        f.write(template)
    
    print(f"\nCreated coding template: {template_path}")

if __name__ == "__main__":
    df = categorize_by_error_patterns()
    create_coding_template()
    print("\n" + "=" * 80)
    print("Open coding analysis complete!")
    print("=" * 80)
