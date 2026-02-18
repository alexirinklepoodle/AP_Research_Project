"""
Intra-Rater Reliability Check Tool

This script calculates intra-rater reliability (Cohen's κ) for qualitative coding:
1. Set aside coded data for 1-2 weeks (handled by researcher)
2. Randomly select 25% subset and shuffle order
3. Recode subset blindly without reference to previous codes
4. Calculate Cohen's κ to assess reliability
5. Revise coding rubric if κ < 0.7

Usage:
    python3 scripts/reliability_check.py
"""

import csv
import json
import os
import glob
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import Counter
import math


def calculate_cohens_kappa(coding1: List[str], coding2: List[str]) -> float:
    """
    Calculate Cohen's kappa coefficient for inter-rater reliability
    
    Args:
        coding1: First round of codes
        coding2: Second round of codes
    
    Returns:
        Cohen's kappa coefficient (0-1, where >0.7 is acceptable)
    """
    if len(coding1) != len(coding2):
        raise ValueError("Coding lists must have same length")
    
    n = len(coding1)
    if n == 0:
        return 0.0
    
    # Get all unique categories
    all_categories = set(coding1) | set(coding2)
    categories = list(all_categories)
    k = len(categories)
    
    # Create confusion matrix
    matrix = {cat1: {cat2: 0 for cat2 in categories} for cat1 in categories}
    for c1, c2 in zip(coding1, coding2):
        matrix[c1][c2] += 1
    
    # Calculate observed agreement (Po)
    po = sum(matrix[cat][cat] for cat in categories) / n
    
    # Calculate expected agreement (Pe)
    # Sum of (proportion of cat in coding1 * proportion of cat in coding2)
    pe = 0
    for cat in categories:
        count1 = sum(matrix[cat].values())
        count2 = sum(matrix[cat2][cat] for cat2 in categories)
        pe += (count1 / n) * (count2 / n)
    
    # Calculate kappa
    if pe == 1.0:
        return 0.0  # Perfect expected agreement means kappa is undefined
    
    kappa = (po - pe) / (1 - pe)
    
    return kappa


def interpret_kappa(kappa: float) -> str:
    """
    Interpret kappa value using Landis & Koch (1977) guidelines
    
    Args:
        kappa: Cohen's kappa coefficient
    
    Returns:
        Interpretation string
    """
    if kappa < 0:
        return "Poor (less than chance agreement)"
    elif kappa < 0.20:
        return "Slight agreement"
    elif kappa < 0.40:
        return "Fair agreement"
    elif kappa < 0.60:
        return "Moderate agreement"
    elif kappa < 0.80:
        return "Substantial agreement"
    else:
        return "Almost perfect agreement"


