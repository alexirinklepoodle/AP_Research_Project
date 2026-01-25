"""
build_hle_problems.py - FIXED VERSION
Builds a STEM problem set from Humanity's Last Exam (HLE).
Uses current Hugging Face authentication method.
"""

import pandas as pd
from datasets import load_dataset
import csv
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ==================== CONFIGURATION ====================
TOTAL_HLE_PROBLEMS = 150  # Number of HLE problems to sample
HLE_STEM_CATEGORIES = [
    'Math',
    'Physics', 
    'Engineering',
    'Chemistry',
    'Biology / Medicine',
    'Computer Science / Artificial Intelligence'
]

# ==================== CHECK AUTHENTICATION ====================
def check_hf_auth():
    """Check if Hugging Face token is available."""
    token = os.environ.get('HF_TOKEN') or os.environ.get('HUGGINGFACE_TOKEN')
    if token:
        print(f"✓ HF_TOKEN found ({token[:10]}...)")
        return token
    else:
        print("⚠ No HF_TOKEN found in environment variables.")
        print("ℹ To set it: export HF_TOKEN='your_token_here'")
        return None

# ==================== LOAD HLE DATA ====================
def load_hle_data(token=None, sample_size=TOTAL_HLE_PROBLEMS):
    """
    Load HLE dataset with authentication - FIXED for new datasets library.
    """
    print(f"Loading HLE dataset (requires authentication)...")
    
    try:
        # Method 1: Pass token directly (current method)
        if token:
            print(f"  Using token authentication...")
            # Try multiple ways - newer versions use 'token', older used 'use_auth_token'
            try:
                dataset = load_dataset("cais/hle", token=token)
            except TypeError:
                # Fallback for older versions
                dataset = load_dataset("cais/hle", use_auth_token=token)
        else:
            # Method 2: Will use cached credentials if available
            print(f"  Trying to load with cached credentials...")
            try:
                dataset = load_dataset("cais/hle")
            except Exception as e:
                print(f"  Authentication failed: {e}")
                return pd.DataFrame()
        
        # Check which split is available
        available_splits = list(dataset.keys())
        print(f"  Available splits: {available_splits}")
        
        # Use 'train' if available, otherwise first split
        split_to_use = 'train' if 'train' in available_splits else available_splits[0]
        df_hle = pd.DataFrame(dataset[split_to_use])
        
        print(f"✓ Loaded {len(df_hle)} HLE problems from '{split_to_use}' split")
        
        # Filter for STEM categories
        df_hle_stem = df_hle[df_hle['category'].isin(HLE_STEM_CATEGORIES)].copy()
        print(f"✓ Filtered to {len(df_hle_stem)} STEM problems")
        
        # Filter out questions with images (if image field exists)
        if 'image' in df_hle_stem.columns:
            df_hle_stem = df_hle_stem[(df_hle_stem['image'].isna()) | (df_hle_stem['image'] == '')]
            print(f"✓ Further filtered to {len(df_hle_stem)} text-only STEM problems")
        
        # Sample the desired number
        if len(df_hle_stem) >= sample_size:
            df_hle_sampled = df_hle_stem.sample(sample_size, random_state=42)
            print(f"✓ Sampled {sample_size} HLE problems")
        else:
            print(f"⚠ Only {len(df_hle_stem)} STEM problems available. Taking all.")
            df_hle_sampled = df_hle_stem
        
        return df_hle_sampled
        
    except Exception as e:
        print(f"✗ Error loading HLE: {str(e)[:200]}")
        
        # Check for specific access errors
        if "gated" in str(e).lower() or "access" in str(e).lower():
            print("\n🔒 HLE ACCESS REQUIRED:")
            print("   HLE is a gated dataset. Even with a token, you need explicit access.")
            print("   1. Visit: https://huggingface.co/datasets/cais/hle")
            print("   2. Click 'Agree and Access' or 'Request Access'")
            print("   3. Fill out the brief form (academic use is usually approved)")
            print("   4. Wait for email confirmation (can take up to 24 hours)")
            print("\n   In the meantime, you can continue with MMLU-only dataset.")
        
        return pd.DataFrame()

