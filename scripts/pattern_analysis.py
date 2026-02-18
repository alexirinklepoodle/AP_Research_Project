"""
Pattern Analysis Tool for Qualitative Coding

This script performs pattern analysis on coded qualitative data:
1. Quantitize coded data: count frequencies per error type per model group
2. Create contingency tables comparing RLHF vs non-RLHF error distributions
3. Perform chi-square tests on significant differences
4. Identify key patterns: which errors are more common in which group
5. Generate visualizations and export results

Usage:
    python3 scripts/pattern_analysis.py
"""

import csv
import json
import os
import glob
from datetime import datetime
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
import math


def chi_square_test(contingency_table: Dict[str, Dict[str, int]]) -> Dict:
    """
    Perform chi-square test of independence on contingency table
    
    Args:
        contingency_table: Dict of dicts representing contingency table
                          e.g., {'RLHF': {'LOGIC': 10, 'CALC': 5}, 'non-RLHF': {'LOGIC': 8, 'CALC': 12}}
    
    Returns:
        Dictionary with chi-square statistics
    """
    # Convert to matrix format
    rows = list(contingency_table.keys())
    cols = list(contingency_table[rows[0]].keys())
    
    # Build observed matrix
    observed = []
    for row in rows:
        observed.append([contingency_table[row].get(col, 0) for col in cols])
    
    n_rows = len(rows)
    n_cols = len(cols)
    
    # Calculate totals
    row_totals = [sum(row) for row in observed]
    col_totals = [sum(observed[i][j] for i in range(n_rows)) for j in range(n_cols)]
    grand_total = sum(row_totals)
    
    if grand_total == 0:
        return {
            'chi_square': 0,
            'degrees_of_freedom': 0,
            'p_value': 1.0,
            'significant': False,
            'message': 'No data'
        }
    
    # Calculate expected frequencies and chi-square statistic
    chi_square = 0
    expected = []
    
    for i in range(n_rows):
        expected_row = []
        for j in range(n_cols):
            expected_val = (row_totals[i] * col_totals[j]) / grand_total
            expected_row.append(expected_val)
            
            if expected_val > 0:
                chi_square += ((observed[i][j] - expected_val) ** 2) / expected_val
        expected.append(expected_row)
    
    # Degrees of freedom
    df = (n_rows - 1) * (n_cols - 1)
    
    # Calculate p-value using chi-square distribution approximation
    # For more accurate p-values, use scipy.stats.chi2.sf(chi_square, df)
    p_value = chi_square_distribution_sf(chi_square, df)
    
    # Determine significance
    significant = p_value < 0.05
    
    # Calculate effect size (Cramér's V)
    n = grand_total
    min_dim = min(n_rows - 1, n_cols - 1)
    cramers_v = math.sqrt(chi_square / (n * min_dim)) if min_dim > 0 and n > 0 else 0
    
    return {
        'chi_square': chi_square,
        'degrees_of_freedom': df,
        'p_value': p_value,
        'significant': significant,
        'effect_size': cramers_v,
        'observed': observed,
        'expected': expected,
        'row_labels': rows,
        'col_labels': cols,
        'row_totals': row_totals,
        'col_totals': col_totals,
        'grand_total': grand_total
    }


def chi_square_distribution_sf(x: float, df: int) -> float:
    """
    Survival function (1 - CDF) of chi-square distribution
    Approximation using Wilson-Hilferty transformation
    
    For more accurate values, use scipy.stats.chi2.sf(x, df)
    """
    if df <= 0 or x < 0:
        return 1.0
    
    # Wilson-Hilferty transformation
    z = ((x / df) ** (1/3) - (1 - 2/(9*df))) / math.sqrt(2/(9*df))
    
    # Standard normal survival function approximation
    p = 0.5 * (1 + math.erf(-z / math.sqrt(2)))
    
    return p