class ReliabilityChecker:
    """Manages intra-rater reliability checking process"""
    
    def __init__(self, coded_file: str = None):
        self.coded_data = []
        self.recode_subset = []
        self.original_codes = []
        self.recode_codes = []
        self.results = {}
        
        # Load most recent coded data
        if coded_file is None:
            coded_files = glob.glob('data/processed/coded_errors_*.csv')
            coded_file = max(coded_files) if coded_files else None
        
        if coded_file:
            self.load_coded_data(coded_file)
        else:
            print("⚠ No coded data found. Complete qualitative coding first.")
    
    def load_coded_data(self, coded_file: str):
        """Load previously coded data"""
        with open(coded_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.coded_data = list(reader)
        print(f"✓ Loaded {len(self.coded_data)} coded errors from {coded_file}")
    
    def create_recode_subset(self, proportion: float = 0.25, 
                             output_file: str = None) -> List[Dict]:
        """
        Create shuffled subset for blind recoding
        
        Args:
            proportion: Proportion of data to recode (default 0.25 = 25%)
            output_file: File to save subset for recoding
        
        Returns:
            List of errors to recode
        """
        if not self.coded_data:
            print("✗ No coded data loaded")
            return []
        
        # Calculate sample size
        sample_size = max(1, int(len(self.coded_data) * proportion))
        
        # Random sample
        subset = random.sample(self.coded_data, sample_size)
        
        # Shuffle for blind recoding
        random.shuffle(subset)
        
        # Store original codes for comparison
        self.recode_subset = subset
        self.original_codes = [
            error.get('primary_error_type', '') for error in subset
        ]
        
        # Create recoding file (without original codes visible)
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f'data/processed/recode_subset_{timestamp}.csv'
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write subset for recoding (hide original codes)
        fieldnames = [
            'error_id', 'problem_id', 'model_group', 'model_name',
            'problem_type', 'problem_text', 'model_response',
            'correct_solution', 'extracted_answer',
            'primary_error_type', 'secondary_error_type', 
            'confidence', 'coder_notes'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for error in subset:
                # Create row with blank codes for blind recoding
                row = {
                    'error_id': error.get('error_id', ''),
                    'problem_id': error.get('problem_id', ''),
                    'model_group': error.get('model_group', ''),
                    'model_name': error.get('model_name', ''),
                    'problem_type': error.get('problem_type', ''),
                    'problem_text': error.get('problem_text', ''),
                    'model_response': error.get('model_response', ''),
                    'correct_solution': error.get('correct_solution', ''),
                    'extracted_answer': error.get('extracted_answer', ''),
                    'primary_error_type': '',  # Blank for recoding
                    'secondary_error_type': '',
                    'confidence': '',
                    'coder_notes': ''
                }
                writer.writerow(row)
        
        print(f"\n✓ Created recode subset: {sample_size} errors ({proportion*100:.0f}%)")
        print(f"  Saved to: {output_file}")
        print(f"\n⚠ IMPORTANT: Wait 1-2 weeks before recoding to avoid memory bias!")
        print(f"  Original codes are stored separately for comparison.")
        
        # Save metadata for later comparison
        metadata = {
            'subset_file': output_file,
            'subset_size': sample_size,
            'proportion': proportion,
            'original_codes': self.original_codes,
            'created': datetime.now().isoformat()
        }
        
        metadata_file = output_file.replace('.csv', '_metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"  Metadata saved to: {metadata_file}")
        
        return subset
    
    def load_recode_results(self, recode_file: str):
        """Load recoded data"""
        with open(recode_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            recoded_data = list(reader)
        
        if len(recoded_data) != len(self.original_codes):
            print(f"⚠ Warning: Recoded count ({len(recoded_data)}) doesn't match original ({len(self.original_codes)})")
        
        self.recode_codes = [
            error.get('primary_error_type', '') for error in recoded_data
        ]
        
        print(f"✓ Loaded {len(self.recode_codes)} recoded errors")
    
    def calculate_reliability(self) -> Dict:
        """
        Calculate intra-rater reliability statistics
        
        Returns:
            Dictionary with reliability statistics
        """
        if not self.original_codes or not self.recode_codes:
            print("✗ Need both original and recoded data")
            return None
        
        if len(self.original_codes) != len(self.recode_codes):
            print("✗ Code counts don't match")
            return None
        
        # Calculate Cohen's kappa
        kappa = calculate_cohens_kappa(self.original_codes, self.recode_codes)
        interpretation = interpret_kappa(kappa)
        
        # Calculate simple percent agreement
        agreements = sum(1 for c1, c2 in zip(self.original_codes, self.recode_codes) 
                        if c1 == c2)
        percent_agreement = agreements / len(self.original_codes) * 100
        
        # Category-level agreement
        category_agreement = {}
        categories = set(self.original_codes) | set(self.recode_codes)
        for cat in categories:
            if cat:  # Skip empty
                orig_count = sum(1 for c in self.original_codes if c == cat)
                recode_count = sum(1 for c in self.recode_codes if c == cat)
                both_count = sum(1 for c1, c2 in zip(self.original_codes, self.recode_codes) 
                               if c1 == cat and c2 == cat)
                if orig_count > 0:
                    category_agreement[cat] = {
                        'original_count': orig_count,
                        'recode_count': recode_count,
                        'agreement_count': both_count,
                        'agreement_rate': both_count / orig_count * 100 if orig_count > 0 else 0
                    }
        
        # Disagreement analysis
        disagreements = []
        for i, (c1, c2) in enumerate(zip(self.original_codes, self.recode_codes)):
            if c1 != c2:
                disagreements.append({
                    'index': i,
                    'original': c1,
                    'recode': c2
                })
        
        self.results = {
            'kappa': kappa,
            'interpretation': interpretation,
            'percent_agreement': percent_agreement,
            'total_sampled': len(self.original_codes),
            'agreements': agreements,
            'disagreements': len(disagreements),
            'category_agreement': category_agreement,
            'disagreement_details': disagreements,
            'calculated': datetime.now().isoformat()
        }
        
        return self.results
    
    def print_results(self):
        """Print reliability check results"""
        if not self.results:
            print("✗ No results. Run calculate_reliability() first.")
            return
        
        print("\n" + "=" * 70)
        print("INTRA-RATER RELIABILITY RESULTS")
        print("=" * 70)
        
        print(f"\nSample Size: {self.results['total_sampled']} errors")
        print(f"Simple Agreement: {self.results['percent_agreement']:.1f}%")
        print(f"Cohen's κ: {self.results['kappa']:.3f}")
        print(f"Interpretation: {self.results['interpretation']}")
        
        print(f"\nAgreements: {self.results['agreements']}")
        print(f"Disagreements: {self.results['disagreements']}")
        
        if self.results['category_agreement']:
            print("\nCategory-Level Agreement:")
            print("-" * 70)
            for cat, stats in sorted(self.results['category_agreement'].items()):
                print(f"  {cat}:")
                print(f"    Original: {stats['original_count']}, Recoded: {stats['recode_count']}")
                print(f"    Agreement: {stats['agreement_count']}/{stats['original_count']} "
                      f"({stats['agreement_rate']:.1f}%)")
        
        if self.results['disagreement_details']:
            print(f"\nDisagreement Details ({len(self.results['disagreement_details'])} cases):")
            print("-" * 70)
            for d in self.results['disagreement_details'][:10]:  # Show first 10
                print(f"  Case {d['index'] + 1}: {d['original']} → {d['recode']}")
            if len(self.results['disagreement_details']) > 10:
                print(f"  ... and {len(self.results['disagreement_details']) - 10} more")
        
        print("\n" + "=" * 70)
        
        # Recommendation
        if self.results['kappa'] >= 0.7:
            print("✓ RELIABILITY ACCEPTABLE (κ ≥ 0.7)")
            print("  Your coding rubric is reliable. Continue with pattern analysis.")
        else:
            print("⚠ RELIABILITY BELOW THRESHOLD (κ < 0.7)")
            print("  Recommendations:")
            print("  1. Review disagreement cases to identify ambiguous categories")
            print("  2. Refine rubric definitions for problematic categories")
            print("  3. Consider merging categories with low agreement")
            print("  4. Recode a subset with revised rubric")
        
        print("=" * 70)
    
    def save_results(self, output_file: str = None):
        """Save reliability results"""
        if not self.results:
            print("✗ No results to save")
            return None
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f'data/processed/reliability_results_{timestamp}.json'
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"✓ Results saved to: {output_file}")
        
        # Also save human-readable report
        report_file = output_file.replace('.json', '_report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("INTRA-RATER RELIABILITY REPORT\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Generated: {self.results['calculated']}\n\n")
            f.write(f"Sample Size: {self.results['total_sampled']} errors\n")
            f.write(f"Simple Agreement: {self.results['percent_agreement']:.1f}%\n")
            f.write(f"Cohen's κ: {self.results['kappa']:.3f}\n")
            f.write(f"Interpretation: {self.results['interpretation']}\n\n")
            
            f.write("RECOMMENDATION\n")
            f.write("-" * 70 + "\n")
            if self.results['kappa'] >= 0.7:
                f.write("✓ RELIABILITY ACCEPTABLE\n")
                f.write("The coding rubric demonstrates adequate reliability for analysis.\n")
            else:
                f.write("⚠ RELIABILITY BELOW THRESHOLD\n")
                f.write("The coding rubric needs refinement before proceeding.\n\n")
                f.write("Disagreement cases to review:\n")
                for d in self.results['disagreement_details']:
                    f.write(f"  - Case {d['index'] + 1}: {d['original']} → {d['recode']}\n")
        
        print(f"✓ Report saved to: {report_file}")
        return output_file


def check_reliability_workflow():
    """
    Complete workflow for reliability checking
    """
    print("=" * 70)
    print("INTRA-RATER RELIABILITY CHECK WORKFLOW")
    print("=" * 70)
    
    checker = ReliabilityChecker()
    
    if not checker.coded_data:
        print("\n✗ No coded data found!")
        print("  Please complete qualitative coding first using:")
        print("  python3 scripts/qualitative_coding.py")
        return None
    
    print("\nSTEP 1: Create recode subset")
    print("-" * 70)
    proportion = input("Proportion to recode (default 0.25): ").strip()
    proportion = float(proportion) if proportion else 0.25
    
    checker.create_recode_subset(proportion=proportion)
    
    print("\n" + "=" * 70)
    print("STEP 2: Wait 1-2 weeks")
    print("=" * 70)
    print("\n⚠ IMPORTANT: Wait at least 1-2 weeks before recoding!")
    print("   This prevents memory bias in your coding.")
    print("\nAfter waiting, run this script again and select 'Load recode results'")
    
    # Save checker state
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    state_file = f'data/processed/reliability_state_{timestamp}.json'
    
    # Note: We can't easily save the checker object, so we just document the process
    print(f"\n✓ Workflow state documented")
    
    return checker


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Intra-Rater Reliability Check')
    parser.add_argument('--coded-file', type=str, help='Coded data file')
    parser.add_argument('--recode-file', type=str, help='Recoded data file')
    parser.add_argument('--metadata-file', type=str, help='Metadata file with original codes')
    parser.add_argument('--proportion', type=float, default=0.25, 
                       help='Proportion to recode (default 0.25)')
    parser.add_argument('--calculate', action='store_true', 
                       help='Calculate reliability from existing files')
    
    args = parser.parse_args()
    
    checker = ReliabilityChecker(coded_file=args.coded_file)
    
    if args.calculate and args.recode_file and args.metadata_file:
        # Load recode results and metadata
        checker.load_recode_results(args.recode_file)
        
        with open(args.metadata_file, 'r') as f:
            metadata = json.load(f)
            checker.original_codes = metadata.get('original_codes', [])
        
        # Calculate and save
        checker.calculate_reliability()
        checker.print_results()
        checker.save_results()
    
    elif args.recode_file:
        # Just load recode results
        checker.load_recode_results(args.recode_file)
        print("✓ Loaded recode results. Run with --calculate to compute reliability.")
    
    else:
        # Interactive workflow
        check_reliability_workflow()


if __name__ == "__main__":
    main()