# ==================== FORMAT HLE PROBLEMS ====================
def format_hle_problems(df):
    """Format HLE problems to match our CSV format."""
    if df.empty:
        return df
    
    problems = []
    
    for i, row in df.iterrows():
        # Build the question text
        question_text = str(row['question']) if pd.notna(row.get('question')) else ""
        
        # Add answer choices if available
        if 'choices' in row and pd.notna(row.get('choices')):
            choices = row['choices']
            if isinstance(choices, list):
                options = "\n".join([f"{chr(65+j)}. {choice}" for j, choice in enumerate(choices)])
                question_text += f"\n\nOptions:\n{options}"
            elif isinstance(choices, str) and choices.strip():
                question_text += f"\n\nOptions: {choices}"
        
        # Use rationale if available, otherwise placeholder
        reasoning = row.get('rationale', '')
        if pd.isna(reasoning) or str(reasoning).strip() == '':
            reasoning = f"Step-by-step reasoning required for {row.get('category', 'STEM')} problem."
        else:
            reasoning = str(reasoning)
        
        # Clean category for type field
        category = str(row.get('category', 'unknown'))
        category_clean = category.lower().replace(' ', '_').replace('/', '_').replace('\\', '_')
        
        problems.append({
            'id': f"H{i+1:04d}",
            'type': f"hle_{category_clean}",
            'level': 'HLE_Advanced',
            'text': question_text,
            'solution': str(row.get('answer', '')),
            'reasoning': reasoning,
            'source': 'HLE',
            'category': category
        })
    
    return pd.DataFrame(problems)

# ==================== SAVE HLE PROBLEMS ====================
def save_hle_problems(df):
    """Save HLE problems to CSV."""
    if df.empty:
        print("⚠ No HLE problems to save.")
        return None
    
    os.makedirs('problems', exist_ok=True)
    
    # Save HLE-only file
    hle_file = Path('problems') / 'problems_hle.csv'
    df.to_csv(hle_file, index=False, quoting=csv.QUOTE_ALL, encoding='utf-8')
    
    # Create summary
    summary = df.groupby(['category', 'type']).size().reset_index(name='count')
    summary_file = Path('problems') / 'hle_summary.csv'
    summary.to_csv(summary_file, index=False)
    
    print(f"\n{'='*60}")
    print("HLE PROBLEM SET CREATION COMPLETE!")
    print(f"{'='*60}")
    print(f"✓ Total HLE Problems: {len(df)}")
    print(f"✓ Categories:")
    for category in sorted(df['category'].unique()):
        count = len(df[df['category'] == category])
        print(f"    - {category}: {count} problems")
    print(f"✓ Saved to: {hle_file}")
    print(f"✓ Summary: {summary_file}")
    
    return hle_file

# ==================== TEST HLE ACCESS ====================
def test_hle_access(token):
    """Simple test to check HLE access."""
    print("\n🔍 Testing HLE access...")
    try:
        # Small test load
        test_ds = load_dataset("cais/hle", token=token, split='train[:5]')
        print(f"✓ HLE access successful! Found {len(test_ds)} sample problems.")
        print(f"  Sample keys: {list(test_ds[0].keys())}")
        return True
    except Exception as e:
        print(f"✗ HLE access test failed: {str(e)[:150]}")
        return False

# ==================== MAIN FUNCTION ====================
def main():
    print("\n" + "="*60)
    print("BUILDING HLE STEM PROBLEM SET - FIXED VERSION")
    print("="*60)
    print("Note: Requires Hugging Face authentication")
    print("      HLE is a gated dataset for academic use")
    
    # Check for authentication
    print("\n1. Checking authentication...")
    token = check_hf_auth()
    
    # Test access first
    if token:
        access_ok = test_hle_access(token)
        if not access_ok:
            print("\n⚠ HLE access may not be granted yet.")
            print("  Visit: https://huggingface.co/datasets/cais/hle")
            print("  Click 'Agree and Access' and wait for approval.")
            response = input("\nTry loading anyway? (y/n): ").strip().lower()
            if response != 'y':
                print("Exiting. Please get HLE access first.")
                return
    
    # Load HLE data
    print("\n2. Loading HLE dataset...")
    hle_data = load_hle_data(token)
    
    if hle_data.empty:
        print("\n✗ No HLE data loaded. Possible reasons:")
        print("  1. HLE access not yet approved (check email)")
        print("  2. Token not valid for HLE dataset")
        print("  3. Network issues")
        print("\n💡 You can continue with MMLU-only dataset for now.")
        print("   Run: python3 scripts/combine_problems.py")
        return
    
    # Format and save
    print("\n3. Formatting HLE problems...")
    formatted_problems = format_hle_problems(hle_data)
    
    print("\n4. Saving HLE problems...")
    hle_file = save_hle_problems(formatted_problems)
    
    if hle_file:
        # Preview
        print(f"\n📋 Sample HLE Problem:")
        print(f"{'-'*40}")
        sample = formatted_problems.iloc[0]
        print(f"ID: {sample['id']}")
        print(f"Category: {sample['category']}")
        print(f"Question preview: {sample['text'][:100]}...")
        print(f"Answer: {sample['solution'][:50]}...")
        
        print(f"\n{'='*60}")
        print("NEXT STEPS:")
        print(f"{'='*60}")
        print("✓ HLE problems saved to: problems_hle.csv")
        print("✓ To combine with MMLU, run: python3 scripts/combine_problems.py")

if __name__ == "__main__":
    main()