class PatternAnalyzer:
    """Analyzes patterns in qualitatively coded data"""
    
    def __init__(self, coded_file: str = None):
        self.coded_data = []
        self.rubric = {}
        self.patterns = {}
        self.results = {}
        
        # Load most recent coded data
        if coded_file is None:
            coded_files = glob.glob('data/processed/coded_errors_*.csv')
            coded_file = max(coded_files) if coded_files else None
        
        if coded_file:
            self.load_coded_data(coded_file)
        
        # Load rubric
        rubric_files = glob.glob('data/processed/rubric.json')
        if rubric_files:
            with open(rubric_files[0], 'r') as f:
                self.rubric = json.load(f).get('categories', {})
    
    def load_coded_data(self, coded_file: str):
        """Load coded data"""
        with open(coded_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.coded_data = list(reader)
        print(f"✓ Loaded {len(self.coded_data)} coded errors from {coded_file}")
    
    def quantitize_data(self) -> Dict:
        """
        Convert qualitative codes to quantitative frequencies
        
        Returns:
            Dictionary with frequency counts
        """
        if not self.coded_data:
            print("✗ No coded data loaded")
            return {}
        
        # Filter out uncoded errors
        coded_errors = [e for e in self.coded_data if e.get('primary_error_type')]
        
        # Overall frequency by error type
        error_type_freq = Counter(e.get('primary_error_type', '') for e in coded_errors)
        
        # By model group
        group_by_error = defaultdict(Counter)
        for e in coded_errors:
            group = e.get('model_group', 'Unknown')
            error_type = e.get('primary_error_type', '')
            group_by_error[group][error_type] += 1
        
        # By model
        model_by_error = defaultdict(Counter)
        for e in coded_errors:
            model = e.get('model_name', 'Unknown')
            error_type = e.get('primary_error_type', '')
            model_by_error[model][error_type] += 1
        
        # By problem type
        problem_by_error = defaultdict(Counter)
        for e in coded_errors:
            ptype = e.get('problem_type', 'Unknown')
            error_type = e.get('primary_error_type', '')
            problem_by_error[ptype][error_type] += 1
        
        # Secondary error types
        secondary_freq = Counter(
            e.get('secondary_error_type', '') 
            for e in coded_errors 
            if e.get('secondary_error_type')
        )
        
        self.patterns['frequencies'] = {
            'error_type_overall': dict(error_type_freq),
            'by_model_group': {k: dict(v) for k, v in group_by_error.items()},
            'by_model': {k: dict(v) for k, v in model_by_error.items()},
            'by_problem_type': {k: dict(v) for k, v in problem_by_error.items()},
            'secondary_error_types': dict(secondary_freq),
            'total_coded': len(coded_errors)
        }
        
        print(f"✓ Quantitized {len(coded_errors)} coded errors")
        return self.patterns['frequencies']
    
    def create_contingency_tables(self) -> Dict:
        """
        Create contingency tables for chi-square analysis
        
        Returns:
            Dictionary with contingency tables
        """
        if 'frequencies' not in self.patterns:
            self.quantitize_data()
        
        freq = self.patterns['frequencies']
        
        # RLHF vs non-RLHF by error type
        group_freq = freq['by_model_group']
        
        # Get all error types
        all_error_types = set()
        for group_data in group_freq.values():
            all_error_types.update(group_data.keys())
        all_error_types = sorted(all_error_types)
        
        # Build contingency table
        contingency = {}
        for group, error_counts in group_freq.items():
            contingency[group] = {et: error_counts.get(et, 0) for et in all_error_types}
        
        self.patterns['contingency_tables'] = {
            'group_x_error_type': contingency,
            'error_types': all_error_types
        }
        
        print(f"✓ Created contingency tables")
        print(f"  Groups: {list(contingency.keys())}")
        print(f"  Error types: {all_error_types}")
        
        return self.patterns['contingency_tables']
    
    def perform_chi_square_tests(self) -> Dict:
        """
        Perform chi-square tests on contingency tables
        
        Returns:
            Dictionary with test results
        """
        if 'contingency_tables' not in self.patterns:
            self.create_contingency_tables()
        
        contingency = self.patterns['contingency_tables']['group_x_error_type']
        
        # Perform chi-square test
        test_result = chi_square_test(contingency)
        
        # Calculate standardized residuals for each cell
        if test_result['significant']:
            residuals = {}
            observed = test_result['observed']
            expected = test_result['expected']
            
            for i, row in enumerate(test_result['row_labels']):
                residuals[row] = {}
                for j, col in enumerate(test_result['col_labels']):
                    if expected[i][j] > 0:
                        residual = (observed[i][j] - expected[i][j]) / math.sqrt(expected[i][j])
                        residuals[row][col] = residual
        
            test_result['standardized_residuals'] = residuals
            
            # Identify cells driving the difference (|residual| > 2)
            significant_cells = []
            for row, row_residuals in residuals.items():
                for col, residual in row_residuals.items():
                    if abs(residual) > 2:
                        direction = "more" if residual > 0 else "less"
                        significant_cells.append({
                            'group': row,
                            'error_type': col,
                            'residual': residual,
                            'direction': direction
                        })
            
            test_result['significant_cells'] = significant_cells
        
        self.patterns['chi_square_tests'] = {
            'group_comparison': test_result
        }
        
        print(f"✓ Chi-square test completed")
        print(f"  χ²({test_result['degrees_of_freedom']}) = {test_result['chi_square']:.3f}")
        print(f"  p = {test_result['p_value']:.4f}")
        print(f"  Effect size (Cramér's V) = {test_result['effect_size']:.3f}")
        
        return self.patterns['chi_square_tests']
    
    def identify_key_patterns(self) -> Dict:
        """
        Identify key patterns in error distributions
        
        Returns:
            Dictionary with identified patterns
        """
        if 'chi_square_tests' not in self.patterns:
            self.perform_chi_square_tests()
        
        test_result = self.patterns['chi_square_tests']['group_comparison']
        freq = self.patterns['frequencies']
        
        patterns_found = {
            'significant_difference': test_result['significant'],
            'effect_size': test_result['effect_size'],
            'effect_interpretation': self._interpret_effect_size(test_result['effect_size']),
            'key_findings': [],
            'group_profiles': {},
            'recommendations': []
        }
        
        if test_result['significant']:
            # Identify which error types differ by group
            for cell in test_result.get('significant_cells', []):
                group = cell['group']
                error_type = cell['error_type']
                direction = cell['direction']
                
                # Get category name
                cat_name = self.rubric.get(error_type, {}).get('name', error_type)
                
                finding = f"{group} models show significantly {direction} "
                finding += f"{cat_name} errors than expected (residual = {cell['residual']:.2f})"
                patterns_found['key_findings'].append(finding)
            
            # Create group profiles
            for group in freq['by_model_group'].keys():
                group_errors = freq['by_model_group'][group]
                total = sum(group_errors.values())
                
                profile = {
                    'total_errors': total,
                    'error_distribution': {},
                    'most_common': [],
                    'least_common': []
                }
                
                for error_type, count in group_errors.items():
                    pct = (count / total * 100) if total > 0 else 0
                    cat_name = self.rubric.get(error_type, {}).get('name', error_type)
                    profile['error_distribution'][error_type] = {
                        'count': count,
                        'percentage': pct,
                        'name': cat_name
                    }
                
                # Sort by frequency
                sorted_errors = sorted(group_errors.items(), key=lambda x: -x[1])
                profile['most_common'] = [e[0] for e in sorted_errors[:3]]
                profile['least_common'] = [e[0] for e in sorted_errors[-3:]]
                
                patterns_found['group_profiles'][group] = profile
        
        # Generate recommendations
        if not test_result['significant']:
            patterns_found['recommendations'].append(
                "No significant difference in error patterns between RLHF and non-RLHF models."
            )
        else:
            patterns_found['recommendations'].append(
                "Significant differences found. Focus on error types with largest residuals."
            )
            
            if test_result['effect_size'] > 0.3:
                patterns_found['recommendations'].append(
                    "Large effect size suggests meaningful practical differences between groups."
                )
        
        self.patterns['key_patterns'] = patterns_found
        return patterns_found
    
    def _interpret_effect_size(self, cramers_v: float) -> str:
        """Interpret Cramér's V effect size"""
        if cramers_v < 0.1:
            return "Very small effect"
        elif cramers_v < 0.3:
            return "Small effect"
        elif cramers_v < 0.5:
            return "Medium effect"
        else:
            return "Large effect"
    
    def generate_report(self, output_file: str = None) -> str:
        """
        Generate comprehensive pattern analysis report
        
        Returns:
            Path to saved report
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f'data/processed/pattern_analysis_report_{timestamp}.txt'
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("PATTERN ANALYSIS REPORT\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Overview
            f.write("OVERVIEW\n")
            f.write("-" * 70 + "\n")
            freq = self.patterns.get('frequencies', {})
            f.write(f"Total coded errors: {freq.get('total_coded', 0)}\n")
            f.write(f"Error types in rubric: {len(self.rubric)}\n\n")
            
            # Frequency distribution
            f.write("ERROR TYPE FREQUENCIES\n")
            f.write("-" * 70 + "\n")
            error_freq = freq.get('error_type_overall', {})
            for error_type, count in sorted(error_freq.items(), key=lambda x: -x[1]):
                cat_name = self.rubric.get(error_type, {}).get('name', error_type)
                pct = count / freq.get('total_coded', 1) * 100
                f.write(f"  {error_type} ({cat_name}): {count} ({pct:.1f}%)\n")
            f.write("\n")
            
            # By model group
            f.write("ERROR DISTRIBUTION BY MODEL GROUP\n")
            f.write("-" * 70 + "\n")
            for group, errors in freq.get('by_model_group', {}).items():
                f.write(f"\n{group}:\n")
                total = sum(errors.values())
                for error_type, count in sorted(errors.items(), key=lambda x: -x[1]):
                    cat_name = self.rubric.get(error_type, {}).get('name', error_type)
                    pct = (count / total * 100) if total > 0 else 0
                    f.write(f"  {error_type} ({cat_name}): {count} ({pct:.1f}%)\n")
            f.write("\n")
            
            # Chi-square results
            f.write("STATISTICAL TESTS\n")
            f.write("-" * 70 + "\n")
            chi_sq = self.patterns.get('chi_square_tests', {}).get('group_comparison', {})
            if chi_sq:
                f.write(f"Chi-square test (RLHF vs non-RLHF):\n")
                f.write(f"  χ²({chi_sq['degrees_of_freedom']}) = {chi_sq['chi_square']:.3f}\n")
                f.write(f"  p = {chi_sq['p_value']:.4f}\n")
                f.write(f"  Effect size (Cramér's V) = {chi_sq['effect_size']:.3f}\n")
                f.write(f"  Interpretation: {self._interpret_effect_size(chi_sq['effect_size'])}\n")
                f.write(f"  Significant: {'Yes' if chi_sq['significant'] else 'No'}\n")
            f.write("\n")
            
            # Key findings
            f.write("KEY FINDINGS\n")
            f.write("-" * 70 + "\n")
            key_patterns = self.patterns.get('key_patterns', {})
            if key_patterns.get('key_findings'):
                for finding in key_patterns['key_findings']:
                    f.write(f"  • {finding}\n")
            else:
                f.write("  No significant patterns identified.\n")
            f.write("\n")
            
            # Group profiles
            f.write("MODEL GROUP PROFILES\n")
            f.write("-" * 70 + "\n")
            for group, profile in key_patterns.get('group_profiles', {}).items():
                f.write(f"\n{group}:\n")
                f.write(f"  Total errors: {profile['total_errors']}\n")
                f.write(f"  Most common: {', '.join(profile['most_common'])}\n")
                f.write(f"  Least common: {', '.join(profile['least_common'])}\n")
            f.write("\n")
            
            # Recommendations
            f.write("RECOMMENDATIONS\n")
            f.write("-" * 70 + "\n")
            for rec in key_patterns.get('recommendations', []):
                f.write(f"  • {rec}\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("END OF REPORT\n")
        
        print(f"✓ Report saved to: {output_file}")
        return output_file
    
    def save_results(self, output_file: str = None) -> str:
        """Save all analysis results to JSON"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f'data/processed/pattern_analysis_{timestamp}.json'
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, indent=2, default=str)
        
        print(f"✓ Results saved to: {output_file}")
        return output_file
    
    def run_full_analysis(self) -> Dict:
        """Run complete pattern analysis workflow"""
        print("=" * 70)
        print("PATTERN ANALYSIS")
        print("=" * 70)
        
        self.quantitize_data()
        self.create_contingency_tables()
        self.perform_chi_square_tests()
        self.identify_key_patterns()
        self.generate_report()
        self.save_results()
        
        print("\n" + "=" * 70)
        print("✓ ANALYSIS COMPLETE")
        print("=" * 70)
        
        # Print summary
        key_patterns = self.patterns.get('key_patterns', {})
        print(f"\nKey Finding: {'Significant difference' if key_patterns.get('significant_difference') else 'No significant difference'} "
              f"between RLHF and non-RLHF error patterns")
        print(f"Effect Size: {key_patterns.get('effect_size', 0):.3f} ({key_patterns.get('effect_interpretation', '')})")
        
        if key_patterns.get('key_findings'):
            print("\nTop Findings:")
            for finding in key_patterns['key_findings'][:3]:
                print(f"  • {finding}")
        
        return self.patterns


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Pattern Analysis for Qualitative Coding')
    parser.add_argument('--coded-file', type=str, help='Coded data file')
    parser.add_argument('--report-only', action='store_true', help='Generate report only')
    
    args = parser.parse_args()
    
    analyzer = PatternAnalyzer(coded_file=args.coded_file)
    
    if not analyzer.coded_data:
        print("\n✗ No coded data found!")
        print("  Please complete qualitative coding first.")
        return
    
    if args.report_only:
        analyzer.generate_report()
    else:
        analyzer.run_full_analysis()


if __name__ == "__main__":
    main()
