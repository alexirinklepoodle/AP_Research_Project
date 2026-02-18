"""
Qualitative Analysis Master Workflow

This script provides a unified entry point for the complete qualitative 
analysis pipeline. Run this script to be guided through each step.

Usage:
    python3 scripts/qualitative_workflow.py
"""

import sys
import os
import glob
from datetime import datetime

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def check_prerequisites():
    """Check if prerequisites are met"""
    print_header("PREREQUISITE CHECK")
    
    # Check for scored data
    scored_files = glob.glob('data/processed/scored_*.csv')
    if not scored_files:
        print("✗ No scored data found!")
        print("  Please run scoring_engine.py first to score your data.")
        print("\n  Command: python3 scripts/scoring_engine.py")
        return False
    
    print(f"✓ Found scored data: {max(scored_files)}")
    
    # Check for problems.csv
    if not os.path.exists('problems/problems.csv'):
        print("✗ problems.csv not found!")
        return False
    
    print("✓ Found problems.csv")
    
    # Count errors in scored data
    import pandas as pd
    df = pd.read_csv(max(scored_files))
    error_count = (df['score_binary'] == 0).sum()
    print(f"✓ Found {error_count} errors available for qualitative analysis")
    
    if error_count == 0:
        print("✗ No errors found! All responses were correct.")
        return False
    
    return True


def step1_error_collection():
    """Step 1: Build error collection"""
    print_header("STEP 1: BUILD ERROR COLLECTION")
    
    print("\nThis step will:")
    print("  • Extract all incorrect responses from your scored data")
    print("  • Create a stratified sample of ~60 errors (by model group & problem type)")
    print("  • Save files for qualitative coding")
    
    choice = input("\nProceed with error collection? (y/n): ").strip().lower()
    if choice != 'y':
        print("  Skipped")
        return None
    
    from error_collection import build_error_collection
    result = build_error_collection(target_sample_size=60)
    
    if result:
        print("\n✓ Step 1 complete!")
        print(f"  Files created:")
        for name, path in result.items():
            print(f"    • {path}")
    
    return result


def step2_rubric_development():
    """Step 2: Develop coding rubric"""
    print_header("STEP 2: DEVELOP CODING RUBRIC")
    
    print("\nThis step will:")
    print("  • Create a starter rubric with common LLM error types")
    print("  • Allow you to customize categories based on open coding")
    print("  • Save the rubric for use in coding")
    
    print("\nIMPORTANT: Before using the automated rubric:")
    print("  1. Open the error collection file")
    print("  2. Read through 10-15 errors")
    print("  3. Note any patterns you observe (don't force into categories)")
    print("  4. Then use the tool to formalize your categories")
    
    choice = input("\nReady to develop rubric? (y/n): ").strip().lower()
    if choice != 'y':
        print("  Skipped")
        return None
    
    from qualitative_rubric import create_starter_rubric
    rubric = create_starter_rubric()
    
    print("\n✓ Step 2 complete!")
    print("\nNext: Review and refine the rubric based on your observations")
    print("  Use: python3 scripts/qualitative_rubric.py")
    
    return rubric


def step3_coding():
    """Step 3: Code errors"""
    print_header("STEP 3: CODE ERRORS")
    
    print("\nThis step will:")
    print("  • Load your error collection and rubric")
    print("  • Present each error for manual coding")
    print("  • Allow you to assign primary and secondary error types")
    print("  • Track your confidence and add notes")
    
    print("\nTips for coding:")
    print("  • Read the full model response carefully")
    print("  • Compare to the correct solution")
    print("  • Identify the PRIMARY error (most significant issue)")
    print("  • Add SECONDARY error if another issue is present")
    print("  • Mark confidence as high/medium/low")
    print("  • Add notes for ambiguous cases")
    
    choice = input("\nStart coding session? (y/n): ").strip().lower()
    if choice != 'y':
        print("  Skipped")
        return None
    
    import subprocess
    subprocess.run(['python3', 'scripts/qualitative_coding.py'])
    
    print("\n✓ Step 3 complete!")
    return True


def step4_reliability():
    """Step 4: Reliability check"""
    print_header("STEP 4: RELIABILITY CHECK")
    
    print("\nThis step will:")
    print("  • Select a random 25% subset of your coded errors")
    print("  • Have you recode them blindly (without seeing original codes)")
    print("  • Calculate Cohen's κ to assess your coding consistency")
    
    print("\n⚠ CRITICAL: Wait 1-2 weeks before doing this step!")
    print("   This prevents memory bias in your recoding.")
    print("   You can run this script again later for step 4.")
    
    # Check if coded data exists
    coded_files = glob.glob('data/processed/coded_errors_*.csv')
    if not coded_files:
        print("\n✗ No coded data found!")
        print("  Please complete Step 3 (coding) first.")
        return None
    
    print(f"\n✓ Found coded data: {max(coded_files)}")
    
    choice = input("\nProceed with reliability check? (y/n): ").strip().lower()
    if choice != 'y':
        print("  Skipped")
        return None
    
    import subprocess
    subprocess.run(['python3', 'scripts/reliability_check.py'])
    
    print("\n✓ Step 4 complete!")
    print("\nIf κ ≥ 0.7: Your coding is reliable. Proceed to pattern analysis.")
    print("If κ < 0.7: Revise your rubric and recode before proceeding.")
    
    return True


