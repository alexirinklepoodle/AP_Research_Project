"""
combine_problems_fixed.py
SAFELY combines HLE and MMLU problem sets WITHOUT deleting files.
"""

import pandas as pd
import csv
import os
from pathlib import Path
import shutil

# ==================== CONFIGURATION ====================
TOTAL_TARGET = 350  # Final total problems
HLE_TARGET = 150    # Desired HLE problems
MMLU_TARGET = 200   # Desired MMLU problems

def safe_combine_problems():
    """Safely combine HLE and MMLU without deleting original files."""
    print("\n" + "="*60)
    print("SAFELY COMBINING HLE AND MMLU PROBLEM SETS")
    print("="*60)
    
    # Define file paths
    problems_dir = Path('problems')
    hle_file = problems_dir / 'problems_hle.csv'
    mmlu_file = problems_dir / 'problems.csv'  # Current MMLU file
    mmlu_backup = problems_dir / 'problems_mmlu_original.csv'
    combined_file = problems_dir / 'problems_combined.csv'
    final_file = problems_dir / 'problems.csv'  # Final output
    
    # Step 1: Check what files exist
    print("\n1. Checking available files...")
    
    if not hle_file.exists():
        print(f"✗ Missing: {hle_file}")
        print("  Run: python3 scripts/build_hle_problems.py first")
        return
    
    if not mmlu_file.exists():
        print(f"✗ Missing: {mmlu_file}")
        print("  Run: python3 scripts/build_college_mmlu.py first")
        return
    
    print(f"✓ Found: {hle_file}")
    print(f"✓ Found: {mmlu_file}")
    
    # Step 2: Backup original MMLU file
    print("\n2. Creating backups...")
    if not mmlu_backup.exists():
        shutil.copy2(mmlu_file, mmlu_backup)
        print(f"✓ Backed up MMLU to: {mmlu_backup}")
    else:
        print(f"✓ MMLU backup already exists: {mmlu_backup}")
    
    # Step 3: Load data
    print("\n3. Loading data...")
    try:
        df_hle = pd.read_csv(hle_file)
        df_mmlu = pd.read_csv(mmlu_file)
        
        print(f"✓ Loaded {len(df_hle)} HLE problems")
        print(f"✓ Loaded {len(df_mmlu)} MMLU problems")
    except Exception as e:
        print(f"✗ Error loading files: {e}")
        return
    
    # Step 4: Ask for confirmation
    print(f"\n4. Configuration:")
    print(f"   HLE problems available: {len(df_hle)}")
    print(f"   MMLU problems available: {len(df_mmlu)}")
    print(f"   Target combination: {HLE_TARGET} HLE + {MMLU_TARGET} MMLU = {TOTAL_TARGET} total")
    
    response = input("\nProceed with these targets? (y/n): ").strip().lower()
    if response != 'y':
        print("Aborted. No files changed.")
        return
    
    # Step 5: Sample from each dataset
    print("\n5. Creating balanced sample...")
    
    # Sample HLE
    if len(df_hle) >= HLE_TARGET:
        hle_sample = df_hle.sample(HLE_TARGET, random_state=42)
    else:
        hle_sample = df_hle
        print(f"⚠ Only {len(df_hle)} HLE problems available")
    
    # Sample MMLU
    if len(df_mmlu) >= MMLU_TARGET:
        mmlu_sample = df_mmlu.sample(MMLU_TARGET, random_state=42)
    else:
        mmlu_sample = df_mmlu
        print(f"⚠ Only {len(df_mmlu)} MMLU problems available")
    
    # Step 6: Combine and shuffle
    print("\n6. Combining datasets...")
    combined = pd.concat([hle_sample, mmlu_sample], ignore_index=True)
    combined = combined.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Assign new IDs
    combined['id'] = [f"C{i+1:04d}" for i in range(len(combined))]
    
    # Step 7: Save to TEMPORARY file first
    print("\n7. Saving combined dataset...")
    temp_file = problems_dir / 'problems_TEMP.csv'
    combined.to_csv(temp_file, index=False, quoting=csv.QUOTE_ALL, encoding='utf-8')
    
    # Verify the temp file was created
    if not temp_file.exists():
        print("✗ Failed to create temporary file!")
        return
    
    # Step 8: SAFELY replace the original
    # 1. Rename original to backup
    original_backup = problems_dir / 'problems_OLD.csv'
    if mmlu_file.exists():
        mmlu_file.rename(original_backup)
    
    # 2. Move temp to final
    temp_file.rename(final_file)
    
    # 3. Clean up old backup
    if original_backup.exists():
        original_backup.unlink()
    
    print(f"✓ Saved combined dataset to: {final_file}")
    print(f"✓ Total problems: {len(combined)}")
    
    # Step 9: Create summaries
    print("\n8. Creating summaries...")
    
    # Basic summary
    summary_data = []
    if 'source' in combined.columns:
        for source in combined['source'].unique():
            count = len(combined[combined['source'] == source])
            summary_data.append([source, count])
    
    summary_df = pd.DataFrame(summary_data, columns=['Source', 'Count'])
    summary_file = problems_dir / 'combined_summary_fixed.csv'
    summary_df.to_csv(summary_file, index=False)
    
    # Detailed breakdown
    if 'source' in combined.columns and 'type' in combined.columns:
        detailed = combined.groupby(['source', 'type']).size().reset_index(name='count')
        detailed_file = problems_dir / 'detailed_breakdown_fixed.csv'
        detailed.to_csv(detailed_file, index=False)
    
    print(f"✓ Summary saved to: {summary_file}")
    
    # Step 10: Final verification
    print("\n9. Verifying final dataset...")
    
    if final_file.exists():
        final_df = pd.read_csv(final_file)
        print(f"✓ Final file created with {len(final_df)} problems")
        
        print(f"\n{'='*60}")
        print("COMBINATION SUCCESSFUL!")
        print(f"{'='*60}")
        print(f"✓ Original MMLU backed up to: {mmlu_backup}")
        print(f"✓ HLE data preserved in: {hle_file}")
        print(f"✓ Combined dataset: {final_file}")
        print(f"✓ Total problems: {len(final_df)}")
        
        if 'source' in final_df.columns:
            print(f"✓ Source breakdown:")
            for source in final_df['source'].unique():
                count = len(final_df[final_df['source'] == source])
                print(f"   - {source}: {count} problems")
        
        print(f"\nReady for data collection!")
        print(f"Run: python3 scripts/data_collector.py")
    else:
        print("✗ ERROR: Final file not created!")
        print("Check permissions and try again.")

if __name__ == "__main__":
    safe_combine_problems()