def step5_pattern_analysis():
    """Step 5: Pattern analysis"""
    print_header("STEP 5: PATTERN ANALYSIS")
    
    print("\nThis step will:")
    print("  • Convert your qualitative codes to frequencies")
    print("  • Create contingency tables (RLHF vs non-RLHF)")
    print("  • Perform chi-square tests for significant differences")
    print("  • Identify which error types differ between model groups")
    print("  • Generate visualizations and reports")
    
    # Check if coded data exists
    coded_files = glob.glob('data/processed/coded_errors_*.csv')
    if not coded_files:
        print("\n✗ No coded data found!")
        print("  Please complete Step 3 (coding) first.")
        return None
    
    print(f"\n✓ Found coded data: {max(coded_files)}")
    
    choice = input("\nRun pattern analysis? (y/n): ").strip().lower()
    if choice != 'y':
        print("  Skipped")
        return None
    
    import subprocess
    subprocess.run(['python3', 'scripts/pattern_analysis.py'])
    
    print("\n✓ Step 5 complete!")
    return True


def step6_synthesis():
    """Step 6: Synthesis and documentation"""
    print_header("STEP 6: SYNTHESIS & DOCUMENTATION")
    
    print("\nThis step helps you:")
    print("  • Review all analysis results")
    print("  • Link quantitative and qualitative findings")
    print("  • Select prototypical examples")
    print("  • Prepare for visualization and reporting")
    
    print("\nFiles to review:")
    
    # List recent output files
    output_files = glob.glob('data/processed/*.csv') + \
                   glob.glob('data/processed/*.json') + \
                   glob.glob('data/processed/*.txt')
    
    if output_files:
        output_files.sort(key=os.path.getmtime, reverse=True)
        print("\nRecent output files:")
        for f in output_files[:10]:
            mtime = datetime.fromtimestamp(os.path.getmtime(f))
            print(f"  • {f} ({mtime.strftime('%Y-%m-%d %H:%M')})")
    else:
        print("\n  No output files found yet.")
    
    print("\nNext steps:")
    print("  1. Review pattern_analysis_report_*.txt for key findings")
    print("  2. Select 3-5 prototypical examples per major pattern")
    print("  3. Create visualizations linking quant and qual results")
    print("  4. Document your methodology and decisions")
    print("  5. Organize files for your research paper")
    
    return True


def main_workflow():
    """Run the complete qualitative analysis workflow"""
    print_header("QUALITATIVE ANALYSIS WORKFLOW")
    
    print("\nThis workflow guides you through the qualitative analysis process")
    print("for your AP Research project on RLHF vs non-RLHF LLM error patterns.")
    print("\nEach step builds on the previous one. Some steps require manual work.")
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n✗ Prerequisites not met. Please address the issues above.")
        return
    
    # Step 1: Error Collection
    step1_error_collection()
    
    # Step 2: Rubric Development
    step2_rubric_development()
    
    # Step 3: Coding
    step3_coding()
    
    # Step 4: Reliability Check
    print("\n" + "=" * 70)
    print("NOTE: Step 4 (Reliability Check) should be done after 1-2 weeks")
    print("      to prevent memory bias in your recoding.")
    print("=" * 70)
    step4_reliability()
    
    # Step 5: Pattern Analysis
    step5_pattern_analysis()
    
    # Step 6: Synthesis
    step6_synthesis()
    
    print_header("WORKFLOW COMPLETE")
    print("\n✓ All steps completed!")
    print("\nCheck the data/processed/ directory for all output files.")
    print("Review the documentation for guidance on interpreting results.")
    print("\nFor questions about specific steps, run the individual scripts:")
    print("  • python3 scripts/error_collection.py")
    print("  • python3 scripts/qualitative_rubric.py")
    print("  • python3 scripts/qualitative_coding.py")
    print("  • python3 scripts/reliability_check.py")
    print("  • python3 scripts/pattern_analysis.py")


if __name__ == "__main__":
    try:
        main_workflow()
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user.")
        print("You can resume by running this script again.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease check the error message above and try again.")
        print("You can also run individual scripts for more detailed error messages.")
